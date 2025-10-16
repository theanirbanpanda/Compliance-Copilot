#!/usr/bin/env python3
"""
Complete Compliance Copilot Pipeline Runner
Executes the entire pipeline: PDF extraction -> AI processing -> Verification
"""

import os
import sys
import subprocess
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

def run_command(command: str, description: str) -> bool:
    """Run a command and return success status."""
    logger.info(f"🔄 {description}")
    logger.info(f"   Command: {command}")
    
    try:
        # Using shell=True for simplicity, but ensure commands are safe
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        logger.info(f"✅ {description} - SUCCESS")
        if result.stdout:
            # Print only a summary of stdout to keep logs clean
            summary_output = (result.stdout[:200] + '...') if len(result.stdout) > 200 else result.stdout
            logger.info(f"   Output: {summary_output.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ {description} - FAILED (Exit Code: {e.returncode})")
        if e.stderr:
            logger.error(f"   Error: {e.stderr.strip()}")
        if e.stdout:
            logger.error(f"   Output (stdout): {e.stdout.strip()}")
        return False
    except Exception as e:
        logger.error(f"❌ {description} - EXCEPTION: {e}")
        return False

def main():
    """Run the complete pipeline."""
    print("🚀 Compliance Copilot - Full Backend Pipeline")
    print("=" * 60)
    
    # Define file paths
    merged_output_file = "downloads/merged_output.txt"
    processed_file = "data/processed_results_live.json"
    verified_file = "data/verified_categorization.json"
    
    # --- STEP 1: PDF Text Extraction ---
    logger.info("\n" + "="*60 + "\nSTEP 1: PDF Text Extraction\n" + "="*60)
    if not run_command(
        f"python extract_pdfs.py",
        "Extracting text from all PDFs in downloads/"
    ):
        logger.error("❌ PDF extraction failed. Stopping pipeline.")
        return False
    
    # --- STEP 2: Consolidated AI Processing ---
    logger.info("\n" + "="*60 + "\nSTEP 2: AI Document Processing\n" + "="*60)
    if not run_command(
        f"python scraper/process_documents.py --input-file {merged_output_file} --output-file {processed_file} --live",
        "Applying consolidated AI processing and tagging"
    ):
        logger.error("❌ AI processing failed. Stopping pipeline.")
        return False
        
    # --- STEP 3: Verification ---
    logger.info("\n" + "="*60 + "\nSTEP 3: Verification and Reporting\n" + "="*60)
    if not run_command(
        f"python scraper/verify_categorization.py --input-file {processed_file} --output-file {verified_file}",
        "Generating final verification report"
    ):
        logger.error("❌ Verification failed.")
        return False
    
    # --- FINAL SUMMARY ---
    logger.info("\n" + "="*60 + "\n🎉 PIPELINE COMPLETED SUCCESSFULLY!\n" + "="*60)
    logger.info(f"✅ Final, verified data is available at: {verified_file}")
    logger.info("\n📋 Next step: Build the frontend web application.")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)