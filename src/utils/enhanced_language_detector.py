#!/usr/bin/env python3
"""
Enhanced Language Detector for Chinese Variants
==============================================

This module provides enhanced language detection that can distinguish between
different Chinese language variants and other Asian languages more accurately.

Supported Chinese Variants:
- zh-cn: Simplified Chinese (简体中文)
- zh-tw: Traditional Chinese (繁體中文)
- zh-hk: Hong Kong Chinese (香港中文)
- zh-sg: Singapore Chinese
- zh-my: Malaysian Chinese

Other Enhanced Detection:
- ja: Japanese (日本語)
- ko: Korean (한국어)
- th: Thai (ไทย)
- en: English
- id: Indonesian
- vi: Vietnamese
- ms: Malay
"""

import re
from typing import Dict, List, Optional, Tuple
from langdetect import detect, DetectorFactory
import logging

# Set seed for consistent detection
DetectorFactory.seed = 0

class EnhancedLanguageDetector:
    """Enhanced language detector with Chinese variant support"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # Chinese character patterns for different variants
        self.chinese_patterns = {
            'zh-cn': {
                # Simplified Chinese characters (common examples)
                'characters': ['中', '国', '文', '来', '个', '学', '开', '关', '长', '东', '贝', '车', '见', '买', '卖'],
                'words': ['中国', '中文', '学习', '工作', '公司', '发展', '经济', '网络', '手机', '电脑'],
                'description': 'Simplified Chinese (简体中文)'
            },
            'zh-tw': {
                # Traditional Chinese characters (common examples)
                'characters': ['中', '國', '文', '來', '個', '學', '開', '關', '長', '東', '貝', '車', '見', '買', '賣'],
                'words': ['中國', '中文', '學習', '工作', '公司', '發展', '經濟', '網絡', '手機', '電腦'],
                'description': 'Traditional Chinese (繁體中文)'
            },
            'zh-hk': {
                # Hong Kong specific patterns
                'characters': ['中', '國', '文', '來', '個', '學', '開', '關', '長', '東'],
                'words': ['香港', '澳門', '廣東', '話', '飲茶', '點心', '巴士', '的士'],
                'description': 'Hong Kong Chinese (香港中文)'
            }
        }

        # Other language patterns for better accuracy
        self.language_patterns = {
            'ja': {
                'characters': ['あ', 'い', 'う', 'え', 'お', 'か', 'き', 'く', 'け', 'こ', '漢字', 'ひらがな', 'カタカナ'],
                'patterns': [r'[ひらがな]', r'[カタカナ]', r'です', r'ます'],
                'description': 'Japanese (日本語)'
            },
            'ko': {
                'characters': ['가', '나', '다', '라', '마', '바', '사', '아', '자', '차'],
                'patterns': [r'[가-힣]', r'합니다', r'입니다', r'ㅂ니다', r'ㅂ니다'],
                'description': 'Korean (한국어)'
            },
            'th': {
                'characters': ['ก', 'ข', 'ฃ', 'ค', 'ฅ', 'ฆ', 'ง', 'จ', 'ฉ', 'ช'],
                'patterns': [r'[ก-๛]', r'ครับ', r'ค่ะ', r'นะคะ', r'เรียบร้อย'],
                'description': 'Thai (ไทย)'
            }
        }

    def detect_chinese_variant(self, text: str) -> Optional[str]:
        """
        Detect Chinese variant with enhanced accuracy

        Args:
            text: Text to analyze

        Returns:
            Chinese language code (zh-cn, zh-tw, zh-hk) or None if not Chinese
        """
        if not text or len(text.strip()) < 2:
            return None

        text_clean = text.strip()

        # Check for Hong Kong specific patterns first
        hk_words = ['香港', '澳門', '廣東話', '飲茶', '點心', '巴士', '的士', '茶餐廳']
        if any(word in text_clean for word in hk_words):
            return 'zh-hk'

        # Count simplified vs traditional characters
        simplified_count = 0
        traditional_count = 0

        # Common simplified/traditional pairs
        char_pairs = [
            ('国', '國'), ('学', '學'), ('开', '開'), ('关', '關'), ('长', '長'),
            ('东', '東'), ('贝', '貝'), ('车', '車'), ('见', '見'), ('买', '買'),
            ('卖', '賣'), ('个', '個'), ('来', '來'), ('发', '發'), ('会', '會'),
            ('机', '機'), ('电', '電'), ('脑', '腦'), ('长', '長'), ('门', '門')
        ]

        for simple, traditional in char_pairs:
            simplified_count += text_clean.count(simple)
            traditional_count += text_clean.count(traditional)

        # Additional variant-specific characters
        simplified_chars = ['个', '长', '发', '机', '电', '这', '那', '她', '它', '们']
        traditional_chars = ['個', '長', '發', '機', '電', '這', '那', '她', '它', '們']

        for char in simplified_chars:
            simplified_count += text_clean.count(char)

        for char in traditional_chars:
            traditional_count += text_clean.count(char)

        total_chinese = simplified_count + traditional_count

        if total_chinese == 0:
            return None

        # Determine variant based on character ratio
        if total_chinese > 0:
            simplified_ratio = simplified_count / total_chinese

            if simplified_ratio > 0.7:
                return 'zh-cn'  # Predominantly simplified
            elif simplified_ratio < 0.3:
                return 'zh-tw'  # Predominantly traditional
            else:
                # Mixed case - use additional heuristics
                # Check for common words in each variant
                simplified_words = ['我们', '学习', '工作', '公司', '发展', '网络']
                traditional_words = ['我們', '學習', '工作', '公司', '發展', '網絡']

                simplified_word_count = sum(1 for word in simplified_words if word in text_clean)
                traditional_word_count = sum(1 for word in traditional_words if word in text_clean)

                if simplified_word_count > traditional_word_count:
                    return 'zh-cn'
                elif traditional_word_count > simplified_word_count:
                    return 'zh-tw'
                else:
                    # Default to simplified for mixed cases
                    return 'zh-cn'

        return None

    def detect_language_enhanced(self, text: str) -> str:
        """
        Detect language with enhanced Chinese variant support

        Args:
            text: Text to detect language for

        Returns:
            Language code with variant support (e.g., 'zh-cn', 'zh-tw', 'ja', 'ko', 'th', 'en')
        """
        if not text or not text.strip():
            return 'unknown'

        text_clean = text.strip()

        # First check for Chinese variants
        chinese_variant = self.detect_chinese_variant(text_clean)
        if chinese_variant:
            return chinese_variant

        # Check other languages with pattern matching
        for lang_code, patterns in self.language_patterns.items():
            if 'patterns' in patterns:
                for pattern in patterns['patterns']:
                    if re.search(pattern, text_clean):
                        return lang_code
            elif 'characters' in patterns:
                # Check for presence of language-specific characters
                char_count = sum(1 for char in text_clean if char in patterns['characters'])
                if char_count > len(text_clean) * 0.1:  # 10% threshold
                    return lang_code

        # Fallback to standard langdetect
        try:
            detected = detect(text_clean[:500])  # Use first 500 chars

            # Map generic Chinese to specific variant
            if detected == 'zh':
                # Use Chinese variant detection as fallback
                variant = self.detect_chinese_variant(text_clean)
                return variant if variant else 'zh-cn'  # Default to simplified

            return detected

        except Exception as e:
            self.logger.debug(f"Language detection failed: {e}")
            return 'unknown'

    def get_language_name(self, lang_code: str) -> str:
        """
        Get human-readable language name with variant support

        Args:
            lang_code: Language code (e.g., 'zh-cn', 'zh-tw', 'ja', 'th')

        Returns:
            Human-readable language name in Thai
        """
        language_names = {
            # Chinese variants
            'zh-cn': 'จีนตัวย่อ (Simplified)',
            'zh-tw': 'จีนตัวเต็ม (Traditional)',
            'zh-hk': 'จีนฮ่องกง (Hong Kong)',
            'zh-sg': 'จีนสิงคโปร์',
            'zh-my': 'จีนมาเลเซีย',
            'zh': 'จีน',

            # Other languages
            'en': 'อังกฤษ',
            'ja': 'ญี่ปุ่น',
            'ko': 'เกาหลี',
            'th': 'ไทย',
            'id': 'อินโดนีเซีย',
            'vi': 'เวียดนาม',
            'ms': 'มาเลย์',
            'es': 'สเปน',
            'fr': 'ฝรั่งเศส',
            'de': 'เยอรมัน',
            'ru': 'รัสเซีย',
            'ar': 'อาหรับ',
            'hi': 'ฮินดี',
            'pt': 'โปรตุเกส',
            'it': 'อิตาลี',
            'nl': 'ดัตช์',
            'unknown': 'ไม่ทราบ'
        }

        return language_names.get(lang_code, lang_code.upper())

    def batch_detect_languages(self, texts: List[str]) -> Dict[str, int]:
        """
        Detect languages in batch and return statistics

        Args:
            texts: List of texts to analyze

        Returns:
            Dictionary with language codes as keys and counts as values
        """
        language_stats = {}

        for text in texts:
            if text and text.strip():
                lang = self.detect_language_enhanced(text)
                language_stats[lang] = language_stats.get(lang, 0) + 1

        return language_stats

def create_enhanced_detector() -> EnhancedLanguageDetector:
    """Factory function to create enhanced language detector"""
    return EnhancedLanguageDetector()

# Test function
if __name__ == "__main__":
    detector = create_enhanced_detector()

    # Test texts
    test_texts = [
        ("这是一个很好的地方，强烈推荐！", "zh-cn"),
        ("這是一個很好的地方，強烈推薦！", "zh-tw"),
        ("香港這個地方不錯，飲茶很好吃", "zh-hk"),
        ("この場所は素晴らしいです！", "ja"),
        ("이 장소는 훌륭합니다!", "ko"),
        ("สถานที่นี้ดีมากครับ", "th"),
        ("This is a great place!", "en"),
        ("Ini adalah tempat yang bagus!", "id"),
        ("Đây là một nơi tuyệt vời!", "vi")
    ]

    print("🧪 Testing Enhanced Language Detection")
    print("=" * 50)

    for text, expected in test_texts:
        detected = detector.detect_language_enhanced(text)
        name = detector.get_language_name(detected)
        expected_name = detector.get_language_name(expected)

        status = "✅" if detected == expected else "❌"
        print(f"{status} {name} | Expected: {expected_name}")
        print(f"   Text: {text[:50]}...")
        print()

    # Test batch detection
    print("📊 Batch Detection Test")
    print("=" * 50)

    batch_texts = [text for text, _ in test_texts] * 3  # Repeat for better stats
    stats = detector.batch_detect_languages(batch_texts)

    print("Language Detection Results:")
    for lang, count in sorted(stats.items(), key=lambda x: x[1], reverse=True):
        name = detector.get_language_name(lang)
        print(f"  {name}: {count}")