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

# ─────────────── Localization ─────────────── #
TRANSLATIONS = {
    "en": {
        "submit": "Submit Assessment",
        "assessing": "Analyzing data...",
        "success": "Assessment Complete!",
        "error": "Error: ",
        "high_risk": "HIGH RISK",
        "moderate_risk": "MODERATE RISK",
        "low_risk": "LOW RISK"
    },
    "mr": {
        "submit": "जोखीम तपासा",
        "assessing": "डेटाचे विश्लेषण करत आहे...", 
        "success": "मूल्यांकन पूर्ण झाले!",
        "error": "त्रुटी: ",
        "high_risk": "उच्च धोका",
        "moderate_risk": "मध्यम धोका",
        "low_risk": "कमी धोका"
    }
}

def get_language():
    """
    Get current language from query parameters.
    Defaults to 'en' if not present or invalid.
    """
    try:
        # Streamlit 1.30+ uses st.query_params
        # Check if 'lang' is in query params
        qp = st.query_params
        lang = qp.get("lang", "en")
        # Handle if it returns a list (older versions) or string
        if isinstance(lang, list):
            return lang[0] if lang else "en"
        return lang if lang in ["en", "mr"] else "en"
    except:
        return "en"

def get_email():
    """
    Get user email from query parameters for logging.
    Returns None if not provided.
    """
    try:
        # Streamlit 1.30+
        if "email" in st.query_params:
            return st.query_params["email"]
        return None
    except:
        return None

def get_text(key, lang=None):
    """Get translated text for a key."""
    if lang is None:
        lang = get_language()
    return TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, key)

# ─────────────── API Call Wrapper ─────────────── #
def call_openai_api(client, prompt=None, model=None, timeout=30, system_prompt=None, messages=None):
    """
    Make API call to OpenRouter with error handling and timeout.
    
    Args:
        client: OpenAI client instance
        prompt: Single prompt text (used if messages is None)
        model: Model name (uses default if None)
        timeout: Request timeout in seconds
        system_prompt: System instructions for the model
        messages: Full conversation history list
        d
    Returns:
        API response content or None if error
    """
    if model is None:
        model = get_model_name()
    
    if system_prompt is None:
        lang = get_language()
        system_prompt = "You are a helpful medical information assistant. Always remind users to consult healthcare professionals for medical advice."
        
        if lang == "mr":
            system_prompt += " PLEASE RESPOND IN MARATHI LANGUAGE (मराठी). Transliterate technical medical terms if necessary but keep the explanation in Marathi."
    
    # Construct final messages list
    final_messages = []
    if messages:
        # If history provided, use it
        final_messages = messages.copy()
        # Ensure system prompt is at the top if not present or different
        if not any(m.get('role') == 'system' for m in final_messages):
            final_messages.insert(0, {"role": "system", "content": system_prompt})
    else:
        # Fallback to single prompt
        final_messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=final_messages,
            timeout=timeout
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"API Error: {e}")
        return None

def render_risk_meter(risk_percentage):
    """
    Render a visual risk meter (gauge) using HTML/CSS.
    
    Args:
        risk_percentage (float): Risk percentage (0-100)
    """
    # Clamp value between 0 and 100
    risk_value = max(0, min(100, risk_percentage))
    
    # Determine color based on risk
    if risk_value < 40:
        color = "#28a745" # Green
        label = "LOW RISK"
    elif risk_value < 70:
        color = "#fd7e14" # Orange
        label = "MODERATE RISK"
    else:
        color = "#dc3545" # Red
        label = "HIGH RISK"
        
    # HTML for the meter
    meter_html = f"""
    <div style="margin: 20px 0; font-family: sans-serif;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 5px; font-weight: bold; color: #555;">
            <span>0%</span>
            <span>Risk Probability</span>
            <span>100%</span>
        </div>
        <div style="
            position: relative;
            height: 30px;
            background: linear-gradient(to right, #28a745 0%, #ffc107 50%, #dc3545 100%);
            border-radius: 15px;
            box-shadow: inset 0 2px 5px rgba(0,0,0,0.2);
        ">
            <div style="
                position: absolute;
                left: {risk_value}%;
                top: -10px;
                transform: translateX(-50%);
                width: 0; 
                height: 0; 
                border-left: 10px solid transparent;
                border-right: 10px solid transparent;
                border-top: 15px solid #333;
            "></div>
            <div style="
                position: absolute;
                left: {risk_value}%;
                top: -35px;
                transform: translateX(-50%);
                background-color: #333;
                color: white;
                padding: 2px 8px;
                border-radius: 4px;
                font-size: 14px;
                font-weight: bold;
                white-space: nowrap;
            ">
                {risk_value:.1f}%
            </div>
        </div>
        <div style="text-align: center; margin-top: 15px; font-size: 18px; font-weight: bold; color: {color};">
            {label}
        </div>
    </div>
    """
    st.markdown(meter_html, unsafe_allow_html=True)

