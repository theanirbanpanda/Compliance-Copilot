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
except ImportError:
    pass
try:
    import google.generativeai as genai
except ImportError:
    genai = None

# --- Constants ---
MODEL_NAME = "models/gemini-2.5-flash"
VERIFICATION_RULES: Dict[str, List[str]] = {
    "finance": ["tax", "invoice", "payment", "financial", "budget", "revenue", "irs"],
    "legal": ["contract", "agreement", "policy", "regulation", "law", "uscis", "ftc"],
    "labor": ["employee", "salary", "recruitment", "leave", "labor", "dol"],
}

class DocumentProcessor:
    # ... (The __init__, process_with_ai, and verify_chunk methods are correct and do not need changes) ...
    def __init__(self, gemini_api_key: str):
        self.model = None
        if gemini_api_key and genai:
            try:
                genai.configure(api_key=gemini_api_key)
                self.model = genai.GenerativeModel(MODEL_NAME)
                self.gemini_available = True
            except Exception: self.gemini_available = False
        else: self.gemini_available = False

    def process_with_ai(self, chunk: str) -> Dict[str, Any]:
        if not self.gemini_available: return {"summary": "AI offline.", "tags": [], "confidence": 0.0}
        prompt = f"""Analyze the document chunk. Provide a 2-sentence summary and tags from: finance, legal, labor, safety, government. Respond in a valid JSON format with three keys: "summary", "tags", and "confidence". Text: --- {chunk[:3000]} --- JSON Response:"""
        try:
            response = self.model.generate_content(prompt)
            json_text = response.text.strip().replace("```json", "").replace("```", "")
            return json.loads(json_text)
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return {"summary": "AI processing failed.", "tags": [], "confidence": 0.0}

    def verify_chunk(self, item: Dict[str, Any]) -> Dict[str, Any]:
        tags = item.get("tags", [])
        text_sample = item.get("text_sample", "").lower()
        verification_passed = True
        notes = []
        for tag in tags:
            if tag in VERIFICATION_RULES and not any(keyword in text_sample for keyword in VERIFICATION_RULES[tag]):
                verification_passed = False
                notes.append(f"Tag '{tag}' may be inconsistent.")
        item["verification"] = {"status": "passed" if verification_passed else "failed", "notes": " & ".join(notes) or "Consistent."}
        return item
    
    # --- THIS IS THE CORRECTED FUNCTION ---
    def process_chunk(self, chunk: str, chunk_id: int, use_live: bool) -> Dict[str, Any]:
        """Processes a chunk with rule-based tagging, optional AI, and final verification."""
        ai_result = self.process_with_ai(chunk) if use_live else {"summary": "Offline.", "tags": [], "confidence": 0.0}
        tags = ai_result.get("tags", [])
        if not isinstance(tags, list): tags = []
        
        processed_item = {
            "line_number": chunk_id, # Use 'line_number' to match the frontend
            "summary": ai_result.get("summary"),
            "text_sample": chunk[:300] + "...",
            "tags": tags,
            "confidence": ai_result.get("confidence", 0.5)
        }
        return self.verify_chunk(processed_item)

def split_into_chunks(text: str) -> List[str]:
    file_sections = re.split(r'===== (?:BEGIN|END) FILE:.*?=====', text)
    return [section.strip() for section in file_sections if section.strip() and len(section) > 100]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-file", default="downloads/merged_output.txt")
    parser.add_argument("--output-file", default="data/verified_categorization.json")
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()

    try:
        with open(args.input_file, 'r', encoding='utf-8') as f: full_text = f.read()
    except FileNotFoundError:
        logger.error(f"Input file not found: {args.input_file}"); return

    api_key = os.getenv('GEMINI_API_KEY')
    processor = DocumentProcessor(api_key if args.live else None)
    chunks = split_into_chunks(full_text)
    
    all_results = [processor.process_chunk(chunk, i + 1, args.live) for i, chunk in enumerate(chunks)]

    output_path = Path(args.output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f: json.dump(all_results, f, indent=2)
    logger.info(f"Done. Saved {len(all_results)} chunks to {output_path}")

if __name__ == "__main__":
    main()