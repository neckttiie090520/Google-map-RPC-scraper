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
from src.utils.thai_provinces import (
    get_all_provinces, get_province_data, enhance_search_query_with_province,
    get_province_suggestions, get_popular_search_terms, validate_province_search
)

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
    """Get all completed tasks from active_tasks and outputs directory"""
    history = []

    # First, get completed tasks from active_tasks (memory)
    for task_id, task in active_tasks.items():
        if task.get('status') == 'completed':
            # Create history entry from active task
            task_info = {
                'task_id': task_id,
                'status': task.get('status', 'unknown'),
                'place_name': task.get('place_info', {}).get('name', 'Unknown Place'),
                'place_address': task.get('place_info', {}).get('address', ''),
                'place_rating': task.get('place_info', {}).get('rating', 0),
                'total_reviews': len(task.get('result', {}).get('reviews', [])),
                'created_at': task.get('created_at', datetime.now().isoformat()),
                'completed_at': task.get('completed_at', task.get('created_at')),
                'settings': task.get('settings', {}),
                'output_dir': f"outputs/{task_id}",
                'source': 'memory'
            }
            history.append(task_info)

    # Second, get tasks from outputs directory (persisted data)
    if OUTPUT_DIR.exists():
        for task_dir in sorted(OUTPUT_DIR.iterdir(), reverse=True):
            if task_dir.is_dir():
                # Skip if we already have this task from memory
                task_id = task_dir.name
                if not any(h['task_id'] == task_id for h in history):
                    metadata_file = task_dir / "metadata.json"
                    if metadata_file.exists():
                        try:
                            with open(metadata_file, 'r', encoding='utf-8') as f:
                                metadata = json.load(f)
                                metadata['task_id'] = task_id
                                metadata['output_dir'] = str(task_dir)
                                metadata['source'] = 'file'
                                # Set status to 'completed' for tasks loaded from files
                                metadata['status'] = 'completed'
                                history.append(metadata)
                        except:
                            pass

    # Sort by created_at (newest first)
    history.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    return history


LANGUAGE_REGION_PRESETS = {
    'th': ('th', 'th'),
    'thai': ('th', 'th'),
    'th-th': ('th', 'th'),
    'en': ('en', 'th'),      # Default English output with Thai locale
    'english': ('en', 'th'),
    'en-th': ('en', 'th'),
    'en-us': ('en', 'us'),
    'en-sg': ('en', 'sg'),
    'en-gb': ('en', 'gb'),
    'ja': ('ja', 'jp'),
    'ja-jp': ('ja', 'jp'),
    'zh': ('zh-CN', 'cn'),
    'zh-cn': ('zh-CN', 'cn'),
}


