import streamlit as st
import pandas as pd
import numpy as np
import os
import sys
import warnings
from dotenv import load_dotenv

# Suppress versioning and feature name warnings from scikit-learn
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", message=".*unpickle estimator.*")

# Add parent directory to path for importing utils
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import apply_common_styling, apply_button_styling, render_navbar, load_model, get_openai_client, get_model_name, call_openai_api, render_risk_meter, generate_pdf_report, get_language

# Get current language
LANG = get_language()

# ─────────────── Localization Dictionary for Parkinson's App ─────────────── #
LABELS = {
    "en": {
        "title": "🧠 Parkinson's Disease Assessment",
        "subtitle": "### Voice analysis for Parkinson's disease detection",
        "description": "This assessment uses **22 voice measurements** to evaluate Parkinson's disease risk. These measurements analyze various aspects of voice quality, pitch variation, and vocal stability.",
        "section1": "#### 🎵 Fundamental Frequency Measures",
        "sec1_desc": "*Measurements of vocal pitch and frequency range*",
        "mdvp_fo": "Average Vocal Frequency (Hz)", "fo_help": "Average vocal fundamental frequency",
        "mdvp_fhi": "Maximum Vocal Frequency (Hz)", "fhi_help": "Maximum vocal fundamental frequency",
        "mdvp_flo": "Minimum Vocal Frequency (Hz)", "flo_help": "Minimum vocal fundamental frequency",
        "section2": "#### 📊 Jitter Measures",
        "sec2_desc": "*Measures of frequency variation (vocal instability)*",
        "jitter_pct": "Jitter (%)", "jitter_help": "Percentage variation in frequency",
        "jitter_abs": "Jitter (Absolute)", "abs_help": "Absolute jitter in microseconds",
        "rap": "RAP", "rap_help": "Relative Amplitude Perturbation",
        "ppq": "PPQ", "ppq_help": "Five-point Period Perturbation Quotient",
        "ddp": "Jitter DDP", "ddp_help": "Average absolute difference of differences between cycles",
        "section3": "#### 🔊 Shimmer Measures",
        "sec3_desc": "*Measures of amplitude variation (voice strength variation)*",
        "shimmer": "Shimmer", "shimmer_help": "Local shimmer",
        "shimmer_db": "Shimmer (dB)", "db_help": "Shimmer in decibels",
        "apq3": "APQ3", "apq3_help": "Three-point Amplitude Perturbation Quotient",
        "apq5": "APQ5", "apq5_help": "Five-point Amplitude Perturbation Quotient",
        "apq": "MDVP APQ", "apq_help": "11-point Amplitude Perturbation Quotient",
        "dda": "Shimmer DDA", "dda_help": "Average absolute differences between amplitudes",
        "section4": "#### 🎼 Harmonicity & Noise Measures",
        "sec4_desc": "*Measures of voice quality and breathiness*",
        "nhr": "Noise-to-Harmonics Ratio", "nhr_help": "Ratio of noise to tonal components",
        "hnr": "Harmonics-to-Noise Ratio", "hnr_help": "Ratio of tonal to noise components",
        "section5": "#### 📈 Nonlinear Dynamical Complexity Measures",
        "sec5_desc": "*Advanced measures of voice pattern complexity*",
        "rpde": "RPDE", "rpde_help": "Recurrence Period Density Entropy",
        "dfa": "DFA", "dfa_help": "Detrended Fluctuation Analysis",
        "spread1": "Spread 1", "spread1_help": "Nonlinear measure of fundamental frequency variation",
        "spread2": "Spread 2", "spread2_help": "Nonlinear measure of fundamental frequency variation",
        "d2": "D2 (Correlation Dimension)", "d2_help": "Correlation dimension",
        "ppe": "PPE", "ppe_help": "Pitch Period Entropy",
        "section6": "#### 📋 Additional Information",
        "age": "Age", "age_help": "Patient's age in years",
        "sex": "Sex", "sex_help": "Biological sex",
        "family": "Family History of Parkinson's", "family_help": "Family history of Parkinson's disease",
        "submit_btn": "🔍 Assess Parkinson's Risk",
        "analyzing": "🔄 Analyzing voice metrics...",
        "completing": "✅ Assessment Complete!",
        "summary_header": "### 📋 Your Parkinson's Risk Assessment:",
        "prompt_intro": "You are a medical AI assistant specializing in Parkinson's disease. Based on the following voice analysis metrics and AI model prediction, provide a comprehensive Parkinson's disease risk assessment in English:",
        "about_title": "ℹ️ **About Voice Analysis for Parkinson's Detection:**",
        "about_desc": "Parkinson's disease often affects voice production, causing subtle changes in pitch, volume, and quality. These 22 measurements can detect early vocal changes.",
        "high_risk": "HIGH RISK", "mod_risk": "MODERATE RISK", "low_risk": "LOW RISK",
        "prob_text": "probability of Parkinson's disease"
    },
    "mr": {
        "title": "🧠 पार्किन्सन रोग जोखीम मूल्यांकन",
        "subtitle": "### पार्किन्सन रोग शोधण्यासाठी आवाज विश्लेषण",
        "description": "हे मूल्यांकन पार्किन्सन रोगाच्या जोखमीचे मूल्यांकन करण्यासाठी **२२ आवाज मोजमापांचा** वापर करते. ही मोजमापे आवाजाची गुणवत्ता आणि स्थिरता यांचे विश्लेषण करतात.",
        "section1": "#### 🎵 मूलभूत वारंवारता मोजमाप",
        "sec1_desc": "*स्वराची खेळपट्टी आणि वारंवारता श्रेणीचे मोजमाप*",
        "mdvp_fo": "सरासरी आवाज वारंवारता (Hz)", "fo_help": "सरासरी आवाज मूलभूत वारंवारता",
        "mdvp_fhi": "कमाल आवाज वारंवारता (Hz)", "fhi_help": "कमाल आवाज मूलभूत वारंवारता",
        "mdvp_flo": "किमान आवाज वारंवारता (Hz)", "flo_help": "किमान आवाज मूलभूत वारंवारता",
        "section2": "#### 📊 जिटर (Jitter) मोजमाप",
        "sec2_desc": "*वारंवारता बदल (आवाजाची अस्थिरता) मोजमाप*",
        "jitter_pct": "जिटर (%)", "jitter_help": "वारंवारता मधील टक्केवारी बदल",
        "jitter_abs": "जिटर (Absolute)", "abs_help": "मायक्रोसेकंदमध्ये जिटर",
        "rap": "आरएपी (RAP)", "rap_help": "सापेक्ष मोठेपणा बदल",
        "ppq": "पीपीक्यू (PPQ)", "ppq_help": "पाच-पॉइंट पीरियड बदल",
        "ddp": "जिटर डीडीपी (DDP)", "ddp_help": "सरासरी पूर्ण फरक",
        "section3": "#### 🔊 शिमर (Shimmer) मोजमाप",
        "sec3_desc": "*आवाजाच्या ताकदीतील बदलाचे मोजमाप*",
        "shimmer": "शिमर (Shimmer)", "shimmer_help": "स्थानिक शिमर",
        "shimmer_db": "शिमर (dB)", "db_help": "डेसिबलमध्ये शिमर",
        "apq3": "APQ3", "apq3_help": "तीन-पॉइंट मोठेपणा बदल",
        "apq5": "APQ5", "apq5_help": "पाच-पॉइंट मोठेपणा बदल",
        "apq": "MDVP APQ", "apq_help": "११-पॉइंट मोठेपणा बदल",
        "dda": "शिमर डीडीए (DDA)", "dda_help": "मोठेपणामधील सरासरी पूर्ण फरक",
        "section4": "#### 🎼 सुसंवाद आणि आवाज मोजमाप",
        "sec4_desc": "*आवाजाची गुणवत्ता आणि श्वास कोंडणे मोजमाप*",
        "nhr": "नॉईज-टू-हार्मोनिक्स प्रमाण (NHR)", "nhr_help": "आणि टोनल घटकांचे प्रमाण",
        "hnr": "हार्मोनिक्स-टू-नॉईज प्रमाण (HNR)", "hnr_help": "टोनल आणि आवाज घटकांचे प्रमाण",
        "section5": "#### 📈 नॉन-लिनियर गुंतागुंत मोजमाप",
        "sec5_desc": "*आवाजाच्या नमुन्याच्या गुंतागुंतीचे प्रगत मोजमाप*",
        "rpde": "आरपीडीई (RPDE)", "rpde_help": "रिकरन्स पीरियड डेन्सिटी एन्ट्रोपी",
        "dfa": "डीएफए (DFA)", "dfa_help": "डेट्रेंडेड चढउतार विश्लेषण",
        "spread1": "स्प्रेड १ (Spread 1)", "spread1_help": "वारंवारता बदलाचे नॉन-लिनियर मोजमाप",
        "spread2": "स्प्रेड २ (Spread 2)", "spread2_help": "वारंवारता बदलाचे नॉन-लिनियर मोजमाप",
        "d2": "डी२ (D2 - सहसंबंध परिमाण)", "d2_help": "सहसंबंध परिमाण",
        "ppe": "पीपीई (PPE)", "ppe_help": "पिच पीरियड एन्ट्रोपी",
        "section6": "#### 📋 अतिरिक्त माहिती",
        "age": "वय", "age_help": "रुग्णाचे वय (वर्षे)",
        "sex": "लिंग", "sex_help": "जैविक लिंग",
        "family": "पार्किन्सनचा कौटुंबिक इतिहास", "family_help": "कुटुंबात कोणाला पार्किन्सन आहे का?",
        "submit_btn": "🔍 पार्किन्सन जोखीम तपासा",
        "analyzing": "🔄 आवाज मेट्रिक्सचे विश्लेषण करत आहे...",
        "completing": "✅ मूल्यांकन पूर्ण झाले!",
        "summary_header": "### 📋 तुमचे पार्किन्सन जोखीम मूल्यांकन:",
        "prompt_intro": "तुम्ही पार्किन्सन रोगामध्ये तज्ञ असलेले वैद्यकीय एआय सहाय्यक आहात. खालील आवाज विश्लेषण मेट्रिक्स आणि एआय मॉडेल अंदाजावर आधारित, कृपया मराठी भाषेत सर्वसमावेशक पार्किन्सन रोग जोखीम मूल्यांकन प्रदान करा:",
        "about_title": "ℹ️ **पार्किन्सन शोधण्यासाठी आवाज विश्लेषणाबद्दल:**",
        "about_desc": "पार्किन्सन रोगाचा वारंवार आवाजावर परिणाम होतो, ज्यामुळे आवाजाची खेळपट्टी, आवाज आणि गुणवत्तेत सूक्ष्म बदल होतात. ही २२ मोजमापे सुरुवातीचे बदल शोधू शकतात.",
        "high_risk": "उच्च धोका", "mod_risk": "मध्यम धोका", "low_risk": "कमी धोका",
        "prob_text": "पार्किन्सन रोगाची शक्यता"
    }
}

