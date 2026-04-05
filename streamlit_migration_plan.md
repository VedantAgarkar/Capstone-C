# Streamlit → Native HTML Migration: Execution Plans

## Overview

| Plan | Wave | Scope | Files |
|------|------|-------|---------|
| 1.1 | 1 | Backend: 3 prediction API endpoints + remove Streamlit subprocess | `backend/main.py` |
| 1.2 | 1 | Frontend: 3 disease HTML pages + shared assess.css | `frontend/heart.html`, `frontend/diabetes.html`, `frontend/parkinsons.html`, `frontend/css/assess.css` |
| 1.3 | 1 | Frontend JS: form submit, fetch, render risk meter + AI summary | `frontend/js/heart.js`, `frontend/js/diabetes.js`, `frontend/js/parkinsons.js` |
| 1.4 | 2 | Wiring: update product.html links + clean global.js Streamlit code | `frontend/product.html`, `frontend/js/global.js` |
| 1.5 | 1 | Chatbot: POST /api/chat endpoint + bot.html full-page chat UI + bot.js | `backend/main.py`, `frontend/bot.html`, `frontend/js/bot.js` |

> Wave 1 plans (1.1, 1.2, 1.3, 1.5) can run in parallel.
> Wave 2 (1.4) runs after all Wave 1 complete.

---

## Plan 1.1 — FastAPI Prediction Endpoints
**Wave 1 | File: `backend/main.py`**

### Objective
Replace Streamlit subprocess launchers with three FastAPI POST endpoints that load `.sav` models, run predictions, call OpenRouter for AI summary, log to DB, and return JSON. Remove all Streamlit startup/shutdown code.

### Task A: Add three prediction endpoints

Add to `backend/main.py` after existing imports:
```python
import pickle, re
import joblib, pandas as pd
from openai import OpenAI

_model_cache = {}  # module-level — prevents reloading models per request
```

**Pydantic request models:**

`DiabetesInput` — fields matching `diabetes.py` line 217-219:
```
pregnancies:int, glucose:int, blood_pressure:int, skin_thickness:int,
insulin:int, bmi:float, diabetes_pedigree:float, age:int,
family_history:str, physical_activity:str, smoking:str,
diet_quality:str, hypertension:str, sleep_hours:int, sex:str, lang:str="en"
```

`HeartInput` — fields matching `heart.py` line 284-286:
```
age:int, sex:str, chest_pain:str, resting_bp:int, cholesterol:int,
fasting_blood_sugar:str, rest_ecg:str, max_heart_rate:int,
exercise_induced_angina:str, st_depression:float, slope:str, ca:int, thal:str,
family_history:str, diabetes:str, hypertension:str, smoking:str,
exercise_frequency:str, bmi:float, lang:str="en"
```

`ParkinsonsInput` — 22 floats matching `parkinsons.py` lines 333-336:
```
mdvp_fo, mdvp_fhi, mdvp_flo, mdvp_jitter_percent, mdvp_jitter_abs,
mdvp_rap, mdvp_ppq, jitter_ddp, mdvp_shimmer, mdvp_shimmer_db,
shimmer_apq3, shimmer_apq5, mdvp_apq, shimmer_dda, nhr, hnr,
rpde, dfa, spread1, spread2, d2, ppe  (all float)
age:int, sex:str, family_history:str, lang:str="en"
```

**Helper `_get_ai_summary(prompt, lang) -> str`:**
- `OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.getenv("OPENROUTER_API_KEY"))`
- model from `OPENROUTER_MODEL` env var
- System prompt adds "RESPOND IN MARATHI" if `lang == "mr"`
- Returns response content or error string — never raises

**`POST /api/predict/diabetes`:**
1. Load `backend/diabetes_model.sav` (joblib) + `backend/diabetes_scaler.sav` (pickle) into `_model_cache`
2. DataFrame columns: `['Pregnancies','Glucose','BloodPressure','SkinThickness','Insulin','BMI','DiabetesPedigreeFunction','Age']`
3. Scale → `predict_proba` → `risk_pct = proba[1] * 100`
4. Risk class: `>70 = HIGH`, `>40 = MODERATE`, else `LOW` (Marathi alts if `lang=="mr"`)
5. Build prompt identical to `diabetes.py` `assessment_prompt` f-string
6. `_get_ai_summary` → `log_prediction` (email from `Authorization` header) → return `{risk_pct, risk_class, assessment, lang}`

