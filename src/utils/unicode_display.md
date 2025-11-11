# Unicode Display

## Overview

Unicode Display เป็นโมดูลขนาดเล็กสำหรับแก้ไขปัญหาการแสดงผล Unicode บน Windows โดยเฉพาะปัญหาเกี่ยวกับการแสดงผลตัวอักษรไทยและภาษาอื่นๆ ที่ใช้ Unicode บน console ของ Windows

## 🪟 ปัญหาที่แก้ไข (Problems Solved)

### ปัญหาหลัก (Main Issues)

1. **Windows Console Encoding**
   - ปัญหา: Windows cmd/PowerShell default ใช้ CP1252 (Windows-1252)
   - ผล: ตัวอักษรไทยแสดงเป็น ??? หรือตัวอักษรแปลกประกอน

2. **Thai Character Support**
   - ปัญหา: Console ไม่รองรับ Thai Unicode Range (U+0E00-U+0E7F)
   - ผล: ข้อความไทยแสดงผลผิดพลาด

3. **Mixed Language Output**
   - ปัญหา: ข้อความผสมภาษา (ไทย+อังกฤษ) แสดงผลไม่ถูกต้อง
   - ผล: Output มักจะขาดหรือแสดงผลผิด

4. **File Encoding Issues**
   - ปัญหา: บันทึกไฟล์ไม่ถูก encoding
   - ผล: ไฟล์เปิดไม่ได้หรือแสดงผลผิด

## ✨ ฟีเจอร์ (Features)

### 🖥️ Console Encoding Fix
```python
import sys
import os

if sys.platform == 'win32':
    os.system('chcp 65001 > nul 2>&1')
```

### 🔤 Character Rendering
- ✅ Thai character support
- ✅ Mixed language handling
- ✅ Fallback mechanisms
- ✅ Error prevention

### 📁 File Encoding
- ✅ UTF-8 file operations
- ✅ BOM support
- ✅ Cross-platform compatibility

## 📖 API Reference

### Core Functions

#### fix_console_encoding()
แก้ไข Windows console encoding

```python
from src.utils.unicode_display import fix_console_encoding

# Fix console encoding (automatically detects Windows)
fix_console_encoding()

# Now Thai characters will display correctly
print("สวัสดีชาวโลก!")  # Should display correctly
print("这是很好的地方！")   # Should display correctly
print("こんにちは世界！")     # Should display correctly
```

#### safe_print(*args, **kwargs)
Print function ที่รองรับ Unicode อย่างปลอดภัย

```python
from src.utils.unicode_display import safe_print

# Print Unicode text safely
safe_print("สวัสดีชาวโลก")
safe_print("Mixed language: สวัสดี Hello こんにちは")
safe_print("Chinese: 这是一个很好的地方！")

# Works like normal print function
safe_print("Normal text:", variable, sep=" | ", end="\n")
```

#### ensure_utf8_encoding(filepath)
ตรวจสอบและแก้ไข file encoding

```python
from src.utils.unicode_display import ensure_utf8_encoding

# Ensure file is saved with UTF-8 encoding
file_path = "test.txt"

with ensure_utf8_encoding(file_path, mode='w', encoding='utf-8-sig') as f:
    f.write("สวัสดีชาวโลก!")
    f.write("Hello World!")
    f.write("こんにちは世界！")

# File will be properly encoded with UTF-8 BOM for Windows compatibility
```

#### get_console_encoding()
ดู console encoding ปัจจุบัน

```python
from src.utils.unicode_display import get_console_encoding

encoding = get_console_encoding()
print(f"Console encoding: {encoding}")
print(f"Supports Thai: {'UTF-8' in encoding.upper()}")

# Examples:
# Windows (after fix): 'cp65001' or 'utf-8'
# macOS/Linux: 'UTF-8'
# Windows (before fix): 'cp1252'
```

### Utility Functions

#### is_thai_text(text)
ตรวจสอบว่า text มีตัวอักษรไทยหรือไม่

