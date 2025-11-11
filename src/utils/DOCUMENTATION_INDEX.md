# Utils Documentation Index

## 📚 Complete Documentation for Utils Directory

นี่คือดัชนี้ของเอกสารครบคมวลทั้งหมดสำหรับ utils directory ของ Google Maps Scraper

---

## 📋 Main Documentation

### [📖 README.md](./README.md)
**Main documentation for the entire utils directory**
- ภาพรวมโมดูลทั้งหมด
- การเริ่มต้นใช้งาน
- ฟีเจอร์หลักและประสิทธิภาพ
- ตัวอย่างการใช้งาน
- การติดตั้งและ dependencies
- การแก้ไขปัญหา

---

## 🔍 Language Detection & Translation

### [🎯 Enhanced Language Detector](./enhanced_language_detector.md)
**Advanced language detection with Chinese variants support**
- รองรับ Chinese variants (zh-cn, zh-tw, zh-hk)
- Character pattern analysis
- Thai language names
- Batch processing
- Performance benchmarks

### [🔄 Translation Modules](./translator.md)
**Complete translation system documentation**
- Standard Translator (translator.py)
- Dual engine support (deep-translator + py-googletrans)
- Backward compatibility
- Review processing integration
- Statistics tracking

### [⚡ Bulk Translator](./bulk_translator.md)
**High-performance translation system**
- 3-5x faster than standard translation
- Concurrent processing
- Rate limiting protection
- Session pooling
- Advanced retry logic
- Performance benchmarks
- Memory optimization

### [🌐 Language Services](./language_services.md)
**Language service implementations comparison**
- Enhanced Language Service (lingua-based)
- Basic Language Service (py-googletrans-based)
- Service selection and fallback
- Performance comparison
- Feature comparison table

---

## 🛡️ Protection & Utilities

### [🛡️ Anti-Bot Utils](./anti_bot_utils.md)
**Comprehensive anti-bot protection system**
- User-Agent rotation
- Header randomization
- Human-like delays
- Rate limiting detection
- Proxy support
- Retry logic with exponential backoff
- Performance optimization
- Integration examples

### [📁 Output Manager](./output_manager.md)
**Organized file management system**
- Date-based directory structure
- JSON and CSV export
- Metadata management
- File naming conventions
- Space management
- Batch processing
- Performance optimization

### [🪟 Unicode Display](./unicode_display.md)
**Unicode character support for Windows**
- Windows console encoding fix
- Thai character display
- Mixed language handling
- File encoding solutions
- Cross-platform compatibility
- Common issues and fixes

---

## 📊 Quick Reference

### 🚀 Performance Comparison

| Module | Standard Performance | Enhanced Performance | Speed Improvement |
|--------|----------------------|--------------------|-------------------|
| Language Detection | 100-200 texts/sec | 500-1000 texts/sec | 5-10x |
| Translation | 2-3 texts/sec | 10-50 texts/sec | 3-25x |
| Bulk Translation | 100-200 texts/min | 1000-3000 texts/min | 10-30x |

### 🔧 Dependencies

| Module | Required Dependencies | Optional Dependencies |
|--------|---------------------|------------------|
| Enhanced Language Detector | Python 3.7+, langdetect | lingua>=4.15.0 |
| Translation Modules | deep-translator, py-googletrans | None |
| Anti-Bot Utils | Python standard library | None |
| Output Manager | Python standard library | pandas, xlsxwriter |
| Unicode Display | Python standard library | None |
| Language Services | py-googletrans or lingua | None |

### 🌍 Language Support

| Service | Languages | Thai Support | Chinese Variants |
|---------|----------|--------------|-----------------|
| Enhanced Detector | 300+ | ✅ Native | ✅ Full Support |
| Basic Detector | 100+ | ⚠️ Basic | ❌ Generic Only |
| Translation Modules | 100+ | ✅ Native | ✅ Full Support |

---

## 🔗 Quick Links

### Installation Commands

