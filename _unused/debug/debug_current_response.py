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

async def debug_current_response():
    """Debug current response to see what we're actually getting"""

    rpc_search = create_rpc_search()
    query = "ข้าวซอยนิมมาน"

    try:
        # Build the request exactly like the search method does
        url = "https://www.google.com/search"
        params = rpc_search.build_search_params(query, lat=18.7883, lon=98.9853)
        headers = rpc_search.generate_headers()

        try:
            print(f"Making request to: {url}")
        except:
            print("Making request to: [URL]")

        try:
            print(f"Query: {query}")
        except:
            print("Query: [Thai query]")

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, params=params, headers=headers)

            print(f"Status: {response.status_code}")
            print(f"Content length: {len(response.text)}")

            # Save response
            with open('current_response.html', 'w', encoding='utf-8') as f:
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

                        if len(data) > 1:
                            print(f"Second element type: {type(data[1])}")
                            if isinstance(data[1], list):
                                print(f"Second element length: {len(data[1])}")
                                # Look for Place ID in second element
                                for i, item in enumerate(data[1]):
                                    if isinstance(item, str) and '0x' in item and ':' in item:
                                        print(f"Found potential Place ID at index {i}: {item}")
                                        break

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
    asyncio.run(debug_current_response())