def generate_pdf_report(content, risk_pct, title="Start", patient_info="Not Provided"):
    """
    Generate a formatted PDF report with risk meter visualization.
    """
    from fpdf import FPDF
    import io
    import re
    import os
    
    lang = get_language()
    pdf_labels = {
        "en": {
            "subtitle": "Medical Risk Assessment AI",
            "footer": "HealthPredict AI - Not a substitute for professional medical advice | Page ",
            "risk_prob": "Risk Probability: "
        },
        "mr": {
            "subtitle": "वैद्यकीय जोखीम मूल्यांकन एआय",
            "footer": "HealthPredict AI - व्यावसायिक वैद्यकीय सल्ल्याचा पर्याय नाही | पृष्ठ ",
            "risk_prob": "जोखीम शक्यता: "
        }
    }
    L_PDF = pdf_labels.get(lang, pdf_labels["en"])
    # Clean L_PDF values
    L_PDF = {k: "".join(c for c in v if ord(c) < 0x10000) for k, v in L_PDF.items()}

    # 1. First, check and add Unicode font if needed
    font_candidates = [
        "C:\\Windows\\Fonts\\mangal.ttf",
        "C:\\Windows\\Fonts\\kokila.ttf",
        "C:\\Windows\\Fonts\\nirmala.ttf"
    ]
    
    # Create a temporary PDF to check font loading
    temp_pdf = FPDF()
    has_unicode_font = False
    active_font_path = None
    for fp in font_candidates:
        if os.path.exists(fp):
            try:
                temp_pdf.add_font("MarathiFont", style="", fname=fp)
                has_unicode_font = True
                active_font_path = fp
                break
            except:
                continue

    class PDF(FPDF):
        def header(self):
            # Banner color
            self.set_fill_color(6, 6, 28) # #06061C dark blue
            self.rect(0, 0, 210, 40, 'F')
            
            # Title
            self.set_font('Arial', 'B', 24)
            self.set_text_color(255, 255, 255) # White
            self.cell(0, 20, "HealthPredict", 0, 1, 'C', False)
            
            # Subtitle
            if lang == "mr" and has_unicode_font:
                self.set_font("MarathiFont", "", 12)
            else:
                self.set_font('Arial', 'I', 12)
            self.cell(0, 5, L_PDF["subtitle"], 0, 1, 'C', False)
            self.ln(20)

        def footer(self):
            self.set_y(-15)
            if lang == "mr" and has_unicode_font:
                self.set_font("MarathiFont", "", 8)
            else:
                self.set_font('Arial', 'I', 8)
            self.set_text_color(128, 128, 128)
            self.cell(0, 10, L_PDF["footer"] + str(self.page_no()), 0, 0, 'C')

    # Create PDF object
    pdf = PDF()
    if has_unicode_font:
        pdf.add_font("MarathiFont", style="", fname=active_font_path)
    
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    
    # ─── REPORT TITLE ───
    # Helper to strip characters not supported by standard fonts (like emojis)
    def clean_text_for_pdf(text):
        if not text: return ""
        # Remove characters above 0xFFFF (emojis)
        return "".join(c for c in text if ord(c) < 0x10000)

    title = clean_text_for_pdf(title)
    content = clean_text_for_pdf(content)
    patient_info = clean_text_for_pdf(patient_info)

    if has_unicode_font:
        pdf.set_font("MarathiFont", "", 18)
    else:
        pdf.set_font("Arial", "B", 18)
        
    pdf.set_text_color(183, 147, 71) # Gold #B79347
    pdf.cell(0, 10, title, 0, 1, 'L')
    
    # ─── PATIENT INFO ───
    pdf.set_font("Arial", "I", 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, patient_info, 0, 1, 'L')
    pdf.ln(5)
    
    # ─── VISUAL RISK METER ───
    if lang == "mr" and has_unicode_font:
        pdf.set_font("MarathiFont", "", 12)
    else:
        pdf.set_font("Arial", "B", 12)
        
    pdf.set_text_color(50, 50, 50)
    pdf.cell(0, 10, f"{L_PDF['risk_prob']}{risk_pct:.1f}%", 0, 1, 'L')

    
    # Draw Meter Background
    bar_x = 10
    bar_y = pdf.get_y() + 2
    bar_w = 190
    bar_h = 10
    
    pdf.set_fill_color(40, 167, 69)
    pdf.rect(bar_x, bar_y, bar_w * 0.4, bar_h, 'F')
    pdf.set_fill_color(253, 126, 20)
    pdf.rect(bar_x + bar_w * 0.4, bar_y, bar_w * 0.3, bar_h, 'F')
    pdf.set_fill_color(220, 53, 69)
    pdf.rect(bar_x + bar_w * 0.7, bar_y, bar_w * 0.3, bar_h, 'F')
    
    clean_pct = max(0, min(100, risk_pct))
    arrow_x = bar_x + (bar_w * (clean_pct / 100))
    pdf.set_fill_color(0, 0, 0)
    pdf.rect(arrow_x - 1.5, bar_y - 8, 3, 6, 'F')
    
    pdf.ln(20)
    
    # PRE-PROCESS CONTENT: Fix spacing to prevent 34-page bloat
    content = re.sub(r'\n{2,}', '\n', content)
    lines = content.split('\n')
    
    if not has_unicode_font:
        content = content.replace(u'\xa0', u' ')
        try:
            content = content.encode('latin-1', 'replace').decode('latin-1')
        except:
            pass
        lines = content.split('\n')

    for line in lines:
        line = line.strip()
        if not line:
            pdf.ln(3)
            continue
            
        if has_unicode_font:
             if line.startswith('###'):
                 pdf.set_font("MarathiFont", "", 14)
                 pdf.set_text_color(6, 6, 28)
             elif line.startswith('##'):
                 pdf.set_font("MarathiFont", "", 13)
                 pdf.set_text_color(0, 0, 0)
             else:
                 pdf.set_font("MarathiFont", "", 11)
                 pdf.set_text_color(0, 0, 0)
 
             clean_line = line.replace('#', '').replace('**', '').strip()
             # Use multi_cell for reliable paragraph wrapping
             pdf.multi_cell(0, 8, clean_line)
             pdf.ln(1)
             continue
            
        # Fallback path
        if line.startswith('###'):
            pdf.set_font("Arial", "B", 14)
            pdf.set_text_color(6, 6, 28)
            clean_line = line.replace('#', '').strip()
            pdf.multi_cell(0, 10, clean_line)
        elif line.startswith('##'):
            pdf.set_font("Arial", "B", 13)
            clean_line = line.replace('#', '').strip()
            pdf.multi_cell(0, 10, clean_line)
        else:
            pdf.set_font("Arial", "", 11)
            clean_line = line.replace('**', '').strip()
            pdf.multi_cell(0, 8, clean_line)
        pdf.ln(1)
            
    try:
        pdf_data = pdf.output()
        if isinstance(pdf_data, bytearray):
            return bytes(pdf_data)
        return pdf_data
    except Exception as e:
        print(f"PDF Output Error: {e}")
        return b"" 

