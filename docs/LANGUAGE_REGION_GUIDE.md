# Language-Region Management System Guide

## Overview

The Google Maps RPC Scraper includes a sophisticated language-region management system that enables precise control over the language and regional settings used for scraping Google Maps data. This system ensures consistent language enforcement across pagination and provides optimized search results for specific geographic regions.

## Features

### 1. Language-Region Presets

The system includes 12+ predefined language-region combinations optimized for different use cases:

```python
LANGUAGE_REGION_PRESETS = {
    'th': ('th', 'th'),              # Thailand locale
    'en': ('en', 'th'),              # English language with Thailand locale
    'en-th': ('en', 'th'),            # Explicit English-Thai combination
    'en-us': ('en', 'us'),            # US locale
    'ja': ('ja', 'jp'),              # Japanese
    'ja-jp': ('ja', 'jp'),            # Explicit Japanese-Japan combination
    'zh': ('zh-CN', 'cn'),           # Chinese simplified
    'zh-cn': ('zh-CN', 'cn'),         # Explicit Chinese-China combination
    'zh-tw': ('zh-TW', 'tw'),         # Chinese traditional
    'ko': ('ko', 'kr'),              # Korean
    'ko-kr': ('ko', 'kr'),            # Explicit Korean-Korea combination
    'es': ('es', 'es'),              # Spanish
    'fr': ('fr', 'fr'),              # French
    'de': ('de', 'de'),              # German
    'ru': ('ru', 'ru'),              # Russian
    'pt': ('pt', 'br'),              # Portuguese (Brazil)
    'pt-br': ('pt', 'br'),           # Explicit Portuguese-Brazil combination
    'ar': ('ar', 'sa'),              # Arabic (Saudi Arabia)
    'hi': ('hi', 'in'),              # Hindi (India)
    'id': ('id', 'id'),              # Indonesian
    'ms': ('ms', 'my'),              # Malay (Malaysia)
    'vi': ('vi', 'vn'),              # Vietnamese
    'tl': ('tl', 'ph'),              # Filipino (Philippines)
}
```

### 2. Smart Language-Region Parsing

The `split_language_region()` function intelligently parses combined language-region strings:

```python
def split_language_region(language_region):
    """
    Split combined language-region string (e.g., 'en-th') into language and region.

    Args:
        language_region (str): Combined language-region string or simple language code

    Returns:
        tuple: (language, region) pair
    """
```

**Examples:**
- `"en-th"` → `('en', 'th')`
- `"ja-jp"` → `('ja', 'jp')`
- `"zh-CN"` → `('zh-CN', 'cn')`
- `"th"` → `('th', 'th')` (uses preset)
- `"en"` → `('en', 'th')` (default region: Thailand)

### 3. Enhanced Search with Thai Provinces

Integration with Thai provinces system for optimized local search:

```python
from src.utils.thai_provinces import enhance_search_query_with_province

# Enhance search query with province context
query = "โรงแรม"
province = "เชียงใหม่"
enhanced_query = enhance_search_query_with_province(query, province)
# Returns: "โรงแรม จังหวัดเชียงใหม่"
```

## Usage Examples

### Basic Language-Region Configuration

```python
from src.scraper.production_scraper import create_production_scraper
from webapp.app import LANGUAGE_REGION_PRESETS, split_language_region

# Method 1: Use preset directly
scraper = create_production_scraper(
    language="en",
    region="th"  # English language, Thailand region
)

# Method 2: Parse combined string
language, region = split_language_region("en-th")
scraper = create_production_scraper(
    language=language,
    region=region
)

# Method 3: Access all presets
print(f"Available presets: {len(LANGUAGE_REGION_PRESETS)}")
for key, (lang, reg) in LANGUAGE_REGION_PRESETS.items():
    print(f"{key}: {lang}/{reg}")
```

### Web Application Integration

The Flask web application includes language-region management in settings:

```python
# In webapp/app.py
@app.route('/api/settings', methods=['GET', 'POST'])
def handle_settings():
    if request.method == 'POST':
        data = request.get_json()

        # Handle language-region setting
        if 'language_region' in data:
            language_region = data['language_region']
            language, region = split_language_region(language_region)
            current_settings['language'] = language
            current_settings['region'] = region
```

### Translation Pipeline Integration

When translation is enabled, the system uses language-region settings for optimal translation:

```python
# Enhanced settings with translation support
current_settings.update({
    'enable_translation': True,
    'target_language': 'en',
    'translate_review_text': True,
    'translate_review_metadata': False,
    'language_region': 'th',  # Source: Thai
    'language': 'th',
    'region': 'th'
})
```

## Technical Implementation

### 1. Language Enforcement in RPC Requests

The system enforces language settings across all RPC API calls:

```python
def get_language_headers(language, region):
    """Generate HTTP headers for language-specific requests"""
    headers = {
        'Accept-Language': f"{language}-{region},{language};q=0.9,en;q=0.8",
        'X-Preferred-Language': language,
        'Cookie': f'hl={language};gl={region}'
    }
    return headers
```

### 2. Pagination Language Consistency

Ensures consistent language across all pages:

```python
async def fetch_rpc_page(self, client, place_id, page_num, page_token=None):
    # Language parameters are consistent across all requests
    params = self.build_rpc_params(place_id, page_token)

    # Headers include language settings
    headers = self.get_language_headers(self.config.language, self.config.region)

    # Request maintains language consistency
    async with client.get(url, params=params, headers=headers) as response:
        data = await response.json()
        return self.parse_reviews(data), self.extract_page_token(data)
```

