# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2025-11-11

### 🎉 Initial Release

First production-ready release of Google Maps RPC Scraper.

### ✨ Added

#### Core Scraping Features
- **Production Scraper Engine** - High-performance RPC-based scraping (26-40+ reviews/sec)
- **Page Token Pagination** - Zero-duplicate review extraction
- **100% Field Extraction** - All 12 review fields captured
- **3-Tier Date Parsing** - Robust date extraction with fallback strategies
- **Date Range Filtering** - Smart cutoff detection (1month, 6months, 1year, 5years, 7years, all, custom)
- **Multi-Language Support** - Thai, English, Japanese, Chinese
- **Sort by Newest** - In-memory sorting after extraction
- **Progress Callbacks** - Real-time progress tracking during scraping

#### Anti-Bot Protection
- **User-Agent Rotation** - 12+ realistic browser signatures
- **Header Randomization** - Unique request fingerprint per call
- **Rate Limiting Detection** - 60-second rolling window with auto-slowdown
- **Exponential Backoff** - Intelligent retry logic (429: 5s→10s→20s, 5xx: 2s→4s→8s, Timeout: 1s→2s→4s)
- **Proxy Support** - HTTP/SOCKS5 rotation (optional)
- **Human-Like Delays** - Fast mode (50-150ms) and Human mode (500-1500ms)

#### Web Application
- **Flask Web Server** - Modern web interface with SSE streaming
- **Real-Time Progress** - Server-Sent Events for live updates
- **RPC Place Search** - Find places without API key
- **Task Management** - Track multiple concurrent scraping tasks
- **Progress Bars** - Visual feedback with reviews/max and percentage
- **Unlimited Mode** - Auto-detect total_reviews from place data
- **Multi-Format Export** - Download as JSON or CSV
- **Thai/English UI** - Full UTF-8 Unicode support
- **Results Viewer** - Browse and filter scraped reviews
- **Organized Output** - Timestamped directory structure

#### Search Functionality
- **RPC Place Search** - Search places without Google API key
- **Autocomplete Support** - Search suggestions (framework ready)
- **Place Data Extraction** - place_id, name, address, rating, total_reviews, category, coordinates

#### Utilities
- **Output Manager** - Organized file structure (outputs/YYYY-MM-DD/)
- **Unicode Display** - Safe Thai character printing on Windows
- **UTF-8 Encoding Fix** - Automatic chcp 65001 on Windows
- **Anti-Bot Utilities** - Comprehensive detection avoidance toolkit

#### Documentation
- **README.md** - Complete user documentation (560+ lines)
- **CLAUDE.md** - Comprehensive developer documentation (1000+ lines)
- **CONTRIBUTING.md** - Contribution guidelines
- **PROJECT_SUMMARY.md** - Executive summary and architecture
- **CHANGELOG.md** - This file
- **LICENSE** - MIT License
- **.env.example** - Configuration template
- **Inline Documentation** - Docstrings and comments throughout

#### Configuration
- **Environment Variables** - .env file support
- **Factory Functions** - `create_production_scraper()`, `create_rpc_search()`
- **ScraperConfig Dataclass** - Type-safe configuration
- **Flexible Settings** - Language, region, date range, max reviews, performance tuning

#### Testing
- **test_scraper.py** - Quick verification script
- **Example Place IDs** - Central World Bangkok, test cases
- **Manual Testing** - Comprehensive testing checklist

### 🔧 Changed
- N/A (initial release)

### 🐛 Fixed
- N/A (initial release)

### 🗑️ Removed
- N/A (initial release)

### 📊 Performance
- **26-40+ reviews/sec** in fast mode (vs. 4-5 reviews/sec in initial browser-based version)
- **Zero duplicates** achieved through page token pagination
- **3-4x speed improvement** from fast mode vs. human mode
- **7.5x improvement** from initial development to production

### 🔒 Security
- No hardcoded credentials
- Environment variable configuration
- Input validation and sanitization
- .gitignore prevents sensitive data commits
- Safe file path handling

