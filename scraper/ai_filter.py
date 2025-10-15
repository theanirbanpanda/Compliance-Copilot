#!/usr/bin/env python3
"""
AI Filter Module for Compliance Copilot
Processes merged PDF text with rule-based and AI-powered tagging using Gemini API.
"""

import os
import sys
import json
import re
import argparse
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Enhanced rule-based keywords for comprehensive domain tagging
RULE_BASED_KEYWORDS = {
    'finance': [
        'finance', 'financial', 'budget', 'revenue', 'tax', 'investment', 'funding', 'cost', 'expense',
        'accounting', 'audit', 'compliance', 'regulatory', 'banking', 'credit', 'loan', 'payment',
        'profit', 'loss', 'income', 'expenditure', 'fiscal', 'monetary', 'economic', 'treasury'
    ],
    'technology': [
        'technology', 'digital', 'software', 'computer', 'data', 'system', 'network', 'cyber', 'AI', 'automation',
        'IT', 'information', 'database', 'cloud', 'security', 'encryption', 'algorithm', 'machine learning',
        'artificial intelligence', 'blockchain', 'API', 'integration', 'platform', 'application'
    ],
    'healthcare': [
        'health', 'medical', 'healthcare', 'hospital', 'patient', 'disease', 'treatment', 'medicine',
        'clinical', 'diagnosis', 'therapy', 'pharmaceutical', 'drug', 'vaccine', 'surgery', 'nursing',
        'mental health', 'wellness', 'prevention', 'epidemiology', 'public health', 'medical device'
    ],
    'environment': [
        'environment', 'climate', 'carbon', 'emission', 'sustainability', 'green', 'renewable', 'pollution',
        'ecosystem', 'biodiversity', 'conservation', 'energy', 'solar', 'wind', 'clean', 'waste',
        'recycling', 'sustainable', 'environmental impact', 'carbon footprint', 'global warming'
    ],
    'infrastructure': [
        'infrastructure', 'construction', 'building', 'transport', 'road', 'bridge', 'facility', 'development',
        'urban', 'city', 'municipal', 'public works', 'engineering', 'architecture', 'planning',
        'housing', 'utilities', 'water', 'sewage', 'electricity', 'telecommunications'
    ],
    'legal': [
        'legal', 'law', 'regulation', 'compliance', 'policy', 'legislation', 'statute', 'court',
        'judge', 'attorney', 'lawyer', 'contract', 'agreement', 'liability', 'rights', 'obligations',
        'jurisdiction', 'enforcement', 'penalty', 'sanction', 'governance', 'ethics'
    ],
    'education': [
        'education', 'school', 'university', 'college', 'student', 'teacher', 'learning', 'curriculum',
        'academic', 'research', 'study', 'training', 'certification', 'degree', 'scholarship',
        'literacy', 'knowledge', 'skill', 'development', 'pedagogy'
    ],
    'government': [
        'government', 'public', 'administration', 'bureaucracy', 'civil service', 'municipal', 'federal',
        'state', 'local', 'election', 'democracy', 'citizen', 'public service', 'policy', 'governance',
        'bureaucracy', 'public sector', 'civil servant', 'official'
    ]
}

