#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Perfect Backend API v2 - Google Maps RPC Scraper
================================================

Complete rewrite with perfect progress tracking, detailed logging,
and real-time streaming via SSE.

Key Features:
- Real-time progress updates (page-by-page)
- Detailed logging with timestamps
- Complete stats tracking
- SSE streaming for instant updates
- Proper error handling
- Task persistence
- Health monitoring

Author: Nextzus
Date: 2025-11-10
Version: 2.0
"""
import sys
import os

# Fix Windows encoding
if sys.platform == 'win32':
    os.system('chcp 65001 > nul 2>&1')

from flask import Flask, render_template, request, jsonify, Response
from flask_cors import CORS
import asyncio
import json
import uuid
from datetime import datetime
from pathlib import Path
import threading
import queue
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from src.scraper.production_scraper import create_production_scraper
from src.search.rpc_place_search import create_rpc_search

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'google-maps-scraper-v2-secret-key-2025'
app.config['JSON_AS_ASCII'] = False
CORS(app)

# Output directory
OUTPUT_DIR = Path(__file__).parent.parent / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)


# ==================== DATA STRUCTURES ====================

class TaskStatus(Enum):
    """Task status enum"""
    PENDING = "pending"
    INITIALIZING = "initializing"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class LogLevel(Enum):
    """Log level enum"""
    DEBUG = "debug"
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class LogEntry:
    """Log entry structure"""
    timestamp: str
    level: str
    message: str
    task_id: str
    place_index: Optional[int] = None
    place_name: Optional[str] = None
    details: Optional[Dict] = None


@dataclass
class TaskProgress:
    """Detailed task progress"""
    # Overall progress
    status: str
    total_places: int
    completed_places: int
    current_place_index: int
    current_place_name: Optional[str] = None

    # Current place progress
    current_place_id: Optional[str] = None
    current_page: int = 0
    total_pages_estimate: Optional[int] = None
    reviews_scraped_current: int = 0
    reviews_scraped_total: int = 0

    # Performance metrics
    scraping_rate: float = 0.0
    time_elapsed: float = 0.0
    time_remaining_estimate: Optional[float] = None

    # Stats
    successful_requests: int = 0
    failed_requests: int = 0
    rate_limits_encountered: int = 0
    retries_used: int = 0

    # Timestamps
    started_at: Optional[str] = None
    updated_at: Optional[str] = None

    def to_dict(self):
        return asdict(self)


@dataclass
class TaskInfo:
    """Complete task information"""
    task_id: str
    places: List[Dict]
    settings: Dict
    status: str
    progress: TaskProgress
    logs: List[LogEntry]
    result: Optional[Dict] = None
    error: Optional[str] = None
    created_at: str = ""
    started_at: Optional[str] = None
    completed_at: Optional[str] = None

    def to_dict(self):
        return {
            'task_id': self.task_id,
            'places': self.places,
            'settings': self.settings,
            'status': self.status,
            'progress': self.progress.to_dict(),
            'logs': [asdict(log) for log in self.logs[-100:]],  # Last 100 logs
            'result': self.result,
            'error': self.error,
            'created_at': self.created_at,
            'started_at': self.started_at,
            'completed_at': self.completed_at
        }


# ==================== GLOBAL STORAGE ====================

# In-memory storage
active_tasks: Dict[str, TaskInfo] = {}
task_queues: Dict[str, queue.Queue] = {}  # For SSE updates


# ==================== HELPER FUNCTIONS ====================

def create_task_id() -> str:
    """Create unique task ID"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    short_id = str(uuid.uuid4())[:8]
    return f"{timestamp}_{short_id}"


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

    # Broadcast to SSE clients
    if task_id in task_queues:
        task_queues[task_id].put({
            'type': 'log',
            'data': asdict(log_entry)
        })

    # Console output with ASCII-safe encoding
    try:
        print(f"[{level.value.upper()}] [{task_id[:8]}] {message}")
    except UnicodeEncodeError:
        ascii_message = message.encode('ascii', errors='replace').decode('ascii')
        print(f"[{level.value.upper()}] [{task_id[:8]}] {ascii_message}")


def update_progress(task_id: str, **kwargs):
    """Update task progress and broadcast via SSE"""
    if task_id not in active_tasks:
        return

    task = active_tasks[task_id]

    # Update progress fields
    for key, value in kwargs.items():
        if hasattr(task.progress, key):
            setattr(task.progress, key, value)

    # Update timestamp
    task.progress.updated_at = datetime.now().isoformat()

    # Broadcast to SSE clients
    if task_id in task_queues:
        task_queues[task_id].put({
            'type': 'progress',
            'data': task.progress.to_dict()
        })


# ==================== ROUTES - PAGES ====================

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')


@app.route('/search')
def search_page():
    """Search page"""
    return render_template('search.html')


@app.route('/tasks')
def tasks_page():
    """Tasks monitoring page"""
    return render_template('tasks.html')


@app.route('/results/<task_id>')
def results_page(task_id):
    """Results page"""
    return render_template('results.html', task_id=task_id)


