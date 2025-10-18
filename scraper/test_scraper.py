import os
import sys
import time
import logging
import hashlib
from datetime import datetime, timezone
from urllib.parse import urlparse
from typing import Any, List, Dict, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
import pandas as pd
from tqdm import tqdm # For a clean progress bar

# --- Configuration ---
# Configure logging for cleaner output
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
logger = logging.getLogger("scraper.test_scraper")

# --- Constants ---
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DOWNLOADS_DIR = os.path.join(PROJECT_ROOT, "downloads")
METADATA_CSV = os.path.join(DOWNLOADS_DIR, "downloads_metadata.csv")

# --- Core Functions ---
def ensure_directories() -> None:
    os.makedirs(DOWNLOADS_DIR, exist_ok=True)

def safe_filename_from_url(url: str) -> str:
    """Creates a unique, safe filename from a URL."""
    name = os.path.basename(urlparse(url).path)
    if not name or not name.lower().endswith(".pdf"):
        url_hash = hashlib.sha256(url.encode("utf-8")).hexdigest()[:12]
        name = f"download_{url_hash}.pdf"
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{ts}_{name}"

def download_pdf(url: str, timeout: int = 30) -> Dict[str, Any]:
    """Downloads a single PDF and returns a result dictionary."""
    start_time = time.time()
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        with requests.get(url, stream=True, timeout=timeout, headers=headers) as r:
            r.raise_for_status()
            
            filename = safe_filename_from_url(url)
            local_path = os.path.join(DOWNLOADS_DIR, filename)

            with open(local_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            size = os.path.getsize(local_path)
            if size < 1024:
                raise ValueError(f"Downloaded file is too small ({size} bytes).")

            return {"url": url, "filename": filename, "status": "success", "error_message": "", "elapsed_s": time.time() - start_time}
    except Exception as e:
        return {"url": url, "filename": "", "status": "failed", "error_message": str(e), "elapsed_s": time.time() - start_time}

def get_target_urls() -> List[str]:
    """Provides a fresh, verified list of URLs for compliance-related PDFs."""
    return [
        "https://www.irs.gov/pub/irs-pdf/p15.pdf",           # IRS, Employer's Tax Guide
        "https://www.dol.gov/sites/dolgov/files/WHD/legacy/files/fwha-poster.pdf", # Dept of Labor, Employee Rights
        "https://www.uscis.gov/sites/default/files/document/forms/i-9.pdf",    # USCIS, Employment Eligibility
        "https://www.osha.gov/sites/default/files/publications/osha3181.pdf", # OSHA, Hazard Communication
        "https://www.ftc.gov/system/files/documents/plain-language/bus01-complying-with-the-made-in-usa-standard.pdf", # FTC, Made in USA Standard
        "https://www.ecfr.gov/api/renderer/v1/pdf/CFR-2011-title40-vol1-part60.pdf" # EPA, Air Programs
    ]

def run() -> None:
    ensure_directories()
    candidate_urls = get_target_urls()
    logger.info(f"Found {len(candidate_urls)} URLs to download in parallel...")
    records: List[Dict[str, Any]] = []
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        # Wrap the executor with tqdm for a progress bar
        future_to_url = {executor.submit(download_pdf, url): url for url in candidate_urls}
        for future in tqdm(as_completed(future_to_url), total=len(candidate_urls), desc="Downloading PDFs"):
            result = future.result()
            records.append({
                "filename": result["filename"],
                "url": result["url"],
                "status": result["status"],
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                "error": result["error_message"]
            })

    df = pd.DataFrame.from_records(records)
    df.to_csv(METADATA_CSV, index=False)
    logger.info(f"✅ Metadata written to: {METADATA_CSV}")
    
    success_count = sum(1 for r in records if r["status"] == "success")
    fail_count = len(records) - success_count
    
    print("\n" + "="*50 + "\nDOWNLOAD PIPELINE COMPLETE\n" + "="*50)
    print(f"Total URLs processed: {len(records)}")
    print(f"✅ Successful downloads: {success_count}")
    print(f"❌ Failed downloads: {fail_count}")
    print(f"📁 Downloads directory: {DOWNLOADS_DIR}")
    print(f"📊 Metadata report: {METADATA_CSV}")
    print("="*50)

if __name__ == "__main__":
    # Add python-dotenv and tqdm to requirements if not already present
    try:
        import tqdm
    except ImportError:
        print("Installing tqdm for progress bar...")
        os.system(f"{sys.executable} -m pip install tqdm")

    run()