def split_language_region(combined: str) -> tuple:
    """Split combined language-region into separate language and region"""
    if not combined:
        return 'th', 'th'

    key = combined.lower()
    if key in LANGUAGE_REGION_PRESETS:
        return LANGUAGE_REGION_PRESETS[key]

    if '-' in key:
        lang, region = key.split('-', 1)
        return lang or 'th', region or 'th'

    # Fallback to Thai locale if unknown
    return 'th', 'th'


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
    """Search for places with language consistency fix"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        max_results = data.get('max_results', 10)

        # Handle combined language-region setting
        language_region = data.get('language_region', 'th')
        language, region = split_language_region(language_region)

        if not query:
            return jsonify({'error': 'Query is required'}), 400

        print(f"[DEBUG] Search request: query='{query}', language='{language}', region='{region}', max_results={max_results}")

        # Create search service
        try:
            if not SEARCH_AVAILABLE:
                return jsonify({
                    'success': False,
                    'error': 'Search service not available'
                }), 500

            search_service = create_rpc_search(language=language, region=region)
            print(f"[DEBUG] Using original RPC search for language='{language}', region='{region}'")

        except Exception as e:
            print(f"[ERROR] Failed to create search service: {e}")
            return jsonify({
                'success': False,
                'error': f'Failed to create search service: {str(e)}'
            }), 500

        # Search places with proper async handling
        def run_async(coro):
            """Run async function in new event loop"""
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                print(f"[DEBUG] Starting async search...")
                result = loop.run_until_complete(coro)
                print(f"[DEBUG] Async search completed, found {len(result)} results")
                return result
            finally:
                loop.close()

        try:
            results = run_async(search_service.search_places(query, max_results=max_results))
            print(f"[DEBUG] Search completed successfully: {len(results)} results found")
        except Exception as e:
            print(f"[ERROR] Search failed: {e}")
            return jsonify({
                'success': False,
                'error': f'Search failed: {str(e)}'
            }), 500

        # Debug: Check the raw PlaceResult objects before conversion
        for i, result in enumerate(results):
            try:
                print(f"[DEBUG] PlaceResult {i}: ID='{result.place_id}', Name='{result.name}'")
            except UnicodeEncodeError:
                ascii_name = result.name.encode('ascii', errors='replace').decode('ascii')
                print(f"[DEBUG] PlaceResult {i}: ID='{result.place_id}', Name='{ascii_name}' (Thai encoded)")

        # Convert to dict (handle both simple and original search results)
        try:
            # Try to convert PlaceResult objects to dict
            places = [p.__dict__ for p in results]
        except:
            # Fallback: try to extract basic fields
            places = []
            for result in results:
                try:
                    place_dict = {
                        'place_id': getattr(result, 'place_id', ''),
                        'name': getattr(result, 'name', ''),
                        'address': getattr(result, 'address', ''),
                        'rating': getattr(result, 'rating', 0),
                        'total_reviews': getattr(result, 'total_reviews', 0),
                        'category': getattr(result, 'category', ''),
                        'latitude': getattr(result, 'latitude', 0),
                        'longitude': getattr(result, 'longitude', 0),
                        'url': getattr(result, 'url', '')
                    }
                    places.append(place_dict)
                except Exception as e:
                    print(f"[ERROR] Failed to convert place: {e}")
                    continue

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


# ==================== API ROUTES - THAI PROVINCES ====================

@app.route('/api/thai-provinces', methods=['GET'])
def get_thai_provinces():
    """Get list of Thai provinces with data"""
    try:
        provinces = get_all_provinces()
        provinces_data = {}

        for province_name in provinces:
            data = get_province_data(province_name)
            if data:
                provinces_data[province_name] = {
                    'region': data['region'],
                    'aliases': data.get('aliases', []),
                    'keywords': data.get('search_keywords', [])[:3],  # แสดง 3 คำแรก
                    'examples': data.get('examples', [])[:2]  # แสดง 2 ตัวอย่าง
                }

        return jsonify({
            'success': True,
            'provinces': provinces_data,
            'count': len(provinces)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get provinces: {str(e)}'
        }), 500


@app.route('/api/thai-provinces/suggestions', methods=['GET'])
def get_province_suggestions():
    """Get province suggestions based on query"""
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({
                'success': True,
                'suggestions': []
            })

        suggestions = get_province_suggestions(query)

        # เพิ่มข้อมูลเพิ่มเติมสำหรับ suggestions
        enhanced_suggestions = []
        for province in suggestions:
            data = get_province_data(province)
            if data:
                enhanced_suggestions.append({
                    'province': province,
                    'aliases': data.get('aliases', []),
                    'keywords': data.get('search_keywords', [])[:2]
                })

        return jsonify({
            'success': True,
            'suggestions': enhanced_suggestions
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get suggestions: {str(e)}'
        }), 500


@app.route('/api/thai-provinces/validate', methods=['POST'])
def validate_province():
    """Validate province search parameters"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        province = data.get('province', '').strip()

        is_valid, message = validate_province_search(query, province)

        if is_valid and province:
            enhanced_query = enhance_search_query_with_province(query, province)
            province_data = get_province_data(province)

            return jsonify({
                'success': True,
                'valid': True,
                'message': message,
                'enhanced_query': enhanced_query,
                'province_data': {
                    'name': province,
                    'region': province_data['region'] if province_data else 'th',
                    'aliases': province_data.get('aliases', []) if province_data else []
                }
            })
        else:
            return jsonify({
                'success': True,
                'valid': is_valid,
                'message': message
            })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to validate: {str(e)}'
        }), 500


@app.route('/api/thai-provinces/popular-searches', methods=['GET'])
def get_popular_searches():
    """Get popular search terms for Thai provinces"""
    try:
        limit = int(request.args.get('limit', 15))
        terms = get_popular_search_terms()

        return jsonify({
            'success': True,
            'popular_searches': terms[:limit]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get popular searches: {str(e)}'
        }), 500


# ==================== API ROUTES - SETTINGS ====================

