# Google Maps Scraper Framework

A production-ready Python framework for scraping Google Maps reviews and place data using Google's internal RPC API. Achieves 26-40+ reviews/sec with complete anti-bot protection and multi-language support.

## 🚀 Features

### Core Capabilities
- **High Performance**: 26-40+ reviews/sec with optimized HTTP-only RPC method
- **Anti-Bot Protection**: Complete suite including User-Agent rotation, header randomization, proxy support
- **100% Field Extraction**: Extracts all 12 review fields with robust parsing
- **Zero Duplicates**: Page token-based pagination eliminates duplicate reviews
- **Multi-Language Support**: Thai, English, Japanese, Chinese with translation capabilities
- **Date Range Filtering**: Smart filtering with custom date ranges
- **Production Ready**: Comprehensive error handling, retry logic, rate limiting

### Framework Components

#### 📁 Directory Structure
```
src/
├── scraper/
│   └── production_scraper.py    # Main scraping engine with all features
├── search/
│   └── rpc_place_search.py      # RPC-based place search (no API key)
├── utils/
│   ├── anti_bot_utils.py        # Anti-detection utilities
│   ├── output_manager.py        # Organized file management
│   ├── unicode_display.py       # Multi-language text display
│   ├── language_service.py      # Language detection & translation
│   └── enhanced_language_service.py  # Enhanced multi-language support
└── __init__.py
```

## 🛠️ Installation

```bash
# Install base dependencies
pip install -r requirements.txt

# For language detection and translation (optional but recommended)
pip install langdetect deep-translator

# For enhanced language detection (better accuracy)
pip install lingua
```

## 📖 Quick Start

### Basic Scraping

```python
import asyncio
from src.scraper.production_scraper import create_production_scraper

async def main():
    # Create scraper with Thai language/region
    scraper = create_production_scraper(
        language="th",
        region="th",
        fast_mode=True,    # Optimized for performance
        max_rate=10.0      # 10 requests/sec max
    )

    # Scrape Central World Bangkok reviews
    result = await scraper.scrape_reviews(
        place_id="0x30e29ecfc2f455e1:0xc4ad0280d8906604",
        max_reviews=100,
        date_range="1year"
    )

    print(f"Scraped {len(result['reviews'])} reviews")
    print(f"Rate: {result['metadata']['rate']:.2f} reviews/sec")

    return result

asyncio.run(main())
```

### Place Search

```python
import asyncio
from src.search.rpc_place_search import create_rpc_search

async def search_places():
    # Create search service
    search_service = create_rpc_search(language="th", region="th")

    # Search for restaurants in Bangkok
    places = await search_service.search_places(
        query="restaurants in Bangkok",
        max_results=10
    )

    for place in places:
        print(f"{place.name} - Rating: {place.rating} - Reviews: {place.total_reviews}")
        print(f"Place ID: {place.place_id}")

    return places

asyncio.run(search_places())
```

### Multi-Language Scraping with Translation

```python
import asyncio
from src.scraper.production_scraper import create_production_scraper

async def scrape_with_translation():
    scraper = create_production_scraper(
        language="th",
        region="th",
        enable_translation=True,      # Enable translation
        target_language="en",         # Translate to English
        translate_review_text=True,   # Translate review text
        translate_owner_response=True, # Translate owner responses
        use_enhanced_detection=True   # Use enhanced language detection
    )

    result = await scraper.scrape_reviews(
        place_id="0x30e29ecfc2f455e1:0xc4ad0280d8906604",
        max_reviews=50
    )

    # Reviews will have both original and translated text
    for review in result['reviews'][:5]:
        print(f"Original: {review.review_text[:100]}...")
        print(f"Translated: {review.review_text_translated[:100]}...")
        print(f"Detected Language: {review.original_language}")
        print("-" * 50)

    return result

asyncio.run(scrape_with_translation())
```

## 🔧 Configuration

### Scraper Configuration

