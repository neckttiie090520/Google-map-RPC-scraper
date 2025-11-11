#!/usr/bin/env python3
"""
Google Maps Scraper - Enhanced Bulk Translation Module
========================================================

This module provides high-performance bulk translation using py-googletrans
with advanced concurrent processing capabilities.

Features:
- Bulk translation with Google Translate API (free)
- Concurrent processing for maximum speed
- Automatic retry logic with exponential backoff
- Support for Chinese language variants
- Session pooling for connection reuse
- Rate limiting protection
- Performance monitoring and statistics
"""

import asyncio
import time
import logging
from typing import List, Dict, Any, Optional, Tuple, AsyncGenerator
from dataclasses import dataclass, field
from datetime import datetime
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from collections import defaultdict
import sys
import os

# Add the parent directory to the path to import the scraper
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

try:
    from googletrans import Translator, LANGUAGES
    GOOGLETRANS_AVAILABLE = True
except ImportError:
    print("Warning: googletrans not available. Install with: pip install googletrans==4.0.0rc1")
    GOOGLETRANS_AVAILABLE = False
    # Create dummy class for type hints
    class Translator:
        pass

from src.scraper.production_scraper import ProductionReview
from .enhanced_language_detector import create_enhanced_detector

@dataclass
class BulkTranslationStats:
    """Statistics for bulk translation processing"""
    total_texts: int = 0
    translated_texts: int = 0
    failed_texts: int = 0
    languages_detected: Dict[str, int] = field(default_factory=dict)
    processing_time: float = 0.0
    batches_processed: int = 0
    concurrent_workers: int = 1
    rate_limit_hits: int = 0
    retry_count: int = 0
    chars_translated: int = 0
    translation_speed: float = 0.0  # texts per second

