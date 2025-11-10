#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import asyncio
import json

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.search.rpc_place_search import create_rpc_search

async def debug_direct_result_structure():
    """Debug the actual structure of direct result data"""

    rpc_search = create_rpc_search()
    query = "ข้าวซอยนิมมาน"

    try:
        try:
            print(f"=== DEBUG: Direct result structure for: {query} ===")
        except:
            print("=== DEBUG: Direct result structure for: [Thai query] ===")

        # Build the request exactly like the search method does
        import httpx
        url = "https://www.google.com/search"
        params = rpc_search.build_search_params(query, lat=18.7883, lon=98.9853)
        headers = rpc_search.generate_headers()

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, params=params, headers=headers)
            print(f"Status: {response.status_code}")

            # Save response to file for analysis
            with open('debug_direct_response.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            print("Response saved to debug_direct_response.html")

            # Parse and show structure
            text = response.text
            if text.startswith(")]}'"):
                json_text = text[4:]
                data = json.loads(json_text)
                print(f"Data type: {type(data)}")
                print(f"Data length: {len(data) if isinstance(data, list) else 'N/A'}")

                if isinstance(data, list) and len(data) > 0:
                    potential_name = data[0] if len(data) > 0 else None
                    potential_data = data[1] if len(data) > 1 else None

                    try:
                        print(f"potential_name: {potential_name}")
                    except:
                        print("potential_name: [Thai name]")
                    print(f"potential_data type: {type(potential_data)}, length: {len(potential_data) if isinstance(potential_data, list) else 'N/A'}")

                    if isinstance(potential_data, list) and len(potential_data) > 0:
                        print(f"\n=== Examining potential_data structure ===")
                        for i, item in enumerate(potential_data):
                            print(f"potential_data[{i}]: type={type(item)}, length={len(item) if isinstance(item, list) else 'N/A'}")
                            if isinstance(item, list) and len(item) > 0:
                                print(f"  First element: {item[0]}")
                                if len(item) > 10:
                                    print(f"  Elements 10-15: {item[10:16]}")

                        # Check all indices in potential_data for place data
                        print(f"\n=== Searching for place data in potential_data ===")
                        for i, item in enumerate(potential_data):
                            if isinstance(item, list) and len(item) > 15:
                                print(f"potential_data[{i}] has {len(item)} elements - checking for place data:")
                                # Check for rating at index 14
                                if len(item) > 14 and isinstance(item[14], (int, float)):
                                    print(f"  Index 14 (rating): {item[14]}")
                                # Check for reviews at index 15
                                if len(item) > 15:
                                    print(f"  Index 15 (reviews): {item[15]}")
                                # Check for place_id
                                if len(item) > 17 and isinstance(item[17], str) and ':' in item[17]:
                                    print(f"  Index 17 (place_id): {item[17]}")
                                # Check for coordinates
                                if len(item) > 12 and isinstance(item[12], list):
                                    print(f"  Index 12 (coords): {item[12]}")
                                # Check for address
                                if len(item) > 2 and isinstance(item[2], str):
                                    print(f"  Index 2 (address): {item[2]}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_direct_result_structure())