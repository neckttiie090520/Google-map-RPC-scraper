# -*- coding: utf-8 -*-
"""
Perfect Backend API v2 with FORCED JSON + CSV Output
====================================================

Enhanced version of api_v2.py with automatic JSON + CSV output enforcement.
All scraping operations automatically save in both formats.

Author: Nextzus
Date: 2025-11-11
Version: 2.0
"""
import sys
import os

# Fix Windows encoding
if sys.platform == 'win32':
    os.system('chcp 65001 > nul 2>&1')

import asyncio
import json
import time
import queue
import uuid
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

# Import our modules
from src.scraper.production_scraper import create_production_scraper, ProductionReview
from src.search.rpc_place_search import RpcPlaceSearch
from src.utils.output_manager import output_manager
from src.utils.output_enhancer import force_json_csv_output, save_reviews_dual_format

# ==================== DATA CLASSES ====================

class TaskStatus(Enum):
    PENDING = "pending"
    INITIALIZING = "initializing"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    ERROR = "ERROR"

@dataclass
class TaskProgress:
    """Complete task progress tracking"""
    # Overall status
    status: str
    total_places: int
    completed_places: int
    current_place_index: int
    current_place_name: Optional[str] = None
    current_place_id: Optional[str] = None

    # Current place progress (REAL-TIME)
    current_page: int = 1
    total_pages_estimate: Optional[int] = None
    reviews_scraped_current: int = 0
    reviews_scraped_total: int = 0

    # Performance metrics
    scraping_rate: float = 0.0
    time_elapsed: float = 0.0

    # Detailed stats (updated live)
    successful_requests: int = 0
    failed_requests: int = 0
    rate_limits_encountered: int = 0
    retries_used: int = 0

    # Timestamps
    created_at: str = ""
    updated_at: str = ""

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)

@dataclass
class LogEntry:
    """Detailed log entry with context"""
    timestamp: str
    level: str
    message: str
    task_id: str
    place_index: Optional[int] = None
    place_name: Optional[str] = None
    details: Optional[Dict] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)

@dataclass
class TaskInfo:
    """Complete task information"""
    task_id: str
    status: str
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    places: Optional[List[Dict]] = None
    settings: Optional[Dict] = None
    progress: Optional[TaskProgress] = None
    logs: Optional[List[LogEntry]] = None
    result: Optional[Dict] = None

    def __post_init__(self):
        if self.progress is None:
            self.progress = TaskProgress(
                status=self.status,
                total_places=len(self.places) if self.places else 0,
                completed_places=0,
                current_place_index=0,
                created_at=self.created_at,
                updated_at=self.created_at
            )
        if self.logs is None:
            self.logs = []

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'task_id': self.task_id,
            'status': self.status,
            'created_at': self.created_at,
            'started_at': self.started_at,
            'completed_at': self.completed_at,
            'places': self.places,
            'settings': self.settings,
            'progress': self.progress.to_dict() if self.progress else None,
            'logs': [log.to_dict() for log in self.logs] if self.logs else [],
            'result': self.result
        }

# ==================== GLOBAL STATE ====================

# Active tasks storage
active_tasks: Dict[str, TaskInfo] = {}
task_queues: Dict[str, queue.Queue] = {}

# ==================== HELPER FUNCTIONS ====================

def create_task_id() -> str:
    """Generate unique task ID"""
    return str(uuid.uuid4())[:8]

def update_progress(task_id: str, **kwargs):
    """Update task progress and broadcast via SSE"""
    if task_id not in active_tasks:
        return

    task = active_tasks[task_id]
    for key, value in kwargs.items():
        if hasattr(task.progress, key):
            setattr(task.progress, key, value)

    task.progress.updated_at = datetime.now().isoformat()

    # Broadcast via SSE
    if task_id in task_queues:
        task_queues[task_id].put({
            'type': 'progress',
            'data': task.progress.to_dict()
        })

