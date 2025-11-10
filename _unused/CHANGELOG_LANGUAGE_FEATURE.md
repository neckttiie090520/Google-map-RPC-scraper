# Changelog: Language Selection Feature

## 📅 Date: 2025-11-10

## ✨ New Feature: Multi-Language Review Scraping

เพิ่มความสามารถในการเลือกภาษาของ review text ที่ต้องการ scrape

### 🎯 What's New

1. **Language Selection Support**
   - สามารถเลือกภาษาของรีวิวที่ต้องการได้ (EN, TH, JA, ZH-CN และอื่นๆ)
   - Google จะแปลรีวิวเป็นภาษาที่เลือก (ถ้าสามารถแปลได้)
   - รองรับ 15+ ภาษา

2. **New Files Added**
   - `example_language_selection.py` - Interactive mode สำหรับเลือกภาษา
   - `test_language.py` - Quick test script (10 reviews)
   - `LANGUAGE_SELECTION_GUIDE.md` - คู่มือการใช้งานแบบละเอียด
   - `QUICK_START_LANGUAGE.md` - Quick start guide
   - `CHANGELOG_LANGUAGE_FEATURE.md` - Log การเปลี่ยนแปลง (ไฟล์นี้)

3. **Enhanced Functions**
   - เพิ่ม `example_usage_english()` - ตัวอย่างการ scrape ภาษาอังกฤษ
   - เพิ่ม `example_usage_multilang()` - ตัวอย่างการ scrape หลายภาษา
   - อัปเดต documentation ใน README.md

### 🔧 Technical Details

#### Configuration

ระบบใช้ 2 parameters หลักสำหรับควบคุมภาษา:

1. **language** (`hl` parameter ใน RPC URL)
   - ควบคุมภาษาของ UI และ review text
   - ตัวอย่าง: `"en"`, `"th"`, `"ja"`, `"zh-CN"`

2. **region** (`gl` parameter ใน RPC URL)
   - ควบคุม locale และ regional settings
   - ตัวอย่าง: `"us"`, `"th"`, `"jp"`, `"cn"`

#### RPC URL Format

```
https://www.google.com/maps/rpc/listugcposts?hl={language}&gl={region}
```

ตัวอย่าง:
- English: `?hl=en&gl=us`
- Thai: `?hl=th&gl=th`
- Japanese: `?hl=ja&gl=jp`

#### Code Changes

**File: `src/scraper/production_scraper.py`**

```python
# ที่มีอยู่แล้ว (ไม่ได้เปลี่ยน)
@dataclass
class ScraperConfig:
    language: str = "th"  # รองรับอยู่แล้ว
    region: str = "th"    # รองรับอยู่แล้ว

# เพิ่มใหม่
async def example_usage_english():
    """Example: Scrape reviews in English language"""
    scraper = create_production_scraper(
        language="en",
        region="us",
        fast_mode=True,
        max_rate=10.0
    )
    # ...

async def example_usage_multilang():
    """Example: Scrape same place in multiple languages"""
    languages = [
        {"code": "en", "region": "us", "name": "English"},
        {"code": "th", "region": "th", "name": "Thai"},
        {"code": "ja", "region": "jp", "name": "Japanese"},
        {"code": "zh-CN", "region": "cn", "name": "Chinese"}
    ]
    # ...
```

### 📝 Usage Examples

#### Example 1: Single Language

```python
# Scrape English reviews
scraper = create_production_scraper(language="en", region="us")
result = await scraper.scrape_reviews(place_id="...", max_reviews=100)
```

#### Example 2: Multiple Languages

```python
# Scrape in 3 languages
for lang, region in [("en", "us"), ("th", "th"), ("ja", "jp")]:
    scraper = create_production_scraper(language=lang, region=region)
    result = await scraper.scrape_reviews(place_id="...", max_reviews=50)
    scraper.export_to_csv(result['reviews'], f"reviews_{lang.upper()}.csv")
```

#### Example 3: Interactive Mode

```bash
python example_language_selection.py
# เลือกภาษาจากเมนู 1-5
```

### 📊 Supported Languages