```python
from src.utils.unicode_display import is_thai_text

thai_text = "สวัสดีชาวโลก"
english_text = "Hello World"
mixed_text = "สวัสดี Hello"

print(is_thai_text(thai_text))    # True
print(is_thai_text(english_text)) # False
print(is_thai_text(mixed_text))    # True
```

#### sanitize_for_display(text)
ทำความสะอาด text สำหรับแสดงผลบน console

```python
from src.utils.unicode_display import sanitize_for_display

problematic_text = "สวัสดี\0Hello\t世界\r\n"
clean_text = sanitize_for_display(problematic_text)

print(f"Original: {repr(problematic_text)}")
print(f"Clean: {repr(clean_text)}")
```

#### safe_filename(text)
สร้างชื่อไฟล์ที่ปลอดภัยสำหรับ Unicode

```python
from src.utils.unicode_display import safe_filename

unicode_filename = "รีวิวสถานที่_2024.txt"
safe_name = safe_filename(unicode_filename)

print(f"Original: {unicode_filename}")
print(f"Safe: {safe_name}")
```

## 🧪 การใช้งาน (Usage Examples)

### Basic Usage

```python
from src.utils.unicode_display import (
    fix_console_encoding,
    safe_print,
    get_console_encoding
)

# Fix console encoding at start of program
fix_console_encoding()

# Check current encoding
current_encoding = get_console_encoding()
safe_print(f"Console encoding: {current_encoding}")

# Print Unicode text safely
safe_print("🌏 Welcome to Thai Google Maps Scraper! 🌏")
safe_print("สวัสดีครับ ยินดีต้อนรับ")
safe_print("Mixed language: English + ไทย + 中文 + 日本語")
```

### File Operations

```python
from src.utils.unicode_display import ensure_utf8_encoding, safe_filename

def save_unicode_file(data, filename):
    """Save data with proper UTF-8 encoding"""

    # Create safe filename
    safe_name = safe_filename(filename)

    # Save with UTF-8 encoding and BOM
    with ensure_utf8_encoding(safe_name, mode='w', encoding='utf-8-sig') as f:
        if isinstance(data, dict):
            import json
            json.dump(data, f, ensure_ascii=False, indent=2)
        elif isinstance(data, list):
            import json
            json.dump(data, f, ensure_ascii=False, indent=2)
        else:
            f.write(str(data))

    safe_print(f"✅ Saved to: {safe_name}")
    return safe_name

# Usage
data = {
    "place_name": "สยามพารากอน",
    "description": "เป็นสวนสนานแห่งใหญ่แห่งประเทศไทย",
    "reviews": [
        "สวยงมากครับ",
        "Beautiful temple!",
        "很漂亮！"
    ]
}

save_unicode_file(data, "สวนสนาน_ข้อมูล.json")
```

### Integration with Scraper

```python
from src.utils.unicode_display import fix_console_encoding, safe_print
from src.scraper.production_scraper import ProductionGoogleMapsScraper

class UnicodeSafeScraper(ProductionGoogleMapsScraper):
    """Scraper with Unicode display support"""

    def __init__(self, config=None):
        # Fix console encoding first
        fix_console_encoding()

        super().__init__(config)

        # Override print methods
        self.original_print = print
        self.print = safe_print

    def log_progress(self, message):
        """Log progress with Unicode support"""
        safe_print(f"📊 {message}")

    def log_error(self, error):
        """Log errors with Unicode support"""
        safe_print(f"❌ Error: {error}")

    def log_success(self, message):
        """Log success with Unicode support"""
        safe_print(f"✅ {message}")

# Usage
scraper = UnicodeSafeScraper()

# Test Unicode logging
scraper.log_progress("กำลังดึงข้อมูล จาก Central World...")
scraper.log_success("ดึงข้อมูลสำเร็จแล้ว! ได้รีวิว 150 รายการ")
scraper.log_error("เกิดข้อผิดพลาดในการดึงข้อมูล")
```

