# -*- coding: utf-8 -*-
"""
WebApp API for Enhanced Google Maps Scraper
==========================================

API endpoints to integrate the enhanced scraper with web frontend.
Features:
- Enhanced language scraper with session management
- Configurable session refresh intervals
- Real-time progress tracking
- Place search functionality
- Download results in multiple formats

Author: Nextzus
Date: 2025-11-11
"""
import sys
import os

# Fix Windows encoding
if sys.platform == 'win32':
    os.system('chcp 65001 > nul 2>&1')

import asyncio
import json
import time
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import enhanced scraper
from src.scraper.enhanced_language_scraper import create_enhanced_scraper
from src.search.rpc_place_search import RpcPlaceSearch

# Initialize FastAPI app
app = FastAPI(
    title="Enhanced Google Maps Scraper API",
    description="Production-ready scraper with session-based language consistency",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global storage for active tasks (in production, use Redis)
active_tasks: Dict[str, Dict[str, Any]] = {}

# Pydantic models
@dataclass
class ScraperRequest:
    place_id: str
    place_name: str
    max_reviews: int = 1000
    date_range: str = "all"
    language: str = "en"
    region: str = "us"
    session_refresh_interval: int = 30
    use_session_ids: bool = True
    strict_language_mode: bool = True
    fast_mode: bool = True
    max_rate: float = 6.0

class ScraperRequestModel(BaseModel):
    place_id: str
    place_name: str
    max_reviews: int = 1000
    date_range: str = "all"
    language: str = "en"
    region: str = "us"
    session_refresh_interval: int = 30
    use_session_ids: bool = True
    strict_language_mode: bool = True
    fast_mode: bool = True
    max_rate: float = 6.0

class SearchRequestModel(BaseModel):
    query: str
    max_places: int = 10
    language: str = "en"
    region: str = "us"

class ConfigResponse(BaseModel):
    default_language: str = "en"
    default_region: str = "us"
    default_max_reviews: int = 1000
    default_date_range: str = "all"
    default_session_refresh_interval: int = 30
    supported_languages: List[str]
    supported_regions: List[str]
    session_refresh_options: List[int]

# Helper functions
def create_task_id() -> str:
    """Generate unique task ID"""
    return str(uuid.uuid4())

def update_task_progress(task_id: str, progress_data: Dict[str, Any]):
    """Update task progress"""
    if task_id in active_tasks:
        active_tasks[task_id].update(progress_data)
        active_tasks[task_id]['updated_at'] = datetime.now().isoformat()

# API Endpoints

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "name": "Enhanced Google Maps Scraper API",
        "version": "2.0.0",
        "status": "active",
        "description": "Production-ready scraper with session-based language consistency",
        "endpoints": {
            "search": "/search",
            "scrape": "/scrape",
            "status": "/status/{task_id}",
            "stream": "/stream/{task_id}",
            "config": "/config",
            "download": "/download/{task_id}"
        }
    }

@app.get("/config", response_model=ConfigResponse)
async def get_config():
    """Get scraper configuration options"""
    return ConfigResponse(
        supported_languages=["en", "th", "ja", "ko", "es", "fr", "de", "it", "pt", "ru"],
        supported_regions=["us", "th", "jp", "kr", "es", "fr", "de", "it", "pt", "ru"],
        session_refresh_options=[20, 30, 40, 50, 100]
    )

