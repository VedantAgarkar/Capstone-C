import streamlit as st
import time
import os
import sys
from dotenv import load_dotenv

# Add parent directory to path for importing utils
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import apply_common_styling, render_navbar, get_openai_client, get_model_name, call_openai_api

# Load environment variables
load_dotenv()

# ───── Streamlit Config ───── #
st.set_page_config(layout="wide", page_title="HealthPredict - Medical ChatBot")

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
render_navbar(" HealthPredict")

# ───── Title ───── #
st.title("Medical ChatBot (Ask Query)")

# ───── Chat State Setup ───── #
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "👋 Hello! I can provide information about heart health, diabetes, Parkinson's disease, and general medical questions. Please note: I'm not a substitute for professional medical advice. What would you like to know?"}
    ]

# ───── Show All Previous Messages ───── #
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ───── User Chat Input ───── #
if user_input := st.chat_input("Ask a medical question..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Get response from API
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        with st.spinner("🤖💬 Thinking..."):
            system_prompt = """You are a medical information assistant. If the user's latest question is NOT health/medical-related 
(diseases, symptoms, heart health, diabetes, Parkinson's, medical conditions, etc.), 
reply only with: '❌ Please ask a medical-related question'. 
Otherwise, answer in clear, plain English. IMPORTANT: Always remind the user that you are not a substitute for professional medical advice."""
            
            full_response = call_openai_api(client, user_input, openrouter_model, timeout=30)
            
            if full_response:
                # Simulate typing effect
                display_text = ""
                for word in full_response.split():
                    display_text += word + " "
                    time.sleep(0.03)
                    message_placeholder.markdown(display_text + "▌")
                message_placeholder.markdown(full_response)
            else:
                error_msg = "❌ Failed to generate response. Please try again."
                message_placeholder.error(error_msg)
                full_response = error_msg

    st.session_state.messages.append({"role": "assistant", "content": full_response})

# ───── Sticky Footer ───── #
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
    &copy; 2026 HealthPredict | Medical AI ChatBot 
</div>
""", unsafe_allow_html=True)
