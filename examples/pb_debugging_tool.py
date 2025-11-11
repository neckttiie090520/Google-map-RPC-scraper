#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Maps PB Debugging Tool
==========================

Advanced debugging tool for Google Maps Protocol Buffer analysis.
Helps developers understand response structures, validate parsing, and detect changes.

Usage:
    python pb_debugging_tool.py --analyze-response sample.json
    python pb_debugging_tool.py --validate-review sample_review.json
    python pb_debugging_tool.py --analyze-pb "pb_parameter_string"
    python pb_debugging_tool.py --scrape-and-analyze PLACE_ID

Author: Nextzus
Date: 2025-11-11
"""

import asyncio
import sys
import os
import json
import argparse
from datetime import datetime
from pathlib import Path

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.pb_analyzer import GoogleMapsPBAnalyzer, pb_analyzer
from scraper.production_scraper import create_production_scraper
from utils.unicode_display import safe_print


class PBDebuggingTool:
    """Advanced debugging tool for Google Maps PB analysis"""

    def __init__(self):
        self.analyzer = GoogleMapsPBAnalyzer(debug_mode=True)
        self.results = []

    def analyze_response_file(self, filename: str):
        """Analyze Google Maps response from JSON file"""
        safe_print(f"🔍 Analyzing response file: {filename}")

        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Determine analysis type based on content
            analysis_type = self._detect_content_type(data)

            # Perform analysis
            result = self.analyzer.analyze_response_structure(data, analysis_type)
            self.results.append(result)

            # Print detailed report
            self._print_analysis_report(result)

            # Save analysis
            self._save_analysis(result, f"response_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}")

        except Exception as e:
            safe_print(f"❌ Error analyzing file: {e}")

    def analyze_pb_parameters(self, pb_string: str):
        """Analyze Protocol Buffer parameters"""
        safe_print(f"🔍 Analyzing PB parameters:")
        safe_print(f"   Input: {pb_string}")

        try:
            result = self.analyzer.analyze_pb_parameters(pb_string)
            self.results.append(result)

            # Print detailed report
            self._print_analysis_report(result)

            # Save analysis
            self._save_analysis(result, f"pb_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}")

        except Exception as e:
            safe_print(f"❌ Error analyzing PB parameters: {e}")

    def validate_review_parsing(self, filename: str, expected_fields: list = None):
        """Validate review parsing against expected fields"""
        safe_print(f"🔍 Validating review parsing: {filename}")

        try:
            with open(filename, 'r', encoding='utf-8') as f:
                review_data = json.load(f)

            result = self.analyzer.validate_review_parsing(review_data, expected_fields)
            self.results.append(result)

            # Print detailed report
            self._print_analysis_report(result)

            # Save analysis
            self._save_analysis(result, f"validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}")

        except Exception as e:
            safe_print(f"❌ Error validating review: {e}")

    async def scrape_and_analyze(self, place_id: str, max_reviews: int = 10):
        """Scrape reviews and analyze responses"""
        safe_print(f"🔍 Scraping and analyzing: {place_id}")
        safe_print(f"   Max reviews: {max_reviews}")

        try:
            # Create scraper with PB analysis enabled
            scraper = create_production_scraper(
                language="th",
                region="th",
                enable_pb_analysis=True,
                pb_analysis_verbose=True,
                save_pb_analysis=True,
                fast_mode=True
            )

            # Scrape reviews
            result = await scraper.scrape_reviews(
                place_id=place_id,
                max_reviews=max_reviews,
                date_range="1month"
            )

            # Print scraping results
            reviews = result['reviews']
            safe_print(f"✅ Scraped {len(reviews)} reviews")

            # Get PB analysis summary
            pb_summary = scraper.get_pb_analysis_summary()
            safe_print(f"\n📊 PB Analysis Summary:")
            safe_print(f"   Total analyses: {pb_summary['total_analyses']}")
            safe_print(f"   Successful: {pb_summary['successful_analyses']}")

            if pb_summary.get('analysis_types'):
                safe_print(f"   Analysis types: {dict(pb_summary['analysis_types'])}")

            if pb_summary.get('common_warnings'):
                safe_print(f"   Common warnings: {pb_summary['common_warnings']}")

            # Export PB analysis history
            scraper.export_pb_analysis_history()
            safe_print(f"✅ PB analysis history exported")

            self.results.extend(scraper.pb_analysis_results)

        except Exception as e:
            safe_print(f"❌ Error during scraping and analysis: {e}")

    def compare_structures(self, file1: str, file2: str):
        """Compare two response structures to detect changes"""
        safe_print(f"🔍 Comparing structures:")
        safe_print(f"   File 1: {file1}")
        safe_print(f"   File 2: {file2}")

        try:
            # Load both files
            with open(file1, 'r', encoding='utf-8') as f:
                data1 = json.load(f)

            with open(file2, 'r', encoding='utf-8') as f:
                data2 = json.load(f)

            # Analyze changes
            changes = self.analyzer.detect_structure_changes(data2, data1)

            safe_print(f"\n📊 Structure Comparison Results:")
            safe_print(f"   Structure changed: {changes['structure_changed']}")

            if changes.get('differences'):
                safe_print(f"   Differences: {len(changes['differences'])}")
                for diff in changes['differences'][:5]:  # Show first 5 differences
                    safe_print(f"     - {diff}")

            if changes.get('recommendations'):
                safe_print(f"\n💡 Recommendations:")
                for rec in changes['recommendations']:
                    safe_print(f"   - {rec}")

        except Exception as e:
            safe_print(f"❌ Error comparing structures: {e}")

    def generate_field_documentation(self, response_files: list):
        """Generate comprehensive field documentation from response samples"""
        safe_print(f"📚 Generating field documentation from {len(response_files)} files")

        try:
            # Load all response files
            samples = []
            for filename in response_files:
                try:
                    with open(filename, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        samples.append(data)
                        safe_print(f"   ✓ Loaded: {filename}")
                except Exception as e:
                    safe_print(f"   ✗ Failed to load {filename}: {e}")

            if not samples:
                safe_print("❌ No valid samples found")
                return

            # Generate documentation
            docs = self.analyzer.generate_field_documentation(samples)

            # Save documentation
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            doc_filename = f"field_documentation_{timestamp}.json"

            with open(doc_filename, 'w', encoding='utf-8') as f:
                json.dump(docs, f, ensure_ascii=False, indent=2)

            safe_print(f"✅ Field documentation generated: {doc_filename}")
            safe_print(f"   Fields documented: {len(docs['fields'])}")
            safe_print(f"   Sample count: {docs['sample_count']}")

            # Print summary
            safe_print(f"\n📋 Field Documentation Summary:")
            for field_name, field_docs in docs['fields'].items():
                coverage = field_docs['success_rate']
                safe_print(f"   {field_name}: {coverage:.1%} coverage")

        except Exception as e:
            safe_print(f"❌ Error generating documentation: {e}")

    def export_all_results(self, filename: str = None):
        """Export all analysis results to file"""
        if not self.results:
            safe_print("⚠️ No results to export")
            return

        try:
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"pb_debugging_results_{timestamp}.json"

            export_data = {
                'session_info': {
                    'created_at': datetime.now().isoformat(),
                    'total_analyses': len(self.results),
                    'tool_version': '1.0'
                },
                'results': [result.__dict__ for result in self.results]
            }

            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2, default=str)

            safe_print(f"✅ Results exported to: {filename}")

        except Exception as e:
            safe_print(f"❌ Error exporting results: {e}")

    # Private helper methods

    def _detect_content_type(self, data: any) -> str:
        """Detect the type of content for analysis"""
        if not isinstance(data, list):
            return "general"

        # Look for patterns
        if len(data) > 2 and isinstance(data[2], list) and len(data[2]) > 0:
            # Check if it looks like reviews data
            first_item = data[2][0] if isinstance(data[2][0], list) else data[2][0]
            if isinstance(first_item, list) and len(first_item) > 5:
                return "reviews"

        return "general"

    def _print_analysis_report(self, result):
        """Print formatted analysis report"""
        safe_print(f"\n{'='*60}")
        safe_print(f"🔍 PB Analysis Report")
        safe_print(f"{'='*60}")
        safe_print(f"Type: {result.analysis_type}")
        safe_print(f"Timestamp: {result.timestamp}")
        safe_print(f"Status: {'✅ SUCCESS' if result.success else '❌ FAILED'}")

        if result.warnings:
            safe_print(f"\n⚠️  Warnings:")
            for warning in result.warnings:
                safe_print(f"   - {warning}")

        if result.recommendations:
            safe_print(f"\n💡 Recommendations:")
            for rec in result.recommendations:
                safe_print(f"   - {rec}")

        if result.success:
            safe_print(f"\n📊 Key Findings:")

            # Print specific data based on analysis type
            if result.analysis_type == "reviews":
                data = result.data
                safe_print(f"   Structure type: {data.get('structure_type', 'unknown')}")
                safe_print(f"   Total depth: {data.get('total_depth', 0)}")
                safe_print(f"   Array count: {data.get('array_count', 0)}")

                if 'reviews_analysis' in data:
                    reviews = data['reviews_analysis']
                    safe_print(f"   Reviews section: {reviews.get('has_reviews_section', False)}")
                    safe_print(f"   Estimated reviews: {reviews.get('estimated_review_count', 0)}")

            elif result.analysis_type == "pb_parameters":
                data = result.data
                safe_print(f"   Place ID found: {data.get('place_id_extracted', 'N/A')}")
                safe_print(f"   Components: {len(data.get('components', []))}")

            elif result.analysis_type == "review_validation":
                data = result.data
                safe_print(f"   Field coverage: {data.get('field_coverage', 0):.1%}")
                safe_print(f"   Found fields: {len(data.get('found_fields', []))}")
                safe_print(f"   Missing fields: {len(data.get('missing_fields', []))}")

        safe_print(f"{'='*60}\n")

    def _save_analysis(self, result, base_filename):
        """Save analysis result to file"""
        try:
            # Create pb_debug directory
            pb_dir = Path("pb_debug")
            pb_dir.mkdir(exist_ok=True)

            # Save detailed analysis
            filename = f"{base_filename}.json"
            filepath = pb_dir / filename

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(result.__dict__, f, ensure_ascii=False, indent=2, default=str)

            safe_print(f"💾 Analysis saved: {filepath}")

        except Exception as e:
            safe_print(f"⚠️ Failed to save analysis: {e}")


async def main():
    """Main function with CLI interface"""
    parser = argparse.ArgumentParser(
        description="Google Maps PB Debugging Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze response file
  python pb_debugging_tool.py --analyze-response sample_response.json

  # Analyze PB parameters
  python pb_debugging_tool.py --analyze-pb "!1m6!1splace_id!6m4..."

  # Validate review parsing
  python pb_debugging_tool.py --validate-review sample_review.json

  # Scrape and analyze in real-time
  python pb_debugging_tool.py --scrape-and-analyze 0x30e29ecfc2f455e1:0xc4ad0280d8906604

  # Compare structures
  python pb_debugging_tool.py --compare old_response.json new_response.json

  # Generate field documentation
  python pb_debugging_tool.py --generate-docs *.json
        """
    )

    # Analysis options
    parser.add_argument('--analyze-response', help='Analyze response from JSON file')
    parser.add_argument('--analyze-pb', help='Analyze Protocol Buffer parameters')
    parser.add_argument('--validate-review', help='Validate review parsing from JSON file')
    parser.add_argument('--scrape-and-analyze', help='Scrape reviews and analyze responses')
    parser.add_argument('--compare', nargs=2, metavar=('FILE1', 'FILE2'), help='Compare two response files')
    parser.add_argument('--generate-docs', nargs='+', help='Generate field documentation from response files')

    # Options
    parser.add_argument('--max-reviews', type=int, default=10, help='Max reviews to scrape (default: 10)')
    parser.add_argument('--expected-fields', nargs='+', help='Expected field names for validation')
    parser.add_argument('--export-results', help='Export all results to file')

    args = parser.parse_args()

    # Fix Windows encoding
    if sys.platform == 'win32':
        os.system('chcp 65001 > nul 2>&1')

    # Create debugging tool
    tool = PBDebuggingTool()

    try:
        # Execute requested action
        if args.analyze_response:
            tool.analyze_response_file(args.analyze_response)

        elif args.analyze_pb:
            tool.analyze_pb_parameters(args.analyze_pb)

        elif args.validate_review:
            tool.validate_review_parsing(args.validate_review, args.expected_fields)

        elif args.scrape_and_analyze:
            await tool.scrape_and_analyze(args.scrape_and_analyze, args.max_reviews)

        elif args.compare:
            tool.compare_structures(args.compare[0], args.compare[1])

        elif args.generate_docs:
            tool.generate_field_documentation(args.generate_docs)

        else:
            parser.print_help()
            return

        # Export results if requested
        if args.export_results or tool.results:
            tool.export_all_results(args.export_results)

        safe_print("🎉 PB debugging completed successfully!")

    except KeyboardInterrupt:
        safe_print("\n⚠️ Debugging interrupted by user")
    except Exception as e:
        safe_print(f"\n❌ Debugging failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())