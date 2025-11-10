# -*- coding: utf-8 -*-
"""
Output Manager Service
====================

Manages organized file output for reviews and places data.
Creates structured directories and standardized filenames.

Author: Nextzus
Date: 2025-11-10
Version: 1.0
"""
import sys
import io
import os

# Fix Windows encoding
if sys.platform == 'win32':
    os.system('chcp 65001 > nul 2>&1')

import json
import csv
import time
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import asdict


class OutputManager:
    """Manages organized output storage for scraped data"""

    def __init__(self, base_dir: str = "./outputs"):
        self.base_dir = Path(base_dir)
        self.reviews_dir = self.base_dir / "reviews"
        self.places_dir = self.base_dir / "places"
        self.logs_dir = self.base_dir / "logs"
        self.exports_dir = self.base_dir / "exports"

        # Create all directories
        self._ensure_directories()

    def _ensure_directories(self):
        """Create necessary directories if they don't exist"""
        for directory in [self.base_dir, self.reviews_dir, self.places_dir,
                          self.logs_dir, self.exports_dir]:
            directory.mkdir(parents=True, exist_ok=True)

        # Create subdirectories by date
        today = datetime.now().strftime("%Y-%m-%d")
        (self.reviews_dir / today).mkdir(exist_ok=True)
        (self.places_dir / today).mkdir(exist_ok=True)
        (self.logs_dir / today).mkdir(exist_ok=True)

    def generate_filename(self,
                         place_name: str,
                         data_type: str,
                         format_type: str = "json",
                         timestamp: Optional[str] = None) -> str:
        """
        Generate standardized filename for output files

        Args:
            place_name: Name of the place
            data_type: Type of data (reviews, places, search)
            format_type: File format (json, csv, txt)
            timestamp: Optional timestamp (uses current time if None)

        Returns:
            Standardized filename
        """
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Clean place name for filename
        clean_name = self._clean_filename(place_name)

        return f"{clean_name}_{data_type}_{timestamp}.{format_type}"

    def _clean_filename(self, text: str, max_length: int = 50) -> str:
        """Clean text to be safe for filenames"""
        # Replace spaces with underscores
        text = text.replace(" ", "_")

        # Remove special characters
        import re
        text = re.sub(r'[^\w\-_\.]', '', text)

        # Remove multiple underscores
        text = re.sub(r'_+', '_', text)

        # Limit length
        if len(text) > max_length:
            text = text[:max_length].rstrip('_')

        return text.lower()

    def save_reviews(self,
                    reviews: List[Dict[str, Any]],
                    place_name: str,
                    place_id: str,
                    task_id: str,
                    settings: Dict[str, Any]) -> Dict[str, str]:
        """
        Save reviews data in multiple formats

        Args:
            reviews: List of review dictionaries
            place_name: Name of the place
            place_id: Google Maps place ID
            task_id: Scraping task ID
            settings: Scraper settings used

        Returns:
            Dictionary with file paths
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        today = datetime.now().strftime("%Y-%m-%d")

        # Create metadata
        metadata = {
            "place_info": {
                "place_name": place_name,
                "place_id": place_id,
                "task_id": task_id,
                "scraped_at": datetime.now().isoformat(),
                "total_reviews": len(reviews)
            },
            "settings": settings,
            "data": reviews
        }

        # Generate file paths
        base_filename = self.generate_filename(place_name, "reviews")
        json_path = self.reviews_dir / today / base_filename
        csv_path = self.reviews_dir / today / base_filename.replace('.json', '.csv')

        file_paths = {
            "json": str(json_path),
            "csv": str(csv_path),
            "directory": str(self.reviews_dir / today)
        }

        # Save JSON
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        # Save CSV (if reviews exist)
        if reviews:
            with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)

                # Write header
                writer.writerow([
                    "review_id", "author", "author_url", "rating", "text",
                    "date", "date_relative", "language", "helpful_count",
                    "response_text", "response_date", "page_number"
                ])

                # Write reviews
                for review in reviews:
                    writer.writerow([
                        review.get("review_id", ""),
                        review.get("author", ""),
                        review.get("author_url", ""),
                        review.get("rating", 0),
                        review.get("text", ""),
                        review.get("date", ""),
                        review.get("date_relative", ""),
                        review.get("language", ""),
                        review.get("helpful_count", 0),
                        review.get("response_text", ""),
                        review.get("response_date", ""),
                        review.get("page_number", 0)
                    ])

        print(f"[OK] Saved {len(reviews)} reviews to: {file_paths['directory']}")
        return file_paths

    def save_places(self,
                    places: List[Dict[str, Any]],
                    search_query: str,
                    settings: Dict[str, Any]) -> Dict[str, str]:
        """
        Save place search results

        Args:
            places: List of place dictionaries
            search_query: Search query used
            settings: Search settings used

        Returns:
            Dictionary with file paths
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        today = datetime.now().strftime("%Y-%m-%d")

        # Create metadata
        metadata = {
            "search_info": {
                "query": search_query,
                "searched_at": datetime.now().isoformat(),
                "total_places": len(places)
            },
            "settings": settings,
            "data": places
        }

        # Generate file paths
        clean_query = self._clean_filename(search_query)
        json_filename = f"{clean_query}_places_{timestamp}.json"
        csv_filename = f"{clean_query}_places_{timestamp}.csv"

        json_path = self.places_dir / today / json_filename
        csv_path = self.places_dir / today / csv_filename

        file_paths = {
            "json": str(json_path),
            "csv": str(csv_path),
            "directory": str(self.places_dir / today)
        }

        # Save JSON
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        # Save CSV
        with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)

            # Write header
            writer.writerow([
                "place_id", "name", "address", "rating", "total_reviews",
                "category", "url"
            ])

            # Write places
            for place in places:
                writer.writerow([
                    place.get("place_id", ""),
                    place.get("name", ""),
                    place.get("address", ""),
                    place.get("rating", 0),
                    place.get("total_reviews", 0),
                    place.get("category", ""),
                    place.get("url", "")
                ])

        print(f"[OK] Saved {len(places)} places to: {file_paths['directory']}")
        return file_paths

    def save_log(self,
                 log_content: str,
                 log_type: str = "scraping",
                 task_id: Optional[str] = None) -> str:
        """
        Save log content

        Args:
            log_content: Log content to save
            log_type: Type of log (scraping, search, error)
            task_id: Optional task ID

        Returns:
            Path to saved log file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        today = datetime.now().strftime("%Y-%m-%d")

        # Generate filename
        if task_id:
            filename = f"{log_type}_{task_id}_{timestamp}.log"
        else:
            filename = f"{log_type}_{timestamp}.log"

        log_path = self.logs_dir / today / filename

        # Save log
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write(f"Log created: {datetime.now().isoformat()}\n")
            f.write(f"Log type: {log_type}\n")
            if task_id:
                f.write(f"Task ID: {task_id}\n")
            f.write("=" * 50 + "\n\n")
            f.write(log_content)

        print(f"[OK] Saved {log_type} log to: {log_path}")
        return str(log_path)

    def get_recent_files(self,
                        data_type: str = "reviews",
                        limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get list of recent output files

        Args:
            data_type: Type of data (reviews, places, logs)
            limit: Maximum number of files to return

        Returns:
            List of file information
        """
        # Determine directory
        if data_type == "reviews":
            directory = self.reviews_dir
        elif data_type == "places":
            directory = self.places_dir
        elif data_type == "logs":
            directory = self.logs_dir
        else:
            return []

        files = []

        # Search through subdirectories (organized by date)
        for date_dir in directory.iterdir():
            if date_dir.is_dir():
                for file_path in date_dir.glob("*.json"):
                    if file_path.is_file():
                        stat = file_path.stat()
                        files.append({
                            "filename": file_path.name,
                            "path": str(file_path),
                            "size": stat.st_size,
                            "created": datetime.fromtimestamp(stat.st_ctime),
                            "date": date_dir.name
                        })

        # Sort by creation time (newest first) and limit
        files.sort(key=lambda x: x["created"], reverse=True)
        return files[:limit]

    def cleanup_old_files(self, days_to_keep: int = 30):
        """
        Clean up old files older than specified days

        Args:
            days_to_keep: Number of days to keep files
        """
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        deleted_count = 0

        for directory in [self.reviews_dir, self.places_dir, self.logs_dir]:
            for date_dir in directory.iterdir():
                if date_dir.is_dir():
                    # Check if directory is older than cutoff
                    try:
                        dir_date = datetime.strptime(date_dir.name, "%Y-%m-%d")
                        if dir_date < cutoff_date:
                            shutil.rmtree(date_dir)
                            deleted_count += 1
                            print(f"[DELETE] Deleted old directory: {date_dir}")
                    except ValueError:
                        continue

        print(f"[OK] Cleanup completed. Deleted {deleted_count} old directories.")

    def get_storage_info(self) -> Dict[str, Any]:
        """
        Get storage information and statistics

        Returns:
            Dictionary with storage statistics
        """
        total_size = 0
        file_counts = {
            "reviews": 0,
            "places": 0,
            "logs": 0,
            "exports": 0
        }

        # Calculate sizes and counts
        directories = [
            ("reviews", self.reviews_dir, file_counts["reviews"]),
            ("places", self.places_dir, file_counts["places"]),
            ("logs", self.logs_dir, file_counts["logs"]),
            ("exports", self.exports_dir, file_counts["exports"])
        ]

        for name, directory, count in directories:
            if directory.exists():
                for file_path in directory.rglob("*"):
                    if file_path.is_file():
                        total_size += file_path.stat().st_size
                        if name in ["reviews", "places", "logs"]:
                            count += 1

        return {
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "total_files": sum(file_counts.values()),
            "file_counts": file_counts,
            "base_directory": str(self.base_dir),
            "last_updated": datetime.now().isoformat()
        }


# Global instance
output_manager = OutputManager()