# -*- coding: utf-8 -*-
"""
Force Output API - JSON + CSV Always
===================================

Additional API endpoints to force JSON + CSV output for all operations.
Integrates with the main api_v2.py Flask app.

Author: Nextzus
Date: 2025-11-11
Version: 1.0
"""
import sys
import os

# Fix Windows encoding
if sys.platform == 'win32':
    os.system('chcp 65001 > nul 2>&1')

from flask import Flask, request, jsonify
from src.utils.output_enhancer import force_json_csv_output, save_reviews_dual_format
from src.utils.output_manager import output_manager
from src.scraper.production_scraper import ProductionReview


def register_force_output_routes(app: Flask):
    """Register forced output routes with Flask app"""

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
                'message': f"Successfully saved {len(reviews)} reviews in JSON + CSV format",
                'files': file_paths,
                'outputs_directory': str(output_manager.base_dir),
                'verification': {
                    'json_file': file_paths['json'],
                    'csv_file': file_paths['csv'],
                    'total_files': 2
                }
            })

        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @app.route('/api/v2/force-batch-output', methods=['POST'])
    def api_force_batch_output():
        """Force save multiple places' reviews in JSON + CSV format"""
        try:
            data = request.get_json()
            batch_data = data.get('batch', [])  # List of {reviews, place} objects
            task_id = data.get('task_id', 'batch_manual')
            settings = data.get('settings', {})

            if not batch_data:
                return jsonify({'error': 'No batch data provided'}), 400

            total_reviews = 0
            all_files_created = []

            for item in batch_data:
                reviews_data = item.get('reviews', [])
                place_info = item.get('place', {})

                if not reviews_data:
                    continue

                # Convert to ProductionReview objects
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
                    task_id=f"{task_id}_{place_info.get('name', 'unknown')}",
                    settings=settings
                )

                all_files_created.extend([file_paths['json'], file_paths['csv']])
                total_reviews += len(reviews)

            return jsonify({
                'success': True,
                'message': f"Successfully saved {total_reviews} reviews from {len(batch_data)} places in JSON + CSV format",
                'total_places': len(batch_data),
                'total_reviews': total_reviews,
                'files_created': all_files_created,
                'outputs_directory': str(output_manager.base_dir)
            })

        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

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
                'features': {
                    'forced_json_csv': True,
                    'automatic_backup': True,
                    'organized_structure': True
                }
            })

        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @app.route('/api/v2/convert-existing', methods=['POST'])
    def api_convert_existing():
        """Convert existing JSON files to CSV format"""
        try:
            data = request.get_json()
            json_file_path = data.get('json_file_path')

            if not json_file_path:
                return jsonify({'error': 'JSON file path required'}), 400

            # Read existing JSON
            import json
            from pathlib import Path

            json_path = Path(json_file_path)
            if not json_path.exists():
                return jsonify({'error': 'JSON file not found'}), 404

            with open(json_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)

            # Extract reviews data
            if 'data' in json_data:
                reviews_data = json_data['data']
            elif isinstance(json_data, list):
                reviews_data = json_data
            else:
                return jsonify({'error': 'Invalid JSON structure'}), 400

            # Convert to ProductionReview objects
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
                    place_id=review_dict.get('place_id', ''),
                    place_name=review_dict.get('place_name', '')
                )
                reviews.append(review)

            # Save CSV
            csv_path = json_path.with_suffix('.csv')
            from src.scraper.production_scraper import ProductionGoogleMapsScraper
            scraper = ProductionGoogleMapsScraper()
            scraper.export_to_csv(reviews, str(csv_path))

            return jsonify({
                'success': True,
                'message': f"Converted {len(reviews)} reviews to CSV",
                'csv_file': str(csv_path),
                'original_json': str(json_path)
            })

        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    print("[ROUTES] Registered forced output API routes:")
    print("  POST /api/v2/force-output - Force JSON + CSV output for single place")
    print("  POST /api/v2/force-batch-output - Force JSON + CSV output for multiple places")
    print("  GET  /api/v2/output-status - Get output directory status")
    print("  POST /api/v2/convert-existing - Convert existing JSON to CSV")

    return app