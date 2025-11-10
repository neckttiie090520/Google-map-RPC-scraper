# Sort by Newest Guide

คู่มือการใช้งานฟีเจอร์เรียงลำดับรีวิวตามวันที่ (ใหม่สุดก่อน)

## 📋 Overview

ฟีเจอร์ **Sort by Newest** ช่วยให้คุณสามารถเรียงลำดับรีวิวตามวันที่ โดยรีวิวที่ใหม่ที่สุดจะแสดงก่อน ซึ่งมีประโยชน์สำหรับ:

- 📊 **วิเคราะห์ trend ล่าสุด** - ดูความคิดเห็นล่าสุดของลูกค้า
- 🔍 **ตรวจสอบปัญหาใหม่** - เห็นปัญหาที่เกิดขึ้นล่าสุดได้เร็วขึ้น
- 📈 **ติดตามการเปลี่ยนแปลง** - ดูว่าคุณภาพของบริการเปลี่ยนไปอย่างไรเมื่อเวลาผ่านไป
- 🎯 **จัดลำดับความสำคัญ** - ให้ความสำคัญกับ feedback ล่าสุด

## 🚀 Quick Start

### วิธีที่ 1: Basic Usage

```python
import asyncio
from src.scraper.production_scraper import create_production_scraper

async def main():
    scraper = create_production_scraper(language="en", region="us")

    result = await scraper.scrape_reviews(
        place_id="YOUR_PLACE_ID",
        max_reviews=100,
        date_range="1year",
        sort_by_newest=True  # เปิดใช้งาน sorting
    )

    # แสดง 5 รีวิวล่าสุด
    for i, review in enumerate(result['reviews'][:5], 1):
        print(f"{i}. {review.date_formatted}: {review.review_text[:50]}...")

asyncio.run(main())
```

### วิธีที่ 2: Interactive Example

```bash
python example_sort_by_newest.py
```

เลือก:
1. Simple example with sorting (50 reviews)
2. Compare sorted vs unsorted (20 reviews each)

## 📖 Detailed Usage

### Example 1: Get Latest Reviews

```python
import asyncio
from src.scraper.production_scraper import create_production_scraper

async def get_latest_reviews():
    """Get most recent reviews sorted by date"""

    scraper = create_production_scraper(
        language="th",  # Thai language
        region="th",
        fast_mode=True
    )

    result = await scraper.scrape_reviews(
        place_id="0x30e29ecfc2f455e1:0xc4ad0280d8906604",
        max_reviews=50,
        date_range="1month",  # Last month only
        sort_by_newest=True   # Sort by newest first
    )

    # Export sorted reviews
    scraper.export_to_csv(result['reviews'], "latest_reviews.csv")

    # Show newest 10 reviews
    print("10 Most Recent Reviews:")
    for i, review in enumerate(result['reviews'][:10], 1):
        print(f"{i}. Date: {review.date_formatted}")
        print(f"   Rating: {'⭐' * review.rating}")
        print(f"   Text: {review.review_text[:80]}...")
        print()

asyncio.run(get_latest_reviews())
```

### Example 2: Track Recent Changes

```python
async def track_recent_sentiment():
    """Analyze sentiment of recent reviews"""

    scraper = create_production_scraper(language="en", region="us")

    result = await scraper.scrape_reviews(
        place_id="YOUR_PLACE_ID",
        max_reviews=100,
        date_range="6months",
        sort_by_newest=True
    )

    # Analyze first 20 (newest) vs last 20 (oldest) reviews
    newest_20 = result['reviews'][:20]
    oldest_20 = result['reviews'][-20:]

    newest_avg = sum(r.rating for r in newest_20) / len(newest_20)
    oldest_avg = sum(r.rating for r in oldest_20) / len(oldest_20)

    print(f"Newest 20 reviews average: {newest_avg:.2f} ⭐")
    print(f"Oldest 20 reviews average: {oldest_avg:.2f} ⭐")

    if newest_avg > oldest_avg:
        print("✅ Sentiment is improving!")
    elif newest_avg < oldest_avg:
        print("⚠️  Sentiment is declining!")
    else:
        print("→ Sentiment is stable")

asyncio.run(track_recent_sentiment())
```

### Example 3: Find Recent Problems

