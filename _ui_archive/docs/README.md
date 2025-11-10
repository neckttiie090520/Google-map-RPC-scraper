# Google Maps Scraper - Python Web Application

เว็บแอปพลิเคชัน Python สำหรับดึงรีวิวจาก Google Maps โดยใช้ RPC method (ไม่ต้องใช้ API Key)

## ✨ Features

- 🔍 **ค้นหาสถานที่** - ค้นหาสถานที่จาก Google Maps
- 📊 **ติดตามความคืบหน้า** - ดูความคืบหน้าการ scraping แบบ real-time
- ⚙️ **ตั้งค่าที่ยืดหยุ่น** - ปรับแต่งจำนวนรีวิว, ภาษา, ช่วงเวลา
- 💾 **บันทึกผลลัพธ์** - Export เป็น JSON และ CSV
- 🚀 **ไม่ต้องใช้ API** - ทำงานผ่าน Python โดยตรง

## 🏗️ Project Structure

```
google-maps-scraper-python/
├── app.py                              # Original Flask application
├── app-kanit.py                        # Kanit redesign Flask application
├── run.py                              # Quick start script
├── requirements.txt                    # Python dependencies
├── QUICKSTART.md                       # Quick start guide
├── README-KANIT-REDESIGN.md            # Kanit redesign documentation
│
├── src/                                # Core scraper modules
│   ├── scraper/
│   │   └── production_scraper.py       # Production scraper with anti-bot
│   ├── search/
│   │   └── rpc_place_search.py         # RPC place search
│   └── utils/
│       ├── anti_bot_utils.py           # Anti-bot protection
│       └── output_manager.py           # File output management
│
├── static/                             # Web assets
│   ├── css/
│   │   ├── google-style.css            # Original UI styles
│   │   └── kanit-redesign.css          # Modern Kanit UI styles
│   └── js/
│       ├── google-style-enhanced.js    # Original UI script
│       └── kanit-redesign.js           # Modern Kanit UI script
│
├── templates/                          # HTML templates
│   ├── index.html                      # Original web interface
│   └── kanit-redesign.html             # Modern Kanit interface
│
├── outputs/                            # Generated results
│   └── reviews/                        # Scraped review data
│
└── _unused/                            # Archive of unused development files
    ├── debug/                          # Debug scripts
    ├── tests/                          # Test files
    ├── responses/                      # Response captures
    ├── patches/                        # Development patches
    └── README.md                       # Archive documentation
```

## 🚀 Quick Start

### 1. ติดตั้ง Dependencies

```bash
pip install -r requirements.txt
```

### 2. เลือกแอปพลิเคชันที่ต้องการ

**Option A: Original Application**
```bash
python app.py
```

**Option B: Modern Kanit Redesign (Recommended)**
```bash
python app-kanit.py
```

**หรือใช้ quick start script:**
```bash
python run.py
```

### 3. เปิดเว็บเบราว์เซอร์

```
http://localhost:5000
```

### 🎨 Available Interfaces

#### 1. **Original Interface** (`app.py`)
- Functional UI with basic styling
- All scraping features available
- Tab-based navigation
- Good for development and testing

#### 2. **Kanit Redesign** (`app-kanit.py`)
- Modern Google-style UI with Kanit font
- Thai language optimized
- Enhanced user experience
- Real-time job tracking with log drawer
- Export functionality (JSON/CSV)
- **Recommended for production use**

## 📖 วิธีใช้งาน

1. **ค้นหาสถานที่**
   - พิมพ์ชื่อสถานที่ในช่องค้นหา (เช่น "Central World")
   - กด Enter หรือคลิก "ค้นหา"

2. **เลือกสถานที่**
   - คลิกที่การ์ดสถานที่ที่ต้องการ
   - ตรวจสอบข้อมูล (ชื่อ, rating, จำนวนรีวิว)

3. **ตั้งค่า (ถ้าต้องการ)**
   - คลิกปุ่ม "⚙️ ตั้งค่า"
   - ปรับแต่ง:
     - จำนวนรีวิวต่อร้าน (default: 100)
     - ช่วงเวลา (1 เดือน - ทั้งหมด)
     - ภาษา (ไทย, English, 日本語, 中文)
     - พื้นที่ (ประเทศไทย, US, Japan, China)

4. **เริ่ม Scraping**
   - คลิก "เริ่ม Scraping"
   - ระบบจะสลับไปหน้า "ความคืบหน้า" อัตโนมัติ
   - ดูความคืบหน้าแบบ real-time

