import os
import sys
import logging
import pickle
import json
import re
import joblib 
import pandas as pd
from openai import OpenAI
from fastapi import FastAPI, HTTPException, Body, Header, Depends, Request
from pydantic import BaseModel, EmailStr
from backend.database import get_db_connection, init_db, log_prediction
import sqlite3
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from passlib.context import CryptContext
import jwt
import warnings
try:
    from sklearn.exceptions import InconsistentVersionWarning
    warnings.filterwarnings("ignore", category=InconsistentVersionWarning)
except ImportError:
    pass
warnings.filterwarnings("ignore", module="jwt")
from datetime import datetime, timedelta

_model_cache = {}

class DiabetesInput(BaseModel):
    pregnancies: int
    glucose: int
    blood_pressure: int
    skin_thickness: int
    insulin: int
    bmi: float
    diabetes_pedigree: float
    age: int
    family_history: str
    physical_activity: str
    smoking: str
    diet_quality: str
    hypertension: str
    sleep_hours: int
    sex: str
    lang: str = "en"

class HeartInput(BaseModel):
    age: int
    sex: str
    chest_pain: str
    resting_bp: int
    cholesterol: int
    fasting_blood_sugar: str
    rest_ecg: str
    max_heart_rate: int
    exercise_induced_angina: str
    st_depression: float
    slope: str
    ca: int
    thal: str
    family_history: str
    diabetes: str
    hypertension: str
    smoking: str
    exercise_frequency: str
    bmi: float
    lang: str = "en"

class ParkinsonsInput(BaseModel):
    mdvp_fo: float
    mdvp_fhi: float
    mdvp_flo: float
    mdvp_jitter_percent: float
    mdvp_jitter_abs: float
    mdvp_rap: float
    mdvp_ppq: float
    jitter_ddp: float
    mdvp_shimmer: float
    mdvp_shimmer_db: float
    shimmer_apq3: float
    shimmer_apq5: float
    mdvp_apq: float
    shimmer_dda: float
    nhr: float
    hnr: float
    rpde: float
    dfa: float
    spread1: float
    spread2: float
    d2: float
    ppe: float
    age: int
    sex: str
    family_history: str
    lang: str = "en"

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    lang: str = "en"

def _get_ai_summary(prompt: str, lang: str) -> str:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return "AI summary disabled: OPENROUTER_API_KEY is missing from your .env file."
        
    try:
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key
        )
        model = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.2-3b-instruct:free")
        
        system_text = "You are a helpful medical assistant. "
        if lang == "mr":
            system_text += "RESPOND IN MARATHI. "
            
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_text},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=800
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI summary currently unavailable. Error: {str(e)}"

# Load environment variables from .env file (try both root and backend folders)
backend_env = os.path.join(os.path.dirname(__file__), ".env")
root_env = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
if os.path.exists(root_env):
    load_dotenv(root_env)
elif os.path.exists(backend_env):
    load_dotenv(backend_env)
else:
    load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Password hashing configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        # Fallback for old plain-text passwords
        return plain_password == hashed_password

def get_password_hash(password):
    return pwd_context.hash(password)

# JWT constants
SECRET_KEY = os.getenv("JWT_SECRET", "supersecretkey123")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440 # 24 hours

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        return {"email": email, "is_admin": payload.get("is_admin", False)}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class UserRegister(BaseModel):
    email: EmailStr
    password: str
    fullname: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

@app.post("/api/register")
async def register(user: UserRegister):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Normalize email to lowercase
        email_normalized = user.email.strip().lower()
        
        cursor.execute(
            "INSERT INTO users (email, password, fullname) VALUES (?, ?, ?)",
            (email_normalized, get_password_hash(user.password), user.fullname)
        )
        conn.commit()
        return {"message": "User registered successfully"}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Email already registered")
    finally:
        conn.close()

