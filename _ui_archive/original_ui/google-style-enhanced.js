/**
 * Google Maps Scraper - Google-Style Enhanced Interface
 * Enhanced user experience with smooth animations, better error handling, and accessibility
 */

// ===== GLOBAL STATE =====
const AppState = {
    selectedPlace: null,
    activeTasks: new Map(),
    searchHistory: [],
    settings: {
        maxReviews: 100,
        unlimitedReviews: false,
        stopTime: 60,
        unlimitedTime: false,
        maxPlaces: 5,
        dateRange: '1year',
        language: 'th',
        region: 'th'
    },
    isSearching: false,
    currentTab: 'search'
};

// ===== UTILITY FUNCTIONS =====
const Utils = {
    // Debounce function for search input
    debounce: (func, wait) => {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    // Format numbers with Thai locale
    formatNumber: (num) => {
        return new Intl.NumberFormat('th-TH').format(num);
    },

    // Format dates with Thai locale
    formatDate: (date) => {
        return new Intl.DateTimeFormat('th-TH', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        }).format(new Date(date));
    },

    // Escape HTML to prevent XSS
    escapeHtml: (text) => {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },

    // Copy to clipboard
    copyToClipboard: async (text) => {
        try {
            await navigator.clipboard.writeText(text);
            showToast('คัดลอกไปยังคลิปบอร์ดแล้ว', 'success');
        } catch (err) {
            console.error('Failed to copy text: ', err);
            showToast('ไม่สามารถคัดลอกข้อความได้', 'error');
        }
    }
};

// ===== TOAST NOTIFICATION SYSTEM =====
class ToastManager {
    constructor() {
        this.container = document.getElementById('toastContainer');
        this.toasts = new Map();
    }

    show(message, type = 'info', options = {}) {
        const {
            duration = 4000,
            persistent = false,
            action = null
        } = options;

        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerHTML = `
            <div class="toast-content">
                <span class="toast-message">${Utils.escapeHtml(message)}</span>
                ${action ? `<button class="toast-action">${action.text}</button>` : ''}
                <button class="toast-close" aria-label="ปิด">&times;</button>
            </div>
        `;

        const toastId = Date.now().toString();
        this.toasts.set(toastId, toast);
        this.container.appendChild(toast);

        // Add entrance animation
        requestAnimationFrame(() => {
            toast.classList.add('toast-show');
        });

        // Event listeners
        const closeBtn = toast.querySelector('.toast-close');
        closeBtn.addEventListener('click', () => this.hide(toastId));

        if (action) {
            const actionBtn = toast.querySelector('.toast-action');
            actionBtn.addEventListener('click', () => {
                action.handler();
                this.hide(toastId);
            });
        }

        // Auto-hide if not persistent
        if (!persistent) {
            setTimeout(() => this.hide(toastId), duration);
        }

        return toastId;
    }

    hide(toastId) {
        const toast = this.toasts.get(toastId);
        if (toast) {
            toast.classList.add('toast-hide');
            setTimeout(() => {
                toast.remove();
                this.toasts.delete(toastId);
            }, 300);
        }
    }

    success(message, options = {}) {
        return this.show(message, 'success', options);
    }

    error(message, options = {}) {
        return this.show(message, 'error', { ...options, persistent: true });
    }

    info(message, options = {}) {
        return this.show(message, 'info', options);
    }

    warning(message, options = {}) {
        return this.show(message, 'warning', options);
    }
}

const toastManager = new ToastManager();

// ===== MODAL MANAGER =====
class ModalManager {
    constructor() {
        this.activeModal = null;
        this.initEventListeners();
    }

    initEventListeners() {
        // Close modal on escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.activeModal) {
                this.close();
            }
        });

        // Close modal on backdrop click
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal')) {
                this.close();
            }
        });
    }

    open(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            this.activeModal = modal;
            modal.classList.add('active');
            document.body.style.overflow = 'hidden';

            // Focus management
            const firstFocusable = modal.querySelector('button, input, select, textarea, [tabindex]:not([tabindex="-1"])');
            if (firstFocusable) {
                firstFocusable.focus();
            }
        }
    }

    close() {
        if (this.activeModal) {
            this.activeModal.classList.remove('active');
            document.body.style.overflow = '';
            this.activeModal = null;
        }
    }
}

const modalManager = new ModalManager();

