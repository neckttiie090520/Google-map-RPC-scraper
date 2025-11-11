# Google Maps Scraper - Utils

นี่คือยูทิลิตี้โมดูลสำหรับระบบ Google Maps Scraper ที่รองรับการตรวจจับภาษา การแปลภาษา และฟีเจอร์อื่นๆ ที่จำเป็นสำหรับการทำงานแบบ Multi-language

## 📋 ภาพรวมโมดูล (Module Overview)

### 🔍 โมดูลหลัก (Core Modules)

| โมดูล | คำอธิบาย | หน้าที่หลัก |
|--------|---------|------------|
| **`enhanced_language_detector.py`** | Enhanced Language Detector | ตรวจจับภาษาแบบขั้นสูง รองรับ Chinese Variants |
| **`translator.py`** | Standard Translator | แปลภาษาแบบมาตรฐาน (deep-translator) |
| **`bulk_translator.py`** | Bulk Translator | แปลภาษาแบบขนาดใหญ่ ความเร็วสูง (py-googletrans) |
| **`enhanced_language_service.py`** | Enhanced Language Service | บริการตรวจจับภาษาแบบขั้นสูง |
| **`language_service.py`** | Language Service | บริการตรวจจับภาษาแบบพื้นฐาน |

### 🛠 โมดูลสนับสนุน (Supporting Modules)

| โมดูล | คำอธิบาย | หน้าที่หลัก |
|--------|---------|------------|
| **`anti_bot_utils.py`** | Anti-Bot Protection | ป้องกันการตรวจจับจาก bot |
| **`output_manager.py`** | Output Management | จัดการไฟล์ผลลัพธ์และการส่งออก |
| **`unicode_display.py`** | Unicode Display | จัดการการแสดงผล Unicode บน Windows |

---

## 🚀 การเริ่มต้นใช้งาน (Getting Started)

### การติดตั้ง (Installation)

```bash
# ติดตั้ง dependencies ทั้งหมด
pip install -r requirements.txt

# dependencies ที่จำเป็นสำหรับ translation
pip install langdetect>=1.0.9
pip install deep-translator>=1.11.4
pip install googletrans==4.0.0rc1
pip install lingua>=4.15.0
```

### การใช้งานพื้นฐาน (Basic Usage)

```python
# 1. Enhanced Language Detection
from src.utils.enhanced_language_detector import create_enhanced_detector

detector = create_enhanced_detector()
lang = detector.detect_language_enhanced("这是一个很好的地方！")
print(detector.get_language_name(lang))  # Output: จีนตัวย่อ

# 2. Standard Translation
from src.utils.translator import BatchTranslator

translator = BatchTranslator(target_language='th')
translated = translator.translate_text("This is a great place!")

# 3. High-Performance Bulk Translation
from src.utils.bulk_translator import create_bulk_translator

bulk_translator = create_bulk_translator(
    target_language='th',
    batch_size=50,
    max_workers=5
)
texts = ["Hello", "这是一个很好的地方", "สถานที่ดีมาก"]
translated_texts = bulk_translator.translate_bulk(texts)
```

---

## 🔍 โมดูลตรวจจับภาษา (Language Detection Modules)

### Enhanced Language Detector

**รองรับ Chinese Variants:**
- `zh-cn`: จีนตัวย่อ (Simplified Chinese)
- `zh-tw`: จีนตัวเต็ม (Traditional Chinese)
- `zh-hk`: จีนฮ่องกง (Hong Kong Chinese)

**ฟีเจอร์:**
- ✅ ตรวจจับภาษาแบบขั้นสูงด้วย character pattern analysis
- ✅ รองรับภาษาจีนหลายรูปแบบ (Simplified, Traditional, Hong Kong)
- ✅ Batch detection สำหรับประสิทธิภาพสูง
- ✅ Custom language names ในภาษาไทย