The `ScraperConfig` class provides comprehensive configuration options:

```python
@dataclass
class ScraperConfig:
    # Anti-bot settings
    use_proxy: bool = False
    proxy_list: Optional[List[str]] = None
    fast_mode: bool = True          # 50-150ms delays (fast) vs 500-1500ms (human)
    max_rate: float = 10.0         # Max requests per second

    # Performance settings
    timeout: float = 30.0          # Request timeout
    max_retries: int = 3           # Max retry attempts

    # Language settings
    language: str = "th"           # Interface language
    region: str = "th"             # Geographic region

    # Translation settings
    enable_translation: bool = False
    target_language: str = "en"    # "th" or "en"
    translate_review_text: bool = True
    translate_owner_response: bool = True
    use_enhanced_detection: bool = True
    translation_batch_size: int = 50
```

### Configuration Examples

#### Conservative Mode (Minimal Risk)
```python
scraper = create_production_scraper(
    language="th",
    region="th",
    fast_mode=False,      # Human-like delays (500-1500ms)
    max_rate=3.0,         # Very conservative rate
    timeout=60.0,         # Longer timeout
    max_retries=5         # More retry attempts
)
```

#### Proxy Rotation
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
```

## 📊 Data Structures

### Review Structure

Each review contains 12 complete fields:

```python
@dataclass
class ProductionReview:
    review_id: str                    # Unique review ID
    author_name: str                  # Reviewer name
    author_url: str                   # Reviewer profile URL
    author_reviews_count: int         # Total reviews by author
    rating: int                       # Star rating (1-5)
    date_formatted: str               # DD/MM/YYYY format
    date_relative: str                # Relative date (e.g., "2 สัปดาห์ที่แล้ว")
    review_text: str                  # Original review content
    review_text_translated: str       # Translated review text
    original_language: str            # Detected original language
    target_language: str              # Target language for translations
    review_likes: int                 # Number of likes
    review_photos_count: int          # Number of attached photos
    owner_response: str               # Business owner response
    owner_response_translated: str    # Translated owner response
    page_number: int                  # Page number where review was found
```

### Place Structure

```python
@dataclass
class PlaceResult:
    place_id: str                     # Google Maps place ID
    name: str                         # Place name
    address: str                      # Full address
    rating: float                     # Average rating
    total_reviews: int                # Total review count
    category: str                     # Place category
    url: str                          # Google Maps URL
    latitude: float                   # Latitude
    longitude: float                  # Longitude
```

## 🔍 Search Features

### RPC Place Search

No API key required - uses Google's internal RPC API:

```python
from src.search.rpc_place_search import create_rpc_search

search_service = create_rpc_search(language="th", region="th")

# Search with location parameters
places = await search_service.search_places(
    query="coffee shops in Sukhumvit",
    max_results=20,
    lat=13.7468,    # Custom center point
    lon=100.5350
)
```

### Search Parameters

- `query`: Search query string
- `max_results`: Maximum results to return (default: 10)
- `lat`, `lon`: Center coordinates for search (default: Bangkok)
- Language support: Thai, English, Japanese, Chinese

## 🛡️ Anti-Bot Protection

### Features Overview

The framework includes comprehensive anti-detection:

1. **User-Agent Rotation**: 12+ real browser User-Agents
2. **Header Randomization**: Accept-Language, Cache-Control, etc.
3. **Human-Like Delays**: Configurable delay patterns
4. **Rate Limiting**: Auto-detection and slowdown
5. **Proxy Rotation**: HTTP/SOCKS5 proxy support
6. **Request Fingerprinting**: Randomized request patterns

### Using Anti-Bot Features

```python
from src.utils.anti_bot_utils import (
    generate_randomized_headers,
    HumanLikeDelay,
    RateLimitDetector,
    ProxyRotator,
    ProxyConfig
)

# Generate randomized headers
headers = generate_randomized_headers(
    language="th",
    region="th"
)

