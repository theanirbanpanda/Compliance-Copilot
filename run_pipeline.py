#!/usr/bin/env python3
"""
Complete Compliance Copilot Pipeline Runner
Executes the simplified backend pipeline: PDF extraction -> AI processing & verification
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
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        logger.info(f"✅ {description} - SUCCESS")
        if result.stdout:
            summary_output = (result.stdout[:300] + '...') if len(result.stdout) > 300 else result.stdout
            logger.info(f"   Output:\n{summary_output.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ {description} - FAILED (Exit Code: {e.returncode})")
        if e.stderr:
            logger.error(f"   Error: {e.stderr.strip()}")
        if e.stdout:
            logger.error(f"   Output (stdout): {e.stdout.strip()}")
        return False

def main():
    """Run the complete, simplified pipeline."""
    print("🚀 Compliance Copilot - Final Backend Pipeline")
    print("=" * 60)
    
    # Define file paths
    merged_output_file = "downloads/merged_output.txt"
    final_output_file = "data/verified_categorization.json" # This is our final destination
    
    # --- STEP 1: PDF Text Extraction ---
    logger.info("\n" + "="*60 + "\nSTEP 1: PDF Text Extraction\n" + "="*60)
    if not run_command(f"python extract_pdfs.py", "Extracting text from all PDFs"):
        logger.error("❌ PDF extraction failed. Stopping pipeline.")
        return
    
    # --- STEP 2: Consolidated AI Processing & Verification ---
    logger.info("\n" + "="*60 + "\nSTEP 2: AI Processing & Verification\n" + "="*60)
    if not run_command(
        f"python scraper/process_documents.py --input-file {merged_output_file} --output-file {final_output_file} --live",
        "Applying consolidated AI processing, tagging, and verification"
    ):
        logger.error("❌ AI processing failed. Stopping pipeline.")
        return
        
    logger.info("\n" + "="*60 + "\n🎉 PIPELINE COMPLETED SUCCESSFULLY!\n" + "="*60)
    logger.info(f"✅ Final, verified data is available at: {final_output_file}")
    
if __name__ == "__main__":
    main()