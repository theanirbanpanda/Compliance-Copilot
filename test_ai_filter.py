#!/usr/bin/env python3
"""
Test script for AI Filter Module
Creates sample data and tests the AI filter functionality.
"""

import os
import sys
import json
from pathlib import Path

# Add scraper to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scraper'))

def create_sample_merged_text():
    """Create sample merged text for testing."""
    sample_text = """# Merged text generated at 2024-01-15T10:30:00Z
# Each file is separated by a header marker

===== BEGIN FILE: sample_environmental_report.pdf =====
Environmental Impact Assessment Report 2023

This comprehensive report analyzes the environmental impact of our infrastructure development projects. The study covers carbon emissions, renewable energy initiatives, and sustainability measures implemented throughout 2023. Key findings include a 15% reduction in carbon footprint compared to 2022, with significant investments in green technology and pollution control systems.

The climate change mitigation strategies have been successful, with renewable energy sources now accounting for 40% of our total energy consumption. Environmental compliance has been maintained across all construction projects, with special attention to green building standards and sustainable development practices.
===== END FILE: sample_environmental_report.pdf =====

===== BEGIN FILE: financial_compliance_2023.pdf =====
Financial Compliance and Budget Report 2023

This document outlines the financial performance and compliance requirements for the fiscal year 2023. Total revenue exceeded projections by 12%, with significant investments in technology infrastructure and healthcare systems. The budget allocation includes $2.5M for digital transformation initiatives and $1.8M for medical equipment upgrades.

Tax compliance has been maintained at 100% accuracy, with all financial reporting meeting regulatory standards. Investment returns have been strong, with a focus on sustainable finance and responsible investment practices. Cost management initiatives have resulted in 8% operational savings across all departments.
===== END FILE: financial_compliance_2023.pdf =====

===== BEGIN FILE: healthcare_technology_update.pdf =====
Healthcare Technology Integration Report

This report details the implementation of new medical technology systems across our healthcare facilities. The digital transformation includes electronic health records, telemedicine platforms, and AI-powered diagnostic tools. Patient care has improved significantly with the introduction of automated systems and data analytics.

The technology infrastructure supports real-time patient monitoring and automated treatment protocols. Medical staff have been trained on new software systems, with 95% adoption rate across all facilities. The integration of computer networks and cyber security measures ensures patient data protection and system reliability.
===== END FILE: healthcare_technology_update.pdf =====
"""
    
    # Ensure downloads directory exists
    downloads_dir = Path("downloads")
    downloads_dir.mkdir(exist_ok=True)
    
    # Write sample text
    sample_file = downloads_dir / "merged_output.txt"
    with open(sample_file, 'w', encoding='utf-8') as f:
        f.write(sample_text)
    
    print(f"✅ Created sample merged text: {sample_file}")
    return sample_file

def test_ai_filter():
    """Test the AI filter with sample data."""
    print("🧪 Testing AI Filter Module...")
    
    # Create sample data
    sample_file = create_sample_merged_text()
    
    # Import and test AI filter
    try:
        from ai_filter import AIFilter
        
        # Test without Gemini API (rule-based only)
        print("\n📋 Testing rule-based tagging...")
        ai_filter = AIFilter()
        
        # Test individual methods
        test_text = "This is a financial report about budget allocation and tax compliance in 2023."
        years = ai_filter.extract_years(test_text)
        tags = ai_filter.rule_based_tagging(test_text)
        
        print(f"   Test text: {test_text}")
        print(f"   Extracted years: {years}")
        print(f"   Detected tags: {tags}")
        
        # Test chunk processing
        print("\n🔄 Testing chunk processing...")
        result = ai_filter.process_text_chunk(test_text, 1)
        print(f"   Processed result: {json.dumps(result, indent=2)}")
        
        # Test with actual sample file
        print("\n📄 Testing with sample merged text...")
        with open(sample_file, 'r', encoding='utf-8') as f:
            text = f.read()
        
        chunks = ai_filter.split_text_into_chunks(text)
        print(f"   Split into {len(chunks)} chunks")
        
        results = []
        for i, chunk in enumerate(chunks, 1):
            result = ai_filter.process_text_chunk(chunk, i)
            results.append(result)
        
        # Print summary
        total_tags = set()
        for result in results:
            total_tags.update(result['tags'])
        
        print(f"\n✅ Test Results:")
        print(f"   Total chunks processed: {len(results)}")
        print(f"   Total tags detected: {len(total_tags)}")
        print(f"   Tags found: {sorted(list(total_tags))}")
        
        if results:
            print(f"\n   First item sample:")
            print(f"   {json.dumps(results[0], indent=4)}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

def test_command_line():
    """Test command-line functionality."""
    print("\n🔧 Testing command-line interface...")
    
    # Test dry run
    print("   Testing --dry-run...")
    os.system("python3 scraper/ai_filter.py --dry-run --input-file downloads/merged_output.txt")
    
    # Test live run
    print("\n   Testing --live...")
    os.system("python3 scraper/ai_filter.py --live --input-file downloads/merged_output.txt --output-file data/ai_filtered_results.json")
    
    # Check if output file was created
    output_file = Path("data/ai_filtered_results.json")
    if output_file.exists():
        print(f"✅ Output file created: {output_file}")
        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"   Contains {len(data)} processed chunks")
    else:
        print("❌ Output file not created")

def main():
    """Main test function."""
    print("🚀 Starting AI Filter Tests...")
    
    # Ensure data directory exists
    Path("data").mkdir(exist_ok=True)
    
    # Test core functionality
    success = test_ai_filter()
    
    if success:
        # Test command-line interface
        test_command_line()
        
        print("\n🎉 All tests completed!")
        print("\n📋 Next steps:")
        print("   1. Set GEMINI_API_KEY environment variable for AI-enhanced tagging")
        print("   2. Run: python3 scraper/ai_filter.py --live")
        print("   3. Check data/ai_filtered_results.json for results")
    else:
        print("\n❌ Tests failed. Check error messages above.")

if __name__ == "__main__":
    main()