// ===== SEARCH FUNCTIONALITY =====
class SearchManager {
    constructor() {
        this.searchInput = document.getElementById('searchInput');
        this.searchBtn = document.getElementById('searchBtn');
        this.searchResults = document.getElementById('searchResults');
        this.debounceSearch = Utils.debounce(this.performSearch.bind(this), 300);
        this.initEventListeners();
    }

    initEventListeners() {
        this.searchBtn.addEventListener('click', () => this.search());
        this.searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                this.search();
            }
        });

        // Add search suggestions
        this.searchInput.addEventListener('input', (e) => {
            const query = e.target.value.trim();
            if (query.length > 2) {
                this.debounceSearch(query);
            } else if (query.length === 0) {
                this.clearResults();
            }
        });
    }

    async search() {
        const query = this.searchInput.value.trim();
        if (!query) {
            toastManager.error('กรุณาใส่คำค้นหา');
            this.searchInput.focus();
            return;
        }

        if (AppState.isSearching) {
            return;
        }

        this.setSearchingState(true);
        this.showLoadingState();

        try {
            const response = await fetch('/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    query: query,
                    max_results: AppState.settings.maxPlaces,
                    language: AppState.settings.language,
                    region: AppState.settings.region
                })
            });

            const data = await response.json();

            if (data.success && data.places.length > 0) {
                // Add to search history
                this.addToHistory(query, data.places);

                toastManager.success(`พบ ${data.places.length} สถานที่`);
                this.displayResults(data.places);
            } else {
                this.showEmptyState();
                toastManager.info('ไม่พบสถานที่ที่ตรงกับการค้นหา');
            }
        } catch (error) {
            console.error('Search error:', error);
            this.showErrorState();
            toastManager.error('เกิดข้อผิดพลาดในการค้นหา กรุณาลองใหม่อีกครั้ง');
        } finally {
            this.setSearchingState(false);
        }
    }

    async performSearch(query) {
        // This could be used for autocomplete suggestions in the future
        // For now, it's debounced search
    }

    setSearchingState(isSearching) {
        AppState.isSearching = isSearching;
        this.searchBtn.disabled = isSearching;

        if (isSearching) {
            this.searchBtn.innerHTML = '<span class="loading"></span> กำลังค้นหา...';
        } else {
            this.searchBtn.textContent = 'ค้นหา';
        }
    }

    showLoadingState() {
        this.searchResults.innerHTML = `
            <div class="search-loading">
                <div class="loading-spinner"></div>
                <p>กำลังค้นหาสถานที่...</p>
            </div>
        `;
    }

    showEmptyState() {
        this.searchResults.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">🔍</div>
                <h3>ไม่พบสถานที่</h3>
                <p>ลองค้นหาด้วยคำอื่นหรือตรวจสอบการสะกดคำ</p>
            </div>
        `;
    }

    showErrorState() {
        this.searchResults.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">⚠️</div>
                <h3>เกิดข้อผิดพลาด</h3>
                <p>ไม่สามารถค้นหาได้ในขณะนี้ กรุณาลองใหม่อีกครั้ง</p>
                <button class="secondary-btn" onclick="searchManager.search()">ลองใหม่</button>
            </div>
        `;
    }

    clearResults() {
        this.searchResults.innerHTML = '';
    }

    displayResults(places) {
        this.searchResults.innerHTML = `
            <div class="results-header">
                <h3>ผลการค้นหา (${places.length} สถานที่)</h3>
                <button class="text-btn" onclick="searchManager.clearResults()">ล้างผลลัพธ์</button>
            </div>
            <div class="places-grid">
                ${places.map(place => this.createPlaceCard(place)).join('')}
            </div>
        `;

        // Add event listeners to place cards
        this.searchResults.querySelectorAll('.place-card').forEach((card, index) => {
            card.addEventListener('click', () => {
                this.selectPlace(places[index], card);
            });
        });
    }

    createPlaceCard(place) {
        const rating = place.rating || 0;
        const reviews = place.total_reviews || 0;
        const address = Utils.escapeHtml(place.address || 'ไม่มีที่อยู่');
        const category = Utils.escapeHtml(place.category || 'ไม่ระบุหมวดหมู่');
        const name = Utils.escapeHtml(place.name);

        return `
            <div class="place-card" tabindex="0" role="button" aria-label="เลือกสถานที่: ${name}">
                <div class="place-header">
                    <h4 class="place-name">${name}</h4>
                    <div class="place-rating">
                        <span class="rating-stars">${this.renderStars(rating)}</span>
                        <span class="rating-value">${rating.toFixed(1)}</span>
                        <span class="rating-count">(${Utils.formatNumber(reviews)} รีวิว)</span>
                    </div>
                </div>
                <div class="place-details">
                    <div class="place-address">
                        <svg class="icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
                            <circle cx="12" cy="10" r="3"></circle>
                        </svg>
                        ${address}
                    </div>
                    <div class="place-meta">
                        <span class="place-category">${category}</span>
                        ${place.latitude && place.longitude ? `
                            <button class="text-btn" onclick="event.stopPropagation(); window.open('https://maps.google.com/?q=${place.latitude},${place.longitude}', '_blank')">
                                <svg class="icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>
                                    <polyline points="15,3 21,3 21,9"></polyline>
                                    <line x1="10" y1="14" x2="21" y2="3"></line>
                                </svg>
                                ดูแผนที่
                            </button>
                        ` : ''}
                    </div>
                </div>
            </div>
        `;
    }

    renderStars(rating) {
        const fullStars = Math.floor(rating);
        const hasHalfStar = rating % 1 >= 0.5;
        const emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0);

        let stars = '';
        for (let i = 0; i < fullStars; i++) {
            stars += '<span class="star">⭐</span>';
        }
        if (hasHalfStar) {
            stars += '<span class="star">⭐</span>';
        }
        for (let i = 0; i < emptyStars; i++) {
            stars += '<span class="star empty">☆</span>';
        }
        return stars;
    }

    selectPlace(place, cardElement) {
        // Update selected place state
        AppState.selectedPlace = place;

        // Update UI
        document.querySelectorAll('.place-card').forEach(card => {
            card.classList.remove('selected');
            card.setAttribute('aria-selected', 'false');
        });

        cardElement.classList.add('selected');
        cardElement.setAttribute('aria-selected', 'true');

        // Show selected place section
        this.showSelectedPlace(place);

        // Smooth scroll to selected place section
        document.getElementById('selectedPlace').scrollIntoView({
            behavior: 'smooth',
            block: 'nearest'
        });

        toastManager.success(`เลือกสถานที่: ${place.name}`);
    }

    showSelectedPlace(place) {
        const selectedPlaceDiv = document.getElementById('selectedPlace');
        const selectedPlaceInfo = document.getElementById('selectedPlaceInfo');

        selectedPlaceInfo.innerHTML = `
            <div class="selected-place-details">
                <div class="selected-place-header">
                    <h3>${Utils.escapeHtml(place.name)}</h3>
                    <div class="place-rating">
                        <span class="rating-stars">${this.renderStars(place.rating || 0)}</span>
                        <span class="rating-value">${(place.rating || 0).toFixed(1)}</span>
                        <span class="rating-count">(${Utils.formatNumber(place.total_reviews || 0)} รีวิว)</span>
                    </div>
                </div>
                <div class="selected-place-info">
                    <div class="info-item">
                        <svg class="icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
                            <circle cx="12" cy="10" r="3"></circle>
                        </svg>
                        <span>${Utils.escapeHtml(place.address || 'ไม่มีที่อยู่')}</span>
                    </div>
                    <div class="info-item">
                        <svg class="icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <rect x="3" y="11" width="18" height="10" rx="2" ry="2"></rect>
                            <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
                        </svg>
                        <span>Place ID: ${Utils.escapeHtml(place.place_id)}</span>
                        <button class="text-btn" onclick="Utils.copyToClipboard('${place.place_id}')">
                            <svg class="icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                                <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                            </svg>
                        </button>
                    </div>
                    <div class="info-item">
                        <svg class="icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"></path>
                            <line x1="7" y1="7" x2="7.01" y2="7"></line>
                        </svg>
                        <span>${Utils.escapeHtml(place.category || 'ไม่ระบุหมวดหมู่')}</span>
                    </div>
                </div>
            </div>
        `;

        selectedPlaceDiv.style.display = 'block';
    }

    addToHistory(query, places) {
        AppState.searchHistory.unshift({
            query,
            places,
            timestamp: new Date().toISOString()
        });

        // Keep only last 10 searches
        if (AppState.searchHistory.length > 10) {
            AppState.searchHistory = AppState.searchHistory.slice(0, 10);
        }
    }
}

