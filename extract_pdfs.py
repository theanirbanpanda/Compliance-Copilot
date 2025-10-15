#!/usr/bin/env python3
"""
PDF Text Extraction Module for Compliance Copilot
Extracts text from PDFs in downloads/ folder and merges into merged_output.txt
"""

import os
import sys
import logging
from pathlib import Path
from typing import List, Tuple
from datetime import datetime, timezone

try:
    from PyPDF2 import PdfReader
except ImportError:
    print("❌ PyPDF2 not installed. Install with: pip install PyPDF2")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class PDFExtractor:
    """PDF text extraction and merging utility."""
    
    def __init__(self, downloads_dir: str = "downloads", output_file: str = "downloads/merged_output.txt"):
        self.downloads_dir = Path(downloads_dir)
        self.output_file = Path(output_file)
        self.downloads_dir.mkdir(exist_ok=True)
        self.output_file.parent.mkdir(exist_ok=True)
    
    def extract_text_from_pdf(self, pdf_path: Path) -> Tuple[bool, str, str]:
        """
        Extract text from a single PDF file.
        Returns: (success, extracted_text, error_message)
        """
        try:
            logger.info(f"📄 Processing: {pdf_path.name}")
            reader = PdfReader(pdf_path)
            texts = []
            
            for page_num, page in enumerate(reader.pages, 1):
                try:
                    text = page.extract_text()
                    if text:
                        texts.append(text)
                    logger.debug(f"   Page {page_num}: {len(text)} characters")
                except Exception as e:
                    logger.warning(f"   Page {page_num} extraction failed: {e}")
                    texts.append(f"[ERROR extracting page {page_num}: {e}]")
            
            if not texts:
                return False, "", "No text content found in PDF"
            
            full_text = "\n".join(texts)
            return True, full_text, ""
            
        except Exception as e:
            error_msg = f"Failed to read PDF {pdf_path.name}: {e}"
            logger.error(error_msg)
            return False, "", error_msg
    
    def find_pdf_files(self) -> List[Path]:
        """Find all PDF files in downloads directory."""
        if not self.downloads_dir.exists():
            logger.warning(f"Downloads directory not found: {self.downloads_dir}")
            return []
        
        pdf_files = list(self.downloads_dir.glob("*.pdf"))
        logger.info(f"📁 Found {len(pdf_files)} PDF files in {self.downloads_dir}")
        return pdf_files
    
    def merge_texts(self, pdf_results: List[Tuple[str, str, bool]]) -> str:
        """
        Merge extracted texts with file headers.
        pdf_results: List of (filename, text, success)
        """
        merged_content = []
        merged_content.append(f"# Merged PDF text generated at {datetime.now(timezone.utc).isoformat()}")
        merged_content.append("# Each file is separated by a header marker")
        merged_content.append("")
        
        for filename, text, success in pdf_results:
            if success and text.strip():
                merged_content.append(f"===== BEGIN FILE: {filename} =====")
                merged_content.append(text.strip())
                merged_content.append(f"===== END FILE: {filename} =====")
                merged_content.append("")
            else:
                merged_content.append(f"===== BEGIN FILE: {filename} (EXTRACTION FAILED) =====")
                merged_content.append(f"[ERROR: {text}]")
                merged_content.append(f"===== END FILE: {filename} (EXTRACTION FAILED) =====")
                merged_content.append("")
        
        return "\n".join(merged_content)
    
    def extract_all_pdfs(self) -> Tuple[int, int, int, str]:
        """
        Extract text from all PDFs and create merged output.
        Returns: (total_pdfs, successful_extractions, failed_extractions, merged_file_path)
        """
        # Check if merged output already exists
        if self.output_file.exists():
            logger.info(f"✅ Merged output already exists: {self.output_file}")
            with open(self.output_file, 'r', encoding='utf-8') as f:
                content = f.read()
            return 0, 0, 0, str(self.output_file)
        
        # Find PDF files
        pdf_files = self.find_pdf_files()
        if not pdf_files:
            logger.warning("No PDF files found in downloads directory")
            return 0, 0, 0, ""
        
        # Extract text from each PDF
        pdf_results = []
        successful = 0
        failed = 0
        
        for pdf_path in pdf_files:
            success, text, error = self.extract_text_from_pdf(pdf_path)
            pdf_results.append((pdf_path.name, text, success))
            
            if success:
                successful += 1
                logger.info(f"✅ Successfully extracted: {pdf_path.name} ({len(text)} chars)")
            else:
                failed += 1
                logger.error(f"❌ Failed to extract: {pdf_path.name} - {error}")
        
        # Merge all texts
        merged_content = self.merge_texts(pdf_results)
        
        # Save merged output
        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                f.write(merged_content)
            logger.info(f"💾 Merged output saved: {self.output_file}")
        except Exception as e:
            logger.error(f"❌ Failed to save merged output: {e}")
            return len(pdf_files), successful, failed, ""
        
        return len(pdf_files), successful, failed, str(self.output_file)

def main():
    """Main execution function."""
    print("🚀 PDF Text Extraction Pipeline")
    print("=" * 50)
    
    extractor = PDFExtractor()
    total_pdfs, successful, failed, output_path = extractor.extract_all_pdfs()
    
    # Print summary
    print(f"\n📊 Extraction Summary:")
    print(f"   Total PDF files found: {total_pdfs}")
    print(f"   Successfully extracted: {successful}")
    print(f"   Failed extractions: {failed}")
    
    if output_path:
        print(f"   Merged output: {output_path}")
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"   Total characters: {len(content)}")
    else:
        print("   ❌ No output file created")
    
    return successful > 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