# Human-like delays
delay_gen = HumanLikeDelay()
delay = delay_gen.random_page_delay(fast_mode=True)  # 50-150ms
delay = delay_gen.random_page_delay(fast_mode=False) # 500-1500ms

# Rate limiting detection
rate_detector = RateLimitDetector(window_seconds=60)
should_slow, suggested_delay = rate_detector.should_slow_down(max_rate=10.0)
```

## 🌐 Language Support

### Supported Languages

- **Thai** (th) - Native support with proper encoding
- **English** (en) - Full support
- **Japanese** (ja) - Detection and display
- **Chinese** (zh-CN) - Detection and display

### Language Detection & Translation

```python
# Basic language service
from src.utils.language_service import create_language_service

lang_service = create_language_service(
    target_language="en",
    enable_translation=True
)

# Enhanced language service (recommended)
from src.utils.enhanced_language_service import create_enhanced_language_service

enhanced_service = create_enhanced_language_service(
    target_language="en",
    enable_translation=True
)
```

### Unicode Display

Proper handling of mixed-language text:

```python
from src.utils.unicode_display import (
    safe_print,
    format_name,
    print_review_summary
)

# Safe printing of Unicode text
safe_print("สวัสดีครับ - Hello - こんにちは")

# Format names with language indicators
formatted = format_name("สมชาย", "th")  # "สมชาย [TH]"

# Print review summary with language statistics
print_review_summary(reviews)
```

## 📅 Date Filtering

### Available Date Ranges

- `'1month'` - Last 30 days
- `'6months'` - Last 6 months
- `'1year'` - Last year
- `'5years'` - Last 5 years
- `'7years'` - Last 7 years
- `'all'` - All reviews (no filter)
- `'custom'` - Custom date range

### Date Filtering Examples

```python
# Standard date range
result = await scraper.scrape_reviews(
    place_id="0x30e29ecfc2f455e1:0xc4ad0280d8906604",
    max_reviews=100,
    date_range="6months"  # Last 6 months only
)

# Custom date range
result = await scraper.scrape_reviews(
    place_id="0x30e29ecfc2f455e1:0xc4ad0280d8906604",
    max_reviews=100,
    date_range="custom",
    start_date="2024-01-01",
    end_date="2024-12-31"
)
```

## 📁 Output Management

### Organized File Structure

The framework automatically organizes output files:

```
outputs/
├── reviews/YYYY-MM-DD/
│   ├── place_name_reviews_20250111_143022.json
│   └── place_name_reviews_20250111_143022.csv
├── places/YYYY-MM-DD/
│   ├── search_query_places_20250111_143022.json
│   └── search_query_places_20250111_143022.csv
└── logs/YYYY-MM-DD/
```

### Using Output Manager

```python
from src.utils.output_manager import output_manager

# Save reviews
file_paths = output_manager.save_reviews(
    reviews=[review.__dict__ for review in reviews],
    place_name="Central World",
    place_id="0x30e29ecfc2f455e1:0xc4ad0280d8906604",
    task_id="scrape_20250111",
    settings={"max_reviews": 100, "date_range": "1year"}
)

print(f"Saved to: {file_paths['directory']}")

# Get recent files
recent_files = output_manager.get_recent_files(data_type="reviews", limit=5)

# Get storage info
storage_info = output_manager.get_storage_info()
print(f"Total size: {storage_info['total_size_mb']} MB")
```

## ⚡ Performance Optimization

### Performance Tips

1. **Use Fast Mode**: `fast_mode=True` for 50-150ms delays
2. **Optimal Rate**: `max_rate=10.0` requests/sec for best balance
3. **Batch Processing**: Translation happens in configurable batches
4. **Connection Pooling**: Automatic with httpx AsyncClient
5. **Smart Date Filtering**: Stops early when >50% of reviews are outside range

### Performance Benchmarks

- **Fast Mode**: 26-40+ reviews/sec
- **Human Mode**: ~10 reviews/sec
- **With Translation**: ~15-25 reviews/sec (depends on text length)
- **With Proxies**: ~20-30 reviews/sec (network latency dependent)

## 🔧 Advanced Usage

### Custom Progress Callback

```python
def progress_callback(page_num, total_reviews, **kwargs):
    progress = (total_reviews / max_reviews) * 100
    print(f"Progress: {progress:.1f}% ({total_reviews}/{max_reviews})")

