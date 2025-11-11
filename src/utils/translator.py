#!/usr/bin/env python3
"""
Google Maps Scraper - Batch Translation Processing Module
========================================================

This module handles Phase 2 of the two-stage scraping process:
Batch translation processing after RPC data collection is complete.

Features:
- Language detection for review filtering
- Batch translation processing
- Progress tracking and reporting
- Support for review text and owner response translation
- Enhanced language detection settings
"""

import asyncio
from typing import List, Dict, Any, Optional, Tuple, Callable
import logging
from dataclasses import dataclass, field
from datetime import datetime
import json
import time
import sys
import os

# Add the parent directory to the path to import the scraper
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.scraper.production_scraper import ProductionReview
from langdetect import detect, DetectorFactory
from deep_translator import GoogleTranslator
from .enhanced_language_detector import create_enhanced_detector

# Import bulk translator for enhanced performance
try:
    from .bulk_translator import EnhancedBulkTranslator, create_bulk_translator
    BULK_TRANSLATOR_AVAILABLE = True
except ImportError:
    print("Warning: Enhanced bulk translator not available. Using standard translator.")
    BULK_TRANSLATOR_AVAILABLE = False

# Set seed for consistent language detection
DetectorFactory.seed = 0

@dataclass
class TranslationStats:
    """Statistics for batch translation processing"""
    total_reviews: int = 0
    reviews_needing_translation: int = 0
    reviews_translated: int = 0
    languages_detected: Dict[str, int] = field(default_factory=dict)
    translation_errors: int = 0
    processing_time: float = 0.0
    batch_count: int = 0
    target_language: str = 'th'

