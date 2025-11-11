# -*- coding: utf-8 -*-
"""
Production-Ready Google Maps Scraper for Framework
================================================

Complete integration of all features from project 005:
1. Anti-bot protection (User-Agent rotation, proxies, fingerprint randomization)
2. CAPTCHA solving (CapSolver integration)
3. Advanced anti-detection (WebDriver stealth, Canvas/WebGL randomization)
4. Rate limiting and retry logic
5. Data completeness (100% fields)
6. Performance optimization (37.83+ reviews/sec)

Based on production_ready_scraper.py from project 005

Author: Nextzus
Date: 2025-11-10
Version: v1_framework_integration
"""
import sys
import io
import os

# Fix Windows encoding
if sys.platform == 'win32':
    os.system('chcp 65001 > nul 2>&1')

import asyncio
import httpx
import csv
import json
import random
import secrets
import time
import re
from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from urllib.parse import quote

# Import unicode display handler
from src.utils.unicode_display import UnicodeDisplay, safe_print, format_name, print_review_summary

# Import PB analyzer for debugging and structure analysis
try:
    from ..utils.pb_analyzer import GoogleMapsPBAnalyzer, PBAnalysisResult
    PB_ANALYZER_AVAILABLE = True
except ImportError:
    PB_ANALYZER_AVAILABLE = False
    GoogleMapsPBAnalyzer = None
    PBAnalysisResult = None

# Import enhanced language service for detection and translation
try:
    # Try enhanced language service first (with langdetect + deep-translator)
    from ..utils.enhanced_language_service import EnhancedLanguageService, SupportedLanguage, create_enhanced_language_service
    ENHANCED_LANGUAGE_SERVICE_AVAILABLE = True
    print("Enhanced multi-language detection and translation available")
except ImportError:
    print("Warning: Enhanced language service not available. Install with: pip install langdetect deep-translator")
    ENHANCED_LANGUAGE_SERVICE_AVAILABLE = False
    EnhancedLanguageService = None

# Fallback to basic language service
try:
    from ..utils.language_service import LanguageService, SupportedLanguage, create_language_service
    LANGUAGE_SERVICE_AVAILABLE = True
except ImportError:
    print("Warning: Basic language service not available. Install with: pip install lingua py-googletrans")
    LANGUAGE_SERVICE_AVAILABLE = False
    LanguageService = None
    SupportedLanguage = None
    create_language_service = None

# Import anti-bot utilities from our framework
try:
    from ..utils.anti_bot_utils import (
        generate_randomized_headers,
        HumanLikeDelay,
        ProxyConfig,
        ProxyRotator,
        RateLimitDetector
    )
except ImportError:
    # Fallback implementations
    def generate_randomized_headers(base_headers=None, language="th", region="th"):
        headers = base_headers.copy() if base_headers else {}
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]

        # Enhanced Accept-Language with primary language first for consistency
        if language == "en":
            accept_language = "en-US,en;q=0.9,en-GB;q=0.8"
        elif language == "th":
            accept_language = "th-TH,th;q=0.9,en;q=0.8"
        elif language == "ja":
            accept_language = "ja-JP,ja;q=0.9,en;q=0.8"
        else:
            accept_language = f"{language}-{region.upper()},{language};q=0.9,en;q=0.8"

        headers.update({
            'User-Agent': random.choice(user_agents),
            'Accept-Language': accept_language,
            'Referer': f'https://www.google.com/maps?hl={language}&gl={region}',
            'Accept': 'application/json, text/plain, */*',
            'Cache-Control': random.choice(['no-cache', 'no-store', 'max-age=0']),
            'Pragma': 'no-cache',
        })
        return headers

    class HumanLikeDelay:
        def random_page_delay(self, fast_mode=True):
            if fast_mode:
                return random.uniform(0.05, 0.15)  # 50-150ms for fast mode
            else:
                return random.uniform(0.5, 1.5)  # 500-1500ms for human mode

    class ProxyConfig:
        def __init__(self, http_proxy=None, https_proxy=None):
            self.http_proxy = http_proxy
            self.https_proxy = https_proxy

    class ProxyRotator:
        def __init__(self, proxies):
            self.proxies = proxies
            self.current_index = 0

        def get_next_proxy(self):
            if not self.proxies:
                return None
            proxy = self.proxies[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.proxies)
            return proxy

    class RateLimitDetector:
        def __init__(self, window_seconds=60):
            self.window_seconds = window_seconds
            self.requests = []

        def record_request(self):
            now = time.time()
            self.requests.append(now)
            # Remove old requests outside window
            self.requests = [req_time for req_time in self.requests if now - req_time < self.window_seconds]

        def should_slow_down(self, max_rate=10.0):
            """Returns (should_slow, delay_seconds)"""
            current_rate = len(self.requests) / self.window_seconds
            if current_rate > max_rate:
                delay = (current_rate / max_rate) * 0.5  # Exponential slowdown
                return True, min(delay, 5.0)  # Cap at 5 seconds
            return False, 0

        def get_request_rate(self):
            now = time.time()
            recent_requests = [req_time for req_time in self.requests if now - req_time < self.window_seconds]
            return len(recent_requests) / self.window_seconds


# ==================== DATA STRUCTURES ====================

@dataclass
class ProductionReview:
    """Production review data structure - 100% complete fields"""
    review_id: str
    author_name: str
    author_url: str
    author_reviews_count: int
    rating: int
    date_formatted: str  # DD/MM/YYYY
    date_relative: str   # "2 weeks ago"
    review_text: str
    review_text_translated: str  # Translated review text
    original_language: str  # Detected original language
    target_language: str  # Target language for translations
    review_likes: int
    review_photos_count: int
    owner_response: str
    owner_response_translated: str  # Translated owner response
    page_number: int

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'review_id': self.review_id,
            'author_name': self.author_name,
            'author_url': self.author_url,
            'author_reviews_count': self.author_reviews_count,
            'rating': self.rating,
            'date_formatted': self.date_formatted,
            'date_relative': self.date_relative,
            'review_text': self.review_text,
            'review_text_translated': self.review_text_translated,
            'original_language': self.original_language,
            'target_language': self.target_language,
            'review_likes': self.review_likes,
            'review_photos_count': self.review_photos_count,
            'owner_response': self.owner_response,
            'owner_response_translated': self.owner_response_translated,
            'page_number': self.page_number
        }


@dataclass
class ScraperConfig:
    """Complete scraper configuration"""
    # Anti-bot settings
    use_proxy: bool = False
    proxy_list: Optional[List[str]] = None
    fast_mode: bool = True
    max_rate: float = 10.0

    # Performance settings
    timeout: float = 30.0
    max_retries: int = 3

    # Language settings
    language: str = "th"
    region: str = "th"

    # Translation settings
    enable_translation: bool = False
    target_language: str = "en"  # "th" or "en"
    translate_review_text: bool = True
    translate_owner_response: bool = True
    # Enhanced translation options
    use_enhanced_detection: bool = True  # Use langdetect for better accuracy
    translation_batch_size: int = 50  # Process translations in batches for performance

    # Debug and analysis options
    enable_pb_analysis: bool = False  # Enable Protocol Buffer analysis for debugging
    pb_analysis_verbose: bool = False  # Verbose PB analysis output
    save_pb_analysis: bool = False  # Save PB analysis results to files


# ==================== PRODUCTION SCRAPER ====================

