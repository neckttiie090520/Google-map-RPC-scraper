# CLAUDE.md

This file provides comprehensive guidance to Claude Code (claude.ai/code) when working with this repository.

## Project Overview

Google Maps RPC Scraper - Production-ready Python web scraper for extracting Google Maps reviews and place data using Google's internal RPC API (no API key required). Achieves 26-40+ reviews/sec with complete anti-bot protection.

**Architecture:** Standalone Python application with archived Flask web UIs. Core scraping engine designed as library modules with complete integration of production features from project 005.

**Key Features:**
- High-performance scraping (26-40+ reviews/sec)
- Complete anti-bot protection (User-Agent rotation, header randomization, proxy support)
- 100% field extraction (12 fields per review)
- 3-tier date parsing fallback strategy
- Zero-duplicate pagination with page token management
- Date range filtering with smart cutoff detection
- Multi-language support (Thai, English, Japanese, Chinese)
- Production-ready with rate limiting, retry logic, exponential backoff

## Development Commands

### Running the Scraper

```bash
# Install dependencies
pip install -r requirements.txt

# Run test script (recommended for testing)
python test_scraper.py

# Direct scraper usage (programmatic)
python -m src.scraper.production_scraper

# Test place search
python -m src.search.rpc_place_search
```

**Note:** There is NO active Flask web application in the main directory. The `run.py` script attempts to import `app.py` which doesn't exist. Flask UIs have been archived to `_ui_archive/`.

### Testing the Scraper

Use `test_scraper.py` for quick testing:
```bash
python test_scraper.py
```

This tests Central World Bangkok (place_id: `0x30e29ecfc2f455e1:0xc4ad0280d8906604`) with:
- 50 reviews max
- Fast mode enabled
- Thai language/region
- 1 year date range

Expected performance: 26-30 reviews/sec with zero duplicates.

## Architecture Overview

### Core Modules Structure

```
src/
├── scraper/
│   └── production_scraper.py    # Main scraping engine with all features
├── search/
│   └── rpc_place_search.py      # RPC-based place search
└── utils/
    ├── anti_bot_utils.py        # Anti-detection utilities
    └── output_manager.py        # File organization
```

### Production Scraper (`src/scraper/production_scraper.py`)

**Key Classes:**
- `ProductionGoogleMapsScraper` - Main scraper with complete feature integration
- `ScraperConfig` - Configuration dataclass for all settings
- `ProductionReview` - Complete review data structure (12 fields)

**RPC Method Details:**
- Endpoint: `https://www.google.com/maps/rpc/listugcposts`
- Protocol: GET with `pb` (Protocol Buffer) parameter
- Response: JSON with `)]}'` prefix (must be stripped)
- Pagination: Uses page tokens from `data[1]`

**pb Parameter Format:**
```
!1m6!1s{place_id}!6m4!4m1!1e1!4m1!1e3!2m2!1i20!2s{page_token}!5m2!1s...!7e81!8m9!...
```

**Review Data Structure (100% Complete Fields):**
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
    review_text: str                  # Review content
    review_likes: int                 # Number of likes
    review_photos_count: int          # Number of attached photos
    owner_response: str               # Business owner response
    page_number: int                  # Page number where review was found
```

**Review Parsing Strategy:**
The scraper navigates deeply nested arrays using `safe_get()` method:
- Review ID: `el[0]`
- Author name: `el[1][4][5][0]`
- Author URL: `el[1][4][2][0]`
- Author reviews count: `el[1][4][15][1]`
- Rating: `el[2][0][0]`
- Review text: `el[2][15][0][0]`
- Review likes: `el[2][16]`
- Review photos count: `len(el[2][22])` if exists
- Owner response: `el[2][19][0][1]`

**Date Extraction (3-Tier Fallback Strategy):**

This is critical for robust date parsing when Google's response structure varies:

1. **Primary Path: `el[2][2][0][1][21][6][8]`**
   - Returns array: `[year, month, day]`
   - Validates: 2000 ≤ year ≤ 2100, 1 ≤ month ≤ 12, 1 ≤ day ≤ 31
   - Formats as: `DD/MM/YYYY`

2. **Alternative Container: `el[2][2][i][1][21][6][8]`**
   - Searches first 5 elements of `el[2][2]` array
   - Uses same validation as primary path
   - Fallback when primary path is empty

3. **Fallback Path: `el[2][21][6][8]`**
   - Final attempt to find date array
   - Same validation and formatting

4. **Relative Date: `el[2][1]`**
   - Used when no absolute date found
   - Returns Thai relative strings (e.g., "2 สัปดาห์ที่แล้ว")
   - Sets `date_formatted = "Unknown Date"`

5. **Default: "Unknown Date"**
   - Used when all strategies fail

**Pagination with Page Tokens:**
```python
# Extract next page token from response
next_page_token = data[1] if len(data) > 1 and isinstance(data[1], str) else None

