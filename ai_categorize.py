#!/usr/bin/env python3
import argparse
import json
import logging
import os
import sys
import time
from typing import Any, Dict, List, Optional, Tuple


# ===== Logging Setup =====
logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# ===== Constants =====
CHUNK_SIZE = 50
BACKOFF_SECONDS = [30, 60, 120]
MODEL_PRIORITY = [
    "gemini-2.5-pro-exp",
    "gemini-2.0-pro-exp",
    "gemini-1.5-flash",
]

# Offline keyword mapping → Tag name (case-insensitive search)
OFFLINE_KEYWORD_TAGS: List[Tuple[str, str]] = [
    ("compliance", "Compliance"),
    ("report", "Report"),
    ("invoice", "Invoice"),
    ("contract", "Contract"),
    ("policy", "Policy"),
]


# ===== Helpers =====
def normalize_input_items(raw: Any) -> List[Dict[str, Any]]:
    """
    Normalize input list where elements can be strings or dicts with
    keys "line_number" and "text". Output is a list of dicts with
    1-based line_number and text, preserving original order.
    Invalid items are skipped with warnings.
    """
    if not isinstance(raw, list):
        logger.warning("Input JSON is not a list. Attempting to use 'lines' key if present.")
        if isinstance(raw, dict) and isinstance(raw.get("lines"), list):
            raw = raw.get("lines")
        else:
            logger.error("Unsupported input format; expected list or {\"lines\": [...]}.")
            return []

    normalized: List[Dict[str, Any]] = []
    for idx, item in enumerate(raw):
        try:
            if isinstance(item, str):
                normalized.append({"line_number": idx + 1, "text": item})
            elif isinstance(item, dict):
                text = item.get("text")
                if not isinstance(text, str):
                    logger.warning(f"Skipping item {idx}: missing or invalid 'text'")
                    continue
                # If provided, trust incoming line_number if it is valid int; otherwise assign by order
                ln = item.get("line_number")
                if isinstance(ln, int) and ln > 0:
                    line_number = ln
                else:
                    line_number = idx + 1
                normalized.append({"line_number": line_number, "text": text})
            else:
                logger.warning(f"Skipping item {idx}: unsupported type {type(item)}")
        except Exception as e:
            logger.warning(f"Skipping item {idx} due to error: {e}")
    # Sort by line_number ascending to maintain proper order after normalization
    normalized.sort(key=lambda x: x["line_number"]) 
    return normalized


def chunkify(items: List[Dict[str, Any]], size: int) -> List[List[Dict[str, Any]]]:
    return [items[i:i + size] for i in range(0, len(items), size)]


def offline_tags(text: str) -> List[str]:
    """Return tags using offline keyword mapping; ensure at least one tag."""
    lower = text.lower()
    tags: List[str] = []
    for keyword, tag in OFFLINE_KEYWORD_TAGS:
        if keyword in lower:
            tags.append(tag)
    if not tags:
        tags = ["General"]
    # De-duplicate while preserving order
    seen = set()
    deduped: List[str] = []
    for t in tags:
        if t not in seen:
            seen.add(t)
            deduped.append(t)
    return deduped


