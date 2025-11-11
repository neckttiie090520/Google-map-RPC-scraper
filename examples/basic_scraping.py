#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Basic Google Maps Scraping Examples
==================================

Demonstrates fundamental usage of the Google Maps scraper framework.
Includes place search, review scraping, and basic configuration.

Author: Nextzus
Date: 2025-11-11
"""

import asyncio
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from scraper.production_scraper import create_production_scraper
from search.rpc_place_search import create_rpc_search
from utils.unicode_display import safe_print, format_name
from utils.output_manager import output_manager


async def example_1_basic_review_scraping():
    """
    Example 1: Basic review scraping with Thai language
    """
    safe_print("=" * 80)
    safe_print("EXAMPLE 1: Basic Review Scraping (Thai)")
    safe_print("=" * 80)

    # Create scraper with default settings
    scraper = create_production_scraper(
        language="th",
        region="th",
        fast_mode=True,    # Optimized for performance
        max_rate=10.0      # 10 requests/sec max
    )

    # Central World Bangkok - popular location with many reviews
    place_id = "0x30e29ecfc2f455e1:0xc4ad0280d8906604"

    safe_print(f"Scraping reviews for: Central World Bangkok")
    safe_print(f"Place ID: {place_id}")

    # Scrape reviews
    result = await scraper.scrape_reviews(
        place_id=place_id,
        max_reviews=20,      # Small number for demo
        date_range="1year"   # Last year only
    )

    # Display results
    reviews = result['reviews']
    metadata = result['metadata']

    safe_print(f"\nResults:")
    safe_print(f"  Total reviews scraped: {len(reviews)}")
    safe_print(f"  Time taken: {metadata['time_taken']:.2f}s")
    safe_print(f"  Rate: {metadata['rate']:.2f} reviews/sec")

    # Show first few reviews
    safe_print(f"\nFirst 3 reviews:")
    for i, review in enumerate(reviews[:3], 1):
        safe_print(f"\nReview {i}:")
        safe_print(f"  Author: {format_name(review.author_name, 'unknown')}")
        safe_print(f"  Rating: {review.rating}/5")
        safe_print(f"  Date: {review.date_relative}")
        safe_print(f"  Text: {review.review_text[:100]}...")

    return result


async def example_2_english_scraping():
    """
    Example 2: Scraping in English language
    """
    safe_print("\n" + "=" * 80)
    safe_print("EXAMPLE 2: English Language Scraping")
    safe_print("=" * 80)

    # Create scraper for English
    scraper = create_production_scraper(
        language="en",
        region="us",
        fast_mode=True,
        max_rate=10.0
    )

    # Same place, but in English
    place_id = "0x30e29ecfc2f455e1:0xc4ad0280d8906604"

    safe_print(f"Scraping English reviews for: Central World Bangkok")

    result = await scraper.scrape_reviews(
        place_id=place_id,
        max_reviews=15,
        date_range="6months"
    )

    reviews = result['reviews']

    safe_print(f"\nEnglish reviews found: {len(reviews)}")

    # Show English reviews
    for i, review in enumerate(reviews[:3], 1):
        safe_print(f"\nEnglish Review {i}:")
        safe_print(f"  Author: {review.author_name}")
        safe_print(f"  Rating: {review.rating}/5")
        safe_print(f"  Text: {review.review_text[:100]}...")

    return result


async def example_3_place_search():
    """
    Example 3: Place search without API key
    """
    safe_print("\n" + "=" * 80)
    safe_print("EXAMPLE 3: Place Search (No API Key Required)")
    safe_print("=" * 80)

    # Create search service
    search_service = create_rpc_search(language="th", region="th")

    # Search for restaurants
    query = "ร้านอาหาร ใน กรุงเทพมหานคร"  # Restaurants in Bangkok
    safe_print(f"Searching for: {query}")

    places = await search_service.search_places(
        query=query,
        max_results=5
    )

    safe_print(f"\nFound {len(places)} places:")

    for i, place in enumerate(places, 1):
        safe_print(f"\nPlace {i}:")
        safe_print(f"  Name: {format_name(place.name, 'unknown')}")
        safe_print(f"  Rating: {place.rating}/5 ({place.total_reviews} reviews)")
        safe_print(f"  Category: {place.category}")
        safe_print(f"  Address: {place.address}")
        safe_print(f"  Place ID: {place.place_id}")

    return places


async def example_4_conservative_mode():
    """
    Example 4: Conservative scraping mode (minimal risk)
    """
    safe_print("\n" + "=" * 80)
    safe_print("EXAMPLE 4: Conservative Mode (Minimal Risk)")
    safe_print("=" * 80)

    # Create scraper with conservative settings
    scraper = create_production_scraper(
        language="th",
        region="th",
        fast_mode=False,      # Human-like delays (500-1500ms)
        max_rate=3.0,         # Very conservative rate
        timeout=60.0,         # Longer timeout
        max_retries=5         # More retry attempts
    )

    safe_print("Using conservative scraping mode:")
    safe_print("  - Human-like delays (500-1500ms)")
    safe_print("  - Conservative rate (3.0 req/sec)")
    safe_print("  - Extended timeout (60s)")
    safe_print("  - Increased retries (5)")

    place_id = "0x30e29ecfc2f455e1:0xc4ad0280d8906604"

    result = await scraper.scrape_reviews(
        place_id=place_id,
        max_reviews=10,      # Small number for demo
        date_range="1month"  # Recent reviews only
    )

    safe_print(f"\nConservative mode results:")
    safe_print(f"  Reviews: {len(result['reviews'])}")
    safe_print(f"  Rate: {result['metadata']['rate']:.2f} reviews/sec (slower but safer)")

    # Show anti-bot statistics
    stats = result['metadata']['stats']
    safe_print(f"\nAnti-bot statistics:")
    safe_print(f"  Total requests: {stats['total_requests']}")
    safe_print(f"  Rate limits encountered: {stats['rate_limits_encountered']}")
    safe_print(f"  Retries used: {stats['retries_used']}")

    return result


async def example_5_date_filtering():
    """
    Example 5: Advanced date filtering
    """
    safe_print("\n" + "=" * 80)
    safe_print("EXAMPLE 5: Advanced Date Filtering")
    safe_print("=" * 80)

    scraper = create_production_scraper(
        language="th",
        region="th",
        fast_mode=True
    )

    place_id = "0x30e29ecfc2f455e1:0xc4ad0280d8906604"

    # Test different date ranges
    date_ranges = ["1month", "6months", "1year", "5years"]

    for date_range in date_ranges:
        safe_print(f"\nTesting date range: {date_range}")

        result = await scraper.scrape_reviews(
            place_id=place_id,
            max_reviews=20,
            date_range=date_range
        )

        safe_print(f"  Reviews found: {len(result['reviews'])}")
        safe_print(f"  Date cutoff: {result['metadata'].get('date_cutoff', 'No limit')}")

    # Custom date range example
    safe_print(f"\nTesting custom date range:")

    result = await scraper.scrape_reviews(
        place_id=place_id,
        max_reviews=20,
        date_range="custom",
        start_date="2024-01-01",
        end_date="2024-12-31"
    )

    safe_print(f"  Custom range reviews: {len(result['reviews'])}")

    return result


async def example_6_output_management():
    """
    Example 6: Using output manager for organized file storage
    """
    safe_print("\n" + "=" * 80)
    safe_print("EXAMPLE 6: Output Management")
    safe_print("=" * 80)

    scraper = create_production_scraper(
        language="th",
        region="th",
        fast_mode=True
    )

    place_id = "0x30e29ecfc2f455e1:0xc4ad0280d8906604"

    result = await scraper.scrape_reviews(
        place_id=place_id,
        max_reviews=10,
        date_range="1month"
    )

    # Manual save using output manager
    reviews_data = [review.__dict__ for review in result['reviews']]

    file_paths = output_manager.save_reviews(
        reviews=reviews_data,
        place_name="Central World Bangkok",
        place_id=place_id,
        task_id="example_6_output",
        settings={
            "max_reviews": 10,
            "date_range": "1month",
            "language": "th",
            "example": "output_management"
        }
    )

    safe_print(f"\nFiles saved to:")
    safe_print(f"  Directory: {file_paths['directory']}")
    safe_print(f"  JSON: {file_paths['json']}")
    safe_print(f"  CSV: {file_paths['csv']}")

    # Get recent files
    recent_files = output_manager.get_recent_files(data_type="reviews", limit=3)
    safe_print(f"\nRecent review files:")
    for file_info in recent_files:
        safe_print(f"  - {file_info['filename']} ({file_info['size']} bytes)")

    # Get storage info
    storage_info = output_manager.get_storage_info()
    safe_print(f"\nStorage information:")
    safe_print(f"  Total size: {storage_info['total_size_mb']} MB")
    safe_print(f"  Total files: {storage_info['total_files']}")

    return file_paths


async def example_7_error_handling():
    """
    Example 7: Error handling and statistics
    """
    safe_print("\n" + "=" * 80)
    safe_print("EXAMPLE 7: Error Handling & Statistics")
    safe_print("=" * 80)

    # Create scraper with moderate settings for testing
    scraper = create_production_scraper(
        language="th",
        region="th",
        fast_mode=True,
        max_rate=8.0,
        timeout=15.0,
        max_retries=2
    )

    # Test with invalid place ID (should handle gracefully)
    invalid_place_id = "invalid_place_id_12345"

    safe_print(f"Testing with invalid place ID: {invalid_place_id}")

    try:
        result = await scraper.scrape_reviews(
            place_id=invalid_place_id,
            max_reviews=10,
            date_range="1month"
        )

        safe_print(f"Result: {len(result['reviews'])} reviews (likely 0)")

    except Exception as e:
        safe_print(f"Expected error handled: {e}")

    # Test with valid place ID and check statistics
    safe_print(f"\nTesting with valid place ID and checking statistics:")

    valid_result = await scraper.scrape_reviews(
        place_id="0x30e29ecfc2f455e1:0xc4ad0280d8906604",
        max_reviews=15,
        date_range="1month"
    )

    # Detailed statistics
    stats = valid_result['metadata']['stats']

    safe_print(f"\nDetailed Statistics:")
    safe_print(f"  Total requests: {stats['total_requests']}")
    safe_print(f"  Successful requests: {stats['successful_requests']}")
    safe_print(f"  Failed requests: {stats['failed_requests']}")
    safe_print(f"  Rate limits encountered: {stats['rate_limits_encountered']}")
    safe_print(f"  Proxy switches: {stats['proxy_switches']}")
    safe_print(f"  Retries used: {stats['retries_used']}")

    return valid_result


async def main():
    """
    Run all examples
    """
    safe_print("🚀 Google Maps Scraper Framework - Basic Examples")
    safe_print("=" * 80)

    try:
        # Run examples sequentially
        await example_1_basic_review_scraping()
        await example_2_english_scraping()
        await example_3_place_search()
        await example_4_conservative_mode()
        await example_5_date_filtering()
        await example_6_output_management()
        await example_7_error_handling()

        safe_print("\n" + "=" * 80)
        safe_print("✅ All examples completed successfully!")
        safe_print("=" * 80)

    except KeyboardInterrupt:
        safe_print("\n\n⚠️ Examples interrupted by user")
    except Exception as e:
        safe_print(f"\n\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Fix Windows encoding
    if sys.platform == 'win32':
        os.system('chcp 65001 > nul 2>&1')

    # Run examples
    asyncio.run(main())