5. **ดูผลลัพธ์**
   - ไฟล์จะถูกบันทึกใน `outputs/` directory
   - รูปแบบ: JSON และ CSV

## 🎯 Key Features

### 1. Direct Python Integration
- **ไม่มี API layer** - UI เรียก Python functions โดยตรง
- **Thread-based background tasks** - ใช้ threading แทน background API calls
- **In-memory task tracking** - เก็บ task state ใน memory

### 2. Real-time Progress Tracking
- **Auto-refresh** - อัปเดตความคืบหน้าทุก 2 วินาที
- **Progress bar** - แสดง % ความคืบหน้า
- **Review count** - จำนวนรีวิวที่ scrape ได้

### 3. RPC-based Search
- **No API key required** - ใช้ Google Maps internal RPC
- **Real place data** - Place ID, rating, reviews ที่ใช้งานได้จริง
- **Multi-language support** - รองรับหลายภาษา

## 🔧 Configuration

### Settings Panel

#### การตั้งค่ารีวิว
- **จำนวนรีวิวต่อร้าน**: 1 - 1000 (default: 100)
- **เวลาหยุด**: 10 - 300 วินาที (default: 60)
- **ไม่จำกัด**: เลือก checkbox เพื่อไม่จำกัดจำนวน/เวลา

#### การตั้งค่าการค้นหา
- **จำนวนร้านสูงสุดต่อการค้นหา**: 1 - 20 (default: 5)

#### ระยะเวลาการเก็บรีวิว
- 1 เดือนล่าสุด
- 6 เดือนล่าสุด
- 1 ปีล่าสุด (default)
- 5 ปีล่าสุด
- 7 ปีล่าสุด
- ทั้งหมด

#### ภาษาและพื้นที่
- **ภาษา**: th (ไทย), en (English), ja (日本語), zh (中文)
- **พื้นที่**: th, us, jp, cn

### LocalStorage
การตั้งค่าจะถูกบันทึกอัตโนมัติใน browser localStorage

## 📁 Output Files

ไฟล์ผลลัพธ์จะถูกบันทึกใน:
```
outputs/
└── YYYY-MM-DD_HH-MM-SS_TaskID/
    ├── reviews.json        # รีวิวทั้งหมด (JSON)
    ├── reviews.csv         # รีวิวทั้งหมด (CSV)
    ├── metadata.json       # Metadata การ scrape
    └── settings.json       # การตั้งค่าที่ใช้
```

## 🛠️ Development

### Project Structure

- **app.py** - Flask application หลัก, routing, task management
- **src/scraper/** - Core scraping logic (RPC-based)
- **src/search/** - Place search functionality
- **src/utils/** - Utilities (anti-bot, output management)
- **templates/** - HTML templates (Jinja2)
- **static/** - CSS, JavaScript

### Key Components

#### Flask Routes
- `GET /` - Main page
- `POST /search` - Search places
- `POST /scrape` - Start scraping task
- `GET /status/<task_id>` - Get task status
- `GET /tasks` - List all tasks
- `GET /results/<task_id>` - Get task results

#### Background Tasks
- `ScraperTask` - Task object for tracking progress
- `scrape_task_worker` - Thread worker for scraping
- `run_async` - Async function executor

#### Frontend
- Tab navigation (Search, Progress, History)
- Settings modal with localStorage persistence
- Toast notifications
- Real-time progress updates
- Place search and selection

## 🐛 Troubleshooting

### Port already in use
```bash
# Change port in app.py or run.py
app.run(port=5001)
```

### Encoding issues (Windows)
- Script จัดการ encoding อัตโนมัติผ่าน `chcp 65001`
- ถ้ายังมีปัญหา ให้ตรวจสอบว่า terminal รองรับ UTF-8

### Module import errors
```bash
# ตรวจสอบว่าอยู่ใน project root directory
# และติดตั้ง dependencies แล้ว
pip install -r requirements.txt
```

## 📝 Notes

- **In-memory storage**: Task data จะหายเมื่อ restart server
- **Single instance**: ออกแบบสำหรับ single-server deployment
- **No authentication**: เพิ่ม authentication ก่อน deploy production
- **Rate limiting**: มี anti-bot protection ใน scraper

## 🚀 Next Steps

- [ ] เพิ่ม database สำหรับ persistent storage
- [ ] เพิ่ม user authentication
- [ ] Export รูปแบบเพิ่มเติม (Excel, PDF)
- [ ] Multi-place batch scraping UI
- [ ] Advanced filtering และ sorting

## 📜 License

MIT License

## 👨‍💻 Author

Nextzus - 2025-11-10
