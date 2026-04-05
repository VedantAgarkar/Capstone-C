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
from utils import apply_common_styling, apply_button_styling, render_navbar, load_model, get_openai_client, get_model_name, call_openai_api, get_language, get_text, render_risk_meter, generate_pdf_report

# Load environment variables
load_dotenv()

# Get current language
LANG = get_language()

# ─────────────── Localization Dictionary for Diabetes App ─────────────── #
LABELS = {
    "en": {
        "title": "🩺 Diabetes Risk Assessment",
        "subtitle": "### Complete the form below for a comprehensive diabetes risk analysis",
        "section1": "#### 👤 Demographics & Basic Information",
        "age": "Age", "age_help": "Your age in years",
        "pregnancies": "Number of Pregnancies", "preg_help": "Total number of times pregnant (0 if male or never pregnant)",
        "sex": "Sex", "sex_help": "Biological sex",
        "bmi": "BMI", "bmi_help": "Body Mass Index (weight in kg / height in m²)",
        "section2": "#### 🩺 Clinical Measurements",
        "glucose": "Glucose Level", "glucose_help": "Plasma glucose concentration (mg/dl)",
        "bp": "Blood Pressure", "bp_help": "Diastolic blood pressure (mmHg)",
        "skin": "Skin Thickness", "skin_help": "Triceps skin fold thickness (mm)",
        "insulin": "Insulin Level", "insulin_help": "2-Hour serum insulin (mu U/ml)",
        "pedigree": "Diabetes Pedigree Function", "pedigree_help": "Diabetes pedigree function (genetic influence)",
        "section3": "#### 📋 Lifestyle & Medical History",
        "family": "Family History of Diabetes", "family_help": "First-degree relative with diabetes",
        "activity": "Physical Activity Level", "activity_help": "Your typical physical activity level",
        "smoking": "Smoking Status", "smoking_help": "Current smoking status",
        "diet": "Diet Quality", "diet_help": "Overall quality of your diet",
        "hypertension": "Hypertension", "hyper_help": "Do you have high blood pressure?",
        "sleep": "Average Sleep Hours", "sleep_help": "Average hours of sleep per night",
        "analyzing": "🔄 Analyzing your diabetes risk data...",
        "completing": "✅ Assessment Complete!",
        "prompt_intro": "You are a medical AI assistant. Based on the following health metrics and AI model prediction, provide a comprehensive diabetes risk assessment:",
        "download": "📥 Download Assessment (PDF)",
        "summary_header": "### 📋 Your Diabetes Risk Assessment:",
        "high_risk": "HIGH RISK", "mod_risk": "MODERATE RISK", "low_risk": "LOW RISK",
        "prob_text": "probability of diabetes",
        "submit_btn": "🔍 Assess Diabetes Risk",
        "footer_text": "HealthPredict | Medical Risk Assessment AI - Not a substitute for professional medical advice"
    },
    "mr": {
        "title": "🩺 मधुमेह जोखीम मूल्यांकन",
        "subtitle": "### सर्वसमावेशक विश्लेषणासाठी खालील फॉर्म भरा",
        "section1": "#### 👤 वैयक्तिक माहिती",
        "age": "वय", "age_help": "तुमचे वय (वर्षे)",
        "pregnancies": "गर्भधारणेची संख्या", "preg_help": "एकूण किती वेळा गर्भवती (पुरुष किंवा कधीही गर्भवती नसल्यास 0)",
        "sex": "लिंग", "sex_help": "जैविक लिंग",
        "bmi": "बीएमआय (BMI)", "bmi_help": "बॉडी मास इंडेक्स",
        "section2": "#### 🩺 वैद्यकीय मोजमापे",
        "glucose": "ग्लुकोज पातळी", "glucose_help": "प्लाझ्मा ग्लुकोज एकाग्रता (mg/dl)",
        "bp": "रक्तदाब (Blood Pressure)", "bp_help": "डायस्टोलिक रक्तदाब (mmHg)",
        "skin": "त्वचेची जाडी", "skin_help": "ट्रायसेप्स त्वचेची जाडी (mm)",
        "insulin": "इन्सुलिन पातळी", "insulin_help": "2-तास सीरम इन्सुलिन (mu U/ml)",
        "pedigree": "मधुमेह अनुवांशिकता (Pedigree)", "pedigree_help": "मधुमेह वंशावळ कार्य (अनुवांशिक प्रभाव)",
        "section3": "#### 📋 जीवनशैली आणि वैद्यकीय इतिहास",
        "family": "मधुमेहाचा कौटुंबिक इतिहास", "family_help": "आई, वडील किंवा भावंडांना मधुमेह आहे का?",
        "activity": "शारीरिक हालचालींची पातळी", "activity_help": "तुमची नेहमीची शारीरिक हालचाल",
        "smoking": "धूम्रपान स्थिती", "smoking_help": "सध्याची धूम्रपान स्थिती",
        "diet": "आहाराचा दर्जा", "diet_help": "तुमच्या आहाराची एकूण गुणवत्ता",
        "hypertension": "उच्च रक्तदाब (Hypertension)", "hyper_help": "तुम्हाला उच्च रक्तदाब आहे का?",
        "sleep": "सरासरी झोपेचे तास", "sleep_help": "दररोज रात्री झोपेचे सरासरी तास",
        "analyzing": "🔄 तुमच्या डेटाचे विश्लेषण करत आहे...",
        "completing": "✅ मूल्यांकन पूर्ण झाले!",
        "prompt_intro": "तुम्ही वैद्यकीय एआय सहाय्यक आहात. खालील आरोग्य मेट्रिक्स आणि एआय मॉडेलच्या अंदाजावर आधारित, कृपया मराठी भाषेत सर्वसमावेशक मधुमेह जोखीम मूल्यांकन द्या:",
        "download": "📥 मूल्यांकन डाउनलोड करा (PDF)",
        "summary_header": "### 📋 तुमचे मधुमेह जोखीम मूल्यांकन:",
        "high_risk": "उच्च धोका", "mod_risk": "मध्यम धोका", "low_risk": "कमी धोका",
        "prob_text": "मधुमेहाची शक्यता",
        "submit_btn": "🔍 मधुमेहाचा धोका तपासा",
        "footer_text": "HealthPredict | वैद्यकीय जोखीम मूल्यांकन AI - व्यावसायिक वैद्यकीय सल्ल्याचा पर्याय नाही"
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
    # Assuming LANG is enforced by utils.call_openai_api system prompt as well
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
    if LANG == 'en':
        st.warning("⚠️ Scaler not found. Predictions may be less accurate.")
    else:
        st.warning("⚠️ स्केलर सापडले नाही. अंदाज कमी अचूक असू शकतात.")

# ──────────────🎨 Custom Styling────────────────────────── #
apply_common_styling()
apply_button_styling("diabetes")

# ────────────── Navbar ─────────────── #
render_navbar(L('title'))

st.title(L('title'))
st.markdown(L('subtitle'))
st.divider()

# ═══════════════════ SECTION 1: Demographics & Basic Info ═══════════════════
st.markdown(L('section1'))
col1, col2 = st.columns(2)

with col1:
    age = st.number_input(L('age'), 
                         min_value=18, max_value=120, value=45,
                         help=L('age_help'))
    
    pregnancies = st.number_input(L('pregnancies'), 
                                  min_value=0, max_value=20, value=0,
                                  help=L('preg_help'))

with col2:
    sex_options = ["Male", "Female"] if LANG == 'en' else ["पुरुष", "स्त्री"]
    sex = st.selectbox(L('sex'), sex_options,
                      help=L('sex_help'))
    
    bmi = st.number_input(L('bmi'), 
                         min_value=15.0, max_value=70.0, value=25.0, step=0.1,
                         help=L('bmi_help'))

st.divider()

# ═══════════════════ SECTION 2: Clinical Measurements ═══════════════════
st.markdown(L('section2'))
col3, col4, col5 = st.columns(3)

with col3:
    glucose = st.number_input(L('glucose'), 
                             min_value=0, max_value=250, value=100,
                             help=L('glucose_help'))
    
    blood_pressure = st.number_input(L('bp'), 
                                     min_value=0, max_value=200, value=70,
                                     help=L('bp_help'))

with col4:
    skin_thickness = st.number_input(L('skin'), 
                                     min_value=0, max_value=100, value=20,
                                     help=L('skin_help'))
    
    insulin = st.number_input(L('insulin'), 
                             min_value=0, max_value=900, value=0,
                             help=L('insulin_help'))

with col5:
    diabetes_pedigree = st.number_input(L('pedigree'), 
                                       min_value=0.0, max_value=2.5, value=0.5, step=0.001,
                                       help=L('pedigree_help'))

st.divider()

# ═══════════════════ SECTION 3: Lifestyle & Medical History ═══════════════════
st.markdown(L('section3'))
col6, col7, col8 = st.columns(3)

with col6:
    fam_opts = ["No", "Yes"] if LANG == 'en' else ["नाही (No)", "होय (Yes)"]
    family_history = st.selectbox(L('family'), fam_opts,
                                 help=L('family_help'))
    
    act_opts = ["Sedentary", "Light", "Moderate", "Active"] if LANG == 'en' else ["बैठी जीवनशैली (Sedentary)", "हलका व्यायाम (Light)", "मध्यम (Moderate)", "सक्रिय (Active)"]
    physical_activity = st.selectbox(L('activity'), act_opts,
                                    help=L('activity_help'))

with col7:
    smoke_opts = ["Never", "Former", "Current"] if LANG == 'en' else ["कधीच नाही (Never)", "माजी (Former)", "सध्या (Current)"]
    smoking = st.selectbox(L('smoking'), smoke_opts,
                          help=L('smoking_help'))
    
    diet_opts = ["Poor", "Fair", "Good", "Excellent"] if LANG == 'en' else ["खराब (Poor)", "साधारण (Fair)", "चांगला (Good)", "उत्कृष्ट (Excellent)"]
    diet_quality = st.selectbox(L('diet'), diet_opts,
                               help=L('diet_help'))

with col8:
    hyp_opts = ["No", "Yes"] if LANG == 'en' else ["नाही", "होय"]
    hypertension = st.selectbox(L('hypertension'), hyp_opts,
                               help=L('hyper_help'))
    
    sleep_hours = st.number_input(L('sleep'), 
                                 min_value=3, max_value=12, value=7,
                                 help=L('sleep_help'))

st.divider()

# Submit button
if st.button(L('submit_btn'), type="primary", use_container_width=True):
    # Dataset features: Pregnancies, Glucose, BloodPressure, SkinThickness, Insulin, BMI, DiabetesPedigreeFunction, Age
    # Create feature DataFrame matching the dataset order
    feature_names = ['Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age']
    features = pd.DataFrame([[pregnancies, glucose, blood_pressure, skin_thickness, 
                          insulin, bmi, diabetes_pedigree, age]], columns=feature_names)
    
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
        err_msg = get_text("error", LANG) + str(e)
        st.error(f"❌ {err_msg}")
        prediction = None
        risk_percentage = 0
    
    # Create assessment prompt
    assessment_prompt = f"""
{L('prompt_intro')}

MODEL PREDICTION RESULT:
- Risk Percentage: {risk_percentage:.1f}%
- Risk Classification: {L('high_risk') if risk_percentage > 70 else L('mod_risk') if risk_percentage > 40 else L('low_risk')}

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
"""
    if LANG == "mr":
         assessment_prompt += "\nImportant: Response MUST be in Marathi language."

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
                feature_dict = {
                    'Pregnancies': pregnancies, 'Glucose': glucose, 'BloodPressure': blood_pressure,
                    'SkinThickness': skin_thickness, 'Insulin': insulin, 'BMI': bmi,
                    'DiabetesPedigreeFunction': diabetes_pedigree, 'Age': age
                }
                log_prediction(email, "Diabetes", feature_dict, f"{risk_percentage:.1f}% Risk")
            except Exception as log_err:
                st.error(f"Note: Could not log prediction result: {log_err}")
                
            st.success(L('completing'))
        else:
            st.error("❌ Failed to generate assessment.")

# Display assessment results
if st.session_state.get("assessment"):
    # Show risk percentage in a prominent way
    risk_pct = st.session_state.get("risk_percentage", 0)
    
    risk_labels = {
        "high": get_text("high_risk", LANG),
        "mod": get_text("moderate_risk", LANG),
        "low": get_text("low_risk", LANG)
    }

    if risk_pct > 70:
        st.error(f"⚠️ **{L('high_risk')}**: {risk_pct:.1f}% {L('prob_text')}")
    elif risk_pct > 40:
        st.warning(f"⚠️ **{L('mod_risk')}**: {risk_pct:.1f}% {L('prob_text')}")
    else:
        st.success(f"✅ **{L('low_risk')}**: {risk_pct:.1f}% {L('prob_text')}")
    
    # Render visual risk meter
    render_risk_meter(risk_pct)
    
    st.markdown(L('summary_header'))
    st.write(st.session_state.assessment)
    
    # Generate PDF Report
    pdf_bytes = generate_pdf_report(
        content=st.session_state.assessment,
        risk_pct=risk_pct,
        title=L('title'),
        patient_info=f"Age: {age}, Sex: {sex}, Glucose: {glucose}"
    )

    # Download button
    st.download_button(
        label=L('download'),
        data=pdf_bytes,
        file_name=f"diabetes_risk_assessment_{LANG}.pdf",
        mime="application/pdf"
    )

# ───────────── Sticky Footer ───────────── #
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
        &copy; 2026 {L('footer_text')}
    </div>
""", unsafe_allow_html=True)
