import streamlit as st
import numpy as np
import os
import sys
from dotenv import load_dotenv

# Add parent directory to path for importing utils
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import apply_common_styling, apply_button_styling, render_navbar, load_model, get_openai_client, get_model_name, call_openai_api

# Load environment variables
load_dotenv()

# ──────────────⚙ Page Config────────────────────────── #
st.set_page_config(layout="wide", page_title="HealthPredict - Parkinson's Disease Assessment")

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
render_navbar("HealthPredict - Parkinson's Risk")

st.title("🧠 Parkinson's Disease Assessment")
st.markdown("### Voice analysis for Parkinson's disease detection")
st.markdown("""
This assessment uses **22 voice measurements** to evaluate Parkinson's disease risk. 
These measurements analyze various aspects of voice quality, pitch variation, and vocal stability.
""")
st.divider()

# ═══════════════════ SECTION 1: Fundamental Frequency Measures ═══════════════════
st.markdown("#### 🎵 Fundamental Frequency Measures")
st.markdown("*Measurements of vocal pitch and frequency range*")
col1, col2, col3 = st.columns(3)

with col1:
    mdvp_fo = st.number_input("Average Vocal Frequency (Hz)", 
                             min_value=80.0, max_value=300.0, value=150.0, step=0.01,
                             help="MDVP:Fo(Hz) - Average vocal fundamental frequency")

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
st.markdown("#### 📊 Jitter Measures")
st.markdown("*Measures of frequency variation (vocal instability)*")
col4, col5, col6, col7 = st.columns(4)

with col4:
    mdvp_jitter_percent = st.number_input("Jitter (%)", 
                                         min_value=0.0, max_value=0.1, value=0.005, step=0.00001, format="%.5f",
                                         help="MDVP:Jitter(%) - Percentage variation in frequency")

with col5:
    mdvp_jitter_abs = st.number_input("Jitter (Absolute)", 
                                     min_value=0.0, max_value=0.001, value=0.00005, step=0.000001, format="%.6f",
                                     help="MDVP:Jitter(Abs) - Absolute jitter in microseconds")

with col6:
    mdvp_rap = st.number_input("RAP", 
                              min_value=0.0, max_value=0.05, value=0.003, step=0.00001, format="%.5f",
                              help="MDVP:RAP - Relative Amplitude Perturbation")

with col7:
    mdvp_ppq = st.number_input("PPQ", 
                              min_value=0.0, max_value=0.05, value=0.003, step=0.00001, format="%.5f",
                              help="MDVP:PPQ - Five-point Period Perturbation Quotient")

col8, = st.columns(1)
with col8:
    jitter_ddp = st.number_input("Jitter DDP", 
                                min_value=0.0, max_value=0.15, value=0.01, step=0.00001, format="%.5f",
                                help="Jitter:DDP - Average absolute difference of differences between cycles")

st.divider()

# ═══════════════════ SECTION 3: Shimmer Measures ═══════════════════
st.markdown("#### 🔊 Shimmer Measures")
st.markdown("*Measures of amplitude variation (voice strength variation)*")
col9, col10, col11, col12 = st.columns(4)

with col9:
    mdvp_shimmer = st.number_input("Shimmer", 
                                  min_value=0.0, max_value=0.3, value=0.03, step=0.001, format="%.5f",
                                  help="MDVP:Shimmer - Local shimmer")

with col10:
    mdvp_shimmer_db = st.number_input("Shimmer (dB)", 
                                     min_value=0.0, max_value=3.0, value=0.3, step=0.01,
                                     help="MDVP:Shimmer(dB) - Shimmer in decibels")

with col11:
    shimmer_apq3 = st.number_input("APQ3", 
                                  min_value=0.0, max_value=0.15, value=0.015, step=0.001, format="%.5f",
                                  help="Shimmer:APQ3 - Three-point Amplitude Perturbation Quotient")

with col12:
    shimmer_apq5 = st.number_input("APQ5", 
                                  min_value=0.0, max_value=0.15, value=0.02, step=0.001, format="%.5f",
                                  help="Shimmer:APQ5 - Five-point Amplitude Perturbation Quotient")

col13, col14 = st.columns(2)
with col13:
    mdvp_apq = st.number_input("MDVP APQ", 
                              min_value=0.0, max_value=0.2, value=0.025, step=0.001, format="%.5f",
                              help="MDVP:APQ - 11-point Amplitude Perturbation Quotient")

with col14:
    shimmer_dda = st.number_input("Shimmer DDA", 
                                 min_value=0.0, max_value=0.5, value=0.05, step=0.001, format="%.5f",
                                 help="Shimmer:DDA - Average absolute differences between amplitudes")

st.divider()

# ═══════════════════ SECTION 4: Harmonicity Measures ═══════════════════
st.markdown("#### 🎼 Harmonicity & Noise Measures")
st.markdown("*Measures of voice quality and breathiness*")
col15, col16 = st.columns(2)

with col15:
    nhr = st.number_input("Noise-to-Harmonics Ratio", 
                         min_value=0.0, max_value=0.5, value=0.02, step=0.001, format="%.5f",
                         help="NHR - Ratio of noise to tonal components")

with col16:
    hnr = st.number_input("Harmonics-to-Noise Ratio", 
                         min_value=0.0, max_value=40.0, value=22.0, step=0.1,
                         help="HNR - Ratio of tonal to noise components")

st.divider()

# ═══════════════════ SECTION 5: Nonlinear Measures ═══════════════════
st.markdown("#### 📈 Nonlinear Dynamical Complexity Measures")
st.markdown("*Advanced measures of voice pattern complexity*")
col17, col18, col19, col20 = st.columns(4)

