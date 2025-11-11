# Language Services

## Overview

Language Services ปรวมโมดูลสำหรับการตรวจจับภาษาและจัดการ Multi-language ประกอบด้วย Enhanced Language Service (ขั้นสูง) และ Basic Language Service (พื้นฐาน) เพื่อรองรับความต้องการที่แตกต่างกันในการใช้งาน

## 📚 โมดูลประกอบ (Component Modules)

| โมดูล | ระดับ | คำอธิบาย | Dependencies |
|--------|--------|---------|-------------|
| **`enhanced_language_service.py`** | High | บริการตรวจจับภาษาขั้นสูง | lingua, langdetect |
| **`language_service.py`** | Basic | บริการตรวจจับภาษาพื้นฐาน | py-googletrans |

---

## 🔝 Enhanced Language Service (enhanced_language_service.py)

### Overview

Enhanced Language Service เป็นบริการตรวจจับภาษาขั้นสูงที่ใช้ **lingua** library ซึ่งให้ความแม่นยำสูงและรองรับภาษามากกว่า 300 ภาษาทั่วโลก

### ✨ ฟีเจอร์หลัก (Key Features)

#### 🌍 Extensive Language Support
- ✅ **300+ Languages** รองรับภาษาทั่วโลก
- ✅ **High Accuracy** ความแม่นยำ >95% สำหรับภาษาหลัก
- ✅ **Script Detection** ตรวจจับ script types (Latin, Cyrillic, Arabic, etc.)
- ✅ **Confidence Scoring** ให้คะแนนความมั่นใจ

#### 🎯 Thai & Chinese Optimization
- ✅ **Thai Language Detection** รองรับภาษาไทยอย่างแม่นยำ
- ✅ **Chinese Variants** แยกแยะ Chinese variants (Simplified/Traditional)
- ✅ **Mixed Text Handling** จัดการข้อความผสมภาษา
- ✅ **Custom Language Models** โมเดลสำหรับภาษาเอเชีย

#### 🚀 Performance Features
- ✅ **Fast Processing** ตรวจจับ 1000 ข้อความใน <1 วินาที
- ✅ **Batch Processing** ประมวลผลแบบกลุ่ม
- ✅ **Memory Efficient** ใช้หน่วยความน้อย
- ✅ **Caching Support** แคชผลลัพธ์

### 📖 API Reference

#### Core Classes

**LanguageService** (Enhanced)
```python
from src.utils.enhanced_language_service import (
    create_language_service,
    SupportedLanguage
)

# Create enhanced language service
service = create_language_service()

# Get supported languages
languages = service.get_supported_languages()
print(f"Supported languages: {len(languages)}")

# Detect language with confidence
text = "สวัสดีชาวโลก ยินดีต้อนรับ"
result = service.detect_language(text)

print(f"Language: {result.language}")          # 'th'
print(f"Script: {result.script}")            # 'Thai'
print(f"Confidence: {result.confidence}")      # 0.98
print(f"Probability: {result.probabilities}")  # {'th': 0.98, 'en': 0.02}
```

**SupportedLanguage** Enum
```python
from src.utils.enhanced_language_service import SupportedLanguage

# All supported languages
for lang in SupportedLanguage:
    print(f"{lang.value}: {lang.name}")
    print(f"  Code: {lang.get_iso639_1()}")
    print(f"  Code3: {lang.get_iso639_3()}")
    print(f"  Family: {lang.get_language_family()}")
    print()
```

#### Advanced Usage

**Custom Language Detection**
```python
# Detect with confidence threshold
result = service.detect_language(
    text="This is English text with some 中文 mixed in",
    confidence_threshold=0.8
)

if result.confidence >= 0.8:
    print(f"High confidence detection: {result.language}")
else:
    print(f"Low confidence: {result.language} (confidence: {result.confidence})")

# Detect script type
script = service.detect_script("こんにちは世界")
print(f"Script: {script}")  # 'Japanese'

# Batch detection
texts = [
    "สวัสดีครับ",
    "Hello world",
    "こんにちは",
    "Привет мир"
]

results = service.detect_languages_batch(texts)
for i, result in enumerate(results):
    print(f"Text {i+1}: {result.language} (confidence: {result.confidence})")
```