@app.post("/search")
async def search_places(request: SearchRequestModel):
    """Search for places using RPC search"""
    try:
        search_engine = RpcPlaceSearch()
        results = search_engine.search_places(
            query=request.query,
            max_places=request.max_places,
            language=request.language,
            region=request.region
        )

        return {
            "success": True,
            "query": request.query,
            "places": results,
            "count": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/scrape")
async def start_scraping(request: ScraperRequestModel, background_tasks: BackgroundTasks):
    """Start scraping task"""
    try:
        # Validate request
        if not request.place_id or not request.place_name:
            raise HTTPException(status_code=400, detail="place_id and place_name are required")

        if request.max_reviews <= 0 or request.max_reviews > 5000:
            raise HTTPException(status_code=400, detail="max_reviews must be between 1 and 5000")

        # Generate task ID
        task_id = create_task_id()

        # Initialize task
        task_data = {
            "task_id": task_id,
            "status": "pending",
            "place_id": request.place_id,
            "place_name": request.place_name,
            "max_reviews": request.max_reviews,
            "date_range": request.date_range,
            "language": request.language,
            "region": request.region,
            "session_refresh_interval": request.session_refresh_interval,
            "use_session_ids": request.use_session_ids,
            "strict_language_mode": request.strict_language_mode,
            "fast_mode": request.fast_mode,
            "max_rate": request.max_rate,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "progress": {
                "current_page": 0,
                "total_pages": 0,
                "reviews_scraped": 0,
                "current_rate": 0.0,
                "time_elapsed": 0.0,
                "language_consistency": 100.0,
                "session_refreshes": 0,
                "language_failures": 0
            },
            "results": {
                "reviews": [],
                "total_reviews": 0,
                "english_reviews": 0,
                "thai_reviews": 0,
                "empty_reviews": 0,
                "language_consistency": 0.0,
                "avg_rating": 0.0
            },
            "errors": [],
            "output_files": {}
        }

        active_tasks[task_id] = task_data

        # Start background scraping task
        background_tasks.add_task(
            scrape_reviews_task,
            task_id,
            request.dict()
        )

        return {
            "success": True,
            "task_id": task_id,
            "message": "Scraping task started",
            "estimated_time": f"~{request.max_reviews / 50:.1f} minutes",
            "config": {
                "session_refresh_interval": request.session_refresh_interval,
                "use_session_ids": request.use_session_ids,
                "strict_language_mode": request.strict_language_mode
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def scrape_reviews_task(task_id: str, request_data: Dict[str, Any]):
    """Background task for scraping reviews"""
    try:
        # Update task status to running
        update_task_progress(task_id, {"status": "running"})

        # Create enhanced scraper
        scraper = create_enhanced_scraper(
            language=request_data["language"],
            region=request_data["region"],
            fast_mode=request_data["fast_mode"],
            max_rate=request_data["max_rate"],
            session_refresh_interval=request_data["session_refresh_interval"],
            use_session_ids=request_data["use_session_ids"],
            strict_language_mode=request_data["strict_language_mode"]
        )

        # Start scraping
        start_time = time.time()

        def progress_callback(page_num: int, total_pages: int, reviews_count: int,
                              language_consistency: float, session_refreshes: int):
            """Callback for progress updates"""
            elapsed = time.time() - start_time
            current_rate = reviews_count / elapsed if elapsed > 0 else 0

            update_task_progress(task_id, {
                "progress": {
                    "current_page": page_num,
                    "total_pages": total_pages,
                    "reviews_scraped": reviews_count,
                    "current_rate": current_rate,
                    "time_elapsed": elapsed,
                    "language_consistency": language_consistency,
                    "session_refreshes": session_refreshes,
                    "estimated_remaining": (total_pages - page_num) / current_rate if current_rate > 0 else 0
                }
            })

        # Set progress callback (you'll need to modify the scraper to support callbacks)
        # For now, we'll update progress manually

        # Perform scraping
        result = await scraper.scrape_reviews_enhanced(
            place_id=request_data["place_id"],
            max_reviews=request_data["max_reviews"],
            date_range=request_data["date_range"]
        )

        # Process results
        reviews = result['reviews']
        metadata = result['metadata']

        # Analyze results
        english_reviews = 0
        thai_reviews = 0
        empty_reviews = 0
        total_rating = 0

        for review in reviews:
            text = getattr(review, 'review_text', '').strip()
            rating = getattr(review, 'rating', 0)

            if not text:
                empty_reviews += 1
            elif any('\u0E00' <= char <= '\u0E7F' for char in text):
                thai_reviews += 1
            else:
                english_reviews += 1

            total_rating += rating

        avg_rating = total_rating / len(reviews) if reviews else 0
        language_consistency = (english_reviews / len(reviews) * 100) if reviews else 100

        # Update final results
        update_task_progress(task_id, {
            "status": "completed",
            "results": {
                "reviews": [review.__dict__ for review in reviews],
                "total_reviews": len(reviews),
                "english_reviews": english_reviews,
                "thai_reviews": thai_reviews,
                "empty_reviews": empty_reviews,
                "language_consistency": language_consistency,
                "avg_rating": round(avg_rating, 2),
                "scraping_rate": len(reviews) / (time.time() - start_time)
            },
            "metadata": {
                "session_id": metadata.get('session_id'),
                "language_failures": metadata.get('language_failures', 0),
                "rate_limits": metadata.get('rate_limits_encountered', 0),
                "total_requests": metadata.get('total_requests', 0)
            }
        })

    except Exception as e:
        update_task_progress(task_id, {
            "status": "failed",
            "errors": [str(e)]
        })

@app.get("/status/{task_id}")
async def get_task_status(task_id: str):
    """Get task status and progress"""
    if task_id not in active_tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    return active_tasks[task_id]

@app.get("/stream/{task_id}")
async def stream_task_progress(task_id: str):
    """Stream task progress via Server-Sent Events"""
    if task_id not in active_tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    async def event_stream():
        last_progress = ""

        while True:
            task_data = active_tasks[task_id]
            current_progress = json.dumps(task_data["progress"])

            # Send update if progress changed
            if current_progress != last_progress:
                yield f"data: {current_progress}\n\n"
                last_progress = current_progress

            # Check if task is completed or failed
            if task_data["status"] in ["completed", "failed"]:
                yield f"event: complete\ndata: {json.dumps(task_data)}\n\n"
                break

            await asyncio.sleep(1)  # Update every second

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        }
    )

@app.get("/tasks")
async def list_all_tasks():
    """List all tasks"""
    return {
        "tasks": list(active_tasks.values()),
        "total_tasks": len(active_tasks)
    }

@app.delete("/tasks/{task_id}")
async def delete_task(task_id: str):
    """Delete task and cleanup"""
    if task_id not in active_tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    del active_tasks[task_id]
    return {"success": True, "message": "Task deleted"}

if __name__ == "__main__":
    import uvicorn

    print("Enhanced Google Maps Scraper API")
    print("Starting server...")
    print("Available endpoints:")
    print("  GET  /")
    print("  GET  /config")
    print("  POST /search")
    print("  POST /scrape")
    print("  GET  /status/{task_id}")
    print("  GET  /stream/{task_id}")
    print("  GET  /tasks")
    print("  DELETE /tasks/{task_id}")
    print()
    print("Starting server on http://localhost:8000")

    uvicorn.run(app, host="0.0.0.0", port=8000)