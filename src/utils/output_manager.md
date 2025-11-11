# Output Manager

## Overview

Output Manager เป็นโมดูลสำหรับจัดการไฟล์ผลลัพธ์และการส่งออกข้อมูลอย่างเป็นระเบียบ (Organized File Management) ช่วยให้ผลลัพธ์จากการ scraping มีโครงสร้างที่ชัดเจนและง่ายต่อการจัดการ

## ✨ ฟีเจอร์หลัก (Key Features)

### 📁 Organized File Structure
- ✅ **Automatic Directory Creation** สร้าง directories อัตโนมัติ
- ✅ **Date-Based Organization** จัดระเบียบตามวันที่ (YYYY-MM-DD)
- ✅ **Place-Specific Folders** แยกตามสถานที่
- ✅ **Timestamped Files** ชื่อไฟล์มี timestamp ชัดเจน

### 💾 Multiple Export Formats
- ✅ **JSON Export** ข้อมูลแบบ structured
- ✅ **CSV Export** ข้อมูลแบบ tabular
- ✅ **Metadata Files** ข้อมูลการ scraping
- ✅ **Settings Backup** บันทึก settings ที่ใช้

### 🔍 File Management
- ✅ **File Path Generation** สร้าง paths อัตโนมัติ
- ✅ **Duplicate Prevention** ป้องกันชื่อไฟล์ซ้ำ
- ✅ **File Validation** ตรวจสอบความถูกต้องของไฟล์
- ✅ **Space Management** จัดการพื้นที่ disk

## 📂 โครงสร้างไฟล์ (File Structure)

```
outputs/
├── reviews/                          # Review outputs
│   └── YYYY-MM-DD/                   # Date-based folders
│       ├── place_name_reviews_YYYYMMDD_HHMMSS.json
│       ├── place_name_reviews_YYYYMMDD_HHMMSS.csv
│       └── place_name_metadata_YYYYMMDD_HHMMSS.json
├── places/                           # Place data
│   └── YYYY-MM-DD/
│       ├── search_results_YYYYMMDD_HHMMSS.json
│       └── place_details_YYYYMMDD_HHMMSS.json
├── logs/                            # Scraping logs
│   └── YYYY-MM-DD/
│       ├── scraping_log_YYYYMMDD_HHMMSS.log
│       └── error_log_YYYYMMDD_HHMMSS.log
├── exports/                          # Processed exports
│   └── YYYY-MM-DD/
│       ├── consolidated_YYYYMMDD_HHMMSS.csv
│       └── summary_YYYYMMDD_HHMMSS.json
└── temp/                            # Temporary files
    └── processing_*.tmp
```

## 📖 API Reference

### Global Instance

```python
from src.utils.output_manager import output_manager

# Direct usage with global instance
output_manager.save_reviews(reviews, place_name, place_id)
json_path, csv_path = output_manager.get_output_paths(place_name)
```

### Core Class: OutputManager

#### Constructor

```python
class OutputManager:
    def __init__(self, base_dir: str = None):
        """
        Initialize output manager

        Args:
            base_dir: Base directory for outputs (default: auto-detect)
        """
```

#### Core Methods

**save_reviews(reviews: List[Dict], place_name: str, place_id: str) -> Tuple[str, str]**
บันทึก reviews ทั้งในรูปแบบ JSON และ CSV

```python
from src.utils.output_manager import OutputManager
from src.scraper.production_scraper import ProductionReview

# Create output manager
output_manager = OutputManager()

# Sample reviews
reviews = [
    {
        "review_id": "123",
        "author_name": "John Doe",
        "rating": 5,
        "review_text": "Great place!",
        "date_formatted": "01/01/2024"
    },
    {
        "review_id": "456",
        "author_name": "Jane Smith",
        "rating": 4,
        "review_text": "Good service",
        "date_formatted": "02/01/2024"
    }
]

# Save reviews (creates both JSON and CSV)
place_name = "Central World"
place_id = "0x30e29ecfc2f455e1:0xc4ad0280d8906604"

json_path, csv_path = output_manager.save_reviews(
    reviews=reviews,
    place_name=place_name,
    place_id=place_id
)

print(f"JSON saved to: {json_path}")
print(f"CSV saved to: {csv_path}")
```

