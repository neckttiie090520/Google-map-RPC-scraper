#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick test script for production scraper
"""
import sys
import os
import asyncio
import json

# Fix Windows encoding
if sys.platform == 'win32':
    os.system('chcp 65001 > nul 2>&1')

from src.scraper.production_scraper import ProductionGoogleMapsScraper, ScraperConfig

async def test_scraper():
    """Test the production scraper with a known place"""

    # Test place: Central World Bangkok (known to have many reviews)
    place_id = "0x30e29ecfc2f455e1:0xc4ad0280d8906604"

    print("=" * 80)
    print("TESTING PRODUCTION SCRAPER")
    print("=" * 80)
    print()
    print(f"Testing with Central World Bangkok")
    print(f"Place ID: {place_id}")
    print(f"Max reviews: 50")
    print()

    # Create scraper config
    config = ScraperConfig(
        fast_mode=True,
        max_rate=10.0,
        language="th",
        region="TH"
    )

    # Create scraper
    scraper = ProductionGoogleMapsScraper(config)

    # Scrape reviews
    result = await scraper.scrape_reviews(
        place_id=place_id,
        max_reviews=50,
        date_range="1year"
    )

    print()
    print("=" * 80)
    print("RESULTS")
    print("=" * 80)
    print()
    print(f"Total reviews scraped: {result['metadata']['total_reviews']}")
    print(f"Scraping rate: {result['metadata']['rate']:.2f} reviews/sec")
    print(f"Time elapsed: {result['metadata']['time_taken']:.2f} seconds")
    print()

    # Show stats
    print("Statistics:")
    for key, value in result['metadata']['stats'].items():
        print(f"  {key}: {value}")
    print()

    # Show first 3 reviews
    if result['reviews']:
        print("Sample reviews:")
        print()
        for i, review in enumerate(result['reviews'][:3], 1):
            try:
                print(f"Review {i}:")
                print(f"  ID: {review.review_id}")
                print(f"  Author: {review.author_name}")
                print(f"  Author reviews: {review.author_reviews_count}")
                print(f"  Rating: {review.rating}")
                print(f"  Date: {review.date_formatted} ({review.date_relative})")
                print(f"  Text: {review.review_text[:100]}...")
                print(f"  Likes: {review.review_likes}")
                print(f"  Photos: {review.review_photos_count}")
                if review.owner_response:
                    print(f"  Owner response: {review.owner_response[:100]}...")
                print()
            except UnicodeEncodeError:
                print(f"Review {i}: (contains Thai characters, see JSON output)")
                print()

    # Save results to file
    output_file = "test_output.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        # Convert reviews to dict for JSON serialization
        reviews_dict = [
            {
                'review_id': r.review_id,
                'author_name': r.author_name,
                'author_url': r.author_url,
                'author_reviews_count': r.author_reviews_count,
                'rating': r.rating,
                'date_formatted': r.date_formatted,
                'date_relative': r.date_relative,
                'review_text': r.review_text,
                'review_likes': r.review_likes,
                'review_photos_count': r.review_photos_count,
                'owner_response': r.owner_response,
                'page_number': r.page_number
            }
            for r in result['reviews']
        ]

        json.dump({
            'total_reviews': result['metadata']['total_reviews'],
            'scraping_rate': result['metadata']['rate'],
            'time_elapsed': result['metadata']['time_taken'],
            'stats': result['metadata']['stats'],
            'reviews': reviews_dict
        }, f, ensure_ascii=False, indent=2)

    print(f"Results saved to: {output_file}")
    print()

    return result

if __name__ == '__main__':
    asyncio.run(test_scraper())
