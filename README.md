# Compliance Copilot - Day 2 Pipeline

A comprehensive AI-powered document processing pipeline that extracts text from PDFs, applies intelligent filtering and tagging, and generates structured JSON results with verification reports.

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Prepare PDF Files

Place your PDF files in the `downloads/` directory:
```bash
mkdir -p downloads
# Copy your PDF files to downloads/
```

### 3. Run the Complete Pipeline

```bash
# Run the entire pipeline in one command
python3 extract_pdfs.py && python3 scraper/ai_filter.py --live && python3 verify.py
```

## 📁 Project Structure

```
Compliance-Copilot/
├── downloads/                 # Input PDF files
├── data/                      # Output JSON results
├── scraper/                   # AI filtering module
│   └── ai_filter.py
├── extract_pdfs.py            # PDF text extraction
├── verify.py                  # Verification reports
├── requirements.txt           # Dependencies
└── README.md                  # This file
```

## 🔧 Individual Module Usage

### PDF Text Extraction
```bash
# Extract text from all PDFs in downloads/
python3 extract_pdfs.py
```

### AI Filtering (Rule-based)
```bash
# Process merged text with rule-based tagging
python3 scraper/ai_filter.py --live
```

### AI Filtering (With Gemini API)
```bash
# Set your Gemini API key
export GEMINI_API_KEY="your_api_key_here"

# Run with AI-enhanced tagging
python3 scraper/ai_filter.py --live
```

### Verification Report
```bash
# Generate comprehensive verification report
python3 verify.py

# Quick health check
python3 verify.py --health-check
```

## 🎯 Features

### PDF Text Extraction (`extract_pdfs.py`)
- ✅ Extracts text from all PDFs in `downloads/` folder
- ✅ Merges text into `downloads/merged_output.txt`
- ✅ Handles extraction errors gracefully
- ✅ Preserves document boundaries with file markers
- ✅ Comprehensive logging and progress tracking

### AI Filtering (`scraper/ai_filter.py`)
- ✅ Intelligent text chunking (1000-1500 characters)
- ✅ Rule-based domain tagging (8 categories)
- ✅ Gemini API integration for enhanced tagging
- ✅ Year detection (4-digit years)
- ✅ Command-line argument support
- ✅ Structured JSON output

**Supported Domains:**
- Finance, Technology, Healthcare, Environment
- Infrastructure, Legal, Education, Government

### Verification (`verify.py`)
- ✅ Comprehensive pipeline health checks
- ✅ Detailed statistics and summaries
- ✅ Tag distribution analysis
- ✅ Year detection summary
- ✅ JSON report generation

## 📊 Output Format

### AI Filtered Results (`data/ai_filtered_results.json`)
```json
[
  {
    "id": 1,
    "created_at": "2024-01-15T10:30:00Z",
    "summary": "Environmental impact report...",
    "tags": ["environment", "infrastructure"],
    "detected_years": [2023, 2022],
    "sample_text": "Environmental Impact Assessment...",
    "processing_method": "ai_enhanced"
  }
]
```

### Verification Report (`data/verification_report.json`)
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "pdf_count": 5,
  "merged_output": {
    "exists": true,
    "characters": 125000,
    "files_processed": 5
  },
  "ai_results": {
    "chunks_processed": 45,
    "tags_summary": {"finance": 12, "technology": 8},
    "years_detected": [2023, 2022, 2021]
  }
}
```

## 🔧 Command-Line Options

### AI Filter Options
```bash
python3 scraper/ai_filter.py [OPTIONS]

Options:
  --input-file PATH     Input text file (default: downloads/merged_output.txt)
  --output-file PATH    Output JSON file (default: data/ai_filtered_results.json)
  --dry-run            Print results without writing to file
  --live               Write results to output file
```

### Verification Options
```bash
python3 verify.py [OPTIONS]

Options:
  --data-dir PATH       Data directory (default: data)
  --downloads-dir PATH  Downloads directory (default: downloads)
  --health-check        Run health check only
```

## 🧪 Testing

### Test with Sample Data
```bash
# Create sample merged text and test AI filter
python3 test_ai_filter.py
```

### End-to-End Pipeline Test
```bash
# Run complete pipeline test
./setup_day2.sh
```

## 📈 Expected Output

After running the complete pipeline, you should see:

```
🚀 PDF Text Extraction Pipeline
==================================================
📄 Processing: document1.pdf
✅ Successfully extracted: document1.pdf (15420 chars)
📊 Extraction Summary:
   Total PDF files found: 3
   Successfully extracted: 3
   Failed extractions: 0
   Merged output: downloads/merged_output.txt
   Total characters: 45,230

🤖 AI Filter completed successfully!
📄 Results saved to: data/ai_filtered_results.json
Total chunks processed: 28
Total tags detected: 12
Tags found: ['finance', 'technology', 'healthcare', 'environment']

🔍 Compliance Copilot - Verification Report
============================================================
📄 PDF Files in downloads/: 3
📝 Merged Output: ✅ Found
   Files processed: 3
   Total characters: 45,230
   File size: 46,512 bytes

🤖 AI Filtered Results: ✅ Found
   Chunks processed: 28
   Tags detected: 12
   Tag distribution:
     • finance: 8
     • technology: 6
     • healthcare: 4
   Years detected: 3
   Years: [2021, 2022, 2023]

📊 Pipeline Summary:
   PDF files found: 3
   Files processed: 3
   Text characters: 45,230
   Chunks created: 28
   Unique tags: 12
   Years detected: 3

🏥 Pipeline Health Check:
   Merged output: ✅
   AI results: ✅
   Overall status: ✅ HEALTHY
```

## 🔑 Environment Variables

### Gemini API (Optional)
```bash
export GEMINI_API_KEY="your_gemini_api_key_here"
```

## 🐛 Troubleshooting

### Common Issues

1. **No PDFs found**: Ensure PDF files are in `downloads/` directory
2. **Extraction fails**: Check if PDFs are password-protected or corrupted
3. **AI filter fails**: Verify `merged_output.txt` exists and has content
4. **Gemini API errors**: Check API key and internet connection

### Debug Mode
```bash
# Enable detailed logging
export PYTHONPATH=.
python3 -c "
import logging
logging.basicConfig(level=logging.DEBUG)
# Run your command here
"
```

## 📝 License

This project is part of the Compliance Copilot system for automated document processing and AI-powered compliance analysis.

## 🤝 Contributing

1. Ensure all tests pass: `python3 verify.py --health-check`
2. Follow the modular architecture
3. Add comprehensive logging
4. Update documentation for new features