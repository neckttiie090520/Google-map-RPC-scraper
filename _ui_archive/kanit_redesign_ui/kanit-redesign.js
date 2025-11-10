/*
 * Google Maps Scraper - Kanit Redesign JavaScript
 * Enhanced UI with search autocomplete, job management, export functionality
 */

class GoogleMapsScraperApp {
  constructor() {
    this.jobs = new Map();
    this.mockMode = false;
    this.selectedJobs = new Set();
    this.currentSearchTerm = '';
    this.selectedSuggestionIndex = -1;
    this.suggestions = [];

    this.init();
  }

  init() {
    this.bindEvents();
    this.loadJobsFromStorage();
    this.renderJobs();
    this.checkBackendAvailability();
  }

  bindEvents() {
    // Search functionality
    const searchInput = document.getElementById('searchInput');
    const searchBtn = document.getElementById('searchBtn');

    if (searchInput) {
      searchInput.addEventListener('input', (e) => this.handleSearchInput(e));
      searchInput.addEventListener('keydown', (e) => this.handleSearchKeydown(e));
      searchInput.addEventListener('focus', () => this.showSuggestions());
      searchInput.addEventListener('blur', () => {
        setTimeout(() => this.hideSuggestions(), 200);
      });
    }

    if (searchBtn) {
      searchBtn.addEventListener('click', () => this.handleSearch());
    }

    // Settings modal
    const settingsBtn = document.getElementById('settingsBtn');
    const modalOverlay = document.getElementById('settingsModal');
    const modalClose = document.getElementById('modalClose');
    const saveBtn = document.getElementById('saveSettings');
    const cancelBtn = document.getElementById('cancelSettings');

    if (settingsBtn) {
      settingsBtn.addEventListener('click', () => this.openSettings());
    }

    if (modalClose) {
      modalClose.addEventListener('click', () => this.closeSettings());
    }

    if (cancelBtn) {
      cancelBtn.addEventListener('click', () => this.closeSettings());
    }

    if (saveBtn) {
      saveBtn.addEventListener('click', () => this.saveSettings());
    }

    if (modalOverlay) {
      modalOverlay.addEventListener('click', (e) => {
        if (e.target === modalOverlay) {
          this.closeSettings();
        }
      });
    }

    // Export functionality
    const exportBtn = document.getElementById('exportBtn');
    const exportMenu = document.getElementById('exportMenu');

    if (exportBtn) {
      exportBtn.addEventListener('click', () => this.toggleExportMenu());
    }

    document.addEventListener('click', (e) => {
      if (!e.target.closest('.export-dropdown')) {
        this.closeExportMenu();
      }
    });

    // Log drawer
    document.addEventListener('click', (e) => {
      if (e.target.closest('.btn-logs')) {
        const jobId = e.target.closest('.btn-logs').dataset.jobId;
        this.openLogDrawer(jobId);
      }
    });

    const logDrawerClose = document.getElementById('logDrawerClose');
    if (logDrawerClose) {
      logDrawerClose.addEventListener('click', () => this.closeLogDrawer());
    }

    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        searchInput?.focus();
      }
    });

    // Clear selection when clicking outside
    document.addEventListener('click', (e) => {
      if (!e.target.closest('.job-card')) {
        this.clearSelection();
      }
    });
  }

  async checkBackendAvailability() {
    try {
      const response = await fetch('/tasks');
      if (response.ok) {
        this.mockMode = false;
        console.log('Backend available');
      } else {
        this.mockMode = true;
        console.log('Backend not available, using mock mode');
      }
    } catch (error) {
      this.mockMode = true;
      console.log('Backend not available, using mock mode');
    }
  }

  handleSearchInput(e) {
    this.currentSearchTerm = e.target.value;
    this.selectedSuggestionIndex = -1;

    if (this.currentSearchTerm.length > 2) {
      this.fetchSuggestions(this.currentSearchTerm);
    } else {
      this.hideSuggestions();
    }
  }

  handleSearchKeydown(e) {
    const suggestions = document.querySelectorAll('.suggestion-item');

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        this.selectedSuggestionIndex = Math.min(this.selectedSuggestionIndex + 1, suggestions.length - 1);
        this.updateSuggestionSelection();
        break;
      case 'ArrowUp':
        e.preventDefault();
        this.selectedSuggestionIndex = Math.max(this.selectedSuggestionIndex - 1, -1);
        this.updateSuggestionSelection();
        break;
      case 'Enter':
        e.preventDefault();
        if (this.selectedSuggestionIndex >= 0 && suggestions[this.selectedSuggestionIndex]) {
          suggestions[this.selectedSuggestionIndex].click();
        } else {
          this.handleSearch();
        }
        break;
      case 'Escape':
        this.hideSuggestions();
        break;
    }
  }

  updateSuggestionSelection() {
    const suggestions = document.querySelectorAll('.suggestion-item');
    suggestions.forEach((item, index) => {
      if (index === this.selectedSuggestionIndex) {
        item.classList.add('selected');
        item.scrollIntoView({ block: 'nearest' });
      } else {
        item.classList.remove('selected');
      }
    });
  }

  async fetchSuggestions(query) {
    if (this.mockMode) {
      // Mock suggestions
      this.suggestions = [
        { name: 'Central World Bangkok', address: '999/9 Rama I Rd, Pathum Wan', place_id: 'central_world' },
        { name: 'Siam Paragon', address: '991 Rama I Rd, Pathum Wan', place_id: 'siam_paragon' },
        { name: 'Terminal 21 Asok', address: '88 Sukhumvit Rd, Khlong Toei', place_id: 'terminal21' },
        { name: 'EmQuartier', address: '693 Sukhumvit Rd, Khlong Toei', place_id: 'emquartier' },
        { name: 'ICONSIAM', address: '299 Charoen Nakhon Rd, Khlong San', place_id: 'iconsiam' }
      ].filter(place =>
        place.name.toLowerCase().includes(query.toLowerCase()) ||
        place.address.toLowerCase().includes(query.toLowerCase())
      );
    } else {
      try {
        const response = await fetch('/search', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ query, max_results: 5 })
        });
        const data = await response.json();
        this.suggestions = data.success ? data.places : [];
      } catch (error) {
        console.error('Search error:', error);
        this.suggestions = [];
      }
    }

    this.displaySuggestions();
  }

  displaySuggestions() {
    const suggestionsContainer = document.getElementById('searchSuggestions');
    if (!suggestionsContainer) return;

    if (this.suggestions.length === 0) {
      suggestionsContainer.innerHTML = `
        <div class="suggestion-item">
          <div class="suggestion-name">No results found</div>
          <div class="suggestion-address">Try a different search term</div>
        </div>
      `;
    } else {
      suggestionsContainer.innerHTML = this.suggestions.map(place => `
        <div class="suggestion-item" data-place='${JSON.stringify(place).replace(/'/g, '&apos;')}'>
          <div class="suggestion-name">${this.escapeHtml(place.name)}</div>
          <div class="suggestion-address">${this.escapeHtml(place.address)}</div>
        </div>
      `).join('');

      // Add click handlers
      suggestionsContainer.querySelectorAll('.suggestion-item').forEach(item => {
        item.addEventListener('click', () => {
          const place = JSON.parse(item.dataset.place);
          this.selectPlace(place);
        });
      });
    }

    this.showSuggestions();
  }

  selectPlace(place) {
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
      searchInput.value = place.name;
    }
    this.hideSuggestions();
    this.showToast(`Selected: ${place.name}`, 'info');
  }

  showSuggestions() {
    const suggestionsContainer = document.getElementById('searchSuggestions');
    if (suggestionsContainer) {
      suggestionsContainer.classList.add('active');
    }
  }

  hideSuggestions() {
    const suggestionsContainer = document.getElementById('searchSuggestions');
    if (suggestionsContainer) {
      suggestionsContainer.classList.remove('active');
    }
  }

  async handleSearch() {
    const searchInput = document.getElementById('searchInput');
    const searchBtn = document.getElementById('searchBtn');
    const query = searchInput?.value?.trim();

    if (!query) {
      this.showToast('Please enter a search term', 'error');
      return;
    }

    if (searchBtn) {
      searchBtn.disabled = true;
      searchBtn.innerHTML = '<span class="loading"></span> Searching...';
    }

    this.hideSuggestions();

    // Find the selected place from suggestions
    const selectedPlace = this.suggestions.find(p => p.name === query) || {
      name: query,
      address: 'Custom search location',
      place_id: `custom_${Date.now()}`
    };

    try {
      if (this.mockMode) {
        await this.startMockJob(selectedPlace);
      } else {
        await this.startRealJob(selectedPlace);
      }
    } catch (error) {
      console.error('Search error:', error);
      this.showToast('Failed to start job', 'error');
    } finally {
      if (searchBtn) {
        searchBtn.disabled = false;
        searchBtn.textContent = 'Search';
      }
    }
  }

  async startRealJob(place) {
    const response = await fetch('/scrape', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        place_id: place.place_id,
        place_name: place.name,
        settings: this.getSettings()
      })
    });

    const data = await response.json();
    if (data.success) {
      this.createJob(data.task_id, place.name, 'pending');
      this.showToast('Job started successfully', 'success');
      this.startJobMonitoring(data.task_id);
    } else {
      this.showToast('Failed to start job: ' + data.error, 'error');
    }
  }

  async startMockJob(place) {
    const jobId = `job_${Date.now()}`;
    this.createJob(jobId, place.name, 'pending');
    this.showToast('Mock job started', 'info');

    // Simulate job progression
    setTimeout(() => this.updateJobStatus(jobId, 'running'), 1000);

    const totalSteps = 10;
    for (let i = 1; i <= totalSteps; i++) {
      setTimeout(() => {
        const progress = (i / totalSteps) * 100;
        this.updateJobProgress(jobId, progress, `Processing step ${i} of ${totalSteps}`);
        this.addJobLog(jobId, 'info', `Step ${i}: ${this.getRandomLogMessage(i)}`);

        if (i === totalSteps) {
          setTimeout(() => {
            this.updateJobStatus(jobId, 'completed');
            this.addJobLog(jobId, 'success', 'Job completed successfully');
            this.generateMockResults(jobId);
          }, 500);
        }
      }, i * 2000);
    }
  }

  getRandomLogMessage(step) {
    const messages = [
      'Fetching place details...',
      'Searching for reviews...',
      'Parsing review data...',
      'Processing rating information...',
      'Extracting user data...',
      'Analyzing review sentiment...',
      'Compiling results...',
      'Formatting output...',
      'Validating data...',
      'Finalizing results...'
    ];
    return messages[Math.min(step - 1, messages.length - 1)];
  }

  generateMockResults(jobId) {
    const job = this.jobs.get(jobId);
    if (!job) return;

    const mockResults = {
      place_id: job.placeId,
      place_name: job.title,
      total_reviews: Math.floor(Math.random() * 1000) + 100,
      average_rating: (Math.random() * 2 + 3).toFixed(1),
      reviews: Array.from({ length: 20 }, (_, i) => ({
        author: `User ${i + 1}`,
        rating: Math.floor(Math.random() * 3) + 3,
        text: `This is review number ${i + 1}. The place was ${['great', 'good', 'okay', 'bad'][Math.floor(Math.random() * 4)]}.`,
        date: new Date(Date.now() - Math.random() * 365 * 24 * 60 * 60 * 1000).toISOString(),
        helpful: Math.floor(Math.random() * 50)
      }))
    };

    job.results = mockResults;
    this.saveJobsToStorage();
  }

  createJob(jobId, title, status) {
    const job = {
      id: jobId,
      title: title,
      status: status,
      progress: 0,
      message: 'Initializing...',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      logs: [{ timestamp: new Date().toISOString(), level: 'info', message: 'Job created' }]
    };

    this.jobs.set(jobId, job);
    this.saveJobsToStorage();
    this.renderJobs();
  }

  updateJobStatus(jobId, status) {
    const job = this.jobs.get(jobId);
    if (job) {
      job.status = status;
      job.updatedAt = new Date().toISOString();

      if (status === 'completed') {
        job.progress = 100;
        job.message = 'Completed successfully';
      } else if (status === 'failed') {
        job.message = 'Job failed';
        this.addJobLog(jobId, 'error', 'Job encountered an error');
      } else if (status === 'running') {
        job.message = 'Processing...';
        this.addJobLog(jobId, 'info', 'Job started processing');
      }

      this.saveJobsToStorage();
      this.renderJobs();
    }
  }

  updateJobProgress(jobId, progress, message) {
    const job = this.jobs.get(jobId);
    if (job) {
      job.progress = Math.round(progress);
      job.message = message;
      job.updatedAt = new Date().toISOString();
      this.saveJobsToStorage();
      this.renderJobs();
    }
  }

  addJobLog(jobId, level, message) {
    const job = this.jobs.get(jobId);
    if (job) {
      job.logs.push({
        timestamp: new Date().toISOString(),
        level: level,
        message: message
      });
      this.saveJobsToStorage();

      if (this.currentLogJob === jobId) {
        this.renderLogs(jobId);
      }
    }
  }

  async startJobMonitoring(jobId) {
    const checkStatus = async () => {
      try {
        const response = await fetch(`/status/${jobId}`);
        const data = await response.json();

        if (data.success) {
          this.updateJobProgress(jobId, data.progress || 0, data.message || 'Processing...');

          if (data.status === 'completed' || data.status === 'failed') {
            this.updateJobStatus(jobId, data.status);
          } else {
            setTimeout(checkStatus, 2000);
          }
        }
      } catch (error) {
        console.error('Status check error:', error);
        setTimeout(checkStatus, 5000);
      }
    };

    setTimeout(checkStatus, 1000);
  }

  renderJobs() {
    const container = document.getElementById('jobsContainer');
    if (!container) return;

    const jobsArray = Array.from(this.jobs.values()).sort((a, b) =>
      new Date(b.createdAt) - new Date(a.createdAt)
    );

    if (jobsArray.length === 0) {
      container.innerHTML = `
        <div class="empty-state">
          <div class="empty-state-icon">📋</div>
          <div class="empty-state-title">No jobs yet</div>
          <div class="empty-state-description">Start by searching for a place and scraping reviews</div>
        </div>
      `;
      return;
    }

    container.innerHTML = jobsArray.map(job => `
      <div class="job-card ${this.selectedJobs.has(job.id) ? 'selected' : ''}" data-job-id="${job.id}">
        <div class="job-card-header">
          <div>
            <div class="job-title">${this.escapeHtml(job.title)}</div>
            <div class="job-meta">
              <span>Created: ${this.formatDate(job.createdAt)}</span>
              <span>ID: ${job.id.substring(0, 8)}...</span>
            </div>
          </div>
          <span class="job-status status-${job.status}">${job.status}</span>
        </div>

        ${job.status === 'running' || job.status === 'completed' ? `
          <div class="job-progress">
            <div class="progress-bar">
              <div class="progress-fill" style="width: ${job.progress}%"></div>
            </div>
            <div class="progress-text">
              <span>${job.progress}%</span>
              <span>${this.escapeHtml(job.message)}</span>
            </div>
          </div>
        ` : ''}

        <div class="job-actions">
          <button class="btn-icon btn-logs" data-job-id="${job.id}" title="View logs">
            📋
          </button>
          ${job.status === 'completed' ? `
            <button class="btn-icon btn-export" data-job-id="${job.id}" title="Export results">
              📥
            </button>
          ` : ''}
          <button class="btn-icon btn-select" data-job-id="${job.id}" title="Select job">
            ${this.selectedJobs.has(job.id) ? '✓' : '○'}
          </button>
        </div>
      </div>
    `).join('');

    // Re-bind event listeners
    container.querySelectorAll('.btn-logs').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        this.openLogDrawer(btn.dataset.jobId);
      });
    });

    container.querySelectorAll('.btn-export').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        this.exportJob(btn.dataset.jobId);
      });
    });

    container.querySelectorAll('.btn-select').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        this.toggleJobSelection(btn.dataset.jobId);
      });
    });

    container.querySelectorAll('.job-card').forEach(card => {
      card.addEventListener('click', () => {
        this.selectJobCard(card.dataset.jobId);
      });
    });
  }

  selectJobCard(jobId) {
    this.clearSelection();
    this.selectedJobs.add(jobId);
    this.renderJobs();
  }

  toggleJobSelection(jobId) {
    if (this.selectedJobs.has(jobId)) {
      this.selectedJobs.delete(jobId);
    } else {
      this.selectedJobs.add(jobId);
    }
    this.renderJobs();
  }

  clearSelection() {
    this.selectedJobs.clear();
    this.renderJobs();
  }

  openLogDrawer(jobId) {
    const drawer = document.getElementById('logDrawer');
    const content = document.getElementById('content');

    if (drawer && content) {
      content.classList.add('drawer-open');
      drawer.classList.add('open');
      this.currentLogJob = jobId;
      this.renderLogs(jobId);
    }
  }

  closeLogDrawer() {
    const drawer = document.getElementById('logDrawer');
    const content = document.getElementById('content');

    if (drawer && content) {
      drawer.classList.remove('open');
      content.classList.remove('drawer-open');
      this.currentLogJob = null;
    }
  }

  renderLogs(jobId) {
    const logContent = document.getElementById('logContent');
    const job = this.jobs.get(jobId);

    if (!logContent || !job) return;

    logContent.innerHTML = job.logs.map(log => `
      <div class="log-entry ${log.level}">
        <span class="log-timestamp">${this.formatTime(log.timestamp)}</span>
        <span class="log-message">${this.escapeHtml(log.message)}</span>
      </div>
    `).join('');

    logContent.scrollTop = logContent.scrollHeight;
  }

  toggleExportMenu() {
    const menu = document.getElementById('exportMenu');
    if (menu) {
      menu.classList.toggle('active');
    }
  }

  closeExportMenu() {
    const menu = document.getElementById('exportMenu');
    if (menu) {
      menu.classList.remove('active');
    }
  }

  exportJob(jobId) {
    const job = this.jobs.get(jobId);
    if (!job || !job.results) {
      this.showToast('No results available for this job', 'error');
      return;
    }

    this.exportResults([job.results], `${job.title.replace(/[^a-z0-9]/gi, '_')}_results`);
  }

  exportSelectedJobs() {
    const selectedJobsArray = Array.from(this.selectedJobs).map(jobId => this.jobs.get(jobId)).filter(job => job && job.results);

    if (selectedJobsArray.length === 0) {
      this.showToast('No selected jobs with results', 'error');
      return;
    }

    this.exportResults(selectedJobsArray.map(job => job.results), `selected_jobs_results`);
  }

  exportAllJobs() {
    const jobsWithResults = Array.from(this.jobs.values()).filter(job => job.results);

    if (jobsWithResults.length === 0) {
      this.showToast('No jobs with results available', 'error');
      return;
    }

    this.exportResults(jobsWithResults.map(job => job.results), `all_jobs_results`);
  }

  exportResults(results, filename) {
    // Export JSON
    this.downloadJSON(results, `${filename}.json`);

    // Export CSV
    this.downloadCSV(results, `${filename}.csv`);

    this.showToast(`Exported ${results.length} job(s) results`, 'success');
  }

  downloadJSON(data, filename) {
    const json = JSON.stringify(data, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    this.downloadBlob(blob, filename);
  }

  downloadCSV(results, filename) {
    let csv = 'Place Name,Total Reviews,Average Rating,Author,Rating,Review Text,Date,Helpful Count\n';

    results.forEach(result => {
      if (result.reviews) {
        result.reviews.forEach(review => {
          csv += `"${this.escapeCsv(result.place_name)}",${result.total_reviews},${result.average_rating},"${this.escapeCsv(review.author)}",${review.rating},"${this.escapeCsv(review.text)}","${review.date}",${review.helpful}\n`;
        });
      }
    });

    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    this.downloadBlob(blob, filename);
  }

  downloadBlob(blob, filename) {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  escapeCsv(text) {
    return text ? text.toString().replace(/"/g, '""') : '';
  }

  openSettings() {
    const modal = document.getElementById('settingsModal');
    if (modal) {
      modal.classList.add('active');
      this.loadSettings();
    }
  }

  closeSettings() {
    const modal = document.getElementById('settingsModal');
    if (modal) {
      modal.classList.remove('active');
    }
  }

  loadSettings() {
    const settings = this.getSettings();

    const inputs = {
      maxReviews: settings.maxReviews,
      maxPlaces: settings.maxPlaces,
      dateRange: settings.dateRange,
      language: settings.language,
      region: settings.region
    };

    Object.entries(inputs).forEach(([key, value]) => {
      const input = document.getElementById(key);
      if (input) input.value = value;
    });

    const unlimitedReviews = document.getElementById('unlimitedReviews');
    const unlimitedTime = document.getElementById('unlimitedTime');
    if (unlimitedReviews) unlimitedReviews.checked = settings.unlimitedReviews;
    if (unlimitedTime) unlimitedTime.checked = settings.unlimitedTime;
  }

  getSettings() {
    const stored = localStorage.getItem('scraperSettings');
    if (stored) {
      try {
        return JSON.parse(stored);
      } catch (e) {
        console.error('Failed to parse settings:', e);
      }
    }

    return {
      maxReviews: 100,
      unlimitedReviews: false,
      maxPlaces: 5,
      dateRange: '1year',
      language: 'th',
      region: 'th'
    };
  }

  saveSettings() {
    const settings = {
      maxReviews: parseInt(document.getElementById('maxReviews')?.value || 100),
      unlimitedReviews: document.getElementById('unlimitedReviews')?.checked || false,
      maxPlaces: parseInt(document.getElementById('maxPlaces')?.value || 5),
      dateRange: document.getElementById('dateRange')?.value || '1year',
      language: document.getElementById('language')?.value || 'th',
      region: document.getElementById('region')?.value || 'th'
    };

    localStorage.setItem('scraperSettings', JSON.stringify(settings));
    this.showToast('Settings saved successfully', 'success');
    this.closeSettings();
  }

  saveJobsToStorage() {
    const jobsArray = Array.from(this.jobs.entries());
    localStorage.setItem('scraperJobs', JSON.stringify(jobsArray));
  }

  loadJobsFromStorage() {
    const stored = localStorage.getItem('scraperJobs');
    if (stored) {
      try {
        const jobsArray = JSON.parse(stored);
        this.jobs = new Map(jobsArray);
      } catch (e) {
        console.error('Failed to load jobs:', e);
      }
    }
  }

  showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;

    const icons = {
      success: '✅',
      error: '❌',
      info: 'ℹ️',
      warning: '⚠️'
    };

    toast.innerHTML = `
      <span class="toast-icon">${icons[type] || icons.info}</span>
      <span class="toast-message">${this.escapeHtml(message)}</span>
      <button class="toast-close">&times;</button>
    `;

    container.appendChild(toast);

    // Add close handler
    toast.querySelector('.toast-close').addEventListener('click', () => {
      toast.remove();
    });

    // Show animation
    requestAnimationFrame(() => {
      toast.classList.add('show');
    });

    // Auto-remove
    setTimeout(() => {
      if (toast.parentNode) {
        toast.remove();
      }
    }, 5000);
  }

  escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  formatDate(dateString) {
    return new Date(dateString).toLocaleDateString();
  }

  formatTime(dateString) {
    return new Date(dateString).toLocaleTimeString();
  }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  window.app = new GoogleMapsScraperApp();
});