**Language Filtering**
```python
# Filter by language family
thai_langs = service.get_languages_by_family("Tai")
print(f"Tai family languages: {thai_langs}")

# Filter by region
asian_langs = service.get_languages_by_region("Asia")
print(f"Asian languages: {len(asian_langs)}")

# Check if language is supported
if service.is_language_supported("th"):
    print("Thai is supported")

if service.is_language_supported("zz"):
    print("Unknown language is not supported")
```

### 🧪 การใช้งาน (Usage Examples)

#### Basic Enhanced Detection

```python
from src.utils.enhanced_language_service import create_language_service

# Create enhanced service
service = create_language_service()

# Test various languages
test_texts = [
    "สวัสดีครับ ยินดีต้อนรับ",
    "Hello world! How are you?",
    "这是一个很好的地方！",
    "こんにちは世界！",
    "¡Hola mundo!",
    "Привет мир!",
    "مرحبا بالعالم"
]

print("🌍 Enhanced Language Detection Results:")
print("=" * 50)

for text in test_texts:
    result = service.detect_language(text)

    # Get language details
    lang_obj = SupportedLanguage.from_iso639_1(result.language)

    print(f"Text: {text[:30]}...")
    print(f"Language: {result.language} ({lang_obj.name if lang_obj else 'Unknown'})")
    print(f"Script: {result.script}")
    print(f"Confidence: {result.confidence:.3f}")
    print(f"Family: {lang_obj.get_language_family() if lang_obj else 'Unknown'}")
    print()
```

#### Multi-Language Processing Pipeline

```python
from src.utils.enhanced_language_service import create_language_service
from collections import defaultdict

class MultiLanguageProcessor:
    """Process multi-language content with enhanced detection"""

    def __init__(self):
        self.service = create_language_service()
        self.language_stats = defaultdict(int)

    def process_document(self, document):
        """Process document and categorize by language"""

        # Split document into paragraphs/sentences
        paragraphs = self._split_document(document)

        results = {
            'document_language': None,
            'paragraphs': [],
            'language_distribution': {},
            'mixed_language': False,
            'confidence_score': 0.0
        }

        language_votes = []
        paragraph_results = []

        for i, paragraph in enumerate(paragraphs):
            if len(paragraph.strip()) < 10:
                continue

            # Detect language
            result = self.service.detect_language(paragraph)

            paragraph_result = {
                'index': i,
                'text': paragraph,
                'language': result.language,
                'confidence': result.confidence,
                'script': result.script
            }

            paragraph_results.append(paragraph_result)
            language_votes.append(result.language)
            self.language_stats[result.language] += 1

        # Determine overall document language
        from collections import Counter
        language_counter = Counter(language_votes)

        if language_counter:
            # Most common language
            dominant_lang, count = language_counter.most_common(1)[0]
            results['document_language'] = dominant_lang

            # Calculate confidence
            total_paragraphs = len(paragraph_results)
            results['confidence_score'] = count / total_paragraphs

            # Check if mixed language
            unique_languages = len(set(language_votes))
            results['mixed_language'] = unique_languages > 1

            # Language distribution
            results['language_distribution'] = dict(language_counter)

        results['paragraphs'] = paragraph_results
        return results

    def _split_document(self, document):
        """Split document into meaningful chunks"""
        import re

        # Split by paragraphs, sentences, or lines
        paragraphs = re.split(r'\n\s*\n|\.\s+|\?\s+|\!\s+', document)

        # Filter empty or very short paragraphs
        return [p.strip() for p in paragraphs if len(p.strip()) > 10]

    def get_statistics(self):
        """Get processing statistics"""
        return dict(self.language_stats)

# Usage
processor = MultiLanguageProcessor()

document = """
สวัสดีครับ ยินดีต้อนรับสู่เว็บไซต์ของเรา
Hello everyone! Welcome to our website.
这是一个很棒的网站！
ぜひ当サイトへようこそ！
"""

results = processor.process_document(document)

print("📄 Document Analysis Results:")
print(f"Primary Language: {results['document_language']}")
print(f"Mixed Language: {results['mixed_language']}")
print(f"Confidence Score: {results['confidence_score']:.3f}")
print(f"Language Distribution: {results['language_distribution']}")

print(f"\nParagraph Breakdown:")
for para in results['paragraphs']:
    print(f"  {para['language']} ({para['confidence']:.2f}): {para['text'][:50]}...")

print(f"\nOverall Statistics:")
stats = processor.get_statistics()
for lang, count in sorted(stats.items(), key=lambda x: x[1], reverse=True):
    print(f"  {lang}: {count} paragraphs")
```