### Mixed Language Processing

```python
from src.utils.unicode_display import (
    fix_console_encoding,
    safe_print,
    is_thai_text,
    sanitize_for_display
)

def process_mixed_language_reviews(reviews):
    """Process reviews with mixed languages"""

    # Fix console encoding
    fix_console_encoding()

    thai_count = 0
    english_count = 0
    chinese_count = 0
    other_count = 0

    for i, review in enumerate(reviews, 1):
        text = review.get('review_text', '')

        # Clean text for display
        display_text = sanitize_for_display(text)

        # Detect language
        if is_thai_text(text):
            lang = "Thai 🇹🇭"
            thai_count += 1
        elif any('\u4e00' <= char <= '\u9fff' for char in text):
            lang = "Chinese 🇨🇳"
            chinese_count += 1
        elif text.replace(' ', '').isalpha():
            lang = "English 🇬🇧"
            english_count += 1
        else:
            lang = "Other 🌍"
            other_count += 1

        # Safe print with language detection
        safe_print(f"Review {i}: {lang}")
        safe_print(f"  Text: {display_text[:50]}...")
        safe_print(f"  Author: {review.get('author_name', 'Unknown')}")
        safe_print(f"  Rating: {review.get('rating', 'N/A')}")
        safe_print()

    # Summary
    safe_print("📊 Language Summary:")
    safe_print(f"  Thai: {thai_count} reviews")
    safe_print(f"  English: {english_count} reviews")
    safe_print(f"  Chinese: {chinese_count} reviews")
    safe_print(f"  Other: {other_count} reviews")
    safe_print(f"  Total: {len(reviews)} reviews")

# Usage
reviews = [
    {
        "author_name": "สมชาย",
        "review_text": "สวนสนานสวยงมากครับ แนะนะ",
        "rating": 5
    },
    {
        "author_name": "John",
        "review_text": "Beautiful place with amazing architecture!",
        "rating": 5
    },
    {
        "author_name": "游客",
        "review_text": "很漂亮的地方，值得参观！",
        "rating": 4
    }
]

process_mixed_language_reviews(reviews)
```

### Web Application Integration

```python
from flask import Flask
from src.utils.unicode_display import fix_console_encoding

app = Flask(__name__)

# Fix console encoding for Flask app
fix_console_encoding()

@app.route('/')
def home():
    # Thai text in template
    return """
    <h1>ยินดีต้อนรับสู่ Google Maps Scraper</h1>
    <p>Welcome to Thai Google Maps Scraper!</p>
    """

@app.route('/api/test')
def test_unicode():
    # API endpoint returning Unicode
    return {
        "thai": "สวัสดีชาวโลก",
        "english": "Hello World",
        "chinese": "你好世界",
        "japanese": "こんにちは世界"
    }

if __name__ == '__main__':
    # Console messages will display Thai correctly
    print("🚀 Starting Flask app...")
    print("📝 Thai Unicode support enabled")
    print("🌍 Ready for international characters")

    app.run(debug=True)
```

## ⚙️ การคอนฟิก (Configuration)

### Environment Detection

```python
import sys
import os
import locale

def get_system_info():
    """Get system encoding information"""

    info = {
        "platform": sys.platform,
        "default_encoding": sys.getdefaultencoding(),
        "stdout_encoding": getattr(sys.stdout, 'encoding', 'unknown'),
        "stderr_encoding": getattr(sys.stderr, 'encoding', 'unknown'),
        "file_system_encoding": sys.getfilesystemencoding(),
        "locale_encoding": locale.getpreferredencoding(False)
    }

    return info

def print_system_info():
    """Print system encoding information"""
    from src.utils.unicode_display import fix_console_encoding, safe_print

    fix_console_encoding()

    info = get_system_info()

    safe_print("💻 System Encoding Information:")
    safe_print(f"Platform: {info['platform']}")
    safe_print(f"Default encoding: {info['default_encoding']}")
    safe_print(f"Stdout encoding: {info['stdout_encoding']}")
    safe_print(f"Stderr encoding: {info['stderr_encoding']}")
    safe_print(f"Filesystem encoding: {info['file_system_encoding']}")
    safe_print(f"Locale encoding: {info['locale_encoding']}")

# Usage
print_system_info()
```