```bash
# Core dependencies
pip install langdetect>=1.0.9
pip install deep-translator>=1.11.4
pip install googletrans==4.0.0rc1

# Enhanced detection
pip install lingua>=4.15.0

# All dependencies
pip install -r requirements.txt
```

### Quick Usage Examples

```python
# Enhanced language detection
from src.utils.enhanced_language_detector import create_enhanced_detector
detector = create_enhanced_detector()
lang = detector.detect_language_enhanced("这是一个很好的地方！")

# Standard translation
from src.utils.translator import BatchTranslator
translator = BatchTranslator(target_language='th')
translated = translator.translate_text("Hello world!")

# Bulk translation (high performance)
from src.utils.bulk_translator import create_bulk_translator
bulk_translator = create_bulk_translator(target_language='th', max_workers=5)
translated_texts = bulk_translator.translate_bulk(texts)

# Anti-bot protection
from src.utils.anti_bot_utils import generate_randomized_headers
headers = generate_randomized_headers(language="th", region="th")
```

---

## 📋 Documentation Status

| Document | Status | Last Updated |
|----------|--------|--------------|
| README.md | ✅ Complete | 2025-11-11 |
| enhanced_language_detector.md | ✅ Complete | 2025-11-11 |
| translator.md | ✅ Complete | 2025-11-11 |
| bulk_translator.md | ✅ Complete | 2025-11-11 |
| language_services.md | ✅ Complete | 2025-11-11 |
| anti_bot_utils.md | ✅ Complete | 2025-11-11 |
| output_manager.md | ✅ Complete | 2025-11-11 |
| unicode_display.md | ✅ Complete | 2025-11-11 |

---

## 🎯 Key Features Summary

### ✅ Multi-Language Support
- **Thai** (ไทย) - Native support
- **Chinese Variants** - Simplified (zh-cn), Traditional (zh-tw), Hong Kong (zh-hk)
- **English**, **Japanese**, **Korean** - Full support
- **100+ Additional Languages** - Via enhanced detection

### ⚡ Performance Features
- **Concurrent Processing** - Multi-threaded translation
- **Batch Operations** - Process multiple items efficiently
- **Memory Optimization** - Handle large datasets
- **Rate Limiting** - Smart request management

### 🛡️ Protection Features
- **Anti-Detection** - Advanced bot protection
- **Human-Like Behavior** - Random delays and patterns
- **Proxy Support** - IP rotation and anonymity
- **Retry Logic** - Intelligent error recovery

### 📁 Management Features
- **Organized Storage** - Date-based file organization
- **Multiple Formats** - JSON, CSV, metadata export
- **Unicode Support** - Cross-platform character handling
- **Statistics Tracking** - Comprehensive monitoring

---

## 📞 Getting Help

### Common Issues & Solutions

1. **Chinese detection not working**
   - Use Enhanced Language Detector
   - Install lingua: `pip install lingua>=4.15.0`

2. **Translation performance slow**
   - Switch to Bulk Translator
   - Increase concurrent workers
   - Enable batch processing

3. **Thai characters not displaying**
   - Use Unicode Display module
   - Run: `fix_console_encoding()`

4. **Rate limiting errors**
   - Reduce concurrent workers
   - Increase delays between requests
   - Enable proxy rotation

### Testing Commands

```bash
# Test enhanced detection
python -c "from src.utils.enhanced_language_detector import create_enhanced_detector; print('✅ Enhanced detector works')"

# Test translation modules
python -c "from src.utils.translator import BatchTranslator; print('✅ Translator works')"

# Test bulk translation
python -c "from src.utils.bulk_translator import create_bulk_translator; print('✅ Bulk translator works')"

# Test anti-bot utils
python -c "from src.utils.anti_bot_utils import generate_randomized_headers; print('✅ Anti-bot works')"
```

---

## 📄 License

All documentation is part of the Google Maps RPC Scraper project and follows the same license terms.

---

*📚 สำหรับดูรายละเอียดโดยละเอียดของเอกสารแต่ละโมดูลตามความต้องการใช้งาน*

**Last Updated: 2025-11-11**
**Author: Nextzus**
**Version: 1.0.0**