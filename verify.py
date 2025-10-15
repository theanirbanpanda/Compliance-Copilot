#!/usr/bin/env python3
"""
Verification Report Module for Compliance Copilot
Generates comprehensive CLI reports and logs for the AI filtering pipeline.
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime, timezone
from collections import Counter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class VerificationReport:
    """Generates comprehensive verification reports for the AI filtering pipeline."""
    
    def __init__(self, data_dir: str = "data", downloads_dir: str = "downloads"):
        self.data_dir = Path(data_dir)
        self.downloads_dir = Path(downloads_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.downloads_dir.mkdir(exist_ok=True)
    
    def count_pdf_files(self) -> int:
        """Count PDF files in downloads directory."""
        if not self.downloads_dir.exists():
            return 0
        return len(list(self.downloads_dir.glob("*.pdf")))
    
    def analyze_merged_output(self) -> Dict[str, Any]:
        """Analyze the merged output file."""
        merged_file = self.downloads_dir / "merged_output.txt"
        
        if not merged_file.exists():
            return {
                "exists": False,
                "size": 0,
                "characters": 0,
                "files_processed": 0
            }
        
        try:
            with open(merged_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Count files processed (by BEGIN FILE markers)
            files_processed = content.count("===== BEGIN FILE:")
            
            return {
                "exists": True,
                "size": merged_file.stat().st_size,
                "characters": len(content),
                "files_processed": files_processed,
                "path": str(merged_file)
            }
        except Exception as e:
            logger.error(f"Error analyzing merged output: {e}")
            return {
                "exists": False,
                "size": 0,
                "characters": 0,
                "files_processed": 0,
                "error": str(e)
            }
    
    def analyze_ai_results(self) -> Dict[str, Any]:
        """Analyze the AI filtered results JSON file."""
        results_file = self.data_dir / "ai_filtered_results.json"
        
        if not results_file.exists():
            return {
                "exists": False,
                "chunks_processed": 0,
                "tags_summary": {},
                "years_detected": [],
                "processing_methods": {}
            }
        
        try:
            with open(results_file, 'r', encoding='utf-8') as f:
                results = json.load(f)
            
            # Analyze results
            chunks_processed = len(results)
            all_tags = []
            all_years = []
            processing_methods = []
            
            for result in results:
                all_tags.extend(result.get('tags', []))
                all_years.extend(result.get('detected_years', []))
                processing_methods.append(result.get('processing_method', 'unknown'))
            
            # Count tags
            tag_counts = Counter(all_tags)
            year_counts = Counter(all_years)
            method_counts = Counter(processing_methods)
            
            return {
                "exists": True,
                "chunks_processed": chunks_processed,
                "tags_summary": dict(tag_counts),
                "years_detected": sorted(set(all_years)),
                "year_counts": dict(year_counts),
                "processing_methods": dict(method_counts),
                "path": str(results_file)
            }
        except Exception as e:
            logger.error(f"Error analyzing AI results: {e}")
            return {
                "exists": False,
                "chunks_processed": 0,
                "tags_summary": {},
                "years_detected": [],
                "processing_methods": {},
                "error": str(e)
            }
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive verification report."""
        print("🔍 Compliance Copilot - Verification Report")
        print("=" * 60)
        
        # Count PDFs
        pdf_count = self.count_pdf_files()
        print(f"📄 PDF Files in downloads/: {pdf_count}")
        
        # Analyze merged output
        merged_analysis = self.analyze_merged_output()
        if merged_analysis["exists"]:
            print(f"📝 Merged Output: ✅ Found")
            print(f"   Files processed: {merged_analysis['files_processed']}")
            print(f"   Total characters: {merged_analysis['characters']:,}")
            print(f"   File size: {merged_analysis['size']:,} bytes")
        else:
            print(f"📝 Merged Output: ❌ Not found")
        
        # Analyze AI results
        ai_analysis = self.analyze_ai_results()
        if ai_analysis["exists"]:
            print(f"\n🤖 AI Filtered Results: ✅ Found")
            print(f"   Chunks processed: {ai_analysis['chunks_processed']}")
            
            # Tags summary
            if ai_analysis["tags_summary"]:
                print(f"   Tags detected: {len(ai_analysis['tags_summary'])}")
                print("   Tag distribution:")
                for tag, count in sorted(ai_analysis["tags_summary"].items(), key=lambda x: x[1], reverse=True):
                    print(f"     • {tag}: {count}")
            else:
                print("   Tags detected: 0")
            
            # Years detected
            if ai_analysis["years_detected"]:
                print(f"   Years detected: {len(ai_analysis['years_detected'])}")
                print(f"   Years: {sorted(ai_analysis['years_detected'])}")
            else:
                print("   Years detected: 0")
            
            # Processing methods
            if ai_analysis["processing_methods"]:
                print("   Processing methods:")
                for method, count in ai_analysis["processing_methods"].items():
                    print(f"     • {method}: {count}")
        else:
            print(f"\n🤖 AI Filtered Results: ❌ Not found")
        
        # Summary statistics
        print(f"\n📊 Pipeline Summary:")
        print(f"   PDF files found: {pdf_count}")
        print(f"   Files processed: {merged_analysis.get('files_processed', 0)}")
        print(f"   Text characters: {merged_analysis.get('characters', 0):,}")
        print(f"   Chunks created: {ai_analysis.get('chunks_processed', 0)}")
        print(f"   Unique tags: {len(ai_analysis.get('tags_summary', {}))}")
        print(f"   Years detected: {len(ai_analysis.get('years_detected', []))}")
        
        # Save report to file
        report_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "pdf_count": pdf_count,
            "merged_output": merged_analysis,
            "ai_results": ai_analysis,
            "summary": {
                "total_pdfs": pdf_count,
                "files_processed": merged_analysis.get('files_processed', 0),
                "total_characters": merged_analysis.get('characters', 0),
                "chunks_processed": ai_analysis.get('chunks_processed', 0),
                "unique_tags": len(ai_analysis.get('tags_summary', {})),
                "years_detected": len(ai_analysis.get('years_detected', []))
            }
        }
        
        # Save report to JSON
        report_file = self.data_dir / "verification_report.json"
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Verification report saved: {report_file}")
        except Exception as e:
            logger.error(f"Failed to save verification report: {e}")
        
        return report_data
    
    def check_pipeline_health(self) -> bool:
        """Check if the pipeline is healthy and complete."""
        merged_analysis = self.analyze_merged_output()
        ai_analysis = self.analyze_ai_results()
        
        # Check if we have the essential files
        has_merged = merged_analysis["exists"] and merged_analysis["characters"] > 0
        has_ai_results = ai_analysis["exists"] and ai_analysis["chunks_processed"] > 0
        
        print(f"\n🏥 Pipeline Health Check:")
        print(f"   Merged output: {'✅' if has_merged else '❌'}")
        print(f"   AI results: {'✅' if has_ai_results else '❌'}")
        
        if has_merged and has_ai_results:
            print("   Overall status: ✅ HEALTHY")
            return True
        else:
            print("   Overall status: ❌ NEEDS ATTENTION")
            return False

def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Verification Report for Compliance Copilot')
    parser.add_argument('--data-dir', default='data', help='Data directory path')
    parser.add_argument('--downloads-dir', default='downloads', help='Downloads directory path')
    parser.add_argument('--health-check', action='store_true', help='Run health check only')
    
    args = parser.parse_args()
    
    verifier = VerificationReport(args.data_dir, args.downloads_dir)
    
    if args.health_check:
        health = verifier.check_pipeline_health()
        sys.exit(0 if health else 1)
    else:
        report = verifier.generate_report()
        health = verifier.check_pipeline_health()
        sys.exit(0 if health else 1)

if __name__ == "__main__":
    main()
