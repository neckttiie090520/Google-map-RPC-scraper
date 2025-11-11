# Thai Provinces Search System Guide

## Overview

The Thai Provinces Search System provides comprehensive support for searching Google Maps places by Thailand provinces with automatic region optimization and enhanced search queries. This system includes 15+ major Thai provinces with detailed metadata, aliases, search keywords, and examples to optimize search results for each region.

## Features

### 1. Comprehensive Province Database

Complete database of major Thai provinces with rich metadata:

```python
THAI_PROVINCES = {
    "กรุงเทพมหานคร": {
        "region": "th",
        "search_keywords": ["โรงแรม", "ร้านอาหาร", "ห้างสรรพสินค้า", "ตลาด", "สถานที่ท่องเที่ยว"],
        "examples": ["สยามพารากอน", "เซ็นทรัลเวิลด์", "จตุจักร", "วัดพระแก้ว", "เอราวัณด์"],
        "aliases": ["bangkok", "กทม"]
    },
    "เชียงใหม่": {
        "region": "th",
        "search_keywords": ["โรงแรม", "ร้านอาหาร", "ตลาดน้ำ", "วัด", "สถานที่ท่องเที่ยว"],
        "examples": ["โดยติเศรษฐี", "ตลาดน้ำตำแยง", "วัดพระธาตุดอยสุเทพ", "นิมมานเฮมต์"],
        "aliases": ["chiang mai"]
    },
    # ... 13 more provinces
}
```

### 2. Smart Search Enhancement

Automatically enhances search queries with province context:

```python
def enhance_search_query_with_province(query, province):
    """
    Add province context to search queries for better results.

    Examples:
    - "โรงแรม" + "เชียงใหม่" → "โรงแรม จังหวัดเชียงใหม่"
    - "restaurant" + "bangkok" → "restaurant bangkok thailand"
    """
```

### 3. Province Validation and Suggestions

Real-time province validation and autocomplete suggestions:

```python
def get_province_suggestions(query):
    """Get province suggestions from partial input"""

def validate_province_search(query, province):
    """Validate search parameters and provide feedback"""
```

## Available Provinces

The system includes 15 major Thai provinces:

| Province | English Name | Region | Key Attractions |
|----------|--------------|--------|-----------------|
| กรุงเทพมหานคร | Bangkok | th | Siam Paragon, Central World, Chatuchak |
| เชียงใหม่ | Chiang Mai | th | Doi Suthep, Nimman, Night Bazaar |
| ภูเก็ต | Phuket | th | Patong Beach, Big Buddha |
| สุราษฎร์ธานี | Surat Thani | th | Koh Samui, Koh Phangan |
| กระบี่ | Krabi | th | Phi Phi Islands, Railay Beach |
| ชลบุรี | Chonburi | th | Pattaya, Bang Saen |
| นครราชสีมา | Nakhon Ratchasima | th | Khao Yai, The Mall |
| ขอนแก่น | Khon Kaen | th | Khon Kaen University |
| เชียงราย | Chiang Rai | th | Wat Rong Khun, Golden Triangle |
| หาดใหญ่ | Hua Hin | th | Hua Hin Beach, Night Market |
| นครศรีธรรมราช | Nakhon Si Thammarat | th | Wat Phra Mahathat |
| สงขลา | Songkhla | th | Hat Yai, Samila Beach |
| พัทยา | Pattaya | th | Walking Street, Jomtien Beach |
| อุบลราชธานี | Ubon Ratchathani | th | Candle Festival |
| นราธิวาสรรม | Nakhon Pathom | th | Phra Pathom Chedi |

## Usage Examples

### Basic Province Search

