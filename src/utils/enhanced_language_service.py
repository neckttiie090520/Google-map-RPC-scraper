#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Language Detection and Translation Service
===============================================

Advanced language detection supporting multiple languages and
translation to English for all non-English content.

Author: Nextzus
Date: 2025-11-11
"""
import sys
import os
import io

# Fix Windows encoding for console output
if sys.platform == 'win32':
    os.system('chcp 65001 > nul 2>&1')
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import asyncio
import time
from typing import Optional, Dict, Tuple, List
from enum import Enum
from dataclasses import dataclass

# Language detection
try:
    from lingua import Language, LanguageDetectorBuilder
    LINGUA_AVAILABLE = True
except ImportError:
    print("Warning: lingua library not installed. Install with: pip install lingua")
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
    FRENCH = "fr"
    KOREAN = "ko"
    JAPANESE = "ja"
    CHINESE = "zh"
    SPANISH = "es"
    GERMAN = "de"
    RUSSIAN = "ru"
    ARABIC = "ar"
    UNKNOWN = "unknown"


@dataclass
class LanguageDetectionResult:
    """Result of language detection"""
    detected_language: SupportedLanguage
    confidence: float
    is_target_language: bool
    needs_translation: bool
    detected_scripts: List[str]


@dataclass
class TranslationResult:
    """Result of text translation"""
    original_text: str
    original_language: SupportedLanguage
    translated_text: str
    target_language: SupportedLanguage
    success: bool
    error_message: Optional[str] = None


class EnhancedLanguageService:
    """
    Enhanced language detection and translation service.

    Features:
    - Multi-language detection (TH, EN, FR, KO, JA, ZH, ES, DE, RU, AR)
    - Character script detection for better accuracy
    - All non-English languages translated to English
    - High-quality translation using Google Translate
    - Fallback detection for missing dependencies
    """

    def __init__(self, target_language: SupportedLanguage = SupportedLanguage.ENGLISH):
        """
        Initialize enhanced language service.

        Args:
            target_language: Target language for translations (default: English)
        """
        self.target_language = target_language

        # Initialize language detector with multiple languages
        if LINGUA_AVAILABLE:
            # Include many languages for comprehensive detection
            languages = [
                Language.ENGLISH, Language.THAI, Language.FRENCH,
                Language.KOREAN, Language.JAPANESE, Language.CHINESE,
                Language.SPANISH, Language.GERMAN, Language.RUSSIAN, Language.ARABIC
            ]

            self.detector = LanguageDetectorBuilder.from_languages(*languages)\
                .with_preloaded_language_models().build()
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
            'fallback_detection': 0,
            'languages_detected': {}
        }

    def detect_scripts(self, text: str) -> List[str]:
        """
        Detect character scripts present in text.

        Args:
            text: Text to analyze

        Returns:
            List of detected scripts
        """
        scripts = []

        # Thai script
        if any(3584 <= ord(c) <= 3711 for c in text):
            scripts.append("thai")

        # Korean script (Hangul)
        if any(44032 <= ord(c) <= 55215 for c in text):
            scripts.append("korean")

        # Japanese scripts (Hiragana, Katakana, Kanji)
        if any((12352 <= ord(c) <= 12447) or (12448 <= ord(c) <= 12543) or
               (19968 <= ord(c) <= 40959) for c in text):
            scripts.append("japanese")

        # Chinese script
        if any(19968 <= ord(c) <= 40959 for c in text):
            scripts.append("chinese")

        # Arabic script
        if any(1536 <= ord(c) <= 1791 for c in text):
            scripts.append("arabic")

        # Cyrillic script (Russian, etc.)
        if any(1024 <= ord(c) <= 1279 for c in text):
            scripts.append("cyrillic")

        # European accented characters
        if any(c in 'àâäçéèêëïîôöùûüÿæœ' for c in text.lower()):
            scripts.append("european")

        # German specific
        if any(c in 'äöüß' for c in text.lower()):
            scripts.append("german_specific")

        # Spanish specific
        if any(c in 'ñáéíóúü¿¡' for c in text.lower()):
            scripts.append("spanish_specific")

        return scripts

    def detect_language(self, text: str) -> LanguageDetectionResult:
        """
        Detect language of given text with enhanced accuracy.

        Args:
            text: Text to analyze

        Returns:
            LanguageDetectionResult with detailed detection info
        """
        if not text or not text.strip():
            return LanguageDetectionResult(
                detected_language=SupportedLanguage.ENGLISH,
                confidence=0.0,
                is_target_language=True,
                needs_translation=False,
                detected_scripts=[]
            )

        self.stats['detections'] += 1

        # Detect character scripts first
        detected_scripts = self.detect_scripts(text)

        if self.detector and LINGUA_AVAILABLE:
            try:
                # Use lingua for accurate detection
                detected_lang = self.detector.detect_language_of(text)

                # Map lingua Language to our enum
                lang_mapping = {
                    Language.THAI: SupportedLanguage.THAI,
                    Language.ENGLISH: SupportedLanguage.ENGLISH,
                    Language.FRENCH: SupportedLanguage.FRENCH,
                    Language.KOREAN: SupportedLanguage.KOREAN,
                    Language.JAPANESE: SupportedLanguage.JAPANESE,
                    Language.CHINESE: SupportedLanguage.CHINESE,
                    Language.SPANISH: SupportedLanguage.SPANISH,
                    Language.GERMAN: SupportedLanguage.GERMAN,
                    Language.RUSSIAN: SupportedLanguage.RUSSIAN,
                    Language.ARABIC: SupportedLanguage.ARABIC
                }

                detected_enum = lang_mapping.get(detected_lang, self._fallback_detection_with_scripts(text, detected_scripts))

                # Update statistics
                self.stats['languages_detected'][detected_enum.value] = self.stats['languages_detected'].get(detected_enum.value, 0) + 1

            except Exception as e:
                print(f"Language detection error: {e}")
                detected_enum = self._fallback_detection_with_scripts(text, detected_scripts)
                self.stats['fallback_detection'] += 1
        else:
            # Fallback: enhanced heuristic with script detection
            detected_enum = self._fallback_detection_with_scripts(text, detected_scripts)
            self.stats['fallback_detection'] += 1

        # Determine if translation is needed
        is_target_language = (detected_enum == self.target_language)
        needs_translation = not is_target_language and detected_enum != SupportedLanguage.UNKNOWN

        # Calculate confidence
        if self.detector and LINGUA_AVAILABLE:
            confidence = 0.9
        else:
            confidence = 0.7

        return LanguageDetectionResult(
            detected_language=detected_enum,
            confidence=confidence,
            is_target_language=is_target_language,
            needs_translation=needs_translation,
            detected_scripts=detected_scripts
        )

    def _fallback_detection_with_scripts(self, text: str, scripts: List[str]) -> SupportedLanguage:
        """
        Enhanced fallback detection using character scripts.

        Args:
            text: Text to analyze
            scripts: Detected character scripts

        Returns:
            Detected language as SupportedLanguage
        """
        # Priority-based detection

        # Thai script detection
        if "thai" in scripts:
            thai_ratio = sum(1 for char in text if 3584 <= ord(char) <= 3711) / len(text)
            if thai_ratio > 0.2:  # More than 20% Thai characters
                return SupportedLanguage.THAI

        # Korean detection
        if "korean" in scripts:
            korean_ratio = sum(1 for char in text if 44032 <= ord(char) <= 55215) / len(text)
            if korean_ratio > 0.2:
                return SupportedLanguage.KOREAN

        # Japanese detection
        if "japanese" in scripts or "chinese" in scripts:
            # Check for Japanese-specific patterns
            if any(char in 'あいうえおかきくけこ' for char in text):  # Hiragana
                return SupportedLanguage.JAPANESE
            elif any(char in 'アイウエオカキクケコ' for char in text):  # Katakana
                return SupportedLanguage.JAPANESE
            elif "chinese" in scripts and not any(char in 'あいうえおアイウエオ' for char in text):
                return SupportedLanguage.CHINESE

        # Arabic detection
        if "arabic" in scripts:
            arabic_ratio = sum(1 for char in text if 1536 <= ord(char) <= 1791) / len(text)
            if arabic_ratio > 0.2:
                return SupportedLanguage.ARABIC

        # Cyrillic detection
        if "cyrillic" in scripts:
            return SupportedLanguage.RUSSIAN

        # European languages detection
        if "german_specific" in scripts:
            return SupportedLanguage.GERMAN
        elif "spanish_specific" in scripts:
            return SupportedLanguage.SPANISH
        elif "european" in scripts:
            # Simple heuristic for French vs other European languages
            if any(word in text.lower() for word in ['le', 'la', 'les', 'de', 'du', 'des', 'et', 'est', 'dans', 'pour', 'avec']):
                return SupportedLanguage.FRENCH
            else:
                return SupportedLanguage.SPANISH  # Default to Spanish for other European

        # Default to English if no specific scripts detected
        return SupportedLanguage.ENGLISH

    def translate_text(self, text: str, source_language: Optional[SupportedLanguage] = None) -> TranslationResult:
        """
        Translate text to target language (English by default).

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
        if source_language == self.target_language or source_language == SupportedLanguage.UNKNOWN:
            return TranslationResult(
                original_text=text,
                original_language=source_language,
                translated_text=text,
                target_language=self.target_language,
                success=True
            )

        self.stats['translations'] += 1

        if not DEEP_TRANSLATOR_AVAILABLE:
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
            lang_codes = {
                SupportedLanguage.THAI: "th",
                SupportedLanguage.ENGLISH: "en",
                SupportedLanguage.FRENCH: "fr",
                SupportedLanguage.KOREAN: "ko",
                SupportedLanguage.JAPANESE: "ja",
                SupportedLanguage.CHINESE: "zh-CN",  # Use zh-CN for Simplified Chinese
                SupportedLanguage.SPANISH: "es",
                SupportedLanguage.GERMAN: "de",
                SupportedLanguage.RUSSIAN: "ru",
                SupportedLanguage.ARABIC: "ar"
            }

            src_code = lang_codes.get(source_language, "auto")
            target_code = lang_codes.get(self.target_language, "en")

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

    def process_review_text(self, text: str) -> Tuple[str, bool, Optional[str], SupportedLanguage]:
        """
        Process review text: detect language and translate if needed.

        Args:
            text: Review text to process

        Returns:
            Tuple of (processed_text, was_translated, error_message, detected_language)
        """
        if not text or not text.strip():
            return text, False, None, SupportedLanguage.ENGLISH

        # Detect language
        detection = self.detect_language(text)

        if not detection.needs_translation:
            return text, False, None, detection.detected_language

        # Translate to target language
        translation = self.translate_text(text, detection.detected_language)

        if translation.success:
            return translation.translated_text, True, None, detection.detected_language
        else:
            return text, False, translation.error_message, detection.detected_language

    async def process_review_text_async(self, text: str) -> Tuple[str, bool, Optional[str], SupportedLanguage]:
        """
        Async version of process_review_text.

        Args:
            text: Review text to process

        Returns:
            Tuple of (processed_text, was_translated, error_message, detected_language)
        """
        if not text or not text.strip():
            return text, False, None, SupportedLanguage.ENGLISH

        # Detect language
        detection = self.detect_language(text)

        if not detection.needs_translation:
            return text, False, None, detection.detected_language

        # Translate to target language
        translation = await self.translate_text_async(text, detection.detected_language)

        if translation.success:
            return translation.translated_text, True, None, detection.detected_language
        else:
            return text, False, translation.error_message, detection.detected_language

    def get_stats(self) -> Dict:
        """Get language service statistics."""
        return self.stats.copy()

    def reset_stats(self) -> None:
        """Reset statistics."""
        self.stats = {
            'detections': 0,
            'translations': 0,
            'translation_errors': 0,
            'fallback_detection': 0,
            'languages_detected': {}
        }