def L(key):
    return LABELS.get(LANG, LABELS["en"]).get(key, key)

# ──────────────⚙ Page Config────────────────────────── #
st.set_page_config(layout="wide", page_title=f"HealthPredict - {L('title')}")

# ───────────────🔐 API Setup ─────────────── #
try:
    client = get_openai_client()
    openrouter_model = get_model_name()
except ValueError as e:
    st.error(f"Configuration Error: {str(e)}. Please set OPENROUTER_API_KEY in environment.")
    st.stop()

# ───── Load Pre-trained Model and Scaler ───── #
parkinsons_model = load_model("backend/parkinsons_model.sav")
try:
    import pickle
    parkinsons_scaler = pickle.load(open("backend/parkinsons_scaler.sav", 'rb'))
except:
    parkinsons_scaler = None
    st.warning("⚠️ Scaler not found. Predictions may be less accurate.")

# ──────────────🎨 Custom Styling────────────────────────── #
apply_common_styling()
apply_button_styling("parkinsons")

# ────────────── Navbar ─────────────── #
render_navbar(f"HealthPredict - {L('title')}")

st.title(L('title'))
st.markdown(L('subtitle'))
st.markdown(L('description'))
st.divider()

# ═══════════════════ SECTION 1: Fundamental Frequency Measures ═══════════════════
st.markdown(L('section1'))
st.markdown(L('sec1_desc'))
col1, col2, col3 = st.columns(3)