// ===== SETTINGS MANAGER =====
class SettingsManager {
    constructor() {
        this.initEventListeners();
        this.loadSettings();
    }

    initEventListeners() {
        // Settings modal
        document.getElementById('settingsBtn').addEventListener('click', () => {
            modalManager.open('settingsModal');
        });

        document.querySelector('.close').addEventListener('click', () => {
            modalManager.close();
        });

        document.getElementById('cancelSettingsBtn').addEventListener('click', () => {
            modalManager.close();
        });

        document.getElementById('saveSettingsBtn').addEventListener('click', () => {
            this.saveSettings();
            modalManager.close();
        });

        // Settings inputs with validation
        this.setupValidation();
    }

    setupValidation() {
        // Number input validation
        const numberInputs = document.querySelectorAll('input[type="number"]');
        numberInputs.forEach(input => {
            input.addEventListener('input', (e) => {
                const min = parseInt(e.target.min);
                const max = parseInt(e.target.max);
                const value = parseInt(e.target.value);

                if (value < min) e.target.value = min;
                if (value > max) e.target.value = max;
            });
        });

        // Unlimited checkboxes logic
        document.getElementById('unlimitedReviews').addEventListener('change', (e) => {
            document.getElementById('maxReviews').disabled = e.target.checked;
        });

        document.getElementById('unlimitedTime').addEventListener('change', (e) => {
            document.getElementById('stopTime').disabled = e.target.checked;
        });
    }