class BatchTranslator:
    """Handles batch translation of collected reviews with enhanced language detection"""

    def __init__(self, target_language: str = 'th', batch_size: int = 50, use_bulk_translator: bool = True, max_workers: int = 5):
        """
        Initialize batch translator

        Args:
            target_language: Target language code (default: 'th' for Thai)
            batch_size: Number of reviews to process in each batch
            use_bulk_translator: Whether to use enhanced bulk translator (default: True)
            max_workers: Maximum concurrent workers for bulk translation
        """
        self.target_language = target_language
        self.batch_size = batch_size
        self.use_bulk_translator = use_bulk_translator and BULK_TRANSLATOR_AVAILABLE
        self.max_workers = max_workers
        self.stats = TranslationStats(target_language=target_language)
        self.logger = logging.getLogger(__name__)

        # Initialize enhanced language detector
        try:
            self.enhanced_detector = create_enhanced_detector()
            self.logger.info("Enhanced language detector initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize enhanced detector: {e}")
            self.enhanced_detector = None

        # Initialize translator based on availability and preference
        if self.use_bulk_translator:
            try:
                self.bulk_translator = create_bulk_translator(
                    target_language=target_language,
                    batch_size=batch_size,
                    max_workers=max_workers
                )
                self.translator = None  # Not needed when using bulk translator
                self.logger.info(f"Enhanced bulk translator initialized (workers: {max_workers})")
            except Exception as e:
                self.logger.error(f"Failed to initialize bulk translator: {e}")
                self.use_bulk_translator = False
                self.bulk_translator = None
                self._init_standard_translator()
        else:
            self.bulk_translator = None
            self._init_standard_translator()

    def _init_standard_translator(self):
        """Initialize standard GoogleTranslator as fallback"""
        try:
            self.translator = GoogleTranslator(source='auto', target=self.target_language)
            self.logger.info("Standard translator initialized as fallback")
        except Exception as e:
            self.logger.error(f"Failed to initialize standard translator: {e}")
            self.translator = None

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
                # Fallback to standard detection
                clean_text = text.strip()[:500]  # Use first 500 chars for detection

                # Skip if too short
                if len(clean_text) < 10:
                    return 'unknown'

                detected = detect(clean_text)
                return detected

        except Exception as e:
            self.logger.debug(f"Enhanced language detection failed for text: {text[:50]}... - {e}")
            # Fallback to basic detection
            try:
                clean_text = text.strip()[:500]
                if len(clean_text) >= 10:
                    return detect(clean_text)
            except:
                pass
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
            # For simplicity, we'll translate between different Chinese variants
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

    def translate_text(self, text: str) -> str:
        """
        Translate text to target language

        Args:
            text: Text to translate

        Returns:
            Translated text or original text if translation fails
        """
        if not text or not text.strip():
            return text

        # Use bulk translator if available (more efficient)
        if self.use_bulk_translator and self.bulk_translator:
            try:
                translated_text, success = self.bulk_translator._translate_single_text(text)
                return translated_text if success else text
            except Exception as e:
                self.logger.error(f"Bulk translation failed for text: {text[:100]}... - {e}")
                return text

        # Fallback to standard translator
        if not self.translator:
            self.logger.warning("Translator not initialized, returning original text")
            return text

        try:
            # Split long text into chunks if needed (Google has limits)
            max_length = 4500  # Leave room for safety
            if len(text) <= max_length:
                translated = self.translator.translate(text)
                return translated
            else:
                # For long texts, translate in chunks and combine
                chunks = self._split_text(text, max_length)
                translated_chunks = []
                for chunk in chunks:
                    translated_chunk = self.translator.translate(chunk)
                    translated_chunks.append(translated_chunk)
                return ' '.join(translated_chunks)

        except Exception as e:
            self.logger.error(f"Translation failed for text: {text[:100]}... - {e}")
            return text

    def _split_text(self, text: str, max_length: int) -> List[str]:
        """
        Split long text into chunks for translation

        Args:
            text: Text to split
            max_length: Maximum length per chunk

        Returns:
            List of text chunks
        """
        if len(text) <= max_length:
            return [text]

        chunks = []
        current_chunk = ""

        # Split by sentences to maintain context
        sentences = text.split('. ')
        for sentence in sentences:
            # Add period back if it's not the last sentence
            if sentence != sentences[-1]:
                sentence += '. '

            if len(current_chunk + sentence) <= max_length:
                current_chunk += sentence
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    def process_review(self, review: ProductionReview,
                      translate_review_text: bool = True,
                      translate_owner_response: bool = False) -> ProductionReview:
        """
        Process a single review for language detection and translation

        Args:
            review: Review to process
            translate_review_text: Whether to translate review text
            translate_owner_response: Whether to translate owner response

        Returns:
            Review with added translation information
        """
        self.stats.total_reviews += 1

        # Detect languages
        review_language = 'unknown'
        owner_response_language = 'unknown'

        if review.review_text:
            review_language = self.detect_language(review.review_text)
            self.stats.languages_detected[review_language] = self.stats.languages_detected.get(review_language, 0) + 1

        if review.owner_response:
            owner_response_language = self.detect_language(review.owner_response)
            # Count owner response language separately if needed
            # self.stats.languages_detected[f'owner_{owner_response_language}'] = self.stats.languages_detected.get(f'owner_{owner_response_language}', 0) + 1

        # Check if translation is needed
        review_needs_translation = (translate_review_text and
                                   self.is_translation_needed(review.review_text, review_language))
        owner_response_needs_translation = (translate_owner_response and
                                           self.is_translation_needed(review.owner_response, owner_response_language))

        if review_needs_translation or owner_response_needs_translation:
            self.stats.reviews_needing_translation += 1

        # Perform translations
        if review_needs_translation:
            try:
                translated_text = self.translate_text(review.review_text)
                if translated_text != review.review_text:
                    review.review_text_translated = translated_text
                    review.review_text_language = review_language
                    self.stats.reviews_translated += 1
            except Exception as e:
                self.logger.error(f"Failed to translate review {review.review_id}: {e}")
                self.stats.translation_errors += 1

        if owner_response_needs_translation:
            try:
                translated_response = self.translate_text(review.owner_response)
                if translated_response != review.owner_response:
                    review.owner_response_translated = translated_response
                    review.owner_response_language = owner_response_language
                    self.stats.reviews_translated += 1
            except Exception as e:
                self.logger.error(f"Failed to translate owner response for review {review.review_id}: {e}")
                self.stats.translation_errors += 1

        return review

    def process_batch(self, reviews: List[ProductionReview],
                     translate_review_text: bool = True,
                     translate_owner_response: bool = False,
                     progress_callback: Optional[Callable] = None) -> List[ProductionReview]:
        """
        Process a batch of reviews with bulk translation for maximum performance

        Args:
            reviews: List of reviews to process
            translate_review_text: Whether to translate review text
            translate_owner_response: Whether to translate owner response
            progress_callback: Optional progress callback

        Returns:
            List of processed reviews
        """
        start_time = time.time()

        # Use bulk translator for much better performance
        if self.use_bulk_translator and self.bulk_translator:
            try:
                self.logger.info(f"Processing batch of {len(reviews)} reviews with bulk translator...")

                # Process the entire batch with bulk translation
                processed_reviews = self.bulk_translator.process_review_batch(
                    reviews=reviews,
                    translate_review_text=translate_review_text,
                    translate_owner_response=translate_owner_response
                )

                # Update statistics from bulk translator
                bulk_stats = self.bulk_translator.get_stats()
                self.stats.total_reviews += len(reviews)
                self.stats.languages_detected.update(bulk_stats.languages_detected)
                self.stats.reviews_translated += bulk_stats.translated_texts
                self.stats.translation_errors += bulk_stats.failed_texts
                self.stats.batch_count += 1

                processing_time = time.time() - start_time
                self.stats.processing_time += processing_time

                # Calculate translation rate for this batch
                if processing_time > 0 and len(reviews) > 0:
                    batch_rate = len(reviews) / processing_time
                    self.logger.info(f"Batch processed: {len(reviews)} reviews in {processing_time:.2f}s "
                                   f"({batch_rate:.1f} reviews/s)")

                # Call progress callback if provided
                if progress_callback:
                    progress_callback(len(reviews), len(reviews), self.stats.languages_detected)

                return processed_reviews

            except Exception as e:
                self.logger.error(f"Bulk translation failed, falling back to individual processing: {e}")
                # Fall back to individual processing

        # Fallback to individual processing (original method)
        processed_reviews = []
        for i, review in enumerate(reviews):
            try:
                processed_review = self.process_review(
                    review, translate_review_text, translate_owner_response
                )
                processed_reviews.append(processed_review)

                # Call progress callback if provided
                if progress_callback:
                    progress_callback(i + 1, len(reviews), self.stats.languages_detected)

            except Exception as e:
                self.logger.error(f"Failed to process review {review.review_id}: {e}")
                self.stats.translation_errors += 1
                processed_reviews.append(review)  # Keep original review

        self.stats.batch_count += 1
        processing_time = time.time() - start_time
        self.stats.processing_time += processing_time

        return processed_reviews

    def process_all_reviews(self,
                          reviews: List[ProductionReview],
                          translate_review_text: bool = True,
                          translate_owner_response: bool = False,
                          progress_callback: Optional[Callable] = None) -> List[ProductionReview]:
        """
        Process all reviews in batches

        Args:
            reviews: List of all reviews to process
            translate_review_text: Whether to translate review text
            translate_owner_response: Whether to translate owner response
            progress_callback: Optional progress callback

        Returns:
            List of all processed reviews
        """
        start_time = time.time()
        self.logger.info(f"Starting batch translation processing for {len(reviews)} reviews")

        all_processed_reviews = []

        # Process in batches
        for i in range(0, len(reviews), self.batch_size):
            batch = reviews[i:i + self.batch_size]
            self.logger.debug(f"Processing batch {i//self.batch_size + 1}/{(len(reviews) + self.batch_size - 1)//self.batch_size}")

            processed_batch = self.process_batch(
                batch, translate_review_text, translate_owner_response,
                lambda current, total, langs: progress_callback(i + current, len(reviews), langs) if progress_callback else None
            )

            all_processed_reviews.extend(processed_batch)

            # Small delay between batches to avoid rate limiting
            if i + self.batch_size < len(reviews):
                time.sleep(0.1)

        self.stats.processing_time = time.time() - start_time

        self.logger.info(f"Batch translation completed in {self.stats.processing_time:.2f}s")
        self.logger.info(f"Processed {self.stats.total_reviews} reviews")
        self.logger.info(f"Languages detected: {self.stats.languages_detected}")
        self.logger.info(f"Reviews needing translation: {self.stats.reviews_needing_translation}")
        self.logger.info(f"Reviews successfully translated: {self.stats.reviews_translated}")
        self.logger.info(f"Translation errors: {self.stats.translation_errors}")

        return all_processed_reviews

