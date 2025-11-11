#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced Google Maps Scraping Examples
=====================================

Demonstrates advanced features including translation, proxy rotation,
concurrent processing, and custom configurations.

Author: Nextzus
Date: 2025-11-11
"""

import asyncio
import sys
import os
import time
from datetime import datetime

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from scraper.production_scraper import create_production_scraper
from search.rpc_place_search import create_rpc_search
from utils.unicode_display import safe_print, format_name, print_review_summary
from utils.anti_bot_utils import ProxyConfig, ProxyRotator
from utils.output_manager import output_manager


async def example_1_translation_enabled():
    """
    Example 1: Scraping with translation enabled
    """
    safe_print("=" * 80)
    safe_print("EXAMPLE 1: Multi-Language Scraping with Translation")
    safe_print("=" * 80)

    # Create scraper with translation features
    scraper = create_production_scraper(
        language="th",
        region="th",
        fast_mode=True,
        enable_translation=True,          # Enable translation
        target_language="en",             # Translate to English
        translate_review_text=True,       # Translate review text
        translate_owner_response=True,    # Translate owner responses
        use_enhanced_detection=True,      # Use enhanced language detection
        translation_batch_size=20         # Process in batches of 20
    )

    safe_print("Translation features enabled:")
    safe_print("  - Detect Thai/English/Japanese/Chinese languages")
    safe_print("  - Translate reviews to English")
    safe_print("  - Translate owner responses")
    safe_print("  - Enhanced detection accuracy")

    place_id = "0x30e29ecfc2f455e1:0xc4ad0280d8906604"

    # Scrape with translation
    result = await scraper.scrape_reviews(
        place_id=place_id,
        max_reviews=25,
        date_range="3months"
    )

    reviews = result['reviews']

    safe_print(f"\nTranslation Results:")
    safe_print(f"  Total reviews: {len(reviews)}")

    # Show translation statistics
    if 'translation' in result['metadata']:
        trans_stats = result['metadata']['translation']
        safe_print(f"  Texts analyzed: {trans_stats['detection_count']}")
        safe_print(f"  Texts translated: {trans_stats['translated_count']}")
        safe_print(f"  Translation errors: {trans_stats['translation_errors']}")
        safe_print(f"  Success rate: {trans_stats['translation_success_rate']:.1f}%")

        # Language distribution
        languages = trans_stats['language_distribution']['languages_found']
        safe_print(f"  Languages detected: {dict(languages)}")

    # Show translated reviews
    safe_print(f"\nSample Translated Reviews:")
    for i, review in enumerate(reviews[:3], 1):
        safe_print(f"\nReview {i}:")
        safe_print(f"  Author: {review.author_name}")
        safe_print(f"  Original Language: {review.original_language}")
        safe_print(f"  Original Text: {review.review_text[:80]}...")
        safe_print(f"  Translated Text: {review.review_text_translated[:80]}...")

        if review.owner_response:
            safe_print(f"  Owner Response (TH): {review.owner_response[:60]}...")
            safe_print(f"  Owner Response (EN): {review.owner_response_translated[:60]}...")

    return result


async def example_2_proxy_rotation():
    """
    Example 2: Proxy rotation configuration
    """
    safe_print("\n" + "=" * 80)
    safe_print("EXAMPLE 2: Proxy Rotation (Demo Configuration)")
    safe_print("=" * 80)

    # Note: This is a demo with example proxy URLs
    # Replace with actual proxy URLs for production use
    example_proxy_list = [
        "http://proxy1.example.com:8080",
        "http://proxy2.example.com:8080",
        "socks5://proxy3.example.com:1080"
    ]

    safe_print("Proxy configuration (demo - replace with real proxies):")
    for i, proxy in enumerate(example_proxy_list, 1):
        safe_print(f"  {i}. {proxy}")

    # Create scraper with proxy support
    scraper = create_production_scraper(
        language="th",
        region="th",
        fast_mode=True,
        use_proxy=True,
        proxy_list=example_proxy_list,  # Use example proxies
        max_rate=5.0  # Conservative rate with proxies
    )

    safe_print("\nProxy features enabled:")
    safe_print("  - Round-robin proxy rotation")
    safe_print("  - Automatic proxy switching on rate limits")
    safe_print("  - Support for HTTP and SOCKS5 proxies")
    safe_print("  - Conservative rate limiting")

    place_id = "0x30e29ecfc2f455e1:0xc4ad0280d8906604"

    # Scrape with proxy rotation (will fail with demo proxies, but shows setup)
    try:
        result = await scraper.scrape_reviews(
            place_id=place_id,
            max_reviews=10,
            date_range="1month"
        )

        stats = result['metadata']['stats']
        safe_print(f"\nProxy Statistics:")
        safe_print(f"  Proxy switches: {stats['proxy_switches']}")
        safe_print(f"  Rate limits: {stats['rate_limits_encountered']}")

    except Exception as e:
        safe_print(f"\nExpected error with demo proxies: {e}")
        safe_print("Replace proxy_list with actual working proxies for production use")

    return scraper


async def example_3_multilingual_search():
    """
    Example 3: Multi-language place search and scraping
    """
    safe_print("\n" + "=" * 80)
    safe_print("EXAMPLE 3: Multi-Language Search and Scraping")
    safe_print("=" * 80)

    # Search configurations
    languages = [
        {"code": "th", "region": "th", "name": "Thai"},
        {"code": "en", "region": "us", "name": "English"},
        {"code": "ja", "region": "jp", "name": "Japanese"}
    ]

    search_query = "restaurant"  # Same query in different languages

    results = {}

    for lang_config in languages:
        safe_print(f"\nSearching in {lang_config['name']}...")

        # Create search service
        search_service = create_rpc_search(
            language=lang_config["code"],
            region=lang_config["region"]
        )

        # Search for places
        places = await search_service.search_places(
            query=search_query,
            max_results=3
        )

        safe_print(f"Found {len(places)} places in {lang_config['name']}:")

        for place in places:
            safe_print(f"  - {format_name(place.name, lang_config['code'])}")
            safe_print(f"    Rating: {place.rating}/5 ({place.total_reviews} reviews)")

        results[lang_config['name']] = places

        # Small delay between searches
        await asyncio.sleep(1)

    return results


async def example_4_custom_progress_tracking():
    """
    Example 4: Custom progress tracking and callbacks
    """
    safe_print("\n" + "=" * 80)
    safe_print("EXAMPLE 4: Custom Progress Tracking")
    safe_print("=" * 80)

    # Progress tracking variables
    progress_data = {
        'start_time': None,
        'current_reviews': 0,
        'pages_processed': 0,
        'translation_progress': []
    }

    def custom_progress_callback(page_num, total_reviews, **kwargs):
        """
        Custom progress callback function
        """
        progress_data['pages_processed'] = page_num
        progress_data['current_reviews'] = total_reviews

        # Calculate elapsed time
        if progress_data['start_time']:
            elapsed = time.time() - progress_data['start_time']
            rate = total_reviews / elapsed if elapsed > 0 else 0
        else:
            rate = 0

        # Print progress
        progress_pct = (total_reviews / 50) * 100  # Assuming max 50 for demo
        safe_print(f"Progress: {progress_pct:.1f}% - Page {page_num} - {total_reviews} reviews ({rate:.1f} reviews/sec)")

        # Handle translation progress
        if 'translation_progress' in kwargs:
            trans_progress = kwargs['translation_progress']
            safe_print(f"  Translation: {trans_progress}")

        if 'detected_languages' in kwargs:
            languages = kwargs['detected_languages']
            safe_print(f"  Languages: {dict(languages)}")

    # Create scraper
    scraper = create_production_scraper(
        language="th",
        region="th",
        fast_mode=True,
        enable_translation=True,
        target_language="en",
        translation_batch_size=10
    )

    # Set start time
    progress_data['start_time'] = time.time()

    safe_print("Starting scraping with custom progress tracking...")

    # Scrape with custom callback
    result = await scraper.scrape_reviews(
        place_id="0x30e29ecfc2f455e1:0xc4ad0280d8906604",
        max_reviews=50,
        date_range="6months",
        progress_callback=custom_progress_callback
    )

    safe_print(f"\nFinal Statistics:")
    safe_print(f"  Total time: {time.time() - progress_data['start_time']:.2f}s")
    safe_print(f"  Pages processed: {progress_data['pages_processed']}")
    safe_print(f"  Total reviews: {len(result['reviews'])}")
    safe_print(f"  Final rate: {result['metadata']['rate']:.2f} reviews/sec")

    return result


async def example_5_concurrent_multi_place():
    """
    Example 5: Concurrent scraping of multiple places
    """
    safe_print("\n" + "=" * 80)
    safe_print("EXAMPLE 5: Concurrent Multi-Place Scraping")
    safe_print("=" * 80)

    # Multiple popular places in Bangkok
    places = [
        {"name": "Central World", "id": "0x30e29ecfc2f455e1:0xc4ad0280d8906604"},
        {"name": "Siam Paragon", "id": "0x3118b51bb5bfe1fd:0x3c8a1bfc5a6c5c9c"},
        {"name": "MBK Center", "id": "0x3118b51bb5bfe1fd:0x9e8e8b5a5c5c5c9c"},
        {"name": "Terminal 21", "id": "0x3118b51bb5bfe1fd:0x1d5a5a5a5c5c5c9c"}
    ]

    async def scrape_single_place(place_info, max_reviews=15):
        """
        Scrape a single place with its own scraper instance
        """
        scraper = create_production_scraper(
            language="th",
            region="th",
            fast_mode=True,
            max_rate=5.0  # Conservative for concurrent
        )

        safe_print(f"Starting scrape for {place_info['name']}...")

        try:
            result = await scraper.scrape_reviews(
                place_id=place_info['id'],
                max_reviews=max_reviews,
                date_range="3months"
            )

            safe_print(f"✓ {place_info['name']}: {len(result['reviews'])} reviews")
            return place_info['name'], result

        except Exception as e:
            safe_print(f"✗ {place_info['name']}: Error - {e}")
            return place_info['name'], None

    # Run scraping concurrently
    safe_print(f"Starting concurrent scraping of {len(places)} places...")

    start_time = time.time()

    # Create tasks for concurrent execution
    tasks = [scrape_single_place(place) for place in places]

    # Wait for all tasks to complete
    results = await asyncio.gather(*tasks, return_exceptions=True)

    total_time = time.time() - start_time

    # Process results
    total_reviews = 0
    successful_places = 0

    safe_print(f"\nConcurrent Scraping Results:")
    safe_print(f"  Total time: {total_time:.2f}s")
    safe_print(f"  Average time per place: {total_time/len(places):.2f}s")

    for result in results:
        if isinstance(result, Exception):
            safe_print(f"  Error: {result}")
        else:
            place_name, place_result = result
            if place_result:
                reviews_count = len(place_result['reviews'])
                total_reviews += reviews_count
                successful_places += 1
                safe_print(f"  ✓ {place_name}: {reviews_count} reviews")
            else:
                safe_print(f"  ✗ {place_name}: Failed")

    safe_print(f"\nSummary:")
    safe_print(f"  Successful places: {successful_places}/{len(places)}")
    safe_print(f"  Total reviews: {total_reviews}")
    safe_print(f"  Combined rate: {total_reviews/total_time:.2f} reviews/sec")

    return results


async def example_6_advanced_configuration():
    """
    Example 6: Advanced scraper configuration
    """
    safe_print("\n" + "=" * 80)
    safe_print("EXAMPLE 6: Advanced Configuration Options")
    safe_print("=" * 80)

    # Demonstrate different configuration profiles
    configs = {
        "Ultra-Fast": {
            "fast_mode": True,
            "max_rate": 15.0,
            "timeout": 20.0,
            "max_retries": 2
        },
        "Balanced": {
            "fast_mode": True,
            "max_rate": 8.0,
            "timeout": 30.0,
            "max_retries": 3
        },
        "Ultra-Safe": {
            "fast_mode": False,
            "max_rate": 2.0,
            "timeout": 60.0,
            "max_retries": 5
        }
    }

    place_id = "0x30e29ecfc2f455e1:0xc4ad0280d8906604"

    for profile_name, config_settings in configs.items():
        safe_print(f"\nTesting '{profile_name}' profile:")
        safe_print(f"  Fast mode: {config_settings['fast_mode']}")
        safe_print(f"  Max rate: {config_settings['max_rate']} req/sec")
        safe_print(f"  Timeout: {config_settings['timeout']}s")
        safe_print(f"  Max retries: {config_settings['max_retries']}")

        # Create scraper with profile
        scraper = create_production_scraper(
            language="th",
            region="th",
            **config_settings
        )

        # Small scrape to test performance
        start_time = time.time()

        result = await scraper.scrape_reviews(
            place_id=place_id,
            max_reviews=10,
            date_range="1month"
        )

        elapsed = time.time() - start_time
        rate = len(result['reviews']) / elapsed if elapsed > 0 else 0

        stats = result['metadata']['stats']

        safe_print(f"  Results:")
        safe_print(f"    Reviews: {len(result['reviews'])}")
        safe_print(f"    Time: {elapsed:.2f}s")
        safe_print(f"    Rate: {rate:.2f} reviews/sec")
        safe_print(f"    Rate limits: {stats['rate_limits_encountered']}")
        safe_print(f"    Retries: {stats['retries_used']}")

        # Small delay between profiles
        await asyncio.sleep(1)

    return configs


async def example_7_custom_data_processing():
    """
    Example 7: Custom data processing and analysis
    """
    safe_print("\n" + "=" * 80)
    safe_print("EXAMPLE 7: Custom Data Processing & Analysis")
    safe_print("=" * 80)

    scraper = create_production_scraper(
        language="th",
        region="th",
        fast_mode=True,
        enable_translation=True,
        target_language="en"
    )

    place_id = "0x30e29ecfc2f455e1:0xc4ad0280d8906604"

    # Get a larger dataset for analysis
    result = await scraper.scrape_reviews(
        place_id=place_id,
        max_reviews=50,
        date_range="6months"
    )

    reviews = result['reviews']

    safe_print(f"Analyzing {len(reviews)} reviews...")

    # Custom analysis functions
    def analyze_ratings(reviews):
        """Analyze rating distribution"""
        rating_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for review in reviews:
            rating_counts[review.rating] += 1

        total = len(reviews)
        avg_rating = sum(review.rating for review in reviews) / total

        return {
            'distribution': rating_counts,
            'average': avg_rating,
            'total': total
        }

    def analyze_language_distribution(reviews):
        """Analyze language distribution"""
        languages = {}
        for review in reviews:
            lang = review.original_language
            languages[lang] = languages.get(lang, 0) + 1

        return languages

    def analyze_review_lengths(reviews):
        """Analyze review text lengths"""
        lengths = []
        for review in reviews:
            if review.review_text:
                lengths.append(len(review.review_text))

        if lengths:
            return {
                'average': sum(lengths) / len(lengths),
                'min': min(lengths),
                'max': max(lengths),
                'total_reviews_with_text': len(lengths)
            }
        return None

    def analyze_recent_activity(reviews):
        """Analyze recent review activity"""
        recent_count = 0
        for review in reviews:
            # Simple heuristic for recent reviews
            if any(keyword in review.date_relative.lower()
                   for keyword in ['week', 'day', 'เดือน', 'สัปดาห์', 'วัน']):
                recent_count += 1

        return {
            'recent_reviews': recent_count,
            'recent_percentage': (recent_count / len(reviews)) * 100
        }

    # Perform analysis
    safe_print(f"\n📊 Review Analysis Results:")

    # Rating analysis
    rating_analysis = analyze_ratings(reviews)
    safe_print(f"\nRating Distribution:")
    safe_print(f"  Average rating: {rating_analysis['average']:.2f}/5")
    safe_print(f"  Total reviews: {rating_analysis['total']}")
    for rating in range(1, 6):
        count = rating_analysis['distribution'][rating]
        percentage = (count / rating_analysis['total']) * 100
        safe_print(f"  {rating} stars: {count} ({percentage:.1f}%)")

    # Language analysis
    language_analysis = analyze_language_distribution(reviews)
    safe_print(f"\nLanguage Distribution:")
    for lang, count in language_analysis.items():
        percentage = (count / len(reviews)) * 100
        safe_print(f"  {lang}: {count} ({percentage:.1f}%)")

    # Length analysis
    length_analysis = analyze_review_lengths(reviews)
    if length_analysis:
        safe_print(f"\nReview Length Analysis:")
        safe_print(f"  Average length: {length_analysis['average']:.0f} characters")
        safe_print(f"  Min length: {length_analysis['min']} characters")
        safe_print(f"  Max length: {length_analysis['max']} characters")
        safe_print(f"  Reviews with text: {length_analysis['total_reviews_with_text']}")

    # Recent activity
    activity_analysis = analyze_recent_activity(reviews)
    safe_print(f"\nRecent Activity:")
    safe_print(f"  Recent reviews: {activity_analysis['recent_reviews']}")
    safe_print(f"  Recent percentage: {activity_analysis['recent_percentage']:.1f}%")

    # Translation statistics
    if 'translation' in result['metadata']:
        trans_stats = result['metadata']['translation']
        safe_print(f"\nTranslation Statistics:")
        safe_print(f"  Detection accuracy: Enhanced mode enabled")
        safe_print(f"  Texts processed: {trans_stats['detection_count']}")
        safe_print(f"  Successfully translated: {trans_stats['translated_count']}")
        safe_print(f"  Translation success rate: {trans_stats['translation_success_rate']:.1f}%")

    return {
        'rating_analysis': rating_analysis,
        'language_analysis': language_analysis,
        'length_analysis': length_analysis,
        'activity_analysis': activity_analysis
    }


async def main():
    """
    Run all advanced examples
    """
    safe_print("🚀 Google Maps Scraper Framework - Advanced Examples")
    safe_print("=" * 80)

    try:
        # Run advanced examples
        await example_1_translation_enabled()
        await example_2_proxy_rotation()
        await example_3_multilingual_search()
        await example_4_custom_progress_tracking()
        await example_5_concurrent_multi_place()
        await example_6_advanced_configuration()
        await example_7_custom_data_processing()

        safe_print("\n" + "=" * 80)
        safe_print("✅ All advanced examples completed successfully!")
        safe_print("=" * 80)

    except KeyboardInterrupt:
        safe_print("\n\n⚠️ Examples interrupted by user")
    except Exception as e:
        safe_print(f"\n\n❌ Error running advanced examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Fix Windows encoding
    if sys.platform == 'win32':
        os.system('chcp 65001 > nul 2>&1')

    # Run advanced examples
    asyncio.run(main())