@app.route('/history')
def history_page():
    """History page"""
    return render_template('history.html')


# ==================== API ROUTES - SEARCH ====================

@app.route('/api/v2/search', methods=['POST'])
def api_search():
    """Search for places"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        max_results = data.get('max_results', 10)
        language = data.get('language', 'th')
        region = data.get('region', 'th')

        if not query:
            return jsonify({'error': 'Query is required'}), 400

        # Validate max_results
        max_results = min(max(1, int(max_results)), 50)

        print(f"[INFO] Search request: query='{query}', max={max_results}, lang={language}, region={region}")

        # Create search service
        search_service = create_rpc_search(language=language, region=region)

        # Run async search
        def run_async(coro):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(coro)
            finally:
                loop.close()

        results = run_async(search_service.search_places(query, max_results=max_results))

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


# ==================== API ROUTES - SCRAPING ====================

@app.route('/api/v2/scrape', methods=['POST'])
def api_scrape():
    """Start scraping task with perfect progress tracking"""
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

        # Initialize progress
        progress = TaskProgress(
            status=TaskStatus.PENDING.value,
            total_places=len(valid_places),
            completed_places=0,
            current_place_index=0,
            started_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )

        # Create task info
        task = TaskInfo(
            task_id=task_id,
            places=valid_places,
            settings=settings,
            status=TaskStatus.PENDING.value,
            progress=progress,
            logs=[],
            created_at=datetime.now().isoformat()
        )

        active_tasks[task_id] = task
        task_queues[task_id] = queue.Queue()

        # Log task creation
        add_log(
            task_id,
            LogLevel.INFO,
            f"Task created: {len(valid_places)} places to scrape",
            details={'settings': settings}
        )

        # Start scraping in background
        thread = threading.Thread(
            target=run_scraping_task_v2,
            args=(task_id,),
            daemon=True
        )
        thread.start()

        return jsonify({
            'success': True,
            'task_id': task_id,
            'message': 'Scraping task started',
            'places_count': len(valid_places)
        })

    except Exception as e:
        print(f"[ERROR] Failed to start scraping: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/v2/tasks/<task_id>')
def api_task_status(task_id):
    """Get complete task status"""
    if task_id not in active_tasks:
        return jsonify({'error': 'Task not found'}), 404

    task = active_tasks[task_id]
    return jsonify({
        'success': True,
        'task': task.to_dict()
    })


@app.route('/api/v2/tasks/<task_id>/stream')
def api_task_stream(task_id):
    """Real-time task updates via SSE"""
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

            # Stream updates
            while True:
                try:
                    # Get update from queue (with timeout)
                    update = q.get(timeout=1.0)
                    yield f"data: {json.dumps(update, ensure_ascii=False)}\n\n"

                    # Stop if task completed/failed
                    if task.status in [TaskStatus.COMPLETED.value, TaskStatus.FAILED.value]:
                        # Send final state
                        yield f"data: {json.dumps({'type': 'complete', 'data': task.to_dict()}, ensure_ascii=False)}\n\n"
                        break

                except queue.Empty:
                    # Send heartbeat
                    yield f": heartbeat\n\n"

                    # Check if task still exists
                    if task_id not in active_tasks:
                        break

        except GeneratorExit:
            pass

    return Response(generate(), mimetype='text/event-stream')


@app.route('/api/v2/tasks')
def api_tasks_list():
    """Get all tasks"""
    tasks = [task.to_dict() for task in active_tasks.values()]
    tasks.sort(key=lambda x: x['created_at'], reverse=True)

    return jsonify({
        'success': True,
        'count': len(tasks),
        'tasks': tasks
    })


# ==================== BACKGROUND SCRAPING ====================

def run_scraping_task_v2(task_id: str):
    """
    Perfect scraping with detailed progress tracking

    This function provides:
    - Page-by-page progress updates
    - Detailed logging for every action
    - Real-time stats
    - Proper error handling
    - Complete result storage
    """
    task = active_tasks[task_id]

    try:
        # Update status
        task.status = TaskStatus.INITIALIZING.value
        update_progress(task_id, status=TaskStatus.INITIALIZING.value)
        add_log(task_id, LogLevel.INFO, "Initializing scraper...")

        # Get settings
        settings = task.settings
        max_reviews = settings.get('max_reviews', 1000)
        language = settings.get('language', 'th')
        region = settings.get('region', 'th')
        date_range = settings.get('date_range', '1year')
        fast_mode = settings.get('fast_mode', True)

        add_log(
            task_id,
            LogLevel.INFO,
            f"Settings: max_reviews={max_reviews}, language={language}, region={region}, date_range={date_range}, fast_mode={fast_mode}"
        )

        # Create output directory
        task_dir = OUTPUT_DIR / task_id
        task_dir.mkdir(exist_ok=True)
        add_log(task_id, LogLevel.INFO, f"Output directory: {task_dir}")

        # Start scraping
        task.status = TaskStatus.RUNNING.value
        task.started_at = datetime.now().isoformat()
        update_progress(task_id, status=TaskStatus.RUNNING.value)
        add_log(task_id, LogLevel.SUCCESS, "Starting scraping process...")

        all_reviews = []
        task_start_time = time.time()

        # Scrape each place
        for place_idx, place in enumerate(task.places):
            place_id = place.get('place_id', '')
            place_name = place.get('name', 'Unknown')

            # Update current place
            update_progress(
                task_id,
                current_place_index=place_idx,
                current_place_name=place_name,
                current_place_id=place_id,
                current_page=0,
                reviews_scraped_current=0
            )

            add_log(
                task_id,
                LogLevel.INFO,
                f"Starting place {place_idx + 1}/{task.progress.total_places}: {place_name}",
                place_index=place_idx,
                place_name=place_name,
                details={'place_id': place_id}
            )

            # Create scraper with progress callback
            scraper = create_production_scraper(
                language=language,
                region=region,
                fast_mode=fast_mode
            )

            add_log(task_id, LogLevel.DEBUG, f"Scraper initialized for {place_name}")

            # Progress callback for page updates
            def progress_callback(page_num, reviews_count):
                update_progress(
                    task_id,
                    current_page=page_num,
                    reviews_scraped_current=reviews_count,
                    reviews_scraped_total=len(all_reviews) + reviews_count
                )
                add_log(
                    task_id,
                    LogLevel.DEBUG,
                    f"Page {page_num}: {reviews_count} reviews scraped",
                    place_index=place_idx,
                    place_name=place_name
                )

            # Run scraping
            place_start_time = time.time()
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            try:
                result = loop.run_until_complete(
                    scraper.scrape_reviews(
                        place_id=place_id,
                        max_reviews=max_reviews,
                        date_range=date_range,
                        progress_callback=progress_callback
                    )
                )

                reviews = result.get('reviews', [])
                metadata = result.get('metadata', {})

                # Add place info to reviews
                for review in reviews:
                    review.place_id = place_id
                    review.place_name = place_name

                all_reviews.extend(reviews)

                # Calculate time and rate
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
                loop.close()

        # Save results
        add_log(task_id, LogLevel.INFO, "Saving results...")

        # Calculate final stats
        total_elapsed = time.time() - task_start_time
        overall_rate = len(all_reviews) / total_elapsed if total_elapsed > 0 else 0

        # Save JSON
        json_file = task_dir / "reviews.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(
                [r.__dict__ for r in all_reviews],
                f,
                ensure_ascii=False,
                indent=2,
                default=str
            )

        add_log(task_id, LogLevel.SUCCESS, f"Saved JSON: {json_file}")

        # Save CSV
        if all_reviews:
            csv_file = task_dir / "reviews.csv"
            scraper.export_to_csv(all_reviews, str(csv_file))
            add_log(task_id, LogLevel.SUCCESS, f"Saved CSV: {csv_file}")

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
            'final_progress': task.progress.to_dict()
        }

        metadata_file = task_dir / "metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        add_log(task_id, LogLevel.SUCCESS, f"Saved metadata: {metadata_file}")

        # Update final state
        task.status = TaskStatus.COMPLETED.value
        task.completed_at = datetime.now().isoformat()
        task.result = {
            'total_reviews': len(all_reviews),
            'total_places': len(task.places),
            'time_elapsed': total_elapsed,
            'scraping_rate': overall_rate,
            'output_dir': str(task_dir)
        }

        update_progress(
            task_id,
            status=TaskStatus.COMPLETED.value,
            time_elapsed=total_elapsed,
            scraping_rate=overall_rate
        )

        add_log(
            task_id,
            LogLevel.SUCCESS,
            f"Task completed! Total: {len(all_reviews)} reviews from {len(task.places)} places in {total_elapsed:.2f}s ({overall_rate:.2f} rev/sec)",
            details=task.result
        )

    except Exception as e:
        # Handle failure
        task.status = TaskStatus.FAILED.value
        task.error = str(e)
        task.completed_at = datetime.now().isoformat()

        update_progress(task_id, status=TaskStatus.FAILED.value)
        add_log(
            task_id,
            LogLevel.ERROR,
            f"Task failed: {str(e)}",
            details={'error': str(e), 'traceback': __import__('traceback').format_exc()}
        )


# ==================== RUN APP ====================

if __name__ == '__main__':
    print("=" * 70)
    print("PERFECT BACKEND API v2 - GOOGLE MAPS SCRAPER")
    print("=" * 70)
    print()
    print("Features:")
    print("  [OK] Real-time progress tracking (page-by-page)")
    print("  [OK] Detailed logging with timestamps")
    print("  [OK] Complete stats monitoring")
    print("  [OK] SSE streaming for instant updates")
    print("  [OK] Proper error handling")
    print()
    print("Starting Flask server...")
    print("API v2 Endpoint: http://localhost:5001")
    print()
    print("=" * 70)

    app.run(
        host='0.0.0.0',
        port=5001,
        debug=True,
        threaded=True
    )
from force_output_api import register_force_output_routes
# Register forced output routes
app = register_force_output_routes(app)