# Use in next request
reviews, next_page_token = await scraper.fetch_rpc_page(
    client, place_id, page_num, page_token
)

# Stop when no token
if not next_page_token:
    break
```

This ensures zero duplicates and proper pagination through all available reviews.

**Performance Optimization:**
- Fast mode: 50-150ms delays between requests
- Target: 26-40+ reviews/sec
- Uses `httpx.AsyncClient` with connection pooling
- Auto-slowdown when rate limiting detected
- Connection pool: max 10 connections, max 5 keepalive

**Date Range Filtering:**
- Implemented in `is_review_within_date_range()` method
- Parses DD/MM/YYYY format from `date_formatted` field
- Stops scraping when >50% of page reviews are outside range
- Options: '1month', '6months', '1year', '5years', '7years', 'all'
- Smart cutoff detection prevents unnecessary API calls

**Duplicate Detection:**
- Uses set-based tracking: `seen_review_ids`
- Checks every review before adding to results
- Reports duplicate counts in console output
- Critical for data quality

### Anti-Bot Protection (`src/utils/anti_bot_utils.py`)

**This is THE critical feature that makes the scraper production-ready.**

**Features:**
- User-Agent rotation (12+ agents across Chrome, Firefox, Edge, Safari)
- Request header randomization (Accept-Language, Cache-Control, Pragma)
- Human-like delays with jitter
- Rate limiting detection with auto-slowdown
- Proxy rotation support (HTTP/SOCKS5)
- Request fingerprint randomization

**Key Classes:**

**1. `HumanLikeDelay`**
```python
class HumanLikeDelay:
    def random_page_delay(self, fast_mode=True):
        if fast_mode:
            return random.uniform(0.05, 0.15)  # 50-150ms for fast mode
        else:
            return random.uniform(0.5, 1.5)    # 500-1500ms for human mode
```
- Fast mode: Optimized for performance (50-150ms)
- Human mode: More cautious (500-1500ms)
- Random jitter prevents pattern detection

**2. `RateLimitDetector`**
```python
class RateLimitDetector:
    def should_slow_down(self, max_rate=10.0):
        """Returns (should_slow, delay_seconds)"""
        current_rate = len(self.requests) / self.window_seconds
        if current_rate > max_rate:
            delay = (current_rate / max_rate) * 0.5
            return True, min(delay, 5.0)  # Cap at 5 seconds
        return False, 0
```
- Tracks requests in 60-second rolling window
- Auto-slowdown when exceeding max_rate
- Prevents 429 rate limit errors

**3. `ProxyRotator`**
```python
class ProxyRotator:
    def get_next_proxy(self):
        proxy = self.proxies[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.proxies)
        return proxy
```
- Round-robin proxy rotation
- Switches on rate limit detection
- Supports HTTP and SOCKS5 proxies

**4. `generate_randomized_headers()`**
```python
def generate_randomized_headers(base_headers=None):
    headers.update({
        'User-Agent': random.choice(USER_AGENTS),
        'Accept-Language': get_random_accept_language(),
        'Referer': 'https://www.google.com/',
        'Accept': 'application/json, text/plain, */*',
        'Cache-Control': random.choice(['no-cache', 'no-store', 'max-age=0']),
        'Pragma': 'no-cache',
    })
```
- Called for EVERY request
- Rotates 12+ User-Agent variants
- Randomizes Accept-Language and Cache-Control

**Usage Pattern:**
```python
# Create config with anti-bot settings
config = ScraperConfig(
    fast_mode=True,
    max_rate=10.0,
    use_proxy=False,
    timeout=30.0
)

