import streamlit as st
import time
import os
import sys
from dotenv import load_dotenv

# Add parent directory to path for importing utils
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import apply_common_styling, render_navbar, get_openai_client, get_model_name, call_openai_api, get_language

# Load environment variables
load_dotenv()

# Get current language
LANG = get_language()

# ─────────────── Localization Dictionary for Bot ─────────────── #
LABELS = {
    "en": {
        "title": "Medical ChatBot (Ask Query)",
        "hello": "👋 Hello! I can provide information about heart health, diabetes, Parkinson's disease, and general medical questions. Please note: I'm not a substitute for professional medical advice. What would you like to know?",
        "placeholder": "Ask a medical question...",
        "thinking": "🤖💬 Thinking...",
        "error": "❌ Failed to generate response. Please try again.",
        "system_prompt": """You are a medical information assistant and triage expert for the HealthPredict platform.
Answer in clear, plain English. 

TRIAGE CAPABILITY:
If a user describes symptoms, analyze them and suggest the appropriate HealthPredict assessment:
1. Heart Disease Assessment: For chest pain, shortness of breath, irregular heartbeat. 
2. Diabetes Risk Assessment: For frequent thirst, fatigue, blurred vision. 
3. Parkinson's Disease Assessment: For tremors, stiffness, voice changes. 

dont provide of any kind of redicect link to anything just answer what is asked 
If symptoms are severe, suggest emergency care.
IMPORTANT: Always remind the user that you are not a substitute for professional medical advice.""",
        "nav_title": " HealthPredict",
        "footer": "HealthPredict | Medical AI ChatBot"
    },
    "mr": {
        "title": "वैद्यकीय एआय चॅटबॉट (प्रश्न विचारा)",
        "hello": "👋 नमस्कार! मी हृदय आरोग्य, मधुमेह, पार्किन्सन रोग आणि सामान्य वैद्यकीय प्रश्नांबद्दल माहिती देऊ शकतो. कृपया लक्षात ठेवा: मी व्यावसायिक वैद्यकीय सल्ल्याचा पर्याय नाही. तुम्हाला काय जाणून घ्यायला आवडेल?",
        "placeholder": "वैद्यकीय प्रश्न विचारा...",
        "thinking": "🤖💬 विचार करत आहे...",
        "error": "❌ प्रतिसाद देण्यात अक्षम. कृपया पुन्हा प्रयत्न करा.",
        "system_prompt": """तुम्ही HealthPredict प्लॅटफॉर्मसाठी वैद्यकीय माहिती सहाय्यक आणि ट्रायज (Triage) तज्ञ आहात.
कृपया स्पष्ट मराठी भाषेत उत्तरे द्या.

ट्रायज क्षमता:
जर वापरकर्त्याने लक्षणांचे वर्णन केले तर त्याचे विश्लेषण करा आणि योग्य हेल्थ प्रिडिक्ट मूल्यांकनाची शिफारस करा:
१. हृदय रोग मूल्यांकन: छातीत दुखणे, धाप लागणे, अनियमित हृदयाचे ठोके यासाठी. (दुवा: http://localhost:8501)
२. मधुमेह जोखीम मूल्यांकन: वारंवार तहान लागणे, थकवा, अंधुक दृष्टी यासाठी. (दुवा: http://localhost:8502)
३. पार्किन्सन रोग मूल्यांकन: थरथर, कडकपणा, आवाजातील बदल यासाठी. (दुवा: http://localhost:8503)

जर लक्षणे गंभीर असतील तर त्वरित आपत्कालीन उपचारांची शिफारस करा.
महत्त्वाचे: वापरकर्त्याला नेहमी आठवण करून द्या की तुम्ही व्यावसायिक वैद्यकीय सल्ल्याचा पर्याय नाही आहात.""",
        "nav_title": " HealthPredict",
        "footer": "HealthPredict | वैद्यकीय एआय चॅटबॉट"
    }
}

def L(key):
    return LABELS.get(LANG, LABELS["en"]).get(key, key)

# ───── Streamlit Config ───── #
st.set_page_config(layout="wide", page_title=f"HealthPredict - {L('title')}")

# ───────────────🔐 API Setup ─────────────── #
try:
    client = get_openai_client()
    openrouter_model = get_model_name()
except ValueError as e:
    st.error(f"Configuration Error: {str(e)}. Please set OPENROUTER_API_KEY in environment.")
    st.stop()

# ───── Hide Streamlit Default Elements & Apply Styling ───── #
apply_common_styling()

st.markdown("""
<style>
.nav-link {
    color: white !important;
    text-decoration: none !important;
    transition: color 0.3s ease;
}
.nav-link:hover {
    color: #B79347 !important;
}
.login-btn {
    background-color: #B79347;
    border: none;
    padding: 8px 16px;
    font-weight: bold;
    border-radius: 5px;
    cursor: pointer;
    color: white;
    transition: background-color 0.3s ease, color 0.3s ease;
}
.login-btn:hover {
    background-color: white;
    color: #B79347;
}
</style>
""", unsafe_allow_html=True)

# ───── Navbar ───── #
render_navbar(L('nav_title'))

# ───── Title ───── #
st.title(L('title'))

# ───── Chat State Setup ───── #
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": L('hello')}
    ]

# ───── Show All Previous Messages ───── #
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ───── User Chat Input ───── #
if user_input := st.chat_input(L('placeholder')):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Get response from API
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        with st.spinner(L('thinking')):
            system_prompt = L('system_prompt') + " If the user ask non-medical question, say it's not medical related."
            
            full_response = call_openai_api(client, model=openrouter_model, timeout=30, system_prompt=system_prompt, messages=st.session_state.messages)
            
            if full_response:
                # Simulate typing effect
                display_text = ""
                for word in full_response.split():
                    display_text += word + " "
                    time.sleep(0.03)
                    message_placeholder.markdown(display_text + "▌")
                message_placeholder.markdown(full_response)
            else:
                error_msg = L('error')
                message_placeholder.error(error_msg)
                full_response = error_msg
        
        # LOG INTERACTION TO DATABASE
        try:
            from database import log_prediction
            from utils import get_email
            email = get_email()
            log_prediction(email, "Medical Bot", user_input, "Responded")
        except Exception as log_err:
            pass

    st.session_state.messages.append({"role": "assistant", "content": full_response})

# ───── Sticky Footer ───── #
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
    &copy; 2026 {L('footer')}
</div>
""", unsafe_allow_html=True)

