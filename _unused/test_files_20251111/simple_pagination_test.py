# -*- coding: utf-8 -*-
"""
Simple Pagination Test - Why 1,238 reviews?
============================================

Simple test to understand pagination limits and try to get more reviews.
"""
import sys
import os
import time

# Fix Windows encoding
if sys.platform == 'win32':
    os.system('chcp 65001 > nul 2>&1')

import asyncio
from src.scraper.enhanced_language_scraper import create_enhanced_scraper

async def test_different_strategies():
    print("=" * 80)
    print("TESTING DIFFERENT STRATEGIES FOR MORE REVIEWS")
    print("=" * 80)

    place_id = "0x30da3a89dde356f5:0xa8e9df0a32571ee1"  # Khao Soi Nimman

    # Test 1: Try without session refresh (see if session management affects pagination)
    print("\n1. Testing WITHOUT session refresh...")
    try:
        scraper1 = create_enhanced_scraper(
            language="en",
            region="us",
            fast_mode=True,
            max_rate=4.0,  # Slower rate
            session_refresh_interval=100,  # Very large number = no refresh
            use_session_ids=False,  # Disable session IDs
            strict_language_mode=False  # More lenient
        )

        result1 = await scraper1.scrape_reviews_enhanced(place_id, 2000, "all")
        print(f"   Result: {len(result1['reviews'])} reviews")

    except Exception as e:
        print(f"   Error: {e}")

    await asyncio.sleep(2)

    # Test 2: Try with different language settings
    print("\n2. Testing with THAI region (might unlock more data)...")
    try:
        scraper2 = create_enhanced_scraper(
            language="th",  # Try Thai language first
            region="th",
            fast_mode=True,
            max_rate=4.0,
            session_refresh_interval=30,
            use_session_ids=True,
            strict_language_mode=False
        )

        result2 = await scraper2.scrape_reviews_enhanced(place_id, 2000, "all")
        print(f"   Result: {len(result2['reviews'])} reviews")

    except Exception as e:
        print(f"   Error: {e}")

    await asyncio.sleep(2)

    # Test 3: Try with enhanced settings but longer time
    print("\n3. Testing with VERY slow rate (avoid rate limiting)...")
    try:
        scraper3 = create_enhanced_scraper(
            language="en",
            region="us",
            fast_mode=False,  # Human mode
            max_rate=2.0,  # Very slow
            session_refresh_interval=20,
            use_session_ids=True,
            strict_language_mode=True
        )

        result3 = await scraper3.scrape_reviews_enhanced(place_id, 2000, "all")
        print(f"   Result: {len(result3['reviews'])} reviews")

    except Exception as e:
        print(f"   Error: {e}")

    await asyncio.sleep(2)

    # Test 4: Try the original production scraper (without enhancements)
    print("\n4. Testing ORIGINAL production scraper (no session management)...")
    try:
        from src.scraper.production_scraper import create_production_scraper

        scraper4 = create_production_scraper(
            language="en",
            region="us",
            fast_mode=True,
            max_rate=6.0
        )

        result4 = await scraper4.scrape_reviews(place_id, 2000, "all")
        print(f"   Result: {len(result4['reviews'])} reviews")

    except Exception as e:
        print(f"   Error: {e}")

    await asyncio.sleep(2)

    # Test 5: Try different date ranges (might affect pagination)
    print("\n5. Testing with RECENT date range only...")
    try:
        scraper5 = create_enhanced_scraper(
            language="en",
            region="us",
            fast_mode=True,
            max_rate=6.0,
            session_refresh_interval=30,
            use_session_ids=True,
            strict_language_mode=True
        )

        result5 = await scraper5.scrape_reviews_enhanced(place_id, 2000, "1year")
        print(f"   Result: {len(result5['reviews'])} reviews")

    except Exception as e:
        print(f"   Error: {e}")

    print("\n" + "=" * 80)
    print("ANALYSIS")
    print("=" * 80)
    print("If all tests return similar results (~1,200-1,300 reviews):")
    print("  - This is likely the API limit for this specific place")
    print("  - Google may limit accessible reviews per place")
    print("  - Different restaurants might have different limits")
    print()
    print("If one test gets significantly more reviews:")
    print("  - That strategy is the key to unlocking more data")
    print("  - We should adopt that configuration")

async def check_place_info():
    """Check actual place information to understand expected review count"""
    print("\n" + "=" * 80)
    print("CHECKING PLACE INFORMATION")
    print("=" * 80)

    try:
        from src.search.rpc_place_search import RpcPlaceSearch

        search = RpcPlaceSearch()
        results = search.search_places("Khao Soi Nimman", 1, "en", "us")

        if results:
            place = results[0]
            print(f"Place: {place.get('name', 'Unknown')}")
            print(f"Total Reviews (claimed): {place.get('total_reviews', 'Unknown')}")
            print(f"Rating: {place.get('rating', 'Unknown')}")
            print(f"Address: {place.get('address', 'Unknown')}")

            claimed_reviews = place.get('total_reviews', 0)
            if claimed_reviews and claimed_reviews < 2000:
                print(f"\nIMPORTANT: Place claims only {claimed_reviews} total reviews")
                print(f"If true, then getting 1,238 reviews is actually excellent!")
                print(f"({1,238}/{claimed_reviews} = {(1238/claimed_reviews)*100:.1f}% of available reviews)")
        else:
            print("Could not fetch place information")

    except Exception as e:
        print(f"Error checking place info: {e}")

async def main():
    print("Simple Pagination Test")
    print("Starting at:", time.strftime("%Y-%m-%d %H:%M:%S"))

    await check_place_info()
    await test_different_strategies()

    print(f"\nTest completed at: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    print("\nRECOMMENDATIONS:")
    print("1. If all tests get similar results (~1,200-1,300):")
    print("   - This is likely the actual API limit")
    print("   - Our scraper is working perfectly")
    print("   - Try restaurants with more total reviews")
    print()
    print("2. If one strategy works better:")
    print("   - Adopt that configuration")
    print("   - Update webapp defaults")

    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    print(f"Pagination test exit code: {exit_code}")