    loadSettings() {
        const saved = localStorage.getItem('scraperSettings');
        if (saved) {
            try {
                const savedSettings = JSON.parse(saved);
                AppState.settings = { ...AppState.settings, ...savedSettings };
            } catch (e) {
                console.error('Failed to load settings:', e);
            }
        }
        this.applySettings();
    }

    applySettings() {
        const settings = AppState.settings;

        // Apply to form elements
        document.getElementById('maxReviews').value = settings.maxReviews;
        document.getElementById('unlimitedReviews').checked = settings.unlimitedReviews;
        document.getElementById('stopTime').value = settings.stopTime;
        document.getElementById('unlimitedTime').checked = settings.unlimitedTime;
        document.getElementById('maxPlaces').value = settings.maxPlaces;
        document.getElementById('dateRange').value = settings.dateRange;
        document.getElementById('language').value = settings.language;
        document.getElementById('region').value = settings.region;

        // Update disabled states
        document.getElementById('maxReviews').disabled = settings.unlimitedReviews;
        document.getElementById('stopTime').disabled = settings.unlimitedTime;
    }

    saveSettings() {
        const form = document.getElementById('settingsModal');
        const formData = new FormData(form);

        AppState.settings = {
            maxReviews: parseInt(document.getElementById('maxReviews').value),
            unlimitedReviews: document.getElementById('unlimitedReviews').checked,
            stopTime: parseInt(document.getElementById('stopTime').value),
            unlimitedTime: document.getElementById('unlimitedTime').checked,
            maxPlaces: parseInt(document.getElementById('maxPlaces').value),
            dateRange: document.getElementById('dateRange').value,
            language: document.getElementById('language').value,
            region: document.getElementById('region').value
        };

        localStorage.setItem('scraperSettings', JSON.stringify(AppState.settings));
        toastManager.success('บันทึกการตั้งค่าเรียบร้อย');
    }
}

// ===== SCRAPING MANAGER =====
class ScrapingManager {
    constructor() {
        this.startScrapeBtn = document.getElementById('startScrapeBtn');
        this.initEventListeners();
    }

    initEventListeners() {
        this.startScrapeBtn.addEventListener('click', () => this.startScraping());
    }

