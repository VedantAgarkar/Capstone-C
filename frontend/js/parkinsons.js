// JavaScript for Parkinson's Disease Risk Assessment

const API_BASE = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' ? 'http://localhost:8000' : 'https://your-render-backend-url.onrender.com'; 

document.getElementById('parkinsonsForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const lang = localStorage.getItem('healthpredict_lang') || 'en';
    const token = localStorage.getItem('token');
    const headers = { 'Content-Type': 'application/json' };
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const payload = {
        mdvp_fo: parseFloat(document.getElementById('mdvp_fo').value),
        mdvp_fhi: parseFloat(document.getElementById('mdvp_fhi').value),
        mdvp_flo: parseFloat(document.getElementById('mdvp_flo').value),
        mdvp_jitter_percent: parseFloat(document.getElementById('mdvp_jitter_percent').value),
        mdvp_jitter_abs: parseFloat(document.getElementById('mdvp_jitter_abs').value),
        mdvp_rap: parseFloat(document.getElementById('mdvp_rap').value),
        mdvp_ppq: parseFloat(document.getElementById('mdvp_ppq').value),
        jitter_ddp: parseFloat(document.getElementById('jitter_ddp').value),
        mdvp_shimmer: parseFloat(document.getElementById('mdvp_shimmer').value),
        mdvp_shimmer_db: parseFloat(document.getElementById('mdvp_shimmer_db').value),
        shimmer_apq3: parseFloat(document.getElementById('shimmer_apq3').value),
        shimmer_apq5: parseFloat(document.getElementById('shimmer_apq5').value),
        mdvp_apq: parseFloat(document.getElementById('mdvp_apq').value),
        shimmer_dda: parseFloat(document.getElementById('shimmer_dda').value),
        nhr: parseFloat(document.getElementById('nhr').value),
        hnr: parseFloat(document.getElementById('hnr').value),
        rpde: parseFloat(document.getElementById('rpde').value),
        dfa: parseFloat(document.getElementById('dfa').value),
        spread1: parseFloat(document.getElementById('spread1').value),
        spread2: parseFloat(document.getElementById('spread2').value),
        d2: parseFloat(document.getElementById('d2').value),
        ppe: parseFloat(document.getElementById('ppe').value),
        age: parseInt(document.getElementById('age').value),
        sex: document.getElementById('sex').value,
        family_history: document.getElementById('family_history').value,
        lang
    };

    document.getElementById('loadingOverlay').classList.add('active');

    try {
        const res = await fetch(`${API_BASE}/api/predict/parkinsons`, {
            method: 'POST', 
            headers, 
            body: JSON.stringify(payload)
        });
        if (!res.ok) throw new Error(`Error ${res.status}`);
        const data = await res.json();

        document.getElementById('loadingOverlay').classList.remove('active');
        renderResult(data, "probability of Parkinson's disease");
    } catch (err) {
        document.getElementById('loadingOverlay').classList.remove('active');
        hAlert('Assessment Error', err.message || 'Please try again.');
    }
});

function renderResult(data, probabilityLabel) {
    const resultSection = document.getElementById('resultSection');
    resultSection.style.display = 'block';

    const pct = Math.max(0, Math.min(100, data.risk_pct));
    document.getElementById('riskArrow').style.left = `calc(${pct}% - 8px)`;
    document.getElementById('riskLabel').style.left = `${pct}%`;
    document.getElementById('riskLabel').textContent = `${pct.toFixed(1)}%`;

    const badge = document.getElementById('riskBadge');
    badge.textContent = `${data.risk_class}: ${pct.toFixed(1)}% ${probabilityLabel}`;
    badge.className = 'risk-badge ' +
        (pct > 70 ? 'badge-high' : pct > 40 ? 'badge-moderate' : 'badge-low');

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
