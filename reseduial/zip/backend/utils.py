"""
Shared utilities for Streamlit health prediction apps.
Centralizes common styling, model loading, and API setup.
"""
import streamlit as st
import os
from openai import OpenAI

# ─────────────── API Configuration ─────────────── #
def get_openai_client():
    """Get OpenAI/OpenRouter client with API key from environment."""
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY not set in environment variables")
    
    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key
    )

def get_model_name():
    """Get the model name from environment, default to deepseek."""
    return os.getenv("OPENROUTER_MODEL", "deepseek/deepseek-chat-v3.1")

# ─────────────── Streamlit Styling ─────────────── #
BUTTON_COLORS = {
    "heart": "#28a745",      # Green
    "diabetes": "#fd7e14",   # Orange
    "parkinsons": "#6f42c1", # Purple
    "default": "#007bff"     # Blue
}

def apply_common_styling():
    """Apply common CSS styling to all Streamlit apps."""
    st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: visible;}
    .css-1d391kg {display: none;}
    .css-18e3th9 {padding-left: 0px;}
    </style>
    """, unsafe_allow_html=True)

def apply_button_styling(color_key="default"):
    """Apply button styling with theme-specific color."""
    color = BUTTON_COLORS.get(color_key, BUTTON_COLORS["default"])
    st.markdown(f"""
    <style>
    .stButton > button {{
        background-color: white !important;
        color: black !important;
        border: 2px solid black !important;
        border-radius: 6px !important;
        font-weight: bold;
        padding: 10px 20px;
        transition: all 0.3s ease;
        font-size: 16px;
    }}
    .stButton > button:hover {{
        background-color: {color} !important;
        color: white !important;
        border-color: {color} !important;
    }}
    </style>
    """, unsafe_allow_html=True)

def render_navbar(title, color=None):
    """Render consistent navbar across all apps."""
    navbar_html = f"""
    <header style="display: flex; justify-content: space-between; align-items: center; 
                   background-color: #06061C; color: white; padding: 15px 2rem;">
        <div style="font-size: 24px; font-weight: bold;">🏥 {title}</div>
        <nav style="display: flex; gap: 20px;">
        </nav>
    </header>
    """
    st.markdown(navbar_html, unsafe_allow_html=True)

# ─────────────── Model Loading ─────────────── #
@st.cache_resource
def load_model(model_path):
    """
    Load and cache a pre-trained model.
    
    Args:
        model_path: Path to the model file
        
    Returns:
        Loaded model object
    """
    import joblib
    return joblib.load(model_path)

# ─────────────── API Call Wrapper ─────────────── #
def call_openai_api(client, prompt, model=None, timeout=30):
    """
    Make API call to OpenRouter with error handling and timeout.
    
    Args:
        client: OpenAI client instance
        prompt: Prompt text to send
        model: Model name (uses default if None)
        timeout: Request timeout in seconds
        
    Returns:
        API response content or None if error
    """
    if model is None:
        model = get_model_name()
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful medical information assistant. Always remind users to consult healthcare professionals for medical advice."},
                {"role": "user", "content": prompt}
            ],
            timeout=timeout
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"API Error: {str(e)}")
        return None