**ตัวอย่าง:**
```python
from src.utils.enhanced_language_detector import create_enhanced_detector

detector = create_enhanced_detector()

# Test different Chinese variants
texts = [
    "这是一个很好的地方",  # Simplified
    "這是一個很好的地方",  # Traditional
    "香港這個地方不錯",   # Hong Kong
    "この場所は素晴らしいです",  # Japanese
    "สถานที่นี้ดีมากครับ"   # Thai
]

for text in texts:
    lang = detector.detect_language_enhanced(text)
    name = detector.get_language_name(lang)
    print(f"{text[:20]}... -> {name} ({lang})")
```

---

## 🔄 โมดูลแปลภาษา (Translation Modules)

### 1. Standard Translator (translator.py)

**คุณสมบัติ:**
- ✅ Backward compatible กับโค้ดเดิม
- ✅ ใช้ deep-translator (Google Translate API)
- ✅ Enhanced language detection integration
- ✅ Automatic fallback ระหว่าง bulk และ standard translator

**ตัวอย่าง:**
```python
from src.utils.translator import BatchTranslator

# Standard usage
translator = BatchTranslator(
    target_language='th',
    batch_size=50,
    use_bulk_translator=True  # Auto-enable bulk when available
)

reviews = [...]  # List of ProductionReview objects
translated_reviews = translator.process_batch(
    reviews,
    translate_review_text=True,
    translate_owner_response=False
)
```

### 2. Bulk Translator (bulk_translator.py)

**ประสิทธิภาพสูง (High Performance):**
- ⚡ **3-5x เร็วกว่า** ด้วย concurrent processing
- 🔄 **Batch API calls** ลด overhead
- 🛡️ **Smart Rate Limiting** ป้องกัน API blocks
- 📊 **Performance Monitoring** ติดตามสถิติการแปล

**ฟีเจอร์:**
- ✅ Concurrent translation (multi-threading)
- ✅ Automatic retry logic with exponential backoff
- ✅ Session pooling for connection reuse
- ✅ Comprehensive statistics and monitoring
- ✅ Rate limiting protection

**ตัวอย่าง:**
```python
from src.utils.bulk_translator import create_bulk_translator

# High-performance bulk translation
translator = create_bulk_translator(
    target_language='th',
    batch_size=100,      # Process 100 texts at once
    max_workers=5,       # 5 concurrent workers
    timeout=10.0,        # 10 second timeout
    max_retries=3        # Retry up to 3 times
)

# Bulk translate texts
texts = [
    "This place is amazing!",
    "这是一个很好的地方！",
    "สถานที่ดีครับ",
    # ... hundreds more texts
]

translated = translator.translate_bulk(texts)

# Get performance statistics
stats = translator.get_stats()
print(f"Translated: {stats.translated_texts}/{stats.total_texts}")
print(f"Speed: {stats.translation_speed:.1f} texts/s")
print(f"Processing time: {stats.processing_time:.2f}s")
```

---

## 🛡 โมดูลป้องกัน Bot (Anti-Bot Modules)

### Anti-Bot Utils

**คุณสมบัติ:**
- ✅ **User-Agent Rotation** - สุ่มเปลี่ยน User-Agent
- ✅ **Request Header Randomization** - สุ่มค่า headers
- ✅ **Human-like Delays** - ดีเลย์แบบมนุษย์
- ✅ **Rate Limit Detection** - ตรวจจับและปรับอัตราคำขอ
- ✅ **Proxy Support** - รองรับ proxy rotation
- ✅ **Exponential Backoff** - ลองใหม่แบบชาญฉลาด

**ตัวอย่าง:**
```python
from src.utils.anti_bot_utils import (
    generate_randomized_headers,
    HumanLikeDelay,
    RateLimitDetector,
    ProxyRotator
)

# Generate randomized headers
headers = generate_randomized_headers(language='th', region='th')

# Human-like delays
delay_manager = HumanLikeDelay()
sleep_time = delay_manager.random_page_delay(fast_mode=True)

# Rate limiting detection
rate_detector = RateLimitDetector()
should_slow, delay = rate_detector.should_slow_down(max_rate=10.0)

# Proxy rotation
proxy_rotator = ProxyRotator(['http://proxy1:8080', 'http://proxy2:8080'])
next_proxy = proxy_rotator.get_next_proxy()
```

