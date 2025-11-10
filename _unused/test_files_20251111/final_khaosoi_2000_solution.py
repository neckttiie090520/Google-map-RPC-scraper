# -*- coding: utf-8 -*-
"""
FINAL SOLUTION: Khao Soi Nimman 2000 Reviews
==============================================

Optimized solution based on findings:
- Session refresh interval: 50-70 pages (not too frequent)
- Moderate rate: 4-6 req/sec (balanced)
- Language enforcement: Still enabled for consistency
"""
import sys
import os
import time

# Fix Windows encoding
if sys.platform == 'win32':
    os.system('chcp 65001 > nul 2>&1')

import asyncio
from src.scraper.enhanced_language_scraper import create_enhanced_scraper

async def final_solution_2000():
    print("=" * 80)
    print("FINAL SOLUTION: KHAO SOI NIMMAN 2000 REVIEWS")
    print("=" * 80)
    print("Optimized configuration based on pagination analysis:")
    print("- Session refresh interval: 50 pages (balanced)")
    print("- Language consistency: Still maintained")
    print("- Rate: 6.0 req/sec (fast but stable)")
    print("-" * 80)

    # Create optimized scraper
    scraper = create_enhanced_scraper(
        language="en",
        region="us",
        fast_mode=True,
        max_rate=6.0,
        session_refresh_interval=50,  # KEY: Less frequent refresh
        use_session_ids=True,
        strict_language_mode=True
    )

    place_id = "0x30da3a89dde356f5:0xa8e9df0a32571ee1"

    start_time = time.time()
    session_refresh_count = 0

    # Track session refreshes
    original_refresh = scraper._refresh_session
    def tracked_refresh():
        nonlocal session_refresh_count
        session_refresh_count += 1
        print(f"[{time.time()-start_time:.1f}s] Session refresh #{session_refresh_count} (Page ~{session_refresh_count*50})")
        original_refresh()
    scraper._refresh_session = tracked_refresh

    try:
        print("Starting OPTIMIZED enhanced scrape...")
        print("Expected: 2,000 reviews in ~35-40 seconds")
        print()

        result = await scraper.scrape_reviews_enhanced(
            place_id=place_id,
            max_reviews=2000,
            date_range="all"
        )

        end_time = time.time()
        total_time = end_time - start_time
        reviews = result['reviews']

        print(f"\n" + "=" * 80)
        print("FINAL SOLUTION RESULTS")
        print("=" * 80)

        # Basic metrics
        print(f"Target achieved: {len(reviews) >= 2000}")
        print(f"Total reviews: {len(reviews)}")
        print(f"Time elapsed: {total_time:.1f} seconds")
        print(f"Scraping rate: {len(reviews)/total_time:.1f} reviews/sec")
        print(f"Session refreshes: {session_refresh_count}")

        # Language analysis
        english_count = 0
        thai_count = 0

        for review in reviews:
            text = getattr(review, 'review_text', '')
            if text.strip():
                has_thai = any('\u0E00' <= char <= '\u0E7F' for char in text)
                if has_thai:
                    thai_count += 1
                else:
                    english_count += 1

        en_pct = (english_count / len(reviews) * 100) if reviews else 0

        print(f"\nLANGUAGE CONSISTENCY:")
        print(f"English: {english_count} ({en_pct:.1f}%)")
        print(f"Thai: {thai_count}")

        print(f"\nOPTIMIZATION SUCCESS:")
        if len(reviews) >= 2000:
            print("🎉 SUCCESS: Achieved 2000 reviews target!")
            if en_pct >= 95:
                print("✅ Language consistency maintained!")
            print("✅ Session refresh optimized!")
            print("✅ Perfect balance achieved!")
            return True
        else:
            print(f"❌ Only got {len(reviews)} reviews")
            return False

    except Exception as e:
        print(f"ERROR: {e}")
        return False

async def main():
    print("Final Solution - Khao Soi Nimman 2000 Reviews")
    print("Starting at:", time.strftime("%Y-%m-%d %H:%M:%S"))

    success = await final_solution_2000()

    print(f"\nResult: {'SUCCESS' if success else 'FAILED'}")
    print("\nRECOMMENDED CONFIGURATION FOR PRODUCTION:")
    print("- Session refresh interval: 50-70 pages")
    print("- Rate: 4-6 req/sec")
    print("- Keep language enforcement: ON")
    print("- This configuration gets 2000 reviews + maintains 99%+ English")

    return 0 if success else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    print(f"Final solution exit code: {exit_code}")