@app.route('/api/settings', methods=['GET'])
def api_load_settings():
    """Load settings from .env file"""
    try:
        # Path to .env file
        env_path = Path(__file__).parent.parent / '.env'

        # Default settings
        settings = {
            'max_search_results': 10,
            'max_reviews': 100,
            'unlimited_reviews': False,
            'date_range': '1year',
            'start_date': None,
            'end_date': None,
            'auto_save': True,
            'show_notifications': True,
            'auto_refresh': True,
            'default_export': 'csv',
            'language_region': 'en-th',
            'enable_translation': False,
            'target_language': 'th',
            'translate_review_text': True,
            'translate_owner_response': False,
            'translation_batch_size': 50,
            'use_enhanced_detection': True
        }

        # Read from .env if exists
        if env_path.exists():
            with open(env_path, 'r', encoding='utf-8') as f:
                env_content = f.read()

            # Parse .env file
            env_mappings = {
                'MAX_SEARCH_RESULTS': 'max_search_results',
                'DEFAULT_MAX_REVIEWS': 'max_reviews',
                'DEFAULT_DATE_RANGE': 'date_range',
                'CUSTOM_START_DATE': 'start_date',
                'CUSTOM_END_DATE': 'end_date',
                'AUTO_SAVE': 'auto_save',
                'SHOW_NOTIFICATIONS': 'show_notifications',
                'AUTO_REFRESH': 'auto_refresh',
                'DEFAULT_EXPORT': 'default_export',
                'LANGUAGE_REGION': 'language_region',
                'ENABLE_TRANSLATION': 'enable_translation',
                'TARGET_LANGUAGE': 'target_language',
                'TRANSLATE_REVIEW_TEXT': 'translate_review_text',
                'TRANSLATE_OWNER_RESPONSE': 'translate_owner_response',
                'TRANSLATION_BATCH_SIZE': 'translation_batch_size',
                'USE_ENHANCED_DETECTION': 'use_enhanced_detection'
            }

            for line in env_content.split('\n'):
                line = line.strip()
                if '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()

                    if key in env_mappings:
                        setting_key = env_mappings[key]

                        # Convert string values to appropriate types
                        if setting_key in ['auto_save', 'show_notifications', 'auto_refresh', 'enable_translation', 'translate_review_text', 'translate_owner_response', 'use_enhanced_detection', 'unlimited_reviews']:
                            settings[setting_key] = value.lower() in ('true', '1', 'yes', 'on')
                        elif setting_key in ['max_search_results', 'max_reviews', 'translation_batch_size']:
                            try:
                                settings[setting_key] = int(value)
                            except ValueError:
                                pass  # Keep default value
                        elif setting_key in ['start_date', 'end_date'] and value.lower() in ('null', 'none', ''):
                            settings[setting_key] = None
                        else:
                            settings[setting_key] = value

        return jsonify({
            'success': True,
            'settings': settings
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


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
            'default_export': 'DEFAULT_EXPORT',
            'enable_translation': 'ENABLE_TRANSLATION',
            'target_language': 'TARGET_LANGUAGE',
            'translate_review_text': 'TRANSLATE_REVIEW_TEXT',
            'translate_owner_response': 'TRANSLATE_OWNER_RESPONSE',
            'translation_batch_size': 'TRANSLATION_BATCH_SIZE',
            'use_enhanced_detection': 'USE_ENHANCED_DETECTION'
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
            'current_place': None,
            # Translation settings for UI display
            'translation_enabled': settings.get('enable_translation', False),
            'target_language': settings.get('target_language', 'th'),
            'translation_status': 'pending' if settings.get('enable_translation', False) else 'disabled',
            'translation_progress': '0%',
            'detected_languages': {},
            'translated_count': 0
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

@app.route('/api/history/reviews')
def api_history_reviews():
    """Get all reviews from all completed tasks for history page"""
    try:
        all_reviews = []
        task_details = {}

        # First, collect reviews from memory (active_tasks)
        for task_id, task in active_tasks.items():
            if task.get('status') == 'completed' and 'result' in task and 'reviews' in task['result']:
                reviews = task['result']['reviews']
                place_info = task['result'].get('place_info', {})
                created_at = task.get('created_at', datetime.now().isoformat())

                # Store task details for reference
                task_details[task_id] = {
                    'place_name': place_info.get('name', 'Unknown Place'),
                    'place_address': place_info.get('address', ''),
                    'created_at': created_at,
                    'total_reviews': len(reviews)
                }

                # Add task information to each review
                for review in reviews:
                    enhanced_review = review.copy()
                    enhanced_review.update({
                        'task_id': task_id,
                        'place_name': place_info.get('name', 'Unknown Place'),
                        'place_address': place_info.get('address', ''),
                        'place_rating': place_info.get('rating', 0),
                        'total_reviews': place_info.get('total_reviews', 0),
                        'scraped_at': created_at
                    })

                    # Add translation information if available
                    if 'translation_info' in task['result']:
                        translation_info = task['result']['translation_info']
                        enhanced_review.update({
                            'translation_enabled': translation_info.get('enabled', False),
                            'target_language': translation_info.get('target_language', ''),
                            'original_language': translation_info.get('detected_languages', {}).get(review.get('review_id'), ''),
                            'translation_stats': translation_info.get('stats', {})
                        })

                    all_reviews.append(enhanced_review)

        # Second, collect reviews from JSON files in outputs directory
        outputs_path = Path(__file__).parent.parent / "outputs"
        if outputs_path.exists():
            # Look for task directories in outputs
            for task_dir in outputs_path.iterdir():
                if task_dir.is_dir():
                    # Check for reviews.json
                    reviews_file = task_dir / "reviews.json"
                    metadata_file = task_dir / "metadata.json"

                    if reviews_file.exists():
                        try:
                            # Read reviews from JSON file
                            with open(reviews_file, 'r', encoding='utf-8') as f:
                                task_data = json.load(f)

                            # Handle different JSON structures
                            reviews = []
                            place_info = {}
                            created_at = task_dir.name  # Use directory name as fallback timestamp

                            if isinstance(task_data, list):
                                # Old format: direct list of reviews
                                reviews = task_data
                                if reviews:
                                    # Extract place info from first review
                                    first_review = reviews[0]
                                    place_info = {
                                        'name': first_review.get('place_name', 'Unknown Place'),
                                        'address': first_review.get('place_address', ''),
                                        'rating': first_review.get('place_rating', 0),
                                        'total_reviews': len(reviews)
                                    }
                            elif isinstance(task_data, dict):
                                # New format: structured data
                                if 'data' in task_data:
                                    # Latest format with data array
                                    reviews = task_data['data']
                                    place_info = task_data.get('place_info', {})
                                    settings = task_data.get('settings', {})
                                    created_at = task_data.get('scraped_at', created_at)
                                elif 'reviews' in task_data:
                                    # Format with reviews key
                                    reviews = task_data['reviews']
                                    place_info = task_data.get('place_info', {})
                                    created_at = task_data.get('created_at', created_at)

                            # Read metadata if available for additional info
                            if metadata_file.exists():
                                try:
                                    with open(metadata_file, 'r', encoding='utf-8') as f:
                                        metadata = json.load(f)
                                    settings = metadata.get('settings', {})
                                    created_at = metadata.get('created_at', created_at)

                                    # Update place info from metadata places
                                    if 'places' in metadata and metadata['places']:
                                        metadata_place = metadata['places'][0]
                                        place_info.update({
                                            'name': metadata_place.get('name', place_info.get('name', 'Unknown Place')),
                                            'address': metadata_place.get('address', place_info.get('address', '')),
                                            'rating': metadata_place.get('rating', place_info.get('rating', 0)),
                                            'total_reviews': metadata_place.get('total_reviews', place_info.get('total_reviews', len(reviews)))
                                        })
                                except Exception as e:
                                    print(f"[ERROR] Reading metadata for {task_dir.name}: {e}")

                            # Generate a task_id from directory name
                            task_id = task_dir.name if len(task_dir.name) > 10 else f"file_{len(task_details)}"

                            # Skip if this task_id already exists in memory (avoid duplicates)
                            if task_id not in task_details:
                                # Store task details
                                task_details[task_id] = {
                                    'place_name': place_info.get('name', 'Unknown Place'),
                                    'place_address': place_info.get('address', ''),
                                    'created_at': created_at,
                                    'total_reviews': len(reviews),
                                    'source': 'file'
                                }

                                # Add task information to each review
                                for review in reviews:
                                    enhanced_review = review.copy() if isinstance(review, dict) else {}
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

                        except Exception as e:
                            print(f"[ERROR] Reading reviews from {task_dir.name}: {e}")
                            continue

            # Also check outputs/reviews directory (date-based structure)
            reviews_dir = outputs_path / "reviews"
            if reviews_dir.exists():
                for date_dir in reviews_dir.iterdir():
                    if date_dir.is_dir():
                        # Look for JSON files in date directories
                        for json_file in date_dir.glob("*.json"):
                            try:
                                with open(json_file, 'r', encoding='utf-8') as f:
                                    task_data = json.load(f)

                                # Similar processing as above
                                reviews = []
                                place_info = {}
                                created_at = json_file.stem  # Use filename as timestamp

                                if isinstance(task_data, list):
                                    reviews = task_data
                                    if reviews:
                                        first_review = reviews[0]
                                        place_info = {
                                            'name': first_review.get('place_name', 'Unknown Place'),
                                            'address': first_review.get('place_address', ''),
                                            'rating': first_review.get('place_rating', 0),
                                            'total_reviews': len(reviews)
                                        }
                                elif isinstance(task_data, dict):
                                    if 'data' in task_data:
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
                                        enhanced_review = review.copy() if isinstance(review, dict) else {}
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

        # Add task information to each review
        for review in reviews:
            enhanced_review = review.copy() if isinstance(review, dict) else {}
            enhanced_review.update({
                                        'task_id': task_id,
                                        'place_name': place_info.get('name', 'Unknown Place'),
                                        'place_address': place_info.get('address', ''),
                                        'place_rating': place_info.get('rating', 0),
                                        'total_reviews': place_info.get('total_reviews', 0),
                                        'scraped_at': created_at,
                                        'source': 'file'
                                    })

#             # Ensure translation fields exist
#             if 'original_language' not in enhanced_review:
#                                         enhanced_review['original_language'] = enhanced_review.get('original_language', 'unknown')
#             if 'target_language' not in enhanced_review:
#                 enhanced_review['target_language'] = enhanced_review.get('target_language', 'none')
#                                 all_reviews.append(enhanced_review)
#                         except Exception as e:
#                             print(f"[ERROR] Reading reviews from {task_dir.name}: {e}")
#                             continue
# 
#         # Sort by scraped date (newest first)
#         all_reviews.sort(key=lambda x: x.get('scraped_at', ''), reverse=True)
# 
        return jsonify({
            'success': True,
            'reviews': all_reviews,
            'task_details': task_details,
            'total_reviews': len(all_reviews),
            'total_tasks': len(task_details)
        })

    except Exception as e:
        # Add logger import if not present
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error fetching review history: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'reviews': [],
            'task_details': {},
            'total_reviews': 0,
            'total_tasks': 0
        }), 500