class EnhancedBulkTranslator:
    """High-performance bulk translator with py-googletrans"""

    def __init__(self,
                 target_language: str = 'th',
                 batch_size: int = 50,
                 max_workers: int = 5,
                 timeout: float = 10.0,
                 max_retries: int = 3,
                 session_pool_size: int = 10):
        """
        Initialize enhanced bulk translator

        Args:
            target_language: Target language code (default: 'th')
            batch_size: Number of texts to process in each batch
            max_workers: Maximum concurrent translation workers
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts per text
            session_pool_size: Number of translator sessions to pool
        """
        if not GOOGLETRANS_AVAILABLE:
            raise ImportError("py-googletrans is required. Install with: pip install py-googletrans>=4.0.0rc1")

        self.target_language = target_language
        self.batch_size = batch_size
        self.max_workers = max_workers
        self.timeout = timeout
        self.max_retries = max_retries
        self.session_pool_size = session_pool_size

        self.stats = BulkTranslationStats(concurrent_workers=max_workers)
        self.logger = logging.getLogger(__name__)

        # Initialize enhanced language detector
        try:
            self.enhanced_detector = create_enhanced_detector()
            self.logger.info("Enhanced language detector initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize enhanced detector: {e}")
            self.enhanced_detector = None

        # Create translator session pool
        self._init_translator_pool()

        # Rate limiting protection
        self._rate_limit_lock = threading.Lock()
        self._request_times = []
        self._max_requests_per_second = 10

    def _init_translator_pool(self):
        """Initialize pool of translator instances for concurrent use"""
        self.translator_pool = []
        for i in range(self.session_pool_size):
            try:
                # Create translator with basic configuration
                translator = Translator(timeout=self.timeout)
                self.translator_pool.append(translator)
            except Exception as e:
                self.logger.warning(f"Failed to create translator session {i}: {e}")

        if not self.translator_pool:
            raise RuntimeError("Failed to create any translator sessions")

        self.logger.info(f"Created {len(self.translator_pool)} translator sessions")

    def _get_translator(self) -> Translator:
        """Get a translator instance from the pool"""
        import random
        return random.choice(self.translator_pool)

    def _check_rate_limit(self):
        """Check and enforce rate limiting"""
        with self._rate_limit_lock:
            current_time = time.time()

            # Remove old requests (older than 1 second)
            self._request_times = [t for t in self._request_times if current_time - t < 1.0]

            # Check if we're at the rate limit
            if len(self._request_times) >= self._max_requests_per_second:
                sleep_time = 1.0 - (current_time - self._request_times[0])
                if sleep_time > 0:
                    self.logger.debug(f"Rate limit hit, sleeping {sleep_time:.2f}s")
                    self.stats.rate_limit_hits += 1
                    time.sleep(sleep_time)

            # Add current request time
            self._request_times.append(current_time)

    def detect_language(self, text: str) -> str:
        """
        Detect language of given text with enhanced Chinese variant support

        Args:
            text: Text to detect language for

        Returns:
            Language code with variant support (e.g., 'zh-cn', 'zh-tw', 'ja', 'th', 'en')
        """
        if not text or not text.strip():
            return 'unknown'

        try:
            # Use enhanced detector if available
            if self.enhanced_detector:
                return self.enhanced_detector.detect_language_enhanced(text)
            else:
                # Fallback to googletrans language detection
                translator = self._get_translator()
                detected = translator.detect(text)
                return detected.lang

        except Exception as e:
            self.logger.debug(f"Language detection failed for text: {text[:50]}... - {e}")
            return 'unknown'

    def is_translation_needed(self, text: str, detected_language: str) -> bool:
        """
        Check if translation is needed for the given text with Chinese variant support

        Args:
            text: Text to check
            detected_language: Detected language code (with variants, e.g., 'zh-cn', 'zh-tw')

        Returns:
            True if translation is needed, False otherwise
        """
        if not text or not text.strip():
            return False

        if detected_language == 'unknown':
            return False

        # Handle Chinese variants
        if detected_language.startswith('zh-'):
            # Any Chinese variant needs translation if target is not Chinese
            if not self.target_language.startswith('zh'):
                return True
            # If target is Chinese, check if variants differ
            return True

        # Handle generic Chinese code
        if detected_language == 'zh':
            if self.target_language.startswith('zh') or self.target_language == 'zh':
                return False
            return True

        # Handle target Chinese variants
        if self.target_language.startswith('zh-') or self.target_language == 'zh':
            if detected_language.startswith('zh-') or detected_language == 'zh':
                return False

        # Standard language comparison
        if detected_language == self.target_language:
            return False

        return True

    def _translate_single_text(self, text: str, source_lang: str = 'auto') -> Tuple[str, bool]:
        """
        Translate a single text with retry logic

        Args:
            text: Text to translate
            source_lang: Source language code (default: auto-detect)

        Returns:
            Tuple of (translated_text, success)
        """
        if not text or not text.strip():
            return text, True

        for attempt in range(self.max_retries + 1):
            try:
                # Check rate limit before request
                self._check_rate_limit()

                translator = self._get_translator()

                # Use bulk translate even for single text for consistency
                result = translator.translate(
                    [text],
                    src=source_lang,
                    dest=self.target_language
                )

                # Handle googletrans response properly
                if result:
                    # googletrans sometimes returns a float (error code) instead of translation object
                    if isinstance(result, (int, float)):
                        raise Exception(f"Translation API returned error code: {result}")

                    # Handle list response
                    if isinstance(result, list) and len(result) > 0:
                        translation_obj = result[0]

                        # Check if translation object has expected attributes
                        if hasattr(translation_obj, 'text'):
                            translated_text = translation_obj.text
                            self.stats.chars_translated += len(text)
                            return translated_text, True
                        elif isinstance(translation_obj, str):
                            # Sometimes the translation is returned as a string directly
                            translated_text = translation_obj
                            self.stats.chars_translated += len(text)
                            return translated_text, True
                        else:
                            raise Exception(f"Translation object has unexpected type: {type(translation_obj)}")
                    else:
                        raise Exception("Empty or invalid translation result")
                else:
                    raise Exception("Empty translation result")

            except Exception as e:
                error_msg = str(e).lower()

                if attempt < self.max_retries:
                    # Exponential backoff for retries
                    backoff_time = (2 ** attempt) * 0.5
                    self.logger.warning(f"Translation attempt {attempt + 1} failed, retrying in {backoff_time}s: {e}")

                    # Additional delay for rate limiting errors
                    if any(keyword in error_msg for keyword in ['rate limit', 'too many requests', '429']):
                        backoff_time *= 2
                        self.stats.rate_limit_hits += 1

                    self.stats.retry_count += 1
                    time.sleep(backoff_time)
                else:
                    self.logger.error(f"Translation failed after {self.max_retries + 1} attempts: {e}")
                    return text, False

        return text, False

    def translate_bulk(self, texts: List[str], source_lang: str = 'auto') -> List[str]:
        """
        Translate multiple texts in bulk using concurrent processing

        Args:
            texts: List of texts to translate
            source_lang: Source language code (default: auto-detect)

        Returns:
            List of translated texts (same order as input)
        """
        if not texts:
            return []

        start_time = time.time()
        self.stats.total_texts += len(texts)

        # Filter out empty texts
        valid_texts = [(i, text) for i, text in enumerate(texts) if text and text.strip()]

        if not valid_texts:
            return texts

        # Prepare results list
        results = [''] * len(texts)

        # Process in batches for better memory management
        for batch_start in range(0, len(valid_texts), self.batch_size):
            batch_end = min(batch_start + self.batch_size, len(valid_texts))
            batch_items = valid_texts[batch_start:batch_end]

            self.logger.debug(f"Processing batch {batch_start//self.batch_size + 1}: {len(batch_items)} texts")

            # Process batch concurrently
            with ThreadPoolExecutor(max_workers=min(self.max_workers, len(batch_items))) as executor:
                # Submit translation tasks
                future_to_index = {
                    executor.submit(self._translate_single_text, text, source_lang): original_index
                    for original_index, text in batch_items
                }

                # Collect results
                batch_translated = 0
                batch_failed = 0

                for future in as_completed(future_to_index):
                    original_index = future_to_index[future]
                    try:
                        translated_text, success = future.result()
                        results[original_index] = translated_text

                        if success:
                            batch_translated += 1
                        else:
                            batch_failed += 1

                    except Exception as e:
                        self.logger.error(f"Future failed for text {original_index}: {e}")
                        results[original_index] = texts[original_index]  # Keep original
                        batch_failed += 1

                self.stats.translated_texts += batch_translated
                self.stats.failed_texts += batch_failed
                self.stats.batches_processed += 1

                # Small delay between batches to avoid overwhelming the service
                if batch_end < len(valid_texts):
                    time.sleep(0.1)

        # Update statistics
        processing_time = time.time() - start_time
        self.stats.processing_time += processing_time

        if processing_time > 0:
            self.stats.translation_speed = len(valid_texts) / processing_time

        self.logger.info(f"Bulk translation completed: {len(valid_texts)} texts in {processing_time:.2f}s "
                        f"({self.stats.translation_speed:.1f} texts/s)")

        return results

    def process_review_batch(self,
                           reviews: List[ProductionReview],
                           translate_review_text: bool = True,
                           translate_owner_response: bool = False) -> List[ProductionReview]:
        """
        Process a batch of reviews with bulk translation

        Args:
            reviews: List of reviews to process
            translate_review_text: Whether to translate review text
            translate_owner_response: Whether to translate owner response

        Returns:
            List of processed reviews with translations
        """
        if not reviews:
            return reviews

        start_time = time.time()

        # Collect texts for translation
        review_texts_to_translate = []
        owner_responses_to_translate = []
        review_indices = []

        for i, review in enumerate(reviews):
            # Detect languages
            review_language = 'unknown'
            owner_response_language = 'unknown'

            if review.review_text and translate_review_text:
                review_language = self.detect_language(review.review_text)
                if self.is_translation_needed(review.review_text, review_language):
                    review_texts_to_translate.append(review.review_text)
                    review_indices.append(i)
                    self.stats.languages_detected[review_language] = self.stats.languages_detected.get(review_language, 0) + 1

            if review.owner_response and translate_owner_response:
                owner_response_language = self.detect_language(review.owner_response)
                if self.is_translation_needed(review.owner_response, owner_response_language):
                    owner_responses_to_translate.append(review.owner_response)

        # Perform bulk translations
        translated_review_texts = []
        translated_owner_responses = []

        if review_texts_to_translate:
            self.logger.info(f"Translating {len(review_texts_to_translate)} review texts...")
            translated_review_texts = self.translate_bulk(review_texts_to_translate)

        if owner_responses_to_translate:
            self.logger.info(f"Translating {len(owner_responses_to_translate)} owner responses...")
            translated_owner_responses = self.translate_bulk(owner_responses_to_translate)

        # Update reviews with translations
        review_text_idx = 0
        owner_response_idx = 0

        for i, review in enumerate(reviews):
            # Update review text translation
            if review.review_text and translate_review_text and i in review_indices:
                if review_text_idx < len(translated_review_texts):
                    translated_text = translated_review_texts[review_text_idx]
                    if translated_text != review.review_text:
                        review.review_text_translated = translated_text
                        # Detect language for storage
                        review.review_text_language = self.detect_language(review.review_text)
                    review_text_idx += 1

            # Update owner response translation
            if review.owner_response and translate_owner_response:
                if owner_response_idx < len(translated_owner_responses):
                    translated_response = translated_owner_responses[owner_response_idx]
                    if translated_response != review.owner_response:
                        review.owner_response_translated = translated_response
                        # Detect language for storage
                        review.owner_response_language = self.detect_language(review.owner_response)
                    owner_response_idx += 1

        processing_time = time.time() - start_time
        self.logger.info(f"Review batch processing completed in {processing_time:.2f}s")

        return reviews

    def get_supported_languages(self) -> Dict[str, str]:
        """Get dictionary of supported languages"""
        if GOOGLETRANS_AVAILABLE:
            return LANGUAGES
        return {}

    def get_language_name(self, lang_code: str) -> str:
        """
        Get human-readable language name in Thai

        Args:
            lang_code: Language code (e.g., 'en', 'zh-cn', 'th')

        Returns:
            Language name in Thai
        """
        if self.enhanced_detector:
            return self.enhanced_detector.get_language_name(lang_code)

        # Fallback to googletrans language names
        languages = self.get_supported_languages()
        if lang_code in languages:
            return languages[lang_code].title()

        # Thai language names for common codes
        thai_names = {
            'en': 'อังกฤษ',
            'th': 'ไทย',
            'zh': 'จีน',
            'zh-cn': 'จีนตัวย่อ',
            'zh-tw': 'จีนตัวเต็ม',
            'zh-hk': 'จีนฮ่องกง',
            'ja': 'ญี่ปุ่น',
            'ko': 'เกาหลี',
            'vi': 'เวียดนาม',
            'id': 'อินโดนีเซีย',
            'ms': 'มาเลย์',
            'unknown': 'ไม่ทราบ'
        }

        return thai_names.get(lang_code, lang_code.upper())

    def get_stats(self) -> BulkTranslationStats:
        """Get current translation statistics"""
        return self.stats

    def reset_stats(self):
        """Reset translation statistics"""
        self.stats = BulkTranslationStats(concurrent_workers=self.max_workers)

