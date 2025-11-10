# -*- coding: utf-8 -*-
"""
Output Enhancement Module
========================

Forces JSON + CSV output for all scraping operations.
Integrates with webapp API v2 to ensure consistent dual-format output.

Author: Nextzus
Date: 2025-11-11
Version: 1.0
"""
import sys
import os

# Fix Windows encoding
if sys.platform == 'win32':
    os.system('chcp 65001 > nul 2>&1')

import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

# Import our modules
from src.utils.output_manager import output_manager


def force_json_csv_output(reviews: List[Any], places: List[Dict], task_id: str, settings: Dict) -> Dict[str, Any]:
    """
    Force save reviews in BOTH JSON and CSV formats automatically

    Args:
        reviews: List of ProductionReview objects
        places: List of place dictionaries from task
        task_id: Task ID for tracking
        settings: Scraper settings used

    Returns:
        Dictionary with output file paths and statistics
    """
    output_stats = {
        'total_places': len(places),
        'total_reviews': len(reviews),
        'files_created': [],
        'outputs_directory': str(output_manager.base_dir)
    }

    print(f"[OUTPUT] Forcing JSON + CSV output for {len(places)} places...")

    # Group reviews by place
    place_review_groups = {}
    for review in reviews:
        place_id = review.place_id
        if place_id not in place_review_groups:
            place_review_groups[place_id] = []
        place_review_groups[place_id].append(review)

    # Save each place's reviews with OutputManager (automatically creates JSON + CSV)
    for place in places:
        place_id = place['place_id']
        place_name = place['name']

        if place_id in place_review_groups:
            place_reviews = place_review_groups[place_id]

            # Convert ProductionReview objects to dictionaries
            place_reviews_data = []
            for review in place_reviews:
                review_dict = {
                    'review_id': review.review_id,
                    'author_name': review.author_name,
                    'author_url': review.author_url,
                    'author_reviews_count': review.author_reviews_count,
                    'rating': review.rating,
                    'date_formatted': review.date_formatted,
                    'date_relative': review.date_relative,
                    'review_text': review.review_text,
                    'review_likes': review.review_likes,
                    'review_photos_count': review.review_photos_count,
                    'owner_response': review.owner_response,
                    'page_number': review.page_number,
                    'place_id': review.place_id,
                    'place_name': review.place_name
                }
                place_reviews_data.append(review_dict)

            # Use OutputManager to save BOTH JSON and CSV automatically
            file_paths = output_manager.save_reviews(
                reviews=place_reviews_data,
                place_name=place_name,
                place_id=place_id,
                task_id=task_id,
                settings=settings
            )

            output_stats['files_created'].extend([
                file_paths['json'],
                file_paths['csv']
            ])

            print(f"[OK] {place_name}: {len(place_reviews)} reviews → JSON + CSV")

        else:
            print(f"[WARNING] No reviews found for {place_name}")

    # Save consolidated files for all places together
    all_reviews_data = []
    for review in reviews:
        review_dict = {
            'review_id': review.review_id,
            'author_name': review.author_name,
            'author_url': review.author_url,
            'author_reviews_count': review.author_reviews_count,
            'rating': review.rating,
            'date_formatted': review.date_formatted,
            'date_relative': review.date_relative,
            'review_text': review.review_text,
            'review_likes': review.review_likes,
            'review_photos_count': review.review_photos_count,
            'owner_response': review.owner_response,
            'page_number': review.page_number,
            'place_id': review.place_id,
            'place_name': review.place_name
        }
        all_reviews_data.append(review_dict)

    # Create consolidated metadata with all reviews
    consolidated_metadata = {
        "task_info": {
            "task_id": task_id,
            "created_at": datetime.now().isoformat(),
            "total_places": len(places),
            "total_reviews": len(reviews)
        },
        "settings": settings,
        "places": places,
        "data": all_reviews_data
    }

    # Save consolidated JSON
    from src.scraper.production_scraper import ProductionGoogleMapsScraper
    scraper = ProductionGoogleMapsScraper()

    # Create consolidated files in exports directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    consolidated_name = f"consolidated_{task_id}_{timestamp}"

    json_path = output_manager.exports_dir / f"{consolidated_name}.json"
    csv_path = output_manager.exports_dir / f"{consolidated_name}.csv"

    # Save consolidated JSON
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(consolidated_metadata, f, ensure_ascii=False, indent=2)

    # Save consolidated CSV
    if all_reviews_data:
        scraper.export_to_csv(reviews, str(csv_path))

    output_stats['files_created'].extend([
        str(json_path),
        str(csv_path)
    ])

    # Final summary
    print(f"[COMPLETE] Output Summary:")
    print(f"  - Total Places: {len(places)}")
    print(f"  - Total Reviews: {len(reviews)}")
    print(f"  - Files Created: {len(output_stats['files_created'])} (JSON + CSV pairs)")
    print(f"  - Output Directory: {output_manager.base_dir}")

    return output_stats


def verify_output_files(output_paths: List[str]) -> Dict[str, bool]:
    """
    Verify that all output files were created successfully

    Args:
        output_paths: List of file paths to verify

    Returns:
        Dictionary with verification results
    """
    verification = {
        'total_files': len(output_paths),
        'existing_files': 0,
        'missing_files': [],
        'file_sizes': {}
    }

    for file_path in output_paths:
        path = Path(file_path)
        if path.exists():
            verification['existing_files'] += 1
            verification['file_sizes'][file_path] = path.stat().st_size
        else:
            verification['missing_files'].append(file_path)

    return verification


# Convenience function for direct usage
def save_reviews_dual_format(reviews: List[Any], place_name: str, place_id: str,
                             task_id: str, settings: Dict) -> Dict[str, str]:
    """
    Quick function to save reviews in both JSON and CSV formats

    Returns:
        Dictionary with json and csv file paths
    """
    reviews_data = []
    for review in reviews:
        review_dict = {
            'review_id': review.review_id,
            'author_name': review.author_name,
            'author_url': review.author_url,
            'author_reviews_count': review.author_reviews_count,
            'rating': review.rating,
            'date_formatted': review.date_formatted,
            'date_relative': review.date_relative,
            'review_text': review.review_text,
            'review_likes': review.review_likes,
            'review_photos_count': review.review_photos_count,
            'owner_response': review.owner_response,
            'page_number': review.page_number,
            'place_id': review.place_id,
            'place_name': review.place_name
        }
        reviews_data.append(review_dict)

    # OutputManager automatically creates both JSON and CSV
    file_paths = output_manager.save_reviews(
        reviews=reviews_data,
        place_name=place_name,
        place_id=place_id,
        task_id=task_id,
        settings=settings
    )

    return file_paths