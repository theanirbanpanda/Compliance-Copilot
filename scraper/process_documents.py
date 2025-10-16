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
    import google.generativeai as genai
except ImportError:
    genai = None

# --- Constants ---
MAX_RETRIES = 2
BACKOFF_TIME = 15
MODEL_NAME = "models/gemini-2.5-flash"
RULE_BASED_KEYWORDS = {
    'finance': ['finance', 'tax', 'budget', 'revenue', 'investment', 'accounting'],
    'legal': ['legal', 'law', 'regulation', 'compliance', 'policy', 'contract'],
    'technology': ['technology', 'software', 'data', 'cyber', 'ai', 'system'],
    'government': ['government', 'public', 'federal', 'state', 'irs'],
}

# --- Core Logic ---
class DocumentProcessor:
    def __init__(self, gemini_api_key: str):
        self.model = None
        if gemini_api_key and genai:
            try:
                genai.configure(api_key=gemini_api_key)
                self.model = genai.GenerativeModel(MODEL_NAME)
                logger.info(f"✅ Gemini API configured with model: {MODEL_NAME}")
                self.gemini_available = True
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
        prompt = f"""Analyze the document chunk. Provide a 2-sentence summary and tags from: finance, legal, technology, government. Respond in JSON with "summary", "tags", and "confidence". Text: --- {chunk[:3000]} --- JSON Response:"""
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
        logger.warning("⚠️ AI processing failed after all retries.")
        return {"summary": "AI processing failed.", "tags": [], "confidence": 0.0}

    def process_chunk(self, chunk: str, chunk_id: int, use_live: bool) -> Dict[str, Any]:
        rule_tags = self.rule_based_tagging(chunk)
        if use_live:
            ai_result = self.process_with_ai(chunk)
            ai_tags = ai_result.get("tags", [])
            
            # --- DEFINITIVE SAFETY CHECK ---
            # This block ensures the script will NOT crash, even if the AI is inconsistent.
            if not isinstance(ai_tags, list):
                logger.warning(f"⚠️ AI returned tags of type {type(ai_tags)}, not a list. Discarding AI tags for this chunk.")
                logger.warning(f"   Problematic AI Result: {ai_result}")
                ai_tags = [] # Default to an empty list to prevent a crash
            # --- END OF FIX ---
            
            combined_tags = sorted(list(set(rule_tags + ai_tags)))
            return {"chunk_id": chunk_id, "processing_method": "ai_enhanced", "summary": ai_result.get("summary"), "tags": combined_tags, "confidence": ai_result.get("confidence", 0.0), "text_sample": chunk[:300] + "..."}
        else:
            return {"chunk_id": chunk_id, "processing_method": "rule_based", "summary": chunk[:200] + "...", "tags": rule_tags, "confidence": 0.5, "text_sample": chunk[:300] + "..."}

def split_into_chunks(text: str) -> List[str]:
    file_sections = re.split(r'===== (?:BEGIN|END) FILE:.*?=====', text)
    chunks = [section.strip() for section in file_sections if section.strip() and len(section) > 100]
    logger.info(f"📊 Found {len(chunks)} meaningful document chunks to process.")
    return chunks

def main():
    parser = argparse.ArgumentParser(description="Consolidated Document Processing Pipeline")
    parser.add_argument("--input-file", required=True)
    parser.add_argument("--output-file", required=True)
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()

    try:
        with open(args.input_file, 'r', encoding='utf-8') as f:
            full_text = f.read()
    except FileNotFoundError:
        logger.error(f"❌ Input file not found: {args.input_file}")
        return

    api_key = os.getenv('GEMINI_API_KEY')
    if args.live and not api_key:
        logger.warning("⚠️ --live flag is set, but GEMINI_API_KEY is not found. Proceeding in offline mode.")
        args.live = False

    processor = DocumentProcessor(api_key if args.live else None)
    chunks = split_into_chunks(full_text)

    all_results = []
    for i, chunk in enumerate(chunks):
        logger.info(f"🚀 Processing chunk {i+1}/{len(chunks)}...")
        result = processor.process_chunk(chunk, i + 1, args.live)
        all_results.append(result)

    output_path = Path(args.output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)

    logger.info(f"✅ Done. Saved {len(all_results)} processed chunks to {output_path}")

if __name__ == "__main__":
    main()