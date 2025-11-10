# Google Maps Scraper - Python Web Application

## 📋 Project Summary

Project folder ใหม่ที่สร้างขึ้นมา โดยใช้ **Flask + Jinja2** สำหรับ Web UI และเรียก Python scraper โดยตรง **ไม่ผ่าน API**

### สร้างเมื่อ
2025-11-10

### Technology Stack
- **Backend**: Python 3.x
- **Web Framework**: Flask 3.0
- **Template Engine**: Jinja2
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Scraper**: Async Python (aiohttp)
- **Data Format**: JSON, CSV

---

## 🏗️ Architecture

### Direct Python Integration (No API Layer)

```
Browser (UI)
    ↓
Flask Routes
    ↓
Python Functions (Direct Call)
    ↓
Scraper Modules
    ↓
Output Files
```

**Key Design Decisions:**
- ✅ ไม่มี REST API layer
- ✅ UI เรียก Python functions ผ่าน Flask routes โดยตรง
- ✅ Background tasks ใช้ threading แทน async API calls
- ✅ Task tracking ใน memory (dict)
- ✅ Real-time updates ผ่าน polling

---

## 📁 Project Structure

```
google-maps-scraper-python/
├── app.py                          # Flask web application (main)
├── run.py                          # Quick start script
├── start.bat                       # Windows startup
├── requirements.txt                # Python dependencies
├── README.md                       # Full documentation
├── QUICKSTART.md                   # Quick start guide
├── PROJECT_SUMMARY.md              # This file
├── .gitignore
│
├── src/                            # Source code
│   ├── scraper/
│   │   └── production_scraper.py   # RPC-based scraper (40+ reviews/sec)
│   ├── search/
│   │   └── simple_place_search.py  # Place search (real Place IDs)
│   └── utils/
│       ├── anti_bot_utils.py       # Anti-bot protection
│       └── output_manager.py       # File management
│
├── templates/                      # Jinja2 HTML templates
│   └── index.html                  # Main UI (single page app)
│
├── static/                         # Static assets
│   ├── css/
│   │   └── style.css               # Complete styling
│   └── js/
│       └── app.js                  # Frontend logic
│
└── outputs/                        # Generated output (gitignored)
    ├── reviews/
    ├── places/
    └── logs/
```

---

## 🎯 Key Features

### 1. Direct Python Integration
- **No API overhead** - UI calls Python directly
- **Simple architecture** - Easy to understand and modify
- **Fast development** - No need to maintain API contracts
- **Type safety** - Direct function calls

### 2. Flask Routes (Acting as API)

```python
GET  /                      # Main page
POST /search                # Search places
POST /scrape                # Start scraping
GET  /status/<task_id>      # Get task status
GET  /tasks                 # List all tasks
GET  /results/<task_id>     # Get results
```

### 3. Background Task Management

```python
class ScraperTask:
    - task_id: str
    - status: str (pending/running/completed/failed)
    - progress: int (0-100)
    - reviews: List[dict]
    - error: Optional[str]
```

- **Threading**: Background scraping in separate thread
- **In-memory storage**: `active_tasks` dict
- **Real-time updates**: Frontend polls every 2 seconds

### 4. Web UI Features

**Search Tab:**
- Place search input
- Results display as cards
- Place selection
- Start scraping button

**Progress Tab:**
- Real-time progress bars
- Review count tracking
- Status badges
- Auto-refresh every 2 seconds

**History Tab:**
- Completed tasks list
- Review counts
- Timestamps

**Settings Modal:**
- Max reviews per place
- Date range selection
- Language/region settings
- LocalStorage persistence

---

## 🚀 Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run (Windows)
start.bat