    async startScraping() {
        if (!AppState.selectedPlace) {
            toastManager.error('กรุณาเลือกสถานที่ก่อน');
            return;
        }

        this.startScrapeBtn.disabled = true;
        this.startScrapeBtn.innerHTML = '<span class="loading"></span> กำลังเริ่ม...';

        try {
            const response = await fetch('/scrape', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    place_id: AppState.selectedPlace.place_id,
                    place_name: AppState.selectedPlace.name,
                    settings: {
                        max_reviews: AppState.settings.unlimitedReviews ? 999999 : AppState.settings.maxReviews,
                        stop_time: AppState.settings.unlimitedTime ? 999999 : AppState.settings.stopTime,
                        date_range: AppState.settings.dateRange,
                        language: AppState.settings.language,
                        region: AppState.settings.region
                    }
                })
            });

            const data = await response.json();

            if (data.success) {
                toastManager.success('เริ่ม scraping เรียบร้อย', {
                    action: {
                        text: 'ดูความคืบหน้า',
                        handler: () => {
                            document.querySelector('[data-tab="progress"]').click();
                        }
                    }
                });

                AppState.activeTasks.set(data.task_id, {
                    ...data,
                    startTime: Date.now()
                });

                // Switch to progress tab
                document.querySelector('[data-tab="progress"]').click();

                // Start monitoring
                this.monitorTask(data.task_id);
            } else {
                toastManager.error('เกิดข้อผิดพลาด: ' + (data.error || 'ไม่ทราบสาเหตุ'));
            }
        } catch (error) {
            console.error('Scrape error:', error);
            toastManager.error('เกิดข้อผิดพลาดในการเริ่ม scraping กรุณาลองใหม่อีกครั้ง');
        } finally {
            this.startScrapeBtn.disabled = false;
            this.startScrapeBtn.textContent = 'เริ่ม Scraping';
        }
    }

    async monitorTask(taskId) {
        const task = AppState.activeTasks.get(taskId);
        if (!task) return;

        const pollInterval = setInterval(async () => {
            try {
                const response = await fetch(`/status/${taskId}`);
                const data = await response.json();

                if (data.success) {
                    this.updateTaskProgress(taskId, data);

                    if (data.status === 'completed') {
                        clearInterval(pollInterval);
                        toastManager.success('Scraping เสร็จสิ้น!', {
                            action: {
                                text: 'ดูผลลัพธ์',
                                handler: () => {
                                    // This could open results or download files
                                    console.log('View results for task:', taskId);
                                }
                            }
                        });
                    } else if (data.status === 'failed') {
                        clearInterval(pollInterval);
                        toastManager.error('Scraping ล้มเหลว: ' + (data.error || 'ไม่ทราบสาเหตุ'), {
                            persistent: true
                        });
                    }
                }
            } catch (error) {
                console.error('Monitor error:', error);
                clearInterval(pollInterval);
                toastManager.error('ไม่สามารถตรวจสอบสถานะได้');
            }
        }, 2000);

        // Store interval for cleanup
        task.pollInterval = pollInterval;
    }

    updateTaskProgress(taskId, data) {
        const container = document.getElementById('progressContainer');
        let card = document.getElementById(`task-${taskId}`);

        if (!card) {
            card = document.createElement('div');
            card.id = `task-${taskId}`;
            card.className = 'progress-card';
            container.appendChild(card);
        }

        const statusClass = `status-${data.status}`;
        const elapsedTime = Date.now() - (AppState.activeTasks.get(taskId)?.startTime || Date.now());
        const elapsedMinutes = Math.floor(elapsedTime / 60000);

        card.innerHTML = `
            <div class="progress-header">
                <div class="progress-title">
                    <h4>${Utils.escapeHtml(data.place_name || 'กำลังประมวลผล...')}</h4>
                    <span class="elapsed-time">เวลาที่ผ่านไป: ${elapsedMinutes} นาที</span>
                </div>
                <span class="status-badge ${statusClass}">${this.getStatusText(data.status)}</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: ${data.progress}%"></div>
            </div>
            <div class="progress-details">
                <div class="progress-stats">
                    <span>รีวิว: ${Utils.formatNumber(data.scraped_reviews || 0)}${data.total_reviews ? ` / ${Utils.formatNumber(data.total_reviews)}` : ''}</span>
                    ${data.reviews_per_sec ? `<span>ความเร็ว: ${data.reviews_per_sec} รีวิว/วินาที</span>` : ''}
                </div>
                ${data.message ? `<p class="progress-message">${Utils.escapeHtml(data.message)}</p>` : ''}
            </div>
        `;
    }

    getStatusText(status) {
        const statusMap = {
            'pending': 'รอดำเนินการ',
            'running': 'กำลังทำงาน',
            'completed': 'เสร็จสิ้น',
            'failed': 'ล้มเหลว'
        };
        return statusMap[status] || status;
    }
}

// ===== TAB MANAGER =====
class TabManager {
    constructor() {
        this.initEventListeners();
    }