with col17:
    rpde = st.number_input("RPDE", 
                          min_value=0.0, max_value=1.0, value=0.5, step=0.001, format="%.6f",
                          help="RPDE - Recurrence Period Density Entropy")

with col18:
    dfa = st.number_input("DFA", 
                         min_value=0.0, max_value=1.0, value=0.7, step=0.001, format="%.6f",
                         help="DFA - Detrended Fluctuation Analysis")

with col19:
    spread1 = st.number_input("Spread 1", 
                             min_value=-10.0, max_value=0.0, value=-5.0, step=0.001, format="%.6f",
                             help="spread1 - Nonlinear measure of fundamental frequency variation")

with col20:
    spread2 = st.number_input("Spread 2", 
                             min_value=0.0, max_value=1.0, value=0.2, step=0.001, format="%.6f",
                             help="spread2 - Nonlinear measure of fundamental frequency variation")

col21, col22 = st.columns(2)
with col21:
    d2 = st.number_input("D2 (Correlation Dimension)", 
                        min_value=0.0, max_value=5.0, value=2.5, step=0.001, format="%.6f",
                        help="D2 - Correlation dimension")

with col22:
    ppe = st.number_input("PPE", 
                         min_value=0.0, max_value=1.0, value=0.2, step=0.001, format="%.6f",
                         help="PPE - Pitch Period Entropy")

st.divider()

# ═══════════════════ SECTION 6: Additional Information ═══════════════════
st.markdown("#### 📋 Additional Information")
col23, col24, col25 = st.columns(3)

with col23:
    age = st.number_input("Age", 
                         min_value=18, max_value=100, value=60,
                         help="Patient's age in years")

with col24:
    sex = st.selectbox("Sex", ["Male", "Female"],
                      help="Biological sex")

with col25:
    family_history = st.selectbox("Family History of Parkinson's", 
                                 ["No", "Yes"],
                                 help="Family history of Parkinson's disease")

st.divider()

# Submit button
if st.button("🔍 Assess Parkinson's Risk", type="primary", use_container_width=True):
    # Dataset features (22 voice measurements):
    # MDVP:Fo(Hz), MDVP:Fhi(Hz), MDVP:Flo(Hz), MDVP:Jitter(%), MDVP:Jitter(Abs), 
    # MDVP:RAP, MDVP:PPQ, Jitter:DDP, MDVP:Shimmer, MDVP:Shimmer(dB), 
    # Shimmer:APQ3, Shimmer:APQ5, MDVP:APQ, Shimmer:DDA, NHR, HNR, 
    # RPDE, DFA, spread1, spread2, D2, PPE
    
    features = np.array([[mdvp_fo, mdvp_fhi, mdvp_flo, mdvp_jitter_percent, mdvp_jitter_abs,
                         mdvp_rap, mdvp_ppq, jitter_ddp, mdvp_shimmer, mdvp_shimmer_db,
                         shimmer_apq3, shimmer_apq5, mdvp_apq, shimmer_dda, nhr, hnr,
                         rpde, dfa, spread1, spread2, d2, ppe]])
    
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
You are a medical AI assistant specializing in Parkinson's disease. Based on the following voice analysis metrics and AI model prediction, provide a comprehensive Parkinson's disease risk assessment:

MODEL PREDICTION RESULT:
- Risk Percentage: {risk_percentage:.1f}%
- Risk Classification: {'HIGH RISK' if risk_percentage > 70 else 'MODERATE RISK' if risk_percentage > 40 else 'LOW RISK'}

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
    
    with st.spinner("🔄 Analyzing voice metrics..."):
        assessment = call_openai_api(client, assessment_prompt, openrouter_model, timeout=30)
        if assessment:
            st.session_state.assessment = assessment
            st.session_state.risk_percentage = risk_percentage
            st.success("✅ Assessment Complete!")
        else:
            st.error("❌ Failed to generate assessment. Please try again.")

# Display assessment results
if st.session_state.get("assessment"):
    # Show risk percentage in a prominent way
    risk_pct = st.session_state.get("risk_percentage", 0)
    if risk_pct > 70:
        st.error(f"⚠️ **HIGH RISK**: {risk_pct:.1f}% probability of Parkinson's disease")
    elif risk_pct > 40:
        st.warning(f"⚠️ **MODERATE RISK**: {risk_pct:.1f}% probability of Parkinson's disease")
    else:
        st.success(f"✅ **LOW RISK**: {risk_pct:.1f}% probability of Parkinson's disease")
    
    st.markdown("### 📋 Your Parkinson's Risk Assessment:")
    st.write(st.session_state.assessment)
    
    # Download button
    st.download_button(
        label="📥 Download Assessment",
        data=st.session_state.assessment,
        file_name="parkinsons_risk_assessment.txt",
        mime="text/plain"
    )

# Information box
st.info("""
ℹ️ **About Voice Analysis for Parkinson's Detection:**
Parkinson's disease often affects voice production, causing subtle changes in:
- **Pitch variation** (Jitter measures)
- **Volume variation** (Shimmer measures)  
- **Voice quality** (Harmonics measures)
- **Vocal complexity** (Nonlinear measures)

These 22 measurements can detect early vocal changes that may indicate Parkinson's disease, often before other symptoms appear.
""")

# ───────────── Sticky Footer ───────────── #
st.markdown("""
    <style>
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #06061C;
        color: gold;
        text-align: center;
        padding: 15px 0;
        font-size: 16px;
        z-index: 9999;
    }
    </style>

    <div class="footer">
        &copy; 2025 HealthPredict | Medical Risk Assessment AI - Not a substitute for professional medical advice
    </div>
""", unsafe_allow_html=True)