@app.route('/api/history/export-csv')
def api_history_export_csv():
    """Export all reviews from history to CSV"""
    import io
    import csv

    try:
        # Get all reviews (reuse the logic from the reviews endpoint)
        all_reviews_response = api_history_reviews()
        all_reviews_data = all_reviews_response.get_json()

        if not all_reviews_data.get('success'):
            return jsonify({'error': 'Failed to retrieve reviews'}), 500

        reviews = all_reviews_data.get('reviews', [])

        # Create CSV content
        output = io.StringIO()
        writer = csv.writer(output)

        # Write comprehensive header
        header = [
            'Task ID', 'Place Name', 'Place Address', 'Place Rating', 'Total Reviews',
            'Review ID', 'Author Name', 'Author URL', 'Author Reviews Count',
            'Rating', 'Date Formatted', 'Date Relative', 'Review Text',
            'Review Likes', 'Review Photos Count', 'Owner Response',
            'Page Number', 'Scraped At', 'Translation Enabled',
            'Target Language', 'Original Language', 'Translated Text'
        ]
        writer.writerow(header)

        # Write reviews
        for review in reviews:
            writer.writerow([
                review.get('task_id', ''),
                review.get('place_name', ''),
                review.get('place_address', ''),
                review.get('place_rating', ''),
                review.get('total_reviews', ''),
                review.get('review_id', ''),
                review.get('author_name', ''),
                review.get('author_url', ''),
                review.get('author_reviews_count', ''),
                review.get('rating', ''),
                review.get('date_formatted', ''),
                review.get('date_relative', ''),
                review.get('review_text', ''),
                review.get('review_likes', ''),
                review.get('review_photos_count', ''),
                review.get('owner_response', ''),
                review.get('page_number', ''),
                review.get('scraped_at', ''),
                review.get('translation_enabled', ''),
                review.get('target_language', ''),
                review.get('original_language', ''),
                review.get('review_text_translated', '')
            ])

        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8-sig')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f"all_reviews_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )

    except Exception as e:
        # Add logger import if not present
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error exporting review history: {str(e)}")
        return jsonify({'error': str(e)}), 500