**save_json(data: Dict, filename: str, subfolder: str = None) -> str**
บันทึกข้อมูลแบบ JSON

```python
# Save custom data
data = {
    "scraping_info": {
        "total_reviews": 150,
        "avg_rating": 4.5,
        "scraped_at": "2024-01-01T12:00:00Z"
    },
    "place_details": {
        "name": "Central World",
        "address": "Ratchadamri, Bangkok"
    }
}

json_path = output_manager.save_json(
    data=data,
    filename="scraping_summary",
    subfolder="summaries"
)

print(f"Summary saved to: {json_path}")
```

**save_csv(data: List[Dict], filename: str, subfolder: str = None) -> str**
บันทึกข้อมูลแบบ CSV

```python
# Save custom CSV data
csv_data = [
    {
        "place_name": "Central World",
        "total_reviews": 150,
        "avg_rating": 4.5,
        "category": "Shopping Mall"
    },
    {
        "place_name": "Siam Paragon",
        "total_reviews": 200,
        "avg_rating": 4.3,
        "category": "Shopping Mall"
    }
]

csv_path = output_manager.save_csv(
    data=csv_data,
    filename="place_summary",
    subfolder="summaries"
)

print(f"CSV saved to: {csv_path}")
```

**get_output_paths(place_name: str) -> Tuple[str, str]**
ดู paths สำหรับ output files

```python
# Get paths without creating files
json_path, csv_path = output_manager.get_output_paths("Central World")

print(f"JSON will be saved to: {json_path}")
print(f"CSV will be saved to: {csv_path}")

# Directory structure
# outputs/reviews/2024-01-01/Central_World_reviews_20240101_120000.json
# outputs/reviews/2024-01-01/Central_World_reviews_20240101_120000.csv
```

**create_directory_structure(place_name: str, base_path: str = None) -> str**
สร้างโครงสร้าง directories

```python
# Create directory structure manually
dir_path = output_manager.create_directory_structure(
    place_name="Siam Paragon",
    base_path="custom/reviews"
)

print(f"Directory created: {dir_path}")
# Structure: custom/reviews/2024-01-01/Siam_Paragon/
```

### Path Generation

**generate_filename(place_name: str, suffix: str, extension: str) -> str**
สร้างชื่อไฟล์แบบ standardized

```python
# Generate filenames
json_name = output_manager.generate_filename(
    place_name="Central World",
    suffix="reviews",
    extension="json"
)
print(json_name)  # "Central_World_reviews_20240101_120000.json"

csv_name = output_manager.generate_filename(
    place_name="Central World",
    suffix="reviews",
    extension="csv"
)
print(csv_name)  # "Central_World_reviews_20240101_120000.csv"
```

**sanitize_filename(filename: str) -> str**
ทำความสะอาดชื่อไฟล์

```python
# Clean problematic filenames
clean_name = output_manager.sanitize_filename("Place/Name:With*Special|Chars")
print(clean_name)  # "Place_Name_With_Special_Chars"

# Handle long names
long_name = "This is a very very long place name that might cause issues on some file systems"
clean_long = output_manager.sanitize_filename(long_name)
print(f"Original length: {len(long_name)}")
print(f"Cleaned length: {len(clean_long)}")
```

### File Operations

**file_exists(filepath: str) -> bool**
ตรวจสอบว่าไฟล์มีอยู่

```python
# Check if files exist
json_exists = output_manager.file_exists(json_path)
csv_exists = output_manager.file_exists(csv_path)

if json_exists and csv_exists:
    print("Both JSON and CSV files exist")
elif json_exists:
    print("Only JSON file exists")
elif csv_exists:
    print("Only CSV file exists")
else:
    print("No files exist yet")
```

**get_file_size(filepath: str) -> int**
ดูขนาดไฟล์

```python
# Get file sizes
json_size = output_manager.get_file_size(json_path)
csv_size = output_manager.get_file_size(csv_path)

print(f"JSON file size: {json_size:,} bytes")
print(f"CSV file size: {csv_size:,} bytes")

if json_size > 1024 * 1024:  # > 1MB
    print("JSON file is large (>1MB)")
```

