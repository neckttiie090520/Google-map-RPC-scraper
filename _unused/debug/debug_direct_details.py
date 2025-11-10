#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import asyncio

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.search.rpc_place_search import create_rpc_search

async def debug_direct_result_details():
    """Debug direct result to see what data we're extracting"""

    rpc_search = create_rpc_search()
    query = "ข้าวซอยนิมมาน"

    try:
        try:
            print(f"=== DEBUG: Direct result details for: {query} ===")
        except:
            print("=== DEBUG: Direct result details for: [Thai query] ===")
        results = await rpc_search.search_places(query, max_results=5, lat=18.7883, lon=98.9853)

        print(f"Results found: {len(results)}")
        for i, place in enumerate(results, 1):
            print(f"\n--- Place {i} ---")
            try:
                print(f"Name: {place.name}")
            except:
                print("Name: [Thai name]")
            print(f"Place ID: {place.place_id}")
            print(f"Rating: {place.rating}")
            print(f"Total Reviews: {place.total_reviews}")
            try:
                print(f"Address: {place.address}")
            except:
                print("Address: [Thai address]")
            try:
                print(f"Category: {place.category}")
            except:
                print("Category: [Thai category]")
            print(f"URL: {place.url}")
            print(f"Coordinates: {place.latitude}, {place.longitude}")

            # Check if values are empty or zero
            if not place.total_reviews:
                print("WARNING: Review count is EMPTY or ZERO")
            if not place.address or place.address == "":
                print("WARNING: Address is EMPTY")
            if place.rating == 0.0:
                print("WARNING: Rating is ZERO")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_direct_result_details())