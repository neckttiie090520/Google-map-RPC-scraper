#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example: Sort Reviews by Newest
================================

This example demonstrates how to scrape reviews and sort them by date (newest first).

Author: Nextzus
Date: 2025-11-10
"""
import sys
import os
import asyncio

# Fix Windows encoding
if sys.platform == 'win32':
    os.system('chcp 65001 > nul 2>&1')

from src.scraper.production_scraper import create_production_scraper
from datetime import datetime


async def scrape_with_sorting():
    """Scrape reviews and sort by newest first"""

    print()
    print("=" * 80)
    print("EXAMPLE: Sort Reviews by Newest")
    print("=" * 80)
    print()

    # Create scraper
    scraper = create_production_scraper(
        language="en",
        region="us",
        fast_mode=True,
        max_rate=10.0
    )

    # Example: Central World Bangkok
    place_id = "0x30e29ecfc2f455e1:0xc4ad0280d8906604"

    # Scrape with sort_by_newest=True
    result = await scraper.scrape_reviews(
        place_id=place_id,
        max_reviews=50,
        date_range="1year",
        sort_by_newest=True  # Enable sorting by newest
    )

    # Display first 5 reviews to verify sorting
    print()
    print("=" * 80)
    print("REVIEWS (Sorted by Newest First)")
    print("=" * 80)
    print()

    for i, review in enumerate(result['reviews'][:5], 1):
        print(f"Review #{i}")
        print(f"Date: {review.date_formatted}")
        print(f"Author: {review.author_name}")
        print(f"Rating: {'⭐' * review.rating}")
        print(f"Text: {review.review_text[:100]}...")
        print("-" * 80)
        print()

    # Export to files
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    scraper.export_to_csv(result['reviews'], f"reviews_sorted_newest_{timestamp}.csv")
    scraper.export_to_json(result, f"reviews_sorted_newest_{timestamp}.json")

    print()
    print(f"✅ Total reviews: {len(result['reviews'])}")
    print(f"📁 Files saved:")
    print(f"   - reviews_sorted_newest_{timestamp}.csv")
    print(f"   - reviews_sorted_newest_{timestamp}.json")
    print()

    # Verify sorting
    print("=" * 80)
    print("SORTING VERIFICATION")
    print("=" * 80)
    print()
    print("Date order (should be descending - newest to oldest):")
    for i, review in enumerate(result['reviews'][:10], 1):
        print(f"  {i}. {review.date_formatted}")

    return result


async def compare_sorted_vs_unsorted():
    """Compare sorted vs unsorted results"""

    print()
    print("=" * 80)
    print("COMPARISON: Sorted vs Unsorted")
    print("=" * 80)
    print()

    place_id = "0x30e29ecfc2f455e1:0xc4ad0280d8906604"

    # Test 1: Without sorting
    print("TEST 1: Scraping WITHOUT sorting...")
    print()

    scraper1 = create_production_scraper(language="en", region="us")
    result_unsorted = await scraper1.scrape_reviews(
        place_id=place_id,
        max_reviews=20,
        date_range="1year",
        sort_by_newest=False  # No sorting
    )

    print()
    print("Unsorted - First 5 dates:")
    for i, review in enumerate(result_unsorted['reviews'][:5], 1):
        print(f"  {i}. {review.date_formatted}")

    # Wait between requests
    print()
    print("⏳ Waiting 5 seconds...")
    await asyncio.sleep(5)
    print()

    # Test 2: With sorting
    print("TEST 2: Scraping WITH sorting...")
    print()

    scraper2 = create_production_scraper(language="en", region="us")
    result_sorted = await scraper2.scrape_reviews(
        place_id=place_id,
        max_reviews=20,
        date_range="1year",
        sort_by_newest=True  # Sort by newest
    )

    print()
    print("Sorted - First 5 dates:")
    for i, review in enumerate(result_sorted['reviews'][:5], 1):
        print(f"  {i}. {review.date_formatted}")

    # Summary
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()
    print("Notice how the sorted version has reviews in descending date order")
    print("(newest dates first), while unsorted follows Google's default order.")
    print()


async def main():
    """Main function - choose example to run"""

    print()
    print("=" * 80)
    print("Sort by Newest Examples")
    print("=" * 80)
    print()
    print("Choose example to run:")
    print("1. Simple example with sorting (50 reviews)")
    print("2. Compare sorted vs unsorted (20 reviews each)")
    print()

    choice = input("Enter choice (1-2): ").strip()

    if choice == "1":
        await scrape_with_sorting()
    elif choice == "2":
        await compare_sorted_vs_unsorted()
    else:
        print("Invalid choice. Running example 1...")
        await scrape_with_sorting()


if __name__ == "__main__":
    # You can run directly or via menu
    asyncio.run(main())

    # Or uncomment to run specific example:
    # asyncio.run(scrape_with_sorting())
    # asyncio.run(compare_sorted_vs_unsorted())
