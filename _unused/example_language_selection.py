#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example: Language Selection for Review Scraping
================================================

This example demonstrates how to scrape Google Maps reviews
in different languages (English, Thai, Japanese, Chinese).

The language parameter controls what language Google returns
the review text in (when available).

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


async def scrape_in_language(language_code: str, region_code: str, language_name: str):
    """
    Scrape reviews in a specific language

    Args:
        language_code: Language code (en, th, ja, zh-CN, etc.)
        region_code: Region code (us, th, jp, cn, etc.)
        language_name: Display name for the language
    """
    print("=" * 80)
    print(f"Scraping reviews in {language_name}")
    print("=" * 80)
    print(f"Language Code: {language_code}")
    print(f"Region Code: {region_code}")
    print()

    # Create scraper with language settings
    scraper = create_production_scraper(
        language=language_code,
        region=region_code,
        fast_mode=True,
        max_rate=10.0
    )

    # Scrape reviews
    # Example: Central World Bangkok
    place_id = "0x30e29ecfc2f455e1:0xc4ad0280d8906604"

    result = await scraper.scrape_reviews(
        place_id=place_id,
        max_reviews=50,
        date_range="1year"
    )

    # Export with language indicator in filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    lang_code = language_code.replace("-", "_").upper()

    csv_filename = f"reviews_{lang_code}_{timestamp}.csv"
    json_filename = f"reviews_{lang_code}_{timestamp}.json"

    scraper.export_to_csv(result['reviews'], csv_filename)
    scraper.export_to_json(result, json_filename)

    print()
    print(f"✅ Completed: {len(result['reviews'])} reviews scraped in {language_name}")
    print(f"📁 Files saved:")
    print(f"   - {csv_filename}")
    print(f"   - {json_filename}")
    print()

    return result


async def main():
    """Main function - select language and scrape"""

    print()
    print("=" * 80)
    print("GOOGLE MAPS REVIEW SCRAPER - LANGUAGE SELECTION")
    print("=" * 80)
    print()
    print("Select language for review text:")
    print("1. English (EN)")
    print("2. Thai (TH)")
    print("3. Japanese (JA)")
    print("4. Chinese Simplified (ZH-CN)")
    print("5. Scrape ALL languages (will take longer)")
    print()

    choice = input("Enter your choice (1-5): ").strip()

    # Language configurations
    languages = {
        "1": {"code": "en", "region": "us", "name": "English"},
        "2": {"code": "th", "region": "th", "name": "Thai"},
        "3": {"code": "ja", "region": "jp", "name": "Japanese"},
        "4": {"code": "zh-CN", "region": "cn", "name": "Chinese Simplified"},
    }

    if choice in languages:
        # Scrape single language
        lang = languages[choice]
        await scrape_in_language(
            language_code=lang["code"],
            region_code=lang["region"],
            language_name=lang["name"]
        )

    elif choice == "5":
        # Scrape all languages
        print("\n🚀 Scraping reviews in ALL languages...")
        print("This will take a few minutes...\n")

        for key in ["1", "2", "3", "4"]:
            lang = languages[key]
            await scrape_in_language(
                language_code=lang["code"],
                region_code=lang["region"],
                language_name=lang["name"]
            )

            # Small delay between languages to be nice to Google
            if key != "4":
                print("⏳ Waiting 5 seconds before next language...")
                await asyncio.sleep(5)

        print()
        print("=" * 80)
        print("✅ ALL LANGUAGES COMPLETED!")
        print("=" * 80)

    else:
        print("❌ Invalid choice. Please run again and select 1-5.")
        return

    print()
    print("🎉 Done! Check the output files in the current directory.")
    print()


# ==================== PROGRAMMATIC USAGE ====================

async def example_programmatic_english():
    """
    Example: Use programmatically to get English reviews
    """
    scraper = create_production_scraper(
        language="en",  # English
        region="us",    # US region
        fast_mode=True
    )

    result = await scraper.scrape_reviews(
        place_id="0x30e29ecfc2f455e1:0xc4ad0280d8906604",
        max_reviews=100,
        date_range="6months"
    )

    # Access reviews
    for review in result['reviews'][:5]:  # First 5 reviews
        print(f"Rating: {review.rating} stars")
        print(f"Text: {review.review_text[:100]}...")
        print(f"Date: {review.date_formatted}")
        print("-" * 50)

    return result


async def example_programmatic_thai():
    """
    Example: Use programmatically to get Thai reviews
    """
    scraper = create_production_scraper(
        language="th",  # Thai
        region="th",    # Thailand region
        fast_mode=True
    )

    result = await scraper.scrape_reviews(
        place_id="0x30e29ecfc2f455e1:0xc4ad0280d8906604",
        max_reviews=100,
        date_range="6months"
    )

    # Access reviews
    for review in result['reviews'][:5]:  # First 5 reviews
        print(f"คะแนน: {review.rating} ดาว")
        print(f"รีวิว: {review.review_text[:100]}...")
        print(f"วันที่: {review.date_formatted}")
        print("-" * 50)

    return result


if __name__ == "__main__":
    # Run interactive mode
    asyncio.run(main())

    # Or uncomment to run programmatically:
    # asyncio.run(example_programmatic_english())
    # asyncio.run(example_programmatic_thai())
