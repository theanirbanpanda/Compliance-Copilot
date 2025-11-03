#!/usr/bin/env python3
import argparse
import json
import os
import logging
import time
import re
from typing import List, Dict, Any
from pathlib import Path

# --- Configuration ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
logger = logging.getLogger(__name__)

try:
    from dotenv import load_dotenv
    load_dotenv()
    logger.info("✅ .env file loaded if present.")
except ImportError:
    logger.warning("⚠️ python-dotenv not found. Relying on manually set environment variables.")

try:
    import google.generativeai as genai
except ImportError:
    genai = None

# --- Constants ---
MODEL_NAME = "models/gemini-2.5-flash"
MAX_RETRIES = 2
BACKOFF_TIME = 15
VERIFICATION_RULES: Dict[str, List[str]] = {
    "finance": ["tax", "invoice", "payment", "financial", "budget", "revenue", "irs"],
    "legal": ["contract", "agreement", "policy", "regulation", "law", "uscis", "ftc"],
    "labor": ["employee", "salary", "recruitment", "leave", "labor", "dol"],
}

# --- Core Logic ---
class DocumentProcessor:
    def __init__(self, gemini_api_key: str):
        self.model = None
        self.gemini_available = False
        if gemini_api_key and genai:
            try:
                genai.configure(api_key=gemini_api_key)
                self.model = genai.GenerativeModel(MODEL_NAME)
                self.gemini_available = True
                logger.info(f"✅ Gemini API configured with model: {MODEL_NAME}")
            except Exception as e:
                logger.error(f"❌ Failed to configure Gemini API: {e}")
        else:
             logger.warning("⚠️ Gemini API key not provided or library not found. AI features disabled.")


    def process_with_ai(self, chunk: str) -> Dict[str, Any]:
        """Processes a single chunk of text using the Gemini API."""
        if not self.gemini_available:
            return {"summary": "AI offline.", "tags": [], "confidence": 0.0}

        prompt = f"""Analyze the document chunk. Provide a 2-sentence summary and tags from: finance, legal, labor. Respond in a valid JSON format with three keys: "summary", "tags", and "confidence" (a float). Text: --- {chunk[:3000]} --- JSON Response:"""
        for attempt in range(MAX_RETRIES):
            try:
                logger.info(f"🔮 Calling Gemini API (Attempt {attempt + 1})...")
                response = self.model.generate_content(prompt)
                # Basic cleaning for potential markdown fences
                json_text = response.text.strip().lstrip('```json').rstrip('```').strip()
                result = json.loads(json_text)
                # Ensure confidence is a float
                result['confidence'] = float(result.get('confidence', 0.0))
                return result
            except Exception as e:
                logger.error(f"❌ Gemini API error or JSON parsing failed: {e}")
                if attempt < MAX_RETRIES - 1:
                    logger.info(f"⏳ Retrying in {BACKOFF_TIME}s...")
                    time.sleep(BACKOFF_TIME)
        # If all retries fail
        return {"summary": "AI processing failed.", "tags": [], "confidence": 0.0}

    def verify_chunk(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Verifies a single processed item against business rules."""
        tags = item.get("tags", [])
        # Use the full chunk text for verification if available, otherwise sample
        text_to_verify = item.get("original_chunk", item.get("text_sample", "")).lower()
        verification_passed = True
        notes = []
        for tag in tags:
            if tag in VERIFICATION_RULES:
                if not any(keyword in text_to_verify for keyword in VERIFICATION_RULES[tag]):
                    verification_passed = False
                    notes.append(f"Tag '{tag}' may be inconsistent with text sample.")
        item["verification"] = {
            "status": "passed" if verification_passed else "failed",
            "notes": " & ".join(notes) or "All tags appear consistent."
        }
        # Remove the temporary original_chunk key if it exists
        item.pop("original_chunk", None)
        return item

    def process_chunk(self, chunk: str, chunk_id: int, use_live: bool) -> Dict[str, Any]:
        """Processes a chunk with optional AI and final verification."""
        ai_result = self.process_with_ai(chunk) if use_live else {"summary": "Offline.", "tags": [], "confidence": 0.0}
        tags = ai_result.get("tags", [])
        if not isinstance(tags, list):
             logger.warning(f"AI returned non-list tags for chunk {chunk_id}: {tags}. Defaulting to empty list.")
             tags = []

        processed_item = {
            "id": chunk_id,
            "summary": ai_result.get("summary"),
            "text_sample": chunk[:300] + ("..." if len(chunk) > 300 else ""),
            "tags": tags,
            "confidence": float(ai_result.get("confidence", 0.5)), # Ensure float
            "original_chunk": chunk # Temporarily add for verification
        }
        # Run verification as the last step
        return self.verify_chunk(processed_item)

# --- THIS IS THE CORRECTED FUNCTION ---
def split_into_chunks(text: str) -> List[str]:
    """
    Splits text into chunks. Handles both multi-document text (with separators)
    and single blocks of text robustly.
    """
    separator = r'===== (?:BEGIN|END) FILE:.*?====='
    min_single_chunk_length = 20 # Minimum characters for a single block to be processed
    min_multi_chunk_length = 50 # Minimum characters after splitting by separators

    # Check if the text contains the file separators
    if re.search(separator, text):
        logger.info("Separator found, splitting by file markers.")
        file_sections = re.split(separator, text)
        # Filter out empty strings and potentially very short metadata lines resulting from split
        chunks = [section.strip() for section in file_sections if section.strip() and len(section.strip()) >= min_multi_chunk_length]
    else:
        # If no separators, treat the whole text as one chunk if it's long enough
        logger.info("No separators found, treating as a single chunk.")
        trimmed_text = text.strip()
        chunks = [trimmed_text] if len(trimmed_text) >= min_single_chunk_length else []

    if not chunks:
        logger.warning("Input text resulted in zero valid chunks after filtering for minimum length.")

    logger.info(f"📊 Split into {len(chunks)} chunk(s).")
    return chunks
# --- END OF FIX ---

def main():
    parser = argparse.ArgumentParser(description="Consolidated Document Processing and Verification Pipeline")
    parser.add_argument("--input-file", default="downloads/merged_output.txt", help="Path to the merged text file")
    parser.add_argument("--output-file", default="data/verified_categorization.json", help="Path for the final JSON output")
    parser.add_argument("--live", action="store_true", help="Enable live Gemini API calls")
    args = parser.parse_args()

    try:
        with open(args.input_file, 'r', encoding='utf-8') as f:
            full_text = f.read()
    except FileNotFoundError:
        logger.error(f"❌ Input file not found: {args.input_file}")
        return
    except Exception as e:
        logger.error(f"❌ Error reading input file {args.input_file}: {e}")
        return

    api_key = os.getenv('GEMINI_API_KEY')
    if args.live and not api_key:
        logger.warning("⚠️ --live flag set, but GEMINI_API_KEY not found. Proceeding in offline mode.")
        args.live = False

    processor = DocumentProcessor(api_key if args.live else None)
    chunks = split_into_chunks(full_text)

    if not chunks:
        logger.warning("🚫 No valid chunks found to process. Exiting.")
        # Create an empty output file for consistency
        all_results = []
    else:
        all_results = [processor.process_chunk(chunk, i + 1, args.live) for i, chunk in enumerate(chunks)]

    output_path = Path(args.output_file)
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False)
        logger.info(f"✅ Done. Saved {len(all_results)} processed and verified chunks to {output_path}")
    except Exception as e:
        logger.error(f"❌ Error writing output file {output_path}: {e}")

if __name__ == "__main__":
    main()