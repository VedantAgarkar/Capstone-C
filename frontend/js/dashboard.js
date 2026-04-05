const API_BASE = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' ? 'http://localhost:8000' : 'https://healthpredict-i5qi.onrender.com';
document.addEventListener('DOMContentLoaded', () => {
    // Security Check: Redirect if not logged in
    const userJson = localStorage.getItem('user');
    if (!userJson) {
        window.location.href = 'login.html';
        return;
    }

    const user = JSON.parse(userJson);
    
    // Toggle View based on Role
    if (user.is_admin) {
        document.getElementById('adminView').style.display = 'grid';
        fetchAdminStats();
    } else {
        const userView = document.getElementById('userView');
        if (userView) userView.style.display = 'grid';
        
        const title = document.getElementById('headerTitle');
        if (title) title.textContent = `Welcome, ${user.fullname}`;
        
        const subtitle = document.getElementById('headerSubtitle');
        if (subtitle) subtitle.textContent = "Your personal health report card";
        
        fetchUserStats();
    }

    // Refresh button event listener
    const refreshBtn = document.getElementById('refreshBtn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', () => {
            refreshDashboard(user.is_admin);
        });
    }
});

async function refreshDashboard(isAdmin) {
    const btn = document.getElementById('refreshBtn');
    if (btn) btn.classList.add('loading');

    if (isAdmin) await fetchAdminStats();
    else await fetchUserStats();

    // Minor delay for visual feedback
    setTimeout(() => {
        if (btn) btn.classList.remove('loading');
    }, 600);
}

async function fetchAdminStats() {
    const token = localStorage.getItem('token');
    try {
        const response = await fetch(`${API_BASE}/api/admin/stats`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (!response.ok) {
            if (response.status === 401 || response.status === 403) {
                hAlert('Access Denied', 'Session expired or access denied.', () => {
                    window.location.href = 'login.html';
                });
                return;
            }
            throw new Error('Failed to fetch admin stats');
        }

        const data = await response.json();
        
        // Update Total Users
        const totalUsersEl = document.getElementById('totalUsers');
        if (totalUsersEl) totalUsersEl.textContent = data.total_users;

        // Update Breakdown
        populateBreakdown(data.prediction_breakdown);

        // Update Recent Predictions
        populateRecentPredictions(data.recent_predictions);

    } catch (error) {
        console.error('Error loading admin dashboard:', error);
    }
}

async function fetchUserStats() {
    const token = localStorage.getItem('token');
    try {
        const response = await fetch(`${API_BASE}/api/user/stats`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (!response.ok) {
            if (response.status === 401) {
                hAlert('Session Expired', 'Session expired. Please log in again.', () => {
                    window.location.href = 'login.html';
                });
                return;
            }
            throw new Error('Failed to fetch user stats');
        }

        const data = await response.json();
        
        // Update Wellness Score
        const wellnessScoreEl = document.getElementById('wellnessScore');
        if (wellnessScoreEl) wellnessScoreEl.textContent = data.wellness_score;
        
        // Populate Status Cards (latest of each)
        populateUserStatusCards(data.predictions);
        
        // Populate History Table
        populateUserHistoryTable(data.predictions);

    } catch (error) {
        console.error('Error loading user dashboard:', error);
    }
}

function populateUserStatusCards(predictions) {
    const list = document.getElementById('userHealthList');
    if (!list) return;
    list.innerHTML = '';
    
    const types = ["Heart Disease", "Diabetes", "Parkinson's"];
    const latest = {};
    
    // Find latest for each type
    predictions.forEach(p => {
        if (!latest[p.type]) {
            latest[p.type] = p;
        }
    });
    
    types.forEach(type => {
        const card = document.createElement('div');
        card.className = 'health-status-card';
        
        const data = latest[type];
        if (data) {
            card.innerHTML = `
                <span class="status-type">${type}</span>
                <span class="status-outcome">${data.outcome}</span>
            `;
        } else {
            card.innerHTML = `
                <span class="status-type">${type}</span>
                <span class="status-outcome" style="color: var(--dash-muted); font-size: 0.9rem;">No data yet</span>
            `;
        }
        list.appendChild(card);
    });
}

function populateUserHistoryTable(predictions) {
    const body = document.getElementById('userHistoryBody');
    if (!body) return;
    body.innerHTML = '';

    if (predictions.length === 0) {
        body.innerHTML = '<tr><td colspan="3" class="loading-text">No previous assessments found.</td></tr>';
        return;
    }

    predictions.forEach(p => {
        const row = document.createElement('tr');
        const date = new Date(p.timestamp).toLocaleString();
        
        row.innerHTML = `
            <td><span class="breakdown-count" style="background: rgba(255,255,255,0.1);">${p.type}</span></td>
            <td>${p.outcome}</td>
            <td style="color: var(--dash-muted); font-size: 0.8rem;">${date}</td>
        `;
        body.appendChild(row);
    });
}

function populateBreakdown(breakdown) {
    const list = document.getElementById('breakdownList');
    if (!list) return;
    list.innerHTML = '';

    const types = Object.keys(breakdown);
    if (types.length === 0) {
        list.innerHTML = '<p class="loading-text">No predictions logged yet.</p>';
        return;
    }

    types.forEach(type => {
        const item = document.createElement('div');
        item.className = 'breakdown-item';
        item.innerHTML = `
            <span class="breakdown-label">${capitalize(type)}</span>
            <span class="breakdown-count">${breakdown[type]}</span>
        `;
        list.appendChild(item);
    });
}

function populateRecentPredictions(predictions) {
    const body = document.getElementById('recentPredictionsBody');
    if (!body) return;
    body.innerHTML = '';

    if (predictions.length === 0) {
        body.innerHTML = '<tr><td colspan="4" class="loading-text">No recent activity.</td></tr>';
        return;
    }

    predictions.forEach(p => {
        const row = document.createElement('tr');
        const date = new Date(p.timestamp).toLocaleString();
        
        row.innerHTML = `
            <td>${p.fullname}</td>
            <td><span class="breakdown-count" style="background: rgba(255,255,255,0.1);">${capitalize(p.type)}</span></td>
            <td>${p.outcome}</td>
            <td style="color: var(--dash-muted); font-size: 0.8rem;">${date}</td>
        `;
        body.appendChild(row);
    });
}

function capitalize(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}