with col1:
    mdvp_fo = st.number_input(L('mdvp_fo'), 
                             min_value=80.0, max_value=300.0, value=150.0, step=0.01,
                             help=L('fo_help'))

with col2:
    mdvp_fhi = st.number_input("Maximum Vocal Frequency (Hz)", 
                              min_value=100.0, max_value=600.0, value=200.0, step=0.01,
                              help="MDVP:Fhi(Hz) - Maximum vocal fundamental frequency")

with col3:
    mdvp_flo = st.number_input("Minimum Vocal Frequency (Hz)", 
                              min_value=60.0, max_value=250.0, value=100.0, step=0.01,
                              help="MDVP:Flo(Hz) - Minimum vocal fundamental frequency")

st.divider()

# ═══════════════════ SECTION 2: Jitter Measures ═══════════════════
st.markdown(L('section2'))
st.markdown(L('sec2_desc'))
col4, col5, col6, col7 = st.columns(4)

with col4:
    mdvp_jitter_percent = st.number_input(L('jitter_pct'), 
                                         min_value=0.0, max_value=0.1, value=0.005, step=0.00001, format="%.5f",
                                         help=L('jitter_help'))

with col5:
    mdvp_jitter_abs = st.number_input(L('jitter_abs'), 
                                     min_value=0.0, max_value=0.001, value=0.00005, step=0.000001, format="%.6f",
                                     help=L('abs_help'))