```python
from src.utils.thai_provinces import (
    get_all_provinces,
    get_province_data,
    enhance_search_query_with_province
)

# Get all available provinces
provinces = get_all_provinces()
print(f"Available provinces: {len(provinces)}")
# Output: Available provinces: 15

# Get detailed province data
province_data = get_province_data("เชียงใหม่")
print(province_data)
# Output: {
#     'region': 'th',
#     'search_keywords': ['โรงแรม', 'ร้านอาหาร', 'ตลาดน้ำ', 'วัด', 'สถานที่ท่องเที่ยว'],
#     'examples': ['โดยติเศรษฐี', 'ตลาดน้ำตำแยง', 'วัดพระธาตุดอยสุเทพ', 'นิมมานเฮมต์'],
#     'aliases': ['chiang mai']
# }

# Enhance search query
enhanced_query = enhance_search_query_with_province("โรงแรม", "เชียงใหม่")
print(enhanced_query)  # "โรงแรม จังหวัดเชียงใหม่"
```

### Province Validation

```python
from src.utils.thai_provinces import validate_province_search, get_province_suggestions

# Validate search parameters
query = "ร้านอาหาร"
province = "เชียงใหม่"
is_valid, message = validate_province_search(query, province)
print(f"Valid: {is_valid}, Message: {message}")
# Output: Valid: True, Message: ค้นหาในจังหวัดเชียงใหม่

# Invalid province
is_valid, message = validate_province_search("ร้านอาหาร", "invalid_province")
print(f"Valid: {is_valid}, Message: {message}")
# Output: Valid: False, Message: จังหวัด 'invalid_province' ไม่พบในระบบ

# Get suggestions
suggestions = get_province_suggestions("เชียง")
print(suggestions)  # ['เชียงใหม่', 'เชียงราย']

# Use English alias
suggestions = get_province_suggestions("chiang")
print(suggestions)  # ['เชียงใหม่']
```

### Integration with Scraper

```python
from src.scraper.production_scraper import create_production_scraper
from src.utils.thai_provinces import enhance_search_query_with_province, get_region_for_province

# Search in specific province
query = "โรงแรมหรู"
province = "ภูเก็ต"

# Enhance query with province context
enhanced_query = enhance_search_query_with_province(query, province)
region = get_region_for_province(province)  # Returns 'th'

# Create scraper with region optimization
scraper = create_production_scraper(
    language="th",
    region=region,
    fast_mode=True
)

print(f"Searching for: {enhanced_query}")
print(f"Using region: {region}")
```

### Web Application Integration

```python
# Flask routes for Thai provinces API
@app.route('/api/provinces', methods=['GET'])
def get_provinces():
    """Get all available Thai provinces"""
    provinces = get_all_provinces()
    return jsonify({
        "success": True,
        "provinces": provinces,
        "count": len(provinces)
    })

@app.route('/api/provinces/suggestions', methods=['GET'])
def get_province_suggestions_api():
    """Get province suggestions from query"""
    query = request.args.get('q', '').strip()
    suggestions = get_province_suggestions(query)
    return jsonify({
        "success": True,
        "query": query,
        "suggestions": suggestions
    })
```

## Web Application Features

### 1. Province Dropdown in Search Form

The webapp includes a province selection dropdown with:

- All 15 major Thai provinces
- English aliases for international users
- Real-time validation feedback

### 2. Auto-Complete Suggestions

JavaScript integration for dynamic suggestions:

```javascript
// frontend JavaScript
async function getProvinceSuggestions(query) {
    const response = await fetch(`/api/provinces/suggestions?q=${encodeURIComponent(query)}`);
    const data = await response.json();

    if (data.success) {
        updateProvinceDropdown(data.suggestions);
    }
}

// Call on input change
document.getElementById('province-input').addEventListener('input', (e) => {
    if (e.target.value.length > 0) {
        getProvinceSuggestions(e.target.value);
    }
});
```

### 3. Enhanced Search Results

Province-aware search results display:

- Province context in search results
- Regional optimization applied automatically
- Popular search terms per province

## API Reference

### Core Functions

#### `get_all_provinces()`

Get list of all available Thai provinces.

**Returns:**
- `List[str]`: List of province names in Thai