**`POST /api/predict/heart`:**
1. Load `backend/heart_disease_model.sav` + `backend/heart_scaler.sav`
2. Encode categoricals **exactly** as `heart.py` lines 274-280:
   - sex: Male=1, Female=0
   - chest_pain: "Typical Angina"=3, "Atypical Angina"=2, "Non-anginal Pain"=1, "Asymptomatic"=0
   - rest_ecg: "Normal"=0, "ST-T Abnormality"=1, "Left Ventricular Hypertrophy"=2
   - fbs/exercise_angina: Yes=1, No=0
   - slope: "Upsloping"=0, "Flat"=1, "Downsloping"=2
   - thal: "Normal"=1, "Fixed Defect"=2, "Reversible Defect"=3
3. 13-col DataFrame → scale → predict → prompt → summary → log → return JSON

**`POST /api/predict/parkinsons`:**
1. Load `backend/parkinsons_model.sav` + `backend/parkinsons_scaler.sav`
2. 22-feature DataFrame (exact column order from `parkinsons.py` lines 333-336)
3. Scale → predict → prompt → summary → log → return JSON

> **AVOID:** importing from `backend.routes.*.py` — those have `st.*` calls
> **AVOID:** reloading models per request — use `_model_cache`
> **USE:** named DataFrame columns matching model training order

**Verify:**
```bash
curl -s -X POST http://localhost:8000/api/predict/diabetes \
  -H "Content-Type: application/json" \
  -d '{"pregnancies":0,"glucose":140,"blood_pressure":80,"skin_thickness":25,"insulin":100,"bmi":28.5,"diabetes_pedigree":0.6,"age":45,"family_history":"Yes","physical_activity":"Light","smoking":"Never","diet_quality":"Fair","hypertension":"No","sleep_hours":7,"sex":"Female","lang":"en"}'
# Expected: {"risk_pct": 65.2, "risk_class": "MODERATE RISK", "assessment": "...", "lang": "en"}
```

### Task B: Remove Streamlit subprocess code

Delete from `main.py`:
- `import subprocess`, `import sys` (lines 1-2)
- `_streamlit_processes = []` (~line 216)
- Entire `launch_streamlit_apps()` function (~lines 225-243)
- `launch_streamlit_apps()` call inside `startup_event()` — keep `init_db()`
- Entire `shutdown_streamlit_apps()` + `@app.on_event("shutdown")` (~lines 245-257)

Result:
```python
@app.on_event("startup")
def startup_event():
    init_db()
```

> **AVOID:** removing static file mount (line 213) or any auth endpoints

### Success Criteria
- [ ] 3 endpoints return `{risk_pct, risk_class, assessment, lang}` on valid input
- [ ] No Streamlit subprocesses launched on startup
- [ ] Model loading cached (2nd request faster)
- [ ] Prediction logged to SQLite

---

## Plan 1.2 — Disease Assessment HTML Pages
**Wave 1 | New files: `frontend/heart.html`, `frontend/diabetes.html`, `frontend/parkinsons.html`, `frontend/css/assess.css`**

### Objective
Create three fully-styled assessment pages replacing Streamlit iframes. Each page has the complete matching form, a result section with risk meter, and AI summary. No ports, no iframes — pure HTML served at `/heart.html`, `/diabetes.html`, `/parkinsons.html`.

### Task A: Create `frontend/css/assess.css`

