# -*- coding: utf-8 -*-
"""
Playwright Stealth + RPC Scraper
================================

Hybrid approach:
1. RPC search to find places
2. Pick place to scrape
3. Playwright Stealth browser with language settings (EN/TH)
4. Use HTTP RPC calls through Playwright browser context

This combines browser authenticity with HTTP speed.
"""
import sys
import os
import time
import asyncio
import json
from typing import List, Dict, Any, Optional

# Fix Windows encoding
if sys.platform == 'win32':
    os.system('chcp 65001 > nul 2>&1')

try:
    from playwright.async_api import async_playwright, Browser, BrowserContext, Page
except ImportError:
    print("Error: Playwright not installed. Run: pip install playwright")
    print("Then run: playwright install")
    sys.exit(1)

from src.search.rpc_place_search import RpcPlaceSearch
from src.utils.anti_bot_utils import HumanLikeDelay, RateLimitDetector

class PlaywrightRPCScraper:
    """Hybrid scraper using Playwright Stealth browser for RPC calls"""

    def __init__(self, language="en", region="us", headless=True):
        self.language = language
        self.region = region
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

        # Anti-bot utilities
        self.delay = HumanLikeDelay()
        self.rate_limiter = RateLimitDetector()

    async def __aenter__(self):
        """Async context manager entry"""
        await self.start_browser()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close_browser()

    async def start_browser(self):
        """Start Playwright Stealth browser"""
        print("Starting Playwright Stealth browser...")

        self.playwright = await async_playwright().start()

        # Launch browser with stealth options
        browser_args = [
            '--no-sandbox',
            '--disable-blink-features=AutomationControlled',
            '--disable-dev-shm-usage',
            '--disable-gpu',
            '--no-first-run',
            '--no-service-autorun',
            '--disable-default-apps',
            '--disable-popup-blocking'
        ]

        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=browser_args
        )

        # Create context with language settings
        context_options = {
            'locale': f'{self.language}-{self.region.upper()}',
            'timezone_id': self._get_timezone(),
            'permissions': ['geolocation'],
            'user_agent': self._get_stealth_user_agent()
        }

        self.context = await self.browser.new_context(**context_options)

        # Set additional headers
        await self.context.set_extra_http_headers({
            'Accept-Language': f'{self.language}-{self.region.upper()},{self.language};q=0.9,en;q=0.8',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        })

        self.page = await self.context.new_page()

        # Anti-detection scripts
        await self.page.add_init_script("""
            // Remove webdriver property
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });

            // Override permissions query
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
            );

            // Override plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });

            // Override languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ["en", "th", "' + self.language + '"],
            });
        """)

        print(f"Browser started with language: {self.language}, region: {self.region}")

    async def close_browser(self):
        """Close browser and cleanup"""
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    def _get_timezone(self):
        """Get timezone based on region"""
        timezones = {
            'us': 'America/New_York',
            'th': 'Asia/Bangkok',
            'jp': 'Asia/Tokyo',
            'kr': 'Asia/Seoul'
        }
        return timezones.get(self.region, 'UTC')

    def _get_stealth_user_agent(self):
        """Get realistic user agent"""
        user_agents = {
            'en': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'th': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
        }
        return user_agents.get(self.language, user_agents['en'])

    async def search_places(self, query: str, max_places: int = 10) -> List[Dict[str, Any]]:
        """Search for places using RPC search"""
        print(f"Searching for: {query}")

        try:
            # Use existing RPC search
            search = RpcPlaceSearch()
            results = search.search_places(query, max_places, self.language, self.region)

            print(f"Found {len(results)} places:")
            for i, place in enumerate(results, 1):
                print(f"  {i}. {place.get('name', 'Unknown')} - {place.get('rating', 0)}★ ({place.get('total_reviews', 0)} reviews)")

            return results

        except Exception as e:
            print(f"Search error: {e}")
            return []

    async def pick_place(self, places: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Interactive place selection"""
        if not places:
            return None

        print("\nSelect a place to scrape:")
        for i, place in enumerate(places, 1):
            print(f"  {i}. {place.get('name', 'Unknown')} - Rating: {place.get('rating', 0)}")
            print(f"     Address: {place.get('address', 'Unknown')[:50]}...")

        while True:
            try:
                choice = input(f"\nEnter choice (1-{len(places)}) or 0 to cancel: ")
                choice_num = int(choice)

                if choice_num == 0:
                    return None
                elif 1 <= choice_num <= len(places):
                    return places[choice_num - 1]
                else:
                    print("Invalid choice. Please try again.")

            except (ValueError, KeyboardInterrupt):
                print("\nInvalid input. Please enter a number.")

    async def scrape_reviews_via_playwright(self, place_id: str, max_reviews: int = 1000) -> Dict[str, Any]:
        """Scrape reviews using HTTP RPC calls through Playwright browser"""
        print(f"\nScraping reviews for place_id: {place_id}")
        print(f"Target: {max_reviews} reviews")
        print(f"Language: {self.language}")

        reviews = []
        page_num = 1
        page_token = None
        start_time = time.time()

        try:
            while len(reviews) < max_reviews and page_num <= 200:  # Max 200 pages
                print(f"Fetching page {page_num}...")

                # Rate limiting
                should_slow, delay = self.rate_limiter.should_slow_down(max_rate=8.0)
                if should_slow:
                    print(f"   Rate limit detected, waiting {delay:.1f}s...")
                    await asyncio.sleep(delay)

                # Human-like delay
                delay_time = self.delay.random_page_delay(fast_mode=True)
                await asyncio.sleep(delay_time)

                # Build RPC request URL
                url = "https://www.google.com/maps/rpc/listugcposts"

                # Enhanced pb parameter for Playwright
                pb_base = f"!1m6!1s{place_id}!6m4!4m1!1e1!4m1!1e3!2m2!1i20!2s{page_token if page_token else ''}!5m2!1s{self.language}!2s{self.region}!7e81!8m9!3m2!1sen!2sUS!4m2!1sen!2sUS"

                params = {
                    'pb': pb_base,
                    'hl': self.language,
                    'gl': self.region,
                    'async': 'reviews',
                    'source': '3',
                    'm': '1'
                }

                # Make request through Playwright page (preserves browser context)
                response = await self.page.goto(f"{url}?pb={pb_base}&hl={self.language}&gl={self.region}&async=reviews&source=3&m=1")

                if not response or response.status != 200:
                    print(f"   HTTP {response.status if response else 'NO_RESPONSE'}")
                    break

                # Get response text
                content = await response.text()

                if not content or not content.strip():
                    print("   Empty response")
                    break

                # Process RPC response
                try:
                    # Strip RPC prefix
                    content = content.strip()
                    if content.startswith(')]}\''):
                        content = content[4:]

                    data = json.loads(content)

                    # Extract reviews
                    page_reviews = self._parse_reviews_from_data(data)

                    if not page_reviews:
                        print("   No reviews found in response")
                        break

                    reviews.extend(page_reviews)
                    print(f"   Got {len(page_reviews)} reviews (total: {len(reviews)})")

                    # Get next page token
                    next_token = data[1] if len(data) > 1 and isinstance(data[1], str) else None
                    if not next_token:
                        print("   No more pages available")
                        break

                    page_token = next_token
                    page_num += 1

                except json.JSONDecodeError as e:
                    print(f"   JSON decode error: {e}")
                    print(f"   Content preview: {content[:200]}...")
                    break
                except Exception as e:
                    print(f"   Parsing error: {e}")
                    break

                # Check if we have enough reviews
                if len(reviews) >= max_reviews:
                    print(f"   Reached target of {max_reviews} reviews")
                    reviews = reviews[:max_reviews]  # Trim to exact number
                    break

        except Exception as e:
            print(f"Scraping error: {e}")

        end_time = time.time()

        # Analyze language consistency
        english_count = 0
        thai_count = 0

        for review in reviews:
            text = review.get('review_text', '')
            if text:
                has_thai = any('\u0E00' <= char <= '\u0E7F' for char in text)
                if has_thai:
                    thai_count += 1
                else:
                    english_count += 1

        total_reviews = len(reviews)
        english_pct = (english_count / total_reviews * 100) if total_reviews > 0 else 0

        print(f"\nScraping completed!")
        print(f"Total reviews: {total_reviews}")
        print(f"English: {english_count} ({english_pct:.1f}%)")
        print(f"Thai: {thai_count}")
        print(f"Time: {end_time - start_time:.1f} seconds")
        print(f"Rate: {total_reviews/(end_time - start_time):.1f} reviews/sec")

        return {
            'reviews': reviews,
            'metadata': {
                'total_reviews': total_reviews,
                'english_reviews': english_count,
                'thai_reviews': thai_count,
                'english_consistency': english_pct,
                'time_elapsed': end_time - start_time,
                'pages_scraped': page_num - 1,
                'scraper_type': 'playwright_rpc',
                'language': self.language,
                'region': self.region
            }
        }

    def _parse_reviews_from_data(self, data: List) -> List[Dict[str, Any]]:
        """Parse reviews from RPC response data"""
        reviews = []

        try:
            # Navigate through nested data structure
            if len(data) > 0 and isinstance(data[0], list):
                for el in data[0]:
                    if isinstance(el, list) and len(el) >= 3:
                        # Extract review data
                        review_data = {
                            'review_id': self._safe_get(el, 0, default=""),
                            'author_name': self._safe_get(el, 1, 4, 5, 0, default="Unknown"),
                            'author_url': self._safe_get(el, 1, 4, 2, 0, default=""),
                            'rating': self._safe_get(el, 2, 0, 0, default=0),
                            'review_text': self._safe_get(el, 2, 15, 0, 0, default=""),
                            'date_relative': self._safe_get(el, 2, 1, default=""),
                            'review_likes': self._safe_get(el, 2, 16, default=0),
                            'page_number': 1  # Will be updated later
                        }

                        if review_data['review_text']:  # Only add reviews with text
                            reviews.append(review_data)

        except Exception as e:
            print(f"Parse error: {e}")

        return reviews

    def _safe_get(self, data: List, *indices, default=None):
        """Safely navigate nested data structure"""
        try:
            current = data
            for index in indices:
                if isinstance(current, list) and index < len(current):
                    current = current[index]
                else:
                    return default
            return current
        except (IndexError, TypeError, KeyError):
            return default

async def interactive_playwright_scraper():
    """Interactive Playwright RPC scraper"""
    print("=" * 80)
    print("PLAYWRIGHT STEALTH + RPC SCRAPER")
    print("=" * 80)
    print("Interactive scraper using Playwright browser for RPC calls")
    print("Combines browser authenticity with HTTP performance")
    print()

    # Get language preference
    while True:
        lang_choice = input("Select language (1=English, 2=Thai): ").strip()
        if lang_choice == '1':
            language = 'en'
            region = 'us'
            break
        elif lang_choice == '2':
            language = 'th'
            region = 'th'
            break
        else:
            print("Invalid choice. Please enter 1 or 2.")

    print(f"Language set to: {language} ({region})")

    # Get max reviews
    while True:
        try:
            max_reviews = int(input("Maximum reviews to scrape (default 1000): ").strip() or "1000")
            if max_reviews > 0:
                break
        except ValueError:
            print("Please enter a valid number.")

    print(f"Will scrape up to {max_reviews} reviews")

    # Get search query
    query = input("\nEnter search query: ").strip()
    if not query:
        query = "restaurants in Chiang Mai"

    async with PlaywrightRPCScraper(language=language, region=region, headless=True) as scraper:
        # Search for places
        places = await scraper.search_places(query, max_places=10)

        if not places:
            print("No places found. Exiting.")
            return

        # Pick place
        selected_place = await scraper.pick_place(places)

        if not selected_place:
            print("No place selected. Exiting.")
            return

        # Scrape reviews
        print(f"\nSelected: {selected_place.get('name', 'Unknown')}")
        print(f"Starting review scraping...")

        result = await scraper.scrape_reviews_via_playwright(
            selected_place.get('place_id', ''),
            max_reviews
        )

        # Show results
        metadata = result['metadata']
        print(f"\n" + "=" * 80)
        print("FINAL RESULTS")
        print("=" * 80)
        print(f"Place: {selected_place.get('name', 'Unknown')}")
        print(f"Total reviews scraped: {metadata['total_reviews']}")
        print(f"Language consistency: {metadata['english_consistency']:.1f}% English")
        print(f"Time: {metadata['time_elapsed']:.1f} seconds")
        print(f"Performance: {metadata['total_reviews']/metadata['time_elapsed']:.1f} reviews/sec")

        # Save results
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = f"outputs/playwright_{timestamp}"
        os.makedirs(output_dir, exist_ok=True)

        with open(f"{output_dir}/reviews.json", 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2, default=str)

        with open(f"{output_dir}/metadata.json", 'w', encoding='utf-8') as f:
            json.dump({
                'place': selected_place,
                'metadata': metadata,
                'scraper_config': {
                    'language': language,
                    'region': region,
                    'max_reviews': max_reviews
                }
            }, f, ensure_ascii=False, indent=2, default=str)

        print(f"Results saved to: {output_dir}/")

async def main():
    """Main entry point"""
    try:
        await interactive_playwright_scraper()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Check if Playwright is installed
    try:
        import playwright
    except ImportError:
        print("Playwright not installed. Installing...")
        os.system("pip install playwright")
        os.system("playwright install")
        print("Playwright installed. Please run this script again.")
        sys.exit(0)

    asyncio.run(main())