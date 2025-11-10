#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import asyncio
import json

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.search.rpc_place_search import create_rpc_search

async def debug_search_response():
    """Debug the raw response for specific search that returns direct result"""

    rpc_search = create_rpc_search()

    # Test with specific query "ข้าวซอยนิมมาน"
    query = "ข้าวซอยนิมมาน"
    try:
        print(f"Testing search for: {query}")
    except:
        print("Testing search for: [Thai query]")

    try:
        # Build search params manually to see the response
        url = "https://www.google.com/search"
        params = rpc_search.build_search_params(query, lat=18.7883, lon=98.9853)  # Chiang Mai
        headers = rpc_search.generate_headers()

        try:
            print(f"Request URL: {url}")
        except:
            print("Request URL: [Google search URL]")

        try:
            print(f"Request params: {params}")
        except:
            print("Request params: [search parameters]")

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, params=params, headers=headers)
            try:
                print(f"Response status: {response.status_code}")
            except:
                print(f"Response status: {response.status_code}")

            if response.status_code == 200:
                # Save raw response for analysis
                with open('debug_response.html', 'w', encoding='utf-8') as f:
                    f.write(response.text)
                try:
                    print("Raw response saved to debug_response.html")
                except:
                    print("Raw response saved to debug_response.html")

                # Try to parse the response
                text = response.text

                # Check if it contains the typical RPC response format
                if text.startswith(")]}'"):
                    print("Found RPC response format")
                    json_text = text[4:]  # Remove prefix
                    try:
                        data = json.loads(json_text)
                        print(f"Successfully parsed JSON")

                        # Print structure of the response
                        def print_structure(obj, indent=0):
                            indent_str = "  " * indent
                            if isinstance(obj, dict):
                                for key, value in obj.items():
                                    print(f"{indent_str}{key}: {type(value).__name__}")
                                    if indent < 3 and key in ['ds', 'dr', 'd']:
                                        print_structure(value, indent + 1)
                            elif isinstance(obj, list):
                                print(f"{indent_str}List with {len(obj)} items")
                                if indent < 2 and len(obj) > 0:
                                    print_structure(obj[0], indent + 1)

                        print_structure(data)

                        # Look for place data in common locations
                        def find_places(data, path=""):
                            places = []
                            if isinstance(data, dict):
                                # Check if this looks like place data
                                if any(key in data for key in ['business', 'place', 'l']):
                                    print(f"Found potential place data at {path}")
                                    places.append((path, data))

                                # Recursively search
                                for key, value in data.items():
                                    places.extend(find_places(value, f"{path}.{key}" if path else key))
                            elif isinstance(data, list):
                                for i, item in enumerate(data):
                                    places.extend(find_places(item, f"{path}[{i}]"))
                            return places

                        found_places = find_places(data)
                        print(f"\nFound {len(found_places)} potential place data structures:")
                        for path, data in found_places[:5]:  # Show first 5
                            print(f"  {path}: {type(data).__name__}")

                    except json.JSONDecodeError as e:
                        print(f"Failed to parse JSON: {e}")
                else:
                    print("Response doesn't start with expected RPC format")
                    print(f"First 200 chars: {text[:200]}")
            else:
                print(f"Request failed with status {response.status_code}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import httpx
    asyncio.run(debug_search_response())