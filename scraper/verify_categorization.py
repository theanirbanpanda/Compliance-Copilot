#!/usr/bin/env python3
import argparse
import json
import os
import logging
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
logger = logging.getLogger(__name__)

# --- Verification Logic ---

# Define the keywords that MUST be present for a tag to be considered valid.
# This is our business logic layer.
VERIFICATION_RULES: Dict[str, List[str]] = {
    "finance": ["tax", "invoice", "payment", "financial", "budget", "revenue"],
    "legal": ["contract", "agreement", "policy", "regulation", "law"],
    "hr": ["employee", "salary", "recruitment", "leave"],
}

def verify_item(item: Dict[str, Any]) -> Dict[str, Any]:
    """
    Verifies a single categorized item against a set of business rules.
    """
    tags = item.get("tags", [])
    text_sample = item.get("text_sample", "").lower()
    
    verification_passed = True
    notes = []

    for tag in tags:
        if tag in VERIFICATION_RULES:
            required_keywords = VERIFICATION_RULES[tag]
            # Check if at least one of the required keywords is in the text
            if not any(keyword in text_sample for keyword in required_keywords):
                verification_passed = False
                notes.append(f"Tag '{tag}' is present, but no required keywords ({', '.join(required_keywords)}) were found in the text sample.")

    # Add the verification results to the original item
    item["verification"] = {
        "status": "passed" if verification_passed else "failed",
        "notes": notes if notes else "All tags appear consistent with text sample."
    }
    return item

# --- Main Workflow ---
def main():
    parser = argparse.ArgumentParser(description="Verification Script for AI Categorization")
    parser.add_argument("--input-file", required=True, help="Input JSON file from ai_categorize step")
    parser.add_argument("--output-file", required=True, help="Output JSON file for verified results")
    args = parser.parse_args()

    try:
        with open(args.input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.info(f"✅ Successfully loaded {len(data)} items from '{args.input_file}'.")
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"❌ Failed to load input file '{args.input_file}': {e}")
        return

    verified_results = []
    passed_count = 0
    failed_count = 0

    logger.info("🚀 Starting verification process...")
    for item in data:
        verified_item = verify_item(item)
        verified_results.append(verified_item)
        if verified_item["verification"]["status"] == "passed":
            passed_count += 1
        else:
            failed_count += 1
    
    # Save the verified output
    output_path = args.output_file
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(verified_results, f, indent=2, ensure_ascii=False)
    
    logger.info(f"✅ Done. Saved {len(verified_results)} verified results to '{output_path}'.")
    logger.info(f"📊 Verification Summary: Passed={passed_count}, Failed={failed_count}")

if __name__ == "__main__":
    main()