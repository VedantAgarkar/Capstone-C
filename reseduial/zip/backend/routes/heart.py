import streamlit as st
import pandas as pd
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
st.set_page_config(layout="wide", page_title="HealthPredict - Heart Disease Risk Assessment")

# ───────────────🔐 API Setup ─────────────── #
try:
    client = get_openai_client()
    openrouter_model = get_model_name()
except ValueError as e:
    st.error(f"Configuration Error: {str(e)}. Please set OPENROUTER_API_KEY in environment.")
    st.stop()

# ───── Load Pre-trained Model and Scaler ───── #
heart_model = load_model("backend/heart_disease_model.sav")
try:
    import pickle
    heart_scaler = pickle.load(open("backend/heart_scaler.sav", 'rb'))
except:
    heart_scaler = None
    st.warning("⚠️ Scaler not found. Predictions may be less accurate.")

# ──────────────🎨 Custom Styling────────────────────────── #
apply_common_styling()
apply_button_styling("heart")

# ───────────────🧭 Navbar───────────────────────────── #
render_navbar(" HealthPredict - Heart Disease Risk")

st.title("❤️ Heart Disease Risk Assessment")
st.markdown("### Complete the form below for a comprehensive cardiovascular risk analysis")
st.divider()

# ═══════════════════ SECTION 1: Demographics & Basic Info ═══════════════════
st.markdown("#### 👤 Demographics & Basic Information")
col1, col2, col3 = st.columns(3)

with col1:
    age = st.number_input("Age", min_value=18, max_value=120, value=50, 
                         help="Your age in years")

with col2:
    sex = st.selectbox("Sex", ["Male", "Female"], 
                      help="Biological sex")

with col3:
    bmi = st.number_input("BMI", min_value=15.0, max_value=50.0, value=25.0, step=0.1,
                         help="Body Mass Index (weight in kg / height in m²)")

st.divider()

# ═══════════════════ SECTION 2: Clinical Measurements ═══════════════════
st.markdown("#### 🩺 Clinical Measurements")
col4, col5, col6 = st.columns(3)

with col4:
    resting_bp = st.number_input("Resting Blood Pressure", 
                                 min_value=80, max_value=200, value=120,
                                 help="Resting blood pressure in mmHg")
    
    fasting_blood_sugar = st.selectbox("Fasting Blood Sugar > 120 mg/dl?", 
                                       ["No", "Yes"],
                                       help="Is fasting blood sugar greater than 120 mg/dl?")

with col5:
    cholesterol = st.number_input("Serum Cholesterol", 
                                  min_value=100, max_value=400, value=200,
                                  help="Serum cholesterol in mg/dl")
    
    max_heart_rate = st.number_input("Maximum Heart Rate Achieved", 
                                     min_value=60, max_value=220, value=150,
                                     help="Maximum heart rate during exercise test")

with col6:
    chest_pain = st.selectbox("Chest Pain Type", 
                             ["Asymptomatic", "Non-anginal Pain", "Atypical Angina", "Typical Angina"],
                             help="Type of chest pain experienced")

st.divider()

# ═══════════════════ SECTION 3: Cardiovascular Test Results ═══════════════════
st.markdown("#### 🫀 Cardiovascular Test Results")
col7, col8, col9 = st.columns(3)

with col7:
    rest_ecg = st.selectbox("Resting ECG Results",
                           ["Normal", "ST-T Abnormality", "Left Ventricular Hypertrophy"],
                           help="Resting electrocardiographic results")
    
    exercise_induced_angina = st.selectbox("Exercise Induced Angina?", 
                                          ["No", "Yes"],
                                          help="Does exercise induce angina (chest pain)?")

with col8:
    st_depression = st.number_input("ST Depression", 
                                    min_value=0.0, max_value=10.0, value=0.0, step=0.1,
                                    help="ST depression induced by exercise relative to rest")
    
    slope = st.selectbox("Slope of Peak Exercise ST Segment", 
                        ["Upsloping", "Flat", "Downsloping"],
                        help="Slope of the peak exercise ST segment")

with col9:
    ca = st.number_input("Number of Major Vessels", 
                        min_value=0, max_value=3, value=0,
                        help="Number of major vessels (0-3) colored by fluoroscopy")
    
    thal = st.selectbox("Thalassemia", 
                       ["Normal", "Fixed Defect", "Reversible Defect"],
                       help="Thalassemia blood disorder status")

st.divider()

# ═══════════════════ SECTION 4: Medical History & Lifestyle ═══════════════════
st.markdown("#### 📋 Medical History & Lifestyle")
col10, col11, col12, col13 = st.columns(4)

with col10:
    family_history = st.selectbox("Family History", 
                                 ["No", "Yes"],
                                 help="Family history of heart disease")

with col11:
    diabetes = st.selectbox("Diabetes", 
                           ["No", "Yes"],
                           help="Do you have diabetes?")