# Create scraper with config
scraper = ProductionGoogleMapsScraper(config)

# Anti-bot features are automatically applied to all requests
```

### ScraperConfig Dataclass

**Complete Configuration Management:**
```python
@dataclass
class ScraperConfig:
    """Complete scraper configuration"""
    # Anti-bot settings
    use_proxy: bool = False
    proxy_list: Optional[List[str]] = None
    fast_mode: bool = True
    max_rate: float = 10.0

    # Performance settings
    timeout: float = 30.0
    max_retries: int = 3

    # Language settings
    language: str = "th"
    region: str = "th"
```

This dataclass pattern provides:
- Type safety for all configuration
- Default values for production use
- Easy override for specific use cases
- Centralized configuration management

### Place Search (`src/search/rpc_place_search.py`)

**Key Class:** `RpcPlaceSearch`

**RPC Search Method:**
- Endpoint: `https://www.google.com/search`
- Parameters: `tbm=map`, `pb` (Protocol Buffer viewport data)
- Extracts: place_id, name, address, rating, reviews, category, coordinates

**Response Types:**
1. **Direct Result** (single place): `["place_name", [place_data_array...]]`
2. **List Results** (multiple places): Nested in `data[0][1]` array

**Extraction Strategy:**
- Uses `_safe_get()` for navigating nested arrays
- Multiple fallback paths for finding place_id
- Go-style extraction (`_extract_go_style_data`) matching indices from reference implementation
- Recursive search (`_find_place_data_in_structure`) as ultimate fallback

**Key Indices (List Results):**
- Place ID: `business[10]` (DataID)
- Name: `business[11]`
- Rating: `business[4][7]`
- Review count: `business[4][8]`
- Address: `business[2]` (array of parts)
- Coordinates: `business[9][2]` (lat), `business[9][3]` (lon)
- Categories: `business[13]`

### Output Management (`src/utils/output_manager.py`)

**Directory Structure:**
```
outputs/
├── reviews/YYYY-MM-DD/
│   ├── place_name_reviews_YYYYMMDD_HHMMSS.json
│   └── place_name_reviews_YYYYMMDD_HHMMSS.csv
├── places/YYYY-MM-DD/
└── logs/YYYY-MM-DD/
```

**Global Instance:** `output_manager` singleton available for import

## Important Implementation Details

### Windows Encoding Handling

All Python files include UTF-8 encoding fix at the top:
```python
if sys.platform == 'win32':
    os.system('chcp 65001 > nul 2>&1')
```
This is **critical** for Thai character support on Windows.

### Safe Navigation Pattern

Always use `safe_get()` method for nested arrays:
```python
value = self.safe_get(data, 2, 15, 0, 0, default="")
```
This prevents crashes on missing/malformed data and is essential for production stability.

### Retry Logic with Exponential Backoff

**Sophisticated retry strategy for different error types:**
```python
# 429 (Rate Limited)
backoff_time = (2 ** attempt) * 5  # 5s, 10s, 20s, ...
await asyncio.sleep(backoff_time)
# Also switches proxy if available

# 5xx (Server Error)
backoff_time = (2 ** attempt) * 2  # 2s, 4s, 8s, ...

# Timeout
backoff_time = (2 ** attempt) * 1  # 1s, 2s, 4s, ...

# Max retries: Configurable via ScraperConfig.max_retries (default: 3)
```

This ensures maximum reliability without wasting time on permanent failures.

### Date Parsing Robustness

**When modifying date parsing:**
1. Test with multiple places (different response structures)
2. Always maintain fallback strategies (minimum 3 tiers)
3. Validate year range (2000-2100) to avoid false positives
4. Support both DD/MM/YYYY and relative date formats
5. Never calculate dates from current time for formatted dates
6. Use "Unknown Date" as final fallback, not calculated dates

**Critical:** Future dates (2025+) in the response are NOT a bug - this is how Google's API currently returns data. The `date_relative` field provides accurate relative timing.

## Factory Function Pattern

**Recommended way to create scraper instances:**
```python
from src.scraper.production_scraper import create_production_scraper

scraper = create_production_scraper(
    language="th",
    region="th",
    fast_mode=True,
    max_rate=10.0,
    use_proxy=False,
    proxy_list=None,
    timeout=30.0,
    max_retries=3
)
```