# Or run directly
python run.py
```

### Usage

1. เปิดเบราว์เซอร์: http://localhost:5000
2. ค้นหาสถานที่: "Central World"
3. เลือกสถานที่จากผลลัพธ์
4. ตั้งค่า (optional): จำนวนรีวิว, ช่วงเวลา
5. คลิก "เริ่ม Scraping"
6. ดูความคืบหน้าแบบ real-time
7. ผลลัพธ์บันทึกใน `outputs/`

---

## 🔧 Configuration

### Settings Panel

| Setting | Default | Range | Description |
|---------|---------|-------|-------------|
| Max Reviews | 100 | 1-1000 | จำนวนรีวิวต่อร้าน |
| Stop Time | 60s | 10-300s | Timeout |
| Max Places | 5 | 1-20 | จำนวนผลลัพธ์การค้นหา |
| Date Range | 1year | 1month-all | ช่วงเวลารีวิว |
| Language | th | th/en/ja/zh | ภาษา |
| Region | th | th/us/jp/cn | พื้นที่ |

### Environment Variables

None required! แอปพลิเคชันทำงานได้ทันทีโดยไม่ต้องตั้งค่าเพิ่มเติม

---

## 📊 Performance

### Scraping Performance
- **Speed**: 40+ reviews/second
- **Efficiency**: Fast mode (50-150ms delays)
- **Anti-bot**: User-Agent rotation, rate limiting
- **Reliability**: Retry logic with exponential backoff

### System Performance
- **Memory**: In-memory task storage (~1MB per task)
- **Threads**: One background thread per scraping task
- **Polling**: Frontend polls every 2 seconds
- **Scaling**: Single-server deployment

---

## 🔒 Limitations

### Current Limitations
- **No persistence**: Task data lost on server restart
- **Single instance**: Not designed for multi-server
- **No auth**: Public access (add auth for production)
- **In-memory only**: No database integration

### Future Improvements
- [ ] Add database for persistent storage
- [ ] Add user authentication
- [ ] WebSocket for real-time updates (replace polling)
- [ ] Multi-place batch scraping UI
- [ ] Advanced filtering and analytics

---

## 📝 Implementation Details

### Flask App (app.py)

**Key Components:**
```python
# Task storage
active_tasks = {}  # Dict[task_id, ScraperTask]
task_lock = threading.Lock()

# Background worker
def scrape_task_worker(task_id, place_id, settings):
    run_async(scrape_task_async(...))

# Routes
@app.route('/search', methods=['POST'])
@app.route('/scrape', methods=['POST'])
@app.route('/status/<task_id>')
```

### Frontend (app.js)

**Key Features:**
```javascript
// State management
let selectedPlace = null;
let settings = { ... };

// Real-time updates
setInterval(refreshProgress, 5000);

// Polling
async function pollTaskStatus(taskId) {
    // Poll every 2 seconds
}
```

### Scraper Integration

**Direct Function Calls:**
```python
# Search
search_service = create_enhanced_search(language, region)
places = await search_service.search_places(query, max_results)

# Scrape
scraper = create_production_scraper(language, region)
reviews = await scraper.scrape_reviews(place_id, max_reviews)
```

---

## 🧪 Testing

### Manual Testing Checklist

- [ ] Search for places
- [ ] Select a place
- [ ] Open settings modal
- [ ] Change settings and save
- [ ] Start scraping
- [ ] Monitor progress in real-time
- [ ] Verify output files generated
- [ ] Check CSV and JSON formats
- [ ] Test multiple concurrent tasks
- [ ] Restart server and verify task reset

---

## 📚 Documentation

| File | Description |
|------|-------------|
| README.md | Complete documentation |
| QUICKSTART.md | Quick start guide |
| PROJECT_SUMMARY.md | This file - architecture overview |

---

## 🎓 Learning Resources

### Understanding the Code

**Start here:**
1. `app.py` - Main Flask application
2. `templates/index.html` - UI structure
3. `static/js/app.js` - Frontend logic
4. `src/search/simple_place_search.py` - Search implementation
5. `src/scraper/production_scraper.py` - Scraping logic

### Key Concepts

- **Flask routing**: How routes map to functions
- **Threading**: Background task execution
- **Async Python**: Async/await for scraping
- **Jinja2 templates**: Server-side rendering
- **LocalStorage**: Browser-based settings storage

---

## 🆚 Comparison with Original Project

| Feature | Original (FastAPI + Next.js) | New (Flask only) |
|---------|------------------------------|------------------|
| Backend | FastAPI | Flask |
| Frontend | Next.js 14 (React) | Jinja2 + Vanilla JS |
| Communication | REST API + SSE | Direct Python calls |
| Build step | Yes (npm build) | No |
| Dependencies | Node.js + Python | Python only |
| Complexity | Medium | Low |
| Deployment | 2 servers | 1 server |

**Why choose this version:**
- ✅ Simpler architecture
- ✅ Easier to understand
- ✅ No Node.js required
- ✅ Faster development
- ✅ Perfect for learning

---

## 👨‍💻 Author

Nextzus - 2025-11-10

---

## 📜 License

MIT License

---

## 🎯 Quick Commands

```bash
# Start server
python run.py

# Install dependencies
pip install -r requirements.txt

# Test imports
python -c "from app import app; print('OK')"

# Open browser
start http://localhost:5000  # Windows
open http://localhost:5000   # Mac
```

---

**สนุกกับการ scrape Google Maps! 🗺️🚀**
