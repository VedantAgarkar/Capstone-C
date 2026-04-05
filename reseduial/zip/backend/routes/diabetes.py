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
st.set_page_config(layout="wide", page_title="HealthPredict - Diabetes Risk Assessment")

# ───────────────🔐 API Setup ─────────────── #
try:
    client = get_openai_client()
    openrouter_model = get_model_name()
except ValueError as e:
    st.error(f"Configuration Error: {str(e)}. Please set OPENROUTER_API_KEY in environment.")
    st.stop()

# ───── Load Pre-trained Model and Scaler ───── #
diabetes_model = load_model("backend/diabetes_model.sav")
try:
    import pickle
    diabetes_scaler = pickle.load(open("backend/diabetes_scaler.sav", 'rb'))
except:
    diabetes_scaler = None
    st.warning("⚠️ Scaler not found. Predictions may be less accurate.")

# ──────────────🎨 Custom Styling────────────────────────── #
apply_common_styling()
apply_button_styling("diabetes")

# ────────────── Navbar ─────────────── #
render_navbar(" HealthPredict - Diabetes Risk")

st.title("🩺 Diabetes Risk Assessment")
st.markdown("### Complete the form below for a comprehensive diabetes risk analysis")
st.divider()

# ═══════════════════ SECTION 1: Demographics & Basic Info ═══════════════════
st.markdown("#### 👤 Demographics & Basic Information")
col1, col2 = st.columns(2)

with col1:
    age = st.number_input("Age", 
                         min_value=18, max_value=120, value=45,
                         help="Your age in years")
    
    pregnancies = st.number_input("Number of Pregnancies", 
                                  min_value=0, max_value=20, value=0,
                                  help="Total number of times pregnant (0 if male or never pregnant)")

with col2:
    sex = st.selectbox("Sex", ["Male", "Female"],
                      help="Biological sex")
    
    bmi = st.number_input("BMI", 
                         min_value=15.0, max_value=70.0, value=25.0, step=0.1,
                         help="Body Mass Index (weight in kg / height in m²)")

st.divider()

# ═══════════════════ SECTION 2: Clinical Measurements ═══════════════════
st.markdown("#### 🩺 Clinical Measurements")
col3, col4, col5 = st.columns(3)

with col3:
    glucose = st.number_input("Glucose Level", 
                             min_value=0, max_value=250, value=100,
                             help="Plasma glucose concentration (mg/dl)")
    
    blood_pressure = st.number_input("Blood Pressure", 
                                     min_value=0, max_value=200, value=70,
                                     help="Diastolic blood pressure (mmHg)")

with col4:
    skin_thickness = st.number_input("Skin Thickness", 
                                     min_value=0, max_value=100, value=20,
                                     help="Triceps skin fold thickness (mm)")
    
    insulin = st.number_input("Insulin Level", 
                             min_value=0, max_value=900, value=0,
                             help="2-Hour serum insulin (mu U/ml)")

with col5:
    diabetes_pedigree = st.number_input("Diabetes Pedigree Function", 
                                       min_value=0.0, max_value=2.5, value=0.5, step=0.001,
                                       help="Diabetes pedigree function (genetic influence)")

st.divider()

# ═══════════════════ SECTION 3: Lifestyle & Medical History ═══════════════════
st.markdown("#### 📋 Lifestyle & Medical History")
col6, col7, col8 = st.columns(3)

with col6:
    family_history = st.selectbox("Family History of Diabetes", 
                                 ["No", "Yes"],
                                 help="First-degree relative with diabetes")
    
    physical_activity = st.selectbox("Physical Activity Level", 
                                    ["Sedentary", "Light", "Moderate", "Active"],
                                    help="Your typical physical activity level")

with col7:
    smoking = st.selectbox("Smoking Status", 
                          ["Never", "Former", "Current"],
                          help="Current smoking status")
    
    diet_quality = st.selectbox("Diet Quality", 
                               ["Poor", "Fair", "Good", "Excellent"],
                               help="Overall quality of your diet")

with col8:
    hypertension = st.selectbox("Hypertension", 
                               ["No", "Yes"],
                               help="Do you have high blood pressure?")
    
    sleep_hours = st.number_input("Average Sleep Hours", 
                                 min_value=3, max_value=12, value=7,
                                 help="Average hours of sleep per night")

st.divider()

# Submit button
if st.button("🔍 Assess Diabetes Risk", type="primary", use_container_width=True):
    # Dataset features: Pregnancies, Glucose, BloodPressure, SkinThickness, Insulin, BMI, DiabetesPedigreeFunction, Age
    # Create feature array matching the dataset order
    features = np.array([[pregnancies, glucose, blood_pressure, skin_thickness, 
                         insulin, bmi, diabetes_pedigree, age]])
    
    # Apply scaling if scaler is available
    if diabetes_scaler is not None:
        features_scaled = diabetes_scaler.transform(features)
    else:
        features_scaled = features
    
    # Get model prediction
    try:
        prediction = diabetes_model.predict(features_scaled)[0]
        prediction_proba = diabetes_model.predict_proba(features_scaled)[0]
        risk_percentage = prediction_proba[1] * 100 if len(prediction_proba) > 1 else 0
    except Exception as e:
        st.error(f"❌ Error in model prediction: {e}")
        prediction = None
        risk_percentage = 0
    
    # Create assessment prompt
    assessment_prompt = f"""
You are a medical AI assistant. Based on the following health metrics and AI model prediction, provide a comprehensive diabetes risk assessment:

MODEL PREDICTION RESULT:
- Risk Percentage: {risk_percentage:.1f}%
- Risk Classification: {'HIGH RISK' if risk_percentage > 70 else 'MODERATE RISK' if risk_percentage > 40 else 'LOW RISK'}

Patient Profile:
Clinical Measurements:
- Age: {age} years
- Sex: {sex}
- BMI: {bmi}
- Number of Pregnancies: {pregnancies}
- Glucose Level: {glucose} mg/dl
- Blood Pressure: {blood_pressure} mmHg
- Skin Thickness: {skin_thickness} mm
- Insulin Level: {insulin} mu U/ml
- Diabetes Pedigree Function: {diabetes_pedigree:.3f}

Lifestyle & History:
- Family History: {family_history}
- Physical Activity: {physical_activity}
- Smoking Status: {smoking}
- Diet Quality: {diet_quality}
- Hypertension: {hypertension}
- Average Sleep: {sleep_hours} hours

Please provide:
1. Risk Level Assessment (based on the model's {risk_percentage:.1f}% prediction)
2. Key Risk Factors Present
3. Protective Factors (if any)
4. Lifestyle Modifications for Risk Reduction
5. When to Consult an Endocrinologist

Important: This is NOT a medical diagnosis. Always recommend consulting with a qualified healthcare provider.
Keep the response clear, actionable, and between 400-600 words.
"""
    
    with st.spinner("🔄 Analyzing your diabetes risk data..."):
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
        st.error(f"⚠️ **HIGH RISK**: {risk_pct:.1f}% probability of diabetes")
    elif risk_pct > 40:
        st.warning(f"⚠️ **MODERATE RISK**: {risk_pct:.1f}% probability of diabetes")
    else:
        st.success(f"✅ **LOW RISK**: {risk_pct:.1f}% probability of diabetes")
    
    st.markdown("### 📋 Your Diabetes Risk Assessment:")
    st.write(st.session_state.assessment)
    
    # Download button
    st.download_button(
        label="📥 Download Assessment",
        data=st.session_state.assessment,
        file_name="diabetes_risk_assessment.txt",
        mime="text/plain"
    )

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