# Factory function for easy creation
def create_bulk_translator(target_language: str = 'th',
                          batch_size: int = 50,
                          max_workers: int = 5,
                          **kwargs) -> EnhancedBulkTranslator:
    """
    Factory function to create enhanced bulk translator

    Args:
        target_language: Target language code
        batch_size: Number of texts per batch
        max_workers: Maximum concurrent workers
        **kwargs: Additional arguments for EnhancedBulkTranslator

    Returns:
        EnhancedBulkTranslator instance
    """
    return EnhancedBulkTranslator(
        target_language=target_language,
        batch_size=batch_size,
        max_workers=max_workers,
        **kwargs
    )

# Convenience function for bulk translation
def bulk_translate_reviews(reviews: List[ProductionReview],
                          target_language: str = 'th',
                          translate_review_text: bool = True,
                          translate_owner_response: bool = False,
                          batch_size: int = 50,
                          max_workers: int = 5,
                          progress_callback=None) -> Tuple[List[ProductionReview], BulkTranslationStats]:
    """
    Convenience function for bulk translation of reviews

    Args:
        reviews: List of reviews to translate
        target_language: Target language code
        translate_review_text: Whether to translate review text
        translate_owner_response: Whether to translate owner response
        batch_size: Number of reviews per batch
        max_workers: Maximum concurrent workers
        progress_callback: Optional callback function

    Returns:
        Tuple of (translated_reviews, translation_stats)
    """
    translator = create_bulk_translator(
        target_language=target_language,
        batch_size=batch_size,
        max_workers=max_workers
    )

    # Process reviews
    translated_reviews = translator.process_review_batch(
        reviews=reviews,
        translate_review_text=translate_review_text,
        translate_owner_response=translate_owner_response
    )

    # Call progress callback if provided
    if progress_callback:
        stats = translator.get_stats()
        progress_callback(len(translated_reviews), len(reviews), stats.languages_detected)

    return translated_reviews, translator.get_stats()