CSS must include:
```css
/* Shared vars inherit from global.css */
.assess-container { max-width: 900px; margin: 0 auto; padding: 80px 20px 40px; }
.assess-hero { padding: 40px; border-radius: 16px; margin-bottom: 32px; }
  .accent-heart { background: linear-gradient(135deg, #1a1f3a, #4a1020); border-left: 4px solid #dc3545; }
  .accent-diabetes { background: linear-gradient(135deg, #1a1f3a, #3d2000); border-left: 4px solid #fd7e14; }
  .accent-parkinsons { background: linear-gradient(135deg, #1a1f3a, #2a1040); border-left: 4px solid #6f42c1; }
.form-section { background: #fff; border-radius: 12px; padding: 24px; margin-bottom: 20px; box-shadow: 0 2px 12px rgba(0,0,0,0.08); }
.form-section h3 { border-left: 4px solid #B79347; padding-left: 12px; color: #1a1f3a; }
.form-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; }
  @media(max-width:600px) { .form-grid { grid-template-columns: 1fr; } }
.form-group label { font-size: 0.85rem; font-weight: 600; color: #555; display: block; margin-bottom: 6px; }
.form-group input, .form-group select { width: 100%; box-sizing: border-box; border: 1px solid #ddd; border-radius: 8px; padding: 10px; font-size: 1rem; }
  input:focus, select:focus { outline: none; border-color: #B79347; box-shadow: 0 0 0 3px rgba(183,147,71,0.15); }
.assess-btn { width: 100%; padding: 14px; background: #B79347; color: white; border: none; border-radius: 10px; font-size: 1.1rem; font-weight: bold; cursor: pointer; transition: all 0.3s; margin-top: 20px; }
  .assess-btn:hover { background: #a6854a; transform: translateY(-2px); }
  .assess-btn.accent-heart-btn { background: #dc3545; }
  .assess-btn.accent-diabetes-btn { background: #fd7e14; }
  .assess-btn.accent-parkinsons-btn { background: #6f42c1; }
#resultSection { display: none; margin-top: 32px; }
.risk-meter-wrap { position: relative; margin: 20px 0 40px; }
.risk-meter { height: 24px; border-radius: 12px; background: linear-gradient(to right, #28a745 0%, #ffc107 50%, #dc3545 100%); }
.risk-arrow { position: absolute; top: -10px; width: 0; height: 0; border-left: 8px solid transparent; border-right: 8px solid transparent; border-top: 14px solid #333; transform: translateX(-50%); transition: left 0.8s ease; }
.risk-label { position: absolute; top: -28px; background: #333; color: white; padding: 2px 8px; border-radius: 4px; font-size: 13px; font-weight: bold; transform: translateX(-50%); white-space: nowrap; }
.risk-badge { display: inline-block; padding: 10px 24px; border-radius: 50px; color: white; font-weight: bold; font-size: 1rem; margin: 12px 0; }
  .badge-high { background: #dc3545; }
  .badge-moderate { background: #fd7e14; }
  .badge-low { background: #28a745; }
.summary-box { background: #f8f9fa; border-radius: 12px; padding: 24px; line-height: 1.8; border-left: 4px solid #B79347; }
  .summary-box h3, .summary-box h4 { color: #1a1f3a; }
  .summary-box li { margin-bottom: 6px; }
.disclaimer { font-size: 0.85rem; color: #888; font-style: italic; margin-top: 16px; padding: 10px; border-left: 3px solid #B79347; background: #fffdf5; }
.loading-overlay { display: none; position: fixed; inset: 0; background: rgba(26,31,58,0.8); z-index: 9999; justify-content: center; align-items: center; flex-direction: column; }
  .loading-overlay.active { display: flex; }
.spinner { width: 52px; height: 52px; border: 5px solid rgba(183,147,71,0.3); border-top-color: #B79347; border-radius: 50%; animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.loading-text { color: white; margin-top: 16px; font-size: 1.1rem; }
```

### Task B: Create `frontend/heart.html`