```python
async def find_recent_problems():
    """Find recent negative reviews"""

    scraper = create_production_scraper(language="th", region="th")

    result = await scraper.scrape_reviews(
        place_id="YOUR_PLACE_ID",
        max_reviews=200,
        date_range="1month",
        sort_by_newest=True
    )

    # Filter low-rating reviews (1-2 stars)
    recent_problems = [
        r for r in result['reviews']
        if r.rating <= 2
    ]

    print(f"Found {len(recent_problems)} low-rating reviews in past month")
    print()

    # Show recent problems
    for i, review in enumerate(recent_problems[:5], 1):
        print(f"Problem #{i}")
        print(f"Date: {review.date_formatted}")
        print(f"Rating: {'⭐' * review.rating}")
        print(f"Review: {review.review_text}")
        print("-" * 80)
        print()

asyncio.run(find_recent_problems())
```

## 🔧 Parameters

### `sort_by_newest` (bool)

- **Default:** `False`
- **Type:** Boolean
- **Description:** เมื่อตั้งเป็น `True` รีวิวจะถูกเรียงตามวันที่จากใหม่ไปเก่า

```python
result = await scraper.scrape_reviews(
    place_id="...",
    max_reviews=100,
    sort_by_newest=True  # เปิดใช้งาน
)
```

## 📊 How It Works

### Sorting Logic

1. **Date Parsing**: ระบบจะ parse วันที่จาก `date_formatted` field (รูปแบบ DD/MM/YYYY)
2. **DateTime Conversion**: แปลงเป็น Python datetime object
3. **Sorting**: เรียงลำดับจากมากไปน้อย (newest first)
4. **Fallback**: รีวิวที่ไม่สามารถ parse วันที่ได้จะถูกวางไว้ท้ายสุด

### Date Format Support

รองรับรูปแบบวันที่:
- ✅ `DD/MM/YYYY` (เช่น 15/11/2024)
- ✅ Validates year range: 1900-2100
- ⚠️  "Unknown Date" จะถูกวางไว้ท้ายสุด

## 💡 Use Cases

### 1. Customer Support Dashboard

```python
async def support_dashboard():
    """Dashboard for customer support team"""

    # Get latest reviews sorted
    scraper = create_production_scraper(language="th", region="th")
    result = await scraper.scrape_reviews(
        place_id="YOUR_PLACE_ID",
        max_reviews=50,
        date_range="1week",
        sort_by_newest=True
    )

    # Show urgent issues (low ratings from past 7 days)
    urgent = [r for r in result['reviews'] if r.rating <= 2]

    print(f"🚨 {len(urgent)} urgent issues to address")
    for review in urgent:
        print(f"- {review.date_formatted}: {review.review_text[:100]}...")
```

### 2. Monthly Report

```python
async def monthly_report():
    """Generate monthly report with recent reviews"""

    scraper = create_production_scraper(language="en", region="us")
    result = await scraper.scrape_reviews(
        place_id="YOUR_PLACE_ID",
        max_reviews=500,
        date_range="1month",
        sort_by_newest=True
    )

    # Statistics
    total = len(result['reviews'])
    avg_rating = sum(r.rating for r in result['reviews']) / total

    # Recent trends (first 100 reviews = most recent)
    recent_100 = result['reviews'][:100]
    recent_avg = sum(r.rating for r in recent_100) / len(recent_100)

    print(f"📊 Monthly Report")
    print(f"Total reviews: {total}")
    print(f"Average rating: {avg_rating:.2f}")
    print(f"Recent trend (last 100): {recent_avg:.2f}")

    # Export
    scraper.export_to_csv(result['reviews'], "monthly_report.csv")
```

### 3. Competitor Analysis

```python
async def compare_competitors():
    """Compare your business vs competitor (recent reviews)"""

    # Your business - recent reviews
    scraper1 = create_production_scraper(language="en", region="us")
    your_reviews = await scraper1.scrape_reviews(
        place_id="YOUR_PLACE_ID",
        max_reviews=100,
        date_range="3months",
        sort_by_newest=True
    )

    # Competitor - recent reviews
    scraper2 = create_production_scraper(language="en", region="us")
    competitor_reviews = await scraper2.scrape_reviews(
        place_id="COMPETITOR_PLACE_ID",
        max_reviews=100,
        date_range="3months",
        sort_by_newest=True
    )

    # Compare recent 50 reviews
    your_recent = your_reviews['reviews'][:50]
    comp_recent = competitor_reviews['reviews'][:50]

    your_avg = sum(r.rating for r in your_recent) / len(your_recent)
    comp_avg = sum(r.rating for r in comp_recent) / len(comp_recent)

    print(f"Your business (recent 50): {your_avg:.2f} ⭐")
    print(f"Competitor (recent 50): {comp_avg:.2f} ⭐")
```

