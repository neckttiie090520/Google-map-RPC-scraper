#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick Start Example - Google Maps Scraper Framework
===============================================

The simplest way to get started with the Google Maps scraper framework.
Just run this script to see the framework in action!

Usage:
    python quick_start.py

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
from utils.unicode_display import safe_print


async def quick_demo():
    """
    Quick demonstration of the framework capabilities
    """
    safe_print("🚀 Google Maps Scraper Framework - Quick Start Demo")
    safe_print("=" * 60)

    # Test place: Central World Bangkok (has lots of reviews)
    test_place_id = "0x30e29ecfc2f455e1:0xc4ad0280d8906604"

    safe_print(f"📍 Testing with: Central World Bangkok")
    safe_print(f"🔑 Place ID: {test_place_id}")
    safe_print("")

    # 1. Create scraper with default settings
    safe_print("1️⃣ Creating scraper...")
    scraper = create_production_scraper(
        language="th",
        region="th",
        fast_mode=True
    )
    safe_print("✅ Scraper created successfully!")

    # 2. Scrape a small sample of reviews
    safe_print("\n2️⃣ Scraping reviews (10 reviews for demo)...")
    result = await scraper.scrape_reviews(
        place_id=test_place_id,
        max_reviews=10,      # Small number for quick demo
        date_range="1month"  # Recent reviews only
    )

    reviews = result['reviews']
    safe_print(f"✅ Scraped {len(reviews)} reviews successfully!")

    # 3. Show sample results
    safe_print("\n3️⃣ Sample Results:")
    safe_print("-" * 40)

    for i, review in enumerate(reviews[:3], 1):
        safe_print(f"\nReview {i}:")
        safe_print(f"  👤 Author: {review.author_name}")
        safe_print(f"  ⭐ Rating: {review.rating}/5")
        safe_print(f"  📅 Date: {review.date_relative}")
        safe_print(f"  💬 Text: {review.review_text[:80]}...")
        safe_print(f"  👍 Likes: {review.review_likes}")

    # 4. Show performance stats
    metadata = result['metadata']
    safe_print(f"\n4️⃣ Performance Stats:")
    safe_print(f"  ⏱️  Time taken: {metadata['time_taken']:.2f}s")
    safe_print(f"  📊 Scraping rate: {metadata['rate']:.2f} reviews/sec")

    stats = metadata['stats']
    safe_print(f"  🌐 Total requests: {stats['total_requests']}")
    safe_print(f"  ✅ Successful: {stats['successful_requests']}")
    safe_print(f"  🔄 Rate limits: {stats['rate_limits_encountered']}")

    # 5. Quick search demo
    safe_print(f"\n5️⃣ Quick Search Demo:")
    safe_print("-" * 40)

    search_service = create_rpc_search(language="th", region="th")

    # Search for cafes
    safe_print("🔍 Searching for 'coffee shops in Bangkok'...")
    places = await search_service.search_places(
        query="coffee shop",
        max_results=3
    )

    safe_print(f"✅ Found {len(places)} places:")
    for i, place in enumerate(places, 1):
        safe_print(f"  {i}. {place.name}")
        safe_print(f"     Rating: {place.rating}/5 ({place.total_reviews} reviews)")
        safe_print(f"     📍 {place.address}")

    safe_print(f"\n🎉 Quick start demo completed!")
    safe_print("=" * 60)
    safe_print("💡 Next steps:")
    safe_print("   - Try examples/basic_scraping.py for more features")
    safe_print("   - Try examples/advanced_scraping.py for translation & more")
    safe_print("   - Try examples/production_scraper.py for CLI tool")
    safe_print("   - Check src/README.md for full documentation")


async def interactive_demo():
    """
    Interactive demo where user can choose what to scrape
    """
    safe_print("\n🎮 Interactive Demo Mode")
    safe_print("=" * 40)

    # Let user choose a place
    test_places = {
        "1": {
            "name": "Central World Bangkok",
            "id": "0x30e29ecfc2f455e1:0xc4ad0280d8906604",
            "description": "Large shopping mall in Bangkok"
        },
        "2": {
            "name": "Siam Paragon",
            "id": "0x3118b51bb5bfe1fd:0x3c8a1bfc5a6c5c9c",
            "description": "Luxury shopping mall"
        },
        "3": {
            "name": "Chatuchak Weekend Market",
            "id": "0x30da3a94d9027f0b:0x2f6b6b8a3c6f5a6f",
            "description": "Famous weekend market"
        }
    }

    safe_print("Choose a place to scrape:")
    for key, place in test_places.items():
        safe_print(f"  {key}. {place['name']} - {place['description']}")

    # For demo purposes, just use Central World
    choice = "1"  # In real interactive mode, you'd get user input
    selected_place = test_places[choice]

    safe_print(f"\nYou selected: {selected_place['name']}")
    safe_print("Starting scraping...")

    # Scrape with interactive feedback
    scraper = create_production_scraper(
        language="th",
        region="th",
        fast_mode=True
    )

    # Progress callback for interactivity
    def progress_callback(page_num, total_reviews):
        progress = (total_reviews / 20) * 100  # Assume max 20 for demo
        safe_print(f"   📈 Progress: {progress:.0f}% - {total_reviews} reviews")

    result = await scraper.scrape_reviews(
        place_id=selected_place['id'],
        max_reviews=20,
        date_range="3months",
        progress_callback=progress_callback
    )

    safe_print(f"\n✅ Interactive scraping completed!")
    safe_print(f"   Place: {selected_place['name']}")
    safe_print(f"   Reviews: {len(result['reviews'])}")
    safe_print(f"   Rate: {result['metadata']['rate']:.2f} reviews/sec")


async def main():
    """
    Main function - runs quick demo
    """
    try:
        # Fix Windows encoding
        if sys.platform == 'win32':
            os.system('chcp 65001 > nul 2>&1')

        # Run quick demo
        await quick_demo()

        # Optional: Run interactive demo
        # await interactive_demo()

    except KeyboardInterrupt:
        safe_print("\n\n⚠️ Demo interrupted by user")
    except Exception as e:
        safe_print(f"\n\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())