Structure:
1. `<head>`: title, `global.css`, `assess.css`, Google Fonts (Outfit), `translations.js`
2. Navbar: copy exactly from `product.html` (Products marked active)
3. Loading overlay: `<div id="loadingOverlay" class="loading-overlay"><div class="spinner"></div><p class="loading-text">Analyzing your data...</p></div>`
4. `.assess-hero.accent-heart`: title + subtitle
5. `.assess-container > <form id="heartForm">`:

   Section 1 — Demographics (`.form-grid` 3 cols):
   - `#age` number (18-120, default 50)
   - `#sex` select (Male/Female)
   - `#bmi` number (15-50, step 0.1, default 25)

   Section 2 — Clinical Measurements (`.form-grid` 2 cols):
   - `#resting_bp` number (80-200, default 120)
   - `#fasting_blood_sugar` select (No/Yes — label: "Fasting Blood Sugar > 120 mg/dl?")
   - `#cholesterol` number (100-400, default 200)
   - `#max_heart_rate` number (60-220, default 150)
   - `#chest_pain` select (Asymptomatic / Non-anginal Pain / Atypical Angina / Typical Angina)

   Section 3 — Cardiovascular Tests:
   - `#rest_ecg` select (Normal / ST-T Abnormality / Left Ventricular Hypertrophy)
   - `#exercise_induced_angina` select (No/Yes)
   - `#st_depression` number (0-10, step 0.1, default 0)
   - `#slope` select (Upsloping / Flat / Downsloping)
   - `#ca` number (0-3, default 0)
   - `#thal` select (Normal / Fixed Defect / Reversible Defect)

   Section 4 — Medical History:
   - `#family_history`, `#diabetes_history`, `#hypertension` — all select No/Yes
   - `#smoking` select (Never/Former/Current)
   - `#exercise_frequency` select (None / 1-2 times / 3-4 times / 5+ times)

6. `.assess-btn.accent-heart-btn` type="submit"
7. `#resultSection` (hidden):
   - `.risk-meter-wrap` with `.risk-meter`, `.risk-arrow#riskArrow`, `.risk-label#riskLabel`
   - `.risk-badge#riskBadge`
   - `.summary-box#summaryText`
   - `.disclaimer`
8. Scripts: `global.js`, `heart.js`

### Task C: Create `frontend/diabetes.html`

Same structure, `accent-diabetes`. Form inputs:

Section 1 — Demographics:
- `#age` (18-120, default 45), `#sex` select, `#pregnancies` (0-20, default 0), `#bmi` (15-70, step 0.1, default 25)

Section 2 — Clinical:
- `#glucose` (0-250, default 100), `#blood_pressure` (0-200, default 70)
- `#skin_thickness` (0-100, default 20), `#insulin` (0-900, default 0)
- `#diabetes_pedigree` (0-2.5, step 0.001, default 0.5)

Section 3 — Lifestyle:
- `#family_history`, `#hypertension` select No/Yes
- `#physical_activity` select (Sedentary/Light/Moderate/Active)
- `#smoking` select (Never/Former/Current)
- `#diet_quality` select (Poor/Fair/Good/Excellent)
- `#sleep_hours` number (3-12, default 7)

### Task D: Create `frontend/parkinsons.html`

Same structure, `accent-parkinsons`. 22 clinical inputs + 3 demographic:

Section 1 — Fundamental Frequency: `#mdvp_fo` (80-300), `#mdvp_fhi` (100-600), `#mdvp_flo` (60-250)
Section 2 — Jitter: `#mdvp_jitter_percent`, `#mdvp_jitter_abs`, `#mdvp_rap`, `#mdvp_ppq`, `#jitter_ddp`
Section 3 — Shimmer: `#mdvp_shimmer`, `#mdvp_shimmer_db`, `#shimmer_apq3`, `#shimmer_apq5`, `#mdvp_apq`, `#shimmer_dda`
Section 4 — Harmonicity: `#nhr`, `#hnr`
Section 5 — Nonlinear: `#rpde`, `#dfa`, `#spread1`, `#spread2`, `#d2`, `#ppe`
Section 6 — Additional: `#age`, `#sex`, `#family_history`

> All input `id` attributes must match the field names expected by the JS fetch payload.

### Success Criteria
- [ ] All three pages load without JS console errors
- [ ] Forms show all inputs matching original Streamlit forms
- [ ] Result section hidden on load
- [ ] Pages use global.css navbar, footer, modals

---

## Plan 1.3 — Assessment Page JavaScript
**Wave 1 | New files: `frontend/js/heart.js`, `frontend/js/diabetes.js`, `frontend/js/parkinsons.js`**

### Objective
Write JS for each page: read form values → POST to API → show loading → render risk meter + badge + AI summary.

### Task A: Create `frontend/js/heart.js`

```javascript
const API_BASE = '';  // empty = same origin (works local + deployed)

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
      method: 'POST', headers, body: JSON.stringify(payload)
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
```

