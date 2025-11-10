#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Google Maps Scraper - Kanit Redesign Flask App
Enhanced UI with Google-style design and Kanit font support
"""

import sys
import os
import json
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.exceptions import HTTPException

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.search.rpc_place_search import create_rpc_search, PlaceResult

app = Flask(__name__)
app.secret_key = 'google-maps-scraper-secret-key'

# Configure Jinja2
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

# Mock data for demo when backend is not available
MOCK_TASKS = {}
MOCK_RESULTS = {}

class MockJobManager:
    """Mock job manager for demonstration purposes"""

    @staticmethod
    def generate_task_id():
        import uuid
        return str(uuid.uuid4())

    @staticmethod
    def create_mock_results(place_name, place_id):
        """Generate mock results for demonstration"""
        import random

        reviews = []
        for i in range(random.randint(10, 50)):
            reviews.append({
                'author': f'User {i+1}',
                'rating': random.randint(1, 5),
                'text': f'This is review {i+1} for {place_name}. Great place to visit!',
                'date': (datetime.now().strftime('%Y-%m-%d')),
                'helpful': random.randint(0, 100)
            })

        return {
            'place_id': place_id,
            'place_name': place_name,
            'total_reviews': len(reviews),
            'average_rating': round(random.uniform(3.0, 5.0), 1),
            'reviews': reviews,
            'scraped_at': datetime.now().isoformat()
        }

@app.route('/')
def index():
    """Main page with Kanit redesign"""
    return render_template('kanit-redesign.html')

@app.route('/search', methods=['POST'])
def search_places():
    """Search for places using RPC or mock data"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        max_results = data.get('max_results', 5)
        language = data.get('language', 'th')
        region = data.get('region', 'th')

        if not query:
            return jsonify({'success': False, 'error': 'Query is required'})

        # Try to use actual RPC search
        try:
            rpc_search = create_rpc_search()
            places = rpc_search.search_places(
                query=query,
                max_results=max_results,
                language=language,
                region=region
            )

            return jsonify({
                'success': True,
                'places': [place.__dict__ for place in places]
            })

        except Exception as e:
            print(f"RPC search failed, using mock data: {e}")

            # Fallback to mock data
            mock_places = [
                PlaceResult(
                    place_id=f"mock_{query.replace(' ', '_')}",
                    name=f"{query} (Mock)",
                    address=f"123 Mock Street, Bangkok, Thailand",
                    rating=4.2,
                    total_reviews=1250,
                    category="Restaurant",
                    url=f"https://maps.google.com/?q={query}",
                    latitude=13.7563,
                    longitude=100.5018
                )
            ]

            return jsonify({
                'success': True,
                'places': [place.__dict__ for place in mock_places]
            })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/scrape', methods=['POST'])