### 📝 Notes
- **Windows UTF-8**: Automatic encoding fix for Thai characters
- **Rate Limiting**: Built-in protection with auto-slowdown
- **Google ToS**: Users responsible for compliance
- **Educational Purpose**: Designed for research and learning

---

## [Unreleased]

### 🚀 Planned Features

#### Performance Enhancements
- Concurrent request processing (target: 50+ reviews/sec)
- Connection pooling optimization
- Response caching
- Batch scraping optimization

#### New Features
- CAPTCHA solving integration (CapSolver)
- Photo downloading
- Review sentiment analysis (Thai/English)
- Email notifications
- Scheduled scraping (cron jobs)
- Export to Excel format

#### Infrastructure
- Docker containerization
- Redis-based task queue
- RESTful API mode
- Elasticsearch integration
- Real-time monitoring dashboard

#### UI/UX
- Dark mode support
- Mobile-responsive improvements
- Real-time charts and visualizations
- Batch export functionality
- Advanced filtering options

#### Stealth Features
- Advanced fingerprinting (Canvas/WebGL)
- Residential proxy integration
- Browser automation fallback (Playwright)
- CAPTCHA auto-detection

---

## Development History

### Phase 1: Research & Prototyping (2025-11-10 14:00-15:30)
- Researched Google Maps RPC API
- Built browser-based scraper (4-5 reviews/sec)
- Migrated to HTTP-only RPC (23 reviews/sec)
- Added anti-bot protection (37.83 reviews/sec)
- Implemented date parsing and pagination

### Phase 2: Framework Integration (2025-11-10 20:00-23:00)
- Created modular src/ structure
- Integrated production features
- Built Flask web application
- Added SSE progress tracking

### Phase 3: Web UI Enhancement (2025-11-11 00:00-03:00)
- Designed Tailwind CSS interface
- Implemented RPC place search
- Added task management
- Created results viewer

### Phase 4: Feature Completion (2025-11-11 03:00-05:00)
- Added unlimited mode
- Enhanced progress bars
- Fixed UTF-8 encoding
- Optimized performance to 26-30 reviews/sec

### Phase 5: Production Preparation (2025-11-11 05:00)
- Cleaned up project structure
- Moved 30+ test files to _unused/
- Created comprehensive documentation
- Prepared for GitHub release

---

## Version History

### Version Numbering
- **Major.Minor.Patch** (Semantic Versioning)
- **Major**: Breaking changes
- **Minor**: New features (backward compatible)
- **Patch**: Bug fixes (backward compatible)

### Release Schedule
- **Major releases**: When significant features are complete
- **Minor releases**: Monthly feature additions
- **Patch releases**: As needed for bug fixes

---

## Migration Guides

### Upgrading to 1.0.0
This is the initial release. No migration required.

---

## Known Issues

### Current Limitations
1. **Review Pagination**: Google limits to ~1000-2000 reviews per place
2. **No Persistence**: Task data lost on server restart (by design)
3. **Single-Server**: No distributed task queue yet
4. **No Authentication**: API is public (add for production deployment)
5. **Windows Encoding**: Requires UTF-8 console setup for Thai characters

### Workarounds
1. Use date range filtering to reduce total reviews
2. Implement external database for persistence (if needed)
3. Use Redis for distributed tasks (planned feature)
4. Add authentication middleware for production
5. Automatic encoding fix included in code

---

## Deprecation Notices

No deprecations in initial release.

---

## Contributors

### Core Team
- **Nextzus** - Project creator and lead developer

### Special Thanks
- Claude AI (Anthropic) - Development assistance
- Open source community - Libraries and inspiration

---

## Links

- **Repository**: https://github.com/yourusername/google-maps-rpc-scraper
- **Issues**: https://github.com/yourusername/google-maps-rpc-scraper/issues
- **Discussions**: https://github.com/yourusername/google-maps-rpc-scraper/discussions
- **Documentation**: See README.md and CLAUDE.md

---

**[1.0.0]**: https://github.com/yourusername/google-maps-rpc-scraper/releases/tag/v1.0.0