class AIFilter:
    """AI-powered text filtering and tagging system."""
    
    def __init__(self, gemini_api_key: Optional[str] = None):
        self.gemini_api_key = gemini_api_key
        self.gemini_available = bool(gemini_api_key)
        
        if self.gemini_available:
            try:
                import google.generativeai as genai
                genai.configure(api_key=gemini_api_key)
                self.model = genai.GenerativeModel('gemini-2.5flash')
                logger.info("✅ Gemini API configured successfully")
            except ImportError:
                logger.warning("⚠️  google-generativeai not installed. Install with: pip install google-generativeai")
                self.gemini_available = False
            except Exception as e:
                logger.warning(f"⚠️  Gemini API setup failed: {e}")
                self.gemini_available = False
        else:
            logger.info("ℹ️  No GEMINI_API_KEY found. Using rule-based tagging only.")
    
    def extract_years(self, text: str) -> List[int]:
        """Extract all 4-digit years from text."""
        year_pattern = r'\b(19|20)\d{2}\b'
        years = re.findall(year_pattern, text)
        return sorted(list(set([int(year) for year in years])))
    
    def rule_based_tagging(self, text: str) -> List[str]:
        """Apply rule-based tagging using keyword matching."""
        text_lower = text.lower()
        detected_tags = []
        
        for category, keywords in RULE_BASED_KEYWORDS.items():
            if any(keyword in text_lower for keyword in keywords):
                detected_tags.append(category)
        
        return detected_tags
    
    def ai_tagging(self, text: str) -> Tuple[List[str], str]:
        """
        Use Gemini API for advanced tagging and summarization.
        Returns: (tags, summary)
        """
        if not self.gemini_available:
            return [], ""
        
        try:
            prompt = f"""
            Analyze the following government/compliance document text and provide:
            1. Relevant tags from these categories: environment, finance, infrastructure, health, technology
            2. A brief summary (2-3 sentences)
            
            Text: {text[:2000]}  # Limit to avoid token limits
            
            Respond in JSON format:
            {{
                "tags": ["tag1", "tag2"],
                "summary": "Brief summary here"
            }}
            """
            
            response = self.model.generate_content(prompt)
            result = json.loads(response.text.strip())
            
            tags = result.get('tags', [])
            summary = result.get('summary', '')
            
            return tags, summary
            
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return [], ""
    
    def process_text_chunk(self, chunk: str, chunk_id: int) -> Dict[str, Any]:
        """Process a single text chunk and return structured data."""
        if not chunk.strip():
            return {
                'id': chunk_id,
                'created_at': datetime.now(timezone.utc).isoformat(),
                'summary': '',
                'tags': [],
                'detected_years': [],
                'sample_text': '',
                'processing_method': 'empty_chunk'
            }
        
        # Extract years
        years = self.extract_years(chunk)
        
        # Get tags and summary
        if self.gemini_available:
            ai_tags, ai_summary = self.ai_tagging(chunk)
            rule_tags = self.rule_based_tagging(chunk)
            # Combine tags, preferring AI results
            all_tags = list(set(ai_tags + rule_tags))
            summary = ai_summary if ai_summary else chunk[:500] + "..." if len(chunk) > 500 else chunk
            processing_method = 'ai_enhanced'
        else:
            all_tags = self.rule_based_tagging(chunk)
            summary = chunk[:500] + "..." if len(chunk) > 500 else chunk
            processing_method = 'rule_based'
        
        return {
            'id': chunk_id,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'summary': summary,
            'tags': all_tags,
            'detected_years': years,
            'sample_text': chunk[:500],
            'processing_method': processing_method
        }
    
    def split_text_into_chunks(self, text: str, chunk_size: int = 1200) -> List[str]:
        """
        Split text into optimal chunks for AI processing.
        Target size: 1000-1500 characters for better context retention.
        """
        # First, split by file markers to preserve document boundaries
        file_sections = re.split(r'===== (?:BEGIN|END) FILE:', text)
        chunks = []
        
        for section in file_sections:
            if not section.strip():
                continue
            
            # Clean up the section
            section = section.strip()
            
            # If section is small enough, keep as one chunk
            if len(section) <= chunk_size:
                chunks.append(section)
            else:
                # Split large sections intelligently
                section_chunks = self._split_section_into_chunks(section, chunk_size)
                chunks.extend(section_chunks)
        
        # Filter out empty chunks and ensure minimum size
        valid_chunks = []
        for chunk in chunks:
            chunk = chunk.strip()
            if len(chunk) >= 50:  # Minimum meaningful chunk size
                valid_chunks.append(chunk)
        
        logger.info(f"📊 Split text into {len(valid_chunks)} chunks (target: {chunk_size} chars)")
        return valid_chunks
    
    def _split_section_into_chunks(self, section: str, chunk_size: int) -> List[str]:
        """Split a large section into optimally sized chunks."""
        chunks = []
        
        # Try to split by paragraphs first
        paragraphs = section.split('\n\n')
        current_chunk = ""
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            
            # If adding this paragraph would exceed chunk size
            if len(current_chunk) + len(paragraph) > chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = paragraph
            else:
                if current_chunk:
                    current_chunk += "\n\n" + paragraph
                else:
                    current_chunk = paragraph
        
        # Add the last chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        # If we still have chunks that are too large, split by sentences
        final_chunks = []
        for chunk in chunks:
            if len(chunk) <= chunk_size:
                final_chunks.append(chunk)
            else:
                # Split by sentences
                sentences = re.split(r'(?<=[.!?])\s+', chunk)
                current_sentence_chunk = ""
                
                for sentence in sentences:
                    if len(current_sentence_chunk) + len(sentence) > chunk_size and current_sentence_chunk:
                        final_chunks.append(current_sentence_chunk.strip())
                        current_sentence_chunk = sentence
                    else:
                        if current_sentence_chunk:
                            current_sentence_chunk += " " + sentence
                        else:
                            current_sentence_chunk = sentence
                
                if current_sentence_chunk.strip():
                    final_chunks.append(current_sentence_chunk.strip())
        
        return final_chunks

