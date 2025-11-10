#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import asyncio
import httpx
import json

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.search.rpc_place_search import create_rpc_search

async def debug_general_search():
    """Debug general search query like 'ข้าวซอย'"""

    rpc_search = create_rpc_search()
    query = "ข้าวซอย"

    try:
        # Build the request exactly like the search method does
        url = "https://www.google.com/search"
        params = rpc_search.build_search_params(query, lat=13.7563, lon=100.5018)
        headers = rpc_search.generate_headers()

        print(f"Making request to: {url}")
        try:
            print(f"Query: {query}")
        except:
            print("Query: [Thai text]")

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, params=params, headers=headers)

            print(f"Status: {response.status_code}")
            print(f"Content length: {len(response.text)}")

            # Save response
            with open('general_search_response.html', 'w', encoding='utf-8') as f:
                f.write(response.text)

            # Parse and show structure
            text = response.text
            if text.startswith(")]}'"):
                json_text = text[4:]
                try:
                    data = json.loads(json_text)
                    print(f"JSON parsed successfully")
                    print(f"Data type: {type(data)}")
                    print(f"Data length: {len(data) if isinstance(data, list) else 'N/A'}")

                    if isinstance(data, list) and len(data) > 0:
                        print(f"First element type: {type(data[0])}")
                        if isinstance(data[0], str):
                            print(f"First element (string): {data[0][:100]}...")

                        # Look for list structure - this should be a list result
                        if len(data) > 1:
                            container = data[0]
                            if isinstance(container, list):
                                items = rpc_search._safe_get(container, 1)
                                if isinstance(items, list):
                                    print(f"Items array length: {len(items)}")
                                    if len(items) > 1:
                                        print("This looks like a list result structure")
                                        # Try to find place IDs in the list
                                        for i, item in enumerate(items[1:6]):  # Check first 5 items
                                            business = rpc_search._safe_get(item, 14)
                                            if isinstance(business, list):
                                                place_id = rpc_search._safe_get(business, 10)
                                                name = rpc_search._safe_get(business, 11)
                                                if place_id and name:
                                                    print(f"  Item {i}: {name} (ID: {place_id})")
                                    else:
                                        print("Items array is too short or empty")

                except json.JSONDecodeError as e:
                    print(f"JSON decode error: {e}")
            else:
                print("Response doesn't start with expected prefix")
                print(f"First 100 chars: {text[:100]}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_general_search())