with col12:
    hypertension = st.selectbox("Hypertension", 
                               ["No", "Yes"],
                               help="Do you have hypertension (high blood pressure)?")

with col13:
    smoking = st.selectbox("Smoking Status", 
                          ["Never", "Former", "Current"],
                          help="Current smoking status")

# Exercise frequency
exercise_frequency = st.select_slider("Exercise Frequency (per week)", 
                                     options=["None", "1-2 times", "3-4 times", "5+ times"],
                                     value="1-2 times",
                                     help="How often do you exercise per week?")

st.divider()

# Submit button
if st.button("🔍 Assess Heart Disease Risk", type="primary", use_container_width=True):
    # Prepare features for model prediction
    sex_encoded = 1 if sex == "Male" else 0
    chest_pain_encoded = {"Typical Angina": 3, "Atypical Angina": 2, "Non-anginal Pain": 1, "Asymptomatic": 0}[chest_pain]
    rest_ecg_encoded = {"Normal": 0, "ST-T Abnormality": 1, "Left Ventricular Hypertrophy": 2}[rest_ecg]
    fasting_encoded = 1 if fasting_blood_sugar == "Yes" else 0
    exercise_angina_encoded = 1 if exercise_induced_angina == "Yes" else 0
    slope_encoded = {"Upsloping": 0, "Flat": 1, "Downsloping": 2}[slope]
    thal_encoded = {"Normal": 1, "Fixed Defect": 2, "Reversible Defect": 3}[thal]
    
    # Create feature array for model (order must match training data)
    # Features: age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal
    features = np.array([[age, sex_encoded, chest_pain_encoded, resting_bp, cholesterol, 
                         fasting_encoded, rest_ecg_encoded, max_heart_rate, exercise_angina_encoded, 
                         st_depression, slope_encoded, ca, thal_encoded]])
    
    # Apply scaling if scaler is available
    if heart_scaler is not None:
        features_scaled = heart_scaler.transform(features)
    else:
        features_scaled = features
    
    # Get model prediction
    try:
        prediction = heart_model.predict(features_scaled)[0]
        prediction_proba = heart_model.predict_proba(features_scaled)[0]
        risk_percentage = prediction_proba[1] * 100 if len(prediction_proba) > 1 else 0
    except Exception as e:
        st.error(f"❌ Error in model prediction: {e}")
        prediction = None
        risk_percentage = 0
    
    # Create assessment prompt with prediction
    assessment_prompt = f"""
You are a medical AI assistant. Based on the following health metrics and AI model prediction, provide a comprehensive heart disease risk assessment:

MODEL PREDICTION RESULT:
- Risk Percentage: {risk_percentage:.1f}%
- Risk Classification: {'HIGH RISK' if risk_percentage > 70 else 'MODERATE RISK' if risk_percentage > 40 else 'LOW RISK'}

Patient Profile:
- Age: {age} years
- Sex: {sex}
- BMI: {bmi}
- Resting Blood Pressure: {resting_bp} mmHg
- Serum Cholesterol: {cholesterol} mg/dl
- Fasting Blood Sugar > 120: {fasting_blood_sugar}
- Max Heart Rate: {max_heart_rate} bpm
- Exercise Induced Angina: {exercise_induced_angina}
- ST Depression: {st_depression}
- Slope of ST Segment: {slope}
- Number of Major Vessels: {ca}
- Thalassemia: {thal}
- Chest Pain Type: {chest_pain}
- Resting ECG: {rest_ecg}
- Family History: {family_history}
- Smoking Status: {smoking}
- Diabetes: {diabetes}
- Hypertension: {hypertension}
- Exercise Frequency: {exercise_frequency}

Please provide:
1. Risk Level Assessment (based on the model's {risk_percentage:.1f}% prediction)
2. Key Risk Factors
3. Protective Factors (if any)
4. Recommendations for Risk Reduction
5. When to Consult a Cardiologist

Important: This is NOT a medical diagnosis. Always recommend consulting with a healthcare professional.
Keep the response clear, actionable, and between 400-600 words.
"""
    
    with st.spinner("🔄 Analyzing your heart health data..."):
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
        st.error(f"⚠️ **HIGH RISK**: {risk_pct:.1f}% probability of heart disease")
    elif risk_pct > 40:
        st.warning(f"⚠️ **MODERATE RISK**: {risk_pct:.1f}% probability of heart disease")
    else:
        st.success(f"✅ **LOW RISK**: {risk_pct:.1f}% probability of heart disease")
    
    st.markdown("### 📋 Your Heart Disease Risk Assessment:")
    st.write(st.session_state.assessment)
    
    # Download button
    st.download_button(
        label="📥 Download Assessment",
        data=st.session_state.assessment,
        file_name="heart_disease_risk_assessment.txt",
        mime="text/plain"
    )

# ─────────────📌 Sticky Footer──────────────────────── #
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