**cleanup_temp_files()**
ลบไฟล์ชั่วคราว

```python
# Clean up temporary files
deleted_count = output_manager.cleanup_temp_files()
print(f"Deleted {deleted_count} temporary files")
```

## 🧪 การใช้งาน (Usage Examples)

### Basic Review Export

```python
from src.utils.output_manager import OutputManager
from src.scraper.production_scraper import ProductionReview

def export_reviews_example():
    # Create output manager
    output_manager = OutputManager()

    # Sample production reviews
    reviews = [
        ProductionReview(
            review_id="123",
            author_name="John Doe",
            author_url="",
            author_reviews_count=10,
            rating=5,
            date_formatted="01/01/2024",
            date_relative="1 week ago",
            review_text="Amazing place! Highly recommended.",
            review_text_translated="",
            original_language="en",
            target_language="th",
            review_likes=5,
            review_photos_count=2,
            owner_response="Thank you for your review!",
            owner_response_translated="",
            page_number=1
        ),
        ProductionReview(
            review_id="456",
            author_name="สมชาย",
            author_url="",
            author_reviews_count=5,
            rating=4,
            date_formatted="02/01/2024",
            date_relative="2 days ago",
            review_text="สถานที่ดีครับ",
            review_text_translated="",
            original_language="th",
            target_language="en",
            review_likes=3,
            review_photos_count=0,
            owner_response="ขอบคุณที่มาใช้บริการ",
            owner_response_translated="",
            page_number=1
        )
    ]

    # Convert to dictionaries for saving
    review_dicts = [review.to_dict() for review in reviews]

    # Save reviews
    place_name = "Central World"
    place_id = "0x30e29ecfc2f455e1:0xc4ad0280d8906604"

    json_path, csv_path = output_manager.save_reviews(
        reviews=review_dicts,
        place_name=place_name,
        place_id=place_id
    )

    print(f"✅ Reviews exported successfully!")
    print(f"📄 JSON: {json_path}")
    print(f"📊 CSV: {csv_path}")

    # Verify files were created
    assert output_manager.file_exists(json_path)
    assert output_manager.file_exists(csv_path)

    return json_path, csv_path

# Run example
json_file, csv_file = export_reviews_example()
```

### Advanced Export with Metadata

```python
def advanced_export_example():
    output_manager = OutputManager()

    # Review data
    reviews = [...]  # List of review dictionaries

    # Place information
    place_info = {
        "place_id": "0x30e29ecfc2f455e1:0xc4ad0280d8906604",
        "name": "Central World",
        "address": "Ratchadamri Road, Bangkok",
        "rating": 4.5,
        "total_reviews": len(reviews),
        "category": "Shopping Mall",
        "coordinates": {
            "lat": 13.7465,
            "lng": 100.5350
        }
    }

    # Scraping metadata
    scraping_metadata = {
        "scraped_at": datetime.now().isoformat(),
        "scraper_version": "1.0.0",
        "scraping_duration": 120.5,  # seconds
        "total_requests": 25,
        "successful_requests": 23,
        "failed_requests": 2,
        "settings": {
            "max_reviews": 1000,
            "language": "th",
            "region": "th",
            "date_range": "1year"
        }
    }

    # Create comprehensive data structure
    export_data = {
        "place_info": place_info,
        "scraping_metadata": scraping_metadata,
        "reviews": reviews,
        "statistics": {
            "total_reviews": len(reviews),
            "avg_rating": sum(r['rating'] for r in reviews) / len(reviews),
            "rating_distribution": {
                "5": sum(1 for r in reviews if r['rating'] == 5),
                "4": sum(1 for r in reviews if r['rating'] == 4),
                "3": sum(1 for r in reviews if r['rating'] == 3),
                "2": sum(1 for r in reviews if r['rating'] == 2),
                "1": sum(1 for r in reviews if r['rating'] == 1)
            }
        }
    }

    # Save comprehensive JSON
    place_name = place_info["name"]
    json_path = output_manager.save_json(
        data=export_data,
        filename=f"{place_name}_full_export",
        subfolder="comprehensive"
    )

    # Save just reviews for CSV (flatten structure)
    csv_data = []
    for review in reviews:
        csv_row = {
            "place_name": place_info["name"],
            "place_id": place_info["place_id"],
            "place_category": place_info["category"],
            "review_id": review["review_id"],
            "author_name": review["author_name"],
            "rating": review["rating"],
            "date_formatted": review["date_formatted"],
            "review_text": review["review_text"],
            "review_likes": review["review_likes"],
            "owner_response": review.get("owner_response", "")
        }
        csv_data.append(csv_row)

    csv_path = output_manager.save_csv(
        data=csv_data,
        filename=f"{place_name}_reviews_flat",
        subfolder="comprehensive"
    )

    print(f"✅ Advanced export completed!")
    print(f"📄 JSON: {json_path}")
    print(f"📊 CSV: {csv_path}")

    # Show file sizes
    json_size = output_manager.get_file_size(json_path)
    csv_size = output_manager.get_file_size(csv_path)

    print(f"📏 JSON size: {json_size:,} bytes")
    print(f"📏 CSV size: {csv_size:,} bytes")

    return json_path, csv_path
```