| Language | Code | Region | Support Level |
|----------|------|--------|---------------|
| English | `en` | `us` | ✅ Full |
| Thai | `th` | `th` | ✅ Full |
| Japanese | `ja` | `jp` | ✅ Full |
| Chinese (Simplified) | `zh-CN` | `cn` | ✅ Full |
| Chinese (Traditional) | `zh-TW` | `tw` | ✅ Full |
| Korean | `ko` | `kr` | ✅ Full |
| Spanish | `es` | `es` | ✅ Full |
| French | `fr` | `fr` | ✅ Full |
| German | `de` | `de` | ✅ Full |
| Italian | `it` | `it` | ✅ Full |
| Portuguese | `pt` | `pt` | ✅ Full |
| Russian | `ru` | `ru` | ✅ Full |
| Vietnamese | `vi` | `vn` | ✅ Full |
| Indonesian | `id` | `id` | ✅ Full |
| Malay | `ms` | `my` | ✅ Full |

### ⚠️ Important Notes

1. **Translation Availability**
   - Google แปลรีวิวเมื่อเป็นไปได้ แต่บางรีวิวอาจแสดงเป็นภาษาต้นฉบับ
   - รีวิวที่เขียนเป็นภาษาเดียวกับที่เลือก จะแสดงเป็นต้นฉบับเสมอ

2. **Review Count Differences**
   - จำนวนรีวิวที่ได้อาจแตกต่างกันในแต่ละภาษา
   - เกิดจากการ filter และ prioritize ของ Google

3. **Rate Limiting**
   - แนะนำให้หน่วงเวลา 5 วินาทีระหว่างการ scrape แต่ละภาษา
   - ใช้ `await asyncio.sleep(5)` ระหว่างภาษา

4. **Output Files**
   - แนะนำให้ใส่ language code ในชื่อไฟล์
   - ตัวอย่าง: `reviews_EN.csv`, `reviews_TH.csv`

### 🧪 Testing

**Quick Test (10 reviews):**
```bash
python test_language.py en    # English
python test_language.py th    # Thai
python test_language.py ja    # Japanese
```

**Full Test (50 reviews, interactive):**
```bash
python example_language_selection.py
```

### 📚 Documentation

- **Quick Start:** [QUICK_START_LANGUAGE.md](QUICK_START_LANGUAGE.md)
- **Full Guide:** [LANGUAGE_SELECTION_GUIDE.md](LANGUAGE_SELECTION_GUIDE.md)
- **Main README:** [README.md](README.md) - มีส่วน "Language Selection" ใหม่

### 🎯 Use Cases

1. **International Business Analysis**
   - Scrape English reviews สำหรับ global audience
   - วิเคราะห์ sentiment ในภาษาที่ใช้สื่อสารหลัก

2. **Local Market Research**
   - Scrape Thai reviews สำหรับตลาดไทย
   - เข้าใจ local preferences และ feedback

3. **Multi-Market Comparison**
   - Scrape หลายภาษาพร้อมกัน
   - เปรียบเทียบ sentiment ข้ามภาษา

4. **Machine Learning / NLP**
   - สร้าง multilingual dataset
   - Train sentiment models สำหรับหลายภาษา

### 🔮 Future Enhancements

Possible improvements for future versions:

1. **Auto-detect Language**
   - ตรวจจับภาษาของรีวิวอัตโนมัติ
   - จัดกลุ่มรีวิวตามภาษา

2. **Translation Layer**
   - แปลรีวิวด้วย translation API
   - เก็บทั้งต้นฉบับและแปล

3. **Language Analytics**
   - วิเคราะห์การกระจายของภาษา
   - สถิติภาษาใน dataset

4. **Bulk Multi-Language Export**
   - Export หลายภาษาในครั้งเดียว
   - รูปแบบ multi-sheet Excel

### 🐛 Known Issues

None at this time.

### 🤝 Contributing

หากพบปัญหาหรือมีข้อเสนอแนะ กรุณา:
1. เปิด issue บน GitHub
2. ระบุภาษาที่มีปัญหา
3. แนบ error logs และ screenshots

---

**Author:** Nextzus
**Date:** 2025-11-10
**Version:** 1.0.0
