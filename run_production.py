#!/usr/bin/env python3
"""
Production server runner - Flask with auto-reload disabled
"""
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Set encoding for Windows
if sys.platform == 'win32':
    os.system('chcp 65001 > nul 2>&1')

from webapp.app import app

if __name__ == '__main__':
    print("======================================================================")
    print("GOOGLE MAPS RPC SCRAPER - PRODUCTION SERVER")
    print("======================================================================")
    print("Starting Flask web server with auto-reload DISABLED...")
    print("Open: http://localhost:5000")
    print("======================================================================")

    # Run with auto-reload disabled
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)