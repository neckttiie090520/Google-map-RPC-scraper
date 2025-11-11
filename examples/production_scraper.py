#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Production-Ready Google Maps Scraper
==================================

A complete, production-ready script for scraping Google Maps reviews.
Includes error handling, logging, progress tracking, and data export.

Usage:
    python production_scraper.py --place-id "PLACE_ID" --max-reviews 1000
    python production_scraper.py --search "restaurants in bangkok" --max-reviews 500

Author: Nextzus
Date: 2025-11-11
"""

import asyncio
import sys
import os
import argparse
import json
import csv
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from scraper.production_scraper import create_production_scraper
from search.rpc_place_search import create_rpc_search
from utils.unicode_display import safe_print, format_name, print_review_summary
from utils.output_manager import output_manager


class ProductionScraper:
    """
    Production-ready Google Maps scraper with comprehensive features
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize production scraper

        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.scraper = None
        self.search_service = None
        self.results = []

        # Initialize components
        self._setup_scraper()
        self._setup_search_service()

    def _setup_scraper(self):
        """Setup the main scraper with configuration"""
        self.scraper = create_production_scraper(
            language=self.config.get('language', 'th'),
            region=self.config.get('region', 'th'),
            fast_mode=self.config.get('fast_mode', True),
            max_rate=self.config.get('max_rate', 10.0),
            use_proxy=self.config.get('use_proxy', False),
            proxy_list=self.config.get('proxy_list'),
            timeout=self.config.get('timeout', 30.0),
            max_retries=self.config.get('max_retries', 3),
            enable_translation=self.config.get('enable_translation', False),
            target_language=self.config.get('target_language', 'en'),
            translate_review_text=self.config.get('translate_review_text', True),
            translate_owner_response=self.config.get('translate_owner_response', True),
            use_enhanced_detection=self.config.get('use_enhanced_detection', True),
            translation_batch_size=self.config.get('translation_batch_size', 50)
        )

        safe_print(f"✓ Scraper initialized with {self.config.get('language', 'th')} language")

    def _setup_search_service(self):
        """Setup place search service"""
        self.search_service = create_rpc_search(
            language=self.config.get('language', 'th'),
            region=self.config.get('region', 'th')
        )

        safe_print(f"✓ Search service initialized")

    async def search_places(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Search for places

        Args:
            query: Search query
            max_results: Maximum results to return

        Returns:
            List of place dictionaries
        """
        safe_print(f"\n🔍 Searching for: {query}")
        safe_print(f"   Max results: {max_results}")

        try:
            places = await self.search_service.search_places(
                query=query,
                max_results=max_results
            )

            safe_print(f"✓ Found {len(places)} places")

            # Convert to dictionaries
            place_dicts = []
            for place in places:
                place_dict = {
                    'place_id': place.place_id,
                    'name': place.name,
                    'address': place.address,
                    'rating': place.rating,
                    'total_reviews': place.total_reviews,
                    'category': place.category,
                    'url': place.url,
                    'latitude': place.latitude,
                    'longitude': place.longitude
                }
                place_dicts.append(place_dict)

            return place_dicts

        except Exception as e:
            safe_print(f"✗ Search failed: {e}")
            return []

    async def scrape_reviews(self, place_id: str, place_name: str = None,
                           max_reviews: int = 1000, date_range: str = "1year",
                           progress_callback=None) -> Dict[str, Any]:
        """
        Scrape reviews for a place

        Args:
            place_id: Google Maps place ID
            place_name: Optional place name for logging
            max_reviews: Maximum reviews to scrape
            date_range: Date range filter
            progress_callback: Optional progress callback

        Returns:
            Scraping result dictionary
        """
        place_display = place_name or place_id[:20] + "..."
        safe_print(f"\n📊 Scraping reviews for: {place_display}")
        safe_print(f"   Place ID: {place_id}")
        safe_print(f"   Max reviews: {max_reviews}")
        safe_print(f"   Date range: {date_range}")

        # Create default progress callback if none provided
        if progress_callback is None:
            def default_progress(page_num, total_reviews, **kwargs):
                progress = (total_reviews / max_reviews) * 100
                safe_print(f"   Progress: {progress:.1f}% - Page {page_num} - {total_reviews} reviews")
            progress_callback = default_progress

        try:
            result = await self.scraper.scrape_reviews(
                place_id=place_id,
                max_reviews=max_reviews,
                date_range=date_range,
                progress_callback=progress_callback
            )

            reviews = result['reviews']
            metadata = result['metadata']

            safe_print(f"✓ Scraping completed!")
            safe_print(f"   Reviews scraped: {len(reviews)}")
            safe_print(f"   Time taken: {metadata['time_taken']:.2f}s")
            safe_print(f"   Rate: {metadata['rate']:.2f} reviews/sec")

            # Show statistics
            stats = metadata.get('stats', {})
            if stats:
                safe_print(f"   Total requests: {stats.get('total_requests', 0)}")
                safe_print(f"   Rate limits: {stats.get('rate_limits_encountered', 0)}")
                safe_print(f"   Retries: {stats.get('retries_used', 0)}")

            return result

        except Exception as e:
            safe_print(f"✗ Scraping failed: {e}")
            return {'reviews': [], 'metadata': {}}

    async def scrape_multiple_places(self, places: List[Dict], max_reviews_per_place: int = 100,
                                  delay_between_places: float = 2.0) -> Dict[str, Any]:
        """
        Scrape reviews for multiple places

        Args:
            places: List of place dictionaries
            max_reviews_per_place: Max reviews per place
            delay_between_places: Delay between places

        Returns:
            Combined results dictionary
        """
        safe_print(f"\n🔄 Starting multi-place scraping for {len(places)} places")
        safe_print(f"   Max reviews per place: {max_reviews_per_place}")
        safe_print(f"   Delay between places: {delay_between_places}s")

        all_results = []
        place_summaries = []
        total_start_time = time.time()

        for i, place in enumerate(places, 1):
            safe_print(f"\n[{i}/{len(places)}] Processing: {place['name']}")

            # Scrape reviews for this place
            result = await self.scrape_reviews(
                place_id=place['place_id'],
                place_name=place['name'],
                max_reviews=max_reviews_per_place,
                date_range=self.config.get('date_range', '1year')
            )

            if result['reviews']:
                # Add place information to each review
                for review in result['reviews']:
                    review.place_name = place['name']
                    review.place_address = place.get('address', '')
                    review.place_category = place.get('category', '')

                all_results.extend(result['reviews'])

                # Store summary for this place
                summary = {
                    'place_name': place['name'],
                    'place_id': place['place_id'],
                    'reviews_count': len(result['reviews']),
                    'average_rating': sum(r.rating for r in result['reviews']) / len(result['reviews']),
                    'scraping_time': result['metadata']['time_taken'],
                    'scraping_rate': result['metadata']['rate']
                }
                place_summaries.append(summary)

                safe_print(f"   ✓ {len(result['reviews'])} reviews scraped")
            else:
                safe_print(f"   ✗ No reviews scraped")

            # Delay between places
            if i < len(places):  # Don't delay after last place
                safe_print(f"   ⏳ Waiting {delay_between_places}s before next place...")
                await asyncio.sleep(delay_between_places)

        # Calculate combined statistics
        total_time = time.time() - total_start_time
        total_reviews = len(all_results)

        safe_print(f"\n✓ Multi-place scraping completed!")
        safe_print(f"   Total places: {len(places)}")
        safe_print(f"   Total reviews: {total_reviews}")
        safe_print(f"   Total time: {total_time:.2f}s")
        safe_print(f"   Combined rate: {total_reviews/total_time:.2f} reviews/sec")

        return {
            'reviews': all_results,
            'place_summaries': place_summaries,
            'metadata': {
                'total_places': len(places),
                'total_reviews': total_reviews,
                'total_time': total_time,
                'combined_rate': total_reviews / total_time if total_time > 0 else 0,
                'date_range': self.config.get('date_range', '1year')
            }
        }

    def export_to_csv(self, reviews: List[Any], filename: str) -> str:
        """
        Export reviews to CSV file

        Args:
            reviews: List of review objects
            filename: Output filename

        Returns:
            Path to saved file
        """
        safe_print(f"\n💾 Exporting {len(reviews)} reviews to CSV: {filename}")

        try:
            # Determine headers based on available data
            has_translation = any(hasattr(r, 'review_text_translated') and r.review_text_translated for r in reviews)
            has_language = any(hasattr(r, 'original_language') and r.original_language for r in reviews)
            has_place_info = any(hasattr(r, 'place_name') and r.place_name for r in reviews)

            headers = ['review_id', 'author_name', 'rating', 'date_formatted', 'date_relative', 'review_text']

            if has_place_info:
                headers.extend(['place_name', 'place_address', 'place_category'])

            if has_language:
                headers.extend(['original_language', 'target_language'])

            if has_translation:
                headers.append('review_text_translated')

            headers.extend(['review_likes', 'review_photos_count', 'owner_response', 'page_number'])

            # Write CSV
            with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(headers)

                for review in reviews:
                    row = [
                        getattr(review, 'review_id', ''),
                        getattr(review, 'author_name', ''),
                        getattr(review, 'rating', 0),
                        getattr(review, 'date_formatted', ''),
                        getattr(review, 'date_relative', ''),
                        getattr(review, 'review_text', '')
                    ]

                    if has_place_info:
                        row.extend([
                            getattr(review, 'place_name', ''),
                            getattr(review, 'place_address', ''),
                            getattr(review, 'place_category', '')
                        ])

                    if has_language:
                        row.extend([
                            getattr(review, 'original_language', ''),
                            getattr(review, 'target_language', '')
                        ])

                    if has_translation:
                        row.append(getattr(review, 'review_text_translated', ''))

                    row.extend([
                        getattr(review, 'review_likes', 0),
                        getattr(review, 'review_photos_count', 0),
                        getattr(review, 'owner_response', ''),
                        getattr(review, 'page_number', 0)
                    ])

                    writer.writerow(row)

            safe_print(f"✓ CSV exported successfully: {filename}")
            return filename

        except Exception as e:
            safe_print(f"✗ CSV export failed: {e}")
            return None

    def export_to_json(self, result: Dict[str, Any], filename: str) -> str:
        """
        Export results to JSON file

        Args:
            result: Results dictionary
            filename: Output filename

        Returns:
            Path to saved file
        """
        safe_print(f"\n💾 Exporting results to JSON: {filename}")

        try:
            # Convert reviews to dictionaries
            reviews_data = []
            for review in result.get('reviews', []):
                if hasattr(review, '__dict__'):
                    review_dict = review.__dict__.copy()
                else:
                    review_dict = review

                # Remove any non-serializable objects
                for key, value in list(review_dict.items()):
                    if not isinstance(value, (str, int, float, bool, list, dict, type(None))):
                        review_dict[key] = str(value)

                reviews_data.append(review_dict)

            # Create complete export data
            export_data = {
                'export_info': {
                    'exported_at': datetime.now().isoformat(),
                    'total_reviews': len(reviews_data),
                    'scraper_config': self.config
                },
                'metadata': result.get('metadata', {}),
                'reviews': reviews_data
            }

            # Add place summaries if available
            if 'place_summaries' in result:
                export_data['place_summaries'] = result['place_summaries']

            # Write JSON
            with open(filename, 'w', encoding='utf-8') as jsonfile:
                json.dump(export_data, jsonfile, ensure_ascii=False, indent=2)

            safe_print(f"✓ JSON exported successfully: {filename}")
            return filename

        except Exception as e:
            safe_print(f"✗ JSON export failed: {e}")
            return None

    def generate_summary_report(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive summary report

        Args:
            result: Scraping results

        Returns:
            Summary report dictionary
        """
        reviews = result.get('reviews', [])

        if not reviews:
            return {'error': 'No reviews to analyze'}

        safe_print(f"\n📈 Generating summary report for {len(reviews)} reviews...")

        # Basic statistics
        total_reviews = len(reviews)
        ratings = [r.rating for r in reviews if r.rating]
        avg_rating = sum(ratings) / len(ratings) if ratings else 0

        # Rating distribution
        rating_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for rating in ratings:
            rating_counts[rating] += 1

        # Language analysis (if translation enabled)
        language_analysis = {}
        if any(hasattr(r, 'original_language') for r in reviews):
            languages = {}
            for review in reviews:
                lang = getattr(review, 'original_language', 'unknown')
                languages[lang] = languages.get(lang, 0) + 1
            language_analysis = languages

        # Date analysis
        dates = [r.date_formatted for r in reviews if r.date_formatted and r.date_formatted != "Unknown Date"]
        unique_dates = len(set(dates)) if dates else 0

        # Reviews with photos
        reviews_with_photos = sum(1 for r in reviews if getattr(r, 'review_photos_count', 0) > 0)

        # Reviews with owner responses
        reviews_with_responses = sum(1 for r in reviews if getattr(r, 'owner_response', ''))

        # Reviews with likes
        total_likes = sum(getattr(r, 'review_likes', 0) for r in reviews)
        reviews_with_likes = sum(1 for r in reviews if getattr(r, 'review_likes', 0) > 0)

        # Place analysis (if multi-place)
        place_analysis = {}
        if any(hasattr(r, 'place_name') for r in reviews):
            places = {}
            for review in reviews:
                place = getattr(review, 'place_name', 'Unknown')
                if place not in places:
                    places[place] = {'count': 0, 'ratings': []}
                places[place]['count'] += 1
                if review.rating:
                    places[place]['ratings'].append(review.rating)

            # Calculate averages per place
            for place in places:
                if places[place]['ratings']:
                    places[place]['avg_rating'] = sum(places[place]['ratings']) / len(places[place]['ratings'])
                else:
                    places[place]['avg_rating'] = 0
                places[place]['rating_count'] = len(places[place]['ratings'])

            place_analysis = places

        # Create summary
        summary = {
            'overview': {
                'total_reviews': total_reviews,
                'average_rating': round(avg_rating, 2),
                'date_range': result.get('metadata', {}).get('date_range', 'unknown'),
                'scraping_rate': result.get('metadata', {}).get('rate', 0),
                'total_time': result.get('metadata', {}).get('time_taken', 0)
            },
            'rating_analysis': {
                'distribution': rating_counts,
                'average_rating': round(avg_rating, 2),
                'total_rated_reviews': len(ratings)
            },
            'content_analysis': {
                'unique_dates': unique_dates,
                'reviews_with_photos': reviews_with_photos,
                'reviews_with_responses': reviews_with_responses,
                'total_likes': total_likes,
                'reviews_with_likes': reviews_with_likes
            },
            'language_analysis': language_analysis,
            'place_analysis': place_analysis
        }

        # Print summary
        safe_print(f"\n📊 Summary Report:")
        safe_print(f"   Total Reviews: {summary['overview']['total_reviews']}")
        safe_print(f"   Average Rating: {summary['overview']['average_rating']}/5")
        safe_print(f"   Scraping Rate: {summary['overview']['scraping_rate']:.2f} reviews/sec")

        safe_print(f"\nRating Distribution:")
        for rating in range(1, 6):
            count = summary['rating_analysis']['distribution'][rating]
            percentage = (count / summary['rating_analysis']['total_rated_reviews']) * 100
            safe_print(f"   {rating} stars: {count} ({percentage:.1f}%)")

        if language_analysis:
            safe_print(f"\nLanguage Distribution:")
            for lang, count in language_analysis.items():
                percentage = (count / total_reviews) * 100
                safe_print(f"   {lang}: {count} ({percentage:.1f}%)")

        if place_analysis:
            safe_print(f"\nPlace Breakdown:")
            for place, data in place_analysis.items():
                safe_print(f"   {place}: {data['count']} reviews (avg: {data['avg_rating']:.1f}/5)")

        safe_print(f"\nContent Insights:")
        safe_print(f"   Reviews with photos: {reviews_with_photos}")
        safe_print(f"   Reviews with responses: {reviews_with_responses}")
        safe_print(f"   Total likes: {total_likes}")

        return summary


async def main():
    """
    Main function with command-line interface
    """
    parser = argparse.ArgumentParser(
        description="Production Google Maps Scraper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scrape reviews for a specific place
  python production_scraper.py --place-id "0x30e29ecfc2f455e1:0xc4ad0280d8906604" --max-reviews 100

  # Search for places and scrape reviews
  python production_scraper.py --search "restaurants in bangkok" --max-results 5 --max-reviews 50

  # Enable translation
  python production_scraper.py --place-id "PLACE_ID" --translate --target-language en

  # Use conservative mode
  python production_scraper.py --place-id "PLACE_ID" --conservative --max-reviews 1000

  # Scrape multiple places
  python production_scraper.py --search "malls in bangkok" --max-results 3 --max-reviews 100 --multi
        """
    )

    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('--place-id', help='Google Maps place ID')
    input_group.add_argument('--search', help='Search query to find places')

    # Scraping options
    parser.add_argument('--max-reviews', type=int, default=100, help='Maximum reviews to scrape per place (default: 100)')
    parser.add_argument('--max-results', type=int, default=10, help='Maximum search results (default: 10)')
    parser.add_argument('--date-range', default='1year', choices=['1month', '6months', '1year', '5years', '7years', 'all'], help='Date range filter (default: 1year)')
    parser.add_argument('--multi', action='store_true', help='Scrape multiple places when using search')

    # Language and translation options
    parser.add_argument('--language', default='th', choices=['th', 'en', 'ja', 'zh-CN'], help='Interface language (default: th)')
    parser.add_argument('--region', default='th', help='Region code (default: th)')
    parser.add_argument('--translate', action='store_true', help='Enable translation')
    parser.add_argument('--target-language', default='en', choices=['th', 'en'], help='Target language for translation (default: en)')

    # Performance options
    parser.add_argument('--fast', action='store_true', default=True, help='Use fast mode (default: enabled)')
    parser.add_argument('--conservative', action='store_true', help='Use conservative mode (overrides --fast)')
    parser.add_argument('--max-rate', type=float, default=10.0, help='Maximum requests per second (default: 10.0)')
    parser.add_argument('--timeout', type=float, default=30.0, help='Request timeout in seconds (default: 30.0)')

    # Output options
    parser.add_argument('--output-dir', default='outputs', help='Output directory (default: outputs)')
    parser.add_argument('--export-csv', action='store_true', help='Export to CSV format')
    parser.add_argument('--export-json', action='store_true', default=True, help='Export to JSON format (default: enabled)')
    parser.add_argument('--no-export', action='store_true', help='Skip file export')

    # Proxy options
    parser.add_argument('--use-proxy', action='store_true', help='Enable proxy rotation')
    parser.add_argument('--proxy-list', help='Comma-separated list of proxy URLs')

    args = parser.parse_args()

    # Configure scraper settings
    config = {
        'language': args.language,
        'region': args.region,
        'fast_mode': args.fast and not args.conservative,
        'max_rate': args.max_rate,
        'timeout': args.timeout,
        'enable_translation': args.translate,
        'target_language': args.target_language,
        'date_range': args.date_range,
        'use_proxy': args.use_proxy,
        'proxy_list': args.proxy_list.split(',') if args.proxy_list else None
    }

    # Adjust mode if conservative
    if args.conservative:
        config['fast_mode'] = False
        config['max_rate'] = 3.0
        config['timeout'] = 60.0
        safe_print("🛡️ Using conservative mode for maximum safety")

    # Create scraper
    scraper = ProductionScraper(config)

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        if args.place_id:
            # Single place scraping
            safe_print(f"🎯 Single place mode: {args.place_id}")

            result = await scraper.scrape_reviews(
                place_id=args.place_id,
                max_reviews=args.max_reviews,
                date_range=args.date_range
            )

            # Generate summary
            summary = scraper.generate_summary_report(result)

            # Export results
            if not args.no_export:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

                if args.export_json:
                    json_file = output_dir / f"reviews_{timestamp}.json"
                    scraper.export_to_json(result, str(json_file))

                if args.export_csv:
                    csv_file = output_dir / f"reviews_{timestamp}.csv"
                    scraper.export_to_csv(result['reviews'], str(csv_file))

                # Save summary
                summary_file = output_dir / f"summary_{timestamp}.json"
                with open(summary_file, 'w', encoding='utf-8') as f:
                    json.dump(summary, f, ensure_ascii=False, indent=2)
                safe_print(f"✓ Summary saved: {summary_file}")

        else:
            # Search and scrape
            safe_print(f"🔍 Search mode: {args.search}")

            places = await scraper.search_places(args.search, args.max_results)

            if not places:
                safe_print("❌ No places found")
                return

            if args.multi and len(places) > 1:
                # Multi-place scraping
                safe_print(f"🔄 Multi-place mode: {len(places)} places")

                result = await scraper.scrape_multiple_places(
                    places=places,
                    max_reviews_per_place=args.max_reviews
                )
            else:
                # Single place from search results
                place = places[0]
                safe_print(f"🎯 Using first search result: {place['name']}")

                result = await scraper.scrape_reviews(
                    place_id=place['place_id'],
                    place_name=place['name'],
                    max_reviews=args.max_reviews,
                    date_range=args.date_range
                )

            # Generate summary
            summary = scraper.generate_summary_report(result)

            # Export results
            if not args.no_export:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                query_safe = ''.join(c for c in args.search if c.isalnum() or c in (' ', '-', '_')).rstrip()[:30]

                if args.export_json:
                    json_file = output_dir / f"{query_safe}_{timestamp}.json"
                    scraper.export_to_json(result, str(json_file))

                if args.export_csv:
                    csv_file = output_dir / f"{query_safe}_{timestamp}.csv"
                    scraper.export_to_csv(result['reviews'], str(csv_file))

                # Save summary
                summary_file = output_dir / f"{query_safe}_summary_{timestamp}.json"
                with open(summary_file, 'w', encoding='utf-8') as f:
                    json.dump(summary, f, ensure_ascii=False, indent=2)
                safe_print(f"✓ Summary saved: {summary_file}")

        safe_print(f"\n🎉 Scraping completed successfully!")
        safe_print(f"📁 Output directory: {output_dir.absolute()}")

    except KeyboardInterrupt:
        safe_print(f"\n⚠️ Scraping interrupted by user")
        sys.exit(1)
    except Exception as e:
        safe_print(f"\n❌ Scraping failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    # Fix Windows encoding
    if sys.platform == 'win32':
        os.system('chcp 65001 > nul 2>&1')

    # Run production scraper
    asyncio.run(main())