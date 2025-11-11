# -*- coding: utf-8 -*-
"""
Simple RPC Place Search with Language Fix
========================================

Simplified place search using Google Maps RPC with language consistency fix.
This version focuses on reliability and direct results.

Author: Nextzus
Date: 2025-11-11
"""
import sys
import os
import json
import re
from typing import List, Optional
from dataclasses import dataclass
from urllib.parse import quote

# Fix Windows encoding
if sys.platform == 'win32':
    os.system('chcp 65001 > nul 2>&1')

try:
    import httpx
except ImportError:
    print("httpx is required. Install with: pip install httpx")
    sys.exit(1)

from dataclasses import dataclass

@dataclass
class PlaceResult:
    """Simple place result data structure"""
    place_id: str
    name: str
    address: str
    rating: float
    total_reviews: int
    category: str
    latitude: float
    longitude: float
    url: str

class SimpleRpcSearch:
    """Simple RPC place search with language consistency"""

    def __init__(self, language: str = "th", region: str = "th"):
        """
        Initialize search service

        Args:
            language: Language code (th, en, ja, etc.)
            region: Region code (th, us, jp, etc.)
        """
        self.language = language
        self.region = region

    async def search_places(self, query: str, max_results: int = 10) -> List[PlaceResult]:
        """
        Search for places using RPC method with language consistency

        Args:
            query: Search query
            max_results: Maximum results to return

        Returns:
            List of PlaceResult objects
        """
        print(f"[SEARCH] Searching for: {query}")
        print(f"[SEARCH] Language: {self.language}, Region: {self.region}")

        try:
            # Build search URL with language parameters
            search_url = (
                f"https://www.google.com/search?"
                f"tbm=map"
                f"&authuser=0"
                f"&hl={self.language}"
                f"&gl={self.region}"
                f"&q={quote(query)}"
            )

            # Build pb parameter for viewport (Bangkok area)
            # This helps get more relevant results
            pb = (
                "!4m12!1m3!1d3826.902183192!2d100.5018!3d13.7563!3m2!1f0!2f0!3f0!"
                "!4m12!1m3!1d3826.902183192!2d100.5018!3d13.7563!3m2!1i800!2i600!4f13.0!7i20!8i0!"
                "!10b1!11b1!12b1!13b1!14b1!15b1!16b1!17m1!18b1!19m1!20m1!21m1!22m1!23m1!"
                "!24m1!25m1!26m1!27m1!28m1!29m1!30b1"
            )

            search_url += f"&pb={quote(pb)}"

            # Headers with language enforcement
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': f'{self.language}-{self.region.upper()},{self.language};q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache',
            }

            # Make request
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(search_url, headers=headers)

                if response.status_code == 200:
                    print(f"[SEARCH] Success: {response.status_code}")

                    # Parse HTML response to extract place data
                    places = self._extract_places_from_html(response.text, max_results)

                    print(f"[SEARCH] Found {len(places)} places")
                    return places
                else:
                    print(f"[SEARCH] HTTP Error: {response.status_code}")
                    return []

        except Exception as e:
            print(f"[SEARCH] Error: {e}")
            return []

    def _extract_places_from_html(self, html_content: str, max_results: int) -> List[PlaceResult]:
        """
        Extract places from HTML response using regex patterns

        This is a simplified approach that looks for data attributes in the HTML
        """
        places = []

        try:
            # Look for data attributes that contain place information
            # Pattern to find data-cid or similar attributes with place data
            data_patterns = [
                r'data-cid="([^"]+)"[^>]*>([^<]+)',
                r'href="/maps/place/([^/]+)/([^"]+)"',
                r'\\"address\\":\\"([^"]+)\\"',
                r'\\"rating\\":([0-9.]+)',
                r'\\"user_ratings_total\\":(\d+)',
            ]

            # Look for place data in JavaScript sections
            js_section_pattern = r'window\.INITIAL_DATA\s*=\s*({.+?});'
            js_match = re.search(js_section_pattern, html_content, re.DOTALL)

            if js_match:
                try:
                    # Try to parse JavaScript data
                    js_data_text = js_match.group(1)
                    # Remove any JavaScript comments and trailing commas
                    js_data_text = re.sub(r'//.*?\n', '', js_data_text)
                    js_data_text = re.sub(r',\s*}', '}', js_data_text)

                    js_data = json.loads(js_data_text)

                    # Extract places from JavaScript data
                    places = self._extract_places_from_js_data(js_data, max_results)

                except Exception as e:
                    print(f"[SEARCH] JS parsing failed: {e}")
                    # Fallback to regex extraction
                    pass

            # Fallback: simple regex-based extraction
            if not places:
                print("[SEARCH] Using fallback regex extraction")
                places = self._extract_places_fallback(html_content, max_results)

        except Exception as e:
            print(f"[SEARCH] Extraction error: {e}")

        # Limit results
        return places[:max_results]

    def _extract_places_from_js_data(self, js_data: dict, max_results: int) -> List[PlaceResult]:
        """Extract places from JavaScript data structure"""
        places = []

        try:
            # Navigate through the complex JavaScript data structure
            # This is based on typical Google Maps page structure

            def find_places_recursive(obj, depth=0):
                if depth > 10:  # Prevent infinite recursion
                    return

                if isinstance(obj, dict):
                    # Look for place-like objects
                    if 'place_id' in obj and 'name' in obj:
                        try:
                            place = PlaceResult(
                                place_id=obj.get('place_id', ''),
                                name=obj.get('name', ''),
                                address=obj.get('formatted_address', obj.get('address', '')),
                                rating=float(obj.get('rating', 0)),
                                total_reviews=int(obj.get('user_ratings_total', 0)),
                                category=obj.get('types', ['Place'])[0] if obj.get('types') else 'Place',
                                latitude=float(obj.get('geometry', {}).get('location', {}).get('lat', 0)),
                                longitude=float(obj.get('geometry', {}).get('location', {}).get('lng', 0)),
                                url=f"https://www.google.com/maps/place/?q=place_id:{obj.get('place_id', '')}"
                            )

                            # Only add if it has a name and place_id
                            if place.name and place.place_id:
                                places.append(place)
                                if len(places) >= max_results:
                                    return
                        except Exception:
                            pass

                    # Recursively search in values
                    for key, value in obj.items():
                        if len(places) >= max_results:
                            return
                        find_places_recursive(value, depth + 1)

                elif isinstance(obj, list):
                    for item in obj:
                        if len(places) >= max_results:
                            return
                        find_places_recursive(item, depth + 1)

            find_places_recursive(js_data)

        except Exception as e:
            print(f"[SEARCH] JS data extraction failed: {e}")

        return places

    def _extract_places_fallback(self, html_content: str, max_results: int) -> List[PlaceResult]:
        """Fallback extraction using simple regex patterns"""
        places = []

        try:
            # Look for structured data (JSON-LD)
            structured_data_pattern = r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>'
            structured_matches = re.findall(structured_data_pattern, html_content, re.DOTALL)

            for match in structured_matches:
                try:
                    data = json.loads(match)
                    if isinstance(data, list):
                        for item in data:
                            if isinstance(item, dict) and item.get('@type') == 'LocalBusiness':
                                place = PlaceResult(
                                    place_id=item.get('identifier', ''),
                                    name=item.get('name', ''),
                                    address=item.get('address', {}).get('streetAddress', ''),
                                    rating=float(item.get('aggregateRating', {}).get('ratingValue', 0)),
                                    total_reviews=int(item.get('aggregateRating', {}).get('reviewCount', 0)),
                                    category=', '.join(item.get('type', [])) if isinstance(item.get('type'), list) else str(item.get('type', '')),
                                    latitude=float(item.get('geo', {}).get('latitude', 0)),
                                    longitude=float(item.get('geo', {}).get('longitude', 0)),
                                    url=item.get('url', '')
                                )

                                if place.name and not any(p.name == place.name for p in places):
                                    places.append(place)
                                    if len(places) >= max_results:
                                        break
                except Exception:
                    continue

                if len(places) >= max_results:
                    break

        except Exception as e:
            print(f"[SEARCH] Fallback extraction failed: {e}")

        return places