#### Language-Aware Content Filtering

```python
from src.utils.enhanced_language_service import create_language_service

class ContentFilter:
    """Filter content by language and script"""

    def __init__(self):
        self.service = create_language_service()
        self.allowed_languages = ['th', 'en', 'ja', 'ko', 'zh']
        self.blocked_scripts = ['Arabic', 'Cyrillic']

    def filter_content(self, content_list):
        """Filter content list based on language and script criteria"""

        filtered_content = []
        blocked_content = []
        language_stats = {}

        for content in content_list:
            if not content or len(content.strip()) < 5:
                continue

            # Detect language
            result = self.service.detect_language(content)

            # Get script
            script = self.service.detect_script(content)

            # Check criteria
            allowed = True
            reason = None

            # Language filter
            if result.language not in self.allowed_languages:
                allowed = False
                reason = f"Language {result.language} not allowed"

            # Script filter
            if script in self.blocked_scripts:
                allowed = False
                reason = f"Script {script} blocked"

            # Confidence filter
            if result.confidence < 0.5:
                allowed = False
                reason = f"Low confidence ({result.confidence})"

            # Categorize
            content_data = {
                'text': content,
                'language': result.language,
                'confidence': result.confidence,
                'script': script,
                'reason': reason
            }

            if allowed:
                filtered_content.append(content_data)
            else:
                blocked_content.append(content_data)

            # Update statistics
            lang = result.language
            language_stats[lang] = language_stats.get(lang, 0) + 1

        return {
            'filtered_content': filtered_content,
            'blocked_content': blocked_content,
            'statistics': language_stats,
            'filter_rate': len(blocked_content) / (len(filtered_content) + len(blocked_content))
        }

    def get_supported_languages(self):
        """Get list of allowed languages with names"""
        supported = []

        for lang_code in self.allowed_languages:
            try:
                lang_obj = SupportedLanguage.from_iso639_1(lang_code)
                supported.append({
                    'code': lang_code,
                    'name': lang_obj.name,
                    'family': lang_obj.get_language_family()
                })
            except:
                supported.append({
                    'code': lang_code,
                    'name': lang_code.upper(),
                    'family': 'Unknown'
                })

        return supported

# Usage
filter = ContentFilter()

# Test content
test_content = [
    "สวัสดีครับ",           # Thai (allowed)
    "Hello world!",          # English (allowed)
    "こんにちは",             # Japanese (allowed)
    "مرحبا بالعالم",          # Arabic (blocked - script)
    "Привет мир",             # Cyrillic (blocked - script)
    "Ola mundo!",             # Portuguese (blocked - language)
    "这是一个测试",           # Chinese (allowed)
    "שלום עולם",             # Hebrew (blocked - script)
    "Too short"               # Too short (ignored)
]

results = filter.filter_content(test_content)

print("🔍 Content Filtering Results:")
print(f"✅ Filtered content: {len(results['filtered_content'])}")
print(f"❌ Blocked content: {len(results['blocked_content'])}")
print(f"📊 Filter rate: {results['filter_rate']:.2%}")

print(f"\n📈 Language Statistics:")
for lang, count in results['statistics'].items():
    print(f"  {lang}: {count} items")

print(f"\n✅ Filtered Content:")
for item in results['filtered_content'][:3]:
    print(f"  {item['language']} ({item['confidence']:.2f}): {item['text'][:30]}...")

print(f"\n❌ Blocked Content:")
for item in results['blocked_content']:
    print(f"  {item['language']} - {item['reason']}")
    print(f"  Text: {item['text'][:30]}...")
```

