# Language Selection Guide

เลือกภาษาของ Review Text ที่ต้องการ Scrape

## 🌐 Supported Languages

The scraper supports multiple languages for review text:

| Language | Code | Region | Description |
|----------|------|--------|-------------|
| English | `en` | `us` | English reviews |
| Thai | `th` | `th` | Thai reviews (ภาษาไทย) |
| Japanese | `ja` | `jp` | Japanese reviews (日本語) |
| Chinese (Simplified) | `zh-CN` | `cn` | Chinese reviews (中文) |
| Korean | `ko` | `kr` | Korean reviews (한국어) |
| Spanish | `es` | `es` | Spanish reviews (Español) |
| French | `fr` | `fr` | French reviews (Français) |
| German | `de` | `de` | German reviews (Deutsch) |

## 🚀 Quick Start

### Option 1: Interactive Mode

Run the example script and choose your language:

```bash
python example_language_selection.py
```

You'll see a menu:
```
Select language for review text:
1. English (EN)
2. Thai (TH)
3. Japanese (JA)
4. Chinese Simplified (ZH-CN)
5. Scrape ALL languages (will take longer)

Enter your choice (1-5):
```

### Option 2: Programmatic Usage

#### Get English Reviews

```python
import asyncio
from src.scraper.production_scraper import create_production_scraper

async def scrape_english_reviews():
    scraper = create_production_scraper(
        language="en",  # English language
        region="us",    # US region
        fast_mode=True,
        max_rate=10.0
    )

    result = await scraper.scrape_reviews(
        place_id="YOUR_PLACE_ID_HERE",
        max_reviews=100,
        date_range="1year"
    )

    # Export with language indicator
    scraper.export_to_csv(result['reviews'], "reviews_EN.csv")
    scraper.export_to_json(result, "reviews_EN.json")

    return result

# Run
asyncio.run(scrape_english_reviews())
```

#### Get Thai Reviews

```python
import asyncio
from src.scraper.production_scraper import create_production_scraper

async def scrape_thai_reviews():
    scraper = create_production_scraper(
        language="th",  # Thai language
        region="th",    # Thailand region
        fast_mode=True,
        max_rate=10.0
    )

    result = await scraper.scrape_reviews(
        place_id="YOUR_PLACE_ID_HERE",
        max_reviews=100,
        date_range="1year"
    )

    # Export with language indicator
    scraper.export_to_csv(result['reviews'], "reviews_TH.csv")
    scraper.export_to_json(result, "reviews_TH.json")

    return result

# Run
asyncio.run(scrape_thai_reviews())
```

#### Scrape Multiple Languages

```python
import asyncio
from src.scraper.production_scraper import create_production_scraper

async def scrape_multilang():
    place_id = "YOUR_PLACE_ID_HERE"

    languages = [
        {"code": "en", "region": "us", "name": "English"},
        {"code": "th", "region": "th", "name": "Thai"},
        {"code": "ja", "region": "jp", "name": "Japanese"},
    ]

    results = {}

    for lang in languages:
        print(f"Scraping {lang['name']} reviews...")

        scraper = create_production_scraper(
            language=lang["code"],
            region=lang["region"],
            fast_mode=True
        )

        result = await scraper.scrape_reviews(
            place_id=place_id,
            max_reviews=50,
            date_range="6months"
        )

        # Export with language code in filename
        scraper.export_to_csv(result['reviews'], f"reviews_{lang['code'].upper()}.csv")

        results[lang['name']] = result

        # Small delay between languages
        await asyncio.sleep(5)

    return results

# Run
asyncio.run(scrape_multilang())
```

## 📖 How It Works

### Language Parameter (`hl`)

The `language` parameter is sent to Google Maps RPC API as the `hl` (host language) parameter:

```
https://www.google.com/maps/rpc/listugcposts?hl=en&gl=us
```

- `hl=en` - Tells Google to return content in English
- `gl=us` - Tells Google the region/locale (US)

### Region Parameter (`gl`)

The `region` parameter (`gl`) affects:
- Date format
- Number format
- Currency symbols
- Regional content preferences

### Important Notes

1. **Language Availability**: Not all reviews are available in all languages. Google translates reviews when possible, but original language reviews are always shown.

2. **Original Language**: Some reviews may appear in their original language regardless of your language setting if:
   - The review was written in that language originally
   - Google doesn't have a translation available

3. **Mixed Results**: You may get a mix of translated and original language reviews depending on availability.

## 🎯 Best Practices

### For English Reviews (International Audience)

```python
scraper = create_production_scraper(
    language="en",
    region="us",
    fast_mode=True
)
```