def start_scraping():
    """Start a scraping job"""
    try:
        data = request.get_json()
        place_id = data.get('place_id')
        place_name = data.get('place_name', 'Unknown Place')
        settings = data.get('settings', {})

        if not place_id:
            return jsonify({'success': False, 'error': 'Place ID is required'})

        # Generate task ID
        task_id = MockJobManager.generate_task_id()

        # Store job info
        MOCK_TASKS[task_id] = {
            'task_id': task_id,
            'place_id': place_id,
            'place_name': place_name,
            'status': 'pending',
            'progress': 0,
            'message': 'Initializing...',
            'scraped_reviews': 0,
            'total_reviews': None,
            'created_at': datetime.now().isoformat(),
            'settings': settings
        }

        # Start mock job progression
        start_mock_job_progression(task_id, place_name, place_id)

        return jsonify({
            'success': True,
            'task_id': task_id,
            'message': 'Scraping job started'
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/status/<task_id>')
def get_task_status(task_id):
    """Get the status of a scraping task"""
    try:
        # Check if it's a mock task
        if task_id in MOCK_TASKS:
            return jsonify({
                'success': True,
                **MOCK_TASKS[task_id]
            })

        # Try to get real task status
        return jsonify({
            'success': False,
            'error': 'Task not found'
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/tasks')
def list_tasks():
    """List all tasks"""
    try:
        # Return mock tasks
        tasks = []
        for task_id, task in MOCK_TASKS.items():
            tasks.append({
                'task_id': task_id,
                'place_name': task['place_name'],
                'status': task['status'],
                'progress': task['progress'],
                'scraped_reviews': task.get('scraped_reviews', 0),
                'created_at': task['created_at'],
                'completed_at': task.get('completed_at')
            })

        return jsonify({
            'success': True,
            'tasks': sorted(tasks, key=lambda x: x['created_at'], reverse=True)
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/results/<task_id>')
def get_results(task_id):
    """Get results for a task"""
    try:
        if task_id in MOCK_RESULTS:
            return jsonify({
                'success': True,
                'results': MOCK_RESULTS[task_id]
            })

        return jsonify({
            'success': False,
            'error': 'Results not found'
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/download/<task_id>')
def download_results(task_id):
    """Download results as JSON file"""
    try:
        if task_id in MOCK_RESULTS:
            results = MOCK_RESULTS[task_id]
            filename = f"{results['place_name'].replace(' ', '_')}_results.json"

            # Create a temporary file
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
                temp_path = f.name

            return send_from_directory(
                os.path.dirname(temp_path),
                os.path.basename(temp_path),
                as_attachment=True,
                download_name=filename
            )

        return jsonify({'success': False, 'error': 'Results not found'})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

def start_mock_job_progression(task_id, place_name, place_id):
    """Start mock job progression in background"""
    import threading
    import time

    def progress_job():
        try:
            total_steps = 10
            time.sleep(1)  # Initial delay

            # Start running
            MOCK_TASKS[task_id]['status'] = 'running'
            MOCK_TASKS[task_id]['message'] = 'Starting scraper...'

            for step in range(1, total_steps + 1):
                time.sleep(2)  # 2 seconds per step

                progress = (step / total_steps) * 100
                messages = [
                    'Initializing scraper...',
                    'Fetching place details...',
                    'Searching for reviews...',
                    'Parsing review data...',
                    'Processing ratings...',
                    'Extracting user information...',
                    'Compiling results...',
                    'Validating data...',
                    'Formatting output...',
                    'Finalizing results...'
                ]

                MOCK_TASKS[task_id].update({
                    'progress': int(progress),
                    'message': messages[min(step - 1, len(messages) - 1)],
                    'scraped_reviews': step * 5
                })

            # Generate mock results
            MOCK_RESULTS[task_id] = MockJobManager.create_mock_results(place_name, place_id)

            # Mark as completed
            MOCK_TASKS[task_id].update({
                'status': 'completed',
                'progress': 100,
                'message': 'Scraping completed successfully',
                'scraped_reviews': MOCK_RESULTS[task_id]['total_reviews'],
                'total_reviews': MOCK_RESULTS[task_id]['total_reviews'],
                'completed_at': datetime.now().isoformat()
            })

        except Exception as e:
            MOCK_TASKS[task_id].update({
                'status': 'failed',
                'message': f'Error: {str(e)}',
                'error': str(e),
                'completed_at': datetime.now().isoformat()
            })

    # Start background thread
    thread = threading.Thread(target=progress_job, daemon=True)
    thread.start()

@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'error': 'Internal server error'}), 500

@app.errorhandler(Exception)
def handle_exception(e):
    """Handle all uncaught exceptions"""
    if isinstance(e, HTTPException):
        return jsonify({'success': False, 'error': e.description}), e.code

    print(f"Unhandled exception: {e}")
    return jsonify({'success': False, 'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("\n" + "="*80)
    print("Google Maps Scraper - Kanit Redesign")
    print("="*80)
    print("Enhanced UI with Google-style design and Kanit font")
    print("Features:")
    print("   • Modern, clean interface with Google Material Design")
    print("   • Kanit font for Thai language support")
    print("   • Real-time job progress tracking")
    print("   • Log drawer for detailed job monitoring")
    print("   • Export functionality (JSON/CSV)")
    print("   • Mock job demo when backend unavailable")
    print("   • Keyboard navigation (Ctrl+K for search)")
    print("="*80)
    print("Starting server on http://localhost:5000")
    print("Press Ctrl+C to stop")
    print("="*80 + "\n")

    # Run Flask app
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    )