#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Inspect Sort PB Parameter
==========================

Use browser to click "Newest" sort and capture the pb parameter
that Google uses for sorting.

Author: Nextzus
Date: 2025-11-10
"""
import asyncio
import re
from urllib.parse import unquote, parse_qs, urlparse

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("Error: playwright not installed")
    print("Install with: pip install playwright")
    print("Then run: playwright install chromium")
    exit(1)


async def inspect_sort_parameter():
    """Inspect pb parameter when sorting by newest"""

    print("=" * 80)
    print("INSPECT SORT PB PARAMETER")
    print("=" * 80)
    print()

    # Use Central World Bangkok as test place
    place_url = "https://www.google.com/maps/place/Central+World/@13.7469126,100.5376163,17z/data=!3m1!4b1!4m6!3m5!1s0x30e29ecfc2f455e1:0xc4ad0280d8906604!8m2!3d13.7469126!4d100.5401912!16zL20vMDN0dHl3?entry=ttu"

    async with async_playwright() as p:
        print("Launching browser...")
        browser = await p.chromium.launch(headless=False)  # Show browser
        context = await browser.new_context()
        page = await context.new_page()

        # Store captured requests
        rpc_requests = []

        # Listen to network requests
        async def capture_request(request):
            if "listugcposts" in request.url:
                rpc_requests.append({
                    'url': request.url,
                    'headers': request.headers
                })
                print(f"\n[CAPTURED] RPC Request")
                print(f"URL: {request.url[:100]}...")

        page.on("request", capture_request)

        print(f"\nNavigating to: {place_url}")
        await page.goto(place_url, wait_until="networkidle")

        print("\nWaiting for page to load...")
        await asyncio.sleep(3)

        # Click on Reviews tab
        print("\nLooking for Reviews tab...")
        try:
            # Try different selectors for Reviews button
            selectors = [
                'button[aria-label*="Reviews"]',
                'button:has-text("Reviews")',
                '[role="tab"]:has-text("Reviews")',
                'button:has-text("รีวิว")',  # Thai
            ]

            clicked = False
            for selector in selectors:
                try:
                    await page.click(selector, timeout=5000)
                    print(f"✓ Clicked Reviews tab")
                    clicked = True
                    break
                except:
                    continue

            if not clicked:
                print("⚠ Could not find Reviews tab, continuing...")
            else:
                await asyncio.sleep(2)
        except Exception as e:
            print(f"⚠ Reviews tab click failed: {e}")

        # Clear previous requests
        rpc_requests.clear()

        # Look for Sort dropdown
        print("\nLooking for Sort dropdown...")
        try:
            # Try different selectors for Sort button
            sort_selectors = [
                'button[aria-label*="Sort"]',
                'button:has-text("Sort")',
                'button:has-text("Most relevant")',
                'button[data-value]',
                '[role="button"]:has-text("Most relevant")',
            ]

            clicked_sort = False
            for selector in sort_selectors:
                try:
                    await page.click(selector, timeout=5000)
                    print(f"✓ Clicked Sort dropdown")
                    clicked_sort = True
                    break
                except:
                    continue

            if not clicked_sort:
                print("⚠ Could not find Sort dropdown")
                print("\nManual steps:")
                print("1. Click on Reviews tab")
                print("2. Click on Sort dropdown (usually says 'Most relevant')")
                print("3. Click 'Newest'")
                print("\nPress Enter when done...")
                input()
            else:
                await asyncio.sleep(1)

                # Click "Newest" option
                print("\nLooking for 'Newest' option...")
                newest_selectors = [
                    '[role="menuitemradio"]:has-text("Newest")',
                    '[role="option"]:has-text("Newest")',
                    'div:has-text("Newest")',
                    '[data-index="1"]',  # Usually second option
                ]

                clicked_newest = False
                for selector in newest_selectors:
                    try:
                        await page.click(selector, timeout=5000)
                        print(f"✓ Clicked 'Newest' option")
                        clicked_newest = True
                        break
                    except:
                        continue

                if not clicked_newest:
                    print("⚠ Could not find 'Newest' option")
                    print("\nPlease manually click 'Newest' and press Enter...")
                    input()

        except Exception as e:
            print(f"⚠ Sort dropdown interaction failed: {e}")
            print("\nPlease manually:")
            print("1. Click Sort dropdown")
            print("2. Select 'Newest'")
            print("3. Press Enter here when done...")
            input()

        # Wait for new requests after sorting
        print("\nWaiting for RPC requests after sorting...")
        await asyncio.sleep(3)

        # Analyze captured requests
        print("\n" + "=" * 80)
        print("CAPTURED REQUESTS ANALYSIS")
        print("=" * 80)
        print()

        if not rpc_requests:
            print("⚠ No RPC requests captured!")
            print("\nPlease check if:")
            print("1. The page loaded correctly")
            print("2. Reviews are visible")
            print("3. Sort was changed to 'Newest'")
        else:
            print(f"Total RPC requests captured: {len(rpc_requests)}")
            print()

            for i, req in enumerate(rpc_requests, 1):
                print(f"Request #{i}:")
                print("-" * 80)

                # Parse URL
                parsed = urlparse(req['url'])
                params = parse_qs(parsed.query)

                if 'pb' in params:
                    pb = params['pb'][0]
                    print(f"PB Parameter:")
                    print(f"{pb}")
                    print()

                    # Look for sort indicators
                    if '!7i1' in pb:
                        print("✓ Found !7i1 - This might be 'Newest' sort")
                    elif '!7i2' in pb:
                        print("✓ Found !7i2 - This might be 'Highest rating' sort")
                    elif '!7i3' in pb:
                        print("✓ Found !7i3 - This might be 'Lowest rating' sort")
                    elif '!7e81' in pb:
                        print("✓ Found !7e81 - This is 'Most relevant' (default)")
                    else:
                        print("⚠ No known sort parameter found")

                    print()

                    # Decode pb to make it more readable
                    try:
                        decoded = unquote(pb)
                        print(f"Decoded PB:")
                        print(f"{decoded}")
                        print()
                    except:
                        pass

                print()

        print("=" * 80)
        print("Keeping browser open for inspection...")
        print("Press Enter to close browser...")
        print("=" * 80)
        input()

        await browser.close()


if __name__ == "__main__":
    asyncio.run(inspect_sort_parameter())