class GeminiClient:
    def __init__(self, api_key: Optional[str]):
        self.api_key = (api_key or "").strip()
        self.live = bool(self.api_key)
        self._genai = None
        if self.live:
            try:
                import google.generativeai as genai  # type: ignore
                genai.configure(api_key=self.api_key)
                self._genai = genai
                logger.info("Gemini live mode enabled")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client, falling back offline: {e}")
                self.live = False
                self._genai = None

    def categorize_chunk(self, lines: List[Dict[str, Any]]) -> Optional[List[Dict[str, Any]]]:
        if not self.live or self._genai is None:
            return None

        payload = self._build_prompt_payload(lines)
        last_error: Optional[Exception] = None

        for model_name in MODEL_PRIORITY:
            for attempt_idx in range(len(BACKOFF_SECONDS) + 1):
                if attempt_idx > 0:
                    delay = BACKOFF_SECONDS[attempt_idx - 1]
                    logger.warning(f"Retrying model {model_name} attempt {attempt_idx + 1}/{len(BACKOFF_SECONDS) + 1} after {delay}s")
                    time.sleep(delay)

                try:
                    logger.info(f"Using model: {model_name}")
                    model = self._genai.GenerativeModel(model_name)
                    response = model.generate_content(json.dumps(payload))
                    text = getattr(response, "text", None)
                    if not text:
                        raise RuntimeError("Empty response from model")
                    parsed = self._parse_response(text)
                    return parsed
                except Exception as e:
                    last_error = e
                    msg = str(e).lower()
                    if "404" in msg or "quota" in msg or "not found" in msg:
                        logger.error(f"Model {model_name} error (fallback to next): {e}")
                        break  # move to next model
                    logger.error(f"Model {model_name} error on attempt {attempt_idx + 1}: {e}")

        logger.warning(f"All Gemini models failed. Last error: {last_error}")
        return None

    def _build_prompt_payload(self, lines: List[Dict[str, Any]]) -> Dict[str, Any]:
        return {
            "instruction": (
                "Classify each line into tags. Return JSON array where each item has "
                "line_number:int, tags:List[str], confidence:float (0..1). Ensure at least one tag per line."
            ),
            "lines": lines,
        }

    def _parse_response(self, text: str) -> List[Dict[str, Any]]:
        candidate = text.strip()
        try:
            if candidate.startswith("["):
                return json.loads(candidate)
            start = candidate.find("[")
            end = candidate.rfind("]")
            if start != -1 and end != -1 and end > start:
                return json.loads(candidate[start:end + 1])
        except Exception as e:
            raise RuntimeError(f"Failed to parse model JSON: {e}")
        raise RuntimeError("Model did not return a JSON array")


def process(input_file: str, output_file: str, live: bool) -> None:
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            raw = json.load(f)
    except Exception as e:
        logger.exception(f"Failed to read input file {input_file}: {e}")
        raw = []

    items = normalize_input_items(raw)
    client = GeminiClient(os.getenv("GOOGLE_API_KEY")) if live else GeminiClient(None)

    ai_processed = 0
    offline_processed = 0
    results: List[Dict[str, Any]] = []

    chunks = chunkify(items, CHUNK_SIZE)
    total_chunks = len(chunks)

    for chunk_idx, chunk in enumerate(chunks, start=1):
        logger.info(f"Processing chunk {chunk_idx}/{total_chunks}")
        ai_response: Optional[List[Dict[str, Any]]] = None
        if client.live:
            try:
                ai_response = client.categorize_chunk(chunk)
            except Exception as e:
                logger.error(f"AI error during chunk {chunk_idx}: {e}")
                ai_response = None

        # Map AI results by line_number if available
        ai_by_ln: Dict[int, Dict[str, Any]] = {}
        if ai_response is not None:
            for item in ai_response:
                try:
                    ln = int(item.get("line_number"))
                    tags = item.get("tags")
                    conf = float(item.get("confidence", 0.0))
                    if not isinstance(tags, list):
                        continue
                    ai_by_ln[ln] = {"tags": [str(t) for t in tags], "confidence": max(0.0, min(conf, 1.0))}
                except Exception:
                    continue

        # Merge results, preserving order
        for line in chunk:
            ln = int(line["line_number"]) if isinstance(line.get("line_number"), int) else len(results) + 1
            text = str(line.get("text", ""))

            if ln in ai_by_ln and ai_by_ln[ln].get("tags"):
                tags = ai_by_ln[ln]["tags"]
                confidence = ai_by_ln[ln]["confidence"]
                ai_processed += 1
            else:
                tags = offline_tags(text)
                confidence = 0.5
                offline_processed += 1
                logger.info("Fallback applied for line via offline keywords")

            results.append({
                "line_number": ln,
                "text": text,
                "tags": tags,
                "category_confidence": float(confidence),
            })

    # Maintain overall order by line_number just in case
    results.sort(key=lambda x: x["line_number"]) 

    try:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved categorized results to {output_file}")
    except Exception as e:
        logger.exception(f"Failed to write output file {output_file}: {e}")

    logger.info(f"AI processed {ai_processed}")
    logger.info(f"Offline fallback {offline_processed}")


def main() -> None:
    parser = argparse.ArgumentParser(description="AI Categorization (Day 3) - Compliance-Copilot")
    parser.add_argument("--input-file", required=True, help="Path to input JSON (Day 2 output)")
    parser.add_argument("--output-file", required=True, help="Path to save categorized JSON")
    parser.add_argument("--live", action="store_true", help="Enable live Gemini API calls")
    args = parser.parse_args()

    try:
        process(args.input_file, args.output_file, args.live)
    except Exception as e:
        logger.exception(f"Unhandled exception: {e}")
        # Never crash
        sys.exit(1)


if __name__ == "__main__":
    main()


