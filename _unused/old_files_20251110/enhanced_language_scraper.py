# -*- coding: utf-8 -*-
"""
Enhanced Language Scraper with Session Management
=================================================

Based on insights from Go version:
- Session-based request IDs
- Dynamic session refresh
- Enhanced language enforcement
- Multiple anti-detection strategies

This addresses the language drift issue by:
1. Creating unique session IDs
2. Refreshing session every 50 pages
3. Using stronger language enforcement
4. Adding Google-specific headers
"""
import sys
import os
import io

# Fix Windows encoding
if sys.platform == 'win32':
    os.system('chcp 65001 > nul 2>&1')

import asyncio
import httpx
import base64
import random
import json
import time
import hashlib
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from urllib.parse import quote
from datetime import datetime

from .production_scraper import ProductionGoogleMapsScraper, ScraperConfig, ProductionReview

from dataclasses import dataclass, field

@dataclass
class EnhancedLanguageConfig:
    """Enhanced config with session management"""
    # Original ScraperConfig fields
    fast_mode: bool = True
    max_rate: float = 10.0
    use_proxy: bool = False
    proxy_list: Optional[List[str]] = None
    timeout: float = 30.0
    max_retries: int = 3
    language: str = "th"
    region: str = "th"

    # Enhanced fields
    session_refresh_interval: int = 30  # Refresh session every N pages
    use_session_ids: bool = True
    strict_language_mode: bool = True