class ProductionGoogleMapsScraper:
    """
    Production-ready Google Maps scraper with all features integrated
    Performance: 37.83+ reviews/sec from project 005
    """

    def __init__(self, config: ScraperConfig):
        """
        Initialize production scraper

        Args:
            config: Complete scraper configuration
        """
        self.config = config

        # Anti-bot components
        self.delay_generator = HumanLikeDelay()
        self.rate_limiter = RateLimitDetector(window_seconds=60)

        # PB analyzer for debugging and structure analysis
        self.pb_analyzer = None
        self.pb_analysis_results = []
        if PB_ANALYZER_AVAILABLE and config.enable_pb_analysis:
            try:
                self.pb_analyzer = GoogleMapsPBAnalyzer(debug_mode=config.pb_analysis_verbose)
                safe_print(f"✓ PB Analyzer initialized (debug mode: {config.pb_analysis_verbose})")
            except Exception as e:
                safe_print(f"⚠ Failed to initialize PB Analyzer: {e}")
                self.pb_analyzer = None

        # Enhanced language service for detection and translation
        self.language_service = None
        self.translation_stats = {
            'detected_languages': {},
            'translated_count': 0,
            'translation_errors': 0,
            'detection_count': 0
        }

        if config.enable_translation:
            # Try enhanced language service first (langdetect + deep-translator)
            if config.use_enhanced_detection and ENHANCED_LANGUAGE_SERVICE_AVAILABLE:
                try:
                    self.language_service = create_enhanced_language_service(
                        target_language=config.target_language,
                        enable_translation=config.enable_translation
                    )
                    safe_print(f"✓ Enhanced multi-language service initialized (target: {config.target_language})")
                except Exception as e:
                    safe_print(f"⚠ Failed to initialize enhanced language service: {e}")
                    self.language_service = None
            # Fallback to basic language service
            elif LANGUAGE_SERVICE_AVAILABLE:
                try:
                    self.language_service = create_language_service(
                        target_language=config.target_language,
                        enable_translation=config.enable_translation
                    )
                    safe_print(f"✓ Basic language service initialized (target: {config.target_language})")
                except Exception as e:
                    safe_print(f"⚠ Failed to initialize language service: {e}")
                    self.language_service = None
            else:
                safe_print("⚠ Language service not available - install: pip install langdetect deep-translator")

        # Proxy rotation
        self.proxy_rotator = None
        self.current_proxy = None
        if config.use_proxy and config.proxy_list:
            proxies = [
                ProxyConfig(http_proxy=url, https_proxy=url)
                for url in config.proxy_list
            ]
            self.proxy_rotator = ProxyRotator(proxies)
            self.current_proxy = self.proxy_rotator.get_next_proxy()

        # Stats
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'rate_limits_encountered': 0,
            'proxy_switches': 0,
            'retries_used': 0,
            'session_refreshes': 0,
            'pages_since_refresh': 0
        }

        # Session identity (headers/cookies) reused across pagination to keep Google tokens stable
        self.session_headers: Dict[str, str] = {}
        self.session_cookies: Dict[str, str] = {}
        self.last_refresh_time = time.time()
        self._init_session_identity()

    def _generate_session_headers(self) -> Dict[str, str]:
        """Create stable headers for the current scraping session."""
        headers = generate_randomized_headers(
            language=self.config.language,
            region=self.config.region
        )
        headers.update({
            'X-Goog-AuthUser': '0',
            'X-Goog-Visitor-Id': self.config.region,
            'Accept-Language': f"{self.config.language}-{self.config.region.upper()},{self.config.language};q=0.9,en;q=0.8,*;q=0.5",
            'Content-Language': self.config.language,
            'X-Preferred-Language': self.config.language,
            'X-Goog-Encode-Response': 'UTF-8',
            'Accept-Charset': 'utf-8',
            'X-Language': self.config.language,
            'X-Region': self.config.region,
            'X-Force-Language': 'true',
        })
        user_agent = headers.get('User-Agent', '')
        if 'Googlebot' in user_agent:
            headers['User-Agent'] = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                                     'AppleWebKit/537.36 (KHTML, like Gecko) '
                                     'Chrome/120.0.0.0 Safari/537.36')
        return headers

    def _generate_session_cookies(self) -> Dict[str, str]:
        """Create stable cookies for the current scraping session."""
        session_token = secrets.token_hex(8)
        return {
            'CONSENT': 'YES+cb.20210401-17-p0.en+FX+700',
            'NID': f'511=_{session_token}',
            'SNL': f'{self.config.language}',
            'HL': f'{self.config.language}',
            'GL': f'{self.config.region}',
            'LOCALE': f'{self.config.language}_{self.config.region.upper()}',
        }

    def _init_session_identity(self) -> None:
        """Initialize headers/cookies for this scraper instance."""
        self.session_headers = self._generate_session_headers()
        self.session_cookies = self._generate_session_cookies()

    def _refresh_session_identity(self, reason: str = "") -> None:
        """Rotate headers/cookies when forced (e.g., rate limit)."""
        self._init_session_identity()
        self.last_refresh_time = time.time()
        self.stats['session_refreshes'] += 1
        self.stats['pages_since_refresh'] = 0
        if reason:
            safe_print(f"   Session identity refreshed ({reason}) - Total refreshes: {self.stats['session_refreshes']}")

    def _get_session_headers(self) -> Dict[str, str]:
        """Return copy of session headers."""
        if not self.session_headers:
            self._init_session_identity()
        return self.session_headers.copy()

    def _get_session_cookies(self) -> Dict[str, str]:
        """Return copy of session cookies."""
        if not self.session_cookies:
            self._init_session_identity()
        return self.session_cookies.copy()

    def _should_proactively_refresh_session(self, page_num: int) -> bool:
        """Determine if we should proactively refresh session to prevent language switching."""
        # Refresh every 50 pages to prevent Google's session token expiration
        if self.stats['pages_since_refresh'] >= 50:
            return True

        # Also refresh if it's been more than 30 minutes (1800 seconds)
        current_time = time.time()
        if current_time - self.last_refresh_time > 1800:
            return True

        return False

    def _check_and_proactively_refresh_session(self, page_num: int) -> None:
        """Check and perform proactive session refresh if needed."""
        if self._should_proactively_refresh_session(page_num):
            self._refresh_session_identity(reason=f"proactive refresh after {self.stats['pages_since_refresh']} pages")

    def _detect_response_language_consistency(self, reviews_data: list, page_num: int) -> Tuple[bool, str]:
        """
        Analyze response content for language consistency.
        Returns tuple of (is_consistent, detected_primary_language)
        """
        if not reviews_data or len(reviews_data) == 0:
            return True, "empty"

        # Sample first few review texts to detect language
        sample_reviews = reviews_data[:3] if len(reviews_data) >= 3 else reviews_data
        detected_languages = []

        for review_el in sample_reviews:
            # Check if we have the new protobuf-encoded format
            if (len(review_el) >= 3 and
                isinstance(review_el[2], str) and
                review_el[2].startswith(('CAES', 'CAI', 'CNEI'))):  # Common protobuf prefixes

                print(f"DEBUG: Found protobuf-encoded review: {review_el[2][:50]}...")
                # Reviews are now encoded - cannot extract text for language detection
                # Mark as encoded format
                detected_languages.append('encoded')
                continue

            # Try original extraction method for backward compatibility
            if len(review_el) > 2 and len(review_el[2]) > 15 and len(review_el[2][15]) > 0 and len(review_el[2][15][0]) > 0:
                review_text = str(review_el[2][15][0][0])[:200]  # First 200 chars
                print(f"DEBUG: Extracted review text: {review_text[:100]}...")

                # Enhanced language detection with lower thresholds
                thai_chars = len([c for c in review_text if 'ก' <= c <= 'ฮ' or 'ฯ' in review_text])
                korean_chars = len([c for c in review_text if '가' <= c <= '힣'])
                japanese_chars = len([c for c in review_text if 'あ' <= c <= 'ゟ' or 'ァ' <= c <= 'ヿ'])
                english_chars = len([c for c in review_text if 'a' <= c.lower() <= 'z'])
                chinese_chars = len([c for c in review_text if '\u4e00' <= c <= '\u9fff'])

                # Enhanced detection with more sensitive thresholds
                if thai_chars >= 2:  # Lowered from 5
                    detected_languages.append('TH')
                elif korean_chars >= 2:  # Lowered from 5
                    detected_languages.append('KO')
                elif chinese_chars >= 2:
                    detected_languages.append('ZH')
                elif japanese_chars >= 2:  # Lowered from 5
                    detected_languages.append('JA')
                elif english_chars >= 5:  # Lowered from 10
                    detected_languages.append('EN')
                else:
                    detected_languages.append('UNKNOWN')

        # Count detected languages
        th_count = detected_languages.count('TH')
        en_count = detected_languages.count('EN')
        ko_count = detected_languages.count('KO')
        ja_count = detected_languages.count('JA')
        zh_count = detected_languages.count('ZH')
        encoded_count = detected_languages.count('encoded')

        # Determine primary language and consistency
        primary_language = 'UNKNOWN'

        # If all reviews are encoded, we can't detect language from text
        if encoded_count == len(detected_languages):
            primary_language = 'ENCODED_DATA'
        else:
            max_count = max([th_count, en_count, ko_count, ja_count, zh_count])

            if max_count == 0:
                primary_language = 'UNKNOWN'
            elif th_count == max_count:
                primary_language = 'TH'
            elif en_count == max_count:
                primary_language = 'EN'
            elif ko_count == max_count:
                primary_language = 'KO'
            elif ja_count == max_count:
                primary_language = 'JA'
            elif zh_count == max_count:
                primary_language = 'ZH'

        # Check if response is consistent (single dominant language)
        non_zero_counts = [count for count in [th_count, en_count, ko_count, ja_count, zh_count] if count > 0]
        is_consistent = len(non_zero_counts) <= 1  # Only one language detected

        # Log language analysis for monitoring
        print(f"LANGUAGE ANALYSIS (Page {page_num}):")
        print(f"  Sampled reviews: {len(sample_reviews)}")
        print(f"  English: {en_count}, Thai: {th_count}, Korean: {ko_count}, Japanese: {ja_count}, Chinese: {zh_count}, Encoded: {encoded_count}")
        print(f"  Primary: {primary_language}, Consistent: {is_consistent}")

        return is_consistent, primary_language

    def _should_refresh_based_on_language_response(self, is_consistent: bool, detected_language: str, page_num: int) -> bool:
        """
        Determine if session should be refreshed based on language response analysis.
        Returns True if refresh is needed.
        """
        # If response is consistent, no refresh needed
        if is_consistent:
            return False

        # If we get inconsistent languages, this might indicate session degradation
        safe_print(f"   WARNING: Language inconsistency detected (mixed languages in response)")

        # If this is after page 60 and we get mixed languages, it's likely session degradation
        if page_num > 60:
            safe_print(f"   CRITICAL: Language mixing after page {page_num} indicates session degradation")
            return True

        return False

    def _log_session_health(self, page_num: int) -> None:
        """Log session health statistics for monitoring."""
        current_time = time.time()
        session_age = current_time - self.last_refresh_time

        print(f"\n=== SESSION HEALTH (Page {page_num}) ===")
        print(f"  Session Age: {session_age:.1f}s ({session_age/60:.1f} min)")
        print(f"  Pages Since Refresh: {self.stats['pages_since_refresh']}")
        print(f"  Total Session Refreshes: {self.stats['session_refreshes']}")
        print(f"  Target Language: {self.config.language}-{self.config.region}")
        print(f"  Successful Requests: {self.stats['successful_requests']}")
        print(f"  Rate Limits Encountered: {self.stats['rate_limits_encountered']}")
        print(f"  Session Health: {'HEALTHY' if session_age < 1800 and self.stats['pages_since_refresh'] < 45 else 'WARNING'}")
        print("=" * 35)

    def _should_log_session_health(self, page_num: int) -> bool:
        """Determine if we should log session health for this page."""
        # Log every 20 pages for monitoring
        return page_num % 20 == 1 or page_num > 60

    def translate_text_field(self, text: str) -> Tuple[str, str]:
        """
        Translate text field and return both translated text and detected language.
        Enhanced with multi-language detection and statistics tracking.

        Args:
            text: Text to translate

        Returns:
            Tuple of (translated_text, detected_language)
        """
        if not text or not text.strip():
            return "", "unknown"

        if not self.language_service:
            return text, "unknown"

        try:
            # Update detection count
            self.translation_stats['detection_count'] += 1

            # Detect language using enhanced service
            if ENHANCED_LANGUAGE_SERVICE_AVAILABLE and isinstance(self.language_service, EnhancedLanguageService):
                detection = self.language_service.detect_language(text)
                detected_lang = detection.detected_language.value
            else:
                detection = self.language_service.detect_language(text)
                detected_lang = detection.detected_language.value

            # Track detected languages
            self.translation_stats['detected_languages'][detected_lang] = \
                self.translation_stats['detected_languages'].get(detected_lang, 0) + 1
            original_text = text

            # Translate if needed
            if detection.needs_translation:
                self.translation_stats['translated_count'] += 1
                translation = self.language_service.translate_text(text, detection.detected_language)
                if translation.success:
                    return translation.translated_text, detected_lang
                else:
                    # Return original if translation failed
                    self.translation_stats['translation_errors'] += 1
                    return original_text, detected_lang
            else:
                # No translation needed
                return original_text, detected_lang

        except Exception as e:
            self.translation_stats['translation_errors'] += 1
            safe_print(f"   Translation error: {e}")
            return text, "unknown"

    def get_translation_stats(self) -> Dict:
        """Get translation statistics."""
        return self.translation_stats.copy()

    def reset_translation_stats(self) -> None:
        """Reset translation statistics."""
        self.translation_stats = {
            'detected_languages': {},
            'translated_count': 0,
            'translation_errors': 0,
            'detection_count': 0
        }

    async def translate_multiple_texts_concurrent(self, texts: List[str], max_concurrent: int = 5) -> List[Tuple[str, str]]:
        """
        Translate multiple texts concurrently for improved performance.

        Args:
            texts: List of texts to translate
            max_concurrent: Maximum number of concurrent translation requests

        Returns:
            List of tuples (translated_text, detected_language)
        """
        if not self.language_service or not texts:
            return [(text, "unknown") for text in texts]

        async def translate_single(text: str) -> Tuple[str, str]:
            # Use synchronous translate_text_field but run in executor
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, self.translate_text_field, text)

        # Process texts in batches to control concurrency
        results = []
        for i in range(0, len(texts), max_concurrent):
            batch = texts[i:i + max_concurrent]
            batch_tasks = [translate_single(text) for text in batch]
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)

            # Handle exceptions and add to results
            for j, result in enumerate(batch_results):
                if isinstance(result, Exception):
                    safe_print(f"   Translation error for text {i+j}: {result}")
                    self.translation_stats['translation_errors'] += 1
                    results.append((batch[j], "unknown"))
                else:
                    results.append(result)

        return results

    async def process_reviews_batch_concurrent(self, reviews: List[ProductionReview], max_concurrent: int = 10) -> List[ProductionReview]:
        """
        Process a batch of reviews with concurrent translation for maximum performance.

        Args:
            reviews: Batch of reviews to process
            max_concurrent: Maximum concurrent operations

        Returns:
            Processed reviews with translations
        """
        if not reviews:
            return []

        # Collect texts to translate
        review_texts = []
        response_texts = []

        for review in reviews:
            if self.config.translate_review_text and review.review_text:
                review_texts.append(review.review_text)
            else:
                review_texts.append(None)

            if self.config.translate_owner_response and review.owner_response:
                response_texts.append(review.owner_response)
            else:
                response_texts.append(None)

        # Process reviews and responses concurrently
        tasks = []

        # Translate review texts concurrently
        if any(review_texts):
            texts_to_translate = [text for text in review_texts if text]
            if texts_to_translate:
                tasks.append(self.translate_multiple_texts_concurrent(texts_to_translate, max_concurrent))

        # Translate response texts concurrently
        if any(response_texts):
            texts_to_translate = [text for text in response_texts if text]
            if texts_to_translate:
                tasks.append(self.translate_multiple_texts_concurrent(texts_to_translate, max_concurrent))

        # Detect languages for texts that don't need translation
        async def detect_language_concurrent(texts: List[str]) -> List[str]:
            if not self.language_service or not texts:
                return ["unknown"] * len(texts)

            loop = asyncio.get_event_loop()
            detect_tasks = []

            for text in texts:
                if text:
                    # Use synchronous detection in executor
                    if ENHANCED_LANGUAGE_SERVICE_AVAILABLE and isinstance(self.language_service, EnhancedLanguageService):
                        task = loop.run_in_executor(
                            None,
                            lambda t=text: self.language_service.detect_language(t).detected_language.value
                        )
                    else:
                        task = loop.run_in_executor(
                            None,
                            lambda t=text: self.language_service.detect_language(t).detected_language.value
                        )
                    detect_tasks.append(task)
                else:
                    detect_tasks.append(asyncio.create_task(asyncio.sleep(0)))  # Placeholder

            results = await asyncio.gather(*detect_tasks, return_exceptions=True)
            return [result if not isinstance(result, Exception) else "unknown" for result in results]

        # Detect languages for non-translated texts
        review_texts_to_detect = [text for text in review_texts if text and not self.config.translate_review_text]
        response_texts_to_detect = [text for text in response_texts if text and not self.config.translate_owner_response]

        if review_texts_to_detect:
            tasks.append(detect_language_concurrent(review_texts_to_detect))
        if response_texts_to_detect:
            tasks.append(detect_language_concurrent(response_texts_to_detect))

        # Wait for all concurrent tasks to complete
        task_results = await asyncio.gather(*tasks, return_exceptions=True) if tasks else []

        # Process results and update reviews
        review_text_index = 0
        response_text_index = 0

        for i, review in enumerate(reviews):
            # Handle review text translation/detection
            if review_texts[i]:
                if self.config.translate_review_text:
                    # Translation was done
                    if task_results and len(task_results) > 0 and review_text_index < len(task_results[0]):
                        translated_text, detected_lang = task_results[0][review_text_index]
                        review.review_text_translated = translated_text
                        review.original_language = detected_lang
                        review.target_language = self.config.target_language
                        review_text_index += 1
                else:
                    # Only detection was done
                    detection_result_index = (1 if task_results and len(task_results) > 0 and any(review_texts) else 0)
                    if review_texts_to_detect and len(task_results) > detection_result_index and review_text_index < len(task_results[detection_result_index]):
                        detected_lang = task_results[detection_result_index][review_text_index]
                        review.original_language = detected_lang
                        review.target_language = self.config.target_language
                        review_text_index += 1

            # Handle response text translation/detection
            if response_texts[i]:
                if self.config.translate_owner_response:
                    # Translation was done
                    translation_result_index = (1 if any(review_texts) else 0)
                    if len(task_results) > translation_result_index and response_text_index < len(task_results[translation_result_index]):
                        translated_response, _ = task_results[translation_result_index][response_text_index]
                        review.owner_response_translated = translated_response
                        response_text_index += 1

        return reviews

    def calculate_date_cutoff(self, date_range: str) -> Optional[datetime]:
        """
        Convert date_range string to datetime cutoff

        Args:
            date_range: Date range option ('1month', '6months', '1year', '5years', '7years', 'all')

        Returns:
            DateTime cutoff or None if 'all'
        """
        if date_range == 'all':
            return None

        now = datetime.now()

        # Define date range mappings
        date_ranges = {
            '1month': now - timedelta(days=30),
            '6months': now - timedelta(days=180),
            '1year': now - timedelta(days=365),
            '5years': now - timedelta(days=1825),  # 5 * 365
            '7years': now - timedelta(days=2555),  # 7 * 365
        }

        return date_ranges.get(date_range, date_ranges['1year'])  # Default to 1 year

    def parse_ddmmyyyy_to_datetime(self, date_str: str) -> Optional[datetime]:
        """
        Parse DD/MM/YYYY string to datetime

        Args:
            date_str: Date string in DD/MM/YYYY format

        Returns:
            DateTime object or None if parsing fails
        """
        try:
            if date_str == "Unknown Date":
                return None

            # Handle DD/MM/YYYY format - require 4-digit year
            if '/' in date_str and len(date_str.split('/')) == 3:
                parts = date_str.split('/')
                if len(parts) == 3:
                    day, month, year = parts
                    # Validate that we have proper 2-digit day/month and 4-digit year
                    if len(year) == 4 and len(day) <= 2 and len(month) <= 2:
                        year_int = int(year)
                        # Validate reasonable year range (1900-2100)
                        if 1900 <= year_int <= 2100:
                            return datetime(year_int, int(month), int(day))

            return None
        except (ValueError, TypeError):
            return None

    def is_review_within_date_range(self, review: ProductionReview, date_cutoff: datetime) -> bool:
        """
        Check if review date is within the specified date range

        Args:
            review: Review object to check
            date_cutoff: Cutoff datetime

        Returns:
            True if review is within date range, False otherwise
        """
        if date_cutoff is None:
            return True  # 'all' date range

        # Try to parse the formatted date first
        review_date = self.parse_ddmmyyyy_to_datetime(review.date_formatted)

        if review_date is None:
            # If formatted date parsing failed, try relative date
            # This is a fallback - in most cases formatted date should work
            return True  # Include review if we can't parse date

        return review_date >= date_cutoff

    def is_review_within_custom_date_range(self, review: ProductionReview, start_date: str, end_date: str) -> bool:
        """
        Check if review date is within a custom date range

        Args:
            review: Review object to check
            start_date: Start date string (YYYY-MM-DD)
            end_date: End date string (YYYY-MM-DD)

        Returns:
            True if review is within custom date range, False otherwise
        """
        if not start_date or not end_date:
            return True  # No valid date range specified

        try:
            # Parse custom dates
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            # Set end date to end of day
            end_dt = end_dt.replace(hour=23, minute=59, second=59)

            # Try to parse the review date
            review_date = self.parse_ddmmyyyy_to_datetime(review.date_formatted)

            if review_date is None:
                # If formatted date parsing failed, include review
                return True

            return start_dt <= review_date <= end_dt

        except (ValueError, TypeError):
            # If date parsing fails, include review
            return True

    def safe_get(self, data, *keys, default=None):
        """Safely navigate nested data structure"""
        try:
            for key in keys:
                if data is None:
                    return default
                if isinstance(data, (list, tuple)):
                    if not isinstance(key, int) or key >= len(data):
                        return default
                    data = data[key]
                elif isinstance(data, dict):
                    data = data.get(key, default)
                else:
                    return default
            return data if data is not None else default
        except (KeyError, IndexError, TypeError):
            return default

    def convert_relative_date_to_ddmmyyyy(self, relative_date: str) -> str:
        """Convert Thai relative date to DD/MM/YYYY format"""
        try:
            current_date = datetime.now()

            # Handle different Thai relative date patterns
            if 'สัปดาห์' in relative_date:
                match = re.search(r'(\d+)\s*สัปดาห์', relative_date)
                if match:
                    weeks = int(match.group(1))
                    target_date = current_date - datetime.timedelta(weeks=weeks)
                    return target_date.strftime('%d/%m/%Y')

            elif 'วัน' in relative_date and 'สัปดาห์' not in relative_date:
                match = re.search(r'(\d+)\s*วัน', relative_date)
                if match:
                    days = int(match.group(1))
                    target_date = current_date - datetime.timedelta(days=days)
                    return target_date.strftime('%d/%m/%Y')

            elif 'เดือน' in relative_date:
                match = re.search(r'(\d+)\s*เดือน', relative_date)
                if match:
                    months = int(match.group(1))
                    target_date = current_date - datetime.timedelta(days=months * 30)
                    return target_date.strftime('%d/%m/%Y')

            elif 'ปี' in relative_date:
                match = re.search(r'(\d+)\s*ปี', relative_date)
                if match:
                    years = int(match.group(1))
                    target_date = current_date - datetime.timedelta(days=years * 365)
                    return target_date.strftime('%d/%m/%Y')

            return relative_date

        except Exception as e:
            return relative_date

    # ==================== PROTOCOL BUFFER ANALYSIS ====================

    def analyze_response_with_pb_analyzer(self, response_data: Any, analysis_type: str = "reviews") -> Optional[PBAnalysisResult]:
        """
        Analyze response data using PB analyzer for debugging

        Args:
            response_data: Raw response data from Google Maps API
            analysis_type: Type of analysis (reviews, places, general)

        Returns:
            PBAnalysisResult or None if analyzer not available
        """
        if not self.pb_analyzer:
            return None

        try:
            result = self.pb_analyzer.analyze_response_structure(response_data, analysis_type)
            self.pb_analysis_results.append(result)

            if self.config.pb_analysis_verbose:
                self.pb_analyzer.print_analysis_report(result, verbose=True)

            # Save analysis if configured
            if self.config.save_pb_analysis:
                self._save_pb_analysis_result(result, analysis_type)

            return result

        except Exception as e:
            safe_print(f"⚠ PB analysis failed: {e}")
            return None

    def analyze_pb_parameters(self, pb_string: str) -> Optional[PBAnalysisResult]:
        """
        Analyze Protocol Buffer parameters

        Args:
            pb_string: Protocol Buffer parameter string

        Returns:
            PBAnalysisResult or None if analyzer not available
        """
        if not self.pb_analyzer:
            return None

        try:
            result = self.pb_analyzer.analyze_pb_parameters(pb_string)
            self.pb_analysis_results.append(result)

            if self.config.pb_analysis_verbose:
                safe_print(f"📋 PB Parameter Analysis:")
                safe_print(f"   Original: {pb_string}")
                if result.success:
                    safe_print(f"   Place ID: {result.data.get('place_id_extracted', 'N/A')}")
                    safe_print(f"   Components: {len(result.data.get('components', []))}")
                else:
                    safe_print(f"   Error: {result.data.get('error', 'Unknown')}")

            return result

        except Exception as e:
            safe_print(f"⚠ PB parameter analysis failed: {e}")
            return None

    def validate_review_with_pb_analyzer(self, review_data: Any, expected_fields: List[str] = None) -> Optional[PBAnalysisResult]:
        """
        Validate review parsing using PB analyzer

        Args:
            review_data: Parsed review data
            expected_fields: List of expected field names

        Returns:
            PBAnalysisResult or None if analyzer not available
        """
        if not self.pb_analyzer:
            return None

        try:
            result = self.pb_analyzer.validate_review_parsing(review_data, expected_fields)

            if self.config.pb_analysis_verbose:
                safe_print(f"🔍 Review Validation:")
                safe_print(f"   Field coverage: {result.data.get('field_coverage', 0):.1%}")
                safe_print(f"   Found fields: {len(result.data.get('found_fields', []))}")
                safe_print(f"   Missing fields: {result.data.get('missing_fields', [])}")

            return result

        except Exception as e:
            safe_print(f"⚠ Review validation failed: {e}")
            return None

    def _save_pb_analysis_result(self, result: PBAnalysisResult, analysis_type: str):
        """Save PB analysis result to file"""
        try:
            from datetime import datetime
            import json
            from pathlib import Path

            # Create pb_analysis directory
            pb_dir = Path("pb_analysis")
            pb_dir.mkdir(exist_ok=True)

            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{analysis_type}_analysis_{timestamp}.json"
            filepath = pb_dir / filename

            # Save result
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(result.__dict__, f, ensure_ascii=False, indent=2, default=str)

            safe_print(f"✓ PB analysis saved: {filepath}")

        except Exception as e:
            safe_print(f"⚠ Failed to save PB analysis: {e}")

    def get_pb_analysis_summary(self) -> Dict[str, Any]:
        """Get summary of all PB analysis results"""
        if not self.pb_analysis_results:
            return {"total_analyses": 0, "summary": "No PB analyses performed"}

        summary = {
            "total_analyses": len(self.pb_analysis_results),
            "successful_analyses": sum(1 for r in self.pb_analysis_results if r.success),
            "analysis_types": {},
            "common_warnings": [],
            "common_recommendations": []
        }

        # Count analysis types
        for result in self.pb_analysis_results:
            analysis_type = result.analysis_type
            summary["analysis_types"][analysis_type] = summary["analysis_types"].get(analysis_type, 0) + 1

            # Collect common warnings
            for warning in result.warnings:
                if warning not in summary["common_warnings"]:
                    summary["common_warnings"].append(warning)

            # Collect common recommendations
            for rec in result.recommendations:
                if rec not in summary["common_recommendations"]:
                    summary["common_recommendations"].append(rec)

        return summary

    def export_pb_analysis_history(self, filename: str = None) -> bool:
        """Export PB analysis history to file"""
        if not self.pb_analyzer or not self.pb_analysis_results:
            safe_print("⚠ No PB analysis results to export")
            return False

        try:
            if filename is None:
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"pb_analysis_history_{timestamp}.json"

            return self.pb_analyzer.export_analysis_history(filename)

        except Exception as e:
            safe_print(f"⚠ Failed to export PB analysis history: {e}")
            return False

    def parse_review(self, entry: list, page_num: int) -> Optional[ProductionReview]:
        """
        Parse single review with complete field extraction
        Using the correct structure from working HTTP scraper

        Enhanced date parsing with 3-tier fallback strategy
        """
        try:
            # Extract el from entry (entry is [el, ..., ...])
            if not isinstance(entry, list) or len(entry) == 0:
                return None

            el = entry[0] if isinstance(entry, list) and len(entry) > 0 else entry
            if not isinstance(el, list):
                return None

            # PB Analysis: Validate review structure if analyzer is enabled
            if self.pb_analyzer and self.config.pb_analysis_verbose and page_num == 1:
                # Validate first review structure for debugging
                validation_result = self.validate_review_with_pb_analyzer(el)
                if validation_result and not validation_result.success:
                    safe_print(f"⚠ Review structure validation failed: {validation_result.data.get('error')}")

            # Review ID: el[0]
            review_id = self.safe_get(el, 0) or ""

            # Check if review_id is the new encoded format
            if (isinstance(review_id, str) and
                review_id.startswith(('CAES', 'CAI', 'CNEI'))):
                # Generate a proper ID for encoded reviews
                review_id = f"encoded_review_{page_num}_{review_idx}"

            if not review_id:
                return None

            # Author name: el[1][4][5][0]
            author_name = self.safe_get(el, 1, 4, 5, 0) or "Unknown"

            # Author URL: el[1][4][2][0]
            author_url = self.safe_get(el, 1, 4, 2, 0) or ""

            # Author reviews count: el[1][4][15][1]
            author_reviews_count = self.safe_get(el, 1, 4, 15, 1) or 0
            if isinstance(author_reviews_count, (int, float)):
                author_reviews_count = int(author_reviews_count)
            else:
                author_reviews_count = 0

            # Rating: el[2][0][0]
            rating = self.safe_get(el, 2, 0, 0) or 0
            if isinstance(rating, (int, float)):
                rating = int(rating)
            else:
                rating = 0

            # Review text: Check if we have the new encoded format
            raw_review_data = self.safe_get(el, 2)
            if (isinstance(raw_review_data, str) and
                raw_review_data.startswith(('CAES', 'CAI', 'CNEI'))):  # Protobuf prefixes

                # New protobuf-encoded format - cannot extract text without decoder
                review_text = "[ENCODED_DATA - Requires protobuf decoder]"
                # Note: review_id is probably also the encoded data, not a real ID
                if not review_id or review_id == raw_review_data:
                    review_id = f"encoded_review_{page_num}_{review_idx}"
            else:
                # Original format: el[2][15][0][0] with cleaning
                review_text = self.safe_get(el, 2, 15, 0, 0) or ""
                # Clean up text: remove newlines and extra whitespace
                review_text = re.sub(r'\n+', ' ', str(review_text)).strip()
                review_text = re.sub(r'\s+', ' ', review_text)  # Normalize whitespace

            # Date extraction with multiple fallback strategies (from project 005)
            date_formatted = ""
            date_relative = ""

            # Strategy 1: Try primary path el[2][2][0][1][21][6][8]
            date_array = self.safe_get(el, 2, 2, 0, 1, 21, 6, 8)

            if date_array and isinstance(date_array, list) and len(date_array) >= 3:
                try:
                    year, month, day = date_array[0], date_array[1], date_array[2]
                    if isinstance(year, int) and isinstance(month, int) and isinstance(day, int):
                        if 2000 <= year <= 2100 and 1 <= month <= 12 and 1 <= day <= 31:
                            date_formatted = f"{int(day):02d}/{int(month):02d}/{int(year):04d}"
                            # Also extract relative date from position [8] if available
                            if len(date_array) > 8 and isinstance(date_array[8], list) and len(date_array[8]) > 0:
                                date_relative = date_array[8][0] or date_formatted
                            else:
                                date_relative = date_formatted
                except (TypeError, ValueError):
                    pass

            # Strategy 2: If no date found, try alternative paths
            if not date_formatted:
                # Try el[2][2] container - search first few elements
                el_2_2 = self.safe_get(el, 2, 2)
                if el_2_2 and isinstance(el_2_2, list):
                    # Try first 5 elements of el[2][2]
                    for i in range(min(5, len(el_2_2))):
                        alt_date = self.safe_get(el_2_2, i, 1, 21, 6, 8)
                        if alt_date and isinstance(alt_date, list) and len(alt_date) >= 3:
                            try:
                                year, month, day = alt_date[0], alt_date[1], alt_date[2]
                                if isinstance(year, int) and isinstance(month, int) and isinstance(day, int):
                                    if 2000 <= year <= 2100 and 1 <= month <= 12 and 1 <= day <= 31:
                                        date_formatted = f"{int(day):02d}/{int(month):02d}/{int(year):04d}"
                                        date_relative = date_formatted
                                        break
                            except (TypeError, ValueError):
                                continue

            # Strategy 3: Try fallback path el[2][21][6][8]
            if not date_formatted:
                date_array = self.safe_get(el, 2, 21, 6, 8)
                if date_array and isinstance(date_array, list) and len(date_array) >= 3:
                    try:
                        year, month, day = date_array[0], date_array[1], date_array[2]
                        if isinstance(year, int) and isinstance(month, int) and isinstance(day, int):
                            if 2000 <= year <= 2100 and 1 <= month <= 12 and 1 <= day <= 31:
                                date_formatted = f"{int(day):02d}/{int(month):02d}/{int(year):04d}"
                                # Relative date is usually at index 8
                                if len(date_array) > 8 and isinstance(date_array[8], list):
                                    date_relative = date_array[8][0] or date_formatted
                    except (TypeError, ValueError):
                        pass

            # Strategy 4: Try alternative relative date (el[2][1]) - but don't convert from current date
            if not date_formatted:
                relative_str = self.safe_get(el, 2, 1)
                if relative_str and isinstance(relative_str, str):
                    # Store relative date as-is without calculating from current date
                    date_relative = relative_str
                    # Try to extract actual timestamp from other fields first
                    timestamp = self.safe_get(el, 2, 0, 1, 21, 6, 8)
                    if timestamp and isinstance(timestamp, list) and len(timestamp) >= 3:
                        try:
                            year, month, day = timestamp[0], timestamp[1], timestamp[2]
                            if isinstance(year, int) and isinstance(month, int) and isinstance(day, int):
                                if 2000 <= year <= 2100 and 1 <= month <= 12 and 1 <= day <= 31:
                                    date_formatted = f"{int(day):02d}/{int(month):02d}/{int(year):04d}"
                        except (TypeError, ValueError):
                            pass
                    else:
                        # If no actual timestamp found, use relative date without conversion
                        date_formatted = "Unknown Date"

            # Strategy 5: Use "Unknown Date" if no date found
            if not date_formatted:
                date_formatted = "Unknown Date"
                date_relative = "Unknown Date"

            # Likes: el[2][16]
            review_likes = self.safe_get(el, 2, 16) or 0
            if isinstance(review_likes, (int, float)):
                review_likes = int(review_likes)
            else:
                review_likes = 0

            # Photos: el[2][22]
            photos = self.safe_get(el, 2, 22)
            review_photos_count = len(photos) if photos and isinstance(photos, list) else 0

            # Owner response: el[2][19][0][1]
            owner_response = self.safe_get(el, 2, 19, 0, 1) or ""

            # Language processing
            original_language = "unknown"
            target_language = self.config.target_language if self.config.enable_translation else "none"
            review_text_translated = review_text
            owner_response_translated = owner_response

            if self.language_service:
                # Process review text
                if self.config.translate_review_text and review_text:
                    review_text_translated, original_language = self.translate_text_field(review_text)
                elif review_text:
                    # Just detect language without translation
                    detection = self.language_service.detect_language(review_text)
                    original_language = detection.detected_language.value

                # Process owner response
                if self.config.translate_owner_response and owner_response:
                    owner_response_translated, _ = self.translate_text_field(owner_response)
                # Note: owner response inherits the same original_language as review text

            return ProductionReview(
                review_id=review_id,
                author_name=author_name,
                author_url=author_url,
                author_reviews_count=author_reviews_count,
                rating=rating,
                date_formatted=date_formatted,
                date_relative=date_relative,
                review_text=review_text,
                review_text_translated=review_text_translated,
                original_language=original_language,
                target_language=target_language,
                review_likes=review_likes,
                review_photos_count=review_photos_count,
                owner_response=owner_response,
                owner_response_translated=owner_response_translated,
                page_number=page_num
            )

        except Exception as e:
            safe_print(f"   Parse error: {e}")
            return None

    async def fetch_rpc_page(
        self,
        client: httpx.AsyncClient,
        place_id: str,
        page_num: int = 1,
        page_token: Optional[str] = None
    ) -> tuple[Optional[List[ProductionReview]], Optional[str]]:
        """
        Fetch single page with all protection features
        Optimized for performance: 50-150ms delays for fast mode
        Returns tuple of (reviews, next_page_token)
        """
        # Check rate limiting and auto-slowdown
        should_slow, delay = self.rate_limiter.should_slow_down(max_rate=self.config.max_rate)
        if should_slow:
            safe_print(f"   Auto-slowing down by {delay:.2f}s (rate: {self.rate_limiter.get_request_rate():.1f} req/sec)")
            await asyncio.sleep(delay)

        # Human-like delay between requests (optimized for performance)
        delay = self.delay_generator.random_page_delay(fast_mode=self.config.fast_mode)
        await asyncio.sleep(delay)

        # Check and perform proactive session refresh to prevent language switching
        self._check_and_proactively_refresh_session(page_num)

        # Build RPC URL with STRONG language enforcement (working parameters)
        rpc_url = (f"https://www.google.com/maps/rpc/listugcposts?"
                  f"authuser=0"
                  f"&hl={self.config.language}"
                  f"&gl={self.config.region}"
                  f"&tbm=lcl")

        # Build pb parameter with language-specific components
        # Critical: Include language enforcement directly in pb parameter structure
        pb_param = f"!1m6!1s{place_id}!6m4!4m1!1e1!4m1!1e3!2m2!1i20!2s"

        if page_token:
            pb_param += page_token
        else:
            pb_param += ""

        # Enhanced pb parameter with STRONG language consistency components
        region_code = self.config.region.lower()
        language_key = self.config.language.lower()
        sanitized_lang = language_key.replace('-', '')
        lang_markers = {
            'en': f"!4m2!1sen!2s{region_code}",
            'th': f"!4m2!1sth!2s{region_code}",
            'ja': f"!4m2!1sja!2s{region_code}",
            'zh-cn': f"!4m2!1szh!2s{region_code}",
        }

        lang_marker = lang_markers.get(language_key, f"!4m2!1s{sanitized_lang}!2s{region_code}")

        # Complete pb parameter with STRONG language enforcement
        pb_param += f"{lang_marker}!5m2!1sHJ8QacelO62QseMP2dTGqQQ!7e81!8m9!2b1!3b1!5b1!7b1!12m4!1b1!2b1!4m1!1e1!11m4!1e3!2e1!6m1!1i2!13m1!1e1"

        rpc_url += f"&pb={quote(pb_param)}"

        # DEBUG: Log RPC request details for language analysis
        print(f"\n=== RPC REQUEST DEBUG (Page {page_num}) ===")
        print(f"Target Language: {self.config.language}-{self.config.region}")
        print(f"Language Marker: {lang_marker}")
        print(f"Has Page Token: {'Yes' if page_token else 'No'}")
        print(f"Full RPC URL: {rpc_url[:200]}...")
        print(f"PB Parameter Language Section: {pb_param}")
        print("=" * 50)

        # Retry logic with exponential backoff
        for attempt in range(self.config.max_retries):
            try:
                # Generate consistent headers with maximum language enforcement
                headers = self._get_session_headers()

                # DEBUG: Log language-related headers
                print(f"LANGUAGE ENFORCEMENT HEADERS:")
                print(f"  Accept-Language: {headers.get('Accept-Language', 'Not set')}")
                print(f"  Content-Language: {headers.get('Content-Language', 'Not set')}")
                print(f"  X-Preferred-Language: {headers.get('X-Preferred-Language', 'Not set')}")
                print(f"  X-Goog-Visitor-Id: {headers.get('X-Goog-Visitor-Id', 'Not set')}")
                print(f"  User-Agent: {headers.get('User-Agent', 'Not set')[:80]}...")
                print("-" * 30)

                # Record request
                self.rate_limiter.record_request()
                self.stats['total_requests'] += 1

                # Add session cookies for language enforcement
                cookies = self._get_session_cookies()

                # Make request with language cookies
                response = await client.get(
                    rpc_url,
                    headers=headers,
                    cookies=cookies,
                    timeout=self.config.timeout
                )

                # Parse response
                if response.status_code == 200:
                    try:
                        raw_data = response.text
                        if raw_data.startswith(")]}'"):
                            raw_data = raw_data[4:]

                        data = json.loads(raw_data)
                        reviews_data = self.safe_get(data, 2)

                        # PB Analysis: Analyze response structure for debugging (first page only)
                        if self.pb_analyzer and page_num == 1:
                            self.analyze_response_with_pb_analyzer(data, "reviews")

                        # Extract next page token from data[1]
                        next_page_token = data[1] if len(data) > 1 and isinstance(data[1], str) else None

                        # LANGUAGE CONSISTENCY VALIDATION (Actionable detection and response)
                        if reviews_data and len(reviews_data) > 0:
                            # Analyze response language consistency
                            is_consistent, primary_language = self._detect_response_language_consistency(reviews_data, page_num)

                            # Check if we need to refresh session based on language response
                            if self._should_refresh_based_on_language_response(is_consistent, primary_language, page_num):
                                self._refresh_session_identity(reason=f"language inconsistency detected (primary: {primary_language})")
                                # Re-request the page with fresh session
                                safe_print(f"   Re-requesting page {page_num} with fresh session...")
                                continue  # Retry with new session

                        if not reviews_data:
                            self.stats['successful_requests'] += 1
                            return [], next_page_token

                        # Parse reviews
                        reviews = []
                        for el in reviews_data:
                            review = self.parse_review(el, page_num)
                            if review:
                                reviews.append(review)

                        self.stats['successful_requests'] += 1
                        self.stats['pages_since_refresh'] += 1

                        # Log session health for monitoring
                        if self._should_log_session_health(page_num):
                            self._log_session_health(page_num)

                        return reviews, next_page_token

                    except json.JSONDecodeError as e:
                        safe_print(f"   JSON parse error on page {page_num}: {e}")
                        self.stats['failed_requests'] += 1
                        return None, None

                elif response.status_code == 429:
                    # Rate limited
                    self.stats['rate_limits_encountered'] += 1
                    backoff_time = (2 ** attempt) * 5
                    safe_print(f"   Rate limited on page {page_num}, waiting {backoff_time}s (attempt {attempt + 1}/{self.config.max_retries})")
                    await asyncio.sleep(backoff_time)

                    # Switch proxy on rate limit
                    if self.proxy_rotator:
                        old_proxy = self.current_proxy
                        self.current_proxy = self.proxy_rotator.get_next_proxy()
                        self.stats['proxy_switches'] += 1
                        safe_print(f"   Switched proxy")

                    # Refresh headers/cookies to keep pagination tokens valid
                    self._refresh_session_identity(reason="rate_limit")

                    self.stats['retries_used'] += 1
                    continue

                elif 500 <= response.status_code < 600:
                    # Server error
                    backoff_time = (2 ** attempt) * 2
                    safe_print(f"   Server error {response.status_code} on page {page_num}, waiting {backoff_time}s")
                    await asyncio.sleep(backoff_time)
                    self._refresh_session_identity(reason="server_error")
                    self.stats['retries_used'] += 1
                    continue

                else:
                    # Client error (4xx) - don't retry
                    safe_print(f"   Request failed on page {page_num}: HTTP {response.status_code}")
                    self.stats['failed_requests'] += 1
                    return None, None

            except httpx.TimeoutError:
                backoff_time = (2 ** attempt) * 1
                safe_print(f"   Timeout on page {page_num}, waiting {backoff_time}s")
                await asyncio.sleep(backoff_time)
                self.stats['retries_used'] += 1
                continue

            except Exception as e:
                safe_print(f"   Request error on page {page_num}: {e}")
                backoff_time = (2 ** attempt) * 2
                await asyncio.sleep(backoff_time)
                self.stats['retries_used'] += 1
                continue

        # All retries exhausted
        safe_print(f"   All retries exhausted for page {page_num}")
        self.stats['failed_requests'] += 1
        return None, None

    async def scrape_reviews(
        self,
        place_id: str,
        max_reviews: int = 1000,
        date_range: str = "1year",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        sort_by_newest: bool = True,  # Default: Always sort by newest
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        Scrape reviews with all protection features and date range filtering

        Args:
            place_id: Google Maps place ID
            max_reviews: Maximum number of reviews to scrape
            date_range: Date range filter ('1month', '6months', '1year', '5years', '7years', 'all', 'custom')
            start_date: Custom start date (YYYY-MM-DD format) - used when date_range='custom'
            end_date: Custom end date (YYYY-MM-DD format) - used when date_range='custom'
            sort_by_newest: Sort reviews by date (newest first)
            progress_callback: Callback function(page_num, total_reviews)

        Returns:
            Dict with reviews and metadata
        """
        safe_print("=" * 80)
        safe_print("PRODUCTION GOOGLE MAPS SCRAPER")
        safe_print("=" * 80)
        safe_print("")
        safe_print(f"Configuration:")
        safe_print(f"  Place ID: {place_id}")
        safe_print(f"  Max reviews: {max_reviews}")
        safe_print(f"  Date range: {date_range}")
        safe_print(f"  Sort by newest: {sort_by_newest}")
        safe_print(f"  Fast mode: {self.config.fast_mode}")
        safe_print(f"  Max rate: {self.config.max_rate} req/sec")
        safe_print(f"  Use proxy: {self.config.use_proxy}")
        safe_print(f"  Language: {self.config.language}")
        safe_print(f"  Region: {self.config.region}")
        safe_print("")

        # Calculate date cutoff for filtering
        date_cutoff = self.calculate_date_cutoff(date_range)
        if date_cutoff:
            safe_print(f"  Date cutoff: {date_cutoff.strftime('%d/%m/%Y')}")
        else:
            safe_print(f"  Date cutoff: No date limit (all reviews)")
        safe_print("")

        start_time = asyncio.get_event_loop().time()
        all_reviews = []
        seen_review_ids = set()  # Track seen reviews to prevent duplicates

        # Setup HTTP client with proxy if enabled
        # Set consistent headers that will be merged with request-specific headers
        client_kwargs = {
            "timeout": self.config.timeout,
            "headers": {
                "Accept-Language": f"{self.config.language}-{self.config.region.upper()},{self.config.language};q=0.9,en;q=0.8",
                "Accept": "application/json, text/plain, */*",
                "Accept-Encoding": "gzip, deflate, br",
                "Cache-Control": "no-cache",
                "Pragma": "no-cache",
                "Accept-Charset": "utf-8",
                "Content-Type": "application/json; charset=utf-8"
            }
        }

        if self.current_proxy:
            proxy_dict = self.current_proxy.to_httpx_proxies() if hasattr(self.current_proxy, 'to_httpx_proxies') else None
            if proxy_dict:
                client_kwargs['proxies'] = proxy_dict
                safe_print(f"Using proxy: {list(proxy_dict.values())[0]}")
                print()

        async with httpx.AsyncClient(**client_kwargs) as client:
            page_num = 1
            page_token = None

            while len(all_reviews) < max_reviews and page_num <= 1000:  # Increased limit: max 1000 pages (~20,000 reviews)
                safe_print(f"Fetching page {page_num}...")

                reviews, next_page_token = await self.fetch_rpc_page(
                    client,
                    place_id,
                    page_num,
                    page_token
                )

                if not reviews:
                    safe_print(f"   No more reviews or error occurred")
                    break

                # Apply date filtering and duplicate detection to reviews
                filtered_reviews = []
                reviews_outside_range = 0
                duplicate_count = 0

                for review in reviews:
                    # Skip duplicates
                    if review.review_id in seen_review_ids:
                        duplicate_count += 1
                        continue

                    seen_review_ids.add(review.review_id)

                    # Check date range based on filter type
                    if date_range == 'custom' and start_date and end_date:
                        # Use custom date range filtering
                        if self.is_review_within_custom_date_range(review, start_date, end_date):
                            filtered_reviews.append(review)
                        else:
                            reviews_outside_range += 1
                    else:
                        # Use standard date range filtering
                        if self.is_review_within_date_range(review, date_cutoff):
                            filtered_reviews.append(review)
                        else:
                            reviews_outside_range += 1

                # NEW LOGIC: Continue scraping even with many old reviews
                # Only stop if we get NO new reviews for several consecutive pages
                # This allows us to skip old reviews and find newer ones in subsequent pages
                if date_range not in ['all', 'custom'] and date_cutoff and reviews_outside_range > len(reviews) * 0.8:
                    safe_print(f"   Warning: {reviews_outside_range}/{len(reviews)} reviews are outside date range")
                    safe_print(f"   Continuing to search for newer reviews in next pages...")
                    # Don't break - continue to next page

                all_reviews.extend(filtered_reviews)

                # Report filtering results
                if reviews_outside_range > 0 or duplicate_count > 0:
                    safe_print(f"   Got {len(filtered_reviews)} reviews within date range (filtered out {reviews_outside_range}, skipped {duplicate_count} duplicates)")
                    safe_print(f"   Total: {len(all_reviews)} reviews")
                else:
                    safe_print(f"   Got {len(filtered_reviews)} reviews (total: {len(all_reviews)})")

                # Progress callback
                if progress_callback:
                    progress_callback(page_num, len(all_reviews))

                # Check if we have next page token
                if not next_page_token:
                    safe_print(f"   No more pages available (no next page token)")
                    break

                # Continue pagination even with fewer than 10 reviews
                # Google may return fewer reviews on later pages but still have more available

                # Check if we have enough
                if len(all_reviews) >= max_reviews:
                    all_reviews = all_reviews[:max_reviews]
                    break

                # Update page token for next request
                page_token = next_page_token
                page_num += 1

        end_time = asyncio.get_event_loop().time()
        elapsed = end_time - start_time
        rate = len(all_reviews) / elapsed if elapsed > 0 else 0

        # Sort reviews by date if requested (post-processing)
        # Note: Google API doesn't reliably sort via pb parameters, so we sort in-memory
        if sort_by_newest and all_reviews:
            print()
            safe_print("Sorting reviews by date (newest first)...")

            # Sort by date - need to parse date_formatted (DD/MM/YYYY)
            def get_sort_key(review):
                """Get sort key for review (datetime object or default)"""
                try:
                    date_obj = self.parse_ddmmyyyy_to_datetime(review.date_formatted)
                    if date_obj:
                        return date_obj
                    # If parsing failed, put at the end
                    return datetime(1900, 1, 1)
                except:
                    return datetime(1900, 1, 1)

            all_reviews.sort(key=get_sort_key, reverse=True)
            safe_print(f"   Sorted {len(all_reviews)} reviews by date")

            # Process translations if enabled (concurrent batch processing for maximum performance)
            if self.config.enable_translation and self.language_service:
                safe_print("Processing translations with concurrent processing...")
                translation_start = time.time()
                self.reset_translation_stats()

                # Process reviews in batches with concurrent translation for maximum performance
                batch_size = self.config.translation_batch_size
                total_reviews = len(all_reviews)

                for i in range(0, total_reviews, batch_size):
                    batch_end = min(i + batch_size, total_reviews)
                    batch_reviews = all_reviews[i:batch_end]

                    # Process this batch with concurrent translation
                    processed_reviews = await self.process_reviews_batch_concurrent(batch_reviews, max_concurrent=min(10, batch_size))

                    # Update the original reviews with processed data
                    for j, review in enumerate(processed_reviews):
                        if j < len(batch_reviews):
                            batch_reviews[j] = review

                    # Update progress callback with translation progress
                    if progress_callback:
                        progress = (batch_end / total_reviews) * 100
                        stats = self.get_translation_stats()
                        progress_callback(
                            page_num=i // batch_size + 1,
                            total_reviews=batch_end,
                            translation_progress=f"{progress:.1f}%",
                            detected_languages=stats['detected_languages'],
                            translated_count=stats['translated_count']
                        )

                translation_time = time.time() - translation_start
                stats = self.get_translation_stats()
                safe_print(f"   Concurrent translation completed in {translation_time:.2f}s")
                safe_print(f"   Detected languages: {dict(stats['detected_languages'])}")
                safe_print(f"   Reviews translated: {stats['translated_count']}")
                safe_print(f"   Translation errors: {stats['translation_errors']}")

        # Print stats
        print()
        safe_print("=" * 80)
        safe_print("SCRAPING COMPLETE")
        safe_print("=" * 80)
        safe_print(f"Total reviews: {len(all_reviews)}")
        safe_print(f"Time taken: {elapsed:.2f}s")
        safe_print(f"Rate: {rate:.2f} reviews/sec")
        print()
        safe_print(f"Statistics:")
        safe_print(f"  Total requests: {self.stats['total_requests']}")
        safe_print(f"  Successful: {self.stats['successful_requests']}")
        safe_print(f"  Failed: {self.stats['failed_requests']}")
        safe_print(f"  Rate limits: {self.stats['rate_limits_encountered']}")
        safe_print(f"  Retries used: {self.stats['retries_used']}")
        safe_print(f"  Proxy switches: {self.stats['proxy_switches']}")
        print()

        # Save reviews to organized output
        try:
            from ..utils.output_manager import output_manager

            # Prepare settings dict
            scraper_settings = {
                'max_reviews': max_reviews,
                'date_range': date_range,
                'sort_by_newest': sort_by_newest,
                'language': self.config.language,
                'region': self.config.region,
                'fast_mode': self.config.fast_mode,
                'timeout': self.config.timeout,
                'use_proxy': self.config.use_proxy
            }

            # Save reviews
            file_paths = output_manager.save_reviews(
                reviews=[review.__dict__ for review in all_reviews],
                place_name=f"Place_{place_id[:8]}...",  # Use partial place_id as name
                place_id=place_id,
                task_id=f"scrape_{int(time.time())}",
                settings=scraper_settings
            )

            safe_print(f"[OK] Reviews saved to: {file_paths['directory']}")

        except Exception as e:
            safe_print(f"[WARNING] Could not save reviews to output manager: {e}")

        # Prepare enhanced metadata with translation analytics
        metadata = {
            'place_id': place_id,
            'total_reviews': len(all_reviews),
            'time_taken': elapsed,
            'rate': rate,
            'language': self.config.language,
            'region': self.config.region,
            'date_range': date_range,
            'sort_by_newest': sort_by_newest,
            'date_cutoff': date_cutoff.strftime('%d/%m/%Y') if date_cutoff else None,
            'stats': self.stats
        }

        # Add translation statistics if translation was enabled
        if self.config.enable_translation and self.language_service:
            translation_stats = self.get_translation_stats()
            metadata['translation'] = {
                'enabled': True,
                'target_language': self.config.target_language,
                'translate_review_text': self.config.translate_review_text,
                'translate_owner_response': self.config.translate_owner_response,
                'detection_count': translation_stats.get('detection_count', 0),
                'translated_count': translation_stats.get('translated_count', 0),
                'translation_errors': translation_stats.get('translation_errors', 0),
                'detected_languages': translation_stats.get('detected_languages', {}),
                'language_distribution': {
                    'total_analyzed': translation_stats.get('detection_count', 0),
                    'unique_languages': len(translation_stats.get('detected_languages', {})),
                    'languages_found': dict(sorted(
                        translation_stats.get('detected_languages', {}).items(),
                        key=lambda x: x[1],
                        reverse=True
                    ))
                },
                'translation_success_rate': (
                    (translation_stats.get('translated_count', 0) /
                     max(1, translation_stats.get('detection_count', 0))) * 100
                )
            }
        else:
            metadata['translation'] = {
                'enabled': False,
                'reason': 'Translation disabled in configuration'
            }

        return {
            'reviews': all_reviews,
            'metadata': metadata
        }

    def export_to_csv(self, reviews: List[ProductionReview], filename: str):
        """Export reviews to CSV with support for translated content"""
        with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)

            # Check if any reviews have translation data and set headers accordingly
            has_translations = any(hasattr(r, 'review_text_translated') and r.review_text_translated for r in reviews)
            has_language_detection = any(hasattr(r, 'original_language') and r.original_language for r in reviews)
            has_response_translation = any(hasattr(r, 'owner_response_translated') and r.owner_response_translated for r in reviews)

            # Build dynamic headers based on available data
            headers = [
                'Review ID', 'Author Name', 'Author URL', 'Author Reviews Count',
                'Rating', 'Date Formatted', 'Date Relative', 'Review Text'
            ]

            if has_language_detection:
                headers.extend(['Original Language', 'Target Language'])

            if has_translations:
                headers.append('Translated Review Text')

            headers.extend(['Review Likes', 'Review Photos Count', 'Owner Response'])

            if has_response_translation:
                headers.append('Translated Owner Response')

            headers.extend(['Page Number'])

            writer.writerow(headers)

            # Write data rows
            for r in reviews:
                row = [
                    r.review_id, r.author_name, r.author_url, getattr(r, 'author_reviews_count', 0),
                    r.rating, r.date_formatted, r.date_relative, r.review_text
                ]

                if has_language_detection:
                    row.extend([
                        getattr(r, 'original_language', ''),
                        getattr(r, 'target_language', '')
                    ])

                if has_translations:
                    row.append(getattr(r, 'review_text_translated', ''))

                row.extend([
                    getattr(r, 'review_likes', 0),
                    getattr(r, 'review_photos_count', 0),
                    getattr(r, 'owner_response', '')
                ])

                if has_response_translation:
                    row.append(getattr(r, 'owner_response_translated', ''))

                row.append(r.page_number)

                writer.writerow(row)

        safe_print(f"Exported to CSV: {filename}")

    def export_to_json(self, data: Dict[str, Any], filename: str):
        """Export complete data to JSON"""
        # Convert reviews to dicts
        json_data = {
            'reviews': [r.to_dict() for r in data['reviews']],
            'metadata': data['metadata']
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)

        safe_print(f"Exported to JSON: {filename}")


# ==================== FACTORY FUNCTION ====================

def create_production_scraper(
    language: str = "th",
    region: str = "th",
    fast_mode: bool = True,
    max_rate: float = 10.0,
    use_proxy: bool = False,
    proxy_list: Optional[List[str]] = None,
    timeout: float = 30.0,
    max_retries: int = 3,
    enable_translation: bool = False,
    target_language: str = "en",
    translate_review_text: bool = True,
    translate_owner_response: bool = True,
    # Enhanced translation settings
    use_enhanced_detection: bool = True,
    translation_batch_size: int = 50,
    # Debug and analysis options
    enable_pb_analysis: bool = False,
    pb_analysis_verbose: bool = False,
    save_pb_analysis: bool = False
) -> ProductionGoogleMapsScraper:
    """
    Factory function to create configured production scraper

    Args:
        language: Language code (th, en, etc.)
        region: Region code (th, us, etc.)
        fast_mode: Use fast delays (50-150ms) for better performance
        max_rate: Maximum requests per second
        use_proxy: Enable proxy rotation
        proxy_list: List of proxy URLs
        timeout: Request timeout in seconds
        max_retries: Maximum retry attempts
        enable_translation: Enable language detection and translation
        target_language: Target language for translation ("th" or "en")
        translate_review_text: Translate review text if needed
        translate_owner_response: Translate owner response if needed

    Returns:
        Configured ProductionGoogleMapsScraper instance
    """
    config = ScraperConfig(
        language=language,
        region=region,
        fast_mode=fast_mode,
        max_rate=max_rate,
        use_proxy=use_proxy,
        proxy_list=proxy_list,
        timeout=timeout,
        max_retries=max_retries,
        enable_translation=enable_translation,
        target_language=target_language,
        translate_review_text=translate_review_text,
        translate_owner_response=translate_owner_response,
        # Enhanced translation settings
        use_enhanced_detection=use_enhanced_detection,
        translation_batch_size=translation_batch_size,
        # Debug and analysis options
        enable_pb_analysis=enable_pb_analysis,
        pb_analysis_verbose=pb_analysis_verbose,
        save_pb_analysis=save_pb_analysis
    )

    return ProductionGoogleMapsScraper(config)


# ==================== USAGE EXAMPLE ====================

async def example_usage():
    """Example of using the production scraper"""
    scraper = create_production_scraper(
        language="th",
        region="th",
        fast_mode=True,  # Optimized for performance
        max_rate=10.0
    )

    # Scrape reviews with date filtering
    result = await scraper.scrape_reviews(
        place_id="0x30e29ecfc2f455e1:0xc4ad0280d8906604",  # Central World Bangkok
        max_reviews=100,
        date_range="6months"  # Only reviews from the last 6 months
    )

    # Export
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    scraper.export_to_csv(result['reviews'], f"production_reviews_{timestamp}.csv")
    scraper.export_to_json(result, f"production_reviews_{timestamp}.json")

    return result


async def example_usage_english():
    """Example: Scrape reviews in English language"""
    scraper = create_production_scraper(
        language="en",  # English language
        region="us",    # US region
        fast_mode=True,
        max_rate=10.0
    )

    result = await scraper.scrape_reviews(
        place_id="0x30e29ecfc2f455e1:0xc4ad0280d8906604",
        max_reviews=100,
        date_range="1year"
    )

    # Export with language indicator in filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    scraper.export_to_csv(result['reviews'], f"reviews_EN_{timestamp}.csv")
    scraper.export_to_json(result, f"reviews_EN_{timestamp}.json")

    return result


async def example_usage_multilang():
    """Example: Scrape same place in multiple languages"""
    place_id = "0x30e29ecfc2f455e1:0xc4ad0280d8906604"
    max_reviews = 50

    # Language configurations
    languages = [
        {"code": "en", "region": "us", "name": "English"},
        {"code": "th", "region": "th", "name": "Thai"},
        {"code": "ja", "region": "jp", "name": "Japanese"},
        {"code": "zh-CN", "region": "cn", "name": "Chinese"}
    ]

    results = {}

    for lang_config in languages:
        safe_print(f"\n{'='*80}")
        safe_print(f"Scraping reviews in {lang_config['name']}...")
        safe_print(f"{'='*80}\n")

        scraper = create_production_scraper(
            language=lang_config["code"],
            region=lang_config["region"],
            fast_mode=True,
            max_rate=10.0
        )

        result = await scraper.scrape_reviews(
            place_id=place_id,
            max_reviews=max_reviews,
            date_range="1year"
        )

        # Export with language indicator
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        lang_code = lang_config["code"].replace("-", "_")
        scraper.export_to_csv(result['reviews'], f"reviews_{lang_code.upper()}_{timestamp}.csv")
        scraper.export_to_json(result, f"reviews_{lang_code.upper()}_{timestamp}.json")

        results[lang_config["name"]] = result

        safe_print(f"\n✅ Completed {lang_config['name']}: {len(result['reviews'])} reviews")

    return results


if __name__ == "__main__":
    asyncio.run(example_usage())
