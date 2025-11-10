// Global state
let selectedPlace = null;
let activeTasks = [];
let settings = {
    maxReviews: 100,
    unlimitedReviews: false,
    stopTime: 60,
    unlimitedTime: false,
    maxPlaces: 5,
    dateRange: '1year',
    language: 'th',
    region: 'th'
};

// Load settings from localStorage
function loadSettings() {
    const saved = localStorage.getItem('scraperSettings');
    if (saved) {
        settings = { ...settings, ...JSON.parse(saved) };
        applySettings();
    }
}

// Apply settings to UI
function applySettings() {
    document.getElementById('maxReviews').value = settings.maxReviews;
    document.getElementById('unlimitedReviews').checked = settings.unlimitedReviews;
    document.getElementById('stopTime').value = settings.stopTime;
    document.getElementById('unlimitedTime').checked = settings.unlimitedTime;
    document.getElementById('maxPlaces').value = settings.maxPlaces;
    document.getElementById('dateRange').value = settings.dateRange;
    document.getElementById('language').value = settings.language;
    document.getElementById('region').value = settings.region;
}

// Save settings to localStorage
function saveSettings() {
    settings.maxReviews = parseInt(document.getElementById('maxReviews').value);
    settings.unlimitedReviews = document.getElementById('unlimitedReviews').checked;
    settings.stopTime = parseInt(document.getElementById('stopTime').value);
    settings.unlimitedTime = document.getElementById('unlimitedTime').checked;
    settings.maxPlaces = parseInt(document.getElementById('maxPlaces').value);
    settings.dateRange = document.getElementById('dateRange').value;
    settings.language = document.getElementById('language').value;
    settings.region = document.getElementById('region').value;

    localStorage.setItem('scraperSettings', JSON.stringify(settings));
    showToast('บันทึกการตั้งค่าเรียบร้อย', 'success');
}

// Toast notification
function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    container.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, 3000);
}

// Tab switching
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const tabName = btn.dataset.tab;

        // Update active tab button
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        // Update active tab content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(`${tabName}-tab`).classList.add('active');

        // Refresh tab content
        if (tabName === 'progress') {
            refreshProgress();
        } else if (tabName === 'history') {
            refreshHistory();
        }
    });
});

// Settings modal
const settingsModal = document.getElementById('settingsModal');
const settingsBtn = document.getElementById('settingsBtn');
const closeBtn = document.querySelector('.close');
const saveSettingsBtn = document.getElementById('saveSettingsBtn');
const cancelSettingsBtn = document.getElementById('cancelSettingsBtn');

settingsBtn.addEventListener('click', () => {
    settingsModal.classList.add('active');
});

closeBtn.addEventListener('click', () => {
    settingsModal.classList.remove('active');
});

cancelSettingsBtn.addEventListener('click', () => {
    settingsModal.classList.remove('active');
});

saveSettingsBtn.addEventListener('click', () => {
    saveSettings();
    settingsModal.classList.remove('active');
});

// Search functionality
const searchInput = document.getElementById('searchInput');
const searchBtn = document.getElementById('searchBtn');
const searchResults = document.getElementById('searchResults');

searchBtn.addEventListener('click', searchPlaces);
searchInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        searchPlaces();
    }
});

async function searchPlaces() {
    const query = searchInput.value.trim();
    if (!query) {
        showToast('กรุณาใส่คำค้นหา', 'error');
        return;
    }

    searchBtn.disabled = true;
    searchBtn.innerHTML = '<span class="loading"></span> กำลังค้นหา...';
    searchResults.innerHTML = '';

    try {
        const response = await fetch('/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                query: query,
                max_results: settings.maxPlaces,
                language: settings.language,
                region: settings.region
            })
        });

        const data = await response.json();

        if (data.success && data.places.length > 0) {
            showToast(`พบ ${data.places.length} สถานที่`, 'success');
            displayPlaces(data.places);
        } else {
            searchResults.innerHTML = '<div class="empty-state"><div class="empty-state-icon">🔍</div><p>ไม่พบสถานที่</p></div>';
            showToast('ไม่พบสถานที่', 'info');
        }
    } catch (error) {
        console.error('Search error:', error);
        showToast('เกิดข้อผิดพลาดในการค้นหา', 'error');
    } finally {
        searchBtn.disabled = false;
        searchBtn.textContent = 'ค้นหา';
    }
}

function displayPlaces(places) {
    searchResults.innerHTML = '<h3>ผลการค้นหา (' + places.length + ' สถานที่)</h3>';

    places.forEach(place => {
        const card = document.createElement('div');
        card.className = 'place-card';
        card.innerHTML = `
            <div class="place-name">${place.name}</div>
            <div class="place-rating">⭐ ${place.rating} (${place.total_reviews.toLocaleString()} รีวิว)</div>
            <div class="place-address">${place.address}</div>
            <span class="place-category">${place.category}</span>
        `;

        card.addEventListener('click', () => selectPlace(place, card));
        searchResults.appendChild(card);
    });
}

function selectPlace(place, cardElement) {
    selectedPlace = place;

    // Update UI
    document.querySelectorAll('.place-card').forEach(card => {
        card.classList.remove('selected');
    });
    cardElement.classList.add('selected');

    // Show selected place section
    const selectedPlaceDiv = document.getElementById('selectedPlace');
    const selectedPlaceInfo = document.getElementById('selectedPlaceInfo');

    selectedPlaceInfo.innerHTML = `
        <div class="place-name">${place.name}</div>
        <div class="place-rating">⭐ ${place.rating} (${place.total_reviews.toLocaleString()} รีวิว)</div>
        <div class="place-address">${place.address}</div>
        <p style="margin-top: 10px; color: #6c757d;">Place ID: ${place.place_id}</p>
    `;

    selectedPlaceDiv.style.display = 'block';
    showToast(`เลือกสถานที่: ${place.name}`, 'success');
}