# ==================== BACKGROUND SCRAPING ====================

def run_scraping_task(task_id, places, settings):
    """Run scraping task in background"""
    try:
        # Update task status
        active_tasks[task_id]['status'] = 'running'
        add_log(task_id, 'info', 'Starting scraping task...')

        # Load default settings (same as Settings page)
        default_settings = {
            'max_search_results': 10,
            'language_region': 'en-th',
            'max_reviews': 100,
            'unlimited_reviews': False,
            'date_range': '1year',
            'start_date': None,
            'end_date': None,
            'auto_save': True,
            'show_notifications': True,
            'auto_refresh': True,
            'default_export': 'csv',
            'enable_translation': False,
            'target_language': 'th',
            'translate_review_text': True,
            'translate_owner_response': False,
            'translation_batch_size': 50,
            'use_enhanced_detection': True
        }

        # Merge with provided settings (same logic as Settings page)
        final_settings = { **default_settings, **settings }

        # Get settings with proper defaults
        max_reviews = final_settings.get('max_reviews', None)

        # Handle unified language-region setting
        language_region = final_settings.get('language_region', 'en-th')
        language, region = split_language_region(language_region)

        # Debug: Print settings to verify
        print(f"  Final settings: {final_settings}")
        print(f"  language_region: {language_region}")
        print(f"  split to -> language: {language}, region: {region}")

        date_range = final_settings.get('date_range', '1year')
        start_date = final_settings.get('start_date')
        end_date = final_settings.get('end_date')

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

            # Get translation settings for Phase 2
            enable_translation = final_settings.get('enable_translation', False)
            target_language = final_settings.get('target_language', 'th')
            translate_review_text = final_settings.get('translate_review_text', True)
            translate_owner_response = final_settings.get('translate_owner_response', False)
            translation_batch_size = final_settings.get('translation_batch_size', 50)
            use_enhanced_detection = final_settings.get('use_enhanced_detection', True)

            # Phase 1: Create scraper for RPC collection (NO translation during collection)
            scraper = create_production_scraper(
                language=language,
                region=region,
                fast_mode=True,
                enable_translation=False,  # IMPORTANT: No translation during RPC collection
                target_language=target_language,
                translate_review_text=False,  # Disable during collection
                translate_owner_response=False,  # Disable during collection
                translation_batch_size=translation_batch_size,
                use_enhanced_detection=use_enhanced_detection
            )

            # Define progress callback for Phase 1: RPC Collection
            def update_progress_rpc_collection(page_num, total_reviews):
                """Callback to update progress during RPC collection phase"""
                task_progress[task_id]['reviews_scraped'] = total_reviews
                task_progress[task_id]['current_page'] = page_num
                task_progress[task_id]['phase'] = 'rpc_collection'
                active_tasks[task_id]['total_reviews'] = total_reviews

            # Define progress callback for Phase 2: Translation Processing
            def update_progress_translation(translation_progress, detected_languages=None, translated_count=0):
                """Callback to update progress during translation phase"""
                task_progress[task_id]['translation_progress'] = translation_progress
                task_progress[task_id]['phase'] = 'translation'
                active_tasks[task_id]['translation_progress'] = translation_progress
                if detected_languages is not None:
                    active_tasks[task_id]['detected_languages'] = detected_languages
                if translated_count is not None:
                    active_tasks[task_id]['translated_count'] = translated_count

            # Determine max_reviews for this place
            if active_tasks[task_id]['is_unlimited']:
                # Unlimited mode - scrape all reviews from this place
                scraper_max_reviews = place_total_reviews if place_total_reviews > 0 else 10000
            else:
                # Limited mode - use user setting
                scraper_max_reviews = max_reviews if max_reviews else 10000

            # Log Phase 1: RPC Collection
            add_log(task_id, 'info', f'  Phase 1: RPC Collection - Collecting up to {scraper_max_reviews} reviews')
            if enable_translation:
                add_log(task_id, 'info', f'  Phase 2: Translation will be processed after collection (Target: {target_language})')
                active_tasks[task_id]['translation_status'] = 'pending'  # Will be processed in Phase 2

            # Scrape reviews
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            try:
                # Phase 1: RPC Collection (NO translation during this phase)
                add_log(task_id, 'info', f'  Starting RPC Collection for {place_name}...')
                result = loop.run_until_complete(
                    scraper.scrape_reviews(
                        place_id=place_id,
                        max_reviews=scraper_max_reviews,
                        date_range=date_range,
                        start_date=start_date,
                        end_date=end_date,
                        sort_by_newest=True,  # Always sort by newest
                        progress_callback=update_progress_rpc_collection  # RPC collection progress callback
                    )
                )

                reviews = result.get('reviews', [])

                # Add place info to each review
                for review in reviews:
                    review.place_id = place_id
                    review.place_name = place_name

                all_reviews.extend(reviews)

                # Update RPC collection progress
                active_tasks[task_id]['completed_places'] = idx + 1
                active_tasks[task_id]['total_reviews'] = len(all_reviews)
                task_progress[task_id]['reviews_scraped'] = len(all_reviews)

                # ASCII-safe success logging for Phase 1
                try:
                    add_log(task_id, 'success', f'  Phase 1 Complete: Collected {len(reviews)} reviews from {place_name}')
                except UnicodeEncodeError:
                    ascii_name = place_name.encode('ascii', errors='replace').decode('ascii')
                    add_log(task_id, 'success', f'  Phase 1 Complete: Collected {len(reviews)} reviews from {ascii_name} (Thai encoded)')

            except Exception as e:
                # ASCII-safe error logging
                try:
                    add_log(task_id, 'error', f'Failed to scrape {place_name}: {str(e)}')
                except UnicodeEncodeError:
                    ascii_name = place_name.encode('ascii', errors='replace').decode('ascii')
                    add_log(task_id, 'error', f'Failed to scrape {ascii_name}: {str(e)} (Thai encoded)')

            finally:
                loop.close()

        # PHASE 2: LANGUAGE DETECTION & ANALYSIS
        if enable_translation and all_reviews:
            add_log(task_id, 'info', f'Phase 2: Starting Language Detection & Analysis - {len(all_reviews)} total reviews collected')

            # Import translator utilities
            from src.utils.translator import BatchTranslator, detect_and_translate_reviews

            # Update task status for language detection phase
            active_tasks[task_id]['translation_status'] = 'detecting'
            task_progress[task_id]['phase'] = 'language_detection'

            try:
                # Create translator for detection only
                translator = BatchTranslator(target_language=target_language, batch_size=translation_batch_size)

                # Phase 2a: Language Detection Analysis
                add_log(task_id, 'info', f'  Phase 2a: Detecting languages and collecting review IDs...')

                review_ids_needing_translation = []
                languages_detected = {}
                detection_progress = 0

                for i, review in enumerate(all_reviews):
                    # Detect review text language
                    review_lang = 'unknown'
                    if review.review_text:
                        review_lang = translator.detect_language(review.review_text)
                        languages_detected[review_lang] = languages_detected.get(review_lang, 0) + 1

                    # Detect owner response language
                    owner_lang = 'unknown'
                    if review.owner_response:
                        owner_lang = translator.detect_language(review.owner_response)

                    # Check if translation is needed
                    review_needs_translation = (
                        (translate_review_text and translator.is_translation_needed(review.review_text, review_lang)) or
                        (translate_owner_response and translator.is_translation_needed(review.owner_response, owner_lang))
                    )

                    if review_needs_translation:
                        # Store original language info for later use
                        review.review_text_language = review_lang if review_lang != 'unknown' else None
                        review.owner_response_language = owner_lang if owner_lang != 'unknown' else None

                        # Add review_id to translation list
                        review_ids_needing_translation.append(review.review_id)

                    detection_progress = (i + 1) / len(all_reviews) * 100

                    # Update progress every 10 reviews
                    if (i + 1) % 10 == 0:
                        update_progress_translation(
                            translation_progress=detection_progress,
                            detected_languages=languages_detected,
                            translated_count=0  # No translations yet in Phase 2
                        )

                # Update final detection progress
                update_progress_translation(
                    translation_progress=100,
                    detected_languages=languages_detected,
                    translated_count=0
                )

                # Store detection results and review IDs list
                active_tasks[task_id]['detected_languages'] = languages_detected
                active_tasks[task_id]['review_ids_needing_translation'] = review_ids_needing_translation
                active_tasks[task_id]['reviews_needing_translation_count'] = len(review_ids_needing_translation)
                active_tasks[task_id]['total_reviews_collected'] = len(all_reviews)

                # Log Phase 2 results with review IDs
                add_log(task_id, 'success', f'  Phase 2a Complete: Language detection finished')
                add_log(task_id, 'info', f'  Total reviews analyzed: {len(all_reviews)}')
                add_log(task_id, 'info', f'  Languages detected: {dict(languages_detected)}')
                add_log(task_id, 'info', f'  Reviews needing translation: {len(review_ids_needing_translation)}')

                if review_ids_needing_translation:
                    # Log the specific review IDs that need translation
                    add_log(task_id, 'info', f'  Phase 2b: Review IDs requiring translation:')
                    for i, review_id in enumerate(review_ids_needing_translation):
                        if i < 10:  # Show first 10 IDs to avoid log spam
                            add_log(task_id, 'info', f'    - {review_id}')
                        elif i == 10:
                            add_log(task_id, 'info', f'    ... and {len(review_ids_needing_translation) - 10} more')
                            break

                    # Save review IDs list to file for Phase 3
                    translation_queue_file = task_dir / "translation_queue.json"
                    with open(translation_queue_file, 'w', encoding='utf-8') as f:
                        json.dump({
                            'task_id': task_id,
                            'target_language': target_language,
                            'translate_review_text': translate_review_text,
                            'translate_owner_response': translate_owner_response,
                            'translation_batch_size': translation_batch_size,
                            'review_ids_needing_translation': review_ids_needing_translation,
                            'detected_languages': languages_detected,
                            'created_at': datetime.now().isoformat()
                        }, f, ensure_ascii=False, indent=2)

                    add_log(task_id, 'info', f'  Translation queue saved to: translation_queue.json')

                    # Update task status to "ready for translation"
                    active_tasks[task_id]['translation_status'] = 'ready_for_translation'
                    task_progress[task_id]['phase'] = 'ready_for_translation'

                    add_log(task_id, 'info', f'  Ready to send {len(review_ids_needing_translation)} review IDs to translator')
                else:
                    add_log(task_id, 'success', f'  No translations needed - all reviews are already in target language')
                    active_tasks[task_id]['translation_status'] = 'completed'
                    active_tasks[task_id]['translated_count'] = 0

            except Exception as e:
                active_tasks[task_id]['translation_status'] = 'failed'
                add_log(task_id, 'error', f'Phase 2 Failed: Language detection error: {str(e)}')
                add_log(task_id, 'warning', 'Continuing with original reviews (no translation)...')

        elif enable_translation and not all_reviews:
            add_log(task_id, 'warning', 'Phase 2: No reviews collected - skipping language detection')

        # PHASE 3: TRANSLATION PROCESSING (Manual or Automatic)
        # This phase can be triggered manually by user or automatically if configured

        # Check if we should automatically proceed to Phase 3
        auto_proceed_to_translation = True  # Automatic translation after Phase 2 completion

        if (enable_translation and all_reviews and
            active_tasks[task_id].get('translation_status') == 'ready_for_translation' and
            auto_proceed_to_translation):

            add_log(task_id, 'info', f'Phase 3: Starting Automatic Translation Processing from Review IDs Queue')

            # Get the review IDs that need translation
            review_ids_needing_translation = active_tasks[task_id].get('review_ids_needing_translation', [])

            if not review_ids_needing_translation:
                add_log(task_id, 'warning', f'Phase 3: No review IDs found in translation queue')
                active_tasks[task_id]['translation_status'] = 'completed'
                active_tasks[task_id]['translated_count'] = 0
            else:
                # Update task status for translation phase
                active_tasks[task_id]['translation_status'] = 'processing'
                task_progress[task_id]['phase'] = 'translation'

                try:
                    add_log(task_id, 'info', f'Phase 3a: Sending {len(review_ids_needing_translation)} review IDs to translator...')

                    # Filter reviews to only those needing translation
                    reviews_to_translate = []
                    for review in all_reviews:
                        if review.review_id in review_ids_needing_translation:
                            reviews_to_translate.append(review)

                    add_log(task_id, 'info', f'Phase 3b: Found {len(reviews_to_translate)} reviews matching translation queue')

                    # Phase 3c: Process translations in batches (only for reviews that need translation)
                    translated_reviews = detect_and_translate_reviews(
                        reviews=reviews_to_translate,
                        target_language=target_language,
                        translate_review_text=translate_review_text,
                        translate_owner_response=translate_owner_response,
                        batch_size=translation_batch_size,
                        progress_callback=lambda current, total, detected_langs: update_progress_translation(
                            translation_progress=(current / total) * 100,
                            detected_languages=detected_langs,
                            translated_count=current
                        )
                    )

                    # Create a dictionary of translated reviews by review_id for quick lookup
                    translated_dict = {review.review_id: review for review in translated_reviews}

                    # Merge translated reviews back into the original all_reviews list
                    final_reviews = []
                    translated_count = 0

                    for review in all_reviews:
                        if review.review_id in translated_dict:
                            # Use the translated version
                            final_reviews.append(translated_dict[review.review_id])
                            translated_count += 1
                        else:
                            # Use the original version (no translation needed)
                            final_reviews.append(review)

                    # Replace all_reviews with the merged version
                    all_reviews = final_reviews

                    # Update translation completion status
                    active_tasks[task_id]['translation_status'] = 'completed'
                    active_tasks[task_id]['translated_count'] = translated_count

                    add_log(task_id, 'success', f'Phase 3 Complete: Translation finished for {translated_count} reviews')
                    add_log(task_id, 'info', f'Phase 3: Total reviews in final output: {len(all_reviews)}')

                except Exception as e:
                    active_tasks[task_id]['translation_status'] = 'failed'
                    add_log(task_id, 'error', f'Phase 3 Failed: Translation processing error: {str(e)}')
                    add_log(task_id, 'warning', 'Reviews remain untranslated due to error...')

        elif (enable_translation and all_reviews and
              active_tasks[task_id].get('translation_status') == 'ready_for_translation'):
            add_log(task_id, 'info', f'Phase 3: Translation processing ready - {len(active_tasks[task_id].get("review_ids_needing_translation", []))} review IDs queued')
            add_log(task_id, 'info', f'Reviews ready for translation: {active_tasks[task_id].get("reviews_needing_translation_count", 0)}')

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
        port=5001,
        debug=True,
        threaded=True
    )