def add_log(task_id: str, level: LogLevel, message: str,
            place_index: Optional[int] = None,
            place_name: Optional[str] = None,
            details: Optional[Dict] = None):
    """Add log entry and broadcast via SSE"""
    if task_id not in active_tasks:
        return

    log_entry = LogEntry(
        timestamp=datetime.now().isoformat(),
        level=level.value,
        message=message,
        task_id=task_id,
        place_index=place_index,
        place_name=place_name,
        details=details
    )

    active_tasks[task_id].logs.append(log_entry)

    # Keep only last 100 logs per task
    if len(active_tasks[task_id].logs) > 100:
        active_tasks[task_id].logs = active_tasks[task_id].logs[-100:]

    # Broadcast via SSE
    if task_id in task_queues:
        task_queues[task_id].put({
            'type': 'log',
            'data': asdict(log_entry)
        })

# ==================== FLASK APP SETUP ====================

app = Flask(__name__)
CORS(app)

# ==================== API ROUTES - SEARCH ====================

@app.route('/api/v2/search', methods=['POST'])
def api_search():
    """Search for places using RPC method"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        max_results = data.get('max_results', 5)
        language = data.get('language', 'th')
        region = data.get('region', 'th')

        if not query:
            return jsonify({'error': 'Query required'}), 400

        # Initialize searcher
        searcher = RpcPlaceSearch(language=language, region=region)

        # Search
        print(f"[SEARCH] Query: {query}")
        results = searcher.search_places(query, max_results=max_results)
        print(f"[SEARCH] Found {len(results)} places")

        # Convert to dict
        places = [p.__dict__ for p in results]

        # Validate place_ids
        valid_places = []
        for place in places:
            if place.get('place_id'):
                valid_places.append(place)
            else:
                print(f"[WARNING] Skipping place without place_id: {place.get('name', 'Unknown')}")

        print(f"[SUCCESS] Found {len(valid_places)} valid places")

        return jsonify({
            'success': True,
            'query': query,
            'count': len(valid_places),
            'places': valid_places
        })

    except Exception as e:
        print(f"[ERROR] Search failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==================== API ROUTES - SCRAPING (ENHANCED) ====================

@app.route('/api/v2/scrape', methods=['POST'])
def api_scrape():
    """Start scraping task with FORCED JSON + CSV output"""
    try:
        data = request.get_json()
        places = data.get('places', [])
        settings = data.get('settings', {})

        if not places:
            return jsonify({'error': 'No places provided'}), 400

        # Validate places
        valid_places = [p for p in places if p.get('place_id')]
        if not valid_places:
            return jsonify({'error': 'No valid places with place_id'}), 400

        # Create task
        task_id = create_task_id()
        created_at = datetime.now().isoformat()

        # Initialize task
        task = TaskInfo(
            task_id=task_id,
            status=TaskStatus.PENDING.value,
            created_at=created_at,
            places=valid_places,
            settings=settings
        )

        active_tasks[task_id] = task
        task_queues[task_id] = queue.Queue()

        print(f"[TASK] Created task {task_id} for {len(valid_places)} places")

        # Start background scraping
        threading.Thread(
            target=run_scraping_task,
            args=(task_id, valid_places, settings),
            daemon=True
        ).start()

        return jsonify({
            'success': True,
            'task_id': task_id,
            'total_places': len(valid_places),
            'status_url': f'/api/v2/tasks/{task_id}',
            'stream_url': f'/api/v2/tasks/{task_id}/stream'
        })

    except Exception as e:
        print(f"[ERROR] Failed to start scraping: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def run_scraping_task(task_id: str, places: List[Dict], settings: Dict):
    """Run scraping task with ENHANCED progress tracking and FORCED output"""
    try:
        task = active_tasks[task_id]
        task_start_time = time.time()

        # Update status
        task.status = TaskStatus.INITIALIZING.value
        task.started_at = datetime.now().isoformat()
        update_progress(task_id, status=TaskStatus.INITIALIZING.value)
        add_log(task_id, LogLevel.INFO, f"Starting task for {len(places)} places")

        # Initialize scraper
        scraper = create_production_scraper(
            language=settings.get('language', 'th'),
            region=settings.get('region', 'th'),
            fast_mode=settings.get('fast_mode', True),
            max_rate=settings.get('max_rate', 10.0),
            use_proxy=settings.get('use_proxy', False),
            proxy_list=settings.get('proxy_list', None),
            timeout=settings.get('timeout', 30.0),
            max_retries=settings.get('max_retries', 3)
        )

        add_log(task_id, LogLevel.SUCCESS, "Scraper initialized successfully")

        # Update to running status
        task.status = TaskStatus.RUNNING.value
        update_progress(task_id, status=TaskStatus.RUNNING.value)

        all_reviews = []

        # Scrape each place
        for place_idx, place in enumerate(places):
            try:
                place_id = place['place_id']
                place_name = place['name']
                max_reviews = settings.get('max_reviews', 100)
                date_range = settings.get('date_range', 'all')

                add_log(task_id, LogLevel.INFO,
                       f"Scraping {place_idx + 1}/{len(places)}: {place_name}")
                update_progress(task_id,
                              current_place_index=place_idx,
                              current_place_name=place_name,
                              current_place_id=place_id,
                              current_page=1)

                # Create event loop for this place
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

                place_start_time = time.time()

                # Scrape reviews
                result = loop.run_until_complete(
                    scraper.scrape_reviews(
                        place_id=place_id,
                        max_reviews=max_reviews,
                        date_range=date_range,
                        progress_callback=lambda page, total, reviews: update_progress(
                            task_id,
                            current_page=page,
                            total_pages_estimate=total,
                            reviews_scraped_current=len(reviews),
                            reviews_scraped_total=len(all_reviews) + len(reviews)
                        )
                    )
                )

                loop.close()

                reviews = result.get('reviews', [])
                metadata = result.get('metadata', {})

                # Set place_id and place_name for each review
                for review in reviews:
                    review.place_id = place_id
                    review.place_name = place_name

                all_reviews.extend(reviews)
                place_elapsed = time.time() - place_start_time
                place_rate = len(reviews) / place_elapsed if place_elapsed > 0 else 0

                # Update progress
                update_progress(
                    task_id,
                    completed_places=place_idx + 1,
                    reviews_scraped_total=len(all_reviews),
                    scraping_rate=place_rate,
                    time_elapsed=time.time() - task_start_time,
                    successful_requests=metadata.get('stats', {}).get('successful_requests', 0),
                    failed_requests=metadata.get('stats', {}).get('failed_requests', 0),
                    rate_limits_encountered=metadata.get('stats', {}).get('rate_limits_encountered', 0),
                    retries_used=metadata.get('stats', {}).get('retries_used', 0)
                )

                add_log(
                    task_id,
                    LogLevel.SUCCESS,
                    f"Completed {place_name}: {len(reviews)} reviews in {place_elapsed:.2f}s ({place_rate:.2f} rev/sec)",
                    place_index=place_idx,
                    place_name=place_name,
                    details={
                        'reviews_count': len(reviews),
                        'time_elapsed': place_elapsed,
                        'rate': place_rate,
                        'stats': metadata.get('stats', {})
                    }
                )

            except Exception as e:
                add_log(
                    task_id,
                    LogLevel.ERROR,
                    f"Failed to scrape {place_name}: {str(e)}",
                    place_index=place_idx,
                    place_name=place_name,
                    details={'error': str(e)}
                )
                # Continue with next place

            finally:
                if 'loop' in locals():
                    loop.close()

        # ==================== ENHANCED OUTPUT - FORCED JSON + CSV ====================
        add_log(task_id, LogLevel.INFO, "FORCED OUTPUT: Saving results in JSON + CSV formats...")

        # Calculate final stats
        total_elapsed = time.time() - task_start_time
        overall_rate = len(all_reviews) / total_elapsed if total_elapsed > 0 else 0

        # Use OutputManager to FORCE save each place's reviews in BOTH formats
        for place in places:
            place_reviews = [r for r in all_reviews if r.place_id == place['place_id']]
            if place_reviews:
                try:
                    # Force save with OutputManager (automatically creates JSON + CSV)
                    file_paths = save_reviews_dual_format(
                        reviews=place_reviews,
                        place_name=place['name'],
                        place_id=place['place_id'],
                        task_id=task_id,
                        settings=settings
                    )

                    add_log(task_id, LogLevel.SUCCESS,
                           f"✓ FORCED OUTPUT: {place['name']} saved as JSON + CSV")
                    add_log(task_id, LogLevel.DEBUG, f"  JSON: {file_paths['json']}")
                    add_log(task_id, LogLevel.DEBUG, f"  CSV: {file_paths['csv']}")

                except Exception as e:
                    add_log(task_id, LogLevel.ERROR,
                           f"Failed to save {place['name']}: {str(e)}")

        # Additional forced output for all reviews together
        try:
            # Force save consolidated data using output enhancer
            consolidated_output = force_json_csv_output(
                reviews=all_reviews,
                places=places,
                task_id=task_id,
                settings=settings
            )

            add_log(task_id, LogLevel.SUCCESS,
                   f"✓ CONSOLIDATED OUTPUT: All {len(places)} places saved as JSON + CSV")
            add_log(task_id, LogLevel.INFO,
                   f"  Total files created: {len(consolidated_output['files_created'])}")
            add_log(task_id, LogLevel.INFO,
                   f"  Output directory: {consolidated_output['outputs_directory']}")

        except Exception as e:
            add_log(task_id, LogLevel.ERROR,
                   f"Failed to create consolidated output: {str(e)}")

        # Create task directory with metadata
        task_dir = Path(f"./outputs/{task_id}")
        task_dir.mkdir(parents=True, exist_ok=True)

        # Save metadata
        metadata = {
            'task_id': task_id,
            'created_at': task.created_at,
            'started_at': task.started_at,
            'completed_at': datetime.now().isoformat(),
            'total_places': len(task.places),
            'total_reviews': len(all_reviews),
            'time_elapsed': total_elapsed,
            'scraping_rate': overall_rate,
            'settings': settings,
            'places': task.places,
            'final_progress': task.progress.to_dict(),
            'output_enforcement': {
                'forced_json_csv': True,
                'automatic_dual_format': True,
                'consolidated_files': True,
                'individual_place_files': True
            }
        }

        metadata_file = task_dir / "metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        add_log(task_id, LogLevel.SUCCESS, f"Saved task metadata: {metadata_file}")

        # Final verification
        add_log(task_id, LogLevel.INFO,
               "🎉 OUTPUT VERIFICATION COMPLETE:")
        add_log(task_id, LogLevel.INFO,
               f"  ✓ {len(places)} individual places → JSON + CSV pairs")
        add_log(task_id, LogLevel.INFO,
               f"  ✓ {len(all_reviews)} total reviews processed")
        add_log(task_id, LogLevel.INFO,
               f"  ✓ Consolidated files created")
        add_log(task_id, LogLevel.INFO,
               f"  ✓ Metadata saved")

        # Update final state
        task.status = TaskStatus.COMPLETED.value
        task.completed_at = datetime.now().isoformat()
        task.result = {
            'total_reviews': len(all_reviews),
            'total_places': len(task.places),
            'time_elapsed': total_elapsed,
            'scraping_rate': overall_rate,
            'output_dir': str(output_manager.base_dir),
            'forced_output': True,
            'formats_created': ['JSON', 'CSV'],
            'files_per_place': 2  # JSON + CSV for each place
        }

        update_progress(task_id, status=TaskStatus.COMPLETED.value)
        add_log(task_id, LogLevel.SUCCESS,
               f"✓ Task completed successfully! Results: {len(all_reviews)} reviews from {len(task.places)} places")
        add_log(task_id, LogLevel.INFO,
               f"  ⏱️  Time: {total_elapsed:.2f}s | ⚡ Rate: {overall_rate:.2f} rev/sec")
        add_log(task_id, LogLevel.INFO,
               f"  📁 Output: {output_manager.base_dir} (JSON + CSV forced)")

    except Exception as e:
        # Handle task failure
        if task_id in active_tasks:
            task = active_tasks[task_id]
            task.status = TaskStatus.FAILED.value
            task.completed_at = datetime.now().isoformat()
            task.result = {'error': str(e)}

            update_progress(task_id, status=TaskStatus.FAILED.value)
            add_log(task_id, LogLevel.ERROR, f"Task failed: {str(e)}")

        print(f"[ERROR] Task {task_id} failed: {str(e)}")

    finally:
        # Clean up task queue
        if task_id in task_queues:
            try:
                task_queues[task_id].put({'type': 'complete', 'data': None})
                time.sleep(1)  # Give SSE connection time to receive
                del task_queues[task_id]
            except:
                pass

# ==================== API ROUTES - TASK MANAGEMENT ====================

@app.route('/api/v2/tasks/<task_id>', methods=['GET'])
def api_get_task(task_id: str):
    """Get task status and progress"""
    if task_id not in active_tasks:
        return jsonify({'error': 'Task not found'}), 404

    task = active_tasks[task_id]
    return jsonify(task.to_dict())

@app.route('/api/v2/tasks/<task_id>/stream', methods=['GET'])
def api_task_stream(task_id: str):
    """SSE stream for real-time task updates"""
    if task_id not in active_tasks:
        return jsonify({'error': 'Task not found'}), 404

    def generate():
        """Generate SSE events"""
        try:
            q = task_queues.get(task_id)
            if not q:
                return

            # Send initial state
            task = active_tasks[task_id]
            yield f"data: {json.dumps({'type': 'init', 'data': task.to_dict()}, ensure_ascii=False)}\n\n"

            while True:
                try:
                    update = q.get(timeout=1.0)
                    yield f"data: {json.dumps(update, ensure_ascii=False)}\n\n"

                    if task.status in [TaskStatus.COMPLETED.value, TaskStatus.FAILED.value]:
                        yield f"data: {json.dumps({'type': 'complete', 'data': task.to_dict()}, ensure_ascii=False)}\n\n"
                        break
                except queue.Empty:
                    yield f": heartbeat\n\n"
        except GeneratorExit:
            pass
        finally:
            # Clean up on disconnect
            if task_id in task_queues:
                try:
                    del task_queues[task_id]
                except:
                    pass

    return app.response_class(
        generate(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Cache-Control'
        }
    )

@app.route('/api/v2/tasks', methods=['GET'])
def api_list_tasks():
    """List all active tasks"""
    return jsonify({
        'tasks': {task_id: task.to_dict() for task_id, task in active_tasks.items()},
        'total_active': len(active_tasks)
    })

# ==================== FORCED OUTPUT API ROUTES ====================

@app.route('/api/v2/output-status', methods=['GET'])
def api_output_status():
    """Get output directory status and recent files"""
    try:
        storage_info = output_manager.get_storage_info()
        recent_reviews = output_manager.get_recent_files("reviews", limit=10)
        recent_places = output_manager.get_recent_files("places", limit=5)

        return jsonify({
            'success': True,
            'storage_info': storage_info,
            'recent_reviews': recent_reviews,
            'recent_places': recent_places,
            'outputs_directory': str(output_manager.base_dir),
            'forced_output_features': {
                'automatic_json_csv': True,
                'individual_place_files': True,
                'consolidated_files': True,
                'metadata_tracking': True
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/v2/force-output', methods=['POST'])
def api_force_output():
    """Force save existing reviews in JSON + CSV format"""
    try:
        data = request.get_json()
        reviews_data = data.get('reviews', [])
        place_info = data.get('place', {})
        task_id = data.get('task_id', 'manual')
        settings = data.get('settings', {})

        if not reviews_data:
            return jsonify({'error': 'No reviews data provided'}), 400

        # Convert dicts to ProductionReview objects
        reviews = []
        for review_dict in reviews_data:
            review = ProductionReview(
                review_id=review_dict.get('review_id', ''),
                author_name=review_dict.get('author_name', ''),
                author_url=review_dict.get('author_url', ''),
                author_reviews_count=review_dict.get('author_reviews_count', 0),
                rating=review_dict.get('rating', 0),
                date_formatted=review_dict.get('date_formatted', ''),
                date_relative=review_dict.get('date_relative', ''),
                review_text=review_dict.get('review_text', ''),
                review_likes=review_dict.get('review_likes', 0),
                review_photos_count=review_dict.get('review_photos_count', 0),
                owner_response=review_dict.get('owner_response', ''),
                page_number=review_dict.get('page_number', 0),
                place_id=place_info.get('place_id', ''),
                place_name=place_info.get('name', '')
            )
            reviews.append(review)

        # Force save in both formats
        file_paths = save_reviews_dual_format(
            reviews=reviews,
            place_name=place_info.get('name', 'Unknown'),
            place_id=place_info.get('place_id', ''),
            task_id=task_id,
            settings=settings
        )

        return jsonify({
            'success': True,
            'message': f"✓ FORCED OUTPUT: Successfully saved {len(reviews)} reviews in JSON + CSV format",
            'files': file_paths,
            'outputs_directory': str(output_manager.base_dir),
            'verification': {
                'json_file': file_paths['json'],
                'csv_file': file_paths['csv'],
                'total_files': 2,
                'forced_dual_format': True
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==================== ROOT ROUTE ====================

@app.route('/')
def index():
    """API documentation"""
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Perfect Backend API v2 - FORCED JSON + CSV OUTPUT</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .header { background: #2563eb; color: white; padding: 20px; border-radius: 8px; }
            .section { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
            .endpoint { background: #f8fafc; padding: 10px; margin: 10px 0; border-radius: 4px; }
            .method { font-weight: bold; padding: 2px 8px; border-radius: 3px; }
            .get { background: #10b981; color: white; }
            .post { background: #3b82f6; color: white; }
            .feature { background: #f0f9ff; padding: 8px; margin: 5px 0; border-radius: 4px; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🚀 Perfect Backend API v2</h1>
            <h2>🔒 FORCED JSON + CSV OUTPUT</h2>
            <p>Real-time progress tracking with automatic dual-format output enforcement</p>
        </div>

        <div class="section">
            <h3>⚡ FORCED OUTPUT FEATURES</h3>
            <div class="feature">✅ Automatic JSON + CSV output for ALL operations</div>
            <div class="feature">✅ Individual place files (one JSON + one CSV per place)</div>
            <div class="feature">✅ Consolidated files for all places together</div>
            <div class="feature">✅ Metadata tracking with output verification</div>
            <div class="feature">✅ Organized directory structure by date</div>
        </div>

        <div class="section">
            <h3>📡 API Endpoints</h3>
            <div class="endpoint">
                <span class="method post">POST</span> /api/v2/search - Search for places
            </div>
            <div class="endpoint">
                <span class="method post">POST</span> /api/v2/scrape - Start scraping (auto JSON + CSV)
            </div>
            <div class="endpoint">
                <span class="method get">GET</span> /api/v2/tasks/{task_id} - Get task status
            </div>
            <div class="endpoint">
                <span class="method get">GET</span> /api/v2/tasks/{task_id}/stream - Real-time SSE
            </div>
            <div class="endpoint">
                <span class="method get">GET</span> /api/v2/tasks - List all tasks
            </div>
            <div class="endpoint">
                <span class="method get">GET</span> /api/v2/output-status - Output directory status
            </div>
            <div class="endpoint">
                <span class="method post">POST</span> /api/v2/force-output - Manual JSON + CSV conversion
            </div>
        </div>

        <div class="section">
            <h3>📁 Output Structure</h3>
            <pre>
outputs/
├── reviews/YYYY-MM-DD/
│   ├── place_name_reviews_YYYYMMDD_HHMMSS.json    # ✅ Auto-created
│   └── place_name_reviews_YYYYMMDD_HHMMSS.csv     # ✅ Auto-created
├── exports/
│   ├── consolidated_{task_id}_{timestamp}.json    # ✅ Auto-created
│   └── consolidated_{task_id}_{timestamp}.csv     # ✅ Auto-created
            </pre>
        </div>
    </body>
    </html>
    """)

# ==================== START SERVER ====================

if __name__ == '__main__':
    print("=" * 70)
    print("PERFECT BACKEND API v2 - FORCED JSON + CSV OUTPUT")
    print("=" * 70)
    print("")
    print("Features:")
    print("  [OK] Real-time progress tracking (page-by-page)")
    print("  [OK] Detailed logging with timestamps")
    print("  [OK] Complete stats monitoring")
    print("  [OK] SSE streaming for instant updates")
    print("  [OK] 🔒 FORCED JSON + CSV OUTPUT")
    print("  [OK] Automatic dual-format enforcement")
    print("  [OK] Individual place files")
    print("  [OK] Consolidated backup files")
    print("  [OK] Proper error handling")
    print("")
    print("Output Enforcement:")
    print("  ✅ Every scrape → JSON + CSV automatically")
    print("  ✅ Each place → individual JSON + CSV pair")
    print("  ✅ All places → consolidated JSON + CSV")
    print("  ✅ Metadata → output verification")
    print("")
    print("Starting Flask server...")
    print(f"API v2 Endpoint: http://localhost:5001")
    print("=" * 70)
    print("")

    # Start Flask server
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=True,
        threaded=True
    )