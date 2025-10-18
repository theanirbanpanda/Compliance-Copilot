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
MAX_RETRIES = 2
BACKOFF_TIME = 15
MODEL_NAME = "models/gemini-2.5-flash"
RULE_BASED_KEYWORDS = {
    'finance': ['finance', 'tax', 'budget', 'revenue', 'investment', 'accounting', 'irs'],
    'legal': ['legal', 'law', 'regulation', 'compliance', 'policy', 'contract', 'uscis', 'ftc'],
    'labor': ['labor', 'employment', 'employee', 'whd', 'dol'],
    'safety': ['safety', 'osha', 'hazard'],
    'government': ['government', 'public', 'federal', 'state'],
}
VERIFICATION_RULES: Dict[str, List[str]] = {
    "finance": ["tax", "invoice", "payment", "financial", "budget", "revenue", "irs"],
    "legal": ["contract", "agreement", "policy", "regulation", "law", "uscis", "ftc"],
    "labor": ["employee", "salary", "recruitment", "leave", "labor", "dol"],
}

# --- Core Logic ---
class DocumentProcessor:
    def __init__(self, gemini_api_key: str):
        self.model = None
        if gemini_api_key and genai:
            try:
                genai.configure(api_key=gemini_api_key)
                self.model = genai.GenerativeModel(MODEL_NAME)
                self.gemini_available = True
                logger.info(f"✅ Gemini API configured with model: {MODEL_NAME}")
            except Exception as e:
                logger.error(f"❌ Failed to configure Gemini API: {e}")
                self.gemini_available = False
        else:
            self.gemini_available = False

    def rule_based_tagging(self, text: str) -> List[str]:
        tags = set()
        text_lower = text.lower()
        for category, keywords in RULE_BASED_KEYWORDS.items():
            if any(kw in text_lower for kw in keywords):
                tags.add(category)
        return list(tags)

    def process_with_ai(self, chunk: str) -> Dict[str, Any]:
        if not self.gemini_available:
            return {"summary": "AI not available.", "tags": [], "confidence": 0.0}
        prompt = f"""Analyze the document chunk. Provide a 2-sentence summary and tags from: finance, legal, labor, safety, government. Respond in a valid JSON format with three keys: "summary", "tags", and "confidence". Text: --- {chunk[:3000]} --- JSON Response:"""
        for attempt in range(MAX_RETRIES):
            try:
                logger.info(f"🔮 Calling Gemini API (Attempt {attempt + 1})...")
                response = self.model.generate_content(prompt)
                json_text = response.text.strip().replace("```json", "").replace("```", "")
                result = json.loads(json_text)
                if "summary" in result and "tags" in result:
                    return result
            except Exception as e:
                logger.error(f"❌ Gemini API error: {e}")
                if attempt < MAX_RETRIES - 1:
                    logger.info(f"⏳ Retrying in {BACKOFF_TIME}s...")
                    time.sleep(BACKOFF_TIME)
        return {"summary": "AI processing failed.", "tags": [], "confidence": 0.0}

    def verify_chunk(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Verifies a single processed item against business rules."""
        tags = item.get("tags", [])
        text_sample = item.get("text_sample", "").lower()
        verification_passed = True
        notes = []
        for tag in tags:
            if tag in VERIFICATION_RULES:
                if not any(keyword in text_sample for keyword in VERIFICATION_RULES[tag]):
                    verification_passed = False
                    notes.append(f"Tag '{tag}' present, but no required keywords found in sample.")
        item["verification"] = {
            "status": "passed" if verification_passed else "failed",
            "notes": notes if notes else "All tags appear consistent with text sample."
        }
        return item

    def process_chunk(self, chunk: str, chunk_id: int, use_live: bool) -> Dict[str, Any]:
        """Processes a chunk with rule-based tagging, optional AI, and final verification."""
        rule_tags = self.rule_based_tagging(chunk)
        processed_item = {}
        if use_live:
            ai_result = self.process_with_ai(chunk)
            ai_tags = ai_result.get("tags", [])
            if not isinstance(ai_tags, list):
                ai_tags = []
            combined_tags = sorted(list(set(rule_tags + ai_tags)))
            processed_item = {
                "id": chunk_id,
                "processing_method": "ai_enhanced",
                "summary": ai_result.get("summary"),
                "tags": combined_tags,
                "confidence": ai_result.get("confidence", 0.0),
                "text_sample": chunk[:300] + "..."
            }
        else:
            processed_item = {
                "id": chunk_id,
                "processing_method": "rule_based",
                "summary": chunk[:200] + "...",
                "tags": rule_tags,
                "confidence": 0.5,
                "text_sample": chunk[:300] + "..."
            }
        
        return self.verify_chunk(processed_item)

def split_into_chunks(text: str) -> List[str]:
    file_sections = re.split(r'===== (?:BEGIN|END) FILE:.*?=====', text)
    return [section.strip() for section in file_sections if section.strip() and len(section) > 100]

def main():
    parser = argparse.ArgumentParser(description="Consolidated Document Processing and Verification Pipeline")
    parser.add_argument("--input-file", default="downloads/merged_output.txt")
    parser.add_argument("--output-file", default="data/verified_categorization.json")
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()

    try:
        # --- FIX IS HERE ---
        # Corrected args.input-file to args.input_file
        with open(args.input_file, 'r', encoding='utf-8') as f:
            full_text = f.read()
    except FileNotFoundError:
        # --- FIX IS HERE ---
        # Corrected args.input-file to args.input_file
        logger.error(f"❌ Input file not found: {args.input_file}")
        return

    api_key = os.getenv('GEMINI_API_KEY')
    if args.live and not api_key:
        logger.warning("⚠️ --live flag set, but GEMINI_API_KEY not found. Proceeding in offline mode.")
        args.live = False

    processor = DocumentProcessor(api_key if args.live else None)
    chunks = split_into_chunks(full_text)
    logger.info(f"📊 Found {len(chunks)} document chunks to process.")

    all_results = [processor.process_chunk(chunk, i + 1, args.live) for i, chunk in enumerate(chunks)]

    # --- FIX IS HERE ---
    # Corrected args.output-file to args.output_file
    output_path = Path(args.output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    logger.info(f"✅ Done. Saved {len(all_results)} processed and verified chunks to {output_path}")

if __name__ == "__main__":
    main()