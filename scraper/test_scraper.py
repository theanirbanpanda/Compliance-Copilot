import os
import csv
import sys
import time
import logging
import hashlib
from datetime import datetime, timezone
from urllib.parse import urlparse
from typing import List, Dict, Tuple

import requests
import pandas as pd

# Configure logging
logger = logging.getLogger("scraper.test_scraper")
logger.setLevel(logging.DEBUG)
_console = logging.StreamHandler(sys.stdout)
_console.setLevel(logging.INFO)
_formatter = logging.Formatter(fmt="%(asctime)s | %(levelname)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
_console.setFormatter(_formatter)
if not logger.handlers:
    logger.addHandler(_console)

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DOWNLOADS_DIR = os.path.join(PROJECT_ROOT, "downloads")
METADATA_CSV = os.path.join(DOWNLOADS_DIR, "downloads_metadata.csv")

def ensure_directories() -> None:
    os.makedirs(DOWNLOADS_DIR, exist_ok=True)

def is_probable_pdf(response: requests.Response, content_start: bytes) -> bool:
    content_type = response.headers.get("Content-Type", "").lower()
    if "pdf" in content_type:
        return True
    # As a fallback, check PDF header
    return content_start.startswith(b"%PDF")

def safe_filename_from_url(url: str) -> str:
    parsed = urlparse(url)
    name = os.path.basename(parsed.path)
    if not name or "." not in name:
        # attempt to derive a name from full URL
        url_hash = hashlib.sha256(url.encode("utf-8")).hexdigest()[:12]
        name = f"download_{url_hash}.pdf"
    if not name.lower().endswith(".pdf"):
        name = f"{name}.pdf"
    # timestamp prefix for uniqueness and ordering
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{ts}_{name}"

def download_pdf(url: str, timeout: int = 30) -> Tuple[str, bool, str]:
    """
    Returns: (local_path_or_empty, success_bool, error_message_if_any)
    """
    try:
        logger.info(f"Attempting download: {url}")
        with requests.get(url, stream=True, timeout=timeout) as r:
            r.raise_for_status()
            # Peek first bytes to validate
            chunk_iter = r.iter_content(chunk_size=4096)
            first_chunk = next(chunk_iter, b"")
            if not is_probable_pdf(r, first_chunk):
                # Some .gov endpoints serve PDFs via redirects or with generic content-type.
                # We'll still save if header check fails but body looks like PDF.
                if not first_chunk.startswith(b"%PDF"):
                    msg = f"Not detected as PDF (Content-Type={r.headers.get('Content-Type')}); skipping."
                    logger.warning(msg)
                    return "", False, msg
            filename = safe_filename_from_url(url)
            local_path = os.path.join(DOWNLOADS_DIR, filename)
            with open(local_path, "wb") as f:
                if first_chunk:
                    f.write(first_chunk)
                for chunk in chunk_iter:
                    if chunk:
                        f.write(chunk)
        # Basic file size sanity
        size = os.path.getsize(local_path)
        if size < 1024:
            msg = f"Downloaded file too small ({size} bytes), likely invalid PDF."
            logger.warning(msg)
            return local_path, False, msg
        logger.info(f"Downloaded: {local_path} ({size} bytes)")
        return local_path, True, ""
    except Exception as e:
        logger.error(f"Download failed for {url}: {e}")
        return "", False, str(e)

def write_metadata_csv(records: List[Dict[str, str]], csv_path: str) -> None:
    df = pd.DataFrame.from_records(records, columns=["filename", "url", "status", "timestamp_utc"])
    df.to_csv(csv_path, index=False)

def run() -> None:
    ensure_directories()
    # A list longer than 3 to increase odds of 3+ successes; all are government (.gov) endpoints
    candidate_urls: List[str] = [
        "https://www.sec.gov/files/form10-k.pdf",
        "https://www.irs.gov/pub/irs-pdf/f1040.pdf",
        "https://www.cisa.gov/sites/default/files/publications/cisa-insights-ransomware-outbreak.pdf",
        "https://www.ftc.gov/system/files/ftc_gov/pdf/p042103_0.pdf",
        "https://www.faa.gov/sites/faa.gov/files/air_traffic/publications/atpubs/pcg/pcg_basic.pdf",
        "https://www.nasa.gov/wp-content/uploads/2015/06/np-2015-03-015-jsc-orion-pg.pdf",
    ]
    # Note: Some of these files are large; network speeds vary. We proceed with timeouts and robust error handling.

    logger.info(f"Downloads directory: {DOWNLOADS_DIR}")
    logger.info(f"Metadata CSV will be written to: {METADATA_CSV}")
    records: List[Dict[str, str]] = []

    success_count = 0
    fail_count = 0
    for url in candidate_urls:
        start = time.time()
        local_path, ok, err = download_pdf(url)
        ts = datetime.now(timezone.utc).isoformat()
        if ok:
            success_count += 1
            filename = os.path.basename(local_path)
            status = "success"
        else:
            fail_count += 1
            filename = os.path.basename(local_path) if local_path else ""
            status = f"failed: {err}"
        records.append({
            "filename": filename,
            "url": url,
            "status": status,
            "timestamp_utc": ts
        })
        logger.info(f"Elapsed for URL: {url} -> {time.time() - start:.2f}s")
    # Write metadata
    write_metadata_csv(records, METADATA_CSV)
    logger.info(f"Metadata written: {METADATA_CSV}")

    # Print summary
    total_attempted = len(candidate_urls)
    print(f"Downloaded {success_count} PDFs, {fail_count} failed, metadata saved to downloads_metadata.csv")
    # Extra verification lines
    print(f"Total attempted: {total_attempted}")
    print(f"Downloads directory: {DOWNLOADS_DIR}")
    print(f"Metadata path: {METADATA_CSV}")

if __name__ == "__main__":
    run()