    initEventListeners() {
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                this.switchTab(btn.dataset.tab);
            });
        });
    }

    switchTab(tabName) {
        // Update button states
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
            btn.setAttribute('aria-selected', 'false');
        });

        const activeBtn = document.querySelector(`[data-tab="${tabName}"]`);
        activeBtn.classList.add('active');
        activeBtn.setAttribute('aria-selected', 'true');

        // Update content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(`${tabName}-tab`).classList.add('active');

        AppState.currentTab = tabName;

        // Refresh tab content
        this.refreshTabContent(tabName);
    }

    async refreshTabContent(tabName) {
        switch (tabName) {
            case 'progress':
                await this.refreshProgress();
                break;
            case 'history':
                await this.refreshHistory();
                break;
        }
    }

    async refreshProgress() {
        try {
            const response = await fetch('/tasks');
            const data = await response.json();

            if (data.success) {
                const container = document.getElementById('progressContainer');

                if (data.tasks.length === 0) {
                    container.innerHTML = `
                        <div class="empty-state">
                            <div class="empty-state-icon">📊</div>
                            <h3>ยังไม่มีงาน scraping</h3>
                            <p>เริ่มต้นโดยการค้นหาและเลือกสถานที่ที่ต้องการ scrape</p>
                        </div>
                    `;
                } else {
                    container.innerHTML = '';
                    data.tasks.forEach(task => {
                        if (!AppState.activeTasks.has(task.task_id)) {
                            scrapingManager.monitorTask(task.task_id);
                        }
                    });
                }
            }
        } catch (error) {
            console.error('Refresh progress error:', error);
        }
    }

    async refreshHistory() {
        try {
            const response = await fetch('/tasks');
            const data = await response.json();

            if (data.success) {
                const container = document.getElementById('historyContainer');
                const completedTasks = data.tasks.filter(t => t.status === 'completed');

                if (completedTasks.length === 0) {
                    container.innerHTML = `
                        <div class="empty-state">
                            <div class="empty-state-icon">📋</div>
                            <h3>ยังไม่มีประวัติ</h3>
                            <p>งาน scraping ที่เสร็จสมบูรณ์จะแสดงที่นี่</p>
                        </div>
                    `;
                } else {
                    container.innerHTML = '<div class="history-list"></div>';
                    const list = container.querySelector('.history-list');

                    completedTasks.forEach(task => {
                        const item = document.createElement('div');
                        item.className = 'progress-card history-item';
                        item.innerHTML = `
                            <div class="history-header">
                                <h4>${Utils.escapeHtml(task.place_name)}</h4>
                                <span class="history-badge">${Utils.formatNumber(task.scraped_reviews)} รีวิว</span>
                            </div>
                            <div class="history-details">
                                <p>เวลา: ${Utils.formatDate(task.started_at)}</p>
                                ${task.completed_at ? `<p>เสร็จสิ้น: ${Utils.formatDate(task.completed_at)}</p>` : ''}
                            </div>
                            <div class="history-actions">
                                <button class="secondary-btn" onclick="window.open('/download/${task.task_id}', '_blank')">
                                    ดาวน์โหลดผลลัพธ์
                                </button>
                            </div>
                        `;
                        list.appendChild(item);
                    });
                }
            }
        } catch (error) {
            console.error('Refresh history error:', error);
        }
    }
}

// ===== GLOBAL INSTANCES =====
let searchManager, settingsManager, scrapingManager, tabManager;

// ===== LEGACY COMPATIBILITY =====
// Backward compatibility functions for existing code
function showToast(message, type = 'info', options = {}) {
    return toastManager.show(message, type, options);
}

// ===== INITIALIZATION =====
document.addEventListener('DOMContentLoaded', () => {
    // Initialize managers
    searchManager = new SearchManager();
    settingsManager = new SettingsManager();
    scrapingManager = new ScrapingManager();
    tabManager = new TabManager();

    // Auto-refresh progress when on progress tab
    setInterval(() => {
        if (AppState.currentTab === 'progress') {
            tabManager.refreshProgress();
        }
    }, 5000);

    // Add keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        // Ctrl/Cmd + K for search focus
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            document.getElementById('searchInput').focus();
        }

        // Ctrl/Cmd + , for settings
        if ((e.ctrlKey || e.metaKey) && e.key === ',') {
            e.preventDefault();
            modalManager.open('settingsModal');
        }
    });

    console.log('Google Maps Scraper - Enhanced UI initialized');
});

// Export for external access if needed
window.AppState = AppState;
window.Utils = Utils;
window.toastManager = toastManager;