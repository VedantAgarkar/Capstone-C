# HealthPredict

A comprehensive health prediction web application that leverages machine learning models to predict the risk of diabetes, heart disease, and Parkinson's disease based on patient health metrics.

## Overview

HealthPredict is a full-stack web application designed to provide accessible health risk assessments using state-of-the-art machine learning models. The application features an interactive frontend and a robust backend API that integrates multiple disease prediction models.

## Features

- **Diabetes Prediction**: Assess the risk of diabetes based on health metrics (glucose, blood pressure, BMI, etc.)
- **Heart Disease Prediction**: Evaluate cardiovascular risk using diagnostic indicators
- **Parkinson's Disease Prediction**: Detect potential Parkinson's disease risk through speech analysis features
- **Interactive Dashboard**: User-friendly interface with real-time predictions and health insights
- **AI-Powered Chatbot**: Get health guidance and answers to medical questions
- **Secure Authentication**: User login and signup functionality
- **Responsive Design**: Mobile-friendly interface compatible with all devices

## Project Structure

```
Capstone/
├── backend/
│   ├── main.py                 # FastAPI application entry point
│   ├── utils.py               # Utility functions
│   ├── models/
│   │   ├── schemas.py         # Pydantic data models
│   │   └── __init__.py
│   ├── routes/
│   │   ├── diabetes.py        # Diabetes prediction endpoint
│   │   ├── heart.py           # Heart disease prediction endpoint
│   │   ├── parkinsons.py      # Parkinson's disease prediction endpoint
│   │   └── bot.py             # Chatbot endpoint
│   ├── train_diabetes_model.ipynb
│   ├── train_heart_model.ipynb
│   ├── train_parkinsons_model.ipynb
│   ├── diabetes_model.sav     # Trained diabetes model
│   ├── heart_disease_model.sav
│   ├── parkinsons_model.sav
│   └── *.sav                  # Model scalers and preprocessors
├── frontend/
│   ├── index.html             # Home page
│   ├── product.html           # Products/predictions page
│   ├── login.html             # Login page
│   ├── signup.html            # Registration page
│   ├── about.html             # About page
│   ├── help.html              # Help/FAQ page
│   ├── css/                   # Stylesheets
│   ├── js/                    # JavaScript functionality
│   └── images/                # Assets
├── README.md                  # This file
├── req.txt                    # Python dependencies
└── changelog.txt              # Version history
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Modern web browser

### Backend Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd Capstone
```

2. Install Python dependencies:
```bash
pip install -r req.txt
```

3. Configure environment variables (if needed):
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Run the FastAPI server:
```bash
python backend/main.py
```

The server will start at `http://localhost:8000`

### Frontend Access

The frontend is automatically served by FastAPI at:
- **Home**: `http://localhost:8000/`
- **Products**: `http://localhost:8000/product.html`
- **Login**: `http://localhost:8000/login.html`
- **About**: `http://localhost:8000/about.html`
- **Help**: `http://localhost:8000/help.html`

## Usage

### Making Predictions

1. Navigate to the **Products** page
2. Select the health condition you want to assess (Diabetes, Heart Disease, or Parkinson's)
3. Enter the required health metrics
4. Submit the form to receive a risk prediction

### Using the Chatbot

1. Access the chatbot feature from the main interface
2. Ask health-related questions
3. Receive AI-powered responses and guidance

## API Endpoints

### Diabetes Prediction
- **POST** `/api/diabetes`
- Request body: Patient health metrics (glucose, blood pressure, BMI, etc.)
- Response: Prediction result and confidence score

### Heart Disease Prediction
- **POST** `/api/heart`
- Request body: Cardiac diagnostic indicators
- Response: Risk assessment and health recommendations

### Parkinson's Disease Prediction
- **POST** `/api/parkinsons`
- Request body: Speech analysis features
- Response: Disease risk indicator and confidence score

### Chatbot
- **POST** `/api/chat`
- Request body: Health-related question
- Response: AI-generated response and recommendations

## Technologies Used

- **Backend**: FastAPI, Python, scikit-learn
- **Frontend**: HTML5, CSS3, JavaScript
- **ML Models**: scikit-learn (trained on clinical datasets)
- **APIs**: Google Generative AI (for chatbot functionality)
- **Streaming**: Streamlit (for interactive model dashboards)

## Data Sources

The models are trained on publicly available clinical datasets:
- Diabetes dataset: Contains health metrics from diabetic patients
- Heart disease dataset: Cardiovascular diagnostic indicators
- Parkinson's dataset: Speech signal processing features

## Model Performance

- **Diabetes Model**: Trained to predict Type 2 Diabetes risk with high accuracy
- **Heart Disease Model**: Evaluates cardiovascular disease risk
- **Parkinson's Model**: Detects Parkinson's disease biomarkers from speech

For detailed model metrics, see the individual Jupyter notebooks in the backend directory.

## Security Considerations

- CORS is configured to allow frontend-backend communication
- User authentication is implemented for account management
- Model predictions are provided as risk assessments, not medical diagnoses
- **IMPORTANT**: This application is for educational and informational purposes only. Always consult with healthcare professionals for medical decisions.

## Development

### Training Models

Each disease prediction model has an associated Jupyter notebook:
- `backend/train_diabetes_model.ipynb`
- `backend/train_heart_model.ipynb`
- `backend/train_parkinsons_model.ipynb`

Run these notebooks to:
1. Load and preprocess clinical datasets
2. Train and evaluate ML models
3. Save trained models and scalers

### Adding New Predictions

1. Create a new route file in `backend/routes/`
2. Define the prediction endpoint
3. Add corresponding frontend pages in `frontend/`
4. Update the chatbot knowledge base

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Submit a pull request

## Limitations & Disclaimers

- This application provides predictions for educational purposes only
- Not intended for medical diagnosis or treatment decisions
- Always consult qualified healthcare professionals
- Results should not replace professional medical advice
- Models are based on historical data and may have limitations
- User privacy and data security are important - handle health data responsibly

## License

This project is provided as-is for educational purposes.

## Support

For issues, questions, or suggestions:
1. Check the **Help** page in the application
2. Review the Jupyter notebooks for model details
3. Contact the development team

## Acknowledgments

- Clinical datasets from public health repositories
- scikit-learn and FastAPI communities
- Google Generative AI for chatbot capabilities
- All healthcare professionals who contributed insights

---

**Version**: 1.0.0  
**Last Updated**: January 2026