### Custom Configuration

```python
# Custom Unicode display configuration
UNICODE_CONFIG = {
    "fix_console": True,           # Automatically fix console encoding
    "safe_print": True,            # Use safe_print for all output
    "utf8_bom": True,              # Add BOM to UTF-8 files
    "fallback_encoding": "utf-8",   # Fallback encoding
    "sanitize_display": True,      # Sanitize text for console display
    "log_unicode_errors": True     # Log Unicode-related errors
}

def apply_unicode_config(config):
    """Apply custom Unicode configuration"""

    if config.get("fix_console", True):
        from src.utils.unicode_display import fix_console_encoding
        fix_console_encoding()

    if config.get("safe_print", True):
        # Override default print (use with caution)
        import builtins
        from src.utils.unicode_display import safe_print
        builtins.print = safe_print

    print("✅ Unicode configuration applied")
    print(f"📝 Config: {config}")

# Usage
apply_unicode_config(UNICODE_CONFIG)
```

## 🐛 การแก้ไขปัญหา (Troubleshooting)

### Common Issues

**1. Thai characters still not displaying**
```python
from src.utils.unicode_display import fix_console_encoding, get_console_encoding

# Try multiple fixes
fix_console_encoding()

# Check if fix worked
encoding = get_console_encoding()
if '65001' not in encoding and 'utf-8' not in encoding.lower():
    print("⚠️ Console encoding fix may not have worked")
    print("Try running in Windows Terminal or PowerShell instead of cmd")
    print("Or set CHCP 65001 manually before running the script")
else:
    print("✅ Console encoding fixed successfully")
```

**2. File encoding issues**
```python
def debug_file_encoding(filepath):
    """Debug file encoding issues"""

    try:
        # Try reading with different encodings
        encodings = ['utf-8-sig', 'utf-8', 'cp1252', 'cp65001']

        for encoding in encodings:
            try:
                with open(filepath, 'r', encoding=encoding) as f:
                    content = f.read()
                print(f"✅ Successfully read with {encoding}")
                print(f"First 100 chars: {content[:100]}")
                return encoding
            except UnicodeDecodeError:
                continue

        print("❌ Could not read file with any encoding")

    except Exception as e:
        print(f"❌ Error reading file: {e}")

# Usage
debug_file_encoding("test_file.txt")
```

**3. Python version issues**
```python
import sys

def check_python_version():
    """Check Python version for Unicode support"""

    version_info = sys.version_info
    print(f"Python version: {version_info.major}.{version_info.minor}.{version_info.micro}")

    if version_info >= (3, 7):
        print("✅ Python 3.7+ - Good Unicode support")
    elif version_info >= (3, 5):
        print("⚠️ Python 3.5-3.6 - Basic Unicode support")
    else:
        print("❌ Python < 3.5 - Limited Unicode support, upgrade recommended")

    # Check for Windows-specific issues
    if sys.platform == 'win32':
        if version_info < (3, 8):
            print("⚠️ Consider Python 3.8+ for better Windows Unicode support")

check_python_version()
```

## 📚 Dependencies

### Required
- Python 3.5+ (for better Unicode support)
- No external dependencies (uses Python standard library only)

### Optional
- `chardet` - For automatic charset detection
- `ftfy` - For fixing Unicode text

### Installation
```bash
# Optional dependencies for enhanced Unicode support
pip install chardet
pip install ftfy
```

## 📄 License

This module is part of the Google Maps RPC Scraper project and follows the same license terms.

---

*💡 Tip: Call `fix_console_encoding()` at the very beginning of your Python script, before any Unicode output.*