### Batch Processing

```python
def batch_export_example(places_data):
    """
    Export multiple places in batch

    Args:
        places_data: List of tuples (place_name, place_id, reviews)
    """
    output_manager = OutputManager()

    export_summary = []

    for place_name, place_id, reviews in places_data:
        try:
            print(f"🔄 Exporting {place_name} ({len(reviews)} reviews)...")

            # Get output paths
            json_path, csv_path = output_manager.get_output_paths(place_name)

            # Check if files already exist
            if output_manager.file_exists(json_path):
                print(f"⚠️ Files already exist for {place_name}, skipping...")
                continue

            # Save reviews
            saved_json, saved_csv = output_manager.save_reviews(
                reviews=reviews,
                place_name=place_name,
                place_id=place_id
            )

            # Record summary
            export_summary.append({
                "place_name": place_name,
                "place_id": place_id,
                "reviews_count": len(reviews),
                "json_path": saved_json,
                "csv_path": saved_csv,
                "json_size": output_manager.get_file_size(saved_json),
                "csv_size": output_manager.get_file_size(saved_csv),
                "status": "success"
            })

            print(f"✅ {place_name} exported successfully")

        except Exception as e:
            print(f"❌ Failed to export {place_name}: {e}")
            export_summary.append({
                "place_name": place_name,
                "place_id": place_id,
                "status": "failed",
                "error": str(e)
            })

    # Save batch summary
    if export_summary:
        summary_path = output_manager.save_json(
            data={
                "batch_export_at": datetime.now().isoformat(),
                "total_places": len(places_data),
                "successful_exports": sum(1 for item in export_summary if item["status"] == "success"),
                "failed_exports": sum(1 for item in export_summary if item["status"] == "failed"),
                "exports": export_summary
            },
            filename="batch_export_summary",
            subfolder="summaries"
        )

        print(f"📊 Batch summary saved to: {summary_path}")

    return export_summary

# Usage
places_data = [
    ("Central World", "place_id_1", reviews_1),
    ("Siam Paragon", "place_id_2", reviews_2),
    ("MBK Center", "place_id_3", reviews_3)
]

summary = batch_export_example(places_data)
```

### Custom Directory Structure

```python
def custom_structure_example():
    # Create custom output manager
    custom_base = "custom_outputs"
    output_manager = OutputManager(base_dir=custom_base)

    # Create custom directory structure
    custom_dir = output_manager.create_directory_structure(
        place_name="Test Place",
        base_path="test/reviews"
    )

    print(f"Custom directory: {custom_dir}")

    # Save data in custom location
    test_data = [{"id": 1, "name": "Test"}]
    json_path = output_manager.save_json(
        data=test_data,
        filename="test_data",
        subfolder="test/data"
    )

    print(f"Custom JSON path: {json_path}")

    return json_path
```

## ⚙️ การคอนฟิก (Configuration)

### Directory Configuration