### 3. Thai Provinces Region Optimization

```python
def get_region_for_province(province_name):
    """Get optimal region setting for Thai province"""
    province_data = get_province_data(province_name)
    if province_data:
        return province_data.get('region', 'th')
    return 'th'  # Default to Thailand
```

## API Reference

### Functions

#### `split_language_region(language_region)`

Parse combined language-region string into separate components.

**Parameters:**
- `language_region` (str): Combined string like "en-th" or simple code like "en"

**Returns:**
- `tuple`: (language, region) pair

**Example:**
```python
language, region = split_language_region("en-th")
# Returns: ('en', 'th')
```

#### `get_language_headers(language, region)`

Generate HTTP headers for language-specific requests.

**Parameters:**
- `language` (str): Language code (e.g., "en", "th")
- `region` (str): Region code (e.g., "us", "th")

**Returns:**
- `dict`: HTTP headers dictionary

#### `validate_language_region(language_region)`

Validate language-region combination against supported presets.

**Parameters:**
- `language_region` (str): Language-region string to validate

**Returns:**
- `tuple`: (is_valid, language, region, message)

### Webapp API Endpoints

#### `GET /api/settings`
Get current language-region and other settings.

**Response:**
```json
{
    "success": true,
    "settings": {
        "language_region": "en-th",
        "language": "en",
        "region": "th",
        "enable_translation": false,
        "target_language": "en"
    }
}
```

#### `POST /api/settings`
Update language-region and other settings.

**Request Body:**
```json
{
    "language_region": "en-th",
    "enable_translation": true,
    "target_language": "en"
}
```

## Configuration

### Environment Variables

```bash
# Language & Region
LANGUAGE_REGION=en-th          # Combined language-region
DEFAULT_LANGUAGE=th           # Fallback language
DEFAULT_REGION=th             # Fallback region

# Translation
ENABLE_TRANSLATION=true       # Enable translation pipeline
TARGET_LANGUAGE=en            # Target language for translation
TRANSLATE_REVIEW_TEXT=true    # Translate review content
```

### ScraperConfig Integration

```python
@dataclass
class ScraperConfig:
    language: str = "th"
    region: str = "th"

    # Translation settings
    enable_translation: bool = False
    target_language: str = "en"
    translate_review_text: bool = True
    translate_review_metadata: bool = False
```

## Troubleshooting

### Common Issues

1. **Language Not Applied Correctly**
   - Verify language-region string format
   - Check LANGUAGE_REGION_PRESETS for supported combinations
   - Ensure `split_language_region()` returns expected values

2. **Translation Errors**
   - Current issue: `'float' object has no attribute 'as_dict'`
   - Workaround: Disable translation temporarily
   - Check data types in translation queue

3. **Region-Specific Results Missing**
   - Verify region code matches target country
   - Use Thai provinces integration for Thailand searches
   - Check Google Maps availability in target region

### Debug Logging

Enable debug logging to trace language-region application:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Logs will show:
# - Language-region parsing
# - Header generation
# - RPC parameter construction
# - Translation pipeline status
```

## Best Practices

### 1. Use Presets When Possible

```python
# Good: Use predefined presets
language, region = LANGUAGE_REGION_PRESETS.get('en-th', ('en', 'th'))

# Acceptable: Parse combined strings
language, region = split_language_region('en-th')

# Avoid: Hardcoding unsupported combinations
language, region = 'xx', 'yy'  # May not work
```

### 2. Validate Input

```python
def safe_language_region_config(user_input):
    if user_input in LANGUAGE_REGION_PRESETS:
        return split_language_region(user_input)
    else:
        # Fallback to default
        return 'th', 'th'
```

### 3. Handle Thai Provinces

```python
def optimized_thai_search(query, province):
    if get_province_data(province):
        enhanced_query = enhance_search_query_with_province(query, province)
        region = get_region_for_province(province)
        return enhanced_query, region
    return query, 'th'
```

## Migration Guide

### From Previous Versions

**Before (separate language/region):**
```python
scraper = create_production_scraper(
    language="en",
    region="th"
)
```

**After (combined language-region):**
```python
# Method 1: Combined string
language, region = split_language_region("en-th")
scraper = create_production_scraper(language=language, region=region)

# Method 2: Direct from preset
language, region = LANGUAGE_REGION_PRESETS['en-th']
scraper = create_production_scraper(language=language, region=region)
```

### Webapp Settings

**Before:**
```json
{
    "language": "en",
    "region": "th"
}
```

**After:**
```json
{
    "language_region": "en-th",
    "language": "en",
    "region": "th"
}
```

## Future Enhancements

### Planned Features

1. **Dynamic Language Detection**
   - Auto-detect review language
   - Smart language switching based on content

2. **Region-Specific Optimization**
   - Custom RPC parameters per region
   - Localized search strategies

3. **Advanced Translation**
   - Multi-provider translation services
   - Batch translation optimization
   - Translation quality scoring

4. **Language-Region Analytics**
   - Track language distribution in results
   - Regional search performance metrics

---

**Last Updated:** 2025-11-11
**Version:** 1.0
**Author:** Nextzus