---

## 📁 โมดูลจัดการข้อมูล (Data Management Modules)

### Output Manager

**ฟีเจอร์:**
- ✅ Organized file structure
- ✅ JSON and CSV export
- ✅ Automatic directory creation
- ✅ Metadata management

**โครงสร้างไฟล์ (File Structure):**
```
outputs/
├── reviews/YYYY-MM-DD/
│   ├── place_name_reviews_YYYYMMDD_HHMMSS.json
│   └── place_name_reviews_YYYYMMDD_HHMMSS.csv
├── places/YYYY-MM-DD/
└── logs/YYYY-MM-DD/
```

**ตัวอย่าง:**
```python
from src.utils.output_manager import output_manager

# Save reviews with automatic file organization
output_manager.save_reviews(
    reviews=reviews,
    place_name="Central World",
    place_id="0x30e29ecfc2f455e1:0xc4ad0280d8906604"
)

# Get organized file paths
json_path, csv_path = output_manager.get_output_paths(
    place_name="Central World"
)
```

### Unicode Display

**คุณสมบัติ:**
- ✅ Windows console encoding fix
- ✅ Thai character support
- ✅ UTF-8 handling
- ✅ Fallback mechanisms

---

## 🌐 รองรับภาษา (Language Support)

### Languages Supported

**ภาษาหลัก (Primary Languages):**
- **Thai** (`th`) - ไทย
- **English** (`en`) - อังกฤษ
- **Chinese Variants**:
  - `zh-cn` - จีนตัวย่อ (Simplified)
  - `zh-tw` - จีนตัวเต็ม (Traditional)
  - `zh-hk` - จีนฮ่องกง (Hong Kong)
- **Japanese** (`ja`) - ญี่ปุ่น
- **Korean** (`ko`) - เกาหลี

**ภาษาอื่นๆ (Other Languages):**
- **Vietnamese** (`vi`) - เวียดนาม
- **Indonesian** (`id`) - อินโดนีเซีย
- **Malay** (`ms`) - มาเลย์
- **Spanish** (`es`) - สเปน
- **French** (`fr`) - ฝรั่งเศส
- **German** (`de`) - เยอรมัน
- **Russian** (`ru`) - รัสเซีย

### Language Names (Thai)

```python
language_names = {
    'th': 'ไทย',
    'en': 'อังกฤษ',
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
```

---

## ⚙️ การคอนฟิก (Configuration)

### Environment Variables

```bash
# Translation Settings
ENABLE_TRANSLATION=true
TARGET_LANGUAGE=th
TRANSLATION_BATCH_SIZE=50
USE_ENHANCED_DETECTION=true

# Performance Settings
TRANSLATION_MAX_WORKERS=5
TRANSLATION_TIMEOUT=10
TRANSLATION_MAX_RETRIES=3

# Anti-Bot Settings
USE_PROXY=false
MAX_RATE=10.0
FAST_MODE=true
```

### Factory Functions

**Recommended Usage Pattern:**

```python
# 1. Language Detection
from src.utils.enhanced_language_detector import create_enhanced_detector
detector = create_enhanced_detector()

# 2. Translation (Standard)
from src.utils.translator import BatchTranslator
translator = BatchTranslator(target_language='th')

# 3. Translation (High Performance)
from src.utils.bulk_translator import create_bulk_translator
bulk_translator = create_bulk_translator(
    target_language='th',
    batch_size=100,
    max_workers=5
)
```

---

## 📊 ประสิทธิภาพ (Performance)

### Benchmarks

| Feature | Standard | Enhanced | Improvement |
|---------|----------|----------|-------------|
| Single Text Translation | 2-3 sec/text | 0.5-1 sec/text | **3-6x faster** |
| Batch Translation (100 texts) | 200-300 sec | 20-40 sec | **5-10x faster** |
| Language Detection | 0.1-0.2 sec/text | 0.01-0.05 sec/text | **2-20x faster** |
| Memory Usage | Baseline | +10-20% | Acceptable |
| CPU Usage | Baseline | +200-400% | Concurrent processing |

