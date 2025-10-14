import os
import sys
import logging
from typing import Tuple
from datetime import datetime, timezone

from PyPDF2 import PdfReader

# Configure logging with timestamps
logger = logging.getLogger("scraper.extract_pdfs")
logger.setLevel(logging.DEBUG)
_console = logging.StreamHandler(sys.stdout)
_console.setLevel(logging.INFO)
_formatter = logging.Formatter(fmt="%(asctime)s | %(levelname)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
_console.setFormatter(_formatter)
if not logger.handlers:
    logger.addHandler(_console)

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DOWNLOADS_DIR = os.path.join(PROJECT_ROOT, "downloads")
MERGED_OUTPUT = os.path.join(DOWNLOADS_DIR, "merged_output.txt")

def extract_text_from_pdf(pdf_path: str) -> Tuple[bool, str]:
    """
    Returns: (success, extracted_text_or_error_message)
    """
    try:
        reader = PdfReader(pdf_path)
        texts = []
        for idx, page in enumerate(reader.pages):
            try:
                txt = page.extract_text() or ""
            except Exception as e_page:
                txt = f"[[ERROR extracting page {idx}: {e_page}]]\n"
            texts.append(txt)
        return True, "\n".join(texts)
    except Exception as e:
        return False, f"Failed to read PDF: {e}"

def run() -> None:
    os.makedirs(DOWNLOADS_DIR, exist_ok=True)
    pdf_files = [f for f in os.listdir(DOWNLOADS_DIR) if f.lower().endswith(".pdf")]
    pdf_files.sort()
    total = len(pdf_files)
    success = 0
    failed = 0
    total_chars = 0

    logger.info(f"Downloads directory: {DOWNLOADS_DIR}")
    logger.info(f"Found {total} PDF file(s) to process")

    with open(MERGED_OUTPUT, "w", encoding="utf-8") as out:
        header = f"# Merged text generated at {datetime.now(timezone.utc).isoformat()}\n"
        out.write(header)
        out.write("# Each file is separated by a header marker\n\n")

        for name in pdf_files:
            pdf_path = os.path.join(DOWNLOADS_DIR, name)
            logger.info(f"Processing: {pdf_path}")
            ok, payload = extract_text_from_pdf(pdf_path)
            if ok:
                success += 1
                out.write(f"\n\n===== BEGIN FILE: {name} =====\n")
                out.write(payload)
                out.write(f"\n===== END FILE: {name} =====\n")
                total_chars += len(payload)
            else:
                failed += 1
                logger.error(f"Extraction failed for {name}: {payload}")
                out.write(f"\n\n===== BEGIN FILE: {name} (EXTRACTION FAILED) =====\n")
                out.write(payload)
                out.write(f"\n===== END FILE: {name} (EXTRACTION FAILED) =====\n")

    # Print required summary
    print(f"Total PDF files processed: {total}")
    print(f"Successfully extracted: {success}")
    print(f"Failed extractions: {failed}")
    print(f"Total characters extracted: {total_chars}")
    print(f"Merged output saved to: {MERGED_OUTPUT}")

if __name__ == "__main__":
    run()