#### `get_province_data(province_name)`

Get detailed information about a province.

**Parameters:**
- `province_name` (str): Province name or alias

**Returns:**
- `dict` or `None`: Province data dictionary

```python
province_data = get_province_data("เชียงใหม่")
# Returns:
# {
#     'region': 'th',
#     'search_keywords': ['โรงแรม', 'ร้านอาหาร', 'ตลาดน้ำ', 'วัด', 'สถานที่ท่องเที่ยว'],
#     'examples': ['โดยติเศรษฐี', 'ตลาดน้ำตำแยง', 'วัดพระธาตุดอยสุเทพ', 'นิมมานเฮมต์'],
#     'aliases': ['chiang mai']
# }
```

#### `enhance_search_query_with_province(query, province)`

Add province context to search query.

**Parameters:**
- `query` (str): Original search query
- `province` (str): Province name

**Returns:**
- `str`: Enhanced search query with province context

#### `get_province_suggestions(query)`

Get province suggestions from partial input.

**Parameters:**
- `query` (str): Partial province name or alias

**Returns:**
- `List[str]`: List of matching province names (max 5)

#### `validate_province_search(query, province)`

Validate search parameters and provide feedback.

**Parameters:**
- `query` (str): Search query
- `province` (str): Province name

**Returns:**
- `tuple`: (is_valid, message)

#### `get_popular_search_terms()`

Get popular search combinations for Thai provinces.

**Returns:**
- `List[dict]`: Popular search terms with province context

```python
terms = get_popular_search_terms()
# Returns:
# [
#     {'term': 'โรงแรม', 'province': 'กรุงเทพมหานคร', 'full_query': 'โรงแรม จังหวัดกรุงเทพมหานคร'},
#     {'term': 'ร้านอาหาร', 'province': 'กรุงเทพมหานคร', 'full_query': 'ร้านอาหาร จังหวัดกรุงเทพมหานคร'},
#     ...
# ]
```

### Webapp API Endpoints

#### `GET /api/provinces`

Get all available provinces.

**Response:**
```json
{
    "success": true,
    "provinces": [
        "กรุงเทพมหานคร",
        "เชียงใหม่",
        "ภูเก็ต",
        "..."
    ],
    "count": 15
}
```

#### `GET /api/provinces/suggestions?q=<query>`

Get province suggestions.

**Parameters:**
- `q` (query string): Partial province name

**Response:**
```json
{
    "success": true,
    "query": "เชียง",
    "suggestions": [
        "เชียงใหม่",
        "เชียงราย"
    ]
}
```

#### `POST /api/provinces/validate`

Validate province search parameters.

**Request Body:**
```json
{
    "query": "โรงแรม",
    "province": "เชียงใหม่"
}
```

**Response:**
```json
{
    "success": true,
    "is_valid": true,
    "message": "ค้นหาในจังหวัดเชียงใหม่",
    "enhanced_query": "โรงแรม จังหวัดเชียงใหม่"
}
```

## Implementation Details

### 1. Province Data Structure

Each province includes comprehensive metadata:

```python
{
    "province_name": {
        "region": "th",                                    # ISO region code
        "search_keywords": ["keyword1", "keyword2", ...],  # Common search terms
        "examples": ["example1", "example2", ...],         # Popular places
        "aliases": ["alias1", "alias2", ...]               # English/alternative names
    }
}
```

### 2. Search Enhancement Algorithm

The search enhancement uses multiple strategies:

```python
def enhance_search_query_with_province(query, province):
    province_variants = [
        f"{query} จังหวัด{province}",    # Thai formal
        f"{query} {province}",            # Simple concatenation
        f"{query} ใน{province}",          # "in" preposition
        f"{query} ที่{province}"          # "at" preposition
    ]
    return province_variants[0]  # Use formal variant
```

### 3. Alias Resolution System

Automatic alias resolution for flexible input:

