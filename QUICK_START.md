# Quick Start Guide 🚀

Get started with Google Maps RPC Scraper in 5 minutes!

---

## Prerequisites

- **Python 3.8+** installed
- **pip** package manager
- **Git** (for cloning the repository)

---

## Step 1: Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/google-maps-rpc-scraper.git

# Navigate to project directory
cd google-maps-rpc-scraper/google-maps-scraper-python

# Install dependencies
pip install -r requirements.txt
```

---

## Step 2: Configuration (Optional)

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your preferred settings
# (Optional - defaults work great!)
```

**Default settings:**
- Language: Thai (th)
- Max Reviews: 2000
- Date Range: 1 year
- Fast Mode: Enabled

---

## Step 3: Run Web Application

```bash
# Start the Flask server
cd webapp
python app.py

# Open your browser to:
# http://localhost:5000
```

---

## Step 4: Scrape Your First Reviews

### Option A: Using Web Interface

1. **Search for a place**:
   - Enter place name (e.g., "Central World Bangkok")
   - Click "ค้นหา" (Search)

2. **Select place**:
   - Click on the place you want to scrape
   - Click "เลือก" (Select)

3. **Configure settings** (optional):
   - Set max reviews (or leave unlimited)
   - Choose date range
   - Select language/region

4. **Start scraping**:
   - Click "เริ่มดึงข้อมูล" (Start Scraping)
   - Watch real-time progress!

5. **Download results**:
   - Click "ดูผลลัพธ์" (View Results)
   - Download as JSON or CSV

### Option B: Using Python Code

```python
import asyncio
from src.scraper.production_scraper import create_production_scraper

async def scrape_example():
    # Create scraper
    scraper = create_production_scraper(
        language="th",
        region="th",
        fast_mode=True
    )

    # Scrape reviews
    result = await scraper.scrape_reviews(
        place_id="0x30e29ecfc2f455e1:0xc4ad0280d8906604",  # Central World
        max_reviews=100,
        date_range="1year"
    )

    print(f"Scraped {len(result['reviews'])} reviews")
    return result

# Run
asyncio.run(scrape_example())
```

---

## Step 5: Quick Test

```bash
# Run test script (from project root)
python test_scraper.py

# Should see:
# ✓ 50 reviews scraped
# ✓ 26-30 reviews/sec
# ✓ Zero duplicates
```

---

## Common Use Cases

### 1. Scrape All Reviews (Unlimited Mode)

**Web UI:**
- Leave "จำนวนรีวิวสูงสุด" empty or set to 0
- Scraper will auto-detect total reviews from place

**Python:**
```python
result = await scraper.scrape_reviews(
    place_id="...",
    max_reviews=0  # or None
)
```

### 2. Filter by Date Range

**Web UI:**
- Select date range from dropdown
- Options: 1 month, 6 months, 1 year, 5 years, 7 years, all

**Python:**
```python
result = await scraper.scrape_reviews(
    place_id="...",
    date_range="6months"  # or "1year", "all", etc.
)
```

### 3. Custom Date Range

**Web UI:**
- Select "กำหนดเอง" (Custom)
- Enter start and end dates (DD/MM/YYYY)

**Python:**
```python
result = await scraper.scrape_reviews(
    place_id="...",
    date_range="custom",
    start_date="01/01/2024",
    end_date="31/12/2024"
)
```

### 4. Multi-Language Scraping

```python
# Scrape in English
scraper_en = create_production_scraper(language="en", region="us")
result_en = await scraper_en.scrape_reviews(place_id="...")

# Scrape in Thai
scraper_th = create_production_scraper(language="th", region="th")
result_th = await scraper_th.scrape_reviews(place_id="...")

# Scrape in Japanese
scraper_ja = create_production_scraper(language="ja", region="jp")
result_ja = await scraper_ja.scrape_reviews(place_id="...")
```

---

## Finding Place IDs

### Method 1: Web UI Search

1. Open web application
2. Search for place name
3. Place ID shown in search results

### Method 2: Google Maps URL