```python
from src.utils.output_manager import OutputManager

# Custom base directory
output_manager = OutputManager(base_dir="my_outputs")

# Directory naming patterns
def custom_place_naming(place_name):
    """Custom naming for place directories"""
    # Convert to lowercase, replace spaces with underscores
    return place_name.lower().replace(" ", "_").replace("-", "_")

# Custom timestamp format
import datetime

def custom_timestamp():
    """Custom timestamp format"""
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
```

### File Size Limits

```python
# Configure file size limits (in bytes)
MAX_JSON_SIZE = 50 * 1024 * 1024  # 50MB
MAX_CSV_SIZE = 100 * 1024 * 1024   # 100MB

def check_file_size_limit(filepath, max_size):
    """Check if file exceeds size limit"""
    if os.path.exists(filepath):
        size = os.path.getsize(filepath)
        if size > max_size:
            print(f"⚠️ File size ({size:,} bytes) exceeds limit ({max_size:,} bytes)")
            return False
    return True
```

## 📊 ประสิทธิภาพ (Performance)

### File I/O Optimization

```python
import json
import csv
from pathlib import Path

class OptimizedOutputManager(OutputManager):
    """Optimized output manager for large datasets"""

    def save_large_json(self, data, filename, chunk_size=1000):
        """Save large JSON files in chunks"""
        filepath = self._get_filepath(filename, "json", "json")

        # Use streaming JSON writer for large files
        with open(filepath, 'w', encoding='utf-8') as f:
            if isinstance(data, list):
                # Stream list items
                f.write('[')
                for i, item in enumerate(data):
                    if i > 0:
                        f.write(',')
                    json.dump(item, f, ensure_ascii=False)
                    if i % chunk_size == 0 and i > 0:
                        f.write('\n')  # Add newline for readability
                f.write(']')
            else:
                json.dump(data, f, ensure_ascii=False, indent=2)

        return filepath

    def save_large_csv(self, data, filename, chunk_size=1000):
        """Save large CSV files efficiently"""
        filepath = self._get_filepath(filename, "csv", "csv")

        if not data:
            return filepath

        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()

            # Write in chunks for memory efficiency
            for i in range(0, len(data), chunk_size):
                chunk = data[i:i + chunk_size]
                writer.writerows(chunk)

                # Force flush periodically
                if i % (chunk_size * 10) == 0:
                    f.flush()

        return filepath

# Usage for large datasets
optimized_manager = OptimizedOutputManager()

# Save 100,000 reviews efficiently
large_reviews = [...]  # Large list of reviews

json_path = optimized_manager.save_large_json(
    data=large_reviews,
    filename="large_dataset",
    chunk_size=5000
)

csv_path = optimized_manager.save_large_csv(
    data=large_reviews,
    filename="large_dataset",
    chunk_size=5000
)
```

### Memory Management

```python
def memory_efficient_export(reviews_generator, place_name):
    """Export reviews using generator for memory efficiency"""
    output_manager = OutputManager()

    # Get file paths
    json_path, csv_path = output_manager.get_output_paths(place_name)

    # Write JSON streaming
    with open(json_path, 'w', encoding='utf-8') as json_file:
        json_file.write('{"reviews":[')

        first_review = True
        for review in reviews_generator:  # Generator yields one review at a time
            if not first_review:
                json_file.write(',')
            json.dump(review.to_dict(), json_file, ensure_ascii=False)
            first_review = False

        json_file.write(']}')

    # Write CSV streaming
    first_review = next(reviews_generator, None)
    if first_review:
        fieldnames = first_review.to_dict().keys()

        with open(csv_path, 'w', newline='', encoding='utf-8') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()

            # Write first review
            writer.writerow(first_review.to_dict())

            # Write remaining reviews
            for review in reviews_generator:
                writer.writerow(review.to_dict())

    return json_path, csv_path
```

## 🐛 การแก้ไขปัญหา (Troubleshooting)

### Common Issues

**1. Permission Errors**
```python
import os
import stat

def fix_file_permissions(filepath):
    """Fix file permissions for read/write access"""
    try:
        # Add write permission for user
        os.chmod(filepath, stat.S_IWUSR | stat.S_IRUSR)
        return True
    except Exception as e:
        print(f"Failed to fix permissions for {filepath}: {e}")
        return False

# Usage
if not os.access(filepath, os.W_OK):
    fix_file_permissions(filepath)
```

