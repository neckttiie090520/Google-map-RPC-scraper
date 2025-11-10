#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Maps Scraper - Flask Web Application
===========================================

Direct Python-based web application without API layer.
UI calls scraper functions directly.

Author: Nextzus
Date: 2025-11-10
"""
import sys
import os

# Fix Windows encoding
if sys.platform == 'win32':
    os.system('chcp 65001 > nul 2>&1')

from flask import Flask, render_template, request, jsonify, session
from datetime import datetime
import asyncio
import threading
import uuid
import json

# Import scraper modules
from src.search.rpc_place_search import create_rpc_search, PlaceResult
from src.scraper.production_scraper import create_production_scraper
from src.utils.output_manager import output_manager

# Create Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)

# In-memory task storage
active_tasks = {}
task_lock = threading.Lock()


class ScraperTask:
    """Task object to track scraping progress"""
    def __init__(self, task_id, place_id, place_name, settings):
        self.task_id = task_id
        self.place_id = place_id
        self.place_name = place_name
        self.settings = settings
        self.status = "pending"
        self.progress = 0
        self.total_reviews = 0
        self.scraped_reviews = 0
        self.message = "กำลังเตรียมการ..."
        self.reviews = []
        self.error = None
        self.started_at = datetime.now()
        self.completed_at = None


def run_async(coro):
    """Run async function in new event loop"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


async def scrape_task_async(task_id, place_id, place_name, settings):
    """Async scraping task"""
    task = active_tasks.get(task_id)
    if not task:
        return

    try:
        task.status = "running"
        task.message = f"กำลัง scrape รีวิวจาก {place_name}..."

        # Create scraper
        scraper = create_production_scraper(
            language=settings.get('language', 'th'),
            region=settings.get('region', 'th')
        )

        # Scrape reviews
        max_reviews = settings.get('max_reviews', 100)
        date_range = settings.get('date_range', '1year')

        task.message = f"กำลังดึงรีวิว (สูงสุด {max_reviews} รีวิว)..."
        task.progress = 10

        # Call scraper once - it handles pagination internally
        try:
            result = await scraper.scrape_reviews(
                place_id=place_id,
                max_reviews=max_reviews,
                date_range=date_range
            )

            reviews = []

            if result and 'reviews' in result:
                # Convert ProductionReview objects to dicts and map fields
                review_objs = result['reviews']
                for review_obj in review_objs:
                    if hasattr(review_obj, '__dict__'):
                        review_dict = review_obj.__dict__
                    else:
                        review_dict = review_obj

                    # Map ProductionReview fields to output_manager format
                    mapped_review = {
                        'review_id': review_dict.get('review_id', ''),
                        'author': review_dict.get('author_name', ''),
                        'rating': review_dict.get('rating', 0),
                        'text': review_dict.get('review_text', ''),
                        'date': review_dict.get('date_formatted', ''),
                        'date_relative': review_dict.get('date_relative', ''),
                        'language': review_dict.get('language', ''),
                        'helpful_count': review_dict.get('helpful_count', 0),
                        'response_text': review_dict.get('response_text', ''),
                        'response_date': review_dict.get('response_date', ''),
                        'author_url': review_dict.get('author_url', ''),
                        'page_number': review_dict.get('page_number', 0)
                    }
                    reviews.append(mapped_review)

                # Update task metadata
                if 'metadata' in result:
                    metadata = result['metadata']
                    task.total_reviews = metadata.get('total_reviews', len(reviews))
                else:
                    task.total_reviews = len(reviews)

                task.scraped_reviews = len(reviews)
                task.progress = 90

        except Exception as e:
            print(f"Error scraping: {e}")
            import traceback
            traceback.print_exc()
            raise

        task.reviews = reviews
        task.scraped_reviews = len(reviews)
        task.progress = 100
        task.status = "completed"
        task.message = f"เสร็จสิ้น! ดึงรีวิวได้ {len(reviews)} รีวิว"
        task.completed_at = datetime.now()

        # Save results
        try:
            file_paths = output_manager.save_reviews(
                reviews=reviews,
                place_id=place_id,
                place_name=place_name,
                settings=settings
            )
            task.output_files = file_paths
        except Exception as e:
            print(f"Error saving results: {e}")

    except Exception as e:
        task.status = "failed"
        task.error = str(e)
        task.message = f"เกิดข้อผิดพลาด: {str(e)}"
        print(f"Task {task_id} failed: {e}")