with col6:
    mdvp_rap = st.number_input(L('rap'), 
                               min_value=0.0, max_value=0.05, value=0.003, step=0.00001, format="%.5f",
                               help=L('rap_help'))

with col7:
    mdvp_ppq = st.number_input(L('ppq'), 
                               min_value=0.0, max_value=0.05, value=0.003, step=0.00001, format="%.5f",
                               help=L('ppq_help'))

col8, = st.columns(1)
with col8:
    jitter_ddp = st.number_input(L('ddp'), 
                                min_value=0.0, max_value=0.15, value=0.01, step=0.00001, format="%.5f",
                                help=L('ddp_help'))

st.divider()

# ═══════════════════ SECTION 3: Shimmer Measures ═══════════════════
st.markdown(L('section3'))
st.markdown(L('sec3_desc'))
col9, col10, col11, col12 = st.columns(4)

with col9:
    mdvp_shimmer = st.number_input(L('shimmer'), 
                                  min_value=0.0, max_value=0.3, value=0.03, step=0.001, format="%.5f",
                                  help=L('shimmer_help'))

with col10:
    mdvp_shimmer_db = st.number_input(L('shimmer_db'), 
                                     min_value=0.0, max_value=3.0, value=0.3, step=0.01,
                                     help=L('db_help'))

with col11:
    shimmer_apq3 = st.number_input(L('apq3'), 
                                  min_value=0.0, max_value=0.15, value=0.015, step=0.001, format="%.5f",
                                  help=L('apq3_help'))

with col12:
    shimmer_apq5 = st.number_input(L('apq5'), 
                                  min_value=0.0, max_value=0.15, value=0.02, step=0.001, format="%.5f",
                                  help=L('apq5_help'))

col13, col14 = st.columns(2)
with col13:
    mdvp_apq = st.number_input(L('apq'), 
                               min_value=0.0, max_value=0.2, value=0.025, step=0.001, format="%.5f",
                               help=L('apq_help'))

with col14:
    shimmer_dda = st.number_input(L('dda'), 
                                 min_value=0.0, max_value=0.5, value=0.05, step=0.001, format="%.5f",
                                 help=L('dda_help'))

st.divider()

# ═══════════════════ SECTION 4: Harmonicity Measures ═══════════════════
st.markdown(L('section4'))
st.markdown(L('sec4_desc'))
col15, col16 = st.columns(2)

with col15:
    nhr = st.number_input(L('nhr'), 
                         min_value=0.0, max_value=0.5, value=0.02, step=0.001, format="%.5f",
                         help=L('nhr_help'))

with col16:
    hnr = st.number_input(L('hnr'), 
                         min_value=0.0, max_value=40.0, value=22.0, step=0.1,
                         help=L('hnr_help'))

st.divider()

# ═══════════════════ SECTION 5: Nonlinear Measures ═══════════════════
st.markdown(L('section5'))
st.markdown(L('sec5_desc'))
col17, col18, col19, col20 = st.columns(4)

