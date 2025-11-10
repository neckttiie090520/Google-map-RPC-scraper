# -*- coding: utf-8 -*-
"""
Final Performance Comparison
============================

Compare the best working methods for getting 2000 reviews:
1. Original Production Scraper (gets 2000 reviews)
2. Enhanced Scraper with Thai region (gets 2000 reviews)
3. Enhanced Scraper without session refresh (gets 2000 reviews)
"""
import sys
import os
import time

# Fix Windows encoding
if sys.platform == 'win32':
    os.system('chcp 65001 > nul 2>&1')

import asyncio
from src.scraper.production_scraper import create_production_scraper
from src.scraper.enhanced_language_scraper import create_enhanced_scraper

async def test_method_1_original():
    """Test 1: Original Production Scraper"""
    print("METHOD 1: Original Production Scraper")
    print("-" * 50)

    scraper = create_production_scraper(
        language="en",
        region="us",
        fast_mode=True,
        max_rate=6.0
    )

    place_id = "0x30da3a89dde356f5:0xa8e9df0a32571ee1"

    start_time = time.time()
    try:
        result = await scraper.scrape_reviews(place_id, 2000, "all")
        end_time = time.time()

        reviews = result['reviews']

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

        total_time = end_time - start_time
        en_pct = (english_count / len(reviews) * 100) if reviews else 0

        results = {
            'method': 'Original Production Scraper',
            'reviews': len(reviews),
            'english': english_count,
            'thai': thai_count,
            'english_pct': en_pct,
            'time': total_time,
            'rate': len(reviews)/total_time,
            'success': len(reviews) >= 2000 and en_pct >= 90
        }

        print(f"  Reviews: {len(reviews)}")
        print(f"  English: {english_count} ({en_pct:.1f}%)")
        print(f"  Thai: {thai_count}")
        print(f"  Time: {total_time:.1f}s")
        print(f"  Rate: {len(reviews)/total_time:.1f}/sec")
        print(f"  Success: {results['success']}")
        print()

        return results

    except Exception as e:
        print(f"  ERROR: {e}")
        print()
        return {
            'method': 'Original Production Scraper',
            'reviews': 0,
            'english': 0,
            'thai': 0,
            'english_pct': 0,
            'time': 0,
            'rate': 0,
            'success': False,
            'error': str(e)
        }

async def test_method_2_enhanced_thai():
    """Test 2: Enhanced Scraper with Thai Region"""
    print("METHOD 2: Enhanced Scraper - Thai Region")
    print("-" * 50)

    scraper = create_enhanced_scraper(
        language="en",
        region="th",  # KEY: Thai region!
        fast_mode=True,
        max_rate=6.0,
        session_refresh_interval=30,
        use_session_ids=True,
        strict_language_mode=True
    )

    place_id = "0x30da3a89dde356f5:0xa8e9df0a32571ee1"

    start_time = time.time()
    try:
        result = await scraper.scrape_reviews_enhanced(place_id, 2000, "all")
        end_time = time.time()

        reviews = result['reviews']

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

        total_time = end_time - start_time
        en_pct = (english_count / len(reviews) * 100) if reviews else 0

        results = {
            'method': 'Enhanced Scraper - Thai Region',
            'reviews': len(reviews),
            'english': english_count,
            'thai': thai_count,
            'english_pct': en_pct,
            'time': total_time,
            'rate': len(reviews)/total_time,
            'success': len(reviews) >= 2000 and en_pct >= 95
        }

        print(f"  Reviews: {len(reviews)}")
        print(f"  English: {english_count} ({en_pct:.1f}%)")
        print(f"  Thai: {thai_count}")
        print(f"  Time: {total_time:.1f}s")
        print(f"  Rate: {len(reviews)/total_time:.1f}/sec")
        print(f"  Success: {results['success']}")
        print()

        return results

    except Exception as e:
        print(f"  ERROR: {e}")
        print()
        return {
            'method': 'Enhanced Scraper - Thai Region',
            'reviews': 0,
            'english': 0,
            'thai': 0,
            'english_pct': 0,
            'time': 0,
            'rate': 0,
            'success': False,
            'error': str(e)
        }