```python
def get_province_data(province_name):
    # Try exact match first
    if province_name in THAI_PROVINCES:
        return THAI_PROVINCES[province_name]

    # Try aliases
    for province, data in THAI_PROVINCES.items():
        if province_name.lower() in [alias.lower() for alias in data.get('aliases', [])]:
            return data

    return None
```

## Configuration

### Environment Variables

```bash
# Thai Provinces Settings
ENABLE_THAI_PROVINCES=true         # Enable Thai provinces system
DEFAULT_PROVINCE_REGION=th         # Default region for Thai provinces
PROVINCE_SUGGESTION_LIMIT=5        # Max suggestions to return

# Search Enhancement
ENHANCE_PROVINCE_QUERIES=true      # Auto-enhance queries with province
PROVINCE_SEARCH_VARIANTS=4         # Number of query variants to generate
```

### Custom Province Data

You can extend the provinces database by adding to `THAI_PROVINCES`:

```python
THAI_PROVINCES["จังหวัดใหม่"] = {
    "region": "th",
    "search_keywords": ["คำค้น", "คำค้นพิเศษ"],
    "examples": ["สถานที่1", "สถานที่2"],
    "aliases": ["new_province", "alias_name"]
}
```

## Troubleshooting

### Common Issues

1. **Province Not Found**
   - Check exact spelling in Thai
   - Try English aliases
   - Use suggestions API for autocomplete

2. **No Search Enhancement**
   - Verify province data exists
   - Check `enhance_search_query_with_province()` output
   - Ensure province validation passes

3. **API Not Returning Suggestions**
   - Check query parameter encoding
   - Verify endpoint exists in Flask routes
   - Check CORS settings

### Debug Logging

Enable debug logging for Thai provinces:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable debug in thai_provinces.py
logger = logging.getLogger(__name__)
logger.debug(f"Province data for {province}: {province_data}")
logger.debug(f"Enhanced query: {enhanced_query}")
logger.debug(f"Province suggestions: {suggestions}")
```

## Best Practices

### 1. Input Validation

```python
def safe_province_search(query, province):
    if not query or not query.strip():
        return None, "กรุณาระบุคำค้น"

    if not province:
        return query, "ค้นหาทั่วประเทศไทย"

    if not get_province_data(province):
        return None, f"จังหวัด '{province}' ไม่พบในระบบ"

    enhanced_query = enhance_search_query_with_province(query, province)
    return enhanced_query, f"ค้นหาในจังหวัด{province}"
```

### 2. Performance Optimization

```python
# Cache province data for performance
from functools import lru_cache

@lru_cache(maxsize=100)
def get_cached_province_data(province_name):
    return get_province_data(province_name)

# Batch suggestions for autocomplete
def get_batch_province_suggestions(queries):
    results = {}
    for query in queries:
        results[query] = get_province_suggestions(query)
    return results
```

### 3. User Experience

```python
# Provide helpful error messages
def get_user_friendly_error(error_code):
    errors = {
        'no_province': 'กรุณาเลือกจังหวัดจากรายการ',
        'invalid_query': 'คำค้นต้องมีอย่างน้อย 2 ตัวอักษร',
        'no_results': 'ไม่พบข้อมูลที่ตรงกับคำค้น'
    }
    return errors.get(error_code, 'เกิดข้อผิดพลาดที่ไม่ทราบสาเหตุ')
```

## Future Enhancements

### Planned Features

1. **Extended Province Coverage**
   - All 77 Thai provinces
   - District-level search (อำเภอ)
   - Postal code integration

2. **Advanced Search Algorithms**
   - Machine learning for query enhancement
   - Context-aware search suggestions
   - Popular trends per province

3. **Multilingual Support**
   - Chinese province names
   - Japanese province names
   - Enhanced English aliases

4. **Regional Analytics**
   - Search popularity by province
   - Tourism trend analysis
   - Regional business insights

---

**Last Updated:** 2025-11-11
**Version:** 1.0
**Author:** Nextzus