def create_enhanced_language_service(
    target_language: str = "en",
    enable_translation: bool = True
) -> Optional[EnhancedLanguageService]:
    """
    Factory function to create enhanced language service.

    Args:
        target_language: Target language ("en", "th", etc.)
        enable_translation: Whether to enable translation

    Returns:
        EnhancedLanguageService instance or None if not available
    """
    try:
        # Convert string to enum
        lang_mapping = {
            "th": SupportedLanguage.THAI,
            "en": SupportedLanguage.ENGLISH,
            "fr": SupportedLanguage.FRENCH,
            "ko": SupportedLanguage.KOREAN,
            "ja": SupportedLanguage.JAPANESE,
            "zh": SupportedLanguage.CHINESE,
            "es": SupportedLanguage.SPANISH,
            "de": SupportedLanguage.GERMAN,
            "ru": SupportedLanguage.RUSSIAN,
            "ar": SupportedLanguage.ARABIC
        }

        target_enum = lang_mapping.get(target_language.lower(), SupportedLanguage.ENGLISH)

        service = EnhancedLanguageService(target_language=target_enum)

        # Check if dependencies are available
        if not LINGUA_AVAILABLE or not DEEP_TRANSLATOR_AVAILABLE:
            if enable_translation:
                print("Warning: Some language features not available due to missing dependencies")
                print("Install with: pip install lingua deep-translator")

        return service

    except Exception as e:
        print(f"Failed to create enhanced language service: {e}")
        return None