Create `diabetes.js` and `parkinsons.js` with the same pattern:
- Same `API_BASE`, `renderResult`, `renderMarkdown` functions
- `diabetes.js` reads all diabetes form field IDs, POSTs to `/api/predict/diabetes`
- `parkinsons.js` reads all 22 float fields + 3 demographic fields, POSTs to `/api/predict/parkinsons`

> **AVOID:** hardcoding `http://localhost:8000` — use empty string `''` as API_BASE
> **USE:** `hAlert()` from global.js for errors (not native `alert()`)
> **AVOID:** page reload on submit — result should render in-place below the form

### Success Criteria
- [ ] Submit triggers fetch to correct endpoint
- [ ] Loading overlay shows during fetch
- [ ] Risk arrow positions correctly at `risk_pct`%
- [ ] AI summary renders with basic formatting
- [ ] `hAlert()` shown on errors

---

## Plan 1.4 — Wiring: product.html + global.js Cleanup
**Wave 2 | Files: `frontend/product.html`, `frontend/js/global.js`**

### Objective
Replace all `localhost:850X` hrefs in product.html with links to the new HTML pages. Remove Streamlit URL manipulation from global.js.

### Task A: Update card buttons in `frontend/product.html`

Change ONLY the `href` on `.card-btn` anchors:
- Heart card (line 59): `href="http://localhost:8501"` → `href="heart.html"`, remove `target="_blank"`
- Parkinson's card (line 71): `href="http://localhost:8503"` → `href="parkinsons.html"`, remove `target="_blank"`
- Diabetes card (line 83): `href="http://localhost:8502"` → `href="diabetes.html"`, remove `target="_blank"`
- Bot card (line 92): leave unchanged (bot migration is out of scope)

### Task B: Remove Streamlit URL block from `frontend/js/global.js`

In `updateLanguage()` at lines 110-130, remove the entire forEach block:
```javascript
// REMOVE THIS ENTIRE BLOCK:
document.querySelectorAll('a[href^="http://localhost"]').forEach(link => {
  const url = new URL(link.href);
  url.searchParams.set('lang', lang);
  ...
  link.href = url.toString();
});
```

The new pages read lang from localStorage directly — no URL manipulation needed.

### Task C: Update `backend/requirements.txt`

Remove:
- `streamlit`
- `fpdf2` (PDF download was Streamlit-only; not used in new HTML pages)

> Check `backend/routes/bot.py` first — if it imports fpdf2, keep it

### Success Criteria
- [ ] "Try Now" on Heart/Diabetes/Parkinson's cards navigate to HTML pages (no ports)
- [ ] No `localhost:850X` hrefs remain in product.html
- [ ] global.js no longer has Streamlit URL manipulation block
- [ ] requirements.txt does not list `streamlit`

---

## Plan 1.5 — Chatbot: bot.py → bot.html
**Wave 1 | Files: `backend/main.py`, `frontend/bot.html`, `frontend/js/bot.js`**

### Objective
Replace the Streamlit chatbot on port 8504 with a full-page native chat interface.
The backend gets a `POST /api/chat` endpoint. The frontend gets `bot.html` with a
premium chat bubble UI — typing indicator, markdown rendering, persistent session
history (client-side), and full Marathi support.

### Key facts extracted from `backend/routes/bot.py`
- System prompt (English): triage expert for Heart/Diabetes/Parkinson's, no redirect links, always adds medical disclaimer
- System prompt (Marathi): same but in Marathi — BUT currently references `localhost:8501/8502/8503` — **fix these to relative page links**
- Welcome message: language-aware greeting stored as first message
- API: uses `call_openai_api()` util (OpenRouter) — same as other routes
- Logs each interaction: `log_prediction(email, "Medical Bot", user_input, "Responded")`
- No PDF, no model files — pure chat

### Task A: Add `POST /api/chat` endpoint to `backend/main.py`

Add Pydantic model:
```python
class ChatMessage(BaseModel):
    role: str        # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    messages: list[ChatMessage]   # full conversation history
    lang: str = "en"
```

