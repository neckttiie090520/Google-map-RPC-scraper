# Quick Start: Language Selection

เริ่มใช้งานฟีเจอร์เลือกภาษารีวิว ใน 3 ขั้นตอน

## 🚀 วิธีที่ 1: ทดสอบเร็ว (10 รีวิว)

```bash
# English reviews
python test_language.py en

# Thai reviews
python test_language.py th

# Japanese reviews
python test_language.py ja
```

## 🎯 วิธีที่ 2: Interactive Mode

```bash
python example_language_selection.py
```

จากนั้นเลือกภาษาจากเมนู (1-5)

## 💻 วิธีที่ 3: เขียน Script เอง

### ภาษาอังกฤษ (English)

```python
import asyncio
from src.scraper.production_scraper import create_production_scraper

async def main():
    scraper = create_production_scraper(language="en", region="us")

    result = await scraper.scrape_reviews(
        place_id="YOUR_PLACE_ID",
        max_reviews=100,
        date_range="1year"
    )

    scraper.export_to_csv(result['reviews'], "reviews_EN.csv")

asyncio.run(main())
```

### ภาษาไทย (Thai)

```python
import asyncio
from src.scraper.production_scraper import create_production_scraper

async def main():
    scraper = create_production_scraper(language="th", region="th")

    result = await scraper.scrape_reviews(
        place_id="YOUR_PLACE_ID",
        max_reviews=100,
        date_range="1year"
    )

    scraper.export_to_csv(result['reviews'], "reviews_TH.csv")

asyncio.run(main())
```

## 📋 รหัสภาษาที่ใช้บ่อย

| ภาษา | Code | Region |
|------|------|--------|
| English | `en` | `us` |
| Thai | `th` | `th` |
| Japanese | `ja` | `jp` |
| Chinese | `zh-CN` | `cn` |
| Korean | `ko` | `kr` |

## ❓ FAQ

**Q: รีวิวจะเป็นภาษาที่เลือกทั้งหมดเลยหรือไม่?**
A: ไม่เสมอไป Google จะแปลรีวิวที่มีอยู่ แต่บางรีวิวอาจแสดงเป็นภาษาต้นฉบับ

**Q: Scrape หลายภาษาพร้อมกันได้ไหม?**
A: ต้อง scrape ทีละภาษา ดูตัวอย่างใน `example_language_selection.py`

**Q: ภาษาไหนเหมาะสำหรับ sentiment analysis?**
A: ใช้ภาษาที่ตรงกับกลุ่มเป้าหมาย เช่น ร้านในไทย → ภาษาไทย, นานาชาติ → ภาษาอังกฤษ

## 📖 เอกสารเพิ่มเติม

- [LANGUAGE_SELECTION_GUIDE.md](LANGUAGE_SELECTION_GUIDE.md) - คู่มือฉบับเต็ม
- [README.md](README.md) - เอกสารหลัก

---

**สร้างโดย:** Nextzus
**วันที่:** 2025-11-10
