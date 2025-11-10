# -*- coding: utf-8 -*-
"""
Playwright Hybrid Scraper - RPC Scraping through Stealth Browser
================================================================

Uses Playwright stealth browser as a proxy/context for HTTP RPC requests.
This approach combines:
1. Browser fingerprint/session from Playwright (anti-bot)
2. Fast RPC API calls (performance)
3. Language switching through browser locale (better language control)

Author: Nextzus
Date: 2025-11-11
Version: v1_playwright_hybrid
"""
import sys
import os

# Fix Windows encoding
if sys.platform == 'win32':
    os.system('chcp 65001 > nul 2>&1')

import asyncio
import json
import re
import secrets
import base64
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from urllib.parse import quote

# Import from production scraper
from .production_scraper import (
    ProductionReview,
    ScraperConfig,
    ProductionGoogleMapsScraper
)
from ..utils.unicode_display import safe_print


def generate_random_request_id(length: int = 21) -> str:
    """
    Generate random request ID matching Project 005's implementation

    Args:
        length: Length of the ID (default 21)

    Returns:
        Base64-encoded random ID
    """
    # Calculate required bytes (from Go implementation)
    num_bytes = max((length * 6 + 7) // 8, 16)

    # Generate random bytes
    random_bytes = secrets.token_bytes(num_bytes)

    # Encode to base64 URL-safe without padding
    encoded = base64.urlsafe_b64encode(random_bytes).decode('utf-8').rstrip('=')

    # Return first 'length' characters
    return encoded[:length]


@dataclass
class PlaywrightConfig:
    """Playwright browser configuration"""
    headless: bool = True
    language: str = "en"
    region: str = "US"
    viewport_width: int = 1920
    viewport_height: int = 1080
    user_agent: Optional[str] = None
    stealth: bool = True  # Enable stealth mode


class PlaywrightHybridScraper:
    """
    Hybrid scraper that uses Playwright browser context for RPC requests

    This combines:
    - Playwright browser session (cookies, fingerprint, locale)
    - Direct RPC API calls through browser context
    - Language switching via browser preferences
    """

    def __init__(self, scraper_config: ScraperConfig, playwright_config: PlaywrightConfig):
        self.scraper_config = scraper_config
        self.playwright_config = playwright_config
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.playwright = None

        # Session request ID (generated once per scraper instance)
        self.session_request_id = generate_random_request_id(21)

        # Initialize production scraper (for parsing logic)
        self.production_scraper = ProductionGoogleMapsScraper(scraper_config)

    async def start_browser(self):
        """Launch Playwright browser with stealth settings"""
        safe_print(">> Launching Playwright browser...")

        self.playwright = await async_playwright().start()

        # Browser launch arguments for stealth + language
        launch_args = [
            '--disable-blink-features=AutomationControlled',
            '--disable-dev-shm-usage',
            '--disable-web-security',
            '--disable-features=IsolateOrigins,site-per-process',
            '--disable-site-isolation-trials',
            f'--lang={self.playwright_config.language}',  # Set browser UI language
            '--no-first-run',
            '--no-default-browser-check'
        ]

        # Launch browser
        self.browser = await self.playwright.chromium.launch(
            headless=self.playwright_config.headless,
            args=launch_args,
            chromium_sandbox=False
        )

        # Build Accept-Language header with proper priority
        if self.playwright_config.language == "en":
            accept_language = "en-US,en;q=0.9"
            language_list = ["en-US", "en"]
        elif self.playwright_config.language == "th":
            accept_language = "th-TH,th;q=0.9,en-US;q=0.8,en;q=0.7"
            language_list = ["th-TH", "th", "en-US", "en"]
        elif self.playwright_config.language == "ja":
            accept_language = "ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7"
            language_list = ["ja-JP", "ja", "en-US", "en"]
        elif self.playwright_config.language == "zh":
            accept_language = "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7"
            language_list = ["zh-CN", "zh", "en-US", "en"]
        else:
            accept_language = f"{self.playwright_config.language}-{self.playwright_config.region},{self.playwright_config.language};q=0.9,en;q=0.8"
            language_list = [f"{self.playwright_config.language}-{self.playwright_config.region}", self.playwright_config.language, "en"]

        # Create browser context with language preferences
        context_options = {
            'viewport': {
                'width': self.playwright_config.viewport_width,
                'height': self.playwright_config.viewport_height
            },
            'locale': f"{self.playwright_config.language}-{self.playwright_config.region}",
            'timezone_id': 'Asia/Bangkok' if self.playwright_config.region == 'TH' else 'America/New_York',
            'permissions': ['geolocation'],
            'extra_http_headers': {
                'Accept-Language': accept_language,
                'sec-ch-ua-platform': '"Windows"',
                'sec-ch-ua': '"Chromium";v="120", "Google Chrome";v="120", "Not=A?Brand";v="24"',
            }
        }

        if self.playwright_config.user_agent:
            context_options['user_agent'] = self.playwright_config.user_agent

        self.context = await self.browser.new_context(**context_options)

        # Set Chrome preferences for language (equivalent to chrome://settings/languages)
        await self.context.add_init_script("""
            // Override navigator.languages to match browser language preference
            Object.defineProperty(navigator, 'languages', {
                get: () => %LANGUAGES%
            });

            // Override navigator.language
            Object.defineProperty(navigator, 'language', {
                get: () => '%PRIMARY_LANGUAGE%'
            });
        """.replace('%LANGUAGES%', json.dumps(language_list))
           .replace('%PRIMARY_LANGUAGE%', language_list[0])
        )

        # Apply stealth scripts
        if self.playwright_config.stealth:
            await self._apply_stealth_scripts(self.context)

        # Create page
        self.page = await self.context.new_page()

        # Initialize Google Maps session
        await self._initialize_google_session()

        safe_print(f"[OK] Browser ready (Language: {self.playwright_config.language}-{self.playwright_config.region})")

    async def _apply_stealth_scripts(self, context: BrowserContext):
        """Apply stealth/anti-detection scripts (without overriding language settings)"""
        stealth_js = """
        // Remove webdriver property
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });

        // Override plugins
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5]
        });

        // Chrome runtime
        window.chrome = {
            runtime: {}
        };

        // Permissions
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
        );
        """

        await context.add_init_script(stealth_js)

    async def _initialize_google_session(self):
        """Initialize Google Maps session with browser"""
        safe_print(">> Initializing Google Maps session...")

        # Navigate to Google Maps to establish session
        maps_url = f"https://www.google.com/maps?hl={self.playwright_config.language}&gl={self.playwright_config.region}"

        try:
            # Use 'load' instead of 'networkidle' for faster initialization
            await self.page.goto(maps_url, wait_until='load', timeout=60000)
        except Exception as e:
            safe_print(f"[WARN] Navigation warning: {e}")
            # Continue anyway - we just need cookies/session

        # Wait for page to establish session
        await asyncio.sleep(3)

        safe_print("[OK] Google Maps session initialized")

    async def fetch_rpc_through_browser(
        self,
        place_id: str,
        page_num: int = 1,
        page_token: Optional[str] = None
    ) -> tuple[Optional[List[ProductionReview]], Optional[str]]:
        """
        Fetch RPC data through browser context using page.evaluate()
        This uses the browser's session, cookies, and fingerprint
        """

        # Build RPC URL (using language from config)
        rpc_url = (f"https://www.google.com/maps/rpc/listugcposts?"
                  f"authuser=0"
                  f"&hl={self.playwright_config.language}")

        # Build pb parameter components (matching Project 005 structure)
        page_size = 20
        encoded_page_token = quote(page_token) if page_token else ""

        pb_components = [
            f"!1m6!1s{place_id}",
            "!6m4!4m1!1e1!4m1!1e3",
            f"!2m2!1i{page_size}!2s{encoded_page_token}",
            f"!5m2!1s{self.session_request_id}!7e81",  # Use session request ID
            "!8m9!2b1!3b1!5b1!7b1",
            "!12m4!1b1!2b1!4m1!1e1!11m0!13m1!1e1",
        ]

        pb_param = "".join(pb_components)
        full_url = rpc_url + f"&pb={quote(pb_param)}"

        try:
            # Use browser's fetch API to make request with browser context
            response_data = await self.page.evaluate(f"""
                async () => {{
                    const response = await fetch('{full_url}', {{
                        method: 'GET',
                        credentials: 'include',
                        headers: {{
                            'Accept': 'application/json, text/plain, */*',
                            'Accept-Language': '{self.playwright_config.language}-{self.playwright_config.region},{self.playwright_config.language};q=0.9'
                        }}
                    }});
                    const text = await response.text();
                    return text;
                }}
            """)

            # Parse response (same as production scraper)
            if response_data.startswith(")]}'"):
                response_data = response_data[4:]

            data = json.loads(response_data)
            reviews_data = self.production_scraper.safe_get(data, 2)

            # Extract next page token
            next_page_token = data[1] if len(data) > 1 and isinstance(data[1], str) else None

            if not reviews_data:
                return [], next_page_token

            # Parse reviews using production scraper's parser
            reviews = []
            for el in reviews_data:
                review = self.production_scraper.parse_review(el, page_num)
                if review:
                    reviews.append(review)

            return reviews, next_page_token

        except Exception as e:
            import traceback
            safe_print(f"[ERROR] Error fetching page {page_num}: {e}")
            safe_print(f"[DEBUG] Traceback: {traceback.format_exc()}")
            return None, None

    async def scrape_reviews(
        self,
        place_id: str,
        max_reviews: int = 1000,
        date_range: str = "all"
    ) -> Dict[str, Any]:
        """
        Scrape reviews through Playwright browser context

        Args:
            place_id: Google Maps place ID
            max_reviews: Maximum reviews to scrape
            date_range: Date range filter

        Returns:
            Dict with reviews and metadata
        """
        safe_print("=" * 80)
        safe_print(">> PLAYWRIGHT HYBRID SCRAPER")
        safe_print("=" * 80)
        safe_print(f"Place ID: {place_id}")
        safe_print(f"Max reviews: {max_reviews}")
        safe_print(f"Date range: {date_range}")
        safe_print(f"Browser language: {self.playwright_config.language}-{self.playwright_config.region}")
        safe_print("")

        all_reviews = []
        seen_ids = set()
        page_num = 1
        next_page_token = None
        start_time = datetime.now()

        # Calculate date cutoff
        date_cutoff = self.production_scraper.calculate_date_cutoff(date_range)

        try:
            while len(all_reviews) < max_reviews:
                safe_print(f">> Fetching page {page_num} through browser...")

                reviews, next_page_token = await self.fetch_rpc_through_browser(
                    place_id, page_num, next_page_token
                )

                if reviews is None:
                    safe_print(f"[WARN] Failed to fetch page {page_num}")
                    break

                if not reviews:
                    safe_print(f"[OK] No more reviews (page {page_num})")
                    break

                # Filter duplicates and apply date range
                new_reviews = 0
                outside_date_range = 0

                for review in reviews:
                    if review.review_id not in seen_ids:
                        # Check date range
                        if date_cutoff and review.date_formatted != "Unknown Date":
                            if not self.production_scraper.is_review_within_date_range(
                                review.date_formatted, date_cutoff
                            ):
                                outside_date_range += 1
                                continue

                        seen_ids.add(review.review_id)
                        all_reviews.append(review)
                        new_reviews += 1

                        if len(all_reviews) >= max_reviews:
                            break

                safe_print(f"   [+] Page {page_num}: {new_reviews} new reviews (Total: {len(all_reviews)})")

                # Check if we should stop (date range cutoff)
                if outside_date_range > len(reviews) * 0.5:
                    safe_print(f"   [STOP] Stopping: >50% reviews outside date range")
                    break

                # Check if we have next page
                if not next_page_token:
                    safe_print(f"   [OK] No more pages")
                    break

                page_num += 1

                # Delay between pages
                await asyncio.sleep(0.5)

        except Exception as e:
            import traceback
            safe_print(f"[ERROR] Scraping error: {e}")
            safe_print(f"[DEBUG] Traceback: {traceback.format_exc()}")

        # Calculate stats
        end_time = datetime.now()
        time_taken = (end_time - start_time).total_seconds()
        rate = len(all_reviews) / time_taken if time_taken > 0 else 0

        safe_print("")
        safe_print("=" * 80)
        safe_print(">> SCRAPING COMPLETE")
        safe_print("=" * 80)
        safe_print(f"Total reviews: {len(all_reviews)}")
        safe_print(f"Time taken: {time_taken:.2f}s")
        safe_print(f"Rate: {rate:.2f} reviews/sec")
        safe_print("")

        return {
            'reviews': all_reviews,
            'metadata': {
                'total_reviews': len(all_reviews),
                'pages_scraped': page_num,
                'time_taken': time_taken,
                'rate': rate,
                'browser_language': f"{self.playwright_config.language}-{self.playwright_config.region}"
            }
        }

    async def close(self):
        """Close browser and cleanup"""
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

        safe_print("[OK] Browser closed")


# ==================== FACTORY FUNCTION ====================

def create_playwright_hybrid_scraper(
    language: str = "en",
    region: str = "US",
    headless: bool = True,
    fast_mode: bool = True
) -> PlaywrightHybridScraper:
    """
    Factory function to create Playwright hybrid scraper

    Args:
        language: Browser language (en, th, ja, etc.)
        region: Browser region (US, TH, JP, etc.)
        headless: Run browser in headless mode
        fast_mode: Use fast scraping mode

    Returns:
        Configured PlaywrightHybridScraper instance
    """
    scraper_config = ScraperConfig(
        language=language,
        region=region.lower(),
        fast_mode=fast_mode,
        max_rate=10.0
    )

    playwright_config = PlaywrightConfig(
        headless=headless,
        language=language,
        region=region.upper(),
        stealth=True
    )

    return PlaywrightHybridScraper(scraper_config, playwright_config)


# ==================== USAGE EXAMPLE ====================

async def example_usage():
    """Example: Scrape reviews with Playwright hybrid approach"""

    # Create scraper with English language
    scraper = create_playwright_hybrid_scraper(
        language="en",
        region="US",
        headless=True,
        fast_mode=True
    )

    try:
        # Start browser
        await scraper.start_browser()

        # Scrape reviews
        place_id = "0x30da3a89dde356f5:0xa8e9df0a32571ee1"  # Khao Soi Nimman
        result = await scraper.scrape_reviews(
            place_id=place_id,
            max_reviews=100,
            date_range="1year"
        )

        # Show sample reviews
        for i, review in enumerate(result['reviews'][:3], 1):
            safe_print(f"Review {i}:")
            safe_print(f"  Author: {review.author_name}")
            safe_print(f"  Rating: {review.rating}")
            safe_print(f"  Text: {review.review_text[:100]}...")
            safe_print("")

    finally:
        # Always close browser
        await scraper.close()


if __name__ == '__main__':
    asyncio.run(example_usage())