# Global enhanced language service instance
_global_enhanced_language_service = None


def get_enhanced_language_service() -> Optional[EnhancedLanguageService]:
    """Get or create global enhanced language service instance."""
    global _global_enhanced_language_service
    if _global_enhanced_language_service is None:
        _global_enhanced_language_service = create_enhanced_language_service()
    return _global_enhanced_language_service


def init_enhanced_language_service(target_language: str = "en", enable_translation: bool = True) -> None:
    """
    Initialize global enhanced language service.

    Args:
        target_language: Target language (default: "en")
        enable_translation: Whether to enable translation
    """
    global _global_enhanced_language_service
    _global_enhanced_language_service = create_enhanced_language_service(target_language, enable_translation)


# Convenience functions
def detect_language_enhanced(text: str) -> LanguageDetectionResult:
    """Convenience function for enhanced language detection."""
    service = get_enhanced_language_service()
    if service:
        return service.detect_language(text)
    else:
        # Fallback - basic detection
        thai_chars = sum(1 for c in text if ord(c) >= 3584 and ord(c) <= 3711)
        lang = SupportedLanguage.THAI if thai_chars > len(text) * 0.3 else SupportedLanguage.ENGLISH
        return LanguageDetectionResult(
            detected_language=lang,
            confidence=0.5,
            is_target_language=True,
            needs_translation=False,
            detected_scripts=[]
        )