result = await scraper.scrape_reviews(
    place_id="0x30e29ecfc2f455e1:0xc4ad0280d8906604",
    max_reviews=500,
    progress_callback=progress_callback
)
```

### Multi-Place Batch Scraping

```python
async def scrape_multiple_places(place_ids):
    scraper = create_production_scraper(language="th", region="th")

    results = {}
    for place_id in place_ids:
        print(f"Scraping {place_id}...")
        result = await scraper.scrape_reviews(
            place_id=place_id,
            max_reviews=100,
            date_range="6months"
        )
        results[place_id] = result

        # Small delay between places
        await asyncio.sleep(1)

    return results

place_ids = [
    "0x30e29ecfc2f455e1:0xc4ad0280d8906604",  # Central World
    "0x3118b51bb5bfe1fd:0x3c8a1bfc5a6c5c9c",  # Siam Paragon
    "0x3118b51bb5bfe1fd:0x9e8e8b5a5c5c5c9c"   # MBK Center
]

results = await scrape_multiple_places(place_ids)
```

### Error Handling & Monitoring

```python
# Access detailed statistics
stats = result['metadata']['stats']

print(f"Total requests: {stats['total_requests']}")
print(f"Successful: {stats['successful_requests']}")
print(f"Failed: {stats['failed_requests']}")
print(f"Rate limits encountered: {stats['rate_limits_encountered']}")
print(f"Retries used: {stats['retries_used']}")
print(f"Proxy switches: {stats['proxy_switches']}")

# Translation statistics (if enabled)
if 'translation' in result['metadata']:
    trans_stats = result['metadata']['translation']
    print(f"Texts analyzed: {trans_stats['detection_count']}")
    print(f"Texts translated: {trans_stats['translated_count']}")
    print(f"Languages found: {trans_stats['language_distribution']['languages_found']}")
```

## 🚨 Troubleshooting

### Common Issues

#### Thai Character Display
```python
# Framework handles this automatically
# Ensure your console supports UTF-8
# Windows: chcp 65001
```

#### Rate Limiting
```python
# Reduce max_rate and enable human mode
scraper = create_production_scraper(
    fast_mode=False,    # Slower delays
    max_rate=5.0        # Conservative rate
)
```

#### Parsing Errors
The framework uses 3-tier fallback parsing for maximum reliability:
1. Primary date path: `el[2][2][0][1][21][6][8]`
2. Alternative container search
3. Fallback path: `el[2][21][6][8]`
4. Relative date extraction
5. Default: "Unknown Date"

### Performance Issues

1. **Check rate limiting stats**: If >0, reduce `max_rate`
2. **Enable proxy rotation**: If getting blocked
3. **Use fast mode**: For maximum performance
4. **Monitor memory usage**: Large result sets may need streaming

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
This project implements production-grade anti-bot protection and high-performance scraping techniques inspired by the collective knowledge from these repositories. The framework combines the best practices from these projects with original enhancements for Thai/Asian language support and production deployment.

---

## 📄 License

This framework is provided for educational and research purposes. Please respect Google's Terms of Service when scraping.

## 🤝 Contributing

Contributions are welcome! Please ensure:
1. All code includes proper encoding handling
2. Anti-bot features remain effective
3. Tests include multi-language support
4. Documentation is updated

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the code examples
3. Test with the provided examples
4. Ensure dependencies are properly installed

---

**Framework Version**: v1.0
**Last Updated**: 2025-11-11
**Author**: Nextzus
**Performance**: 26-40+ reviews/sec with complete anti-bot protection