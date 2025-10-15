#!/usr/bin/env python3
"""
Complete Compliance Copilot Day 2 Pipeline Runner
Executes the entire pipeline: PDF extraction → AI filtering → Verification
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def run_command(command: str, description: str) -> bool:
    """Run a command and return success status."""
    logger.info(f"🔄 {description}")
    logger.info(f"   Command: {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info(f"✅ {description} - SUCCESS")
            if result.stdout:
                logger.info(f"   Output: {result.stdout.strip()}")
            return True
        else:
            logger.error(f"❌ {description} - FAILED")
            if result.stderr:
                logger.error(f"   Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        logger.error(f"❌ {description} - EXCEPTION: {e}")
        return False

def create_sample_pdfs():
    """Create sample PDF content for testing."""
    logger.info("📄 Creating sample PDF content...")
    
    # Create downloads directory
    downloads_dir = Path("downloads")
    downloads_dir.mkdir(exist_ok=True)
    
    # Create sample merged text (simulating extracted PDF content)
    sample_content = """# Merged text generated at 2024-01-15T10:30:00Z
# Each file is separated by a header marker

===== BEGIN FILE: financial_report_2023.pdf =====
Financial Compliance Report 2023

This comprehensive financial report covers our fiscal year 2023 performance. Total revenue reached $2.5M, representing a 15% increase from 2022. Our investment portfolio has been diversified across technology and healthcare sectors, with significant allocations to renewable energy projects.

Key financial metrics include:
- Revenue: $2,500,000 (up 15% from 2022)
- Operating expenses: $1,800,000
- Net profit: $700,000
- Tax compliance: 100% accuracy maintained

The budget allocation for 2024 includes $500,000 for technology infrastructure upgrades and $300,000 for healthcare system improvements. Our financial team has implemented new accounting software to enhance data security and regulatory compliance.
===== END FILE: financial_report_2023.pdf =====

===== BEGIN FILE: technology_roadmap.pdf =====
Technology Infrastructure Roadmap 2023-2024

This document outlines our digital transformation strategy and technology implementation plan. We are migrating to cloud-based systems and implementing AI-powered analytics across all departments.

Key technology initiatives:
- Cloud migration: 80% complete
- AI integration: Machine learning algorithms for data analysis
- Cybersecurity: Enhanced encryption and network security
- Digital platforms: New software applications for patient management

The technology team has successfully deployed new database systems and integrated APIs for seamless data flow. Our IT infrastructure now supports real-time analytics and automated reporting systems.
===== END FILE: technology_roadmap.pdf =====

===== BEGIN FILE: healthcare_compliance.pdf =====
Healthcare Compliance and Patient Safety Report

This report details our healthcare compliance measures and patient safety protocols implemented throughout 2023. Our medical facilities have undergone significant upgrades to improve patient care and treatment outcomes.

Healthcare improvements include:
- Electronic health records system implementation
- Telemedicine platform deployment
- Medical device upgrades and maintenance
- Patient safety protocol enhancements

Our healthcare team has successfully integrated new medical technology, including AI-powered diagnostic tools and automated patient monitoring systems. The hospital has maintained 100% compliance with healthcare regulations and improved patient satisfaction scores.
===== END FILE: healthcare_compliance.pdf =====

===== BEGIN FILE: environmental_sustainability.pdf =====
Environmental Impact and Sustainability Report 2023

This environmental assessment covers our sustainability initiatives and carbon footprint reduction efforts. We have implemented comprehensive green technology solutions and renewable energy systems across all facilities.

Environmental achievements:
- Carbon footprint reduced by 25% compared to 2022
- Renewable energy: 40% of total energy consumption
- Waste reduction: 30% decrease in landfill waste
- Green building certifications: 3 facilities certified

Our environmental team has successfully implemented solar panel systems, energy-efficient lighting, and waste recycling programs. The organization is committed to achieving carbon neutrality by 2025 through continued investment in green technology and sustainable practices.
===== END FILE: environmental_sustainability.pdf =====
"""
    
    # Write sample merged output
    merged_file = downloads_dir / "merged_output.txt"
    with open(merged_file, 'w', encoding='utf-8') as f:
        f.write(sample_content)
    
    logger.info(f"✅ Created sample merged text: {merged_file}")
    return str(merged_file)

def main():
    """Run the complete pipeline."""
    print("🚀 Compliance Copilot - Day 2 Pipeline")
    print("=" * 60)
    
    # Ensure directories exist
    Path("data").mkdir(exist_ok=True)
    Path("downloads").mkdir(exist_ok=True)
    
    # Create sample data if no PDFs exist
    downloads_dir = Path("downloads")
    pdf_files = list(downloads_dir.glob("*.pdf"))
    
    if not pdf_files:
        logger.info("📄 No PDF files found, creating sample data...")
        create_sample_pdfs()
    else:
        logger.info(f"📄 Found {len(pdf_files)} PDF files in downloads/")
    
    # Step 1: PDF Text Extraction
    logger.info("\n" + "="*60)
    logger.info("STEP 1: PDF Text Extraction")
    logger.info("="*60)
    
    success1 = run_command(
        "python3 extract_pdfs.py",
        "Extracting text from PDFs and creating merged output"
    )
    
    if not success1:
        logger.error("❌ PDF extraction failed. Stopping pipeline.")
        return False
    
    # Step 2: AI Filtering
    logger.info("\n" + "="*60)
    logger.info("STEP 2: AI Filtering and Tagging")
    logger.info("="*60)
    
    success2 = run_command(
        "python3 scraper/ai_filter.py --live",
        "Applying AI filtering and domain tagging"
    )
    
    if not success2:
        logger.error("❌ AI filtering failed. Stopping pipeline.")
        return False
    
    # Step 3: Verification
    logger.info("\n" + "="*60)
    logger.info("STEP 3: Verification and Reporting")
    logger.info("="*60)
    
    success3 = run_command(
        "python3 verify.py",
        "Generating verification report and health check"
    )
    
    if not success3:
        logger.error("❌ Verification failed.")
        return False
    
    # Final summary
    logger.info("\n" + "="*60)
    logger.info("🎉 PIPELINE COMPLETED SUCCESSFULLY!")
    logger.info("="*60)
    
    # Check output files
    data_dir = Path("data")
    ai_results = data_dir / "ai_filtered_results.json"
    verification_report = data_dir / "verification_report.json"
    
    if ai_results.exists():
        logger.info(f"✅ AI results: {ai_results}")
    else:
        logger.warning("⚠️  AI results file not found")
    
    if verification_report.exists():
        logger.info(f"✅ Verification report: {verification_report}")
    else:
        logger.warning("⚠️  Verification report not found")
    
    logger.info("\n📋 Next steps:")
    logger.info("   1. Check data/ai_filtered_results.json for structured results")
    logger.info("   2. Review data/verification_report.json for detailed statistics")
    logger.info("   3. Set GEMINI_API_KEY for enhanced AI tagging")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