## 🎯 Best Practices

### 1. Always Verify Date Range

เมื่อใช้ `sort_by_newest=True` ควรระบุ `date_range` ที่เหมาะสม:

```python
# ดี - ระบุ date range ชัดเจน
result = await scraper.scrape_reviews(
    place_id="...",
    max_reviews=100,
    date_range="1month",  # เฉพาะเดือนล่าสุด
    sort_by_newest=True
)

# ไม่แนะนำ - ไม่ระบุ date range (จะใช้ default)
result = await scraper.scrape_reviews(
    place_id="...",
    sort_by_newest=True
)
```

### 2. Limit Review Count

เมื่อต้องการดูเฉพาะรีวิวล่าสุด ใช้ `max_reviews` ที่น้อยลง:

```python
# เร็วและมีประสิทธิภาพ
result = await scraper.scrape_reviews(
    place_id="...",
    max_reviews=50,      # เฉพาะ 50 รีวิวล่าสุด
    date_range="1month",
    sort_by_newest=True
)
```

### 3. Combine with Date Range

ใช้ `date_range` และ `sort_by_newest` ร่วมกัน:

```python
# Pattern: Recent trends analysis
result = await scraper.scrape_reviews(
    place_id="...",
    max_reviews=200,
    date_range="6months",  # เฉพาะ 6 เดือนล่าสุด
    sort_by_newest=True    # เรียงจากใหม่ไปเก่า
)

# ตอนนี้ result['reviews'][0] = รีวิวล่าสุด
# และ result['reviews'][-1] = รีวิวเก่าสุด (ในช่วง 6 เดือน)
```

## ⚠️ Important Notes

### Date Parsing

1. **รูปแบบที่รองรับ**: DD/MM/YYYY เท่านั้น
2. **Validation**: ระบบตรวจสอบว่าวันที่อยู่ในช่วง 1900-2100
3. **Fallback**: รีวิวที่มี "Unknown Date" จะถูกวางไว้ท้ายสุด

### Performance

- Sorting ทำงาน **หลัง** scraping เสร็จ (in-memory)
- ไม่มีผลต่อความเร็วในการ scrape
- เพิ่มเวลาประมวลผล ~0.1s สำหรับ 1000 รีวิว

### Metadata

ข้อมูล sorting จะถูกบันทึกใน metadata:

```python
result = await scraper.scrape_reviews(
    place_id="...",
    sort_by_newest=True
)

print(result['metadata']['sort_by_newest'])  # True
```

## 📁 Output Files

เมื่อใช้ `sort_by_newest=True` ไฟล์ output จะมีรีวิวเรียงตามวันที่:

```csv
review_id,author,rating,date,text,...
123,John,5,15/11/2024,Great!,...     # ใหม่สุด
124,Jane,4,14/11/2024,Good,...
125,Bob,3,13/11/2024,Okay,...        # เก่าสุด
```

## 🧪 Testing

### Quick Test

```bash
# รัน example script
python example_sort_by_newest.py

# เลือก option 1 หรือ 2
```

### Manual Verification

หลังจาก scrape ตรวจสอบไฟล์ CSV:
1. เปิดไฟล์ CSV
2. ดูคอลัมน์ `date_formatted`
3. ตรวจสอบว่าวันที่เรียงจากใหม่ไปเก่า

## 🔮 Future Enhancements

Possible improvements:

1. **Multiple Sort Options**
   - Sort by rating (highest first)
   - Sort by helpfulness
   - Sort by length

2. **Custom Sort Function**
   ```python
   result = await scraper.scrape_reviews(
       place_id="...",
       sort_by=lambda r: (r.rating, r.date_formatted)
   )
   ```

3. **Sort Direction**
   ```python
   result = await scraper.scrape_reviews(
       place_id="...",
       sort_by="date",
       sort_direction="desc"  # or "asc"
   )
   ```

---

**Author:** Nextzus
**Date:** 2025-11-10
**Version:** 1.0.0
