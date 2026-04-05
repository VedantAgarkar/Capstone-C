// JavaScript for Diabetes Risk Assessment

const API_BASE = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' ? 'http://localhost:8000' : 'https://your-render-backend-url.onrender.com'; 

document.getElementById('diabetesForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const lang = localStorage.getItem('healthpredict_lang') || 'en';
    const token = localStorage.getItem('token');
    const headers = { 'Content-Type': 'application/json' };
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const payload = {
        pregnancies: parseInt(document.getElementById('pregnancies').value),
        glucose: parseInt(document.getElementById('glucose').value),
        blood_pressure: parseInt(document.getElementById('blood_pressure').value),
        skin_thickness: parseInt(document.getElementById('skin_thickness').value),
        insulin: parseInt(document.getElementById('insulin').value),
        bmi: parseFloat(document.getElementById('bmi').value),
        diabetes_pedigree: parseFloat(document.getElementById('diabetes_pedigree').value),
        age: parseInt(document.getElementById('age').value),
        family_history: document.getElementById('family_history').value,
        physical_activity: document.getElementById('physical_activity').value,
        smoking: document.getElementById('smoking').value,
        diet_quality: document.getElementById('diet_quality').value,
        hypertension: document.getElementById('hypertension').value,
        sleep_hours: parseInt(document.getElementById('sleep_hours').value),
        sex: document.getElementById('sex').value,
        lang
    };

    document.getElementById('loadingOverlay').classList.add('active');

    try {
        const res = await fetch(`${API_BASE}/api/predict/diabetes`, {
            method: 'POST', 
            headers, 
            body: JSON.stringify(payload)
        });
        if (!res.ok) throw new Error(`Error ${res.status}`);
        const data = await res.json();

        document.getElementById('loadingOverlay').classList.remove('active');
        renderResult(data, 'probability of diabetes');
    } catch (err) {
        document.getElementById('loadingOverlay').classList.remove('active');
        hAlert('Assessment Error', err.message || 'Please try again.');
    }
});

function renderResult(data, probabilityLabel) {
    const resultSection = document.getElementById('resultSection');
    resultSection.style.display = 'block';

    // Risk arrow + label
    const pct = Math.max(0, Math.min(100, data.risk_pct));
    document.getElementById('riskArrow').style.left = `calc(${pct}% - 8px)`;
    document.getElementById('riskLabel').style.left = `${pct}%`;
    document.getElementById('riskLabel').textContent = `${pct.toFixed(1)}%`;

    // Badge
    const badge = document.getElementById('riskBadge');
    badge.textContent = `${data.risk_class}: ${pct.toFixed(1)}% ${probabilityLabel}`;
    badge.className = 'risk-badge ' +
        (pct > 70 ? 'badge-high' : pct > 40 ? 'badge-moderate' : 'badge-low');

    // AI Summary (markdown-like)
    document.getElementById('summaryText').innerHTML = renderMarkdown(data.assessment);

    resultSection.scrollIntoView({ behavior: 'smooth' });
}

function renderMarkdown(text) {
    if (!text) return '<p>No assessment available.</p>';
    return text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/^### (.*$)/gm, '<h4>$1</h4>')
        .replace(/^## (.*$)/gm, '<h3>$1</h3>')
        .replace(/^- (.*$)/gm, '<li>$1</li>')
        .replace(/(<li>.*<\/li>\n?)+/g, '<ul>$&</ul>')
        .replace(/\n\n+/g, '</p><p>')
        .replace(/^(?!<[hup])/gm, '')
        .replace(/\n/g, '<br>');
}
