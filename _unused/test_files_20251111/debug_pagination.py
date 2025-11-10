# -*- coding: utf-8 -*-
"""
Debug Pagination - Why only 1,238 reviews?
==========================================

Debug script to understand why scraping stops at 1,238 reviews
and try different strategies to reach 2,000 reviews.
"""
import sys
import os
import time

# Fix Windows encoding
if sys.platform == 'win32':
    os.system('chcp 65001 > nul 2>&1')

import asyncio
import json
import httpx
from src.scraper.enhanced_language_scraper import create_enhanced_scraper

async def debug_pagination():
    print("=" * 80)
    print("DEBUG PAGINATION - INVESTIGATING REVIEW LIMIT")
    print("=" * 80)
    print("Testing different strategies to get more reviews")
    print("-" * 80)

    place_id = "0x30da3a89dde356f5:0xa8e9df0a32571ee1"  # Khao Soi Nimman

    strategies = [
        {
            "name": "DEFAULT ENHANCED",
            "language": "en",
            "region": "us",
            "max_rate": 6.0,
            "session_refresh_interval": 30,
            "date_range": "all"
        },
        {
            "name": "DIFFERENT REGION (TH)",
            "language": "en",
            "region": "th",
            "max_rate": 8.0,
            "session_refresh_interval": 50,
            "date_range": "all"
        },
        {
            "name": "SLOWER RATE",
            "language": "en",
            "region": "us",
            "max_rate": 3.0,
            "session_refresh_interval": 25,
            "date_range": "all"
        },
        {
            "name": "NO DATE RANGE",
            "language": "en",
            "region": "us",
            "max_rate": 6.0,
            "session_refresh_interval": 30,
            "date_range": "all"
        }
    ]

    results = []

    for i, strategy in enumerate(strategies, 1):
        print(f"\n{'='*60}")
        print(f"STRATEGY {i}: {strategy['name']}")
        print(f"{'='*60}")
        print(f"Language: {strategy['language']}")
        print(f"Region: {strategy['region']}")
        print(f"Max rate: {strategy['max_rate']} req/sec")
        print(f"Session refresh: {strategy['session_refresh_interval']} pages")
        print()

        try:
            # Create scraper with strategy
            scraper = create_enhanced_scraper(
                language=strategy['language'],
                region=strategy['region'],
                fast_mode=True,
                max_rate=strategy['max_rate'],
                session_refresh_interval=strategy['session_refresh_interval'],
                use_session_ids=True,
                strict_language_mode=True
            )

            start_time = time.time()

            # Override scrape method to add debugging
            original_fetch = scraper._parent_scraped_reviews

            async def debug_fetch_rpc_page(client, place_id, page_num, page_token):
                """Debug version of fetch_rpc_page"""
                url = "https://www.google.com/maps/rpc/listugcposts"

                # Enhanced headers based on strategy
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                    'Accept': 'application/json, text/plain, */*',
                    'Accept-Language': f"{strategy['language']}-{strategy['region'].upper()},{strategy['language']};q=0.9,en;q=0.8",
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Cache-Control': 'no-cache',
                    'Pragma': 'no-cache',
                    'Referer': 'https://www.google.com/maps',
                    'Origin': 'https://www.google.com'
                }

                # Session-specific headers
                if scraper.use_session_ids:
                    headers['X-Goog-AuthUser'] = '0'
                    headers['X-Goog-PageId'] = scraper.session_id
                    headers['X-Goog-Session-Id'] = scraper.session_id

                # Different pb parameter based on strategy
                base_pb = f"!1m6!1s{place_id}!6m4!4m1!1e1!4m1!1e3!2m2!1i20!2s{page_token if page_token else ''}!5m2!1s{strategy['language']}!2s{strategy['region']}!7e81"

                params = {
                    'pb': base_pb,
                    'hl': strategy['language'],
                    'gl': strategy['region'],
                    'async': 'reviews',
                    'source': '3',
                    'm': '1'
                }

                response = await client.get(url, params=params, headers=headers)

                if response.status_code == 200:
                    content = response.text.strip()
                    if content.startswith(')]}\''):
                        content = content[4:]

                    try:
                        data = json.loads(content)

                        # Debug: Check response structure
                        if len(data) > 1:
                            next_token = data[1] if len(data) > 1 and isinstance(data[1], str) else None
                            print(f"   Page {page_num}: Got response, next_token: {'YES' if next_token else 'NO'}")
                            if not next_token:
                                print(f"   *** NO NEXT TOKEN - THIS IS WHY WE STOPPED ***")
                            return data, next_token
                        else:
                            print(f"   Page {page_num}: Empty response")
                            return [], None

                    except json.JSONDecodeError as e:
                        print(f"   Page {page_num}: JSON decode error: {e}")
                        return [], None
                else:
                    print(f"   Page {page_num}: HTTP {response.status_code}")
                    return [], None

            # Temporarily replace fetch method
            scraper._parent_scraped_reviews = None
            scraper._debug_fetch_rpc_page = debug_fetch_rpc_page

            # Run scraping with timeout
            try:
                result = await asyncio.wait_for(
                    scraper.scrape_reviews_enhanced(place_id, 2000, strategy['date_range']),
                    timeout=120  # 2 minute timeout per strategy
                )

                end_time = time.time()
                reviews = result['reviews']

                strategy_result = {
                    'name': strategy['name'],
                    'reviews': len(reviews),
                    'time': end_time - start_time,
                    'rate': len(reviews) / (end_time - start_time),
                    'success': True
                }

                print(f"\nResults for {strategy['name']}:")
                print(f"  Reviews: {len(reviews)}")
                print(f"  Time: {end_time - start_time:.1f}s")
                print(f"  Rate: {len(reviews)/(end_time - start_time):.1f} reviews/sec")

                results.append(strategy_result)

            except asyncio.TimeoutError:
                print(f"TIMEOUT after 2 minutes")
                strategy_result = {
                    'name': strategy['name'],
                    'reviews': 0,
                    'time': 120,
                    'rate': 0,
                    'success': False,
                    'error': 'timeout'
                }
                results.append(strategy_result)

        except Exception as e:
            print(f"ERROR: {e}")
            strategy_result = {
                'name': strategy['name'],
                'reviews': 0,
                'time': 0,
                'rate': 0,
                'success': False,
                'error': str(e)
            }
            results.append(strategy_result)

        # Brief pause between strategies
        await asyncio.sleep(3)

    # Summary
    print(f"\n{'='*80}")
    print("STRATEGY COMPARISON SUMMARY")
    print(f"{'='*80}")

    for result in results:
        if result['success']:
            print(f"✓ {result['name']:20}: {result['reviews']:4d} reviews ({result['rate']:5.1f}/sec)")
        else:
            print(f"✗ {result['name']:20}: FAILED ({result.get('error', 'unknown')})")

    # Find best strategy
    successful_results = [r for r in results if r['success']]
    if successful_results:
        best = max(successful_results, key=lambda x: x['reviews'])
        print(f"\nBest strategy: {best['name']} with {best['reviews']} reviews")

        if best['reviews'] < 2000:
            print(f"\nRecommendations:")
            if best['reviews'] >= 1500:
                print(f"✓ Enhanced scraper is working well")
                print(f"✓ 1,238 reviews may be the actual API limit for this place")
                print(f"✓ Consider trying different restaurants with more reviews")
            else:
                print(f"✗ Need further optimization")
        else:
            print(f"🎉 SUCCESS: Reached 2000 reviews!")
    else:
        print(f"\nAll strategies failed - may need different approach")

    return results

async def main():
    print("Debug Pagination Script")
    print("Starting at:", time.strftime("%Y-%m-%d %H:%M:%S"))

    results = await debug_pagination()
    print(f"\nDebug completed at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    print(f"Debug exit code: {exit_code}")