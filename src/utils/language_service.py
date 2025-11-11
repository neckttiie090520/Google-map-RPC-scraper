# -*- coding: utf-8 -*-
"""
Language Detection and Translation Service
========================================

Supports detection and translation of review text between Thai and English.
Uses lingua-py for accurate language detection and googletrans for translation.

Author: Nextzus
Date: 2025-11-11
"""
import sys
import os

# Fix Windows encoding for console output
if sys.platform == 'win32':
    os.system('chcp 65001 > nul 2>&1')

import asyncio
import time
from typing import Optional, Dict, Tuple
from enum import Enum
from dataclasses import dataclass

# Language detection
LINGUA_AVAILABLE = False
try:
    # Try to import the expected classes from lingua
    from lingua import Language, LanguageDetectorBuilder
    LINGUA_AVAILABLE = True
except (ImportError, AttributeError):
    try:
        # Fallback: check if lingua is installed but has different API
        import lingua
        # Check if it has the expected attributes
        if hasattr(lingua, 'Language') and hasattr(lingua, 'LanguageDetectorBuilder'):
            Language = lingua.Language
            LanguageDetectorBuilder = lingua.LanguageDetectorBuilder
            LINGUA_AVAILABLE = True
        else:
            LINGUA_AVAILABLE = False
    except ImportError:
        LINGUA_AVAILABLE = False

# Translation service
try:
    from deep_translator import GoogleTranslator
    DEEP_TRANSLATOR_AVAILABLE = True
except ImportError:
    print("Warning: deep-translator library not installed. Install with: pip install deep-translator")
    DEEP_TRANSLATOR_AVAILABLE = False


class SupportedLanguage(Enum):
    """Supported languages for detection and translation"""
    THAI = "th"
    ENGLISH = "en"


@dataclass
class LanguageDetectionResult:
    """Result of language detection"""
    detected_language: SupportedLanguage
    confidence: float
    is_target_language: bool
    needs_translation: bool


@dataclass
class TranslationResult:
    """Result of text translation"""
    original_text: str
    original_language: SupportedLanguage
    translated_text: str
    target_language: SupportedLanguage
    success: bool
    error_message: Optional[str] = None