---

## 🔧 Basic Language Service (language_service.py)

### Overview

Basic Language Service เป็นบริการตรวจจับภาษาแบบพื้นฐานที่ใช้ **py-googletrans** เป็น dependency ให้ฟีเจอร์พื้นฐานสำหรับกรณีที่ต้องการแบบง่ายหรือไม่สามารถติดตั้ง lingua ได้

### ✨ ฟีเจอร์หลัก (Key Features)

- ✅ **Google Translate API** ใช้ Google Translate detection
- ✅ **Basic Language Support** รองรับภาษาหลัก
- ✅ **Lightweight** ไม่ต้องการ dependencies เพิ่มเติม
- ✅ **Easy Integration** ใช้งานง่าย
- ✅ **Fallback Support** สำหรับกรณีที่ Enhanced Service ไม่พร้อมใช้

### 📖 API Reference

```python
from src.utils.language_service import (
    create_language_service,
    SupportedLanguage
)

# Create basic language service
service = create_language_service()

# Basic language detection
text = "สวัสดีครับ"
language = service.detect_language(text)
print(f"Detected language: {language}")

# Get language name
lang_name = service.get_language_name(language)
print(f"Language name: {lang_name}")

# Check if translation is needed
needs_translation = service.is_translation_needed(text, language, target_language='en')
print(f"Needs translation: {needs_translation}")

# Get supported languages
languages = service.get_supported_languages()
print(f"Supported languages: {len(languages)}")
```

### 🧪 การใช้งาน (Usage Examples)

#### Basic Detection

```python
from src.utils.language_service import create_language_service

# Create service
service = create_language_service()

# Test texts
test_texts = [
    "สวัสดีครับ",
    "Hello world",
    "こんにちは",
    "Hola mundo"
]

for text in test_texts:
    lang = service.detect_language(text)
    name = service.get_language_name(lang)
    needs_thai = service.is_translation_needed(text, lang, 'th')

    print(f"Text: {text}")
    print(f"Language: {name} ({lang})")
    print(f"Needs Thai translation: {needs_thai}")
    print()
```

#### Translation Integration

```python
from src.utils.language_service import create_language_service

class SimpleTranslator:
    def __init__(self):
        self.language_service = create_language_service()

    def process_text(self, text, target_language='th'):
        """Process text with language detection"""

        # Detect language
        source_lang = self.language_service.detect_language(text)
        lang_name = self.language_service.get_language_name(source_lang)

        # Check if translation needed
        needs_translation = self.language_service.is_translation_needed(
            text, source_lang, target_language
        )

        result = {
            'original_text': text,
            'source_language': source_lang,
            'language_name': lang_name,
            'target_language': target_language,
            'needs_translation': needs_translation
        }

        # Simulate translation (in real implementation, use translation service)
        if needs_translation:
            result['translated_text'] = f"[Translated from {lang_name} to {target_language}] {text}"
        else:
            result['translated_text'] = text
            result['note'] = f"Text is already in {lang_name}"

        return result

# Usage
translator = SimpleTranslator()

text = "Hello world! How are you today?"
result = translator.process_text(text, target_language='th')

print("🔄 Translation Processing:")
for key, value in result.items():
    print(f"  {key}: {value}")
```

---

## 🔄 Service Selection & Fallback

### Automatic Service Selection

