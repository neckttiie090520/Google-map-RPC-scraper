# -*- coding: utf-8 -*-
"""
Google Maps Protocol Buffer Analyzer
=================================

Comprehensive PB analysis tool for debugging and understanding Google Maps RPC responses.
Inspired by SerpApi's google-maps-pb-decoder with Python implementation.

Features:
1. Response structure analysis and validation
2. Field mapping discovery and documentation
3. PB parameter decoding and encoding
4. Change detection for Google API updates
5. Developer debugging utilities

Author: Nextzus
Date: 2025-11-11
"""

import sys
import os
import json
import re
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from datetime import datetime
from urllib.parse import quote, unquote

# Fix Windows encoding
if sys.platform == 'win32':
    os.system('chcp 65001 > nul 2>&1')


@dataclass
class PBAnalysisResult:
    """Result of PB analysis"""
    analysis_type: str
    timestamp: str
    success: bool
    data: Dict[str, Any]
    warnings: List[str]
    recommendations: List[str]


@dataclass
class FieldMapping:
    """Field mapping information"""
    field_name: str
    path: List[int]
    description: str
    data_type: str
    example_value: Any
    found: bool = True


class GoogleMapsPBAnalyzer:
    """
    Comprehensive Google Maps Protocol Buffer analyzer for debugging and development.

    Inspired by SerpApi's google-maps-pb-decoder but enhanced for production use.
    """

    def __init__(self, debug_mode: bool = False):
        """
        Initialize PB Analyzer

        Args:
            debug_mode: Enable verbose debugging output
        """
        self.debug_mode = debug_mode
        self.analysis_history = []

        # Known field mappings from production scraper experience
        self.known_mappings = {
            # Review fields
            'review_id': {'path': [0], 'type': 'str', 'desc': 'Unique review identifier'},
            'author_name': {'path': [1, 4, 5, 0], 'type': 'str', 'desc': 'Reviewer name'},
            'author_url': {'path': [1, 4, 2, 0], 'type': 'str', 'desc': 'Reviewer profile URL'},
            'author_reviews_count': {'path': [1, 4, 15, 1], 'type': 'int', 'desc': 'Total reviews by author'},
            'rating': {'path': [2, 0, 0], 'type': 'int', 'desc': 'Star rating (1-5)'},
            'review_text': {'path': [2, 15, 0, 0], 'type': 'str', 'desc': 'Review content'},
            'review_likes': {'path': [2, 16], 'type': 'int', 'desc': 'Number of helpful votes'},
            'review_photos_count': {'path': [2, 22], 'type': 'int', 'desc': 'Number of attached photos'},
            'owner_response': {'path': [2, 19, 0, 1], 'type': 'str', 'desc': 'Business owner response'},

            # Date fields (multiple fallback paths)
            'date_primary': {'path': [2, 2, 0, 1, 21, 6, 8], 'type': 'list', 'desc': 'Primary date array [Y, M, D]'},
            'date_alt1': {'path': [2, 2, 'search_first_5'], 'type': 'list', 'desc': 'Alternative date in container'},
            'date_fallback': {'path': [2, 21, 6, 8], 'type': 'list', 'desc': 'Fallback date array'},
            'date_relative': {'path': [2, 1], 'type': 'str', 'desc': 'Relative date string'},

            # Place search fields
            'place_id': {'path': [10], 'type': 'str', 'desc': 'Google Maps place ID'},
            'place_name': {'path': [11], 'type': 'str', 'desc': 'Place name'},
            'place_rating': {'path': [4, 7], 'type': 'float', 'desc': 'Average rating'},
            'place_reviews': {'path': [4, 8], 'type': 'int', 'desc': 'Total review count'},
            'place_address': {'path': [2], 'type': 'list', 'desc': 'Address components'},
            'place_coords': {'path': [9], 'type': 'list', 'desc': 'Coordinates [lat, lon]'},
            'place_category': {'path': [13], 'type': 'list', 'desc': 'Category list'},
        }

    def safe_get(self, data: Any, *indices, default=None) -> Any:
        """
        Safely navigate nested data structure with multiple strategies

        Args:
            data: Data structure to navigate
            *indices: Path indices (supports 'search_first_5' pattern)
            default: Default value if path not found

        Returns:
            Extracted value or default
        """
        try:
            current = data
            for idx in indices:
                if current is None:
                    return default

                if isinstance(idx, str) and idx.startswith('search_first_'):
                    # Special pattern: search first N elements
                    n = int(idx.split('_')[2])
                    if isinstance(current, list) and len(current) > 0:
                        for i in range(min(n, len(current))):
                            item = current[i]
                            if isinstance(item, list) and len(item) > 0:
                                return item
                    return default
                elif isinstance(current, (list, tuple)):
                    if isinstance(idx, int) and 0 <= idx < len(current):
                        current = current[idx]
                    else:
                        return default
                elif isinstance(current, dict):
                    current = current.get(idx, default)
                else:
                    return default

            return current if current is not None else default

        except (IndexError, TypeError, KeyError, AttributeError):
            return default

    def analyze_response_structure(self, response_data: Any, analysis_type: str = "general") -> PBAnalysisResult:
        """
        Analyze Google Maps RPC response structure

        Args:
            response_data: Raw response data from Google Maps RPC
            analysis_type: Type of analysis (general, reviews, places, debug)

        Returns:
            PBAnalysisResult with comprehensive structure analysis
        """
        timestamp = datetime.now().isoformat()
        warnings = []
        recommendations = []

        try:
            analysis_data = {
                'structure_type': self._detect_structure_type(response_data),
                'total_depth': self._calculate_depth(response_data),
                'array_count': self._count_arrays(response_data),
                'field_count': self._count_fields(response_data),
                'sample_structure': self._generate_sample_structure(response_data)
            }

            # Add specific analysis based on type
            if analysis_type == "reviews":
                analysis_data.update(self._analyze_reviews_structure(response_data))
            elif analysis_type == "places":
                analysis_data.update(self._analyze_places_structure(response_data))
            elif analysis_type == "debug":
                analysis_data.update(self._debug_structure(response_data))

            # Add field mapping validation
            field_validation = self._validate_field_mappings(response_data)
            analysis_data['field_validation'] = field_validation

            # Generate warnings and recommendations
            if field_validation['missing_fields']:
                warnings.append(f"Missing expected fields: {field_validation['missing_fields']}")

            if field_validation['changed_structure']:
                warnings.append("Structure may have changed from expected format")
                recommendations.append("Update field mappings in scraper")

            # Success
            result = PBAnalysisResult(
                analysis_type=analysis_type,
                timestamp=timestamp,
                success=True,
                data=analysis_data,
                warnings=warnings,
                recommendations=recommendations
            )

        except Exception as e:
            result = PBAnalysisResult(
                analysis_type=analysis_type,
                timestamp=timestamp,
                success=False,
                data={'error': str(e)},
                warnings=[f"Analysis failed: {e}"],
                recommendations=["Check response data format"]
            )

        # Store in history
        self.analysis_history.append(result)

        return result

    def analyze_pb_parameters(self, pb_string: str) -> PBAnalysisResult:
        """
        Decode and analyze Google Maps pb parameters

        Args:
            pb_string: Protocol Buffer parameter string

        Returns:
            PBAnalysisResult with pb parameter analysis
        """
        timestamp = datetime.now().isoformat()
        warnings = []
        recommendations = []

        try:
            # Decode URL encoding
            decoded_pb = unquote(pb_string)

            # Parse structure
            pb_structure = self._parse_pb_structure(decoded_pb)

            analysis_data = {
                'original_pb': pb_string,
                'decoded_pb': decoded_pb,
                'structure': pb_structure,
                'components': self._extract_pb_components(decoded_pb),
                'place_id_extracted': self._extract_place_id_from_pb(decoded_pb),
                'pagination_tokens': self._extract_pagination_tokens(decoded_pb)
            }

            # Generate recommendations
            if not analysis_data['place_id_extracted']:
                warnings.append("No place ID found in pb parameters")
                recommendations.append("Verify pb parameter structure")

            result = PBAnalysisResult(
                analysis_type="pb_parameters",
                timestamp=timestamp,
                success=True,
                data=analysis_data,
                warnings=warnings,
                recommendations=recommendations
            )

        except Exception as e:
            result = PBAnalysisResult(
                analysis_type="pb_parameters",
                timestamp=timestamp,
                success=False,
                data={'error': str(e), 'pb_string': pb_string},
                warnings=[f"PB analysis failed: {e}"],
                recommendations=["Check pb parameter format"]
            )

        self.analysis_history.append(result)
        return result

    def validate_review_parsing(self, review_data: Any, expected_fields: List[str] = None) -> PBAnalysisResult:
        """
        Validate review parsing against expected structure

        Args:
            review_data: Parsed review data
            expected_fields: List of expected field names

        Returns:
            PBAnalysisResult with validation results
        """
        if expected_fields is None:
            expected_fields = list(self.known_mappings.keys())

        timestamp = datetime.now().isoformat()
        warnings = []
        recommendations = []

        try:
            validation_results = {}
            found_fields = []
            missing_fields = []

            for field_name in expected_fields:
                if field_name in self.known_mappings:
                    field_info = self.known_mappings[field_name]
                    path = field_info['path']

                    # Handle special patterns
                    actual_path = []
                    for idx in path:
                        if isinstance(idx, str) and idx.startswith('search_first_'):
                            # For validation, we'll check if the path exists
                            continue
                        actual_path.append(idx)

                    value = self.safe_get(review_data, *actual_path)

                    validation_results[field_name] = {
                        'path': path,
                        'value': value if not isinstance(value, (list, dict)) or len(str(value)) < 100 else type(value).__name__,
                        'found': value is not None and value != ""
                    }

                    if validation_results[field_name]['found']:
                        found_fields.append(field_name)
                    else:
                        missing_fields.append(field_name)
                else:
                    warnings.append(f"Unknown field: {field_name}")

            analysis_data = {
                'validation_results': validation_results,
                'found_fields': found_fields,
                'missing_fields': missing_fields,
                'field_coverage': len(found_fields) / len(expected_fields) if expected_fields else 0,
                'review_size': len(str(review_data))
            }

            # Generate recommendations
            if analysis_data['field_coverage'] < 0.8:
                recommendations.append("Low field coverage - check parsing logic")

            if missing_fields:
                recommendations.append(f"Focus on missing fields: {missing_fields[:3]}")

            result = PBAnalysisResult(
                analysis_type="review_validation",
                timestamp=timestamp,
                success=True,
                data=analysis_data,
                warnings=warnings,
                recommendations=recommendations
            )

        except Exception as e:
            result = PBAnalysisResult(
                analysis_type="review_validation",
                timestamp=timestamp,
                success=False,
                data={'error': str(e)},
                warnings=[f"Validation failed: {e}"],
                recommendations=["Check review data format"]
            )

        self.analysis_history.append(result)
        return result

    def generate_field_documentation(self, response_samples: List[Any]) -> Dict[str, Any]:
        """
        Generate comprehensive field documentation from response samples

        Args:
            response_samples: List of response samples to analyze

        Returns:
            Dictionary with field documentation
        """
        documentation = {
            'generated_at': datetime.now().isoformat(),
            'sample_count': len(response_samples),
            'fields': {}
        }

        for field_name, field_info in self.known_mappings.items():
            field_docs = {
                'description': field_info['desc'],
                'path': field_info['path'],
                'type': field_info['type'],
                'examples': [],
                'success_rate': 0,
                'sample_values': []
            }

            found_count = 0
            for sample in response_samples:
                value = self.safe_get(sample, *field_info['path'])
                if value is not None and value != "":
                    found_count += 1
                    if len(str(value)) < 200:
                        field_docs['examples'].append(value)
                    field_docs['sample_values'].append(str(value)[:100])

            field_docs['success_rate'] = found_count / len(response_samples) if response_samples else 0
            documentation['fields'][field_name] = field_docs

        return documentation

    def detect_structure_changes(self, current_data: Any, baseline_data: Any = None) -> Dict[str, Any]:
        """
        Detect changes in Google Maps response structure

        Args:
            current_data: Current response data
            baseline_data: Baseline data to compare against

        Returns:
            Dictionary with change detection results
        """
        if baseline_data is None:
            # Use current data as baseline
            return {
                'status': 'baseline_established',
                'current_structure': self._get_structure_fingerprint(current_data),
                'recommendations': ['Save this as baseline for future comparisons']
            }

        current_fingerprint = self._get_structure_fingerprint(current_data)
        baseline_fingerprint = self._get_structure_fingerprint(baseline_data)

        changes = {
            'structure_changed': current_fingerprint != baseline_fingerprint,
            'current_fingerprint': current_fingerprint,
            'baseline_fingerprint': baseline_fingerprint,
            'differences': []
        }

        if changes['structure_changed']:
            changes['recommendations'] = [
                'Review field mappings',
                'Update parsing logic',
                'Test with new structure'
            ]

        return changes

    # Private helper methods

    def _detect_structure_type(self, data: Any) -> str:
        """Detect the type of response structure"""
        if not isinstance(data, list) or len(data) == 0:
            return "unknown"

        # Look for patterns
        if len(data) > 10 and all(isinstance(x, (list, dict)) for x in data[:5]):
            return "reviews_response"
        elif len(data) == 2 and isinstance(data[0], list) and isinstance(data[1], list):
            return "search_response"
        elif isinstance(data[0], list) and len(data[0]) > 10:
            return "place_details"
        else:
            return "mixed_structure"

    def _calculate_depth(self, data: Any, current_depth: int = 0) -> int:
        """Calculate maximum depth of nested structure"""
        if not isinstance(data, (list, dict)) or current_depth > 10:
            return current_depth

        if isinstance(data, list):
            return max([self._calculate_depth(item, current_depth + 1) for item in data[:5]], default=current_depth)
        elif isinstance(data, dict):
            return max([self._calculate_depth(value, current_depth + 1) for value in data.values()], default=current_depth)

        return current_depth

    def _count_arrays(self, data: Any) -> int:
        """Count number of arrays in structure"""
        if not isinstance(data, (list, dict)):
            return 0

        count = 1 if isinstance(data, list) else 0
        if isinstance(data, list):
            count += sum([self._count_arrays(item) for item in data[:10]])
        elif isinstance(data, dict):
            count += sum([self._count_arrays(value) for value in data.values()])

        return count

    def _count_fields(self, data: Any) -> int:
        """Count total number of primitive fields"""
        if not isinstance(data, (list, dict)):
            return 1 if data is not None else 0

        if isinstance(data, list):
            return sum([self._count_fields(item) for item in data[:10]])
        elif isinstance(data, dict):
            return sum([self._count_fields(value) for value in data.values()])

        return 0

    def _generate_sample_structure(self, data: Any, max_depth: int = 3, current_depth: int = 0) -> Dict:
        """Generate simplified structure sample"""
        if current_depth >= max_depth:
            return str(type(data).__name__)

        if isinstance(data, list):
            if len(data) == 0:
                return "[]"
            return [self._generate_sample_structure(data[0] if data else None, max_depth, current_depth + 1)]
        elif isinstance(data, dict):
            return {k: self._generate_sample_structure(v, max_depth, current_depth + 1)
                   for k, v in list(data.items())[:5]}
        else:
            return str(type(data).__name__)

    def _analyze_reviews_structure(self, data: Any) -> Dict[str, Any]:
        """Analyze reviews-specific structure"""
        reviews_analysis = {
            'estimated_review_count': 0,
            'has_reviews_section': False,
            'pagination_available': False,
            'date_fields_found': []
        }

        # Look for reviews section (typically at index 2)
        reviews_section = self.safe_get(data, 2)
        if reviews_section and isinstance(reviews_section, list):
            reviews_analysis['has_reviews_section'] = True
            reviews_analysis['estimated_review_count'] = len(reviews_section)

            # Check for pagination token
            if len(data) > 1 and isinstance(data[1], str):
                reviews_analysis['pagination_available'] = True

            # Check date fields in first few reviews
            for i, review in enumerate(reviews_section[:3]):
                if isinstance(review, list) and len(review) > 0:
                    el = review[0] if isinstance(review[0], list) else review

                    # Check various date field paths
                    date_paths = [
                        self.safe_get(el, 2, 2, 0, 1, 21, 6, 8),
                        self.safe_get(el, 2, 21, 6, 8),
                        self.safe_get(el, 2, 1)
                    ]

                    for j, date_val in enumerate(date_paths):
                        if date_val:
                            reviews_analysis['date_fields_found'].append(f"review_{i}_path_{j}")

        return reviews_analysis

    def _analyze_places_structure(self, data: Any) -> Dict[str, Any]:
        """Analyze places search structure"""
        places_analysis = {
            'estimated_place_count': 0,
            'has_places_section': False,
            'has_direct_result': False,
            'search_metadata': {}
        }

        # Check for direct result (single place)
        if len(data) >= 2 and isinstance(data[0], (str, list)) and isinstance(data[1], list):
            if isinstance(data[0], str) and isinstance(data[1], list) and len(data[1]) > 10:
                places_analysis['has_direct_result'] = True
                places_analysis['estimated_place_count'] = 1

        # Check for list results
        if isinstance(data, list) and len(data) > 0:
            items_section = self.safe_get(data, 0, 1)
            if items_section and isinstance(items_section, list):
                places_analysis['has_places_section'] = True
                places_analysis['estimated_place_count'] = len([x for x in items_section if isinstance(x, list)]) - 1  # Skip first item

        return places_analysis

    def _debug_structure(self, data: Any) -> Dict[str, Any]:
        """Detailed debugging analysis"""
        debug_info = {
            'data_type': str(type(data)),
            'length': len(data) if hasattr(data, '__len__') else None,
            'first_elements': [],
            'unusual_patterns': []
        }

        # Sample first few elements
        if isinstance(data, list):
            for i, item in enumerate(data[:5]):
                debug_info['first_elements'].append({
                    'index': i,
                    'type': str(type(item)),
                    'length': len(item) if hasattr(item, '__len__') else None,
                    'preview': str(item)[:100] if item else None
                })

        # Look for unusual patterns
        if isinstance(data, list) and len(data) > 0:
            first_item = data[0]
            if isinstance(first_item, str) and ':' in first_item and first_item.startswith('0x'):
                debug_info['unusual_patterns'].append('Possible place_id in first position')

        return debug_info

    def _validate_field_mappings(self, data: Any) -> Dict[str, Any]:
        """Validate known field mappings against actual data"""
        validation = {
            'total_fields': len(self.known_mappings),
            'found_fields': [],
            'missing_fields': [],
            'changed_structure': False
        }

        for field_name, field_info in self.known_mappings.items():
            path = field_info['path']
            value = self.safe_get(data, *path)

            if value is not None and value != "":
                validation['found_fields'].append(field_name)
            else:
                validation['missing_fields'].append(field_name)

        # Check if structure has changed significantly
        missing_ratio = len(validation['missing_fields']) / validation['total_fields']
        validation['changed_structure'] = missing_ratio > 0.3  # If >30% fields missing

        return validation

    def _parse_pb_structure(self, pb_string: str) -> Dict[str, Any]:
        """Parse pb parameter string into structure"""
        structure = {
            'components': [],
            'parameters': {}
        }

        # Split by ! markers
        parts = pb_string.split('!')

        for i, part in enumerate(parts):
            if part:
                component = {
                    'index': i,
                    'raw_value': part,
                    'type': self._detect_component_type(part),
                    'decoded_value': None
                }

                # Try to decode numeric values
                try:
                    if part.isdigit():
                        component['decoded_value'] = int(part)
                    elif part.replace('.', '').isdigit():
                        component['decoded_value'] = float(part)
                    elif part.startswith('0x') and ':' in part:
                        component['decoded_value'] = part  # Place ID
                except:
                    pass

                structure['components'].append(component)
                structure['parameters'][f'param_{i}'] = component

        return structure

    def _detect_component_type(self, component: str) -> str:
        """Detect the type of a pb component"""
        if not component:
            return 'empty'
        elif component.isdigit():
            return 'integer'
        elif component.replace('.', '').isdigit():
            return 'float'
        elif component.startswith('0x') and ':' in component:
            return 'place_id'
        elif component.startswith('0x'):
            return 'hex_id'
        elif component.startswith('http'):
            return 'url'
        elif any(c in component for c in ['ฟั', 'สั', 'อ.', 'น.']):  # Thai characters
            return 'thai_text'
        elif any(c.isalpha() for c in component):
            return 'text'
        else:
            return 'unknown'

    def _extract_pb_components(self, pb_string: str) -> List[Dict[str, Any]]:
        """Extract and analyze individual PB components"""
        components = []
        parts = pb_string.split('!')

        for i, part in enumerate(parts):
            if part:
                components.append({
                    'position': i,
                    'raw': part,
                    'length': len(part),
                    'type': self._detect_component_type(part),
                    'description': self._describe_pb_component(part, i)
                })

        return components

    def _describe_pb_component(self, component: str, position: int) -> str:
        """Describe what a PB component likely represents"""
        if position == 1 and component.startswith('0x'):
            return "Place ID"
        elif position == 5 and component.endswith('e81'):
            return "Magic number / version"
        elif component.isdigit() and len(component) == 1:
            return "Flag or option"
        elif component.startswith('1s') or component.startswith('2s'):
            return "Size parameter"
        elif component.startswith('1i') or component.startswith('2i'):
            return "Index parameter"
        elif component == 'm':
            return "Multi-dimensional marker"
        else:
            return f"Component at position {position}"

    def _extract_place_id_from_pb(self, pb_string: str) -> Optional[str]:
        """Extract place ID from PB parameters"""
        parts = pb_string.split('!')
        for part in parts:
            if part.startswith('0x') and ':' in part:
                return part
        return None

    def _extract_pagination_tokens(self, pb_string: str) -> List[str]:
        """Extract pagination tokens from PB parameters"""
        tokens = []
        parts = pb_string.split('!')

        for part in parts:
            # Look for base64-like strings (pagination tokens are often base64 encoded)
            if len(part) > 20 and part.isalnum():
                tokens.append(part)

        return tokens

    def _get_structure_fingerprint(self, data: Any) -> str:
        """Generate a fingerprint of the structure for comparison"""
        try:
            if not isinstance(data, list):
                return str(type(data))

            # Create simplified fingerprint
            fingerprint_parts = []
            fingerprint_parts.append(f"len_{len(data)}")

            # Sample first few elements
            for i in range(min(5, len(data))):
                item = data[i]
                if isinstance(item, list):
                    fingerprint_parts.append(f"arr_{i}_len_{len(item)}")
                elif isinstance(item, str):
                    fingerprint_parts.append(f"str_{i}_{len(item)}")
                elif isinstance(item, (int, float)):
                    fingerprint_parts.append(f"num_{i}_{item}")
                else:
                    fingerprint_parts.append(f"type_{i}_{type(item).__name__}")

            return '_'.join(fingerprint_parts)

        except Exception:
            return f"fingerprint_error_{datetime.now().timestamp()}"

    def print_analysis_report(self, result: PBAnalysisResult, verbose: bool = False):
        """Print formatted analysis report"""
        print(f"\n{'='*60}")
        print(f"🔍 Google Maps PB Analysis Report")
        print(f"{'='*60}")
        print(f"Analysis Type: {result.analysis_type}")
        print(f"Timestamp: {result.timestamp}")
        print(f"Status: {'✅ SUCCESS' if result.success else '❌ FAILED'}")

        if result.warnings:
            print(f"\n⚠️  Warnings:")
            for warning in result.warnings:
                print(f"   - {warning}")

        if result.recommendations:
            print(f"\n💡 Recommendations:")
            for rec in result.recommendations:
                print(f"   - {rec}")

        if result.success and verbose:
            print(f"\n📊 Analysis Data:")
            print(json.dumps(result.data, indent=2, ensure_ascii=False, default=str))

        print(f"\n{'='*60}\n")

    def export_analysis_history(self, filename: str) -> bool:
        """Export analysis history to JSON file"""
        try:
            history_data = {
                'exported_at': datetime.now().isoformat(),
                'total_analyses': len(self.analysis_history),
                'analyses': [asdict(result) for result in self.analysis_history]
            }

            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(history_data, f, ensure_ascii=False, indent=2)

            return True
        except Exception as e:
            print(f"Export failed: {e}")
            return False


# Global instance for easy access
pb_analyzer = GoogleMapsPBAnalyzer(debug_mode=False)


# Convenience functions
def analyze_response(data: Any, analysis_type: str = "general") -> PBAnalysisResult:
    """Quick function to analyze response data"""
    return pb_analyzer.analyze_response_structure(data, analysis_type)


def analyze_pb_params(pb_string: str) -> PBAnalysisResult:
    """Quick function to analyze PB parameters"""
    return pb_analyzer.analyze_pb_parameters(pb_string)


def validate_review(review_data: Any, expected_fields: List[str] = None) -> PBAnalysisResult:
    """Quick function to validate review parsing"""
    return pb_analyzer.validate_review_parsing(review_data, expected_fields)