This provides:
- Clean API for scraper creation
- Type-safe parameter passing
- Sensible defaults
- Easy configuration override

## Common Development Tasks

### Adding New Review Fields

1. Identify field path using debug output
2. Add extraction in `parse_review()` method using `safe_get()`
3. Add field to `ProductionReview` dataclass
4. Update `to_dict()` method if needed
5. Update CSV export headers in `output_manager.py`

### Modifying Rate Limiting

Adjust in `ScraperConfig`:
```python
config = ScraperConfig(
    max_rate=5.0,        # Maximum requests/second (default: 10.0)
    fast_mode=False,     # Use human-like delays (default: True)
    timeout=30.0         # Request timeout in seconds
)
```

- Conservative: `max_rate=5.0`, `fast_mode=False` (safer, slower)
- Aggressive: `max_rate=10.0`, `fast_mode=True` (faster, more risk)
- Ultra-safe: `max_rate=3.0`, `fast_mode=False` (minimum risk)

### Adding Proxy Support

```python
config = ScraperConfig(
    use_proxy=True,
    proxy_list=[
        "http://proxy1.example.com:8080",
        "http://proxy2.example.com:8080",
        "socks5://proxy3.example.com:1080"
    ]
)
scraper = ProductionGoogleMapsScraper(config)
```

The scraper will automatically:
- Rotate through proxies on each request
- Switch proxy on rate limit (429)
- Track proxy switches in stats

### Debugging Response Structure

Uncomment debug output in:
- `production_scraper.py`: `parse_review()` method
- Add print statements for `el` structure
- `rpc_place_search.py`: `_parse_search_results()` method

Example debug code:
```python
# In parse_review()
print(f"DEBUG: Full el structure: {json.dumps(el, indent=2, ensure_ascii=False)}")
```

## Usage Examples

### Basic Usage (Thai, Fast Mode)
```python
import asyncio
from src.scraper.production_scraper import create_production_scraper

async def main():
    scraper = create_production_scraper(
        language="th",
        region="th",
        fast_mode=True,
        max_rate=10.0
    )

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

### With Proxy Rotation
```python
scraper = create_production_scraper(
    language="th",
    region="th",
    fast_mode=True,
    max_rate=10.0,
    use_proxy=True,
    proxy_list=[
        "http://proxy1:8080",
        "http://proxy2:8080"
    ]
)

result = await scraper.scrape_reviews(
    place_id="0x30e29ecfc2f455e1:0xc4ad0280d8906604",
    max_reviews=100
)
```

### Multi-Language Scraping
```python
async def scrape_multilang(place_id, max_reviews=50):
    languages = [
        {"code": "en", "region": "us", "name": "English"},
        {"code": "th", "region": "th", "name": "Thai"},
        {"code": "ja", "region": "jp", "name": "Japanese"}
    ]

    results = {}
    for lang in languages:
        scraper = create_production_scraper(
            language=lang["code"],
            region=lang["region"],
            fast_mode=True
        )

        result = await scraper.scrape_reviews(
            place_id=place_id,
            max_reviews=max_reviews
        )

        results[lang["name"]] = result

    return results
```

### Conservative Mode (Minimal Risk)
```python
scraper = create_production_scraper(
    language="th",
    region="th",
    fast_mode=False,    # Human-like delays (500-1500ms)
    max_rate=3.0,       # Very conservative rate
    timeout=60.0,       # Longer timeout
    max_retries=5       # More retry attempts
)