with col17:
    rpde = st.number_input(L('rpde'), 
                          min_value=0.0, max_value=1.0, value=0.5, step=0.001, format="%.6f",
                          help=L('rpde_help'))

with col18:
    dfa = st.number_input(L('dfa'), 
                         min_value=0.0, max_value=1.0, value=0.7, step=0.001, format="%.6f",
                         help=L('dfa_help'))

with col19:
    spread1 = st.number_input(L('spread1'), 
                             min_value=-10.0, max_value=0.0, value=-5.0, step=0.001, format="%.6f",
                             help=L('spread1_help'))

with col20:
    spread2 = st.number_input(L('spread2'), 
                             min_value=0.0, max_value=1.0, value=0.2, step=0.001, format="%.6f",
                             help=L('spread2_help'))

col21, col22 = st.columns(2)
with col21:
    d2 = st.number_input(L('d2'), 
                        min_value=0.0, max_value=5.0, value=2.5, step=0.001, format="%.6f",
                        help=L('d2_help'))

with col22:
    ppe = st.number_input(L('ppe'), 
                         min_value=0.0, max_value=1.0, value=0.2, step=0.001, format="%.6f",
                         help=L('ppe_help'))

st.divider()

# ═══════════════════ SECTION 6: Additional Information ═══════════════════
st.markdown(L('section6'))
col23, col24, col25 = st.columns(3)

with col23:
    age = st.number_input(L('age'), 
                         min_value=18, max_value=100, value=60,
                         help=L('age_help'))

with col24:
    sex_display = st.selectbox(L('sex'), ["पुरुष", "स्त्री"] if LANG == "mr" else ["Male", "Female"], help=L('sex_help'))
    sex = "Male" if (sex_display == "Male" or sex_display == "पुरुष") else "Female"

with col25:
    family_display = st.selectbox(L('family'), ["नाही", "हो"] if LANG == "mr" else ["No", "Yes"], help=L('family_help'))
    family_history = "Yes" if (family_display == "हो" or family_display == "Yes") else "No"

st.divider()

