#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick start script for Google Maps Scraper
"""
import sys
import os

# Fix Windows encoding
if sys.platform == 'win32':
    os.system('chcp 65001 > nul 2>&1')

if __name__ == '__main__':
    print("=" * 80)
    print("Google Maps Scraper - Starting...")
    print("=" * 80)
    print()

    # Check if running from correct directory
    if not os.path.exists('app.py'):
        print("Error: Please run this script from the project root directory")
        sys.exit(1)

    # Import and run the Flask app
    from app import app

    print("Server starting on http://localhost:5000")
    print("Press Ctrl+C to stop")
    print()

    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
