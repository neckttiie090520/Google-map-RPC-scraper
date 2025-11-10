# -*- coding: utf-8 -*-
"""
Language Filter for Reviews
==========================

Provides language filtering functionality for review text.
Filters reviews based on target language setting.

Author: Nextzus
Date: 2025-11-11
"""
import re
import sys
import os

# Fix Windows encoding
if sys.platform == 'win32':
    os.system('chcp 65001 > nul 2>&1')


class LanguageFilter:
    """Language filtering utilities for review text"""

    @staticmethod
    def filter_by_language(text: str, language: str, debug: bool = False) -> str:
        """Filter text based on target language"""
        if not text or len(text.strip()) < 2:
            return text

        try:
            # For English: Only keep English characters, numbers, and basic punctuation
            if language == 'en':
                # Remove non-ASCII characters (Thai, Japanese, Chinese, etc.)
                # Keep English letters, numbers, spaces, and basic punctuation
                filtered = re.sub(r'[^\x00-\x7F\s.,!?;:()[\]{}"\'-]', '', text)
                # Clean up any remaining problematic characters
                filtered = re.sub(r'[^\w\s.,!?;:()[\]{}"\'-]', '', filtered)
                return filtered.strip()

            # For Thai: Keep Thai + English characters (common in Thai reviews)
            elif language == 'th':
                # Thai Unicode range: \u0E00-\u0E7F
                # Thai numbers: \u0E50-\u0E59
                # Keep Thai, English, numbers, spaces, and basic punctuation
                thai_range = '\u0E00-\u0E7F\u0E50-\u0E59'
                english_range = 'a-zA-Z0-9'
                pattern = f'[^{thai_range}{english_range}\s.,!?;:()[\]{}"\'-]'
                filtered = re.sub(pattern, '', text)
                return filtered.strip()

            # For Japanese: Keep Hiragana, Katakana, Kanji + English
            elif language == 'ja':
                # Japanese Unicode ranges
                hiragana = '\u3040-\u309F'
                katakana = '\u30A0-\u30FF'
                kanji = '\u4E00-\u9FAF'  # Common range, simplified
                japanese_ranges = f'{hiragana}{katakana}{kanji}'
                english_range = 'a-zA-Z0-9'
                pattern = f'[^{japanese_ranges}{english_range}\s.,!?;:()[\]{}"\'-]'
                filtered = re.sub(pattern, '', text)
                return filtered.strip()

            # For Chinese: Keep Chinese characters + English
            elif language == 'zh':
                # Chinese Unicode ranges
                chinese_simplified = '\u4E00-\u9FFF'
                english_range = 'a-zA-Z0-9'
                pattern = f'[^{chinese_simplified}{english_range}\s.,!?;:()[\]{}"\'-]'
                filtered = re.sub(pattern, '', text)
                return filtered.strip()

            # For other languages: return as-is (no filtering)
            else:
                return text

        except Exception as e:
            if debug:
                print(f"[DEBUG] Language filtering failed: {e}")
            return text

    @staticmethod
    def is_english_text(text: str) -> bool:
        """Check if text is primarily English"""
        if not text or len(text.strip()) < 2:
            return False

        # Count English vs non-English characters
        english_chars = len(re.findall(r'[a-zA-Z]', text))
        total_chars = len(re.sub(r'\s', '', text))

        if total_chars == 0:
            return False

        return english_chars / total_chars > 0.7  # 70% English threshold

    @staticmethod
    def is_thai_text(text: str) -> bool:
        """Check if text is primarily Thai"""
        if not text or len(text.strip()) < 2:
            return False

        # Count Thai characters
        thai_chars = len(re.findall(r'[\u0E00-\u0E7F]', text))
        total_chars = len(re.sub(r'\s', '', text))

        if total_chars == 0:
            return False

        return thai_chars / total_chars > 0.3  # 30% Thai threshold (allows mixed Thai-English)

    @staticmethod
    def detect_language(text: str) -> str:
        """Detect the primary language of text"""
        if not text or len(text.strip()) < 2:
            return 'unknown'

        # Check for language indicators
        if LanguageFilter.is_english_text(text):
            return 'en'
        elif LanguageFilter.is_thai_text(text):
            return 'th'
        elif re.search(r'[\u3040-\u309F\u30A0-\u30FF]', text):  # Japanese
            return 'ja'
        elif re.search(r'[\u4E00-\u9FFF]', text):  # Chinese
            return 'zh'
        else:
            return 'unknown'

    @staticmethod
    def should_include_review(review_text: str, target_language: str, debug: bool = False) -> bool:
        """Determine if a review should be included based on language matching"""
        if not review_text or len(review_text.strip()) < 2:
            return False

        # Detect the actual language of the review
        detected_language = LanguageFilter.detect_language(review_text)

        if debug:
            print(f"[LANG] Review language detected: {detected_language}, Target: {target_language}")
            print(f"[LANG] Review text: {review_text[:100]}...")

        # Include if languages match
        if detected_language == target_language:
            return True

        # For English target, also include mixed-language reviews with high English content
        if target_language == 'en' and LanguageFilter.is_english_text(review_text):
            return True

        # For Thai target, include mixed Thai-English reviews
        if target_language == 'th' and LanguageFilter.is_thai_text(review_text):
            return True

        return False