**2. Long Path Names**
```python
def handle_long_paths(filepath):
    """Handle Windows long path limitations"""
    if len(filepath) > 260 and os.name == 'nt':
        # Windows extended length path prefix
        return "\\\\?\\" + os.path.abspath(filepath)
    return filepath

# Usage
long_path = "very_long_path_that_exceeds_windows_limitation..."
safe_path = handle_long_paths(long_path)
```

**3. Disk Space Issues**
```python
import shutil

def check_disk_space(path, required_space_mb=100):
    """Check if enough disk space is available"""
    try:
        total, used, free = shutil.disk_usage(path)
        free_mb = free // (1024 * 1024)

        if free_mb < required_space_mb:
            raise IOError(f"Not enough disk space. Required: {required_space_mb}MB, Available: {free_mb}MB")

        return free_mb
    except Exception as e:
        print(f"Could not check disk space: {e}")
        return None

# Usage before saving large files
available_space = check_disk_space(output_manager.base_dir, required_space_mb=500)
if available_space:
    print(f"Available space: {available_space}MB")
```

**4. File Encoding Issues**
```python
def safe_write_json(filepath, data):
    """Safely write JSON with proper encoding"""
    try:
        # Write with UTF-8 BOM for better Windows compatibility
        with open(filepath, 'w', encoding='utf-8-sig') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Failed to write JSON: {e}")
        return False

def safe_write_csv(filepath, data):
    """Safely write CSV with proper encoding"""
    try:
        with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
            if data:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
        return True
    except Exception as e:
        print(f"Failed to write CSV: {e}")
        return False
```

## 🧪 การทดสอบ (Testing)

### Unit Tests

```python
import unittest
import tempfile
import shutil
from src.utils.output_manager import OutputManager

class TestOutputManager(unittest.TestCase):

    def setUp(self):
        # Create temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()
        self.output_manager = OutputManager(base_dir=self.temp_dir)

    def tearDown(self):
        # Clean up temporary directory
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_save_reviews(self):
        """Test saving reviews"""
        reviews = [
            {"id": 1, "name": "Test Review 1"},
            {"id": 2, "name": "Test Review 2"}
        ]

        json_path, csv_path = self.output_manager.save_reviews(
            reviews=reviews,
            place_name="Test Place",
            place_id="test_id"
        )

        # Check files were created
        self.assertTrue(os.path.exists(json_path))
        self.assertTrue(os.path.exists(csv_path))

        # Check file contents
        with open(json_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
            self.assertEqual(len(json_data), 2)

        with open(csv_path, 'r', encoding='utf-8') as f:
            csv_reader = csv.DictReader(f)
            csv_rows = list(csv_reader)
            self.assertEqual(len(csv_rows), 2)

    def test_filename_generation(self):
        """Test filename generation"""
        filename = self.output_manager.generate_filename(
            place_name="Test Place",
            suffix="reviews",
            extension="json"
        )

        # Check format
        self.assertTrue(filename.startswith("Test_Place_reviews_"))
        self.assertTrue(filename.endswith(".json"))

        # Check timestamp pattern
        import re
        pattern = r"Test_Place_reviews_\d{8}_\d{6}\.json"
        self.assertRegex(filename, pattern)

    def test_file_sanitization(self):
        """Test filename sanitization"""
        problematic_name = "Place/Name:With*Special|Chars"
        clean_name = self.output_manager.sanitize_filename(problematic_name)

        # Should not contain problematic characters
        self.assertNotIn("/", clean_name)
        self.assertNotIn(":", clean_name)
        self.assertNotIn("*", clean_name)
        self.assertNotIn("|", clean_name)

if __name__ == '__main__':
    unittest.main()
```

---

## 📚 Dependencies

### Required
- Python standard library only (json, csv, os, datetime, pathlib)

### Optional
- `pandas` - For advanced data manipulation
- `xlsxwriter` - For Excel export
- `openpyxl` - For Excel file reading

---

## 📄 License

This module is part of the Google Maps RPC Scraper project and follows the same license terms.