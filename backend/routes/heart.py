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

# Load environment variables
load_dotenv()

# Get current language
LANG = get_language()

# ─────────────── Localization Dictionary for Heart App ─────────────── #
LABELS = {
    "en": {
        "title": "❤️ Heart Disease Risk Assessment",
        "subtitle": "### Complete the form below for a comprehensive cardiovascular risk analysis",
        "section1": "#### 👤 Demographics & Basic Information",
        "age": "Age", "age_help": "Your age in years",
        "sex": "Sex", "sex_help": "Biological sex",
        "bmi": "BMI", "bmi_help": "Body Mass Index (weight in kg / height in m²)",
        "section2": "#### 🩺 Clinical Measurements",
        "resting_bp": "Resting Blood Pressure", "rbp_help": "Resting blood pressure in mmHg",
        "fbs_label": "Fasting Blood Sugar > 120 mg/dl?", "fbs_help": "Is fasting blood sugar greater than 120 mg/dl?",
        "cholesterol": "Serum Cholesterol", "chol_help": "Serum cholesterol in mg/dl",
        "max_hr": "Maximum Heart Rate Achieved", "max_hr_help": "Maximum heart rate during exercise test",
        "chest_pain": "Chest Pain Type", "cp_help": "Type of chest pain experienced",
        "section3": "#### 🫀 Cardiovascular Test Results",
        "ecg": "Resting ECG Results", "ecg_help": "Resting electrocardiographic results",
        "ex_angina": "Exercise Induced Angina?", "ex_angina_help": "Does exercise induce angina (chest pain)?",
        "st_dep": "ST Depression", "st_dep_help": "ST depression induced by exercise relative to rest",
        "slope": "Slope of Peak Exercise ST Segment", "slope_help": "Slope of the peak exercise ST segment",
        "vessels": "Number of Major Vessels", "vessels_help": "Number of major vessels (0-3) colored by fluoroscopy",
        "thal": "Thalassemia", "thal_help": "Thalassemia blood disorder status",
        "section4": "#### 📋 Medical History & Lifestyle",
        "family": "Family History", "family_help": "Family history of heart disease",
        "diabetes": "Diabetes", "diabetes_help": "Do you have diabetes?",
        "hypertension": "Hypertension", "hyper_help": "Do you have high blood pressure?",
        "smoking": "Smoking Status", "smoking_help": "Current smoking status",
        "exercise_freq": "Exercise Frequency (per week)", "freq_help": "How often do you exercise per week?",
        "submit_btn": "🔍 Assess Heart Disease Risk",
        "analyzing": "🔄 Analyzing your heart health data...",
        "completing": "✅ Assessment Complete!",
        "summary_header": "### 📋 Your Heart Disease Risk Assessment:",
        "prompt_intro": "You are a medical AI assistant. Based on the following health metrics and AI model prediction, provide a comprehensive heart disease risk assessment in English:",
        "high_risk": "HIGH RISK", "mod_risk": "MODERATE RISK", "low_risk": "LOW RISK",
        "prob_text": "probability of heart disease"
    },
    "mr": {
        "title": "❤️ हृदयविकार जोखीम मूल्यांकन",
        "subtitle": "### सर्वसमावेशक विश्लेषणासाठी खालील फॉर्म भरा",
        "section1": "#### 👤 वैयक्तिक माहिती",
        "age": "वय", "age_help": "तुमचे वय (वर्षे)",
        "sex": "लिंग", "sex_help": "जैविक लिंग",
        "bmi": "बीएमआय (BMI)", "bmi_help": "बॉडी मास इंडेक्स",
        "section2": "#### 🩺 वैद्यकीय मोजमापे",
        "resting_bp": "विश्रांतीचा रक्तदाब", "rbp_help": "विश्रांतीचा रक्तदाब (mmHg)",
        "fbs_label": "उपाशी पोटी रक्तातील साखर > 120 mg/dl आहे का?", "fbs_help": "तुमची साखर १२० पेक्षा जास्त आहे का?",
        "cholesterol": "सीरम कोलेस्ट्रॉल", "chol_help": "सीरम कोलेस्ट्रॉल (mg/dl)",
        "max_hr": "कमाल हृदय गती", "max_hr_help": "व्यायाम चाचणी दरम्यान कमाल हृदय गती",
        "chest_pain": "छातीत दुखण्याचा प्रकार", "cp_help": "तुम्हाला कोणत्या प्रकारचे छातीत दुखते?",
        "section3": "#### 🫀 हृदय चाचणी निकाल",
        "ecg": "ईसीजी (ECG) निकाल", "ecg_help": "ईसीजी निकाल",
        "ex_angina": "व्यायामामुळे छातीत दुखते का?", "ex_angina_help": "व्यायाम केल्यावर छातीत दुखते का?",
        "st_dep": "एसटी डिप्रेशन (ST Depression)", "st_dep_help": "व्यायामामुळे होणारे एसटी डिप्रेशन",
        "slope": "पीक व्यायाम ST विभागाचा उतार", "slope_help": "एसटी विभागाचा उतार",
        "vessels": "मुख्य रक्तवाहिन्यांची संख्या", "vessels_help": "मुख्य रक्तवाहिन्यांची संख्या (0-3)",
        "thal": "थॅलेसेमिया (Thalassemia)", "thal_help": "थॅलेसेमिया रक्ताची स्थिती",
        "section4": "#### 📋 वैद्यकीय इतिहास आणि जीवनशैली",
        "family": "कौटुंबिक इतिहास", "family_help": "कुटुंबात कोणाला हृदयविकार आहे का?",
        "diabetes": "मधुमेह", "diabetes_help": "तुम्हाला मधुमेह आहे का?",
        "hypertension": "उच्च रक्तदाब", "hyper_help": "तुम्हाला उच्च रक्तदाब आहे का?",
        "smoking": "धूम्रपान स्थिती", "smoking_help": "धूम्रपान स्थिती",
        "exercise_freq": "व्यायामाची वारंवारता (दर आठवड्याला)", "freq_help": "तुम्ही आठवड्यातून किती वेळा व्यायाम करता?",
        "submit_btn": "🔍 हृदयविकाराचा धोका तपासा",
        "analyzing": "🔄 तुमच्या हृदयाच्या आरोग्याचे विश्लेषण करत आहे...",
        "completing": "✅ मूल्यांकन पूर्ण झाले!",
        "summary_header": "### 📋 तुमचे हृदयविकार जोखीम मूल्यांकन:",
        "prompt_intro": "तुम्ही वैद्यकीय एआय सहाय्यक आहात. खालील आरोग्य मेट्रिक्स आणि एआय मॉडेलच्या अंदाजावर आधारित, कृपया मराठी भाषेत सर्वसमावेशक हृदयविकार जोखीम मूल्यांकन द्या:",
        "high_risk": "उच्च धोका", "mod_risk": "मध्यम धोका", "low_risk": "कमी धोका",
        "prob_text": "हृदयविकाराची शक्यता"
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
render_navbar(f" HealthPredict - {L('title')}")

st.title(L('title'))
st.markdown(L('subtitle'))
st.divider()

# ═══════════════════ SECTION 1: Demographics & Basic Info ═══════════════════
st.markdown(L('section1'))
col1, col2, col3 = st.columns(3)

with col1:
    age = st.number_input(L('age'), min_value=18, max_value=120, value=50, 
                         help=L('age_help'))

with col2:
    sex_options = ["Male", "Female"]
    if LANG == "mr":
        sex_map = {"Male": "पुरुष", "Female": "स्त्री"}
        sex_display = st.selectbox(L('sex'), ["पुरुष", "स्त्री"], help=L('sex_help'))
        sex = "Male" if sex_display == "पुरुष" else "Female"
    else:
        sex = st.selectbox(L('sex'), sex_options, help=L('sex_help'))

with col3:
    bmi = st.number_input(L('bmi'), min_value=15.0, max_value=50.0, value=25.0, step=0.1,
                         help=L('bmi_help'))

st.divider()

# ═══════════════════ SECTION 2: Clinical Measurements ═══════════════════
st.markdown(L('section2'))
col4, col5, col6 = st.columns(3)

with col4:
    resting_bp = st.number_input(L('resting_bp'), 
                                 min_value=80, max_value=200, value=120,
                                 help=L('rbp_help'))
    
    fbs_display_options = ["No", "Yes"]
    if LANG == "mr":
        fbs_map = {"No": "नाही", "Yes": "हो"}
        fbs_display = st.selectbox(L('fbs_label'), ["नाही", "हो"], help=L('fbs_help'))
        fasting_blood_sugar = "Yes" if fbs_display == "हो" else "No"
    else:
        fasting_blood_sugar = st.selectbox(L('fbs_label'), fbs_display_options, help=L('fbs_help'))

with col5:
    cholesterol = st.number_input(L('cholesterol'), 
                                  min_value=100, max_value=400, value=200,
                                  help=L('chol_help'))
    
    max_heart_rate = st.number_input(L('max_hr'), 
                                     min_value=60, max_value=220, value=150,
                                     help=L('max_hr_help'))

with col6:
    cp_options = ["Asymptomatic", "Non-anginal Pain", "Atypical Angina", "Typical Angina"]
    if LANG == "mr":
        cp_map = {"Asymptomatic": "लक्षणे नाहीत", "Non-anginal Pain": "नॉन-अँजिनल त्रास", 
                  "Atypical Angina": "असामान्य अँजिना", "Typical Angina": "सामान्य अँजिना"}
        cp_display = st.selectbox(L('chest_pain'), list(cp_map.values()), help=L('cp_help'))
        chest_pain = [k for k, v in cp_map.items() if v == cp_display][0]
    else:
        chest_pain = st.selectbox(L('chest_pain'), cp_options, help=L('cp_help'))

st.divider()

# ═══════════════════ SECTION 3: Cardiovascular Test Results ═══════════════════
st.markdown(L('section3'))
col7, col8, col9 = st.columns(3)

with col7:
    ecg_options = ["Normal", "ST-T Abnormality", "Left Ventricular Hypertrophy"]
    if LANG == "mr":
        ecg_map = {"Normal": "सामान्य", "ST-T Abnormality": "ST-T विकृती", 
                   "Left Ventricular Hypertrophy": "डाव्या वेंट्रिक्युलर हायपरट्रॉफी"}
        ecg_display = st.selectbox(L('ecg'), list(ecg_map.values()), help=L('ecg_help'))
        rest_ecg = [k for k, v in ecg_map.items() if v == ecg_display][0]
    else:
        rest_ecg = st.selectbox(L('ecg'), ecg_options, help=L('ecg_help'))
    
    angina_display = st.selectbox(L('ex_angina'), ["नाही", "हो"] if LANG == "mr" else ["No", "Yes"], help=L('ex_angina_help'))
    exercise_induced_angina = "Yes" if (angina_display == "हो" or angina_display == "Yes") else "No"

with col8:
    st_depression = st.number_input(L('st_dep'), 
                                    min_value=0.0, max_value=10.0, value=0.0, step=0.1,
                                    help=L('st_dep_help'))
    
    slope_options = ["Upsloping", "Flat", "Downsloping"]
    if LANG == "mr":
        slope_map = {"Upsloping": "वर जाणारा", "Flat": "सपाट", "Downsloping": "खाली जाणारा"}
        slope_display = st.selectbox(L('slope'), list(slope_map.values()), help=L('slope_help'))
        slope = [k for k, v in slope_map.items() if v == slope_display][0]
    else:
        slope = st.selectbox(L('slope'), slope_options, help=L('slope_help'))

with col9:
    ca = st.number_input(L('vessels'), 
                        min_value=0, max_value=3, value=0,
                        help=L('vessels_help'))
    
    thal_options = ["Normal", "Fixed Defect", "Reversible Defect"]
    if LANG == "mr":
        thal_map = {"Normal": "सामान्य", "Fixed Defect": "निश्चित दोष", "Reversible Defect": "पुन्हा उलटणारा दोष"}
        thal_display = st.selectbox(L('thal'), list(thal_map.values()), help=L('thal_help'))
        thal = [k for k, v in thal_map.items() if v == thal_display][0]
    else:
        thal = st.selectbox(L('thal'), thal_options, help=L('thal_help'))

st.divider()

# ═══════════════════ SECTION 4: Medical History & Lifestyle ═══════════════════
st.markdown(L('section4'))
col10, col11, col12, col13 = st.columns(4)

with col10:
    family_display = st.selectbox(L('family'), ["नाही", "हो"] if LANG == "mr" else ["No", "Yes"], help=L('family_help'))
    family_history = "Yes" if (family_display == "हो" or family_display == "Yes") else "No"

with col11:
    diabetes_display = st.selectbox(L('diabetes'), ["नाही", "हो"] if LANG == "mr" else ["No", "Yes"], help=L('diabetes_help'))
    diabetes = "Yes" if (diabetes_display == "हो" or diabetes_display == "Yes") else "No"

with col12:
    hyper_display = st.selectbox(L('hypertension'), ["नाही", "हो"] if LANG == "mr" else ["No", "Yes"], help=L('hyper_help'))
    hypertension = "Yes" if (hyper_display == "हो" or hyper_display == "Yes") else "No"

with col13:
    smoking_options = ["Never", "Former", "Current"]
    if LANG == "mr":
        smoking_map = {"Never": "कधीही नाही", "Former": "माजी धूम्रपान करणारा", "Current": "सध्या धूम्रपान करणारा"}
        smoking_display = st.selectbox(L('smoking'), list(smoking_map.values()), help=L('smoking_help'))
        smoking = [k for k, v in smoking_map.items() if v == smoking_display][0]
    else:
        smoking = st.selectbox(L('smoking'), smoking_options, help=L('smoking_help'))

# Exercise frequency
freq_options = ["None", "1-2 times", "3-4 times", "5+ times"]
if LANG == "mr":
    freq_map = {"None": "काहीही नाही", "1-2 times": "१-२ वेळा", "3-4 times": "३-४ वेळा", "5+ times": "५+ वेळा"}
    freq_display = st.select_slider(L('exercise_freq'), options=list(freq_map.values()), value="१-२ वेळा", help=L('freq_help'))
    exercise_frequency = [k for k, v in freq_map.items() if v == freq_display][0]
else:
    exercise_frequency = st.select_slider(L('exercise_freq'), options=freq_options, value="1-2 times", help=L('freq_help'))

st.divider()

# Submit button
if st.button(L('submit_btn'), type="primary", use_container_width=True):
    # Prepare features for model prediction
    sex_encoded = 1 if sex == "Male" else 0
    chest_pain_encoded = {"Typical Angina": 3, "Atypical Angina": 2, "Non-anginal Pain": 1, "Asymptomatic": 0}[chest_pain]
    rest_ecg_encoded = {"Normal": 0, "ST-T Abnormality": 1, "Left Ventricular Hypertrophy": 2}[rest_ecg]
    fasting_encoded = 1 if fasting_blood_sugar == "Yes" else 0
    exercise_angina_encoded = 1 if exercise_induced_angina == "Yes" else 0
    slope_encoded = {"Upsloping": 0, "Flat": 1, "Downsloping": 2}[slope]
    thal_encoded = {"Normal": 1, "Fixed Defect": 2, "Reversible Defect": 3}[thal]
    
    # Create feature array for model
    feature_names = ['age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 'restecg', 'thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal']
    features = pd.DataFrame([[age, sex_encoded, chest_pain_encoded, resting_bp, cholesterol, 
                          fasting_encoded, rest_ecg_encoded, max_heart_rate, exercise_angina_encoded, 
                          st_depression, slope_encoded, ca, thal_encoded]], columns=feature_names)
    
    if heart_scaler is not None:
        features_scaled = heart_scaler.transform(features)
    else:
        features_scaled = features
    
    try:
        prediction = heart_model.predict(features_scaled)[0]
        prediction_proba = heart_model.predict_proba(features_scaled)[0]
        risk_percentage = prediction_proba[1] * 100 if len(prediction_proba) > 1 else 0
    except Exception as e:
        st.error(f"❌ Error: {e}")
        prediction = None
        risk_percentage = 0
    
    # Create assessment prompt with prediction
    assessment_prompt = f"""
{L('prompt_intro')}

MODEL PREDICTION RESULT:
- Risk Percentage: {risk_percentage:.1f}%
- Risk Classification: {L('high_risk') if risk_percentage > 70 else L('mod_risk') if risk_percentage > 40 else L('low_risk')}

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
                log_prediction(email, "Heart Disease", features.to_dict(orient='records')[0], f"{risk_percentage:.1f}% Risk")
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
        patient_info=f"Age: {age}, Sex: {sex}, BMI: {bmi}"
    )

    st.markdown(L('summary_header'))
    st.write(st.session_state.assessment)
    
    st.download_button(
        label=f"📥 {L('title')} (PDF)",
        data=pdf_bytes,
        file_name="heart_disease_risk_assessment.pdf",
        mime="application/pdf"
    )

# ─────────────📌 Sticky Footer──────────────────────── #
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