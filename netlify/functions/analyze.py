import json
import os
import re
import logging
from typing import List, Dict, Any

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Try to import Gemini client
try:
    import google.generativeai as genai
except ImportError:
    genai = None

# --- Constants (copied from your scripts) ---
MODEL_NAME = "models/gemini-2.5-flash"
RULE_BASED_KEYWORDS = {
    'finance': ['finance', 'tax', 'budget', 'revenue', 'investment', 'accounting'],
    'legal': ['legal', 'law', 'regulation', 'compliance', 'policy', 'contract'],
    'technology': ['technology', 'software', 'data', 'cyber', 'ai', 'system'],
    'government': ['government', 'public', 'federal', 'state', 'irs'],
}

# --- Core Logic (adapted from your scripts) ---
class DocumentProcessor:
    def __init__(self, gemini_api_key: str):
        self.model = None
        if gemini_api_key and genai:
            try:
                genai.configure(api_key=gemini_api_key)
                self.model = genai.GenerativeModel(MODEL_NAME)
                self.gemini_available = True
            except Exception as e:
                logger.error(f"Failed to configure Gemini API: {e}")
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
            return {"summary": "AI not available.", "tags": []}
        prompt = f"""Analyze the document chunk. Provide a 2-sentence summary and tags from: finance, legal, technology, government. Respond in JSON with "summary" and "tags". Text: --- {chunk[:3000]} --- JSON Response:"""
        try:
            response = self.model.generate_content(prompt)
            json_text = response.text.strip().replace("```json", "").replace("```", "")
            return json.loads(json_text)
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return {"summary": "AI processing failed.", "tags": []}

    def process_chunk(self, chunk: str, chunk_id: int) -> Dict[str, Any]:
        rule_tags = self.rule_based_tagging(chunk)
        ai_result = self.process_with_ai(chunk)
        ai_tags = ai_result.get("tags", [])
        if not isinstance(ai_tags, list):
            ai_tags = []
        combined_tags = sorted(list(set(rule_tags + ai_tags)))
        return {
            "chunk_id": chunk_id,
            "summary": ai_result.get("summary"),
            "tags": combined_tags,
            "text_sample": chunk[:300] + "..."
        }

def split_into_chunks(text: str) -> List[str]:
    # A simple chunking strategy for now, we can make this smarter later
    return [p.strip() for p in text.split('\n\n') if p.strip()]

# --- The Netlify Handler Function ---
def handler(event, context):
    """
    This is the main entry point for our API. It gets triggered by a web request.
    """
    logger.info("Analyze endpoint triggered.")
    
    # Get the text from the user's request
    try:
        body = json.loads(event.get('body', '{}'))
        text_to_process = body.get('text')
        if not text_to_process:
            raise ValueError("Request body must contain a 'text' field.")
    except Exception as e:
        return {'statusCode': 400, 'body': json.dumps({'error': f'Invalid request: {e}'})}

    # Get the API key from environment variables (this is how Netlify handles secrets)
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        return {'statusCode': 500, 'body': json.dumps({'error': 'GEMINI_API_KEY is not set.'})}

    processor = DocumentProcessor(api_key)
    chunks = split_into_chunks(text_to_process)
    
    all_results = []
    for i, chunk in enumerate(chunks):
        result = processor.process_chunk(chunk, i + 1)
        all_results.append(result)

    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(all_results)
    }