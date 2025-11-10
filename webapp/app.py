#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Maps RPC Scraper - Flask Web Application
================================================

Modern, user-friendly web interface for Google Maps review scraping.

Author: Nextzus
Date: 2025-11-10
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

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from src.scraper.production_scraper import create_production_scraper
from src.search.rpc_place_search import create_rpc_search

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'google-maps-scraper-secret-key-2025'
app.config['JSON_AS_ASCII'] = False
CORS(app)

# Global storage for tasks and progress
active_tasks = {}
task_progress = {}
task_logs = {}

# Output directory
OUTPUT_DIR = Path(__file__).parent.parent / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)


# ==================== HELPER FUNCTIONS ====================

def get_task_history():
    """Get all completed tasks from outputs directory"""
    history = []

    if OUTPUT_DIR.exists():
        for task_dir in sorted(OUTPUT_DIR.iterdir(), reverse=True):
            if task_dir.is_dir():
                metadata_file = task_dir / "metadata.json"
                if metadata_file.exists():
                    try:
                        with open(metadata_file, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                            metadata['task_id'] = task_dir.name
                            metadata['output_dir'] = str(task_dir)
                            history.append(metadata)
                    except:
                        pass

    return history


def split_language_region(combined: str) -> tuple:
    """Split combined language-region into separate language and region"""
    if combined == 'th':
        return 'th', 'th'
    elif combined == 'en':
        return 'en', 'us'
    else:
        return 'th', 'th'  # default fallback


def create_task_id():
    """Create unique task ID with timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    short_id = str(uuid.uuid4())[:8]
    return f"{timestamp}_{short_id}"


# ==================== ROUTES - PAGES ====================

@app.route('/')
def index():
    """Home page - redirect to search"""
    return render_template('index.html')


@app.route('/search')
def search_page():
    """Search page - place search interface"""
    return render_template('search.html')


@app.route('/pick')
def pick_page():
    """Pick page - select places to scrape"""
    return render_template('pick.html')


@app.route('/tasks')
def tasks_page():
    """Tasks page - monitor active scraping tasks"""
    return render_template('tasks.html')


@app.route('/results/<task_id>')
def results_page(task_id):
    """Results page - view scraping results"""
    return render_template('results.html', task_id=task_id)


@app.route('/history')
def history_page():
    """History page - view past tasks"""
    history = get_task_history()
    return render_template('history.html', history=history)


@app.route('/settings')
def settings_page():
    """Settings page - configure scraper settings"""
    return render_template('settings.html')


# ==================== API ROUTES - SEARCH ====================

@app.route('/api/search', methods=['POST'])
def api_search():
    """Search for places"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        max_results = data.get('max_results', 10)

        # Handle combined language-region setting
        language_region = data.get('language_region', 'th')
        language, region = split_language_region(language_region)

        if not query:
            return jsonify({'error': 'Query is required'}), 400

        # Create search service (using same approach as working original UI)
        search_service = create_rpc_search(language=language, region=region)

        # Search places using the same approach as working original UI
        def run_async(coro):
            """Run async function in new event loop"""
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(coro)
            finally:
                loop.close()

        results = run_async(search_service.search_places(query, max_results=max_results))

        # Debug: Check the raw PlaceResult objects before conversion
        for i, result in enumerate(results):
            try:
                print(f"[DEBUG] PlaceResult {i}: ID='{result.place_id}', Name='{result.name}'")
            except UnicodeEncodeError:
                ascii_name = result.name.encode('ascii', errors='replace').decode('ascii')
                print(f"[DEBUG] PlaceResult {i}: ID='{result.place_id}', Name='{ascii_name}' (Thai encoded)")

        # Convert to dict using exact same approach as working original UI
        places = [p.__dict__ for p in results]

        # Debug logging - check for missing place_ids with encoding fix
        for place in places:
            place_id = place.get('place_id', '')
            place_name = place.get('name', 'Unknown')
            if not place_id:
                continue
            else:
                # Use ASCII-safe encoding for Thai text to prevent charmap errors
                try:
                    print(f"[DEBUG] Found place_id: {place_id} for place: {place_name}")
                except UnicodeEncodeError:
                    ascii_name = place_name.encode('ascii', errors='replace').decode('ascii')
                    print(f"[DEBUG] Found place_id: {place_id} for place: {ascii_name} (Thai text encoded)")

        return jsonify({
            'success': True,
            'query': query,
            'count': len(places),
            'places': places
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ==================== API ROUTES - SETTINGS ====================

@app.route('/api/settings', methods=['POST'])
def api_save_settings():
    """Save settings to .env file"""
    try:
        data = request.get_json()
        settings = data.get('settings', {})

        # Path to .env file
        env_path = Path(__file__).parent.parent / '.env'

        # Read existing .env or create new content
        env_content = []
        if env_path.exists():
            with open(env_path, 'r', encoding='utf-8') as f:
                env_content = f.readlines()

        # Settings to save (mapping from JS settings to .env format)
        env_mappings = {
            'max_search_results': 'MAX_SEARCH_RESULTS',
            'max_reviews': 'DEFAULT_MAX_REVIEWS',
            'date_range': 'DEFAULT_DATE_RANGE',
            'start_date': 'CUSTOM_START_DATE',
            'end_date': 'CUSTOM_END_DATE',
            'auto_save': 'AUTO_SAVE',
            'show_notifications': 'SHOW_NOTIFICATIONS',
            'auto_refresh': 'AUTO_REFRESH',
            'default_export': 'DEFAULT_EXPORT'
        }

        # Handle unified language-region setting
        language_region_mappings = {
            'language_region': ('LANGUAGE_REGION', None)  # Unified setting
        }

        # Update or add settings
        updated_lines = []
        settings_updated = set()

        for line in env_content:
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                key, value = line.split('=', 1)
                # Check if this key should be updated
                updated = False
                for js_key, env_key in env_mappings.items():
                    if key.strip() == env_key and js_key in settings:
                        # Convert value to string representation
                        new_value = str(settings[js_key])
                        updated_lines.append(f"{env_key}={new_value}")
                        settings_updated.add(js_key)
                        updated = True
                        break

                # Check language-region mappings
                if not updated:
                    for js_key, (lang_env_key, region_env_key) in language_region_mappings.items():
                        if key.strip() in [lang_env_key, region_env_key] and js_key in settings:
                            combined_value = settings[js_key]
                            language, region = split_language_region(combined_value)
                            if key.strip() == lang_env_key:
                                updated_lines.append(f"{lang_env_key}={language}")
                            elif key.strip() == region_env_key:
                                updated_lines.append(f"{region_env_key}={region}")
                            settings_updated.add(js_key)
                            updated = True
                            break

                if not updated:
                    updated_lines.append(line)
            else:
                updated_lines.append(line)

        # Add new settings that weren't in the file
        for js_key, env_key in env_mappings.items():
            if js_key in settings and js_key not in settings_updated:
                value = str(settings[js_key])
                updated_lines.append(f"{env_key}={value}")

        # Handle language-region combined settings
        for js_key, (lang_env_key, region_env_key) in language_region_mappings.items():
            if js_key in settings and js_key not in settings_updated:
                combined_value = settings[js_key]
                language, region = split_language_region(combined_value)
                updated_lines.append(f"{lang_env_key}={language}")
                updated_lines.append(f"{region_env_key}={region}")

        # Write back to .env file
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(updated_lines))

        return jsonify({
            'success': True,
            'message': 'Settings saved to .env file successfully'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==================== API ROUTES - SCRAPING ====================

@app.route('/api/scrape', methods=['POST'])
def api_scrape():
    """Start scraping task"""
    try:
        data = request.get_json()
        places = data.get('places', [])
        settings = data.get('settings', {})

        if not places:
            return jsonify({'error': 'No places selected'}), 400

        # Create task
        task_id = create_task_id()

        # Calculate max_reviews based on settings
        # If unlimited (None or 0), use sum of total_reviews from all places
        user_max_reviews = settings.get('max_reviews')
        if user_max_reviews is None or user_max_reviews == 0 or user_max_reviews == '':
            # Unlimited mode - use total_reviews from places
            max_reviews_for_task = sum(place.get('total_reviews', 0) for place in places)
            is_unlimited = True
        else:
            max_reviews_for_task = user_max_reviews
            is_unlimited = False

        # Store task info
        active_tasks[task_id] = {
            'task_id': task_id,
            'places': places,
            'settings': settings,
            'status': 'pending',
            'created_at': datetime.now().isoformat(),
            'total_places': len(places),
            'completed_places': 0,
            'total_reviews': 0,
            'max_reviews': max_reviews_for_task,  # Store max_reviews for progress calculation
            'is_unlimited': is_unlimited,  # Flag to show unlimited mode
            'current_place': None
        }

        task_progress[task_id] = {
            'current_place_index': 0,
            'total_places': len(places),
            'reviews_scraped': 0,
            'status': 'starting'
        }

        task_logs[task_id] = []

        # Start scraping in background thread
        thread = threading.Thread(
            target=run_scraping_task,
            args=(task_id, places, settings)
        )
        thread.daemon = True
        thread.start()

        return jsonify({
            'success': True,
            'task_id': task_id,
            'message': 'Scraping task started'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/tasks/<task_id>/status')
def api_task_status(task_id):
    """Get task status"""
    if task_id not in active_tasks:
        return jsonify({'error': 'Task not found'}), 404

    task = active_tasks[task_id]
    progress = task_progress.get(task_id, {})
    logs = task_logs.get(task_id, [])

    return jsonify({
        'success': True,
        'task': task,
        'progress': progress,
        'logs': logs[-50:]  # Last 50 logs
    })


@app.route('/api/tasks/<task_id>/stream')
def api_task_stream(task_id):
    """Stream task progress via SSE"""

    def generate():
        """Generate SSE events"""
        while True:
            if task_id in active_tasks:
                task = active_tasks[task_id]
                progress = task_progress.get(task_id, {})
                logs = task_logs.get(task_id, [])

                data = {
                    'task': task,
                    'progress': progress,
                    'logs': logs[-10:]  # Last 10 logs
                }

                yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"

                # Stop if task completed or failed
                if task.get('status') in ['completed', 'failed']:
                    break
            else:
                break

            # Wait before next update
            import time
            time.sleep(1)

    return Response(generate(), mimetype='text/event-stream')


@app.route('/api/tasks')
def api_tasks():
    """Get all active tasks"""
    # Sort tasks by creation time (newest first)
    tasks = list(active_tasks.values())
    tasks.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    return jsonify({
        'success': True,
        'tasks': tasks
    })


# ==================== API ROUTES - RESULTS ====================

@app.route('/api/results/<task_id>')
def api_results(task_id):
    """Get task results"""
    try:
        task_dir = OUTPUT_DIR / task_id

        if not task_dir.exists():
            return jsonify({'error': 'Results not found'}), 404

        # Read metadata
        metadata_file = task_dir / "metadata.json"
        metadata = {}
        if metadata_file.exists():
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)

        # Read reviews JSON
        json_file = task_dir / "reviews.json"
        reviews = []
        if json_file.exists():
            with open(json_file, 'r', encoding='utf-8') as f:
                reviews = json.load(f)

        return jsonify({
            'success': True,
            'task_id': task_id,
            'metadata': metadata,
            'reviews': reviews,
            'total_reviews': len(reviews)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/results/<task_id>/download/<format>')
def api_download_results(task_id, format):
    """Download results in specified format"""
    try:
        task_dir = OUTPUT_DIR / task_id

        if not task_dir.exists():
            return jsonify({'error': 'Results not found'}), 404

        if format == 'csv':
            file_path = task_dir / "reviews.csv"
        elif format == 'json':
            file_path = task_dir / "reviews.json"
        else:
            return jsonify({'error': 'Invalid format'}), 400

        if not file_path.exists():
            return jsonify({'error': 'File not found'}), 404

        # Try to get place name for better filename
        place_name = "scraped_data"
        try:
            with open(task_dir / "metadata.json", 'r', encoding='utf-8') as f:
                metadata = json.load(f)
                if metadata.get('places') and len(metadata['places']) > 0:
                    first_place = metadata['places'][0]
                    place_name = first_place.get('name', 'scraped_data')
                    # Clean place name for filename
                    place_name = "".join(c for c in place_name if c.isalnum() or c in (' ', '-')).rstrip()
        except:
            pass

        # Set MIME type based on format
        if format == 'csv':
            mimetype = 'text/csv'
        elif format == 'json':
            mimetype = 'application/json'
        else:
            mimetype = 'application/octet-stream'

        return send_file(
            file_path,
            as_attachment=True,
            download_name=f"{place_name}_reviews_{task_id[:8]}.{format}",
            mimetype=mimetype
        )

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/history')
def api_history():
    """Get task history"""
    history = get_task_history()
    return jsonify({
        'success': True,
        'history': history,
        'total': len(history)
    })


# ==================== BACKGROUND SCRAPING ====================

def run_scraping_task(task_id, places, settings):
    """Run scraping task in background"""
    try:
        # Update task status
        active_tasks[task_id]['status'] = 'running'
        add_log(task_id, 'info', 'Starting scraping task...')

        # Get settings
        max_reviews = settings.get('max_reviews', None)

        # Handle unified language-region setting
        language_region = settings.get('language_region', 'th')
        language, region = split_language_region(language_region)

        # Debug: Print language settings to verify
        print(f"  language_region: {language_region}")
        print(f"  split to -> language: {language}, region: {region}")

        date_range = settings.get('date_range', '1year')
        start_date = settings.get('start_date')
        end_date = settings.get('end_date')

        # Debug: Print settings values
        print(f"  max_reviews: {max_reviews} (type: {type(max_reviews)})")
        print(f"  date_range: {date_range}")
        print(f"  language: {language}")
        print(f"  Full settings: {settings}")

        # Create output directory
        task_dir = OUTPUT_DIR / task_id
        task_dir.mkdir(exist_ok=True)

        all_reviews = []

        # Scrape each place
        for idx, place in enumerate(places):
            place_id = place.get('place_id', '')
            place_name = place.get('name', 'Unknown')
            place_total_reviews = place.get('total_reviews', 0)

            # Update progress
            active_tasks[task_id]['current_place'] = place_name
            task_progress[task_id]['current_place_index'] = idx

            # ASCII-safe progress logging
            try:
                add_log(task_id, 'info', f'Scraping place {idx + 1}/{len(places)}: {place_name}')
                if active_tasks[task_id]['is_unlimited']:
                    add_log(task_id, 'info', f'  Mode: Unlimited (place has {place_total_reviews} reviews)')
                else:
                    add_log(task_id, 'info', f'  Mode: Limited to {max_reviews} reviews')
            except UnicodeEncodeError:
                ascii_name = place_name.encode('ascii', errors='replace').decode('ascii')
                add_log(task_id, 'info', f'Scraping place {idx + 1}/{len(places)}: {ascii_name} (Thai encoded)')

            # Create scraper
            scraper = create_production_scraper(
                language=language,
                region=region,
                fast_mode=True
            )

            # Define progress callback to update task progress
            def update_progress(page_num, total_reviews):
                """Callback to update progress during scraping"""
                task_progress[task_id]['reviews_scraped'] = total_reviews
                task_progress[task_id]['current_page'] = page_num
                active_tasks[task_id]['total_reviews'] = total_reviews

            # Determine max_reviews for this place
            if active_tasks[task_id]['is_unlimited']:
                # Unlimited mode - scrape all reviews from this place
                scraper_max_reviews = place_total_reviews if place_total_reviews > 0 else 10000
            else:
                # Limited mode - use user setting
                scraper_max_reviews = max_reviews if max_reviews else 10000

            # Scrape reviews
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            try:
                result = loop.run_until_complete(
                    scraper.scrape_reviews(
                        place_id=place_id,
                        max_reviews=scraper_max_reviews,
                        date_range=date_range,
                        start_date=start_date,
                        end_date=end_date,
                        sort_by_newest=True,  # Always sort by newest
                        progress_callback=update_progress  # Add progress callback
                    )
                )

                reviews = result.get('reviews', [])

                # Add place info to each review
                for review in reviews:
                    review.place_id = place_id
                    review.place_name = place_name

                all_reviews.extend(reviews)

                # Update progress
                active_tasks[task_id]['completed_places'] = idx + 1
                active_tasks[task_id]['total_reviews'] = len(all_reviews)
                task_progress[task_id]['reviews_scraped'] = len(all_reviews)

                # ASCII-safe success logging
                try:
                    add_log(task_id, 'success', f'Scraped {len(reviews)} reviews from {place_name}')
                except UnicodeEncodeError:
                    ascii_name = place_name.encode('ascii', errors='replace').decode('ascii')
                    add_log(task_id, 'success', f'Scraped {len(reviews)} reviews from {ascii_name} (Thai encoded)')

            except Exception as e:
                # ASCII-safe error logging
                try:
                    add_log(task_id, 'error', f'Failed to scrape {place_name}: {str(e)}')
                except UnicodeEncodeError:
                    ascii_name = place_name.encode('ascii', errors='replace').decode('ascii')
                    add_log(task_id, 'error', f'Failed to scrape {ascii_name}: {str(e)} (Thai encoded)')

            finally:
                loop.close()

        # Save results
        add_log(task_id, 'info', 'Saving results...')

        # Save JSON
        json_file = task_dir / "reviews.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump([r.__dict__ for r in all_reviews], f, ensure_ascii=False, indent=2, default=str)

        # Save CSV
        if all_reviews:
            csv_file = task_dir / "reviews.csv"
            scraper.export_to_csv(all_reviews, str(csv_file))

        # Save metadata
        metadata = {
            'task_id': task_id,
            'created_at': active_tasks[task_id]['created_at'],
            'completed_at': datetime.now().isoformat(),
            'total_places': len(places),
            'total_reviews': len(all_reviews),
            'settings': settings,
            'places': places
        }

        metadata_file = task_dir / "metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        # Update task status
        active_tasks[task_id]['status'] = 'completed'
        active_tasks[task_id]['completed_at'] = datetime.now().isoformat()
        # ASCII-safe completion logging
        try:
            add_log(task_id, 'success', f'Task completed! Total reviews: {len(all_reviews)}')
        except UnicodeEncodeError:
            add_log(task_id, 'success', f'Task completed! Total reviews: {len(all_reviews)} (Thai encoded)')

    except Exception as e:
        active_tasks[task_id]['status'] = 'failed'
        active_tasks[task_id]['error'] = str(e)
        add_log(task_id, 'error', f'Task failed: {str(e)}')


def add_log(task_id, level, message):
    """Add log entry to task"""
    if task_id not in task_logs:
        task_logs[task_id] = []

    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'level': level,
        'message': message
    }

    task_logs[task_id].append(log_entry)

    # Print to console with ASCII-safe encoding
    try:
        print(f"[{level.upper()}] {message}")
    except UnicodeEncodeError:
        # Fallback to ASCII-safe encoding
        ascii_message = message.encode('ascii', errors='replace').decode('ascii')
        print(f"[{level.upper()}] {ascii_message} (Thai encoded)")


# ==================== RUN APP ====================

if __name__ == '__main__':
    print("=" * 70)
    print("GOOGLE MAPS RPC SCRAPER - WEB APP")
    print("=" * 70)
    print()
    print("Starting Flask web server...")
    print("Open: http://localhost:5000")
    print()
    print("=" * 70)

    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    )