### For Thai Reviews (Local Thai Content)

```python
scraper = create_production_scraper(
    language="th",
    region="th",
    fast_mode=True
)
```

### For Multi-Market Analysis

Scrape the same place in multiple languages to:
- Compare sentiment across languages
- Get more complete coverage
- Analyze regional differences

```python
# Scrape in 3 languages for comprehensive analysis
languages = ["en", "th", "ja"]
regions = ["us", "th", "jp"]

for lang, region in zip(languages, regions):
    scraper = create_production_scraper(language=lang, region=region)
    # ... scrape and export
```

## 📁 Output File Organization

When scraping multiple languages, use clear naming:

```python
# Good naming convention
reviews_EN_20251110_143022.csv    # English reviews
reviews_TH_20251110_143022.csv    # Thai reviews
reviews_JA_20251110_143022.csv    # Japanese reviews

# Or organize by directory
outputs/
  en/
    reviews_20251110_143022.csv
  th/
    reviews_20251110_143022.csv
  ja/
    reviews_20251110_143022.csv
```

## 🔧 Configuration Options

All available language codes you can use:

```python
# Western Languages
"en" - English
"es" - Spanish
"fr" - French
"de" - German
"it" - Italian
"pt" - Portuguese
"nl" - Dutch
"pl" - Polish
"ru" - Russian

# Asian Languages
"th" - Thai
"ja" - Japanese
"ko" - Korean
"zh-CN" - Chinese (Simplified)
"zh-TW" - Chinese (Traditional)
"vi" - Vietnamese
"id" - Indonesian
"ms" - Malay

# Middle Eastern Languages
"ar" - Arabic
"he" - Hebrew
"tr" - Turkish
```

Match region codes appropriately:
- `"en"` → `"us"` or `"gb"` (UK)
- `"th"` → `"th"`
- `"ja"` → `"jp"`
- `"zh-CN"` → `"cn"`
- etc.

## ❓ FAQ

**Q: Can I scrape reviews in multiple languages at once?**
A: No, you need to run separate scrapes for each language. Use the multi-language example provided.

**Q: Will all reviews be translated?**
A: Not necessarily. Google shows original language reviews when available, and may provide translations for others.

**Q: Does language affect review count?**
A: Yes, the number of reviews you get may vary by language because Google may filter or prioritize certain reviews based on the language setting.

**Q: Which language should I use for sentiment analysis?**
A: Use the language that matches your target audience. For local Thai businesses, use `"th"`. For international analysis, use `"en"`.

**Q: Can I get the original untranslated text?**
A: The scraper returns whatever Google provides. To ensure original text, you might need to scrape with multiple language settings and compare.

## 🎉 Complete Example

Here's a complete example that scrapes a place in both English and Thai:

```python
import asyncio
from src.scraper.production_scraper import create_production_scraper
from datetime import datetime

async def scrape_bilingual():
    """Scrape reviews in both English and Thai"""

    place_id = "0x30e29ecfc2f455e1:0xc4ad0280d8906604"  # Central World

    # 1. Scrape English reviews
    print("=" * 80)
    print("Scraping ENGLISH reviews...")
    print("=" * 80)

    scraper_en = create_production_scraper(language="en", region="us")
    result_en = await scraper_en.scrape_reviews(
        place_id=place_id,
        max_reviews=100,
        date_range="1year"
    )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    scraper_en.export_to_csv(result_en['reviews'], f"reviews_EN_{timestamp}.csv")

    print(f"✅ English: {len(result_en['reviews'])} reviews")

    # 2. Scrape Thai reviews
    print("\n" + "=" * 80)
    print("Scraping THAI reviews...")
    print("=" * 80)

    scraper_th = create_production_scraper(language="th", region="th")
    result_th = await scraper_th.scrape_reviews(
        place_id=place_id,
        max_reviews=100,
        date_range="1year"
    )

    scraper_th.export_to_csv(result_th['reviews'], f"reviews_TH_{timestamp}.csv")

    print(f"✅ Thai: {len(result_th['reviews'])} reviews")

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"English reviews: {len(result_en['reviews'])}")
    print(f"Thai reviews: {len(result_th['reviews'])}")
    print(f"\nFiles saved:")
    print(f"  - reviews_EN_{timestamp}.csv")
    print(f"  - reviews_TH_{timestamp}.csv")

if __name__ == "__main__":
    asyncio.run(scrape_bilingual())
```

Save this as `scrape_bilingual.py` and run:

```bash
python scrape_bilingual.py
```

---

**Need help?** Check the main README.md or open an issue on GitHub.
