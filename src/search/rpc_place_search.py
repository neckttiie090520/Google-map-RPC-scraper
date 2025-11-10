# -*- coding: utf-8 -*-
"""
Real Google Maps Place Search using RPC
=======================================

Based on Go implementation from project 005.
Uses Google Maps RPC API with pb parameter.

Author: Nextzus
Date: 2025-11-10
"""
import sys
import os

# Fix Windows encoding
if sys.platform == 'win32':
    os.system('chcp 65001 > nul 2>&1')

import asyncio
import httpx
import json
import random
from typing import List, Optional
from dataclasses import dataclass
from urllib.parse import urlencode


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


class RpcPlaceSearch:
    """Real Google Maps place search using RPC"""

    def __init__(self, language="th", region="th"):
        self.language = language
        self.region = region

    def generate_headers(self):
        """Generate request headers"""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]

        return {
            'User-Agent': random.choice(user_agents),
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': f'{self.language}-{self.region.upper()},{self.language};q=0.9,en;q=0.8',
            'Referer': 'https://www.google.com/maps',
            'Origin': 'https://www.google.com',
        }

    def build_search_params(self, query: str, lat: float = 13.7563, lon: float = 100.5018, zoom: float = 13.0):
        """
        Build Google Maps search parameters with pb

        Based on Go implementation:
        pb format: !4m12!1m3!1d{distance}!2d{lon}!3d{lat}!2m3!1f0!2f0!3f0!3m2!1i{width}!2i{height}!4f{zoom}!7i20!8i0...
        """
        viewport_w = 800
        viewport_h = 600

        # Distance is calculated from zoom level (simplified)
        distance = 3826.902183192154 / (2 ** (zoom - 13))

        pb = (
            f"!4m12!1m3!1d{distance:.9f}!2d{lon:.4f}!3d{lat:.4f}"
            f"!2m3!1f0!2f0!3f0!3m2!1i{viewport_w}!2i{viewport_h}!4f{zoom:.1f}"
            f"!7i20!8i0!10b1!12m22!1m3!18b1!30b1!34e1!2m3!5m1!6e2!20e3"
            f"!4b0!10b1!12b1!13b1!16b1!17m1!3e1!20m3!5e2!6b1!14b1"
            f"!46m1!1b0!96b1!19m4!2m3!1i360!2i120!4i8"
        )

        params = {
            'tbm': 'map',
            'authuser': '0',
            'hl': self.language,
            'q': query,
            'pb': pb
        }

        return params

    async def search_places(self, query: str, max_results: int = 10,
                          lat: float = 13.7563, lon: float = 100.5018) -> List[PlaceResult]:
        """
        Search for places using RPC method

        Args:
            query: Search query (e.g., "restaurants in Bangkok")
            max_results: Maximum number of results to return
            lat: Latitude for center point (default: Bangkok)
            lon: Longitude for center point (default: Bangkok)

        Returns:
            List of PlaceResult objects
        """
        try:
            url = "https://www.google.com/search"
            params = self.build_search_params(query, lat, lon)
            headers = self.generate_headers()

            # Print with error handling for Thai characters
            try:
                print(f"[RPC SEARCH] Searching for: {query}")
            except:
                print(f"[RPC SEARCH] Searching for: [query]")
            print(f"[RPC SEARCH] Location: {lat}, {lon}")

            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                response = await client.get(url, params=params, headers=headers)

                print(f"[RPC SEARCH] Status: {response.status_code}")
                print(f"[RPC SEARCH] URL: {response.url}")

                if response.status_code == 200:
                    # Parse response
                    body = response.content

                    # Remove first line (like Go implementation)
                    if b'\n' in body:
                        body = body.split(b'\n', 1)[1]

                    # Try to parse as JSON
                    places = self._parse_search_results(body, max_results)

                    if places:
                        print(f"[RPC SEARCH] Found {len(places)} places")
                        return places
                    else:
                        print(f"[RPC SEARCH] No places found in response")

        except Exception as e:
            print(f"[RPC SEARCH] Error: {e}")
            import traceback
            traceback.print_exc()

        return []

    def _parse_search_results(self, raw: bytes, max_results: int) -> List[PlaceResult]:
        """
        Parse search results from JSON response

        Based on Go implementation's ParseSearchResults function
        """
        try:
            # Decode and parse JSON
            data = json.loads(raw.decode('utf-8'))

            if not isinstance(data, list) or len(data) == 0:
                print("[RPC SEARCH] Invalid JSON structure")
                return []

            # Store response data for direct result extraction
            self._current_response_data = data

            # Debug output removed for production

            # Check for DIRECT RESULT at top level
            # Direct result format: [["place_name", [place_data_array...]], ...] or ["place_name", [place_data_array...], ...]
            if isinstance(data, list) and len(data) >= 1:
                # Check if first element is a list (nested structure)
                if isinstance(data[0], list) and len(data[0]) >= 2:
                    potential_name = data[0][0]
                    potential_data = data[0][1]

                    # Direct result detection - nested structure
                    print(f"[RPC SEARCH] Debug: Checking nested structure - name type: {type(potential_name)}, data type: {type(potential_data)}, data length: {len(potential_data) if isinstance(potential_data, list) else 'N/A'}")

                    # Check if this is actually a list result (many places)
                    if (isinstance(potential_name, str) and
                        isinstance(potential_data, list) and
                        len(potential_data) >= 15):  # List results usually have 15+ items
                        print("[RPC SEARCH] Detected list result structure - skipping direct detection")
                        # Continue to list result parsing below
                        pass
                    elif (isinstance(potential_name, str) and
                          isinstance(potential_data, list) and
                          len(potential_data) >= 1):

                        # Check if the first element contains the actual place data
                        first_element = potential_data[0] if len(potential_data) > 0 else None
                        print(f"[RPC SEARCH] Debug: first_element type: {type(first_element)}, length: {len(first_element) if isinstance(first_element, list) else 'N/A'}")

                        if isinstance(first_element, list) and len(first_element) > 10:
                            actual_place_data = first_element

                            # Try to extract Place ID from different possible indices
                            test_place_id_17 = self._safe_get(actual_place_data, 17)
                            test_place_id_16 = self._safe_get(actual_place_data, 16)
                            test_place_id_15 = self._safe_get(actual_place_data, 15)
                            test_place_id_14 = self._safe_get(actual_place_data, 14)
                            test_place_id_13 = self._safe_get(actual_place_data, 13)
                            test_place_id_12 = self._safe_get(actual_place_data, 12)
                            test_place_id_11 = self._safe_get(actual_place_data, 11)
                            test_place_id_10 = self._safe_get(actual_place_data, 10)

                            # Try to find the Place ID - check all indices
                            place_id_candidates = [test_place_id_17, test_place_id_16, test_place_id_15, test_place_id_14,
                                                  test_place_id_13, test_place_id_12, test_place_id_11, test_place_id_10]

                            test_place_id = None
                            for i, candidate in enumerate(place_id_candidates):
                                if candidate and isinstance(candidate, str) and ':' in candidate:
                                    test_place_id = candidate
                                    break

                            # If not found in expected indices, search the entire structure
                            if not test_place_id:
                                test_place_id = self._search_for_place_id(actual_place_data)

                            if test_place_id and ':' in test_place_id:
                                print("[RPC SEARCH] Found direct result")

                                # Extract place data using recursive search
                                name = potential_name
                                place_id = test_place_id

                                # Try Go-style extraction for direct results
                                place_data = None
                                try:
                                    # For direct results, data is in data[0][1][0][14]
                                    if (isinstance(data[0], list) and len(data[0]) > 1 and
                                        isinstance(data[0][1], list) and len(data[0][1]) > 0 and
                                        isinstance(data[0][1][0], list) and len(data[0][1][0]) > 14):

                                        business_data = data[0][1][0][14]
                                        if isinstance(business_data, list) and len(business_data) > 20:
                                            place_data = self._extract_go_style_data(business_data)
                                except Exception as e:
                                    print(f"[RPC SEARCH] Go-style extraction failed: {e}")

                                # Fallback to recursive search if Go-style failed
                                if not place_data:
                                    place_data = self._find_place_data_in_structure(data[0])
                                    print(f"[RPC SEARCH] Using recursive search data: {place_data}")
                                else:
                                    try:
                                        print(f"[RPC SEARCH] Go-style extracted data: {place_data}")
                                    except:
                                        print("[RPC SEARCH] Go-style extracted data: [contains Thai text]")

                                # Use found data or fallback defaults
                                if place_data:
                                    rating = place_data.get('rating', 0.0)
                                    review_count = place_data.get('review_count', 0)
                                    address = place_data.get('address', '')
                                    lat = place_data.get('latitude', place_data.get('lat', 0.0))
                                    lon = place_data.get('longitude', place_data.get('lon', 0.0))
                                    category = place_data.get('category', 'Place')
                                else:
                                    # Fallback to zeros if no data found
                                    rating = 0.0
                                    review_count = 0
                                    address = ''
                                    lat = 0.0
                                    lon = 0.0
                                    category = 'Place'

                                if place_id and name:
                                    return [PlaceResult(
                                        place_id=place_id,
                                        name=name,
                                        address=address,
                                        rating=rating,
                                        total_reviews=review_count,
                                        category=category,
                                        url=f"https://www.google.com/maps/place/?q=place_id:{place_id}",
                                        latitude=lat,
                                        longitude=lon
                    )]

                else:
                    if (isinstance(potential_name, str) and
                        isinstance(potential_data, list) and
                        len(potential_data) > 10):
                        # This looks like a direct result
                        print("[RPC SEARCH] Found direct result at top level (nested)")
                        print(f"[RPC SEARCH] Debug: potential_name length = {len(potential_name) if isinstance(potential_name, str) else 'N/A'}")
                        print(f"[RPC SEARCH] Debug: first_element length = {len(first_element) if isinstance(first_element, list) else 'N/A'}")

                        # For direct results, we need to search the entire structure for the data
                        name = potential_name

                        # Try to extract data from the main response structure
                        # We need to access the full data structure to find the actual place information
                        place_data = self._extract_direct_result_data()
                        print(f"[RPC SEARCH] Direct result data extracted: {place_data}")
                        if place_data:
                            place_id = place_data.get('place_id', '')
                            rating = place_data.get('rating', 0)
                            review_count = place_data.get('review_count', 0)
                            address = place_data.get('address', '')
                            lat = place_data.get('lat', 0.0)
                            lon = place_data.get('lon', 0.0)
                            category = place_data.get('category', 'Place')
                        else:
                            # Fallback to basic extraction
                            place_id = self._search_for_place_id(potential_data) or ""
                            rating = 0
                            review_count = 0
                            address = ""
                            lat = 0.0
                            lon = 0.0
                            category = "Place"

                        if place_id and name:
                            print(f"[RPC SEARCH] Direct result: {name} (ID: {place_id})")
                            return [PlaceResult(
                                    place_id=place_id,
                                    name=name,
                                    address=address,
                                    rating=float(rating) if rating else 0.0,
                                    total_reviews=review_count,
                                    category=category,
                                    url=f"https://www.google.com/maps/place/?q=place_id:{place_id}",
                                    latitude=lat,
                                    longitude=lon
                                )]

            # Also check flat structure (fallback)
            if len(data) >= 2:
                    potential_name = data[0]
                    potential_data = data[1]

                    try:
                        print(f"[RPC SEARCH] Potential name (flat): {potential_name}")
                    except:
                        print("[RPC SEARCH] Potential name (flat): [Thai text]")
                    print(f"[RPC SEARCH] Potential data type (flat): {type(potential_data)}")
                    print(f"[RPC SEARCH] Potential data length (flat): {len(potential_data) if isinstance(potential_data, list) else 'N/A'}")

                    if (isinstance(potential_name, str) and
                        isinstance(potential_data, list) and
                        len(potential_data) > 10):
                        # This looks like a direct result
                        print("[RPC SEARCH] Found direct result at top level (flat)")

                        # Extract place data
                        name = potential_name
                        place_id = self._safe_get(potential_data, 17) or ""
                        rating = self._safe_get(potential_data, 14) or 0
                        review_count_raw = self._safe_get(potential_data, 15)
                        review_count = int(review_count_raw) if review_count_raw and not isinstance(review_count_raw, (list, type(None))) else 0

                        # Address parts
                        address_parts = []
                        addr1 = self._safe_get(potential_data, 2)
                        addr2 = self._safe_get(potential_data, 3)
                        addr3 = self._safe_get(potential_data, 4)

                        if addr1:
                            address_parts.append(str(addr1))
                        if addr2:
                            address_parts.append(str(addr2))
                        if addr3:
                            address_parts.append(str(addr3))

                        address = ', '.join(address_parts)

                        # Coordinates
                        coords = self._safe_get(potential_data, 12)
                        lat = 0.0
                        lon = 0.0
                        if isinstance(coords, list) and len(coords) >= 2:
                            lat = float(coords[0]) if coords[0] else 0.0
                            lon = float(coords[1]) if coords[1] else 0.0

                        # Category
                        categories = self._safe_get(potential_data, 20)
                        category = "Place"
                        if isinstance(categories, list) and len(categories) > 0 and isinstance(categories[0], str):
                            category = categories[0]

                        if place_id and name:
                            print(f"[RPC SEARCH] Direct result: {name} (ID: {place_id})")
                            return [PlaceResult(
                                place_id=place_id,
                                name=name,
                                address=address,
                                rating=float(rating) if rating else 0.0,
                                total_reviews=review_count,
                                category=category,
                                url=f"https://www.google.com/maps/place/?q=place_id:{place_id}",
                                latitude=lat,
                                longitude=lon
                            )]

            # Continue with list result parsing
            container = data[0]
            if not isinstance(container, list) or len(container) == 0:
                print("[RPC SEARCH] Invalid container structure")
                return []

            # Get items array (index 1)
            items = self._safe_get(container, 1)
            if not isinstance(items, list) or len(items) < 2:
                print("[RPC SEARCH] No items found")
                return []

            # Debug: print first few items structure
            print(f"[RPC SEARCH] Items array length: {len(items)}")
            if len(items) > 0:
                first_item = items[0]
                print(f"[RPC SEARCH] First item type: {type(first_item)}, length: {len(first_item) if isinstance(first_item, list) else 'N/A'}")
                if isinstance(first_item, list) and len(first_item) > 0:
                    print(f"[RPC SEARCH] First item first element: {type(first_item[0])} - {str(first_item[0])[:50]}")

            if len(items) > 1:
                second_item = items[1]
                print(f"[RPC SEARCH] Second item type: {type(second_item)}, length: {len(second_item) if isinstance(second_item, list) else 'N/A'}")
                if isinstance(second_item, list) and len(second_item) > 0:
                    print(f"[RPC SEARCH] Second item first element: {type(second_item[0])} - {str(second_item[0])[:50]}")

            places = []

            # Check for DIRECT RESULT (single place)
            # Direct result format: ["place_name", [place_data_array...]]
            first_item = self._safe_get(items, 1)
            if isinstance(first_item, list) and len(first_item) > 0:
                # Check if this looks like a direct result
                potential_place_name = self._safe_get(first_item, 0)
                if isinstance(potential_place_name, str) and len(first_item) > 10:
                    # This is likely a direct result
                    print("[RPC SEARCH] Found direct result (single place)")

                    # Extract place data from direct result structure
                    # The structure is: [name, [place_data...]]
                    place_data = first_item

                    # Extract fields from direct result
                    name = self._safe_get(place_data, 0) or ""
                    place_id = self._safe_get(place_data, 17) or ""  # Place ID at index 17
                    rating = self._safe_get(place_data, 14) or 0
                    review_count = int(self._safe_get(place_data, 15) or 0)

                    # Address parts
                    address_parts = []
                    addr1 = self._safe_get(place_data, 2)  # Street address
                    addr2 = self._safe_get(place_data, 3)  # District
                    addr3 = self._safe_get(place_data, 4)  # Province

                    if addr1:
                        address_parts.append(str(addr1))
                    if addr2:
                        address_parts.append(str(addr2))
                    if addr3:
                        address_parts.append(str(addr3))

                    address = ', '.join(address_parts)

                    # Coordinates
                    coords = self._safe_get(place_data, 12)  # [lat, lon]
                    lat = 0.0
                    lon = 0.0
                    if isinstance(coords, list) and len(coords) >= 2:
                        lat = float(coords[0]) if coords[0] else 0.0
                        lon = float(coords[1]) if coords[1] else 0.0

                    # Category (extract from categories array)
                    categories = self._safe_get(place_data, 20)
                    category = "Place"
                    if isinstance(categories, list) and len(categories) > 0 and isinstance(categories[0], str):
                        category = categories[0]

                    if place_id and name:
                        places.append(PlaceResult(
                            place_id=place_id,
                            name=name,
                            address=address,
                            rating=float(rating) if rating else 0.0,
                            total_reviews=review_count,
                            category=category,
                            url=f"https://www.google.com/maps/place/?q=place_id:{place_id}",
                            latitude=lat,
                            longitude=lon
                        ))

                        print(f"[RPC SEARCH] Direct result: {name} (ID: {place_id})")
                        return places  # Return immediately for direct result

            # Parse each business entry (skip first item) - LIST RESULTS
            for i in range(1, min(len(items), max_results + 1)):
                arr = items[i]
                if not isinstance(arr, list):
                    continue

                # Get business data (index 14)
                business = self._safe_get(arr, 14)
                if not isinstance(business, list):
                    continue

                # Extract place data (matching Go implementation indices)
                short_id = self._safe_get(business, 0)  # Short ID (not used for scraping)
                place_id = self._safe_get(business, 10)  # DataID - CORRECT Place ID for scraping!
                name = self._safe_get(business, 11)  # Title
                categories = self._safe_get(business, 13)  # Categories
                website = self._safe_get(business, 7, 0)  # Website

                rating = self._safe_get(business, 4, 7)  # ReviewRating
                review_count_raw = self._safe_get(business, 4, 8)
                review_count = int(review_count_raw) if review_count_raw and not isinstance(review_count_raw, (list, type(None))) else 0  # ReviewCount

                # Full address (index 2)
                address_parts = self._safe_get(business, 2)
                address = ', '.join(str(p) for p in address_parts) if isinstance(address_parts, list) else ''

                # Coordinates
                lat = self._safe_get(business, 9, 2)
                lon = self._safe_get(business, 9, 3)

                # Category
                category = categories[0] if isinstance(categories, list) and len(categories) > 0 else 'Place'

                if place_id and name:
                    places.append(PlaceResult(
                        place_id=place_id,
                        name=name,
                        address=address,
                        rating=float(rating) if rating else 0.0,
                        total_reviews=review_count,
                        category=str(category),
                        url=f"https://www.google.com/maps/place/?q=place_id:{place_id}",
                        latitude=float(lat) if lat else 0.0,
                        longitude=float(lon) if lon else 0.0
                    ))

            return places

        except Exception as e:
            print(f"[RPC SEARCH] Parse error: {e}")
            import traceback
            traceback.print_exc()
            return []

    def _search_for_place_id(self, data):
        """Recursively search for Place ID in nested structure"""
        if isinstance(data, str) and ':' in data and data.startswith('0x'):
            return data
        elif isinstance(data, list):
            for item in data:
                result = self._search_for_place_id(item)
                if result:
                    return result
        elif isinstance(data, dict):
            for value in data.values():
                result = self._search_for_place_id(value)
                if result:
                    return result
        return None

    def _find_place_data_in_structure(self, data):
        """Search for place data (rating, reviews, address, etc.) in nested structure"""
        result = {
            'place_id': None,
            'rating': 0,
            'review_count': 0,
            'address': '',
            'lat': 0.0,
            'lon': 0.0,
            'category': 'Place'
        }

        def recursive_search(item, depth=0):
            if depth > 20:  # Prevent infinite recursion
                return False

            # Check if this item contains place data
            if isinstance(item, list) and len(item) >= 10:  # More flexible length requirement
                # Look for rating (float/integer) and reviews (integer)
                for i in range(len(item)):
                    # Check for common patterns based on array length
                    if isinstance(item[i], (int, float)) and item[i] > 0:
                        # Check for common patterns
                        if i == 14 and isinstance(item[i], (int, float)):  # Rating in longer arrays
                            result['rating'] = item[i]
                        elif i == len(item)-1 and isinstance(item[i], (int, float)):  # Last element might be rating
                            result['rating'] = item[i]
                        elif i == 15 and i < len(item) and isinstance(item[i], (int, str)):  # Reviews
                            if isinstance(item[i], str):
                                # Extract number from string like "5,078 ความเห็น"
                                import re
                                match = re.search(r'[\d,]+', str(item[i]))
                                if match:
                                    result['review_count'] = int(match.group().replace(',', ''))
                            else:
                                result['review_count'] = item[i]
                        elif i == 17 and i < len(item) and isinstance(item[i], str) and ':' in item[i]:  # Place ID
                            result['place_id'] = item[i]
                        elif i == 12 and i < len(item) and isinstance(item[i], list) and len(item[i]) >= 2:  # Coordinates
                            try:
                                result['lat'] = float(item[i][0]) if item[i][0] else 0.0
                                result['lon'] = float(item[i][1]) if item[i][1] else 0.0
                            except (ValueError, TypeError):
                                pass
                        elif i == 8 and i < len(item) and isinstance(item[i], list):  # Address parts
                            address_parts = []
                            for part in item[i]:
                                if isinstance(part, str) and part.strip():
                                    address_parts.append(part.strip())
                            if address_parts:
                                result['address'] = ', '.join(address_parts)
                        elif i == 2 and i < len(item) and isinstance(item[i], str) and len(item[i]) > 10:  # Address
                            result['address'] = item[i]
                        elif i == 20 and i < len(item) and isinstance(item[i], list) and len(item[i]) > 0:  # Category
                            if isinstance(item[i][0], str):
                                result['category'] = item[i][0]

                    # Also check for Place ID pattern in strings
                    if isinstance(item[i], str) and ':' in item[i] and item[i].startswith('0x'):
                        result['place_id'] = item[i]

            # Recursively search deeper
            if isinstance(item, list):
                for sub_item in item:
                    if recursive_search(sub_item, depth + 1):
                        return True
            elif isinstance(item, dict):
                for value in item.values():
                    if recursive_search(value, depth + 1):
                        return True

            return False

        # Start the search
        print(f"[RPC SEARCH] Starting recursive search on data type: {type(data)}")
        found = recursive_search(data)
        print(f"[RPC SEARCH] Recursive search completed. Found: {found}")

        # Return result if we found any useful data
        if (result['place_id'] or result['rating'] > 0 or result['review_count'] > 0 or
            result['address'] or result['lat'] != 0.0 or result['lon'] != 0.0):
            print(f"[RPC SEARCH] Returning result: {result}")
            return result
        print("[RPC SEARCH] No place data found")
        return None

    def _extract_go_style_data(self, business_data):
        """Extract data using Go-style indices from business_data array"""
        result = {}

        try:
            # Based on Go implementation indices from multiple.go and entry.go
            # These indices match the Go code: business[0], business[11], business[13], etc.

            # Place ID (business[0])
            if len(business_data) > 0:
                result['place_id'] = business_data[0]

            # Title (business[11])
            if len(business_data) > 11:
                try:
                    result['title'] = business_data[11]
                except:
                    result['title'] = "[Thai title]"

            # Categories (business[13])
            if len(business_data) > 13 and isinstance(business_data[13], list):
                categories = []
                for cat in business_data[13]:
                    if isinstance(cat, str):
                        try:
                            categories.append(cat)
                        except:
                            categories.append("[Thai category]")
                if categories:
                    result['categories'] = categories
                    result['category'] = categories[0]  # First category as primary

            # Review data (business[4][7] and business[4][8])
            if len(business_data) > 4 and isinstance(business_data[4], list):
                review_section = business_data[4]
                if len(review_section) > 7:
                    result['rating'] = float(review_section[7]) if review_section[7] else 0.0
                if len(review_section) > 8:
                    result['review_count'] = int(review_section[8]) if review_section[8] else 0

            # Address (business[2])
            if len(business_data) > 2 and isinstance(business_data[2], list):
                address_parts = []
                for part in business_data[2]:
                    if isinstance(part, str) and part.strip():
                        try:
                            address_parts.append(part.strip())
                        except:
                            address_parts.append("[Thai address]")
                if address_parts:
                    result['address'] = ', '.join(address_parts)

            # Coordinates (business[9][2] and business[9][3])
            if len(business_data) > 9 and isinstance(business_data[9], list) and len(business_data[9]) > 3:
                try:
                    lat = business_data[9][2]
                    lon = business_data[9][3]
                    result['latitude'] = float(lat) if lat else 0.0
                    result['longitude'] = float(lon) if lon else 0.0
                except (ValueError, TypeError):
                    pass

            # Phone (business[178][0][0])
            if len(business_data) > 178 and isinstance(business_data[178], list) and len(business_data[178]) > 0:
                if isinstance(business_data[178][0], list) and len(business_data[178][0]) > 0:
                    result['phone'] = str(business_data[178][0][0]).replace(" ", "")

            # Website (business[7][0])
            if len(business_data) > 7 and isinstance(business_data[7], list) and len(business_data[7]) > 0:
                result['website'] = business_data[7][0]

            # Data ID (business[10])
            if len(business_data) > 10:
                result['data_id'] = business_data[10]

            # Status (business[34][4][4])
            if len(business_data) > 34 and isinstance(business_data[34], list):
                if len(business_data[34]) > 4 and isinstance(business_data[34][4], list):
                    if len(business_data[34][4]) > 4:
                        result['status'] = business_data[34][4][4]

            return result

        except Exception as e:
            print(f"[RPC SEARCH] Error in Go-style extraction: {e}")
            return None

    def _extract_direct_result_data(self):
        """Extract direct result data from the response structure"""
        # Access the full response data that was parsed
        # We need to look at the structure we saw in the debug output

        # The direct result data is in data[0][1][0] from the parsed response
        if hasattr(self, '_current_response_data') and self._current_response_data:
            try:
                data = self._current_response_data
                if (isinstance(data, list) and len(data) > 0 and
                    isinstance(data[0], list) and len(data[0]) > 1 and
                    isinstance(data[0][1], list) and len(data[0][1]) > 0):

                    place_info = data[0][1][0]
                    if isinstance(place_info, list) and len(place_info) > 20:
                        return self._extract_from_place_info(place_info)
            except Exception as e:
                print(f"[RPC SEARCH] Error extracting direct result data: {e}")

        return None

    def _extract_from_place_info(self, place_info):
        """Extract data from the place_info array"""
        result = {}

        try:
            # Index 14: Rating
            if len(place_info) > 14 and isinstance(place_info[14], (int, float)):
                result['rating'] = place_info[14]

            # Index 15: Review count
            if len(place_info) > 15:
                review_data = place_info[15]
                if isinstance(review_data, (int, float)):
                    result['review_count'] = int(review_data)
                elif isinstance(review_data, str):
                    import re
                    match = re.search(r'[\d,]+', review_data)
                    if match:
                        result['review_count'] = int(match.group().replace(',', ''))

            # Index 17: Place ID
            if len(place_info) > 17 and isinstance(place_info[17], str) and ':' in place_info[17]:
                result['place_id'] = place_info[17]

            # Index 12: Coordinates [lat, lon]
            if len(place_info) > 12 and isinstance(place_info[12], list) and len(place_info[12]) >= 2:
                try:
                    result['lat'] = float(place_info[12][0]) if place_info[12][0] else 0.0
                    result['lon'] = float(place_info[12][1]) if place_info[12][1] else 0.0
                except (ValueError, TypeError):
                    pass

            # Index 8: Address components
            if len(place_info) > 8 and isinstance(place_info[8], list):
                address_parts = []
                for part in place_info[8]:
                    if isinstance(part, str) and part.strip():
                        address_parts.append(part.strip())
                if address_parts:
                    result['address'] = ', '.join(address_parts)

            # Index 20: Category
            if len(place_info) > 20 and isinstance(place_info[20], list) and len(place_info[20]) > 0:
                if isinstance(place_info[20][0], str):
                    result['category'] = place_info[20][0]

            print(f"[RPC SEARCH] Extracted direct data: {result}")
            return result

        except Exception as e:
            print(f"[RPC SEARCH] Error parsing place info: {e}")
            return None

    def _find_place_data_direct(self, container):
        """Find place data directly in a container structure"""
        result = {}

        # Look for common patterns in the container
        if isinstance(container, list) and len(container) > 15:
            for i, item in enumerate(container):
                if isinstance(item, (int, float)) and item > 0:
                    # This could be a rating
                    if i == 14:  # Common rating index
                        result['rating'] = item
                    elif i == 15 and isinstance(item, (int, str)):  # Reviews
                        if isinstance(item, str):
                            import re
                            match = re.search(r'[\d,]+', str(item))
                            if match:
                                result['review_count'] = int(match.group().replace(',', ''))
                        else:
                            result['review_count'] = item
                    elif i == 17 and isinstance(item, str) and ':' in item:  # Place ID
                        result['place_id'] = item
                    elif i == 12 and isinstance(item, list) and len(item) >= 2:  # Coordinates
                        try:
                            result['lat'] = float(item[0]) if item[0] else 0.0
                            result['lon'] = float(item[1]) if item[1] else 0.0
                        except (ValueError, TypeError):
                            pass
                    elif i == 2 and isinstance(item, str) and len(item) > 10:  # Address
                        result['address'] = item
                    elif i == 20 and isinstance(item, list) and len(item) > 0:  # Category
                        if isinstance(item[0], str):
                            result['category'] = item[0]

        return result

    def _safe_get(self, data, *indices):
        """Safely get nested element by indices"""
        try:
            current = data
            for idx in indices:
                if isinstance(current, list) and 0 <= idx < len(current):
                    current = current[idx]
                else:
                    return None
            return current
        except (IndexError, TypeError, KeyError):
            return None


def create_rpc_search(language="th", region="th"):
    """Create RPC place search service"""
    return RpcPlaceSearch(language=language, region=region)
