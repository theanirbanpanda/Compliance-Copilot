#!/bin/bash
set -euo pipefail

PROJECT_ROOT="/Users/anirban/Downloads/Compliance-Copilot"
cd "$PROJECT_ROOT"

echo "🚀 Setting up Compliance Copilot Day 2 - AI Filter Module"

# Activate virtual environment
echo "[1/6] Activating virtual environment..."
source "$PROJECT_ROOT/venv/bin/activate"

# Install additional dependencies for AI filter
echo "[2/6] Installing AI filter dependencies..."
pip install google-generativeai

# Ensure all directories exist
echo "[3/6] Creating required directories..."
mkdir -p "$PROJECT_ROOT/data" "$PROJECT_ROOT/downloads"

# Make scripts executable
echo "[4/6] Making scripts executable..."
chmod +x "$PROJECT_ROOT/scraper/ai_filter.py"
chmod +x "$PROJECT_ROOT/test_ai_filter.py"

# Test the AI filter module
echo "[5/6] Testing AI filter module..."
python3 "$PROJECT_ROOT/test_ai_filter.py"

# Run the AI filter with sample data
echo "[6/6] Running AI filter on sample data..."
python3 "$PROJECT_ROOT/scraper/ai_filter.py --live --input-file downloads/merged_output.txt --output-file data/ai_filtered_results.json"

echo ""
echo "✅ Day 2 setup completed successfully!"
echo ""
echo "📋 What was created:"
echo "   • scraper/ai_filter.py - AI-powered text filtering module"
echo "   • test_ai_filter.py - Test script with sample data"
echo "   • data/ai_filtered_results.json - Processed results"
echo ""
echo "🔧 Usage examples:"
echo "   • Rule-based only: python3 scraper/ai_filter.py --live"
echo "   • With Gemini API: GEMINI_API_KEY=your_key python3 scraper/ai_filter.py --live"
echo "   • Dry run: python3 scraper/ai_filter.py --dry-run"
echo ""
echo "📄 Check data/ai_filtered_results.json for structured results!"
