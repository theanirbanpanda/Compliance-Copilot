import os
import sys
import logging
from typing import Tuple
from datetime import datetime, timezone

from PyPDF2 import PdfReader

# Configure logging
logger = logging.getLogger("scraper.extract_pdfs")
logger.setLevel(logging.INFO)
_console = logging.StreamHandler(sys.stdout)
_formatter = logging.Formatter(fmt="%(asctime)s | %(levelname)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
_console.setFormatter(_formatter)
if not logger.handlers:
    logger.addHandler(_console)

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__)))
DOWNLOADS_DIR = os.path.join(PROJECT_ROOT, "downloads")
MERGED_OUTPUT = os.path.join(DOWNLOADS_DIR, "merged_output.txt")

def extract_text_from_pdf(pdf_path: str) -> Tuple[bool, str]:
    """Extracts text from a single PDF file, handling errors gracefully."""
    try:
        reader = PdfReader(pdf_path)
        texts = [page.extract_text() or "" for page in reader.pages]
        return True, "\n".join(texts)
    except Exception as e:
        logger.error(f"Failed to read PDF {os.path.basename(pdf_path)}: {e}")
        return False, f"Failed to read PDF: {e}"

def run() -> None:
    print("🚀 PDF Text Extraction Pipeline")
    print("=" * 50)

    os.makedirs(DOWNLOADS_DIR, exist_ok=True)
    pdf_files = sorted([f for f in os.listdir(DOWNLOADS_DIR) if f.lower().endswith(".pdf")])
    
    total = len(pdf_files)
    success_count = 0
    total_chars = 0

    logger.info(f"Found {total} PDF file(s) in '{DOWNLOADS_DIR}'")

    # The 'w' mode ensures the file is always overwritten for a fresh run
    with open(MERGED_OUTPUT, "w", encoding="utf-8") as out:
        header = f"# Merged text generated at {datetime.now(timezone.utc).isoformat()}\n"
        out.write(header)

        for name in pdf_files:
            pdf_path = os.path.join(DOWNLOADS_DIR, name)
            ok, payload = extract_text_from_pdf(pdf_path)
            if ok:
                success_count += 1
                out.write(f"\n===== BEGIN FILE: {name} =====\n")
                out.write(payload)
                out.write(f"\n===== END FILE: {name} =====\n")
                total_chars += len(payload)
            else:
                logger.warning(f"Skipping failed extraction for {name}")

    print("\n📊 Extraction Summary:")
    print(f"   Total PDF files found: {total}")
    print(f"   Successfully extracted: {success_count}")
    print(f"   Failed extractions: {total - success_count}")
    print(f"   Merged output: {MERGED_OUTPUT}")
    print(f"   Total characters: {total_chars}")

if __name__ == "__main__":
    run()