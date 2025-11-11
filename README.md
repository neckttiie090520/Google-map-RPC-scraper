# Google Maps RPC Scraper 🗺️

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Framework](https://img.shields.io/badge/Framework-Production%20Ready-brightgreen.svg)]()

**Production-ready Google Maps review scraper using RPC API (No API key required)**

A high-performance, feature-complete web scraping framework for extracting Google Maps reviews and place data using Google's internal RPC API. Achieves 26-40+ reviews/sec with comprehensive anti-bot protection and real-time progress tracking.

---

## ⚠️ System Status Notice

### Translation System: Currently Unavailable 🔴
The automatic translation feature is temporarily **disabled** due to a technical issue:
- **Error**: `'float' object has no attribute 'as_dict'` in translation pipeline
- **Impact**: Translation functions are not working
- **Workaround**: Disable translation in settings temporarily
- **Status**: Team is working on a fix for the next update
- **Other Features**: All other features (scraping, search, provinces) work normally

---

## ✨ Key Features

### Core Scraping Capabilities
- 🚀 **High Performance**: 26-40+ reviews/second in fast mode
- 🔒 **No API Key Required**: Uses Google's internal RPC endpoints
- 📊 **Complete Data Extraction**: 12 fields per review (100% coverage)
- 🌍 **Multi-Language Support**: Thai, English, Japanese, Chinese, and more
- 📅 **Date Range Filtering**: Smart filtering with cutoff detection
- 🔄 **Zero Duplicates**: Page token-based pagination
- ♾️ **Unlimited Mode**: Auto-detect total reviews from place data

### Anti-Bot Protection
- 🎭 **User-Agent Rotation**: 12+ different browser agents
- 🔀 **Header Randomization**: Dynamic request fingerprinting
- 🕐 **Human-Like Delays**: Configurable timing patterns
- 🔄 **Rate Limiting**: Auto-slowdown with exponential backoff
- 🌐 **Proxy Support**: HTTP/SOCKS5 rotation (optional)

### Web Application
- 🖥️ **Modern UI**: Clean, responsive Thai/English interface
- 📊 **Real-Time Progress**: Live updates via Server-Sent Events (SSE)
- 🎯 **Smart Search**: RPC-based place search with autocomplete
- 🏛️ **Thai Provinces Support**: Search by Thailand province with region optimization
- 🌐 **Language-Region Management**: 12+ language-region presets with smart parsing
- 🔤 **Translation Pipeline**: Automatic translation with retry logic and error handling
- 📦 **Multi-Format Export**: JSON, CSV output
- 📈 **Progress Tracking**: Visual progress bars with live stats
- 💾 **Auto-Save**: Organized output management

---

## 🎯 Use Cases

- **Business Intelligence**: Analyze customer feedback and sentiment
- **Market Research**: Compare competitor reviews and ratings
- **Data Analysis**: Extract review data for ML/AI training
- **SEO Analysis**: Monitor place reputation and trends
- **Academic Research**: Study location-based social behavior

---

## 📋 Requirements

- **Python**: 3.8 or higher
- **Dependencies**: Listed in `requirements.txt`
- **OS**: Windows, macOS, Linux
- **Optional**: Proxy servers for enhanced anonymity

---

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/google-maps-rpc-scraper.git
cd google-maps-rpc-scraper/google-maps-scraper-python

# Install dependencies
pip install -r requirements.txt
```

### 2. Run Web Application

```bash
# Start the Flask web server
cd webapp
python app.py

# Open browser to http://localhost:5000
```

### 3. Or Use Programmatically

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
        place_id="0x30e29ecfc2f455e1:0xc4ad0280d8906604",  # Central World Bangkok
        max_reviews=100,
        date_range="1year"
    )

    print(f"Scraped {len(result['reviews'])} reviews")
    print(f"Rate: {result['metadata']['rate']:.2f} reviews/sec")

    return result

# Run
asyncio.run(scrape_example())
```

---

## 📁 Project Structure

```
google-maps-scraper-python/
├── src/
│   ├── scraper/
│   │   ├── production_scraper.py    # Main scraping engine
│   │   └── __init__.py
│   ├── search/
│   │   ├── rpc_place_search.py      # RPC place search
│   │   └── __init__.py
│   └── utils/
│       ├── anti_bot_utils.py        # Anti-detection utilities
│       ├── output_manager.py        # File organization
│       ├── unicode_display.py       # Thai/Unicode handling
│       ├── thai_provinces.py        # Thailand provinces data & search
│       ├── enhanced_language_service.py  # Advanced language detection
│       ├── bulk_translator.py       # Batch translation utilities
│       └── __init__.py
├── webapp/
│   ├── app.py                       # Flask web application
│   ├── templates/                   # HTML templates
│   └── static/                      # CSS, JS, images
├── outputs/                         # Scraped data output
├── test_scraper.py                  # Quick test script
├── requirements.txt                 # Python dependencies
├── .env                             # Configuration (optional)
├── CLAUDE.md                        # Developer documentation
└── README.md                        # This file
```

---

## 🔧 Configuration

### Environment Variables (`.env`)

```bash
# Language & Region
LANGUAGE_REGION=th          # Options: th, en, ja, zh, en-th, en-us, ja-jp, zh-cn
# Full list in webapp/app.py LANGUAGE_REGION_PRESETS

# Scraper Settings
DEFAULT_MAX_REVIEWS=2000    # Max reviews per place (0 = unlimited)
DEFAULT_DATE_RANGE=1year    # Options: 1month, 6months, 1year, 5years, all

# Performance
FAST_MODE=true              # true = 50-150ms delays, false = 500-1500ms
MAX_RATE=10.0               # Max requests per second

# Translation Settings
ENABLE_TRANSLATION=false    # Enable automatic translation
TARGET_LANGUAGE=en          # Target language for translation
TRANSLATE_REVIEW_TEXT=true  # Translate review content
TRANSLATE_REVIEW_METADATA=false # Translate review metadata

# Proxy (Optional)
USE_PROXY=false
PROXY_LIST=                 # Comma-separated proxy URLs
```

### Scraper Configuration

```python
from src.scraper.production_scraper import create_production_scraper

# Factory function (recommended)
scraper = create_production_scraper(
    language="th",
    region="th",
    fast_mode=True,
    max_rate=10.0,
    use_proxy=False,
    timeout=30.0,
    max_retries=3
)
```

---

## 📊 Review Data Structure

Each review contains **12 complete fields**:

```python
@dataclass
class ProductionReview:
    review_id: str               # Unique review ID
    author_name: str             # Reviewer name
    author_url: str              # Reviewer profile URL
    author_reviews_count: int    # Total reviews by author
    rating: int                  # Star rating (1-5)
    date_formatted: str          # DD/MM/YYYY format
    date_relative: str           # Relative date (e.g., "2 สัปดาห์ที่แล้ว")
    review_text: str             # Review content
    review_likes: int            # Number of likes
    review_photos_count: int     # Number of attached photos
    owner_response: str          # Business owner response
    page_number: int             # Page number where found
```

---

## 🎨 Web Application Features

### 1. **Place Search**
- Search places in Thai or English
- View place details: rating, reviews, category
- Select multiple places for batch scraping

### 2. **Scraping Configuration**
- Set max reviews (or unlimited mode)
- Choose date range filters
- Select language/region preferences
- Configure sort order (newest first)

### 3. **Real-Time Monitoring**
- Live progress bars showing reviews/max
- Server-Sent Events (SSE) for instant updates
- Current place and page information
- Console logs with detailed status

### 4. **Results Management**
- View scraped reviews in web interface
- Download as JSON or CSV
- Organized output directory structure
- Automatic metadata generation

### 5. **Thai Provinces Search**
- Search by Thailand province with automatic region optimization
- 15+ major provinces with aliases and search keywords
- Real-time province suggestions and validation
- Enhanced search queries with province context

### 6. **Language-Region Management**
- 12+ language-region presets (th, en-th, en-us, ja-jp, zh-cn, etc.)
- Smart parsing of combined language-region strings
- Automatic language detection and enforcement
- Consistent language settings across pagination

### 7. **Translation Pipeline** ⚠️ Temporarily Unavailable
- ~~Automatic translation with retry logic~~
- ~~Support for review text and metadata translation~~
- ~~Multi-provider translation services integration~~
- **Current Status**: Disabled due to technical issue (see notice above)
- **Workaround**: Disable translation in webapp settings

### 8. **Unlimited Mode**
- Auto-detect total reviews from place data
- Progress bar shows actual vs. total reviews
- Stops automatically when complete
- Displays "(ไม่จำกัด)" indicator

---

## 🔬 Advanced Usage

### Date Range Filtering

```python
# Predefined ranges
result = await scraper.scrape_reviews(
    place_id="...",
    date_range="1year"  # Options: 1month, 6months, 1year, 5years, 7years, all
)

# Custom date range
result = await scraper.scrape_reviews(
    place_id="...",
    date_range="custom",
    start_date="01/01/2024",  # DD/MM/YYYY
    end_date="31/12/2024"
)
```

### Progress Callbacks

```python
def my_progress_callback(page_num, total_reviews):
    print(f"Page {page_num}: {total_reviews} reviews collected")

result = await scraper.scrape_reviews(
    place_id="...",
    max_reviews=1000,
    progress_callback=my_progress_callback
)
```

### Language-Region Configuration

```python
from webapp.app import LANGUAGE_REGION_PRESETS, split_language_region

# Available presets
print(LANGUAGE_REGION_PRESETS)
# Output: {
#     'th': ('th', 'th'),        # Thailand locale
#     'en': ('en', 'th'),        # English language with Thailand locale
#     'en-th': ('en', 'th'),      # Explicit English-Thai combination
#     'en-us': ('en', 'us'),      # US locale
#     'ja': ('ja', 'jp'),        # Japanese
#     'zh': ('zh-CN', 'cn'),    # Chinese simplified
#     # ... more presets
# }

# Parse combined language-region strings
language, region = split_language_region("en-th")  # Returns ('en', 'th')
language, region = split_language_region("ja-jp")  # Returns ('ja', 'jp')
language, region = split_language_region("zh-CN")  # Returns ('zh-CN', 'cn')

# Create scraper with specific preset
scraper = create_production_scraper(
    language="en",
    region="th",  # English language, Thailand region
    fast_mode=True
)
```

### Thai Provinces Search

```python
from src.utils.thai_provinces import (
    get_all_provinces,
    enhance_search_query_with_province,
    get_province_suggestions,
    validate_province_search
)

# Get all available provinces
provinces = get_all_provinces()
print(f"Available provinces: {len(provinces)}")

# Get province data
from src.utils.thai_provinces import get_province_data
province_data = get_province_data("เชียงใหม่")
print(province_data)
# Output: {
#     'region': 'th',
#     'search_keywords': ['โรงแรม', 'ร้านอาหาร', 'ตลาดน้ำ', 'วัด', 'สถานที่ท่องเที่ยว'],
#     'examples': ['โดยติเศรษฐี', 'ตลาดน้ำตำแยง', 'วัดพระธาตุดอยสุเทพ', 'นิมมานเฮมต์'],
#     'aliases': ['chiang mai']
# }

# Enhance search query with province
enhanced_query = enhance_search_query_with_province("โรงแรม", "เชียงใหม่")
print(enhanced_query)  # "โรงแรม จังหวัดเชียงใหม่"

# Validate province search
is_valid, message = validate_province_search("ร้านอาหาร", "เชียงใหม่")
print(f"Valid: {is_valid}, Message: {message}")

# Get province suggestions from partial input
suggestions = get_province_suggestions("เชียง")
print(suggestions)  # ['เชียงใหม่', 'เชียงราย']
```

### Translation Pipeline

```python
# Configure translation settings
config = ScraperConfig(
    language="th",
    region="th",
    # Translation settings
    enable_translation=True,
    target_language="en",
    translate_review_text=True,
    translate_review_metadata=False
)

# Scraper will automatically translate reviews during scraping
scraper = ProductionGoogleMapsScraper(config)

result = await scraper.scrape_reviews(
    place_id="...",
    max_reviews=100
)

# Reviews will include both original and translated text
for review in result['reviews'][:5]:
    print(f"Original: {review.review_text}")
    print(f"Translated: {review.review_text_translated}")  # If translation enabled
```

### Multi-Language Scraping

```python
async def scrape_multilang(place_id):
    languages = [
        {"code": "en", "region": "us"},
        {"code": "th", "region": "th"},
        {"code": "ja", "region": "jp"}
    ]

    results = {}
    for lang in languages:
        scraper = create_production_scraper(
            language=lang["code"],
            region=lang["region"]
        )
        result = await scraper.scrape_reviews(place_id=place_id, max_reviews=100)
        results[lang["code"]] = result

    return results
```

### Proxy Rotation

```python
scraper = create_production_scraper(
    language="th",
    region="th",
    use_proxy=True,
    proxy_list=[
        "http://proxy1.example.com:8080",
        "http://proxy2.example.com:8080",
        "socks5://proxy3.example.com:1080"
    ]
)

result = await scraper.scrape_reviews(place_id="...")
print(f"Proxy switches: {result['metadata']['stats']['proxy_switches']}")
```

---

## 🧪 Testing

### Quick Test

```bash
# Test with Central World Bangkok (1000+ reviews)
python test_scraper.py
```

### Expected Output

```
TESTING PRODUCTION SCRAPER
Testing with Central World Bangkok
Place ID: 0x30e29ecfc2f455e1:0xc4ad0280d8906604
Max reviews: 50

RESULTS
Total reviews scraped: 50
Scraping rate: 26-30 reviews/sec
Time elapsed: ~2 seconds
Zero duplicates: ✓
```

---

## ⚡ Performance Benchmarks

| Mode | Delays | Rate | Use Case |
|------|--------|------|----------|
| **Fast Mode** | 50-150ms | 26-40+ reviews/sec | Production, bulk scraping |
| **Human Mode** | 500-1500ms | ~10 reviews/sec | Ultra-safe, minimal detection |
| **Conservative** | Custom | 3-5 reviews/sec | Maximum stealth |

**Factors affecting performance:**
- Fast mode vs. Human mode: 3-4x speed difference
- Proxy usage: ~10-20% slower (network latency)
- Rate limiting: Auto-slowdown when detected
- Date range filtering: Early termination reduces time

---

## 🛡️ Anti-Bot Strategy

### Detection Avoidance

1. **User-Agent Rotation**: 12+ realistic browser signatures
2. **Header Randomization**: Every request has unique fingerprint
3. **Human-Like Timing**: Random jitter in request intervals
4. **Rate Limiting Detection**: Auto-slowdown before 429 errors
5. **Proxy Rotation**: Switch proxies on rate limit (optional)

### Retry Logic

- **429 (Rate Limited)**: Exponential backoff (5s, 10s, 20s...) + proxy switch
- **5xx (Server Error)**: Exponential backoff (2s, 4s, 8s...)
- **Timeout**: Exponential backoff (1s, 2s, 4s...)
- **Max Retries**: Configurable (default: 3)

---

## 📖 API Reference

### Main Functions

#### `create_production_scraper()`
Factory function to create scraper instance.

**Parameters:**
- `language` (str): Language code (e.g., "th", "en", "ja")
- `region` (str): Region code (e.g., "th", "us", "jp")
- `fast_mode` (bool): Enable fast delays (default: True)
- `max_rate` (float): Max requests/second (default: 10.0)
- `use_proxy` (bool): Enable proxy rotation (default: False)
- `proxy_list` (List[str]): List of proxy URLs (optional)
- `timeout` (float): Request timeout in seconds (default: 30.0)
- `max_retries` (int): Max retry attempts (default: 3)

**Returns:** `ProductionGoogleMapsScraper` instance

#### `scraper.scrape_reviews()`
Scrape reviews from a place.

**Parameters:**
- `place_id` (str): Google Maps place ID (required)
- `max_reviews` (int): Maximum reviews to scrape (default: 10000, 0 = unlimited)
- `date_range` (str): Date filter ("1month", "6months", "1year", "5years", "7years", "all", "custom")
- `start_date` (str): Custom start date in DD/MM/YYYY (for date_range="custom")
- `end_date` (str): Custom end date in DD/MM/YYYY (for date_range="custom")
- `sort_by_newest` (bool): Sort by date (default: True)
- `progress_callback` (callable): Callback function(page_num, total_reviews)

**Returns:** Dict with keys:
- `reviews` (List[ProductionReview]): Scraped reviews
- `metadata` (Dict): Scraping metadata and stats

### RPC Place Search

```python
from src.search.rpc_place_search import create_rpc_search

# Create search service
search = create_rpc_search(language="th", region="th")

# Search places
places = await search.search_places("ข้าวซอยนิมมาน", max_results=10)

# Each place contains:
# - place_id, name, address, rating, total_reviews, category, url, latitude, longitude
```

### Thai Provinces API

```python
# All provinces data
from src.utils.thai_provinces import THAI_PROVINCES, get_all_provinces
provinces = get_all_provinces()  # List of province names

# Province data and utilities
from src.utils.thai_provinces import (
    get_province_data,           # Get province information
    enhance_search_query_with_province,  # Add province to search query
    get_province_suggestions,    # Get suggestions from partial input
    validate_province_search,    # Validate search parameters
    get_popular_search_terms     # Get popular search combinations
)

# Example: Search with province enhancement
query = "โรงแรม"
province = "เชียงใหม่"
enhanced_query = enhance_search_query_with_province(query, province)
# Returns: "โรงแรม จังหวัดเชียงใหม่"
```

### Webapp API Endpoints

The Flask web application provides REST API endpoints:

#### Thai Provinces API
- `GET /api/provinces` - List all available provinces
- `GET /api/provinces/suggestions?q=<query>` - Get province suggestions
- `POST /api/provinces/validate` - Validate province search

#### Search API
- `POST /api/search` - Search places with province support
- `POST /api/search/autocomplete` - Get search suggestions

#### Settings API
- `GET /api/settings` - Get current settings
- `POST /api/settings` - Update settings (language, translation, etc.)

#### Tasks API
- `GET /api/tasks` - List all scraping tasks
- `GET /api/tasks/<task_id>` - Get specific task details
- `DELETE /api/tasks/<task_id>` - Delete a task

---

## 🐛 Troubleshooting

### Windows Thai Character Issues

**Problem**: Thai characters display as �����

**Solution**:
```bash
# Set console to UTF-8
chcp 65001

# Or run Python with UTF-8 encoding
set PYTHONIOENCODING=utf-8
python app.py
```

### Rate Limiting

**Problem**: Getting 429 errors or rate limit warnings

**Solutions:**
1. Reduce `max_rate` in config (try 5.0 or 3.0)
2. Enable `use_proxy` with proxy rotation
3. Switch to `fast_mode=False` (human mode)
4. Check `stats['rate_limits_encountered']` in results

### Parsing Errors

**Problem**: Some reviews missing fields

**Solutions:**
1. Google may have changed response structure
2. Check date parsing strategies first (most fragile)
3. Enable debug output in `production_scraper.py`
4. Test with multiple places to identify variations

### Performance Issues

**Problem**: Scraping is slow

**Solutions:**
1. Ensure `fast_mode=True` is enabled
2. Check network latency (especially with proxies)
3. Verify `max_rate` setting (default 10.0)
4. Monitor rate limiting auto-slowdown

### Translation Pipeline Errors

**Problem**: `'float' object has no attribute 'as_dict'` error

**Current Issue**: The translation retry logic is encountering a data type error where a float value is being treated as a review object.

**Workaround:**
1. Disable translation temporarily: `enable_translation=False`
2. Check Flask logs for detailed error traces
3. The issue is in the translation queue processing - fix in progress

### Thai Provinces Not Found

**Problem**: Province search returns "จังหวัด ... ไม่พบในระบบ"

**Solutions:**
1. Check exact province spelling in Thai
2. Use aliases (e.g., "chiang mai" for "เชียงใหม่")
3. Verify province is in the THAI_PROVINCES dictionary
4. Use `/api/provinces/suggestions` endpoint for autocomplete

### Language-Region Parsing Issues

**Problem**: Language-region settings not applied correctly

**Solutions:**
1. Use proper format: "en-th", "ja-jp", "zh-cn"
2. Check LANGUAGE_REGION_PRESETS for supported combinations
3. Verify split_language_region() output
4. Test with individual language and region parameters

### Webapp 404 Errors

**Problem**: Cannot access webapp pages, getting 404 errors

**Solutions:**
1. Check if Flask app is running on correct port (try 5001 instead of 5000)
2. Ensure only one Flask instance is running
3. Verify URL path matches registered routes
4. Check for indentation errors in app.py

---

## 📚 Documentation

- **[README.md](README.md)**: This file - Overview and quick start
- **[CLAUDE.md](CLAUDE.md)**: Comprehensive developer documentation
- **[requirements.txt](requirements.txt)**: Python dependencies
- **[.env.example](.env.example)**: Configuration template

---

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/google-maps-rpc-scraper.git

# Install dependencies
pip install -r requirements.txt

# Run tests
python test_scraper.py

# Make changes and test thoroughly
```

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## ⚠️ Legal Disclaimer

This tool is provided for **educational and research purposes only**. Users are responsible for:

- Complying with Google's Terms of Service
- Respecting robots.txt and rate limits
- Using scraped data ethically and legally
- Obtaining necessary permissions for commercial use

The authors assume **no liability** for misuse of this software.

---

## 🙏 Acknowledgments

This project stands on the shoulders of these amazing open-source projects:

### Core Dependencies
- **[py-googletrans](https://github.com/ssut/py-googletrans)** by ssut - Free Google Translate library for text translation
- **[lingua-py](https://github.com/pemistahl/lingua-py)** by pemistahl - Accurate language detection library supporting 75+ languages
- **[deep-translator](https://github.com/nidhaloff/deep-translator)** - Flexible multi-provider translation library

### Inspiration & Reference
- **[google-maps-scraper](https://github.com/gosom/google-maps-scraper)** by gosom - Reference implementation and Go-based Google Maps scraper
- **[google-maps-pb-decoder](https://github.com/serpapi/google-maps-pb-decoder)** by serpapi - Protocol Buffer decoder for Google Maps responses
- **[botasaurus](https://github.com/omkarcloud/botasaurus)** by omkarcloud - Anti-bot techniques and web scraping patterns

### Browser Automation
- **[playwright](https://github.com/microsoft/playwright)** by Microsoft - Reliable browser automation (inspired anti-bot techniques)

### Special Thanks
- Thai language support for Chiang Mai culinary tourism research
- Community feedback and contributions
- Built with Python, Flask, and httpx

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/google-maps-rpc-scraper/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/google-maps-rpc-scraper/discussions)
- **Email**: your.email@example.com

---

## 🗺️ Roadmap

- [ ] Concurrent request processing (40+ reviews/sec)
- [ ] CAPTCHA solving integration (CapSolver)
- [ ] Redis-based distributed task queue
- [ ] Advanced stealth features (Canvas/WebGL fingerprinting)
- [ ] RESTful API mode
- [ ] Docker containerization
- [ ] Real-time monitoring dashboard

---

**Made with ❤️ by Nextzus**

**Star ⭐ this repo if you find it useful!**