Add endpoint `POST /api/chat`:
1. Pick system prompt based on `lang`:
   - `en`: the full English system prompt from `bot.py` lines 25-36
   - `mr`: the Marathi system prompt from `bot.py` lines 46-56
     **Fix:** replace `http://localhost:8501/8502/8503` with `heart.html`, `diabetes.html`, `parkinsons.html`
2. Append `" If the user asks a non-medical question, say it's not medical related."` to both
3. Call `_get_ai_summary()` helper (already added in Plan 1.1) with the full messages list
4. `log_prediction(email_from_auth_header, "Medical Bot", last_user_message, "Responded")`
5. Return `{reply: str, lang: str}`

> **AVOID:** streaming (keep it simple — return full reply)
> **USE:** same `_get_ai_summary` helper already created in Plan 1.1

**Verify:**
```bash
curl -s -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"What are signs of diabetes?"}],"lang":"en"}'
# Expected: {"reply": "...", "lang": "en"}
```

### Task B: Create `frontend/bot.html`

Full-page chat UI matching the Navy/Gold theme. Structure:
1. `<head>`: title, `global.css`, Google Fonts (Outfit), `translations.js`
2. Navbar: copy from `product.html` (no active link)
3. Loading overlay (same as assess pages)
4. Chat layout — two-panel feel:
   ```
   .chat-page-wrap
     .chat-sidebar (hidden on mobile)
       — Title: "🤖 Medical AI Bot"
       — Subtitle: "Ask about heart health, diabetes, Parkinson's"
       — Disclaimer text
       — [Clear Chat] button
     .chat-main
       .chat-header (Navy bar with bot avatar + name + status dot)
       .chat-window#chatWindow  ← messages render here
       .chat-input-bar
         <textarea id="chatInput" rows=1>
         <button id="sendBtn">Send ➤</button>
   ```
   CSS rules:
   - `.chat-page-wrap`: flex row, height calc(100vh - 60px), margin-top 60px
   - `.chat-sidebar`: width 280px, background #1a1f3a, color white, padding 24px
   - `.chat-main`: flex 1, display flex, flex-direction column
   - `.chat-window`: flex 1, overflow-y auto, padding 20px, background #f4f6fb
   - `.message-bubble`: max-width 70%, border-radius 18px, padding 12px 18px, margin 6px 0
     - `.from-user`: align-self flex-end, background #1a1f3a, color white, border-radius 18px 18px 4px 18px
     - `.from-bot`: align-self flex-start, background white, color #333, border-radius 18px 18px 18px 4px, box-shadow 0 2px 8px rgba(0,0,0,0.1)
   - `.typing-bubble`: same as `.from-bot` but shows three animated dots (CSS dot bounce)
   - `.chat-input-bar`: background white, border-top 1px solid #eee, padding 16px, display flex, gap 12px
   - `#chatInput`: flex 1, border-radius 24px, border 1px solid #ddd, padding 12px 20px, resize none
   - `#sendBtn`: background #B79347, color white, border-radius 24px, padding 12px 24px, border none, font-weight bold

5. Welcome message pre-rendered as first `.from-bot` bubble:
   - English: the greeting text from bot.py line 21
   - Show in the correct language based on `localStorage.getItem('healthpredict_lang')`
6. Scripts: `global.js`, `bot.js`

### Task C: Create `frontend/js/bot.js`