def scrape_task_worker(task_id, place_id, place_name, settings):
    """Worker thread for scraping"""
    run_async(scrape_task_async(task_id, place_id, place_name, settings))


@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')


@app.route('/search', methods=['POST'])
def search_places():
    """Search for places"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        max_results = data.get('max_results', 10)
        language = data.get('language', 'th')
        region = data.get('region', 'th')

        # Create search service
        search_service = create_rpc_search(language=language, region=region)

        # Search places
        places = run_async(search_service.search_places(query, max_results))

        # Convert to dict
        places_data = [p.__dict__ for p in places]

        return jsonify({
            'success': True,
            'total': len(places_data),
            'places': places_data
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/scrape', methods=['POST'])
def start_scrape():
    """Start scraping task"""
    try:
        data = request.get_json()
        place_id = data.get('place_id')
        place_name = data.get('place_name', 'Unknown')
        settings = data.get('settings', {})

        if not place_id:
            return jsonify({'success': False, 'error': 'Place ID required'}), 400

        # Create task
        task_id = str(uuid.uuid4())
        task = ScraperTask(task_id, place_id, place_name, settings)

        with task_lock:
            active_tasks[task_id] = task

        # Start background thread
        thread = threading.Thread(
            target=scrape_task_worker,
            args=(task_id, place_id, place_name, settings)
        )
        thread.daemon = True
        thread.start()

        return jsonify({
            'success': True,
            'task_id': task_id,
            'message': 'เริ่ม scraping แล้ว'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/status/<task_id>')
def get_status(task_id):
    """Get task status"""
    task = active_tasks.get(task_id)

    if not task:
        return jsonify({
            'success': False,
            'error': 'Task not found'
        }), 404

    return jsonify({
        'success': True,
        'task_id': task_id,
        'status': task.status,
        'progress': task.progress,
        'message': task.message,
        'total_reviews': task.total_reviews,
        'scraped_reviews': task.scraped_reviews,
        'error': task.error,
        'started_at': task.started_at.isoformat() if task.started_at else None,
        'completed_at': task.completed_at.isoformat() if task.completed_at else None
    })


@app.route('/tasks')
def get_tasks():
    """Get all tasks"""
    tasks_data = []

    with task_lock:
        for task_id, task in active_tasks.items():
            tasks_data.append({
                'task_id': task_id,
                'place_name': task.place_name,
                'status': task.status,
                'progress': task.progress,
                'scraped_reviews': task.scraped_reviews,
                'started_at': task.started_at.isoformat() if task.started_at else None
            })

    return jsonify({
        'success': True,
        'tasks': tasks_data
    })


@app.route('/results/<task_id>')
def get_results(task_id):
    """Get task results"""
    task = active_tasks.get(task_id)

    if not task:
        return jsonify({
            'success': False,
            'error': 'Task not found'
        }), 404

    if task.status != 'completed':
        return jsonify({
            'success': False,
            'error': 'Task not completed yet'
        }), 400

    return jsonify({
        'success': True,
        'task_id': task_id,
        'place_name': task.place_name,
        'reviews': task.reviews,
        'total': len(task.reviews),
        'output_files': getattr(task, 'output_files', None)
    })


if __name__ == '__main__':
    print("=" * 80)
    print("Google Maps Scraper - Flask Web Application")
    print("=" * 80)
    print("\nStarting server on http://localhost:5000")
    print("\nPress Ctrl+C to stop\n")

    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