result = await scraper.scrape_reviews(
    place_id="0x30e29ecfc2f455e1:0xc4ad0280d8906604",
    max_reviews=1000,
    date_range="all"
)
```

## Performance Benchmarks

Based on project 005 evolution and current implementation:

### Current Performance (v1_framework_integration)
- **Fast Mode**: 26-30 reviews/sec
- **Human Mode**: ~10 reviews/sec
- **Zero Duplicates**: ✅ Confirmed
- **Date Parsing**: 3-tier fallback working
- **Field Extraction**: 100% complete (12/12 fields)

### Project 005 Historical Performance
- **Browser-based**: 4-5 reviews/sec (initial implementation)
- **HTTP-only**: 23.04 reviews/sec (removed browser overhead)
- **HTTP-only optimized**: 37.83 reviews/sec (anti-bot + fast mode)
- **Target with concurrency**: 40+ reviews/sec (future enhancement)

### Performance Factors
1. **Fast mode vs Human mode**: 3-4x speed difference
2. **Proxy usage**: ~10-20% slower (network latency)
3. **Rate limiting**: Auto-slowdown when detected
4. **Date range filtering**: Stops early, reduces total time
5. **Connection pooling**: Reuses connections (faster)

## Known Issues

### Flask App Missing

The `run.py` script references `app.py` which doesn't exist in the main directory. Flask applications have been moved to `_ui_archive/`. To run web UI:
```bash
python _ui_archive/original_ui/app.py
# OR
python _ui_archive/kanit_redesign_ui/app-kanit.py
```

### httpx vs aiohttp

`requirements.txt` lists `aiohttp` but code uses `httpx`. Update requirements:
```txt
httpx>=0.25.2
```

### Review Pagination Limitation

Google typically stops pagination at 1000-2000 reviews regardless of implementation. This is a Google API limitation, not a scraper limitation.

### Future Dates in Response

Google's API sometimes returns future dates (2025+). This is NOT a bug in the scraper - it's how the API currently returns data. The `date_relative` field provides accurate relative timing.

## Testing Strategy

### Test Places

**Primary Test Place: Central World Bangkok**
- Place ID: `0x30e29ecfc2f455e1:0xc4ad0280d8906604`
- Known to have 1000+ reviews
- Mixed Thai/English content
- Good for testing date parsing
- Reliable response structure

### Verification Steps

1. **UTF-8 Encoding**: Thai characters should display correctly
2. **Date Parsing**: All 3 strategies should be tested
3. **Zero Duplicates**: Check with `seen_review_ids` tracking
4. **Rate Limiting**: Monitor `stats['rate_limits_encountered']`
5. **Field Completeness**: Verify all 12 fields are extracted
6. **Pagination**: Confirm page tokens are working
7. **Output Files**: Check both JSON and CSV formats

### Test Script Usage

```bash
python test_scraper.py
```

Expected output:
```
TESTING PRODUCTION SCRAPER
Testing with Central World Bangkok
Place ID: 0x30e29ecfc2f455e1:0xc4ad0280d8906604
Max reviews: 50