```javascript
const API_BASE = '';
const messages = [];  // conversation history (role + content)

// Init: push welcome message based on lang
const lang = localStorage.getItem('healthpredict_lang') || 'en';
const welcome = lang === 'mr'
  ? '👋 नमस्कार! मी हृदय आरोग्य, मधुमेह, पार्किन्सन रोग...'
  : '👋 Hello! I can provide information about heart health, diabetes...';
messages.push({ role: 'assistant', content: welcome });
// (welcome bubble is already in HTML, no need to render again)

async function sendMessage() {
  const input = document.getElementById('chatInput');
  const text = input.value.trim();
  if (!text) return;
  input.value = '';
  input.style.height = 'auto';

  // Render user bubble
  appendBubble('user', text);
  messages.push({ role: 'user', content: text });

  // Show typing indicator
  const typingId = showTyping();

  // Auth header
  const token = localStorage.getItem('token');
  const headers = { 'Content-Type': 'application/json' };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  try {
    const res = await fetch(`${API_BASE}/api/chat`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ messages, lang })
    });
    removeTyping(typingId);
    if (!res.ok) throw new Error(`Error ${res.status}`);
    const data = await res.json();

    // Simulate typing word-by-word (no server-side streaming needed)
    await typeOutMessage(data.reply);
    messages.push({ role: 'assistant', content: data.reply });

  } catch (err) {
    removeTyping(typingId);
    appendBubble('bot', '❌ Failed to get a response. Please try again.');
  }
}

async function typeOutMessage(text) {
  const bubble = appendBubble('bot', '');
  const words = text.split(' ');
  let displayed = '';
  for (const word of words) {
    displayed += word + ' ';
    bubble.innerHTML = renderMarkdown(displayed) + '<span class="cursor">▌</span>';
    scrollToBottom();
    await sleep(30);  // 30ms per word — mirrors original bot.py behavior
  }
  bubble.innerHTML = renderMarkdown(text);  // final clean render
}

function appendBubble(role, html) {
  const win = document.getElementById('chatWindow');
  const div = document.createElement('div');
  div.className = `message-bubble ${role === 'user' ? 'from-user' : 'from-bot'}`;
  div.innerHTML = html ? renderMarkdown(html) : '';
  win.appendChild(div);
  scrollToBottom();
  return div;
}

function showTyping() {
  const win = document.getElementById('chatWindow');
  const div = document.createElement('div');
  div.className = 'message-bubble from-bot typing-bubble';
  const id = 'typing-' + Date.now();
  div.id = id;
  div.innerHTML = '<span class="dot"></span><span class="dot"></span><span class="dot"></span>';
  win.appendChild(div);
  scrollToBottom();
  return id;
}

function removeTyping(id) {
  const el = document.getElementById(id);
  if (el) el.remove();
}

function scrollToBottom() {
  const win = document.getElementById('chatWindow');
  win.scrollTop = win.scrollHeight;
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

function renderMarkdown(text) {
  if (!text) return '';
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/^### (.*$)/gm, '<h4>$1</h4>')
    .replace(/^## (.*$)/gm, '<h3>$1</h3>')
    .replace(/^- (.*$)/gm, '<li>$1</li>')
    .replace(/(<li>.*<\/li>\n?)+/g, '<ul>$&</ul>')
    .replace(/\n\n+/g, '</p><p>')
    .replace(/\n/g, '<br>');
}

// Event listeners
document.getElementById('sendBtn').addEventListener('click', sendMessage);
document.getElementById('chatInput').addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
});

// Auto-resize textarea
document.getElementById('chatInput').addEventListener('input', function() {
  this.style.height = 'auto';
  this.style.height = Math.min(this.scrollHeight, 120) + 'px';
});

// Clear chat
document.getElementById('clearBtn')?.addEventListener('click', () => {
  messages.length = 0;
  messages.push({ role: 'assistant', content: welcome });
  const win = document.getElementById('chatWindow');
  // Keep only the first welcome bubble
  while (win.children.length > 1) win.removeChild(win.lastChild);
});
```

### Success Criteria
- [ ] `POST /api/chat` returns `{reply, lang}` in < 10s
- [ ] bot.html loads with welcome bubble in correct language
- [ ] Typing word-by-word animation plays (30ms/word)
- [ ] Conversation history sent on each message (context preserved)
- [ ] Enter key sends message, Shift+Enter adds newline
- [ ] Clear button resets chat to welcome message only
- [ ] Marathi system prompt no longer references `localhost` ports

---

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 GSD ► STREAMLIT MIGRATION PLANNED ✓ (UPDATED)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

5 plans | 2 waves | 0 new dependencies

  Wave 1 (all parallel):
  • 1.1: FastAPI Endpoints + Remove Streamlit subprocess code
  • 1.2: HTML Assessment Pages + assess.css
  • 1.3: Assessment Page JavaScript (heart.js, diabetes.js, parkinsons.js)
  • 1.5: Chatbot — POST /api/chat + bot.html + bot.js

  Wave 2 (after Wave 1):
  • 1.4: product.html links + global.js cleanup

───────────────────────────────────────────────────────
```