async def test_method_3_no_session():
    """Test 3: Enhanced Scraper - No Session Refresh"""
    print("METHOD 3: Enhanced Scraper - No Session Refresh")
    print("-" * 50)

    scraper = create_enhanced_scraper(
        language="en",
        region="us",
        fast_mode=True,
        max_rate=6.0,
        session_refresh_interval=100,  # No refresh
        use_session_ids=False,         # Disabled
        strict_language_mode=True
    )

    place_id = "0x30da3a89dde356f5:0xa8e9df0a32571ee1"

    start_time = time.time()
    try:
        result = await scraper.scrape_reviews_enhanced(place_id, 2000, "all")
        end_time = time.time()

        reviews = result['reviews']

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

        total_time = end_time - start_time
        en_pct = (english_count / len(reviews) * 100) if reviews else 0

        results = {
            'method': 'Enhanced Scraper - No Session',
            'reviews': len(reviews),
            'english': english_count,
            'thai': thai_count,
            'english_pct': en_pct,
            'time': total_time,
            'rate': len(reviews)/total_time,
            'success': len(reviews) >= 2000 and en_pct >= 95
        }

        print(f"  Reviews: {len(reviews)}")
        print(f"  English: {english_count} ({en_pct:.1f}%)")
        print(f"  Thai: {thai_count}")
        print(f"  Time: {total_time:.1f}s")
        print(f"  Rate: {len(reviews)/total_time:.1f}/sec")
        print(f"  Success: {results['success']}")
        print()

        return results

    except Exception as e:
        print(f"  ERROR: {e}")
        print()
        return {
            'method': 'Enhanced Scraper - No Session',
            'reviews': 0,
            'english': 0,
            'thai': 0,
            'english_pct': 0,
            'time': 0,
            'rate': 0,
            'success': False,
            'error': str(e)
        }

async def main():
    print("=" * 80)
    print("FINAL PERFORMANCE COMPARISON")
    print("=" * 80)
    print("Testing the 3 best methods for getting 2000 reviews")
    print("Target: Khao Soi Nimman (0x30da3a89dde356f5:0xa8e9df0a32571ee1)")
    print("-" * 80)
    print()

    # Test all methods
    results = []
    results.append(await test_method_1_original())
    await asyncio.sleep(2)
    results.append(await test_method_2_enhanced_thai())
    await asyncio.sleep(2)
    results.append(await test_method_3_no_session())

    # Analysis
    print("=" * 80)
    print("PERFORMANCE ANALYSIS")
    print("=" * 80)

    successful = [r for r in results if r['success']]
    print(f"Successful methods: {len(successful)}/3")

    if successful:
        print("\nBEST PERFORMERS:")
        # Sort by total reviews first, then language consistency
        successful.sort(key=lambda x: (x['reviews'], x['english_pct']), reverse=True)

        for i, result in enumerate(successful, 1):
            print(f"  {i}. {result['method']}")
            print(f"     Reviews: {result['reviews']:,} ({result['english_pct']:.1f}% English)")
            print(f"     Speed: {result['rate']:.1f} reviews/sec")
            print(f"     Time: {result['time']:.1f} seconds")

        # Overall best
        best = successful[0]
        print(f"\nWINNER: {best['method']}")
        print(f"  Volume: {best['reviews']:,} reviews")
        print(f"  Language: {best['english_pct']:.1f}% English")
        print(f"  Performance: {best['rate']:.1f} reviews/sec")

    # Language consistency comparison
    print(f"\nLANGUAGE CONSISTENCY RANKING:")
    results.sort(key=lambda x: x['english_pct'], reverse=True)
    for i, result in enumerate(results, 1):
        if result['success']:
            print(f"  {i}. {result['method']}: {result['english_pct']:.1f}% English")

    # Performance ranking
    print(f"\nPERFORMANCE RANKING:")
    results.sort(key=lambda x: x['rate'], reverse=True)
    for i, result in enumerate(results, 1):
        if result['success']:
            print(f"  {i}. {result['method']}: {result['rate']:.1f} reviews/sec")

    # Recommendations
    print(f"\n" + "=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)

    if successful:
        best_volume = max(successful, key=lambda x: x['reviews'])
        best_language = max(successful, key=lambda x: x['english_pct'])
        best_speed = max(successful, key=lambda x: x['rate'])

        print(f"FOR MAXIMUM VOLUME: {best_volume['method']}")
        print(f"  Gets {best_volume['reviews']:,} reviews")
        print()

        print(f"FOR LANGUAGE CONSISTENCY: {best_language['method']}")
        print(f"  {best_language['english_pct']:.1f}% English content")
        print()

        print(f"FOR SPEED: {best_speed['method']}")
        print(f"  {best_speed['rate']:.1f} reviews/sec")
        print()

        # Overall recommendation
        if best_volume['english_pct'] >= 95:
            print("OVERALL RECOMMENDATION:")
            print(f"Use {best_volume['method']} for production")
            print("✅ Gets full volume with excellent language consistency")
        else:
            print("TRADE-OFF ANALYSIS:")
            print(f"  Volume vs Language: {best_volume['method']} gets more reviews but {best_language['english_pct']:.1f}% English vs {best_volume['english_pct']:.1f}%")
            print(f"  Recommendation: Choose based on your priority - volume or language purity")

    else:
        print("❌ ALL METHODS FAILED")
        print("Need to investigate issues with current setup")

    # Historical comparison
    print(f"\nHISTORICAL COMPARISON:")
    print("Original Problem (03:19): 90.1% English, 197 Thai reviews")
    print(f"Solutions Found:")
    for result in successful:
        print(f"  {result['method']}: {result['english_pct']:.1f}% English, {result['thai']} Thai reviews")

    return 0 if successful else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    print(f"Performance comparison exit code: {exit_code}")