class LanguageService:
    """
    Language detection and translation service for review text.

    Features:
    - Accurate Thai/English language detection using lingua
    - High-quality translation using Google Translate
    - Configurable target language settings
    - Async translation support
    - Fallback for missing dependencies
    - Error handling and retry logic
    """

    def __init__(self, target_language: SupportedLanguage = SupportedLanguage.ENGLISH):
        """
        Initialize language service.

        Args:
            target_language: Target language for translations
        """
        self.target_language = target_language

        # Initialize language detector
        if LINGUA_AVAILABLE:
            self.detector = LanguageDetectorBuilder.from_languages(
                Language.THAI, Language.ENGLISH
            ).with_preloaded_language_models().build()
        else:
            self.detector = None

        # Initialize translator
        if DEEP_TRANSLATOR_AVAILABLE:
            self.translator = GoogleTranslator()
        else:
            self.translator = None

        # Statistics
        self.stats = {
            'detections': 0,
            'translations': 0,
            'translation_errors': 0,
            'fallback_detection': 0
        }

    def detect_language(self, text: str) -> LanguageDetectionResult:
        """
        Detect language of given text.

        Args:
            text: Text to analyze

        Returns:
            LanguageDetectionResult with detection details
        """
        if not text or not text.strip():
            return LanguageDetectionResult(
                detected_language=SupportedLanguage.ENGLISH,
                confidence=0.0,
                is_target_language=True,
                needs_translation=False
            )

        self.stats['detections'] += 1

        if self.detector and LINGUA_AVAILABLE:
            try:
                # Use lingua for accurate detection
                detected_lang = self.detector.detect_language_of(text)

                # Map to our enum
                if detected_lang == Language.THAI:
                    lang_enum = SupportedLanguage.THAI
                elif detected_lang == Language.ENGLISH:
                    lang_enum = SupportedLanguage.ENGLISH
                else:
                    # Fallback to English for other languages
                    lang_enum = SupportedLanguage.ENGLISH
                    self.stats['fallback_detection'] += 1
            except Exception as e:
                print(f"Language detection error: {e}")
                # Fallback: simple heuristic
                lang_enum = self._fallback_detection(text)
                self.stats['fallback_detection'] += 1
        else:
            # Fallback: simple heuristic
            lang_enum = self._fallback_detection(text)
            self.stats['fallback_detection'] += 1

        # Determine if translation is needed
        is_target_language = (lang_enum == self.target_language)
        needs_translation = not is_target_language

        # Calculate confidence (simplified)
        confidence = 0.8 if self.detector and LINGUA_AVAILABLE else 0.6

        return LanguageDetectionResult(
            detected_language=lang_enum,
            confidence=confidence,
            is_target_language=is_target_language,
            needs_translation=needs_translation
        )

    def _fallback_detection(self, text: str) -> SupportedLanguage:
        """
        Simple heuristic fallback for language detection.

        Args:
            text: Text to analyze

        Returns:
            Detected language as SupportedLanguage
        """
        # Simple heuristic: check for Thai characters
        thai_chars = sum(1 for char in text if ord(char) >= 3584 and ord(char) <= 3711)

        if thai_chars > len(text) * 0.3:  # If more than 30% Thai characters
            return SupportedLanguage.THAI
        else:
            return SupportedLanguage.ENGLISH

    def translate_text(self, text: str, source_language: Optional[SupportedLanguage] = None) -> TranslationResult:
        """
        Translate text to target language.

        Args:
            text: Text to translate
            source_language: Source language (auto-detect if None)

        Returns:
            TranslationResult with translation details
        """
        if not text or not text.strip():
            return TranslationResult(
                original_text="",
                original_language=SupportedLanguage.ENGLISH,
                translated_text="",
                target_language=self.target_language,
                success=False,
                error_message="Empty text"
            )

        # Auto-detect source language if not provided
        if source_language is None:
            detection = self.detect_language(text)
            source_language = detection.detected_language

        # Check if translation is needed
        if source_language == self.target_language:
            return TranslationResult(
                original_text=text,
                original_language=source_language,
                translated_text=text,
                target_language=self.target_language,
                success=True
            )

        self.stats['translations'] += 1

        if not self.translator or not DEEP_TRANSLATOR_AVAILABLE:
            return TranslationResult(
                original_text=text,
                original_language=source_language,
                translated_text=text,
                target_language=self.target_language,
                success=False,
                error_message="Translation service not available"
            )

        try:
            # Convert to Google Translate language codes
            src_code = "th" if source_language == SupportedLanguage.THAI else "en"
            target_code = "th" if self.target_language == SupportedLanguage.THAI else "en"

            # Perform translation using deep-translator
            translator = GoogleTranslator(source=src_code, target=target_code)
            result = translator.translate(text)

            return TranslationResult(
                original_text=text,
                original_language=source_language,
                translated_text=result,
                target_language=self.target_language,
                success=True
            )

        except Exception as e:
            self.stats['translation_errors'] += 1
            return TranslationResult(
                original_text=text,
                original_language=source_language,
                translated_text=text,  # Return original on error
                target_language=self.target_language,
                success=False,
                error_message=f"Translation failed: {str(e)}"
            )

    async def translate_text_async(self, text: str, source_language: Optional[SupportedLanguage] = None) -> TranslationResult:
        """
        Async version of translate_text.

        Args:
            text: Text to translate
            source_language: Source language (auto-detect if None)

        Returns:
            TranslationResult with translation details
        """
        # Run translation in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.translate_text,
            text,
            source_language
        )

    def process_review_text(self, text: str) -> Tuple[str, bool, Optional[str]]:
        """
        Process review text: detect language and translate if needed.

        Args:
            text: Review text to process

        Returns:
            Tuple of (processed_text, was_translated, error_message)
        """
        if not text or not text.strip():
            return text, False, None

        # Detect language
        detection = self.detect_language(text)

        if not detection.needs_translation:
            return text, False, None

        # Translate to target language
        translation = self.translate_text(text, detection.detected_language)

        if translation.success:
            return translation.translated_text, True, None
        else:
            return text, False, translation.error_message

    async def process_review_text_async(self, text: str) -> Tuple[str, bool, Optional[str]]:
        """
        Async version of process_review_text.

        Args:
            text: Review text to process

        Returns:
            Tuple of (processed_text, was_translated, error_message)
        """
        if not text or not text.strip():
            return text, False, None

        # Detect language
        detection = self.detect_language(text)

        if not detection.needs_translation:
            return text, False, None

        # Translate to target language
        translation = await self.translate_text_async(text, detection.detected_language)

        if translation.success:
            return translation.translated_text, True, None
        else:
            return text, False, translation.error_message

    def get_stats(self) -> Dict:
        """Get language service statistics."""
        return self.stats.copy()

    def reset_stats(self) -> None:
        """Reset statistics."""
        self.stats = {
            'detections': 0,
            'translations': 0,
            'translation_errors': 0,
            'fallback_detection': 0
        }