1. Go to Google Maps
2. Search for place
3. Look at URL: `https://www.google.com/maps/place/.../@...`
4. Place ID format: `0x...` (hexadecimal string)

### Method 3: Using RPC Search

```python
from src.search.rpc_place_search import create_rpc_search

search = create_rpc_search(language="th", region="th")
places = await search.search_places("Central World Bangkok", max_results=5)

for place in places:
    print(f"{place.name}: {place.place_id}")
```

---

## Output Files

Scraped data saved to `outputs/` directory:

```
outputs/
└── YYYYMMDD_HHMMSS_taskid/
    ├── reviews.json      # Full review data
    ├── reviews.csv       # CSV export
    ├── metadata.json     # Scraping stats
    └── settings.json     # Configuration used
```

### JSON Structure

```json
{
  "review_id": "unique_id",
  "author_name": "John Doe",
  "author_url": "https://...",
  "author_reviews_count": 42,
  "rating": 5,
  "date_formatted": "15/11/2024",
  "date_relative": "2 weeks ago",
  "review_text": "Great place!",
  "review_likes": 10,
  "review_photos_count": 3,
  "owner_response": "Thank you!",
  "page_number": 1
}
```

---

## Troubleshooting

### Windows Thai Characters Issue

**Problem:** Thai characters show as �����

**Solution:**
```bash
# Set console to UTF-8
chcp 65001

# Or set environment variable
set PYTHONIOENCODING=utf-8
```

### Rate Limiting Errors

**Problem:** Getting 429 errors

**Solution:**
```python
# Reduce rate in .env
MAX_RATE=5.0
FAST_MODE=false

# Or in code
scraper = create_production_scraper(
    fast_mode=False,  # Use human mode
    max_rate=5.0      # Slower rate
)
```

### Import Errors

**Problem:** `ModuleNotFoundError`

**Solution:**
```bash
# Ensure you're in project root
pwd  # Should end with /google-maps-scraper-python

# Reinstall dependencies
pip install -r requirements.txt

# Or use virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

---

## Performance Tips

### 1. Fast Mode (Default)
- **Speed**: 26-40+ reviews/sec
- **Risk**: Low (with anti-bot protection)
- **Use**: Production scraping

### 2. Human Mode (Conservative)
- **Speed**: ~10 reviews/sec
- **Risk**: Minimal
- **Use**: Ultra-safe scraping

### 3. Date Range Filtering
- **Benefit**: Stops early when reviews outside range
- **Speed**: Faster for recent reviews
- **Use**: When you only need recent data

### 4. Unlimited Mode
- **Benefit**: Auto-detects total reviews
- **Speed**: Scrapes until complete or limit reached
- **Use**: When you want all reviews

---

## Next Steps

1. **Read Full Documentation**: See [README.md](README.md)
2. **Explore Advanced Features**: Check [CLAUDE.md](CLAUDE.md)
3. **Customize Settings**: Edit `.env` file
4. **Add Features**: See [CONTRIBUTING.md](CONTRIBUTING.md)
5. **Report Issues**: Use [GitHub Issues](https://github.com/yourusername/google-maps-rpc-scraper/issues)

---

## Example Places to Try

### High Review Count
- **Central World Bangkok**: `0x30e29ecfc2f455e1:0xc4ad0280d8906604`
- **Siam Paragon**: Search via web UI

### Thai Restaurants
- **Khao Soi Nimman**: Search "ข้าวซอยนิมมาน"
- **Som Tam Nua**: Search "ส้มตำนัว"

### Tourist Attractions
- **Grand Palace Bangkok**: Search "พระบรมมหาราชวัง"
- **Wat Pho**: Search "วัดโพธิ์"

---

## Need Help?

- **Documentation**: [README.md](README.md), [CLAUDE.md](CLAUDE.md)
- **Issues**: [GitHub Issues](https://github.com/yourusername/google-maps-rpc-scraper/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/google-maps-rpc-scraper/discussions)

---

**Happy Scraping! 🎉**

Star ⭐ the repo if you find it useful!