def detect_and_translate_reviews(reviews: List[ProductionReview],
                                target_language: str = 'th',
                                translate_review_text: bool = True,
                                translate_owner_response: bool = False,
                                batch_size: int = 50,
                                progress_callback: Optional[Callable] = None) -> List[ProductionReview]:
    """
    Convenience function for batch language detection and translation

    Args:
        reviews: List of reviews to process
        target_language: Target language code (default: 'th')
        translate_review_text: Whether to translate review text
        translate_owner_response: Whether to translate owner response
        batch_size: Number of reviews to process in each batch
        progress_callback: Optional progress callback(current, total, detected_languages)

    Returns:
        List of processed reviews with translations
    """
    translator = BatchTranslator(target_language, batch_size)

    return translator.process_all_reviews(
        reviews=reviews,
        translate_review_text=translate_review_text,
        translate_owner_response=translate_owner_response,
        progress_callback=progress_callback
    )

# Utility function to save translation statistics
def save_translation_stats(stats: TranslationStats, file_path: str):
    """Save translation statistics to JSON file"""
    stats_dict = {
        'total_reviews': stats.total_reviews,
        'reviews_needing_translation': stats.reviews_needing_translation,
        'reviews_translated': stats.reviews_translated,
        'languages_detected': stats.languages_detected,
        'translation_errors': stats.translation_errors,
        'processing_time': stats.processing_time,
        'batch_count': stats.batch_count,
        'target_language': stats.target_language,
        'timestamp': datetime.now().isoformat()
    }

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(stats_dict, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    # Test the translator module
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))

    from src.scraper.production_scraper import ProductionReview

    # Create sample reviews
    sample_reviews = [
        ProductionReview(
            review_id="1",
            author_name="John Doe",
            author_url="",
            author_reviews_count=10,
            rating=5,
            date_formatted="01/01/2024",
            date_relative="1 week ago",
            review_text="This place is amazing! Highly recommended.",
            review_likes=5,
            review_photos_count=0,
            owner_response="Thank you for your review!",
            page_number=1
        ),
        ProductionReview(
            review_id="2",
            author_name="สมชาย ใจดี",
            author_url="",
            author_reviews_count=5,
            rating=4,
            date_formatted="02/01/2024",
            date_relative="2 days ago",
            review_text="สถานที่ดีครับ น่าเข้าพักมาก",
            review_likes=3,
            review_photos_count=1,
            owner_response="ขอบคุณที่มาใช้บริการนะครับ",
            page_number=1
        )
    ]

    print("Testing batch translation...")

    # Test translation
    translated_reviews = detect_and_translate_reviews(
        reviews=sample_reviews,
        target_language='en',
        translate_review_text=True,
        translate_owner_response=True,
        batch_size=10
    )

    print(f"Processed {len(translated_reviews)} reviews")
    for review in translated_reviews:
        print(f"Review {review.review_id}:")
        print(f"  Original: {review.review_text[:50]}...")
        if hasattr(review, 'review_text_translated') and review.review_text_translated:
            print(f"  Translated: {review.review_text_translated[:50]}...")
        print()