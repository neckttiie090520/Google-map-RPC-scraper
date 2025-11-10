# -*- coding: utf-8 -*-
"""
Unicode Display Handler for Mixed Language Output
===============================================

Provides clean display of mixed language text (Thai, English, Japanese, Chinese)
without encoding issues on different platforms.

Inspired by Go's native UTF-8 support and runewidth library.

Author: Nextzus
Date: 2025-11-11
"""
import sys
import os
import re
from typing import Optional

# Fix Windows encoding
if sys.platform == 'win32':
    os.system('chcp 65001 > nul 2>&1')


class UnicodeDisplay:
    """Handle Unicode text display with proper character width calculation"""

    @staticmethod
    def safe_print(text: str, prefix: str = "", suffix: str = ""):
        """
        Safely print Unicode text without encoding issues

        Args:
            text: Text to display
            prefix: Optional prefix to add before text
            suffix: Optional suffix to add after text
        """
        try:
            # Direct print with UTF-8 handling
            full_text = f"{prefix}{text}{suffix}"
            print(full_text)
        except (UnicodeEncodeError, UnicodeDecodeError) as e:
            # Fallback: Use ASCII-safe encoding
            ascii_text = UnicodeDisplay.to_ascii_safe(text)
            print(f"{prefix}{ascii_text}{suffix} [ENCODING ERROR: {e}]")

    @staticmethod
    def safe_print_with_length(text: str, max_length: int = 80, prefix: str = ""):
        """
        Print Unicode text with length truncation

        Args:
            text: Text to display
            max_length: Maximum display length
            prefix: Optional prefix
        """
        try:
            # Calculate display width (approximation for Thai/Asian chars)
            display_text = UnicodeDisplay.truncate_for_display(text, max_length)
            print(f"{prefix}{display_text}")
        except (UnicodeEncodeError, UnicodeDecodeError):
            ascii_text = UnicodeDisplay.to_ascii_safe(text)
            truncated = ascii_text[:max_length] + "..." if len(ascii_text) > max_length else ascii_text
            print(f"{prefix}{truncated}")

    @staticmethod
    def truncate_for_display(text: str, max_length: int) -> str:
        """
        Truncate text for display, considering Asian character width

        Args:
            text: Text to truncate
            max_length: Maximum display length

        Returns:
            Truncated text
        """
        if not text:
            return text

        # Simple approximation: Thai/Asian chars count as 2 width units
        current_width = 0
        result_chars = []

        for char in text:
            char_width = UnicodeDisplay.get_char_width(char)
            if current_width + char_width > max_length:
                break
            result_chars.append(char)
            current_width += char_width

        result = ''.join(result_chars)
        if len(result) < len(text):
            result += "..."

        return result

    @staticmethod
    def get_char_width(char: str) -> int:
        """
        Get display width of a character
        Approximates runewidth library behavior

        Args:
            char: Single character

        Returns:
            Display width (1 for Latin, 2 for most Asian chars)
        """
        # Latin and basic symbols
        if ord(char) <= 127:
            return 1

        # Thai range
        if '\u0E00' <= char <= '\u0E7F':
            return 2

        # Japanese ranges (Hiragana, Katakana)
        if '\u3040' <= char <= '\u309F' or '\u30A0' <= char <= '\u30FF':
            return 2

        # Chinese/Japanese/Korean unified CJK
        if '\u4E00' <= char <= '\u9FFF':
            return 2

        # Default to 1 for other Unicode
        return 1

    @staticmethod
    def to_ascii_safe(text: str) -> str:
        """
        Convert text to ASCII-safe representation

        Args:
            text: Unicode text

        Returns:
            ASCII-safe text with replacements
        """
        if not text:
            return text

        # Replace problematic characters with ASCII equivalents
        replacements = {
            'ส': 'S', 'ม': 'M', 'น': 'N', 'ว': 'W', 'พ': 'P', 'ฟ': 'F', 'ห': 'H', 'ง': 'N', 'า': 'A',
            'ก': 'K', 'ด': 'D', 'บ': 'B', 'อ': 'O', 'จ': 'J', 'ป': 'P', 'ผ': 'P', 'ฝ': 'F',
            'ไ': 'Y', 'ใ': 'I', 'ล': 'L', 'ร': 'R', 'ว': 'W', 'ศ': 'S', 'ษ': 'S',
            'ห': 'H', 'ฬ': 'L', 'อ': 'O', 'ฮ': 'H', 'ะ': 'A', 'า': 'A', 'ำ': 'M',
            'ิ': 'i', 'ี': 'e', 'ึ': 'ue', 'ื': 'ue', 'ุ': 'u', 'ู': 'oo', 'โ': 'o',
            'เ': 'e', 'แ': 'ae', 'โ': 'o', 'ใ': 'ai', 'ไ': 'ai',
        }

        # Simple character-by-character replacement
        result = []
        for char in text:
            result.append(replacements.get(char, char))

        return ''.join(result)

    @staticmethod
    def format_name_with_language(name: str, language: str = "unknown") -> str:
        """
        Format name with language indicator

        Args:
            name: Person/place name
            language: Detected language

        Returns:
            Formatted name with language info
        """
        if language == "unknown":
            # Try to detect language
            if UnicodeDisplay.is_thai_text(name):
                language = "th"
            elif UnicodeDisplay.is_japanese_text(name):
                language = "ja"
            elif UnicodeDisplay.is_chinese_text(name):
                language = "zh"
            else:
                language = "en"

        # Language indicators
        lang_indicators = {
            "th": "[TH]",
            "ja": "[JP]",
            "zh": "[CN]",
            "en": "[EN]",
            "unknown": "[??]"
        }

        return f"{name} {lang_indicators.get(language, '[??]')}"

    @staticmethod
    def is_thai_text(text: str) -> bool:
        """Check if text contains primarily Thai characters"""
        thai_chars = len(re.findall(r'[\u0E00-\u0E7F]', text))
        total_chars = len(re.sub(r'\s', '', text))
        return total_chars > 0 and thai_chars / total_chars > 0.3

    @staticmethod
    def is_japanese_text(text: str) -> bool:
        """Check if text contains Japanese characters"""
        japanese_chars = len(re.findall(r'[\u3040-\u309F\u30A0-\u30FF]', text))
        return japanese_chars > 0

    @staticmethod
    def is_chinese_text(text: str) -> bool:
        """Check if text contains Chinese characters"""
        chinese_chars = len(re.findall(r'[\u4E00-\u9FFF]', text))
        return chinese_chars > 0

    @staticmethod
    def print_review_summary(reviews: list, language_filter: Optional[str] = None):
        """
        Print summary of reviews with language statistics

        Args:
            reviews: List of review objects
            language_filter: Target language filter
        """
        if not reviews:
            print("No reviews found")
            return

        # Count languages
        languages = {
            'th': 0,
            'en': 0,
            'ja': 0,
            'zh': 0,
            'other': 0
        }

        for review in reviews:
            if hasattr(review, 'review_text') and review.review_text:
                if UnicodeDisplay.is_thai_text(review.review_text):
                    languages['th'] += 1
                elif UnicodeDisplay.is_japanese_text(review.review_text):
                    languages['ja'] += 1
                elif UnicodeDisplay.is_chinese_text(review.review_text):
                    languages['zh'] += 1
                elif UnicodeDisplay.is_english_text(review.review_text):
                    languages['en'] += 1
                else:
                    languages['other'] += 1

        # Print summary
        UnicodeDisplay.safe_print(f"Reviews Summary (Total: {len(reviews)})")
        UnicodeDisplay.safe_print(f"  Thai: {languages['th']}")
        UnicodeDisplay.safe_print(f"  English: {languages['en']}")
        UnicodeDisplay.safe_print(f"  Japanese: {languages['ja']}")
        UnicodeDisplay.safe_print(f"  Chinese: {languages['zh']}")
        UnicodeDisplay.safe_print(f"  Other: {languages['other']}")

        if language_filter:
            filtered_count = languages.get(language_filter, 0)
            UnicodeDisplay.safe_print(f"  Filtered ({language_filter}): {filtered_count}")

    @staticmethod
    def is_english_text(text: str) -> bool:
        """Check if text contains primarily English characters"""
        english_chars = len(re.findall(r'[a-zA-Z]', text))
        total_chars = len(re.sub(r'\s', '', text))
        return total_chars > 0 and english_chars / total_chars > 0.7


# Convenience functions for direct use
safe_print = UnicodeDisplay.safe_print
safe_print_with_length = UnicodeDisplay.safe_print_with_length
format_name = UnicodeDisplay.format_name_with_language
print_review_summary = UnicodeDisplay.print_review_summary