```python
from src.utils.enhanced_language_service import EnhancedLanguageService, create_enhanced_service
from src.utils.language_service import LanguageService, create_language_service

class LanguageServiceManager:
    """Manages multiple language service implementations"""

    def __init__(self):
        self.services = []
        self.active_service = None

        # Try to initialize enhanced service first
        try:
            enhanced_service = create_enhanced_service()
            self.services.append(('enhanced', enhanced_service))
            self.active_service = enhanced_service
            print("✅ Enhanced language service initialized")
        except Exception as e:
            print(f"⚠️ Enhanced service not available: {e}")

        # Always add basic service as fallback
        try:
            basic_service = create_language_service()
            self.services.append(('basic', basic_service))
            if not self.active_service:
                self.active_service = basic_service
                print("✅ Basic language service initialized")
        except Exception as e:
            print(f"❌ Basic service not available: {e}")
            raise RuntimeError("No language service available")

    def detect_language(self, text, confidence_threshold=None):
        """Detect language using the best available service"""
        return self.active_service.detect_language(text, confidence_threshold)

    def get_supported_languages(self):
        """Get supported languages from active service"""
        return self.active_service.get_supported_languages()

    def get_service_info(self):
        """Get information about active service"""
        if isinstance(self.active_service, EnhancedLanguageService):
            return {
                'type': 'enhanced',
                'library': 'lingua',
                'languages': 300,
                'features': ['high_accuracy', 'script_detection', 'confidence_scoring']
            }
        else:
            return {
                'type': 'basic',
                'library': 'py-googletrans',
                'languages': 100,
                'features': ['basic_detection', 'lightweight']
            }

    def switch_service(self, service_type):
        """Manually switch to a specific service"""
        for service_type_name, service in self.services:
            if service_type == service_type_name:
                self.active_service = service
                print(f"✅ Switched to {service_type} service")
                return True

        print(f"❌ Service '{service_type}' not available")
        return False

# Usage
manager = LanguageServiceManager()

# Detect language using best available service
text = "สวัสดีครับ ยินดีต้อนรับ"
result = manager.detect_language(text)

print("🔍 Language Detection Results:")
print(f"Language: {result.language}")
print(f"Confidence: {result.confidence}")

# Get service information
info = manager.get_service_info()
print(f"\n🛠 Active Service:")
print(f"  Type: {info['type']}")
print(f"  Library: {info['library']}")
print(f"  Languages: ~{info['languages']}")
print(f"  Features: {', '.join(info['features'])}")
```

## 📊 การเปรียบเทียบ (Comparison)

| Feature | Enhanced Service | Basic Service |
|---------|----------------|-------------|
| **Library** | lingua | py-googletrans |
| **Languages** | 300+ | 100+ |
| **Accuracy** | Very High (>95%) | Good (>85%) |
| **Performance** | Very Fast | Fast |
| **Dependencies** | lingua | py-googletrans |
| **Memory Usage** | Medium | Low |
| **Script Detection** | ✅ Yes | ❌ No |
| **Confidence Scoring** | ✅ Yes | ❌ No |
| **Language Families** | ✅ Yes | ❌ No |
| **Thai Optimization** | ✅ Yes | ⚠️ Basic |

## 🛠️ Dependencies

### Enhanced Service
```bash
# Required
pip install lingua>=4.15.0

# Optional
pip install langdetect>=1.0.9  # Fallback
```

### Basic Service
```bash
# Required
pip install py-googletrans==4.0.0rc1
pip install httpx>=0.13.3
```

## 🐛 การแก้ไขปัญหา (Troubleshooting)

### Common Issues

**1. Enhanced Service Not Available**
```python
try:
    from src.utils.enhanced_language_service import create_enhanced_service
    service = create_enhanced_service()
except ImportError:
    print("⚠️ Enhanced service not available, falling back to basic service")
    from src.utils.language_service import create_language_service
    service = create_language_service()
```

**2. Language Detection Accuracy**
```python
# Use confidence threshold
result = service.detect_language(text, confidence_threshold=0.7)

if result.confidence < 0.7:
    print(f"⚠️ Low confidence detection: {result.confidence}")
    print("Consider using enhanced service for better accuracy")
```

**3. Mixed Language Text**
```python
# Enhanced service handles mixed text better
mixed_text = "Hello สวัสดี こんにちは"
result = enhanced_service.detect_language(mixed_text)

# Check if confident
if result.confidence > 0.8:
    print(f"Primary language: {result.language}")
else:
    print("Text contains multiple languages - consider processing separately")
```

## 📄 License

These modules are part of the Google Maps RPC Scraper project and follow the same license terms.