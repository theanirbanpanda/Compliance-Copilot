#!/usr/bin/env python3
import argparse
import json
import os
import logging
from time import sleep
from pathlib import Path

# ===== Logging Setup =====
logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ===== Offline Filtration Logic =====
def offline_filter(text):
    """
    Fallback filtration logic when AI models fail.
    Customize this logic as per your domain rules.
    """
    # Example simple keyword-based filtration
    keywords = ["confidential", "sensitive", "private"]
    filtered = [line for line in text.splitlines() if any(k in line.lower() for k in keywords)]
    return filtered

# ===== Gemini Model Handling =====
class GeminiHandler:
    def __init__(self, live=True):
        self.live = live
        # Priority order of models
        self.models = [
            "gemini-2.5-pro-exp",
            "gemini-2.0-pro-exp",
            "gemini-1.5-flash",
            "gemini-1.0-pro"
        ]

    def process_chunk(self, chunk):
        if not self.live:
            logger.info("Offline mode: using offline filter for this chunk")
            return offline_filter(chunk)

        # Try models in order
        for model in self.models:
            try:
                logger.info(f"🧩 Using model: {model}")
                # Placeholder for Gemini API call
                response = self.mock_gemini_call(chunk, model)
                if response:
                    return response
            except RuntimeError as e:
                logger.error(f"❌ Error with {model}: {e}")
            except Exception as e:
                logger.exception(f"Unexpected error with {model}: {e}")

        # If all models fail, fallback to offline
        logger.warning("⚠️ All Gemini models failed. Using offline filter.")
        return offline_filter(chunk)

    def mock_gemini_call(self, chunk, model):
        """
        Replace this with actual Gemini API call logic.
        Raises RuntimeError on failure to simulate model errors.
        """
        # Simulated responses for demonstration
        simulated_failures = ["gemini-2.5-pro-exp", "gemini-2.0-pro-exp"]
        if model in simulated_failures:
            raise RuntimeError("Model not available or quota exceeded")
        # Otherwise, simulate successful AI filtering
        return [line for line in chunk.splitlines() if len(line.strip()) > 0]

# ===== Main Processing =====
def split_chunks(text, chunk_size=1000):
    """
    Split large text into manageable chunks.
    """
    lines = text.splitlines()
    chunks = []
    for i in range(0, len(lines), chunk_size):
        chunks.append("\n".join(lines[i:i+chunk_size]))
    return chunks

def process_chunks(chunks, handler):
    all_results = []
    for idx, chunk in enumerate(chunks, start=1):
        logger.info(f"🔄 Processing chunk {idx}/{len(chunks)}")
        try:
            result = handler.process_chunk(chunk)
            all_results.extend(result)
        except Exception as e:
            logger.exception(f"Unhandled error in chunk {idx}: {e}")
            logger.info("Using offline filter for this chunk due to unhandled error.")
            all_results.extend(offline_filter(chunk))
    return all_results

# ===== CLI =====
def main():
    parser = argparse.ArgumentParser(description="AI Filter Script with Gemini fallback.")
    parser.add_argument("--live", action="store_true", help="Use live Gemini API models")
    parser.add_argument("--input-file", required=True, help="Path to input text file")
    parser.add_argument("--output-file", required=True, help="Path to output JSON file")
    args = parser.parse_args()

    # Load input
    input_path = Path(args.input_file)
    if not input_path.exists():
        logger.error(f"Input file not found: {input_path}")
        return

    with input_path.open("r", encoding="utf-8") as f:
        text = f.read()

    # Split and process
    chunks = split_chunks(text)
    logger.info(f"📊 Split into {len(chunks)} chunks")
    handler = GeminiHandler(live=args.live)
    results = process_chunks(chunks, handler)

    # Save output
    output_path = Path(args.output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    logger.info(f"✅ Processing complete. Results saved to {output_path}")

if __name__ == "__main__":
    main()