def main():
    """Main execution function with command-line argument support."""
    parser = argparse.ArgumentParser(description='AI Filter for Compliance Copilot')
    parser.add_argument('--input-file', default='downloads/merged_output.txt',
                       help='Input text file to process')
    parser.add_argument('--output-file', default='data/ai_filtered_results.json',
                       help='Output JSON file path')
    parser.add_argument('--dry-run', action='store_true',
                       help='Print results without writing to file')
    parser.add_argument('--live', action='store_true',
                       help='Write results to output file')
    
    args = parser.parse_args()
    
    # Ensure data directory exists
    output_path = Path(args.output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Check if input file exists
    input_path = Path(args.input_file)
    if not input_path.exists():
        logger.error(f"❌ Input file not found: {input_path}")
        sys.exit(1)
    
    # Read input text
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            text = f.read()
    except Exception as e:
        logger.error(f"❌ Error reading input file: {e}")
        sys.exit(1)
    
    if not text.strip():
        logger.error("❌ Input file is empty")
        sys.exit(1)
    
    # Initialize AI filter
    gemini_key = os.getenv('GEMINI_API_KEY')
    ai_filter = AIFilter(gemini_key)
    
    # Process text
    logger.info(f"📄 Processing text from: {input_path}")
    chunks = ai_filter.split_text_into_chunks(text)
    logger.info(f"📊 Split into {len(chunks)} chunks")
    
    results = []
    total_tags = set()
    
    for i, chunk in enumerate(chunks, 1):
        logger.info(f"🔄 Processing chunk {i}/{len(chunks)}")
        result = ai_filter.process_text_chunk(chunk, i)
        results.append(result)
        total_tags.update(result['tags'])
    
    # Print summary
    print(f"\n✅ AI Filter completed successfully!")
    print(f"📄 Results saved to: {args.output_file}")
    print(f"Total chunks processed: {len(results)}")
    print(f"Total tags detected: {len(total_tags)}")
    print(f"Tags found: {sorted(list(total_tags))}")
    
    if results:
        print(f"\nFirst item sample:")
        print(json.dumps(results[0], indent=2))
    
    # Write results if not dry run
    if not args.dry_run and (args.live or not args.dry_run):
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            logger.info(f"💾 Results written to: {output_path}")
        except Exception as e:
            logger.error(f"❌ Error writing output file: {e}")
            sys.exit(1)
    elif args.dry_run:
        print(f"\n🔍 DRY RUN: Results not written to file")

if __name__ == "__main__":
    main()