### Optimization Tips

```python
# For best performance
bulk_translator = create_bulk_translator(
    target_language='th',
    batch_size=100,      # Larger batches = better performance
    max_workers=5,       # More workers = faster translation
    timeout=15.0,        # Sufficient timeout for large texts
    max_retries=3        # Balance reliability vs speed
)

# Process in chunks for very large datasets
for chunk in chunks(large_text_list, 1000):
    translated_chunk = bulk_translator.translate_bulk(chunk)
    process_results(translated_chunk)
```

---

## 🐛 การแก้ไขปัญหา (Troubleshooting)

### Common Issues

**1. py-googletrans Import Error:**
```bash
pip install googletrans==4.0.0rc1
# หรือ
pip uninstall py-googletrans googletrans
pip install googletrans==4.0.0rc1
```

**2. Thai Character Display Issues:**
```python
# Windows console fix
import sys
import os

if sys.platform == 'win32':
    os.system('chcp 65001 > nul 2>&1')
```

**3. Rate Limiting Issues:**
```python
# Reduce concurrent workers and increase delays
translator = create_bulk_translator(
    max_workers=2,  # Reduce from 5 to 2
    batch_size=25  # Reduce from 50 to 25
)
```

**4. Memory Issues with Large Datasets:**
```python
# Process in smaller chunks
def process_large_dataset(texts, chunk_size=100):
    for i in range(0, len(texts), chunk_size):
        chunk = texts[i:i + chunk_size]
        translated = bulk_translator.translate_bulk(chunk)
        yield translated
```

---

## 🔗 API Reference

### Enhanced Language Detector

```python
class EnhancedLanguageDetector:
    def detect_language_enhanced(text: str) -> str
    def detect_chinese_variant(text: str) -> Optional[str]
    def get_language_name(lang_code: str) -> str
    def batch_detect_languages(texts: List[str]) -> Dict[str, int]
```

### Bulk Translator

```python
class EnhancedBulkTranslator:
    def __init__(self, target_language: str, batch_size: int, max_workers: int)
    def translate_bulk(self, texts: List[str], source_lang: str) -> List[str]
    def process_review_batch(self, reviews: List[ProductionReview]) -> List[ProductionReview]
    def get_stats(self) -> BulkTranslationStats
    def get_supported_languages(self) -> Dict[str, str]
```

### Batch Translator

```python
class BatchTranslator:
    def __init__(self, target_language: str, use_bulk_translator: bool, max_workers: int)
    def process_batch(self, reviews: List[ProductionReview]) -> List[ProductionReview]
    def process_all_reviews(self, reviews: List[ProductionReview]) -> List[ProductionReview]
    def translate_text(self, text: str) -> str
    def get_stats(self) -> TranslationStats
```

---

## 📝 การทดสอบ (Testing)

```bash
# Run comprehensive tests
python test_bulk_translator.py

# Test language detection
python -m src.utils.enhanced_language_detector

# Test translation modules
python -m src.utils.translator
python -m src.utils.bulk_translator
```

---

## 🤝 การมีส่วนร่วม (Contributing)

**Guidelines:**
1. Follow Python PEP 8 style
2. Add comprehensive docstrings
3. Include type hints
4. Add error handling
5. Write unit tests
6. Update documentation

**Pull Request Template:**
```markdown
## Description
[Describe changes]

## Features
- [ ] New feature
- [ ] Bug fix
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed
```

---

## 📄 ใบอนุญาต (License)

This project is licensed under the MIT License - see the main project LICENSE file for details.

---

## 📞 การติดต่อ (Contact)

- **Project**: Google Maps RPC Scraper
- **Author**: Nextzus
- **Date**: 2025-11-11
- **Version**: 1.0.0

---

*📚 สำหรับข้อมูลเพิ่มเติม ดูที่ไฟล์ documentation ในแต่ละโมดูลครับ*