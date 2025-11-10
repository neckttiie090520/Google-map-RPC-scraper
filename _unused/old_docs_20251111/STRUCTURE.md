# 📁 Project Structure
## Google Maps RPC Scraper - Clean & Organized

**Last Updated:** 2025-11-10
**Version:** 2.0 Perfect Edition

---

## 🎯 Directory Overview

```
google-maps-scraper-python/
├── 📚 Documentation (อ่านเอกสารที่นี่)
├── 🔧 Core System (โค้ดหลัก)
├── 🧪 Testing (ทดสอบ)
├── 📦 Output (ผลลัพธ์)
└── 🗄️ Archives (ไฟล์เก่าที่ไม่ใช้)
```

---

## 📚 Documentation Files

### Essential Docs (ต้องอ่าน)

#### 1. **QUICK_START.md** ⭐ เริ่มที่นี่!
```
คู่มือเริ่มต้นใช้งานแบบ step-by-step
- วิธีเริ่ม server
- วิธีค้นหาสถานที่
- วิธี scrape reviews
- ตัวอย่างการใช้งานจริง
```

#### 2. **PERFECT_SYSTEM_DOCUMENTATION.md** 📖 ฉบับสมบูรณ์
```
เอกสารระบบทั้งหมด 105+ หน้า
- Architecture overview
- API documentation complete
- Progress & logging system
- Performance benchmarks
- Production deployment guide
```

#### 3. **CLAUDE.md** 🤖 สำหรับ AI & Developers
```
คู่มือสำหรับนักพัฒนาและ AI
- Project overview
- Code structure
- Development patterns
- Testing strategy
- Troubleshooting
```

#### 4. **README.md** 📄 Project Introduction
```
แนะนำโปรเจค
- Overview
- Features
- Quick links
```

### Additional Docs

#### 5. **CRITICAL_MISSING_FEATURES.md**
```
เปรียบเทียบกับ project 005
- Feature comparison table
- Missing features analysis
- Priority recommendations
```

---

## 🔧 Core System

### Directory Structure

```
google-maps-scraper-python/
│
├── src/                          # Core scraping engine
│   ├── scraper/
│   │   ├── __init__.py
│   │   └── production_scraper.py  # ⭐ Main scraper (1000+ lines)
│   │
│   ├── search/
│   │   ├── __init__.py
│   │   └── rpc_place_search.py    # Place search via RPC
│   │
│   └── utils/
│       ├── __init__.py
│       ├── anti_bot_utils.py      # Anti-bot protection
│       └── output_manager.py      # File organization
│
├── webapp/                       # Perfect Backend API v2
│   ├── api_v2.py                 # ⭐ Main API (750+ lines)
│   ├── test_api_v2.py            # API test suite
│   ├── app.py                    # Original Flask app (legacy)
│   ├── requirements.txt          # Web dependencies
│   ├── README.md                 # Web app docs
│   │
│   ├── templates/                # HTML templates
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── search.html
│   │   ├── tasks.html
│   │   ├── results.html
│   │   └── history.html
│   │
│   └── outputs/                  # Output from web scraping
│
├── requirements.txt              # Python dependencies
└── test_scraper.py              # Quick test script
```

---

## 🧪 Testing

### Test Files

**1. `test_scraper.py`** - Quick Scraper Test
```python
# Test production scraper directly
python test_scraper.py

# Tests:
- Scraper initialization
- Review scraping (50 reviews)
- Performance measurement
- Output validation
```

**2. `webapp/test_api_v2.py`** - API Test Suite
```python
# Comprehensive API testing
cd webapp
python test_api_v2.py

# Tests:
- API connection
- Search endpoint
- Scrape endpoint
- Task status
- SSE streaming
- Task listing
```

---

## 📦 Output Structure

```
outputs/
└── {task_id}/                    # Format: YYYYMMDD_HHMMSS_abc12345
    ├── reviews.json              # Full review data (all fields)
    ├── reviews.csv               # CSV export
    └── metadata.json             # Task metadata & stats
```

### Output Files

**reviews.json:**
```json
[
  {
    "review_id": "ChZDSUhNMG...",
    "author_name": "John Doe",
    "author_url": "https://...",
    "author_reviews_count": 156,
    "rating": 5,
    "date_formatted": "15/10/2024",
    "date_relative": "1 month ago",
    "review_text": "Excellent!",
    "review_likes": 12,
    "review_photos_count": 3,
    "owner_response": "Thank you!",
    "page_number": 1,
    "place_id": "0x30e29ec...",
    "place_name": "Restaurant"
  }
]
```

**metadata.json:**
```json
{
  "task_id": "20251110_235959_abc12345",
  "total_reviews": 500,
  "total_places": 3,
  "time_elapsed": 17.5,
  "scraping_rate": 28.57,
  "settings": {...},
  "final_progress": {...}
}
```

---

## 🗄️ Archives

### _unused/
```
_unused/
├── old_files_20251110/          # ไฟล์ที่ไม่ใช้แล้ว (2025-11-10)
│   ├── run.py                   # Old runner script
│   ├── start.bat                # Old batch file
│   ├── static/                  # Old static files
│   ├── templates/               # Old templates (moved to webapp)
│   ├── image.png                # Old screenshot
│   ├── test_output.json         # Old test output
│   ├── README-UI-DEVELOPMENT.md # Old UI dev notes
│   └── SORT_BY_NEWEST_GUIDE.md  # Old feature guide
│
├── tests/                       # Old test files
├── debug/                       # Old debug scripts
└── (other old code)
```