@app.post("/api/login")
async def login(user: UserLogin):
    conn = get_db_connection()
    cursor = conn.cursor()
    # Parameterized query to prevent SQL injection
    # Normalize email
    email_normalized = user.email.strip().lower()
    
    cursor.execute(
        "SELECT * FROM users WHERE LOWER(email) = ?",
        (email_normalized,)
    )
    db_user = cursor.fetchone()
    conn.close()
    
    if db_user and verify_password(user.password, db_user["password"]):
        token = create_access_token({
            "sub": db_user["email"],
            "is_admin": bool(db_user["is_admin"])
        })
        return {
            "message": "Login successful",
            "token": token,
            "user": {
                "email": db_user["email"],
                "fullname": db_user["fullname"],
                "is_admin": bool(db_user["is_admin"])
            }
        }
    else:
        raise HTTPException(status_code=401, detail="Invalid email or password")

@app.get("/api/admin/stats")
async def get_admin_stats(current_user: dict = Depends(get_current_user)):
    if not current_user["is_admin"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    email = current_user["email"]
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get total user count
    cursor.execute("SELECT COUNT(*) as count FROM users")
    user_count = cursor.fetchone()["count"]
    
    # Get recent predictions
    cursor.execute("""
        SELECT p.*, IFNULL(u.fullname, 'Guest User') as fullname 
        FROM predictions p 
        LEFT JOIN users u ON p.user_id = u.id 
        ORDER BY timestamp DESC LIMIT 10
    """)
    recent_predictions = [dict(row) for row in cursor.fetchall()]
    
    # Get prediction breakdown
    cursor.execute("SELECT type, COUNT(*) as count FROM predictions GROUP BY type")
    breakdown = {row["type"]: row["count"] for row in cursor.fetchall()}
    
    conn.close()
    
    return {
        "total_users": user_count,
        "recent_predictions": recent_predictions,
        "prediction_breakdown": breakdown
    }

@app.get("/api/user/stats")
async def get_user_stats(current_user: dict = Depends(get_current_user)):
    from backend.database import get_user_predictions
    import re
    
    email = current_user["email"]
    predictions = get_user_predictions(email)
    
    # Calculate Wellness Score
    latest_by_type = {}
    for p in predictions:
        if p["type"] not in latest_by_type:
            latest_by_type[p["type"]] = p
            
    scores = []
    assessment_types = ["Heart Disease", "Diabetes", "Parkinson's"]
    
    for t in assessment_types:
        if t in latest_by_type:
            outcome = latest_by_type[t]["outcome"]
            # Extract number from "75.0% Risk"
            match = re.search(r"(\d+\.?\d*)%", outcome)
            if match:
                risk_pct = float(match.group(1))
                scores.append(100 - risk_pct)
            else:
                scores.append(100)
        else:
            scores.append(100)
            
    wellness_score = sum(scores) / len(assessment_types)
    
    return {
        "predictions": predictions,
        "wellness_score": round(wellness_score, 1)
    }

def extract_email(authorization: str):
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload.get("sub")
        except:
            pass
    return None

@app.post("/api/predict/diabetes")
async def predict_diabetes(req: DiabetesInput, request: Request):
    # Load Models
    if "diabetes_model" not in _model_cache:
        _model_cache["diabetes_model"] = joblib.load(os.path.join(os.path.dirname(__file__), "diabetes_model.sav"))
        _model_cache["diabetes_scaler"] = pickle.load(open(os.path.join(os.path.dirname(__file__), "diabetes_scaler.sav"), "rb"))
        
    model = _model_cache["diabetes_model"]
    scaler = _model_cache["diabetes_scaler"]
    
    # Feature DataFrame
    features = pd.DataFrame([[
        req.pregnancies, req.glucose, req.blood_pressure, req.skin_thickness,
        req.insulin, req.bmi, req.diabetes_pedigree, req.age
    ]], columns=['Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age'])
    
    scaled_feats = scaler.transform(features)
    proba = model.predict_proba(scaled_feats)[0]
    risk_pct = float(proba[1]) * 100
    
    if risk_pct > 70:
        risk_class = "उच्च धोका" if req.lang == "mr" else "HIGH RISK"
    elif risk_pct > 40:
        risk_class = "मध्यम धोका" if req.lang == "mr" else "MODERATE RISK"
    else:
        risk_class = "कमी धोका" if req.lang == "mr" else "LOW RISK"
        
    prompt = f"""
    Please provide a brief, easy-to-understand health assessment for a patient with the following profile:
    - Age: {req.age}
    - Sex: {req.sex}
    - BMI: {req.bmi}
    - Glucose Level: {req.glucose}
    - Blood Pressure: {req.blood_pressure}
    - Family History: {req.family_history}
    - Physical Activity: {req.physical_activity}
    - Diet Quality: {req.diet_quality}
    - AI Model Calculated Diabetes Risk: {risk_pct:.1f}%

    Structure your response with:
    1. A brief summary of their current risk level.
    2. 2-3 key positive factors (if any).
    3. 2-3 areas for improvement.
    4. Actionable next steps.

    Keep it encouraging but informative. Remind them to consult a doctor. Do not use complex medical jargon or output in markdown unless absolutely necessary.
    """
    
    assessment = _get_ai_summary(prompt, req.lang)
    
    email = extract_email(request.headers.get("Authorization"))
    log_prediction(email, "Diabetes", req.model_dump() if hasattr(req, "model_dump") else req.dict(), f"{risk_pct:.1f}% Risk")
    
    return {"risk_pct": risk_pct, "risk_class": risk_class, "assessment": assessment, "lang": req.lang}


@app.post("/api/predict/heart")
async def predict_heart(req: HeartInput, request: Request):
    if "heart_model" not in _model_cache:
        _model_cache["heart_model"] = joblib.load(os.path.join(os.path.dirname(__file__), "heart_disease_model.sav"))
        _model_cache["heart_scaler"] = joblib.load(os.path.join(os.path.dirname(__file__), "heart_scaler.sav"))
        
    model = _model_cache["heart_model"]
    scaler = _model_cache["heart_scaler"]
    
    sex_encoded = 1 if req.sex == "Male" else 0
    
    cp_mapping = {"Asymptomatic": 0, "Non-anginal Pain": 1, "Atypical Angina": 2, "Typical Angina": 3}
    chest_pain_encoded = cp_mapping.get(req.chest_pain, 0)
    
    ecg_mapping = {"Normal": 0, "ST-T Abnormality": 1, "Left Ventricular Hypertrophy": 2}
    rest_ecg_encoded = ecg_mapping.get(req.rest_ecg, 0)
    
    fbs_encoded = 1 if req.fasting_blood_sugar == "Yes" else 0
    angina_encoded = 1 if req.exercise_induced_angina == "Yes" else 0
    
    slope_mapping = {"Upsloping": 0, "Flat": 1, "Downsloping": 2}
    slope_encoded = slope_mapping.get(req.slope, 0)
    
    thal_mapping = {"Normal": 1, "Fixed Defect": 2, "Reversible Defect": 3}
    thal_encoded = thal_mapping.get(req.thal, 1)
    
    features = pd.DataFrame([[
        req.age, sex_encoded, chest_pain_encoded, req.resting_bp, req.cholesterol,
        fbs_encoded, rest_ecg_encoded, req.max_heart_rate, angina_encoded, req.st_depression,
        slope_encoded, req.ca, thal_encoded
    ]], columns=['age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 'restecg', 'thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal'])
    
    scaled_feats = scaler.transform(features)
    proba = model.predict_proba(scaled_feats)[0]
    risk_pct = float(proba[1]) * 100
    
    if risk_pct > 70:
        risk_class = "उच्च धोका" if req.lang == "mr" else "HIGH RISK"
    elif risk_pct > 40:
        risk_class = "मध्यम धोका" if req.lang == "mr" else "MODERATE RISK"
    else:
        risk_class = "कमी धोका" if req.lang == "mr" else "LOW RISK"
        
    prompt = f"""
    Please provide a brief, easy-to-understand health assessment for a patient with the following profile:
    - Age: {req.age}
    - Sex: {req.sex}
    - BMI: {req.bmi}
    - Blood Pressure: {req.resting_bp}
    - Cholesterol: {req.cholesterol}
    - Exercise Frequency: {req.exercise_frequency}
    - Smoking Status: {req.smoking}
    - Family History: {req.family_history}
    - Max Heart Rate: {req.max_heart_rate}
    - AI Model Calculated Heart Risk: {risk_pct:.1f}%

    Structure your response with:
    1. A brief summary of their current risk level.
    2. 2-3 key positive factors.
    3. 2-3 areas for improvement.
    4. Actionable next steps.

    Keep it encouraging but informative. Remind them to consult a doctor.
    """
    
    assessment = _get_ai_summary(prompt, req.lang)
    
    email = extract_email(request.headers.get("Authorization"))
    log_prediction(email, "Heart Disease", req.model_dump() if hasattr(req, "model_dump") else req.dict(), f"{risk_pct:.1f}% Risk")
    
    return {"risk_pct": risk_pct, "risk_class": risk_class, "assessment": assessment, "lang": req.lang}

@app.post("/api/predict/parkinsons")
async def predict_parkinsons(req: ParkinsonsInput, request: Request):
    if "parkinsons_model" not in _model_cache:
        _model_cache["parkinsons_model"] = joblib.load(os.path.join(os.path.dirname(__file__), "parkinsons_model.sav"))
        _model_cache["parkinsons_scaler"] = pickle.load(open(os.path.join(os.path.dirname(__file__), "parkinsons_scaler.sav"), "rb"))
        
    model = _model_cache["parkinsons_model"]
    scaler = _model_cache["parkinsons_scaler"]
    
    cols = ['MDVP:Fo(Hz)', 'MDVP:Fhi(Hz)', 'MDVP:Flo(Hz)', 'MDVP:Jitter(%)',
       'MDVP:Jitter(Abs)', 'MDVP:RAP', 'MDVP:PPQ', 'Jitter:DDP',
       'MDVP:Shimmer', 'MDVP:Shimmer(dB)', 'Shimmer:APQ3', 'Shimmer:APQ5',
       'MDVP:APQ', 'Shimmer:DDA', 'NHR', 'HNR', 'RPDE', 'DFA',
       'spread1', 'spread2', 'D2', 'PPE']
       
    features = pd.DataFrame([[
        req.mdvp_fo, req.mdvp_fhi, req.mdvp_flo, req.mdvp_jitter_percent,
        req.mdvp_jitter_abs, req.mdvp_rap, req.mdvp_ppq, req.jitter_ddp,
        req.mdvp_shimmer, req.mdvp_shimmer_db, req.shimmer_apq3, req.shimmer_apq5,
        req.mdvp_apq, req.shimmer_dda, req.nhr, req.hnr, req.rpde, req.dfa,
        req.spread1, req.spread2, req.d2, req.ppe
    ]], columns=cols)
    
    scaled_feats = scaler.transform(features)
    proba = model.predict_proba(scaled_feats)[0]
    risk_pct = float(proba[1]) * 100
    
    if risk_pct > 70:
        risk_class = "उच्च धोका" if req.lang == "mr" else "HIGH RISK"
    elif risk_pct > 40:
        risk_class = "मध्यम धोका" if req.lang == "mr" else "MODERATE RISK"
    else:
        risk_class = "कमी धोका" if req.lang == "mr" else "LOW RISK"
        
    prompt = f"""
    Please provide a brief, easy-to-understand health assessment for a patient with the following profile:
    - Age: {req.age}
    - Sex: {req.sex}
    - Family History of Parkinson's: {req.family_history}
    - AI Model Calculated Parkinson's Risk (based on voice analysis): {risk_pct:.1f}%

    Structure your response with:
    1. A brief summary of their current risk level based on the voice analysis.
    2. What these voice metrics generally indicate (without diagnosing).
    3. Actionable next steps (seeing a neurologist if risk is high).

    Keep it encouraging but informative. Remind them to consult a doctor. 
    """
    
    assessment = _get_ai_summary(prompt, req.lang)
    
    email = extract_email(request.headers.get("Authorization"))
    log_prediction(email, "Parkinson's", req.model_dump() if hasattr(req, "model_dump") else req.dict(), f"{risk_pct:.1f}% Risk")
    
    return {"risk_pct": risk_pct, "risk_class": risk_class, "assessment": assessment, "lang": req.lang}


@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest, request: Request):
    if req.lang == "mr":
        system_prompt = """तुम्ही HealthPredict प्लॅटफॉर्मसाठी वैद्यकीय माहिती सहाय्यक आणि ट्रायज (Triage) तज्ञ आहात.
कृपया स्पष्ट मराठी भाषेत उत्तरे द्या.

ट्रायज क्षमता:
जर वापरकर्त्याने लक्षणांचे वर्णन केले तर त्याचे विश्लेषण करा आणि योग्य हेल्थ प्रिडिक्ट मूल्यांकनाची शिफारस करा:
१. हृदय रोग मूल्यांकन: छातीत दुखणे, धाप लागणे, अनियमित हृदयाचे ठोके यासाठी. (दुवा: heart.html)
२. मधुमेह जोखीम मूल्यांकन: वारंवार तहान लागणे, थकवा, अंधुक दृष्टी यासाठी. (दुवा: diabetes.html)
३. पार्किन्सन रोग मूल्यांकन: थरथर, कडकपणा, आवाजातील बदल यासाठी. (दुवा: parkinsons.html)

जर लक्षणे गंभीर असतील तर त्वरित आपत्कालीन उपचारांची शिफारस करा.
महत्त्वाचे: वापरकर्त्याला नेहमी आठवण करून द्या की तुम्ही व्यावसायिक वैद्यकीय सल्ल्याचा पर्याय नाही आहात. If the user asks a non-medical question, say it's not medical related."""
    else:
        system_prompt = """You are a medical information assistant and triage expert for the HealthPredict platform.
Answer in clear, plain English. 

TRIAGE CAPABILITY:
If a user describes symptoms, analyze them and suggest the appropriate HealthPredict assessment:
1. Heart Disease Assessment: For chest pain, shortness of breath, irregular heartbeat. (Link: heart.html)
2. Diabetes Risk Assessment: For frequent thirst, fatigue, blurred vision. (Link: diabetes.html)
3. Parkinson's Disease Assessment: For tremors, stiffness, voice changes. (Link: parkinsons.html)

dont provide of any kind of redicect link to anything just answer what is asked 
If symptoms are severe, suggest emergency care.
IMPORTANT: Always remind the user that you are not a substitute for professional medical advice. If the user asks a non-medical question, say it's not medical related."""

    try:
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY")
        )
        model = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.2-3b-instruct:free")
        
        api_messages = [{"role": "system", "content": system_prompt}]
        for m in req.messages:
            api_messages.append({"role": m.role, "content": m.content})
            
        response = client.chat.completions.create(
            model=model,
            messages=api_messages,
            temperature=0.7,
            max_tokens=800
        )
        reply = response.choices[0].message.content
        
        email = extract_email(request.headers.get("Authorization"))
        last_user_msg = req.messages[-1].content if req.messages else "Empty"
        log_prediction(email, "Medical Bot", last_user_msg, "Responded")
        
        return {"reply": reply, "lang": req.lang}
    except Exception as e:
        return {"reply": f"AI summary currently unavailable. Error: {str(e)}", "lang": req.lang}


@app.on_event("startup")
def startup_event():
    """Initialize database on startup."""
    init_db()

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