async def process_review_text_enhanced_async(text: str) -> Tuple[str, bool, Optional[str], SupportedLanguage]:
    """Convenience function for async enhanced text processing."""
    service = get_enhanced_language_service()
    if service:
        return await service.process_review_text_async(text)
    else:
        return text, False, "Enhanced language service not available", SupportedLanguage.ENGLISH


if __name__ == "__main__":
    # Test enhanced language service
    print("Testing Enhanced Language Service...")

    service = create_enhanced_language_service("en")
    if not service:
        print("Failed to create enhanced language service")
        sys.exit(1)

    # Test cases with multiple languages
    test_texts = [
        "ร้านนี้อร่อยมากครับ แนะนำเลย",  # Thai
        "This place is amazing! Highly recommended!",  # English
        "Excellent, plats typiques du nord de la Thaïlande",  # French
        "너무 맛있었어요 👍🏻",  # Korean
        "とても美味しかったです！",  # Japanese
        "食物很好吃，推荐！",  # Chinese
        "¡La comida estaba deliciosa!",  # Spanish
        "Das Essen war sehr gut!",  # German
        "Отличный ресторан!",  # Russian
        "مطعم رائع جداً!"  # Arabic
    ]

    print("\nTesting enhanced language detection and translation:")
    for i, text in enumerate(test_texts, 1):
        print(f"\nTest {i}:")
        print(f"Original: {text}")

        # Detect language
        detection = service.detect_language(text)
        print(f"Detected: {detection.detected_language.value} (confidence: {detection.confidence:.2f})")
        print(f"Scripts: {', '.join(detection.detected_scripts) if detection.detected_scripts else 'None'}")
        print(f"Needs translation: {detection.needs_translation}")

        # Process (detect + translate if needed)
        processed, was_translated, error, detected_lang = service.process_review_text(text)
        print(f"Processed: {processed}")
        print(f"Was translated: {was_translated}")
        print(f"Final detected language: {detected_lang.value}")
        if error:
            print(f"Error: {error}")

    # Print stats
    stats = service.get_stats()
    print(f"\nStats: {stats}")
    print("Enhanced language service test completed!")