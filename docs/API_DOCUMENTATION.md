# Google Maps Scraper Framework - API Documentation

Complete API reference for all modules and classes in the Google Maps Scraper Framework.

## Table of Contents

1. [Core Scraper Module](#core-scraper-module)
   - [ProductionGoogleMapsScraper](#productiongooglemapsscraper)
   - [ScraperConfig](#scraperconfig)
   - [ProductionReview](#productionreview)
2. [Search Module](#search-module)
   - [RpcPlaceSearch](#rpcplacesearch)
   - [PlaceResult](#placeresult)
3. [Utilities Module](#utilities-module)
   - [Anti-Bot Utils](#anti-bot-utils)
   - [Output Manager](#output-manager)
   - [Unicode Display](#unicode-display)
   - [Language Services](#language-services)
4. [Factory Functions](#factory-functions)
5. [Data Structures](#data-structures)
6. [Exceptions and Error Handling](#exceptions-and-error-handling)

---

## Core Scraper Module

### ProductionGoogleMapsScraper

Main scraping engine with complete anti-bot protection and translation features.

```python
class ProductionGoogleMapsScraper:
    """Production-ready Google Maps scraper with all features integrated"""
```

#### Constructor

```python
def __init__(self, config: ScraperConfig):
    """
    Initialize production scraper

    Args:
        config: Complete scraper configuration
    """
```

#### Methods

##### scrape_reviews()

```python
async def scrape_reviews(
    self,
    place_id: str,
    max_reviews: int = 1000,
    date_range: str = "1year",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    sort_by_newest: bool = True,
    progress_callback: Optional[callable] = None
) -> Dict[str, Any]:
```

Scrape reviews with all protection features and date range filtering.

**Parameters:**
- `place_id` (str): Google Maps place ID
- `max_reviews` (int): Maximum number of reviews to scrape (default: 1000)
- `date_range` (str): Date range filter ('1month', '6months', '1year', '5years', '7years', 'all', 'custom')
- `start_date` (Optional[str]): Custom start date (YYYY-MM-DD format) - used when date_range='custom'
- `end_date` (Optional[str]): Custom end date (YYYY-MM-DD format) - used when date_range='custom'
- `sort_by_newest` (bool): Sort reviews by date (newest first)
- `progress_callback` (Optional[callable]): Callback function(page_num, total_reviews, **kwargs)

**Returns:**
- `Dict[str, Any]`: Dictionary with reviews and metadata

**Example:**
```python
scraper = create_production_scraper(language="th", region="th")
result = await scraper.scrape_reviews(
    place_id="0x30e29ecfc2f455e1:0xc4ad0280d8906604",
    max_reviews=500,
    date_range="6months"
)

reviews = result['reviews']
metadata = result['metadata']
```

##### fetch_rpc_page()

```python
async def fetch_rpc_page(
    self,
    client: httpx.AsyncClient,
    place_id: str,
    page_num: int = 1,
    page_token: Optional[str] = None
) -> tuple[Optional[List[ProductionReview]], Optional[str]]:
```

Fetch single page with all protection features.

**Parameters:**
- `client`: httpx AsyncClient instance
- `place_id` (str): Google Maps place ID
- `page_num` (int): Page number for tracking
- `page_token` (Optional[str]): Pagination token from previous page

**Returns:**
- `tuple`: (reviews_list, next_page_token)

##### parse_review()

```python
def parse_review(self, entry: list, page_num: int) -> Optional[ProductionReview]:
```

Parse single review with complete field extraction using 3-tier date parsing fallback.

**Parameters:**
- `entry` (list): Raw review data from API
- `page_num` (int): Page number for tracking

**Returns:**
- `Optional[ProductionReview]`: Parsed review object or None if parsing failed

##### Translation Methods

```python
def translate_text_field(self, text: str) -> Tuple[str, str]:
    """
    Translate text field and return both translated text and detected language.

    Returns:
        Tuple of (translated_text, detected_language)
    """

async def translate_multiple_texts_concurrent(self, texts: List[str], max_concurrent: int = 5) -> List[Tuple[str, str]]:
    """
    Translate multiple texts concurrently for improved performance.

    Returns:
        List of tuples (translated_text, detected_language)
    """

async def process_reviews_batch_concurrent(self, reviews: List[ProductionReview], max_concurrent: int = 10) -> List[ProductionReview]:
    """
    Process a batch of reviews with concurrent translation for maximum performance.

    Returns:
        Processed reviews with translations
    """
```

##### Date Filtering Methods

```python
def calculate_date_cutoff(self, date_range: str) -> Optional[datetime]:
    """Convert date_range string to datetime cutoff"""

def is_review_within_date_range(self, review: ProductionReview, date_cutoff: datetime) -> bool:
    """Check if review date is within the specified date range"""

def is_review_within_custom_date_range(self, review: ProductionReview, start_date: str, end_date: str) -> bool:
    """Check if review date is within a custom date range"""
```

##### Export Methods

```python
def export_to_csv(self, reviews: List[ProductionReview], filename: str):
    """Export reviews to CSV with support for translated content"""

def export_to_json(self, data: Dict[str, Any], filename: str):
    """Export complete data to JSON"""
```

### ScraperConfig

Configuration dataclass for the scraper.

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

    # Translation settings
    enable_translation: bool = False
    target_language: str = "en"
    translate_review_text: bool = True
    translate_owner_response: bool = True
    use_enhanced_detection: bool = True
    translation_batch_size: int = 50
```

### ProductionReview

Complete review data structure with all 12 fields.

```python
@dataclass
class ProductionReview:
    """Production review data structure - 100% complete fields"""

    review_id: str                    # Unique review ID
    author_name: str                  # Reviewer name
    author_url: str                   # Reviewer profile URL
    author_reviews_count: int         # Total reviews by author
    rating: int                       # Star rating (1-5)
    date_formatted: str               # DD/MM/YYYY format
    date_relative: str                # Relative date (e.g., "2 สัปดาห์ที่แล้ว")
    review_text: str                  # Review content
    review_text_translated: str       # Translated review text
    original_language: str            # Detected original language
    target_language: str              # Target language for translations
    review_likes: int                 # Number of likes
    review_photos_count: int          # Number of attached photos
    owner_response: str               # Business owner response
    owner_response_translated: str    # Translated owner response
    page_number: int                  # Page number where review was found

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
```

---

## Search Module

### RpcPlaceSearch

Real Google Maps place search using RPC API (no API key required).

```python
class RpcPlaceSearch:
    """Real Google Maps place search using RPC"""
```

#### Constructor

```python
def __init__(self, language="th", region="th"):
    """
    Initialize RPC place search

    Args:
        language (str): Language code (default: "th")
        region (str): Region code (default: "th")
    """
```

#### Methods

##### search_places()

```python
async def search_places(
    self,
    query: str,
    max_results: int = 10,
    lat: float = 13.7563,
    lon: float = 100.5018
) -> List[PlaceResult]:
```

Search for places using RPC method.

**Parameters:**
- `query` (str): Search query (e.g., "restaurants in Bangkok")
- `max_results` (int): Maximum number of results to return
- `lat` (float): Latitude for center point (default: Bangkok)
- `lon` (float): Longitude for center point (default: Bangkok)

**Returns:**
- `List[PlaceResult]`: List of place results

**Example:**
```python
search_service = create_rpc_search(language="th", region="th")
places = await search_service.search_places(
    query="restaurants in Bangkok",
    max_results=20
)
```

##### Internal Methods

```python
def generate_headers(self) -> Dict[str, str]:
    """Generate request headers"""

def build_search_params(self, query: str, lat: float = 13.7563, lon: float = 100.5018, zoom: float = 13.0):
    """Build Google Maps search parameters with pb"""

def _parse_search_results(self, raw: bytes, max_results: int) -> List[PlaceResult]:
    """Parse search results from JSON response"""
```

### PlaceResult

Place search result data structure.

```python
@dataclass
class PlaceResult:
    """Place search result"""

    place_id: str
    name: str
    address: str
    rating: float
    total_reviews: int
    category: str
    url: str
    latitude: float = 0.0
    longitude: float = 0.0
```

---

## Utilities Module

### Anti-Bot Utils

Comprehensive anti-detection utilities.

#### HumanLikeDelay

Generate human-like delays between requests.

```python
class HumanLikeDelay:
    """Generate human-like delays between requests"""

    @staticmethod
    def short_delay() -> float:
        """Short delay between pages (100-300ms)"""

    @staticmethod
    def medium_delay() -> float:
        """Medium delay for natural browsing (500-1500ms)"""

    @staticmethod
    def long_delay() -> float:
        """Long delay after errors (2-5s)"""

    @staticmethod
    def random_page_delay(fast_mode: bool = True) -> float:
        """
        Random delay between pages

        Args:
            fast_mode: If True, use shorter delays (100-300ms)
                      If False, use more human-like delays (500-1500ms)
        """

    @staticmethod
    def jittered_delay(base_delay: float, jitter_ratio: float = 0.3) -> float:
        """Add jitter to base delay"""
```

#### RateLimitDetector

Detect and handle rate limiting.

```python
class RateLimitDetector:
    """Detect and handle rate limiting"""

    def __init__(self, window_seconds: int = 60):
        """Initialize rate limit detector"""

    def record_request(self):
        """Record a request"""

    def get_request_rate(self) -> float:
        """Get current request rate (requests/second)"""

    def should_slow_down(self, max_rate: float = 10.0) -> Tuple[bool, float]:
        """
        Check if we should slow down

        Returns:
            (should_slow_down, suggested_delay)
        """

    def is_rate_limited(self) -> bool:
        """Check if currently rate limited"""

    def set_rate_limited(self, duration_seconds: float):
        """Mark as rate limited for duration"""
```

#### ProxyConfig & ProxyRotator

Proxy rotation support.

```python
@dataclass
class ProxyConfig:
    """Proxy configuration"""

    http_proxy: Optional[str] = None
    https_proxy: Optional[str] = None
    socks5_proxy: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None

    def to_httpx_proxies(self) -> Optional[Dict]:
        """Convert to httpx proxy format"""

class ProxyRotator:
    """Rotate through multiple proxies"""

    def __init__(self, proxies: List[ProxyConfig]):
        """Initialize proxy rotator"""

    def get_next_proxy(self) -> Optional[ProxyConfig]:
        """Get next proxy in rotation"""

    def mark_proxy_failed(self, proxy: ProxyConfig):
        """Mark proxy as failed"""

    def reset_failed(self):
        """Reset failed proxy list"""
```

#### Header Generation

```python
def get_random_user_agent() -> str:
    """Get random User-Agent from pool"""

def get_random_accept_language(language="th", region="th") -> str:
    """Get Accept-Language for specified language"""

def generate_randomized_headers(base_headers: Optional[Dict] = None, language="th", region="th") -> Dict:
    """
    Generate headers with randomized values to avoid fingerprinting

    Args:
        base_headers: Base headers to merge with randomized ones
        language: Language code for Accept-Language header
        region: Region code for Accept-Language header

    Returns:
        Dict with randomized headers
    """
```

### Output Manager

Organized file output management.

```python
class OutputManager:
    """Manages organized output storage for scraped data"""

    def __init__(self, base_dir: str = "./outputs"):
        """Initialize output manager"""

    def save_reviews(self, reviews: List[Dict[str, Any]], place_name: str, place_id: str, task_id: str, settings: Dict[str, Any]) -> Dict[str, str]:
        """
        Save reviews data in multiple formats

        Returns:
            Dictionary with file paths
        """

    def save_places(self, places: List[Dict[str, Any]], search_query: str, settings: Dict[str, Any]) -> Dict[str, str]:
        """
        Save place search results

        Returns:
            Dictionary with file paths
        """

    def save_log(self, log_content: str, log_type: str = "scraping", task_id: Optional[str] = None) -> str:
        """
        Save log content

        Returns:
            Path to saved log file
        """

    def get_recent_files(self, data_type: str = "reviews", limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get list of recent output files

        Returns:
            List of file information
        """

    def cleanup_old_files(self, days_to_keep: int = 30):
        """Clean up old files older than specified days"""

    def get_storage_info(self) -> Dict[str, Any]:
        """
        Get storage information and statistics

        Returns:
            Dictionary with storage statistics
        """
```

### Unicode Display

Multi-language text display utilities.

```python
class UnicodeDisplay:
    """Handle Unicode text display with proper character width calculation"""

    @staticmethod
    def safe_print(text: str, prefix: str = "", suffix: str = ""):
        """Safely print Unicode text without encoding issues"""

    @staticmethod
    def safe_print_with_length(text: str, max_length: int = 80, prefix: str = ""):
        """Print Unicode text with length truncation"""

    @staticmethod
    def truncate_for_display(text: str, max_length: int) -> str:
        """Truncate text for display, considering Asian character width"""

    @staticmethod
    def get_char_width(char: str) -> int:
        """Get display width of a character"""

    @staticmethod
    def format_name_with_language(name: str, language: str = "unknown") -> str:
        """Format name with language indicator"""

    @staticmethod
    def is_thai_text(text: str) -> bool:
        """Check if text contains primarily Thai characters"""

    @staticmethod
    def is_japanese_text(text: str) -> bool:
        """Check if text contains Japanese characters"""

    @staticmethod
    def is_chinese_text(text: str) -> bool:
        """Check if text contains Chinese characters"""

    @staticmethod
    def print_review_summary(reviews: list, language_filter: Optional[str] = None):
        """Print summary of reviews with language statistics"""
```

### Language Services

#### LanguageService

Basic language detection and translation.

```python
class LanguageService:
    """
    Language detection and translation service for review text.
    """

    def __init__(self, target_language: SupportedLanguage = SupportedLanguage.ENGLISH):
        """Initialize language service"""

    def detect_language(self, text: str) -> LanguageDetectionResult:
        """Detect language of given text"""

    def translate_text(self, text: str, source_language: Optional[SupportedLanguage] = None) -> TranslationResult:
        """Translate text to target language"""

    async def translate_text_async(self, text: str, source_language: Optional[SupportedLanguage] = None) -> TranslationResult:
        """Async version of translate_text"""

    def process_review_text(self, text: str) -> Tuple[str, bool, Optional[str]]:
        """Process review text: detect language and translate if needed"""

    async def process_review_text_async(self, text: str) -> Tuple[str, bool, Optional[str]]:
        """Async version of process_review_text"""
```

#### EnhancedLanguageService

Enhanced multi-language detection and translation.

```python
class EnhancedLanguageService:
    """
    Enhanced language detection and translation service supporting Thai, English, Japanese, and Chinese.
    """

    def __init__(self, target_language: SupportedLanguage = SupportedLanguage.ENGLISH, enable_translation: bool = True):
        """Initialize enhanced language service"""

    def detect_language(self, text: str) -> LanguageDetectionResult:
        """Enhanced language detection supporting 4 languages"""

    def translate_text(self, text: str, source_language: SupportedLanguage) -> TranslationResult:
        """High-quality translation between supported languages"""
```

#### Data Structures

```python
@dataclass
class LanguageDetectionResult:
    """Result of language detection"""
    detected_language: SupportedLanguage
    confidence: float
    is_target_language: bool
    needs_translation: bool

@dataclass
class TranslationResult:
    """Result of text translation"""
    original_text: str
    original_language: SupportedLanguage
    translated_text: str
    target_language: SupportedLanguage
    success: bool
    error_message: Optional[str] = None

class SupportedLanguage(Enum):
    """Supported languages for detection and translation"""
    THAI = "th"
    ENGLISH = "en"
    JAPANESE = "ja"
    CHINESE = "zh"
```

---

## Factory Functions

Convenient factory functions for creating configured instances.

### Scraper Factory

```python
def create_production_scraper(
    language: str = "th",
    region: str = "th",
    fast_mode: bool = True,
    max_rate: float = 10.0,
    use_proxy: bool = False,
    proxy_list: Optional[List[str]] = None,
    timeout: float = 30.0,
    max_retries: int = 3,
    enable_translation: bool = False,
    target_language: str = "en",
    translate_review_text: bool = True,
    translate_owner_response: bool = True,
    use_enhanced_detection: bool = True,
    translation_batch_size: int = 50
) -> ProductionGoogleMapsScraper:
    """
    Factory function to create configured production scraper

    Returns:
        Configured ProductionGoogleMapsScraper instance
    """
```

### Search Factory

```python
def create_rpc_search(language="th", region="th") -> RpcPlaceSearch:
    """Create RPC place search service"""
```

### Language Service Factories

```python
def create_language_service(
    target_language: str = "en",
    enable_translation: bool = True
) -> Optional[LanguageService]:
    """Factory function to create language service"""

def create_enhanced_language_service(
    target_language: str = "en",
    enable_translation: bool = True
) -> Optional[EnhancedLanguageService]:
    """Factory function to create enhanced language service"""
```

---

## Data Structures

### Review Data Fields

Each review contains the following 12 complete fields:

| Field | Type | Description |
|-------|------|-------------|
| `review_id` | str | Unique review identifier |
| `author_name` | str | Reviewer's name |
| `author_url` | str | Reviewer's profile URL |
| `author_reviews_count` | int | Total reviews written by author |
| `rating` | int | Star rating (1-5) |
| `date_formatted` | str | Date in DD/MM/YYYY format |
| `date_relative` | str | Relative date (e.g., "2 weeks ago") |
| `review_text` | str | Original review content |
| `review_text_translated` | str | Translated review text |
| `original_language` | str | Detected original language |
| `target_language` | str | Target language for translations |
| `review_likes` | int | Number of helpful votes |
| `review_photos_count` | int | Number of attached photos |
| `owner_response` | str | Business owner response |
| `owner_response_translated` | str | Translated owner response |
| `page_number` | int | Page number where review was found |

### Place Data Fields

| Field | Type | Description |
|-------|------|-------------|
| `place_id` | str | Google Maps place ID |
| `name` | str | Place name |
| `address` | str | Full address |
| `rating` | float | Average rating |
| `total_reviews` | int | Total review count |
| `category` | str | Place category |
| `url` | str | Google Maps URL |
| `latitude` | float | Latitude coordinate |
| `longitude` | float | Longitude coordinate |

### Scraping Result Structure

```python
{
    'reviews': List[ProductionReview],
    'metadata': {
        'place_id': str,
        'total_reviews': int,
        'time_taken': float,
        'rate': float,
        'language': str,
        'region': str,
        'date_range': str,
        'sort_by_newest': bool,
        'date_cutoff': str,
        'stats': {
            'total_requests': int,
            'successful_requests': int,
            'failed_requests': int,
            'rate_limits_encountered': int,
            'proxy_switches': int,
            'retries_used': int
        },
        'translation': {  # Only if translation enabled
            'enabled': bool,
            'target_language': str,
            'detection_count': int,
            'translated_count': int,
            'translation_errors': int,
            'detected_languages': Dict[str, int],
            'translation_success_rate': float
        }
    }
}
```

---

## Exceptions and Error Handling

### Common Exceptions

- `httpx.TimeoutException`: Request timeout
- `httpx.ConnectError`: Connection failed
- `json.JSONDecodeError`: Invalid JSON response
- `UnicodeEncodeError`/`UnicodeDecodeError`: Text encoding issues

### Error Handling Strategy

The framework uses a multi-layered error handling approach:

1. **Request Level**: Retry logic with exponential backoff
2. **Page Level**: Graceful degradation on parsing errors
3. **Review Level**: Skip malformed reviews, continue processing
4. **Session Level**: Comprehensive error reporting and statistics

### Retry Logic

```python
# Automatic retry with different strategies:
# 429 (Rate Limited): 5s, 10s, 20s delays + proxy switch
# 5xx (Server Error): 2s, 4s, 8s delays
# Timeout: 1s, 2s, 4s delays
# Client Error (4xx): No retry
```

### Error Statistics

All scraping operations include detailed error statistics:

```python
stats = {
    'total_requests': int,
    'successful_requests': int,
    'failed_requests': int,
    'rate_limits_encountered': int,
    'proxy_switches': int,
    'retries_used': int
}
```

---

## Performance Considerations

### Rate Limiting

- Default maximum rate: 10.0 requests/second
- Automatic slowdown detection
- Configurable rate limits

### Memory Usage

- Streaming pagination for large datasets
- Optional batch processing for translations
- Configurable batch sizes

### Network Optimization

- Connection pooling with httpx
- Keep-alive connections
- Configurable timeouts

### Translation Performance

- Concurrent translation processing
- Configurable batch sizes
- Automatic fallback on service unavailability

---

## Configuration Examples

### Conservative Mode

```python
scraper = create_production_scraper(
    fast_mode=False,      # Human-like delays
    max_rate=3.0,         # Conservative rate
    timeout=60.0,         # Extended timeout
    max_retries=5         # More retries
)
```

### High Performance Mode

```python
scraper = create_production_scraper(
    fast_mode=True,       # Fast delays
    max_rate=15.0,        # High rate
    timeout=20.0,         # Shorter timeout
    enable_translation=True,
    translation_batch_size=100
)
```

### Proxy Configuration

```python
scraper = create_production_scraper(
    use_proxy=True,
    proxy_list=[
        "http://proxy1.example.com:8080",
        "socks5://proxy2.example.com:1080"
    ]
)
```

### Translation Configuration

```python
scraper = create_production_scraper(
    enable_translation=True,
    target_language="en",
    translate_review_text=True,
    translate_owner_response=True,
    use_enhanced_detection=True,
    translation_batch_size=50
)
```

---

## Global Instances

The framework provides convenient global instances:

```python
from src.utils.output_manager import output_manager
from src.utils.language_service import get_language_service

# Use directly
file_paths = output_manager.save_reviews(...)
lang_service = get_language_service()
```

---

## Thread Safety

- Scraper instances are NOT thread-safe
- Create separate instances for concurrent use
- Output manager and language services are thread-safe
- Anti-bot utilities are thread-safe

---

**API Documentation Version**: v1.0
**Last Updated**: 2025-11-11
**Framework Version**: v1.0
**Compatible with**: Python 3.8+