# Submit button
if st.button(L('submit_btn'), type="primary", use_container_width=True):
    # MDVP:Fo(Hz), MDVP:Fhi(Hz), MDVP:Flo(Hz), MDVP:Jitter(%), MDVP:Jitter(Abs), 
    # MDVP:RAP, MDVP:PPQ, Jitter:DDP, MDVP:Shimmer, MDVP:Shimmer(dB), 
    # Shimmer:APQ3, Shimmer:APQ5, MDVP:APQ, Shimmer:DDA, NHR, HNR, 
    # RPDE, DFA, spread1, spread2, D2, PPE
    
    feature_names = ['MDVP:Fo(Hz)', 'MDVP:Fhi(Hz)', 'MDVP:Flo(Hz)', 'MDVP:Jitter(%)', 'MDVP:Jitter(Abs)', 
                     'MDVP:RAP', 'MDVP:PPQ', 'Jitter:DDP', 'MDVP:Shimmer', 'MDVP:Shimmer(dB)', 
                     'Shimmer:APQ3', 'Shimmer:APQ5', 'MDVP:APQ', 'Shimmer:DDA', 'NHR', 'HNR', 
                     'RPDE', 'DFA', 'spread1', 'spread2', 'D2', 'PPE']
    
    features = pd.DataFrame([[mdvp_fo, mdvp_fhi, mdvp_flo, mdvp_jitter_percent, mdvp_jitter_abs,
                          mdvp_rap, mdvp_ppq, jitter_ddp, mdvp_shimmer, mdvp_shimmer_db,
                          shimmer_apq3, shimmer_apq5, mdvp_apq, shimmer_dda, nhr, hnr,
                          rpde, dfa, spread1, spread2, d2, ppe]], columns=feature_names)
    
    # Apply scaling if scaler is available
    if parkinsons_scaler is not None:
        features_scaled = parkinsons_scaler.transform(features)
    else:
        features_scaled = features
    
    # Get model prediction
    try:
        prediction = parkinsons_model.predict(features_scaled)[0]
        prediction_proba = parkinsons_model.predict_proba(features_scaled)[0]
        risk_percentage = prediction_proba[1] * 100 if len(prediction_proba) > 1 else 0
    except Exception as e:
        st.error(f"❌ Error in model prediction: {e}")
        prediction = None
        risk_percentage = 0
    
    # Create assessment prompt
    assessment_prompt = f"""
{L('prompt_intro')}

MODEL PREDICTION RESULT:
- Risk Percentage: {risk_percentage:.1f}%
- Risk Classification: {L('high_risk') if risk_percentage > 70 else L('mod_risk') if risk_percentage > 40 else L('low_risk')}

Patient Information:
- Age: {age} years
- Sex: {sex}
- Family History: {family_history}

Voice Analysis Metrics:
Frequency Measures:
- Average Vocal Frequency: {mdvp_fo:.2f} Hz
- Max Frequency: {mdvp_fhi:.2f} Hz
- Min Frequency: {mdvp_flo:.2f} Hz

Jitter (Frequency Variation):
- Jitter %: {mdvp_jitter_percent:.5f}
- RAP: {mdvp_rap:.5f}
- PPQ: {mdvp_ppq:.5f}

Shimmer (Amplitude Variation):
- Shimmer: {mdvp_shimmer:.5f}
- Shimmer dB: {mdvp_shimmer_db:.3f}

Voice Quality:
- NHR: {nhr:.5f}
- HNR: {hnr:.2f}

Nonlinear Complexity:
- RPDE: {rpde:.6f}
- DFA: {dfa:.6f}
- D2: {d2:.6f}
- PPE: {ppe:.6f}

Please provide:
1. Risk Level Assessment (based on the model's {risk_percentage:.1f}% prediction)
2. Voice Characteristics Analysis (what the measurements indicate)
3. Key Indicators Present
4. Recommendations for Further Evaluation
5. When to Consult a Neurologist

Important: This is NOT a medical diagnosis. Voice analysis is a screening tool only. Always recommend consulting with a qualified neurologist or movement disorder specialist for proper evaluation.
Keep the response clear, actionable, and between 400-600 words.
"""
    
    with st.spinner(L('analyzing')):
        assessment = call_openai_api(client, assessment_prompt, openrouter_model, timeout=30)
        if assessment:
            st.session_state.assessment = assessment
            st.session_state.risk_percentage = risk_percentage
            
            # LOG PREDICTION TO DATABASE
            try:
                from database import log_prediction
                from utils import get_email
                email = get_email()
                # Log full features for retraining pipeline
                log_prediction(email, "Parkinson's", features.to_dict(orient='records')[0], f"{risk_percentage:.1f}% Risk")
            except Exception as log_err:
                pass
                
            st.success(L('completing'))
        else:
            st.error("❌ Failed to generate assessment.")

# Display assessment results
if st.session_state.get("assessment"):
    risk_pct = st.session_state.get("risk_percentage", 0)
    risk_class = L('high_risk') if risk_pct > 70 else L('mod_risk') if risk_pct > 40 else L('low_risk')
    icon = "⚠️" if risk_pct > 40 else "✅"
    
    st.markdown(f"{icon} **{risk_class}**: {risk_pct:.1f}% {L('prob_text')}")
    
    render_risk_meter(risk_pct)
    
    pdf_bytes = generate_pdf_report(
        content=st.session_state.assessment,
        risk_pct=risk_pct,
        title=L('title'),
        patient_info=f"Age: {age}, Sex: {sex}"
    )

    st.markdown(L('summary_header'))
    st.write(st.session_state.assessment)
    
    st.download_button(
        label=f"📥 {L('title')} (PDF)",
        data=pdf_bytes,
        file_name="parkinsons_risk_assessment.pdf",
        mime="application/pdf"
    )

# Information box
st.info(f"""
{L('about_title')}
{L('about_desc')}
""")

# ───────────── Sticky Footer ───────────── #
footer_text = "HealthPredict | Medical Risk Assessment AI - Not a substitute for professional medical advice"
if LANG == "mr":
    footer_text = "HealthPredict | वैद्यकीय जोखीम मूल्यांकन AI - व्यावसायिक वैद्यकीय सल्ल्याचा पर्याय नाही"

st.markdown(f"""
    <style>
    .footer {{
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #06061C;
        color: gold;
        text-align: center;
        padding: 15px 0;
        font-size: 14px;
        z-index: 9999;
    }}
    </style>
    <div class="footer">
        &copy; 2026 {footer_text}
    </div>
""", unsafe_allow_html=True)
