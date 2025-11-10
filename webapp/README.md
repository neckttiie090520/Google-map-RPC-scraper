# Google Maps Scraper - Web Application

Modern, user-friendly web interface for Google Maps review scraping.

## 🎨 Features

- **Google Material Design** - Clean, professional interface
- **Thai Font (Kanit)** - Beautiful Thai language support
- **Real-time Progress** - Live updates with SSE (Server-Sent Events)
- **Multi-place Scraping** - Select and scrape multiple places at once
- **Export Options** - Download results as CSV or JSON
- **Settings Management** - Customizable default preferences
- **History Tracking** - View and manage past scraping tasks

## 🚀 User Flow

1. **Search** - Search for places with customizable filters
2. **Pick** - Select multiple places from search results
3. **Configure** - Set scraping parameters (reviews count, date range, language)
4. **Scrape** - Monitor real-time progress with detailed logs
5. **View Results** - Browse, filter, and export scraped reviews
6. **History** - Track and manage all past tasks

## 📦 Installation

### Prerequisites
- Python 3.8+
- All core scraper dependencies (from parent directory)

### Setup

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Run the application:**
```bash
python app.py
```

3. **Open in browser:**
```
http://localhost:5000
```

## 📱 Pages

### Home (`/`)
- Hero section with call-to-action
- Live statistics dashboard
- Feature highlights
- How-to-use guide

### Search (`/search`)
- Place search with customizable filters
- Multi-selection interface
- Real-time search results
- Settings modal for scraping configuration

### Tasks (`/tasks`)
- Monitor active scraping tasks
- Real-time progress bars and logs
- Task detail modal with full logs
- SSE streaming for live updates

### Results (`/results/:task_id`)
- Table view of scraped reviews
- Advanced filtering and search
- Export to CSV/JSON
- Pagination and sorting

### History (`/history`)
- List of all past tasks
- Filter by date, status, or search
- Quick actions (view, download)
- Task details modal

### Settings (`/settings`)
- Default scraping preferences
- Search configuration
- Export/Import settings
- Advanced options

## ⚙️ API Endpoints

### Search
- `POST /api/search` - Search for places

### Scraping
- `POST /api/scrape` - Start scraping task
- `GET /api/tasks/<id>/status` - Get task status
- `GET /api/tasks/<id>/stream` - SSE progress stream
- `GET /api/tasks` - Get all active tasks

### Results
- `GET /api/results/<id>` - Get task results
- `GET /api/results/<id>/download/csv` - Download CSV
- `GET /api/results/<id>/download/json` - Download JSON

### History
- `GET /api/history` - Get task history

## 🎨 UI Components

### Design System
- **Colors:** Google Material Design palette
- **Typography:** Kanit font (Thai/English support)
- **Icons:** Material Icons
- **Framework:** Tailwind CSS

### Features
- **Alert System:** Toast notifications
- **Loading States:** Overlay spinners
- **Modals:** Task details, settings
- **Pagination:** Smooth navigation
- **Real-time Updates:** SSE streaming
- **Responsive Design:** Desktop-optimized

## 🔧 Configuration

### Environment Variables
No additional configuration required. The app uses:

- **Backend URL:** Automatically detected
- **Output Directory:** `../outputs/`
- **Settings Storage:** Browser localStorage

### Default Settings
- Max search results: 10 places
- Max reviews per place: 100 reviews
- Date range: 1 year
- Language: Thai (TH)
- Region: Thailand (TH)

## 📊 File Structure

```
webapp/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── templates/            # HTML templates
│   ├── base.html        # Base template with navbar
│   ├── index.html       # Home page
│   ├── search.html      # Search & selection
│   ├── tasks.html       # Task monitoring
│   ├── results.html     # Results viewing
│   ├── history.html     # Task history
│   └── settings.html    # Settings page
└── static/              # Static assets (if needed)
    ├── css/
    └── js/
```

## 🚀 Development

### Local Development
```bash
cd webapp
python app.py
# Opens at http://localhost:5000
```

### Debug Mode
The app runs with `debug=True` by default for development. Disable in production.

### File Outputs
All scraped data is saved to:
```
../outputs/
└── YYYY-MM-DD_HH-MM-SS_TaskID/
    ├── reviews.json     # Full review data
    ├── reviews.csv      # CSV export
    ├── metadata.json    # Task metadata
    └── settings.json    # Scraper settings
```

## 🐛 Troubleshooting

### Common Issues

1. **Port already in use:**
   ```bash
   # Kill processes on port 5000
   # or change port in app.py
   app.run(port=5001)
   ```

2. **Dependencies not found:**
   ```bash
   # Make sure you're in the correct directory
   cd webapp
   pip install -r requirements.txt
   ```

3. **Backend not responding:**
   - Check if core scraper modules are available
   - Verify Python path includes parent directory
   - Check browser console for errors

### Logs
The app displays detailed Python-style logs in:
- Tasks page (real-time)
- Browser console
- Flask server output

## 📱 Browser Support

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

**Note:** Desktop-optimized experience. Mobile support is basic.

## 🔄 Updates

### Updating from Previous Version
1. Backup your `outputs/` directory
2. Replace all files except `outputs/`
3. Install new dependencies
4. Run `python app.py`

### Version History
- **v1.0** - Initial release with complete UI/UX
  - Search, Pick, Scrape, Results, History, Settings
  - Real-time updates with SSE
  - Thai language support
  - Export functionality

## 📞 Support

For issues and questions:
1. Check browser console for errors
2. Verify all dependencies are installed
3. Ensure backend modules are accessible
4. Check file permissions for `outputs/` directory

## 📄 License

Same as parent project.

---

**Built with ❤️ using Flask + Tailwind CSS**
**Font:** Kanit (Thai language support)
**Design:** Google Material Design