# Test function
if __name__ == "__main__":
    print("🧪 Testing Enhanced Bulk Translator")
    print("=" * 50)

    if not GOOGLETRANS_AVAILABLE:
        print("❌ py-googletrans not available. Install with:")
        print("   pip install py-googletrans>=4.0.0rc1")
        exit(1)

    # Test bulk translation
    test_texts = [
        "This is a great place!",
        "这是一个很好的地方！",
        "這是一個很好的地方！",
        "この場所は素晴らしいです！",
        "이 장소는 훌륭합니다!",
        "สถานที่นี้ดีมากครับ"
    ]

    print(f"Testing bulk translation of {len(test_texts)} texts...")

    try:
        translator = create_bulk_translator(
            target_language='th',
            batch_size=3,
            max_workers=2
        )

        # Test language detection
        print("\n📝 Language Detection Test:")
        for text in test_texts:
            lang = translator.detect_language(text)
            lang_name = translator.get_language_name(lang)
            needs_translation = translator.is_translation_needed(text, lang)
            print(f"  {lang_name} | {'🔄' if needs_translation else '✅'} | {text[:30]}...")

        # Test bulk translation
        print(f"\n🚀 Bulk Translation Test (→ Thai):")
        start_time = time.time()
        translated_texts = translator.translate_bulk(test_texts)
        end_time = time.time()

        for original, translated in zip(test_texts, translated_texts):
            print(f"  Original:  {original}")
            print(f"  Translated: {translated}")
            print()

        stats = translator.get_stats()
        print(f"📊 Performance Statistics:")
        print(f"  Total texts: {stats.total_texts}")
        print(f"  Translated: {stats.translated_texts}")
        print(f"  Failed: {stats.failed_texts}")
        print(f"  Processing time: {stats.processing_time:.2f}s")
        print(f"  Translation speed: {stats.translation_speed:.1f} texts/s")
        print(f"  Rate limit hits: {stats.rate_limit_hits}")
        print(f"  Retry count: {stats.retry_count}")
        print(f"  Characters translated: {stats.chars_translated}")

        print("\n✅ Bulk translation test completed successfully!")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()