def create_language_service(
    target_language: str = "en",
    enable_translation: bool = True
) -> Optional[LanguageService]:
    """
    Factory function to create language service.

    Args:
        target_language: Target language ("th" or "en")
        enable_translation: Whether to enable translation

    Returns:
        LanguageService instance or None if not available
    """
    try:
        # Convert string to enum
        if target_language.lower() == "th":
            target_enum = SupportedLanguage.THAI
        else:
            target_enum = SupportedLanguage.ENGLISH

        service = LanguageService(target_language=target_enum)

        # Check if dependencies are available
        if not LINGUA_AVAILABLE or not DEEP_TRANSLATOR_AVAILABLE:
            if enable_translation:
                print("Warning: Some language features not available due to missing dependencies")
                print("Install with: pip install lingua deep-translator")

        return service

    except Exception as e:
        print(f"Failed to create language service: {e}")
        return None


# Global language service instance
_global_language_service = None


def get_language_service() -> Optional[LanguageService]:
    """Get or create global language service instance."""
    global _global_language_service
    if _global_language_service is None:
        _global_language_service = create_language_service()
    return _global_language_service


def init_language_service(target_language: str = "en", enable_translation: bool = True) -> None:
    """
    Initialize global language service.

    Args:
        target_language: Target language ("th" or "en")
        enable_translation: Whether to enable translation
    """
    global _global_language_service
    _global_language_service = create_language_service(target_language, enable_translation)


# Convenience functions
def detect_language(text: str) -> LanguageDetectionResult:
    """Convenience function for language detection."""
    service = get_language_service()
    if service:
        return service.detect_language(text)
    else:
        # Fallback
        chars = sum(1 for c in text if ord(c) >= 3584 and ord(c) <= 3711)
        lang = SupportedLanguage.THAI if chars > len(text) * 0.3 else SupportedLanguage.ENGLISH
        return LanguageDetectionResult(
            detected_language=lang,
            confidence=0.5,
            is_target_language=True,
            needs_translation=False
        )


async def process_review_text_async(text: str) -> Tuple[str, bool, Optional[str]]:
    """Convenience function for async text processing."""
    service = get_language_service()
    if service:
        return await service.process_review_text_async(text)
    else:
        return text, False, "Language service not available"


if __name__ == "__main__":
    # Test language service
    print("Testing Language Service...")

    service = create_language_service("en")
    if not service:
        print("Failed to create language service")
        sys.exit(1)

    # Test cases
    test_texts = [
        "ร้านนี้อร่อยมากครับ แนะนำเลย",
        "This place is amazing! Highly recommended!",
        "Good food but service was slow",
        "รสชาตดี แต่ราคาค่อนสูง"
    ]

    print("\nTesting language detection and translation:")
    for i, text in enumerate(test_texts, 1):
        print(f"\nTest {i}:")
        print(f"Original: {text}")

        # Detect language
        detection = service.detect_language(text)
        print(f"Detected: {detection.detected_language.value} (confidence: {detection.confidence:.2f})")
        print(f"Needs translation: {detection.needs_translation}")

        # Process (detect + translate if needed)
        processed, was_translated, error = service.process_review_text(text)
        print(f"Processed: {processed}")
        print(f"Was translated: {was_translated}")
        if error:
            print(f"Error: {error}")

    # Print stats
    print(f"\nStats: {service.get_stats()}")
    print("Language service test completed!")