RESULTS
Total reviews scraped: 50
Scraping rate: 26-30 reviews/sec
Time elapsed: ~2 seconds
```

## Production Considerations

### Performance Tuning

**Fast mode** (Recommended for most use cases):
```python
config = ScraperConfig(
    fast_mode=True,      # 50-150ms delays
    max_rate=10.0        # 10 requests/sec max
)
```
- Achieves 26-40+ reviews/sec
- Low risk with proper anti-bot protection
- Suitable for production use

**Human mode** (Ultra-safe):
```python
config = ScraperConfig(
    fast_mode=False,     # 500-1500ms delays
    max_rate=5.0         # 5 requests/sec max
)
```
- Achieves ~10 reviews/sec
- Minimal detection risk
- Use when extra caution needed

### Error Handling

All requests wrapped in try-except with:
- Specific handling for 429, 5xx status codes
- Fallback values for missing data (`default=""` or `default=0`)
- Graceful degradation when parsing fails
- Comprehensive error logging

### Memory Management

No database, all task state in-memory. For long-running production:
- Implement task cleanup after completion
- Consider Redis for distributed task tracking
- Monitor memory usage with large result sets
- Use streaming output for very large scrapes

### Rate Limit Handling

The scraper automatically:
1. Tracks request rate in 60-second rolling window
2. Auto-slows down when approaching max_rate
3. Switches proxy on 429 errors
4. Uses exponential backoff for retries
5. Reports rate limit stats in final output

Monitor `stats['rate_limits_encountered']` - if > 0, consider:
- Reducing max_rate
- Enabling proxy rotation
- Using human mode instead of fast mode

## Dependencies

**Critical:**
- `httpx>=0.25.0` - Async HTTP client with HTTP/2 support
- `asyncio` - Core async support (built-in)

**Current requirements.txt needs update:**
```txt
# Remove aiohttp (not used)
# Add:
httpx>=0.25.2
```

**Optional:**
- Flask/Werkzeug - Only for web UI (archived)
- gunicorn - Production server (unused in current codebase)

## Critical Success Factors

Based on project 005 evolution, these are the critical factors for production success:

1. **Anti-Bot Protection** (THE most important)
   - User-Agent rotation (12+ variants)
   - Header randomization on EVERY request
   - Human-like delays with jitter
   - Rate limiting detection and auto-slowdown

2. **Zero Duplicates** (Data quality)
   - Page token extraction from `data[1]`
   - Set-based duplicate detection with `seen_review_ids`
   - Proper pagination logic

3. **Robust Date Parsing** (Reliability)
   - 3-tier fallback strategy
   - Year validation (2000-2100)
   - Support for both formatted and relative dates

4. **Complete Field Extraction** (100% coverage)
   - All 12 fields extracted per review
   - Safe navigation with `safe_get()`
   - Fallback values for missing data

5. **Performance Optimization**
   - Fast mode (50-150ms delays)
   - Connection pooling
   - Smart date range cutoff
   - Minimal unnecessary API calls

## Evolution from Project 005

This framework integrates learnings from project 005 development (14:00-15:30, 11/10/2025):

### What We Learned
1. Browser automation (Playwright) is 4-5x slower than HTTP-only
2. Anti-bot protection is ESSENTIAL for production use
3. 3-tier date parsing handles all response variations
4. Page token pagination eliminates duplicates completely
5. Fast mode with anti-bot features achieves 37.83+ reviews/sec
6. ScraperConfig dataclass provides clean configuration management

### What We Implemented
- ✅ HTTP-only RPC method (no browser overhead)
- ✅ Complete anti-bot protection suite
- ✅ 3-tier date parsing fallback
- ✅ Page token pagination
- ✅ 100% field extraction (12 fields)
- ✅ ScraperConfig dataclass
- ✅ Zero-duplicate detection
- ✅ Smart date range filtering

### Performance Evolution
```
Initial (Browser): 4-5 reviews/sec
↓
HTTP-only: 23 reviews/sec (+4.6x)
↓
With anti-bot: 37.83 reviews/sec (+7.5x)
↓
Current framework: 26-30 reviews/sec (stable, production-ready)
```

## Troubleshooting

### Windows Thai Character Issues
- Ensure console uses UTF-8: `chcp 65001`
- Run backend with proper encoding setup (handled in code)
- Check that `sys.platform == 'win32'` block is executed

### Rate Limiting
- Reduce `max_rate` in ScraperConfig
- Enable proxy rotation
- Switch to human mode (`fast_mode=False`)
- Check `stats['rate_limits_encountered']`

### Parsing Errors
- Google may change response structure
- Check date parsing strategies first (most fragile)
- Use `safe_get()` to prevent crashes
- Enable debug output to see raw response
- Test with multiple places to identify variations

### Pagination Issues
- Verify page token extraction from `data[1]`
- Check that `next_page_token` is being passed correctly
- Monitor duplicate counts in output
- Ensure `seen_review_ids` set is working

### Performance Issues
- Check if rate limiting is kicking in
- Verify fast_mode is enabled for performance
- Monitor network latency if using proxies
- Check connection pool settings

## Future Enhancements

Potential improvements based on project 005 roadmap:

1. **Concurrent Requests** (Target: 40+ reviews/sec)
   - Fetch multiple pages simultaneously
   - Requires careful rate limit management
   - Expected 1.5-2x speed improvement

2. **CAPTCHA Solving** (Currently framework only)
   - CapSolver integration exists but not fully implemented
   - Auto-detection and solving workflow
   - Fallback to manual intervention

3. **Advanced Stealth** (Project 005 had this)
   - Canvas fingerprint randomization
   - WebGL fingerprint randomization
   - More sophisticated TLS fingerprinting

4. **Distributed Scraping**
   - Redis-based task queue
   - Multiple scraper instances
   - Shared rate limiting

5. **Real-time Monitoring**
   - Health score tracking
   - Bot detection alerts
   - Performance dashboards

## New Features Added (November 2025)

### 1. Language-Region Management System

**Files:**
- `webapp/app.py` (lines 88-119, 413-420, 1192, 1449-1464)

**Key Components:**

**LANGUAGE_REGION_PRESETS Dictionary (lines 88-102):**
```python
LANGUAGE_REGION_PRESETS = {
    'th': ('th', 'th'),        # Thailand locale
    'en': ('en', 'th'),        # English language with Thailand locale
    'en-th': ('en', 'th'),      # Explicit English-Thai combination
    'en-us': ('en', 'us'),      # US locale
    'ja': ('ja', 'jp'),        # Japanese
    'zh': ('zh-CN', 'cn'),    # Chinese simplified
    # ... 20+ total presets
}
```

**split_language_region() Function (lines 105-119):**
- Parses combined language-region strings (e.g., "en-th" → ('en', 'th'))
- Supports both combined and simple language codes
- Falls back to presets for common language codes

**Enhanced Settings (line 415, 1192):**
```python
current_settings.update({
    'enable_translation': False,
    'target_language': 'en',
    'translate_review_text': True,
    'translate_review_metadata': False,
    'language_region': 'th'
})
```

**Translation Pipeline (lines 1449-1464):**
- Queue management with retry logic
- Multiple translation targets support
- Error handling with exponential backoff
- **CURRENT ISSUE**: `'float' object has no attribute 'as_dict'` error

### 2. Thai Provinces Search System

**Files:**
- `src/utils/thai_provinces.py` (NEW)
- `webapp/app.py` (lines 134-153)
- `webapp/templates/search.html` (Enhanced)

**Key Components:**

**THAI_PROVINCES Dictionary:**
- 15+ major Thai provinces with comprehensive metadata
- Each province includes: region, search_keywords, examples, aliases
- Supports both Thai names and English aliases

**Core Functions:**
```python
get_all_provinces()                    # List all provinces
get_province_data(province_name)       # Get province information
enhance_search_query_with_province()   # Add province to search query
get_province_suggestions(query)        # Autocomplete suggestions
validate_province_search(query, province)  # Validate search
get_popular_search_terms()             # Popular search combinations
```

**API Endpoints (webapp/app.py):**
- `GET /api/provinces` - List all provinces
- `GET /api/provinces/suggestions` - Autocomplete suggestions
- `POST /api/provinces/validate` - Validate province search
- Integrated with search API for province-aware results

### 3. Enhanced Web Application

**Files:**
- `webapp/app.py` (Multiple enhancements)
- `webapp/templates/search.html` (Province dropdown)
- `webapp/templates/settings.html` (Translation settings)

**New Features:**
- Province selection dropdown with validation
- Language-region configuration interface
- Translation settings panel
- Real-time search suggestions
- Enhanced error handling and user feedback

**Port Configuration:**
- Default port changed from 5000 to 5001 to avoid conflicts
- Multiple Flask instance detection and prevention

### 4. Translation Infrastructure

**Files:**
- `src/utils/bulk_translator.py` (NEW)
- `src/utils/enhanced_language_service.py` (NEW)
- `src/utils/language_service.py` (NEW)

**Features:**
- Multi-provider translation support
- Batch translation capabilities
- Enhanced language detection
- Retry logic with error handling
- Translation queue management

### 5. Repository Organization

**Reorganization (November 2025):**
- 54 files moved to `_unused/` directory
- Clean main directory structure
- Organized test files, debug scripts, and temporary data
- Maintained essential functionality in main directory

## Updated Requirements

**New Dependencies (November 2025):**
```txt
# Translation and language detection
py-googletrans>=4.0.0rc1
deep-translator>=1.11.4
lingua-language-detector>=1.2.0

# Core HTTP client (updated from aiohttp)
httpx>=0.25.2

# Flask and webapp (existing)
Flask>=2.0.0
Werkzeug>=2.0.0
```

**Remove unused dependencies:**
- `aiohttp` (not used in current codebase)
- Any other unused packages

## New Documentation

**Created (November 2025):**
- `docs/LANGUAGE_REGION_GUIDE.md` - Comprehensive language-region system documentation
- `docs/THAI_PROVINCES_GUIDE.md` - Thai provinces search system documentation
- Updated `README.md` with new features and API endpoints
- Enhanced troubleshooting section for new features

---

**Document Version:** v3.0 (November 2025 feature additions)
**Last Updated:** 2025-11-11
**Author:** Nextzus
**Project:** google-maps-scraper-python
