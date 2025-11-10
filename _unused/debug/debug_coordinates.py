#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import asyncio
import json

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.search.rpc_place_search import create_rpc_search

async def debug_coordinates():
    """Debug coordinate extraction from Go-style business data"""

    rpc_search = create_rpc_search()
    query = "ข้าวซอยนิมมาน"

    try:
        try:
            print(f"=== Debugging coordinates for: {query} ===")
        except:
            print("=== Debugging coordinates for: [Thai query] ===")

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

                # Get the business data like our Go-style extraction
                if (isinstance(data, list) and len(data) > 0 and
                    isinstance(data[0], list) and len(data[0]) > 1 and
                    isinstance(data[0][1], list) and len(data[0][1]) > 0 and
                    isinstance(data[0][1][0], list) and len(data[0][1][0]) > 14):

                    business_data = data[0][1][0][14]
                    print(f"Business data length: {len(business_data)}")

                    # Check coordinates at index 9
                    if len(business_data) > 9:
                        coords_section = business_data[9]
                        print(f"Coordinates section (index 9): {coords_section}")
                        print(f"Type: {type(coords_section)}")
                        if isinstance(coords_section, list):
                            print(f"Length: {len(coords_section)}")
                            for i, coord_part in enumerate(coords_section):
                                print(f"  coords_section[{i}]: {repr(coord_part)} (type: {type(coord_part).__name__})")

                    # Check if coordinates are elsewhere
                    print(f"\n=== Searching for coordinates in business_data ===")
                    for i in range(len(business_data)):
                        item = business_data[i]
                        if isinstance(item, list) and len(item) >= 2:
                            # Check if this looks like coordinates (two numbers)
                            if (isinstance(item[0], (int, float)) and isinstance(item[1], (int, float)) and
                                -90 <= float(item[0]) <= 90 and -180 <= float(item[1]) <= 180):
                                print(f"Found coordinates at index {i}: {item}")
                            elif len(item) > 2:
                                # Check if nested coordinates
                                for j, subitem in enumerate(item):
                                    if (isinstance(subitem, (int, float)) and
                                        -90 <= float(subitem) <= 90):
                                        print(f"Found possible coordinate at index {i}[{j}]: {subitem}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_coordinates())