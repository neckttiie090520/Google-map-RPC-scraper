#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import asyncio
import json

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.search.rpc_place_search import create_rpc_search

async def debug_actual_place_data():
    """Debug the actual_place_data structure"""

    rpc_search = create_rpc_search()
    query = "ข้าวซอยนิมมาน"

    try:
        try:
            print(f"=== DEBUG: Actual place data structure for: {query} ===")
        except:
            print("=== DEBUG: Actual place data structure for: [Thai query] ===")

        # Build the request exactly like the search method does
        import httpx
        url = "https://www.google.com/search"
        params = rpc_search.build_search_params(query, lat=18.7883, lon=98.9853)
        headers = rpc_search.generate_headers()

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, params=params, headers=headers)
            print(f"Status: {response.status_code}")

            # Parse and show structure
            text = response.text
            if text.startswith(")]}'"):
                json_text = text[4:]
                data = json.loads(json_text)

                if isinstance(data, list) and len(data) > 0:
                    potential_name = data[0][0]
                    potential_data = data[0][1]
                    first_element = potential_data[0] if len(potential_data) > 0 else None

                    try:
                        print(f"potential_name: {potential_name}")
                    except:
                        print("potential_name: [Thai name]")
                    print(f"potential_data length: {len(potential_data)}")
                    print(f"first_element length: {len(first_element) if first_element else 'N/A'}")

                    # Let's examine the main data structure directly
                    print(f"\n=== Examining main data structure ===")
                    print(f"data[0] type: {type(data[0])}, length: {len(data[0])}")
                    print(f"data[0][1] type: {type(data[0][1])}, length: {len(data[0][1])}")

                    # Check if data[0][1] has the real place data
                    if isinstance(data[0][1], list) and len(data[0][1]) > 0:
                        print(f"data[0][1][0] type: {type(data[0][1][0])}, length: {len(data[0][1][0])}")
                        direct_place_data = data[0][1][0]

                        if len(direct_place_data) > 20:
                            print(f"\n=== Found real place data with {len(direct_place_data)} elements ===")
                            # Check specific indices we're trying to extract
                            print(f"Index 14 (rating): {direct_place_data[14]}")
                            print(f"Index 15 (reviews): {direct_place_data[15]}")
                            print(f"Index 12 (coords): {direct_place_data[12]}")
                            print(f"Index 8 (address parts): {len(direct_place_data[8]) if isinstance(direct_place_data[8], list) else direct_place_data[8]}")
                            print(f"Index 17 (place_id): {direct_place_data[17]}")
                            print(f"Index 20 (category): {direct_place_data[20]}")
                        else:
                            print(f"data[0][1][0] has only {len(direct_place_data)} elements, need different structure")

                    # Let's also check if there are other elements in data[0][1]
                    if len(data[0][1]) > 1:
                        print(f"\n=== Checking other elements in data[0][1] ===")
                        for i, element in enumerate(data[0][1][:3]):  # Check first 3 elements
                            print(f"data[0][1][{i}] type: {type(element)}, length: {len(element) if isinstance(element, list) else 'N/A'}")
                            if isinstance(element, list) and len(element) > 20:
                                print(f"  -> Found longer array at data[0][1][{i}] with {len(element)} elements")
                                # Check key indices
                                print(f"  Index 14 (rating): {element[14]}")
                                print(f"  Index 15 (reviews): {element[15]}")
                                print(f"  Index 17 (place_id): {element[17]}")

                    # Let's check other elements in data[0]
                    print(f"\n=== Checking other elements in data[0] ===")
                    for i, element in enumerate(data[0][:12]):  # data[0] has 12 elements
                        if isinstance(element, list) and len(element) > 20:
                            print(f"data[0][{i}] has {len(element)} elements - checking for place data")
                            # Check key indices
                            try:
                                print(f"  Index 14: {element[14]}")
                                print(f"  Index 15: {element[15]}")
                                print(f"  Index 17: {element[17]}")
                                if ':' in str(element[17]):  # Found place ID
                                    print(f"  -> FOUND PLACE DATA in data[0][{i}]!")
                            except:
                                pass

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_actual_place_data())