// Start scraping
const startScrapeBtn = document.getElementById('startScrapeBtn');
startScrapeBtn.addEventListener('click', startScraping);

async function startScraping() {
    if (!selectedPlace) {
        showToast('กรุณาเลือกสถานที่ก่อน', 'error');
        return;
    }

    startScrapeBtn.disabled = true;
    startScrapeBtn.innerHTML = '<span class="loading"></span> กำลังเริ่ม...';

    try {
        const response = await fetch('/scrape', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                place_id: selectedPlace.place_id,
                place_name: selectedPlace.name,
                settings: {
                    max_reviews: settings.unlimitedReviews ? 999999 : settings.maxReviews,
                    stop_time: settings.unlimitedTime ? 999999 : settings.stopTime,
                    date_range: settings.dateRange,
                    language: settings.language,
                    region: settings.region
                }
            })
        });

        const data = await response.json();

        if (data.success) {
            showToast('เริ่ม scraping เรียบร้อย', 'success');
            activeTasks.push(data.task_id);

            // Switch to progress tab
            document.querySelector('[data-tab="progress"]').click();

            // Start polling for updates
            pollTaskStatus(data.task_id);
        } else {
            showToast('เกิดข้อผิดพลาด: ' + data.error, 'error');
        }
    } catch (error) {
        console.error('Scrape error:', error);
        showToast('เกิดข้อผิดพลาดในการเริ่ม scraping', 'error');
    } finally {
        startScrapeBtn.disabled = false;
        startScrapeBtn.textContent = 'เริ่ม Scraping';
    }
}

// Poll task status
async function pollTaskStatus(taskId) {
    const interval = setInterval(async () => {
        try {
            const response = await fetch(`/status/${taskId}`);
            const data = await response.json();

            if (data.success) {
                updateTaskProgress(taskId, data);

                if (data.status === 'completed' || data.status === 'failed') {
                    clearInterval(interval);
                    if (data.status === 'completed') {
                        showToast('Scraping เสร็จสิ้น!', 'success');
                    } else {
                        showToast('Scraping ล้มเหลว: ' + data.error, 'error');
                    }
                }
            }
        } catch (error) {
            console.error('Poll error:', error);
            clearInterval(interval);
        }
    }, 2000);
}

function updateTaskProgress(taskId, data) {
    const container = document.getElementById('progressContainer');
    let card = document.getElementById(`task-${taskId}`);

    if (!card) {
        card = document.createElement('div');
        card.id = `task-${taskId}`;
        card.className = 'progress-card';
        container.appendChild(card);
    }

    const statusClass = `status-${data.status}`;

    card.innerHTML = `
        <div class="progress-header">
            <h3>${data.message || 'กำลังประมวลผล...'}</h3>
            <span class="status-badge ${statusClass}">${getStatusText(data.status)}</span>
        </div>
        <div class="progress-bar">
            <div class="progress-fill" style="width: ${data.progress}%">
                ${data.progress}%
            </div>
        </div>
        <p style="margin-top: 10px; color: #6c757d;">
            รีวิว: ${data.scraped_reviews} / ${data.total_reviews || '?'}
        </p>
    `;
}

function getStatusText(status) {
    const statusMap = {
        'pending': 'รอดำเนินการ',
        'running': 'กำลังทำงาน',
        'completed': 'เสร็จสิ้น',
        'failed': 'ล้มเหลว'
    };
    return statusMap[status] || status;
}

// Refresh progress
async function refreshProgress() {
    try {
        const response = await fetch('/tasks');
        const data = await response.json();

        if (data.success) {
            const container = document.getElementById('progressContainer');

            if (data.tasks.length === 0) {
                container.innerHTML = '<div class="empty-state"><div class="empty-state-icon">📊</div><p>ยังไม่มีงาน scraping</p></div>';
            } else {
                container.innerHTML = '';
                data.tasks.forEach(task => {
                    // Fetch detailed status for each task
                    fetch(`/status/${task.task_id}`)
                        .then(res => res.json())
                        .then(taskData => {
                            if (taskData.success) {
                                updateTaskProgress(task.task_id, taskData);
                            }
                        });
                });
            }
        }
    } catch (error) {
        console.error('Refresh error:', error);
    }
}

// Refresh history
async function refreshHistory() {
    try {
        const response = await fetch('/tasks');
        const data = await response.json();

        if (data.success) {
            const container = document.getElementById('historyContainer');

            const completedTasks = data.tasks.filter(t => t.status === 'completed');

            if (completedTasks.length === 0) {
                container.innerHTML = '<div class="empty-state"><div class="empty-state-icon">📋</div><p>ยังไม่มีประวัติ</p></div>';
            } else {
                container.innerHTML = '<div class="history-list"></div>';
                const list = container.querySelector('.history-list');

                completedTasks.forEach(task => {
                    const item = document.createElement('div');
                    item.className = 'progress-card';
                    item.innerHTML = `
                        <h3>${task.place_name}</h3>
                        <p>รีวิว: ${task.scraped_reviews} รีวิว</p>
                        <p style="color: #6c757d; font-size: 0.9em;">
                            เวลา: ${new Date(task.started_at).toLocaleString('th-TH')}
                        </p>
                    `;
                    list.appendChild(item);
                });
            }
        }
    } catch (error) {
        console.error('History error:', error);
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadSettings();

    // Auto-refresh progress when on progress tab
    setInterval(() => {
        const progressTab = document.getElementById('progress-tab');
        if (progressTab.classList.contains('active')) {
            refreshProgress();
        }
    }, 5000);
});