### _ui_archive/
```
_ui_archive/
├── original_ui/                 # Original Flask UI
│   └── app.py
└── kanit_redesign_ui/          # Redesigned UI
    └── app-kanit.py
```

---

## 🎯 Key Files Reference

### Must Know Files

| File | Purpose | Lines | Importance |
|------|---------|-------|------------|
| `webapp/api_v2.py` | Perfect Backend API | 750+ | ⭐⭐⭐⭐⭐ |
| `src/scraper/production_scraper.py` | Core Scraper | 1000+ | ⭐⭐⭐⭐⭐ |
| `QUICK_START.md` | Getting Started | - | ⭐⭐⭐⭐⭐ |
| `PERFECT_SYSTEM_DOCUMENTATION.md` | Complete Docs | 105 pages | ⭐⭐⭐⭐⭐ |
| `test_scraper.py` | Quick Test | 125 | ⭐⭐⭐⭐ |
| `webapp/test_api_v2.py` | API Tests | 450 | ⭐⭐⭐⭐ |
| `src/utils/anti_bot_utils.py` | Anti-bot | 300+ | ⭐⭐⭐⭐ |

### Documentation Priority

1. **Start Here:** `QUICK_START.md` - ใช้งานได้ใน 5 นาที
2. **Deep Dive:** `PERFECT_SYSTEM_DOCUMENTATION.md` - เข้าใจทุกอย่าง
3. **Development:** `CLAUDE.md` - สำหรับพัฒนาต่อ
4. **Comparison:** `CRITICAL_MISSING_FEATURES.md` - ดูว่าขาดอะไร

---

## 🚀 Quick Access Commands

### Start Server
```bash
cd webapp
python api_v2.py
# Server: http://localhost:5001
```

### Run Tests
```bash
# Quick scraper test
python test_scraper.py

# Full API test suite
cd webapp
python test_api_v2.py
```

### Check Structure
```bash
# List main files
ls -1

# Check core modules
ls -R src/

# Check web app
ls -R webapp/
```

---

## 📊 Statistics

### Project Size

| Category | Count | Details |
|----------|-------|---------|
| **Core Python Files** | 10 | Main functionality |
| **Test Files** | 2 | Comprehensive testing |
| **Documentation** | 5 | 150+ pages total |
| **Templates** | 6 | HTML templates |
| **Total Lines (Core)** | 3000+ | Production-ready |
| **Total Lines (Docs)** | 5000+ | Complete documentation |

### Code Distribution

```
Core Scraper (src/)          : 1500+ lines
Backend API (webapp/)        : 1000+ lines
Utils & Search               : 500+ lines
Tests                        : 600+ lines
Documentation                : 5000+ lines
─────────────────────────────────────────
Total Production Code        : 3600+ lines
Total Documentation          : 5000+ lines
```

---

## 🎨 Clean Structure Benefits

### ✅ What We Achieved

1. **Clear Separation**
   - Core engine in `src/`
   - Web API in `webapp/`
   - Documentation at root
   - Archives in `_unused/`

2. **Easy Navigation**
   - Everything has its place
   - No duplicate files
   - Clear naming
   - Logical organization

3. **Production Ready**
   - Only active code
   - Complete documentation
   - Tested and validated
   - Ready to deploy

4. **Maintainable**
   - Easy to find files
   - Easy to update
   - Easy to extend
   - Easy to understand

### 🗑️ What We Archived

- ❌ Old UI files (moved to `_ui_archive/`)
- ❌ Unused test files (moved to `_unused/tests/`)
- ❌ Debug scripts (moved to `_unused/debug/`)
- ❌ Old runner scripts (`run.py`, `start.bat`)
- ❌ Legacy templates and static files
- ❌ Old documentation files

---

## 🔄 Migration Notes

### From Old Structure (Before 2025-11-10)

**Deprecated Files:**
- `run.py` → Use `python webapp/api_v2.py` instead
- `start.bat` → Use command line directly
- `static/` & `templates/` (root) → Moved to `webapp/`
- Old test outputs → Cleared

**New Files:**
- `webapp/api_v2.py` - Perfect Backend API
- `PERFECT_SYSTEM_DOCUMENTATION.md` - Complete docs
- `QUICK_START.md` - Getting started guide
- `STRUCTURE.md` - This file

---

## 📝 Maintenance

### Adding New Files

**Core Code:**
```
src/
└── new_module/
    ├── __init__.py
    └── new_feature.py
```

**Tests:**
```
Add to test_scraper.py or webapp/test_api_v2.py
```

**Documentation:**
```
Add .md file at root level
Update this STRUCTURE.md
```

### Cleaning Up

**Unused files should go to:**
```
_unused/old_files_YYYYMMDD/
```

**Archive old versions:**
```
_unused/versions/vX.X/
```

---

## 🎯 Summary

### Current Structure: Perfect ✅

```
📁 google-maps-scraper-python/
│
├── 📚 5 Essential Docs        # Complete documentation
├── 🔧 src/ & webapp/          # Clean, organized code
├── 🧪 2 Test files            # Comprehensive testing
├── 📦 outputs/                # Organized results
└── 🗄️ _unused/ & _ui_archive/ # Archived files
```

### Status: Production Ready 🚀

- ✅ Clean structure
- ✅ Complete documentation
- ✅ Tested and validated
- ✅ Ready to use
- ✅ Easy to maintain

---

**Document Version:** 1.0
**Last Updated:** 2025-11-10
**Status:** ✅ Clean & Organized

