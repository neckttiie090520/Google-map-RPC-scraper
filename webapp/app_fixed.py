#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Maps RPC Scraper - Flask Web Application (Fixed Version)
==============================================================

Fixed version of the webapp with proper JSON file loading.
"""

import sys
import os

# Fix Windows encoding
if sys.platform == 'win32':
    os.system('chcp 65001 > nul 2>&1')

from flask import Flask, render_template, request, jsonify, Response, send_file
from flask_cors import CORS
import asyncio
import json
import uuid
from datetime import datetime
from pathlib import Path
import threading
import queue
import logging

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

# Import the original working RPC search
try:
    from src.search.rpc_place_search import create_rpc_search
    SEARCH_AVAILABLE = True
    SEARCH_TYPE = "original"
    print("[INFO] Using original working RPC search")
except ImportError:
    SEARCH_AVAILABLE = False
    SEARCH_TYPE = "none"
    print("[ERROR] RPC search service not available")

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# In-memory storage for tasks and progress
active_tasks = {}
task_progress = {}
completed_tasks = []


def build_history_summary(reviews, task_details):
    """
    Build aggregated summary for dashboards/quick overview.

    Args:
        reviews (list[dict]): Flattened review entries.
        task_details (dict): Metadata keyed by task_id.

    Returns:
        dict: Summary slices (counts, language distribution, place ranking, recency).
    """
    summary = {
        'total_reviews': len(reviews),
        'total_tasks': len(task_details),
        'language_counts': {},
        'places': [],
        'recent_tasks': []
    }

    if not reviews:
        return summary

    # Language stats (default unknown)
    for review in reviews:
        lang = review.get('original_language') or 'unknown'
        summary['language_counts'][lang] = summary['language_counts'].get(lang, 0) + 1

    # Aggregate by place
    place_stats = {}
    for review in reviews:
        place_key = review.get('place_name', 'Unknown Place')
        stats = place_stats.setdefault(place_key, {'count': 0, 'tasks': set()})
        stats['count'] += 1
        stats['tasks'].add(review.get('task_id'))

    summary['places'] = sorted(
        [
            {
                'place_name': name,
                'review_count': data['count'],
                'tasks_involved': len(data['tasks'])
            }
            for name, data in place_stats.items()
        ],
        key=lambda item: item['review_count'],
        reverse=True
    )

    # Highlight latest tasks (top 5)
    recent = sorted(
        [
            {
                'task_id': task_id,
                'place_name': meta.get('place_name', 'Unknown Place'),
                'created_at': meta.get('created_at'),
                'total_reviews': meta.get('total_reviews', 0)
            }
            for task_id, meta in task_details.items()
        ],
        key=lambda item: item.get('created_at') or '',
        reverse=True
    )
    summary['recent_tasks'] = recent[:5]

    return summary

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/history/reviews')
def api_history_reviews():
    """Get all reviews from all completed tasks for history page"""
    try:
        all_reviews = []
        task_details = {}

        # Collect reviews from JSON files in outputs directory
        outputs_path = Path(__file__).parent.parent / "outputs"
        print(f"[DEBUG] Looking for outputs in: {outputs_path}")

        if outputs_path.exists():
            # 1. Check task directories (new format)
            for task_dir in outputs_path.iterdir():
                if task_dir.is_dir() and len(task_dir.name) > 5:  # Likely a task ID
                    reviews_file = task_dir / "reviews.json"
                    metadata_file = task_dir / "metadata.json"

                    if reviews_file.exists():
                        try:
                            print(f"[DEBUG] Reading reviews from: {reviews_file}")
                            with open(reviews_file, 'r', encoding='utf-8') as f:
                                task_data = json.load(f)

                            # Handle different JSON structures
                            reviews = []
                            place_info = {}
                            created_at = task_dir.name

                            if isinstance(task_data, dict) and 'data' in task_data:
                                # Latest format with data array
                                reviews = task_data['data']
                                place_info = task_data.get('place_info', {})
                                created_at = task_data.get('scraped_at', created_at)
                                settings = task_data.get('settings', {})
                            elif isinstance(task_data, list):
                                # Old format: direct list of reviews
                                reviews = task_data
                                if reviews:
                                    first_review = reviews[0]
                                    place_info = {
                                        'name': first_review.get('place_name', 'Unknown Place'),
                                        'address': first_review.get('place_address', ''),
                                        'rating': first_review.get('place_rating', 0),
                                        'total_reviews': len(reviews)
                                    }

                            # Read metadata if available
                            if metadata_file.exists():
                                try:
                                    with open(metadata_file, 'r', encoding='utf-8') as f:
                                        metadata = json.load(f)
                                    settings = metadata.get('settings', {})
                                    created_at = metadata.get('created_at', created_at)

                                    if 'places' in metadata and metadata['places']:
                                        metadata_place = metadata['places'][0]
                                        place_info.update({
                                            'name': metadata_place.get('name', place_info.get('name', 'Unknown Place')),
                                            'address': metadata_place.get('address', place_info.get('address', '')),
                                            'rating': metadata_place.get('rating', place_info.get('rating', 0)),
                                            'total_reviews': metadata_place.get('total_reviews', place_info.get('total_reviews', len(reviews)))
                                        })
                                except Exception as e:
                                    print(f"[ERROR] Reading metadata: {e}")

                            task_id = task_dir.name
                            task_details[task_id] = {
                                'place_name': place_info.get('name', 'Unknown Place'),
                                'place_address': place_info.get('address', ''),
                                'created_at': created_at,
                                'total_reviews': len(reviews),
                                'source': 'file'
                            }

                            # Add task information to each review
                            for review in reviews:
                                if not isinstance(review, dict):
                                    continue

                                enhanced_review = review.copy()
                                enhanced_review.update({
                                    'task_id': task_id,
                                    'place_name': place_info.get('name', 'Unknown Place'),
                                    'place_address': place_info.get('address', ''),
                                    'place_rating': place_info.get('rating', 0),
                                    'total_reviews': place_info.get('total_reviews', 0),
                                    'scraped_at': created_at,
                                    'source': 'file'
                                })

                                # Ensure translation fields exist
                                if 'original_language' not in enhanced_review:
                                    enhanced_review['original_language'] = enhanced_review.get('original_language', 'unknown')
                                if 'target_language' not in enhanced_review:
                                    enhanced_review['target_language'] = enhanced_review.get('target_language', 'none')

                                all_reviews.append(enhanced_review)

                            print(f"[DEBUG] Loaded {len(reviews)} reviews from {task_dir.name}")

                        except Exception as e:
                            print(f"[ERROR] Reading {task_dir.name}: {e}")
                            continue

            # 2. Check outputs/reviews directory (date-based structure)
            reviews_dir = outputs_path / "reviews"
            if reviews_dir.exists():
                for date_dir in reviews_dir.iterdir():
                    if date_dir.is_dir():
                        for json_file in date_dir.glob("*.json"):
                            try:
                                with open(json_file, 'r', encoding='utf-8') as f:
                                    task_data = json.load(f)

                                reviews = []
                                place_info = {}
                                created_at = f"{date_dir.name}_{json_file.stem}"

                                if isinstance(task_data, dict) and 'data' in task_data:
                                    reviews = task_data['data']
                                    place_info = task_data.get('place_info', {})
                                    created_at = task_data.get('scraped_at', created_at)

                                task_id = f"{date_dir.name}_{json_file.stem}"
                                if task_id not in task_details:
                                    task_details[task_id] = {
                                        'place_name': place_info.get('name', 'Unknown Place'),
                                        'place_address': place_info.get('address', ''),
                                        'created_at': created_at,
                                        'total_reviews': len(reviews),
                                        'source': 'file_date'
                                    }

                                    for review in reviews:
                                        if not isinstance(review, dict):
                                            continue

                                        enhanced_review = review.copy()
                                        enhanced_review.update({
                                            'task_id': task_id,
                                            'place_name': place_info.get('name', 'Unknown Place'),
                                            'place_address': place_info.get('address', ''),
                                            'place_rating': place_info.get('rating', 0),
                                            'total_reviews': place_info.get('total_reviews', 0),
                                            'scraped_at': created_at,
                                            'source': 'file_date'
                                        })

                                        if 'original_language' not in enhanced_review:
                                            enhanced_review['original_language'] = enhanced_review.get('original_language', 'unknown')
                                        if 'target_language' not in enhanced_review:
                                            enhanced_review['target_language'] = enhanced_review.get('target_language', 'none')

                                        all_reviews.append(enhanced_review)

                            except Exception as e:
                                print(f"[ERROR] Reading {json_file}: {e}")
                                continue

        # Sort by scraped date (newest first)
        all_reviews.sort(key=lambda x: x.get('scraped_at', ''), reverse=True)

        print(f"[DEBUG] Total reviews loaded: {len(all_reviews)}")
        print(f"[DEBUG] Total tasks: {len(task_details)}")

        summary = build_history_summary(all_reviews, task_details)

        return jsonify({
            'success': True,
            'reviews': all_reviews,
            'task_details': task_details,
            'total_reviews': len(all_reviews),
            'total_tasks': len(task_details),
            'summary': summary
        })

    except Exception as e:
        logger.error(f"Error fetching review history: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'reviews': [],
            'task_details': {},
            'total_reviews': 0,
            'total_tasks': 0,
            'summary': build_history_summary([], {})
        }), 500


@app.route('/api/history/summary')
def api_history_summary():
    """Lightweight endpoint returning only summary analytics."""
    # Reuse logic without duplicating file parsing
    response = api_history_reviews()
    if isinstance(response, tuple):
        # Error path bubble-up
        return response

    payload = response.get_json(force=True)
    summary = payload.get('summary', build_history_summary([], {}))
    return jsonify({
        'success': payload.get('success', False),
        'summary': summary
    })

@app.route('/api/test/reviews')
def test_reviews():
    """Test endpoint to verify JSON loading"""
    try:
        # Just test reading one specific file
        test_file = Path(__file__).parent.parent / "outputs/20251111_145658_5088147b/reviews.json"
        if test_file.exists():
            with open(test_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            return jsonify({
                'success': True,
                'file_exists': True,
                'data_type': type(data).__name__,
                'review_count': len(data) if isinstance(data, list) else len(data.get('data', [])),
                'sample_review': data[0] if isinstance(data, list) and data else None
            })
        else:
            return jsonify({
                'success': False,
                'file_exists': False,
                'message': f'Test file not found: {test_file}'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    print("Starting Google Maps Scraper Web Application (Fixed Version)")
    print("Available endpoints:")
    print("  GET  /api/history/reviews - Get all reviews from JSON files")
    print("  GET  /api/history/summary - Get aggregated quick summary")
    print("  GET  /api/test/reviews - Test JSON file reading")
    print("  GET  / - Main page")

    app.run(debug=True, host='0.0.0.0', port=5000)