class EnhancedLanguageScraper(ProductionGoogleMapsScraper):
    """Enhanced scraper with session-based language consistency"""

    def __init__(self, config: EnhancedLanguageConfig):
        # Convert EnhancedLanguageConfig to ScraperConfig for parent class
        scraper_config = ScraperConfig(
            fast_mode=config.fast_mode,
            max_rate=config.max_rate,
            use_proxy=config.use_proxy,
            proxy_list=config.proxy_list,
            timeout=config.timeout,
            max_retries=config.max_retries,
            language=config.language,
            region=config.region
        )

        super().__init__(scraper_config)
        self.enhanced_config = config
        self.session_id = self._generate_session_id()
        self.page_counter = 0
        self.language_failures = 0

    def _generate_session_id(self) -> str:
        """Generate unique session ID similar to Go version"""
        # Generate random bytes and encode as base64 (like Go version)
        random_bytes = base64.urlsafe_b64encode(os.urandom(16))
        return random_bytes.decode('ascii').rstrip('=')[:21]  # 21 chars like Go

    def _refresh_session(self):
        """Refresh session ID to prevent language drift"""
        old_session = self.session_id
        self.session_id = self._generate_session_id()
        print(f"   Session refreshed: {old_session[:8]}... -> {self.session_id[:8]}...")

    async def fetch_rpc_page_enhanced(self, client: httpx.AsyncClient, place_id: str,
                                     page_num: int, page_token: Optional[str] = None) -> tuple:
        """Enhanced RPC page fetch with session management"""
        self.page_counter += 1

        # Check if we need to refresh session
        if (self.enhanced_config.use_session_ids and
            self.page_counter % self.enhanced_config.session_refresh_interval == 0):
            self._refresh_session()

        # Human-like delay
        delay = self.delay_generator.random_page_delay(fast_mode=self.config.fast_mode)
        await asyncio.sleep(delay)

        # Build enhanced RPC URL with session ID
        if self.enhanced_config.use_session_ids:
            rpc_url = self._build_enhanced_rpc_url(place_id, page_token)
        else:
            # Fallback to original method
            rpc_url = self._build_original_rpc_url(place_id, page_token)

        # Enhanced headers for language enforcement
        headers = self._build_enhanced_headers()

        # Retry logic with session refresh on language failure
        for attempt in range(self.config.max_retries):
            try:
                # Record request
                self.rate_limiter.record_request()
                self.stats['total_requests'] += 1

                # Make request
                response = await client.get(rpc_url, headers=headers, timeout=self.config.timeout)

                # Parse response
                if response.status_code == 200:
                    try:
                        raw_data = response.text
                        if raw_data.startswith(")]}'"):
                            raw_data = raw_data[4:]

                        data = json.loads(raw_data)
                        reviews_data = self.safe_get(data, 2)

                        # Extract next page token
                        next_page_token = data[1] if len(data) > 1 and isinstance(data[1], str) else None

                        if not reviews_data:
                            return [], next_page_token

                        # Parse reviews with language validation
                        reviews = []
                        for i, el in enumerate(reviews_data):
                            try:
                                review = self.parse_review(el, page_num)

                                # Language validation in strict mode
                                if (self.enhanced_config.strict_language_mode and
                                    self._is_language_inconsistent(review)):
                                    self.language_failures += 1
                                    if self.language_failures > 5:
                                        # Too many language failures, refresh session
                                        self._refresh_session()
                                        self.language_failures = 0
                                        print(f"   Language drift detected, session refreshed")
                                    continue  # Skip this review

                                reviews.append(review)

                            except Exception as e:
                                print(f"   Warning: Failed to parse review {i+1}: {e}")
                                continue

                        return reviews, next_page_token

                    except json.JSONDecodeError as e:
                        print(f"   JSON decode error: {e}")
                        continue

                elif response.status_code == 429:
                    # Rate limited - switch to human mode temporarily
                    print(f"   Rate limited (429), switching to human mode for 30s")
                    await asyncio.sleep(30)
                    continue

                else:
                    print(f"   HTTP error: {response.status_code}")
                    continue

            except Exception as e:
                print(f"   Request error (attempt {attempt + 1}): {e}")
                if attempt < self.config.max_retries - 1:
                    backoff_time = (2 ** attempt) * 2
                    await asyncio.sleep(backoff_time)
                continue

        return [], None

    def _build_enhanced_rpc_url(self, place_id: str, page_token: Optional[str]) -> str:
        """Build RPC URL with session ID and enhanced parameters"""
        # Base URL with strong language enforcement
        rpc_url = (
            f"https://www.google.com/maps/rpc/listugcposts?"
            f"authuser=0"
            f"&hl={self.config.language}"
            f"&gl={self.config.region}"
            f"&tbm=lcl"
            f"&force_lang={self.config.language}"
            f"&disable_auto_translate=1"
            f"&pref_lang={self.config.language}"
            f"&session={self.session_id}"  # Session ID for consistency
        )

        # Enhanced pb parameter with session ID (like Go version)
        pb_param = f"!1m6!1s{place_id}!6m4!4m1!1e1!4m1!1e3!2m2!1i20!2s"

        if page_token:
            pb_param += page_token
        else:
            pb_param += ""

        # Use session ID in pb parameter (critical for consistency)
        pb_param += f"!5m2!1s{self.session_id}!7e81!8m9!2b1!3b1!5b1!7b1!12m4!1b1!2b1!4m1!1e1!11m4!1e3!2e1!6m1!1i2!13m1!1e1"

        return rpc_url + f"&pb={quote(pb_param)}"

    def _build_original_rpc_url(self, place_id: str, page_token: Optional[str]) -> str:
        """Fallback to original URL building method"""
        rpc_url = (f"https://www.google.com/maps/rpc/listugcposts?"
                  f"authuser=0"
                  f"&hl={self.config.language}"
                  f"&gl={self.config.region}"
                  f"&tbm=lcl"
                  f"&force_lang={self.config.language}"
                  f"&disable_auto_translate=1"
                  f"&pref_lang={self.config.language}")

        pb_param = f"!1m6!1s{place_id}!6m4!4m1!1e1!4m1!1e3!2m2!1i20!2s"

        if page_token:
            pb_param += page_token
        else:
            pb_param += ""

        pb_param += "!5m2!1sHJ8QacelO62QseMP2dTGqQQ!7e81!8m9!2b1!3b1!5b1!7b1!12m4!1b1!2b1!4m1!1e1!11m4!1e3!2e1!6m1!1i2!13m1!1e1"

        return rpc_url + f"&pb={quote(pb_param)}"

    def _build_enhanced_headers(self) -> Dict[str, str]:
        """Build enhanced headers for language enforcement"""
        headers = {
            'User-Agent': random.choice([
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            ]),
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': f"{self.config.language}-{self.config.region.upper()},{self.config.language};q=0.9,en;q=0.8",
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',

            # Google-specific headers
            'X-Goog-AuthUser': '0',
            'X-Goog-Visitor-Id': self.config.region,
            'Content-Language': self.config.language,
            'X-Preferred-Language': self.config.language,

            # Session and anti-detection headers
            'X-Session-ID': self.session_id,
            'X-Request-ID': hashlib.md5(f"{self.session_id}{self.page_counter}".encode()).hexdigest()[:16],
            'Referer': f'https://www.google.com/maps?hl={self.config.language}&gl={self.config.region}',
        }

        return headers

    def _is_language_inconsistent(self, review: ProductionReview) -> bool:
        """Check if review language is inconsistent with target language"""
        if self.config.language == "en":
            # Check for non-English characters
            text = getattr(review, 'review_text', '')
            # If more than 20% non-ASCII, consider inconsistent
            if text:
                non_ascii = sum(1 for c in text if ord(c) >= 128)
                return (non_ascii / len(text)) > 0.2
        return False

    async def scrape_reviews_enhanced(self, place_id: str, max_reviews: int,
                                     date_range: str = "all") -> Dict[str, Any]:
        """Enhanced review scraping with session management"""
        print(f"Starting enhanced scrape with session management")
        print(f"Session ID: {self.session_id}")
        print(f"Session refresh interval: {self.enhanced_config.session_refresh_interval} pages")

        # Use enhanced fetch method
        original_fetch = self.fetch_rpc_page
        self.fetch_rpc_page = self.fetch_rpc_page_enhanced

        try:
            result = await self.scrape_reviews(place_id, max_reviews, date_range)

            # Restore original method
            self.fetch_rpc_page = original_fetch

            # Add enhanced metadata
            result['metadata']['enhanced_language'] = True
            result['metadata']['session_id'] = self.session_id
            result['metadata']['language_failures'] = self.language_failures

            return result

        except Exception as e:
            # Restore original method on error
            self.fetch_rpc_page = original_fetch
            raise e

def create_enhanced_scraper(
    language: str = "en",
    region: str = "us",
    fast_mode: bool = True,
    max_rate: float = 8.0,
    use_proxy: bool = False,
    proxy_list: Optional[List[str]] = None,
    timeout: float = 30.0,
    max_retries: int = 3,
    session_refresh_interval: int = 50,
    use_session_ids: bool = True,
    strict_language_mode: bool = True
) -> EnhancedLanguageScraper:
    """Factory function for enhanced scraper"""
    config = EnhancedLanguageConfig(
        fast_mode=fast_mode,
        max_rate=max_rate,
        use_proxy=use_proxy,
        proxy_list=proxy_list,
        timeout=timeout,
        max_retries=max_retries,
        language=language,
        region=region,
        session_refresh_interval=session_refresh_interval,
        use_session_ids=use_session_ids,
        strict_language_mode=strict_language_mode
    )

    return EnhancedLanguageScraper(config)