def create_simple_rpc_search(language: str = "th", region: str = "th") -> SimpleRpcSearch:
    """
    Factory function to create simple RPC search service

    Args:
        language: Language code (th, en, ja, etc.)
        region: Region code (th, us, jp, etc.)

    Returns:
        SimpleRpcSearch instance
    """
    return SimpleRpcSearch(language=language, region=region)

# Test function
if __name__ == "__main__":
    import asyncio

    async def test_search():
        # Test Thai search
        print("=== Testing Thai Search ===")
        search_th = create_simple_rpc_search(language='th', region='th')
        results_th = await search_th.search_places("Central World Bangkok", max_results=5)

        for i, place in enumerate(results_th):
            print(f"{i+1}. {place.name}")
            print(f"   ID: {place.place_id}")
            print(f"   Address: {place.address}")
            print(f"   Rating: {place.rating} ({place.total_reviews} reviews)")
            print()

        # Test English search
        print("=== Testing English Search ===")
        search_en = create_simple_rpc_search(language='en', region='us')
        results_en = await search_en.search_places("Central World Bangkok", max_results=5)

        for i, place in enumerate(results_en):
            print(f"{i+1}. {place.name}")
            print(f"   ID: {place.place_id}")
            print(f"   Address: {place.address}")
            print(f"   Rating: {place.rating} ({place.total_reviews} reviews)")
            print()

    asyncio.run(test_search())