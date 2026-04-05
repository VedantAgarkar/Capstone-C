// JavaScript for Heart Disease Risk Assessment

const API_BASE = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' ? 'http://localhost:8000' : 'https://your-render-backend-url.onrender.com'; 

document.getElementById('heartForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const lang = localStorage.getItem('healthpredict_lang') || 'en';
    const token = localStorage.getItem('token');
    const headers = { 'Content-Type': 'application/json' };
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const payload = {
        age: parseInt(document.getElementById('age').value),
        sex: document.getElementById('sex').value,
        chest_pain: document.getElementById('chest_pain').value,
        resting_bp: parseInt(document.getElementById('resting_bp').value),
        cholesterol: parseInt(document.getElementById('cholesterol').value),
        fasting_blood_sugar: document.getElementById('fasting_blood_sugar').value,
        rest_ecg: document.getElementById('rest_ecg').value,
        max_heart_rate: parseInt(document.getElementById('max_heart_rate').value),
        exercise_induced_angina: document.getElementById('exercise_induced_angina').value,
        st_depression: parseFloat(document.getElementById('st_depression').value),
        slope: document.getElementById('slope').value,
        ca: parseInt(document.getElementById('ca').value),
        thal: document.getElementById('thal').value,
        family_history: document.getElementById('family_history').value,
        diabetes: document.getElementById('diabetes_history').value,
        hypertension: document.getElementById('hypertension').value,
        smoking: document.getElementById('smoking').value,
        exercise_frequency: document.getElementById('exercise_frequency').value,
        bmi: parseFloat(document.getElementById('bmi').value),
        lang
    };

    document.getElementById('loadingOverlay').classList.add('active');

    try {
        const res = await fetch(`${API_BASE}/api/predict/heart`, {
            method: 'POST', 
            headers, 
            body: JSON.stringify(payload)
        });
        if (!res.ok) throw new Error(`Error ${res.status}`);
        const data = await res.json();

        document.getElementById('loadingOverlay').classList.remove('active');
        renderResult(data, 'probability of heart disease');
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
