"""
Loads the trained model artifacts ONCE at import time (not per-request -
loading a pickle on every form submission would be slow and wasteful),
and exposes a single function: run_prediction(features_dict).

Artifacts expected in this folder (produced by train_model.py):
    crop_model.pkl, disease_risk_model.pkl,
    scaler_crop.pkl, scaler_risk.pkl,
    crop_encoder.pkl, risk_encoder.pkl,
    feature_importance.json
"""

import json   # For loading feature importance data from JSON
import os     # For building file paths to the model artifacts
import joblib # For loading serialized ML models and preprocessors from .pkl files
import numpy as np  # For array manipulation when preparing model inputs

# Get the absolute directory path of this file (predictor/ml/).
# Model artifact .pkl files are stored in this same directory.
ML_DIR = os.path.dirname(os.path.abspath(__file__))

# The 7 numeric feature names, in the exact order expected by the models.
# This order must match the order used during training (train_model.py).
NUMERIC_FEATURES = ["nitrogen", "phosphorus", "potassium", "temperature", "humidity", "ph", "rainfall"]

# =====================================================================
# Load all trained artifacts ONCE when this module is first imported.
# This happens when Django starts up, not on every HTTP request.
# Loading .pkl files is expensive (~100ms), so we do it once.
# =====================================================================

# The trained crop recommendation model (RandomForestClassifier)
# Input: 7 scaled numeric features -> Output: predicted crop name
crop_model = joblib.load(os.path.join(ML_DIR, "crop_model.pkl"))

# The trained disease risk model (RandomForestClassifier)
# Input: 7 scaled numeric features + 1 encoded crop -> Output: risk level (0/1/2)
risk_model = joblib.load(os.path.join(ML_DIR, "disease_risk_model.pkl"))

# StandardScaler for the crop model: fitted on the 7 numeric features.
# Transforms raw feature values to zero-mean, unit-variance before prediction.
scaler_crop = joblib.load(os.path.join(ML_DIR, "scaler_crop.pkl"))

# StandardScaler for the risk model: fitted on 7 numeric features + crop_encoded.
# Separate scaler because the feature set has 8 dimensions instead of 7.
scaler_risk = joblib.load(os.path.join(ML_DIR, "scaler_risk.pkl"))

# LabelEncoder for crops: maps crop names to integers and back.
# e.g., "rice" <-> some integer (used by the risk model which needs numeric crop input)
crop_encoder = joblib.load(os.path.join(ML_DIR, "crop_encoder.pkl"))

# LabelEncoder for risk levels: maps "Low"/"Medium"/"High" to integers 0/1/2.
# risk_encoder.inverse_transform() converts model output (0/1/2) back to text labels.
risk_encoder = joblib.load(os.path.join(ML_DIR, "risk_encoder.pkl"))

# Load feature importance data from JSON (computed during training).
# Used to show which features most influence the risk prediction.
with open(os.path.join(ML_DIR, "feature_importance.json")) as f:
    FEATURE_IMPORTANCE = json.load(f)

# =====================================================================
# Advisory text lookup: maps each risk level to actionable farming advice.
# Kept as a plain dict for simplicity — not worth a database table.
# These strings are displayed on the result page alongside the prediction.
# =====================================================================
RISK_ADVICE = {
    "Low": (
        "Conditions are currently unfavorable for major disease outbreaks. "
        "Maintain standard monitoring and avoid over-irrigation."
    ),
    "Medium": (
        "Some conditions (humidity/rainfall/pH) are drifting into a range that can favor "
        "fungal or bacterial infections. Increase field inspection frequency and ensure good drainage."
    ),
    "High": (
        "Current soil and climate conditions closely match those favorable for disease outbreaks "
        "(e.g. fungal blight/rust). Consider preventive fungicide application, improve field drainage, "
        "and avoid dense planting to improve airflow."
    ),
}


def run_prediction(features: dict, selected_crop: str = ""):
    """
    Run the full two-stage ML prediction pipeline:

    1. If no crop is selected, use the crop model to recommend the best crop
       for the given soil/climate conditions.
    2. Use the disease risk model to predict the risk level (Low/Medium/High)
       for the given (or recommended) crop under those conditions.

    Args:
        features: dict with keys nitrogen, phosphorus, potassium, temperature,
                  humidity, ph, rainfall (all floats from the form)
        selected_crop: optional crop name string. If empty, the crop model
                       recommends one first.

    Returns:
        A dict containing:
            - recommended_crop: the final crop name
            - disease_risk: "Low", "Medium", or "High"
            - confidence: model's confidence as a percentage (0-100)
            - advice: actionable text for the farmer
            - top_features: list of the 3 most important features
            - risk_probabilities: dict of {risk_level: percentage} for all classes
    """
    # Convert the features dict into a numpy array in the correct feature order.
    # Shape: (1, 7) — a single prediction sample with 7 features.
    x = np.array([[features[f] for f in NUMERIC_FEATURES]])

    # --- Step 1: Recommend crop if the user didn't select one ---
    if not selected_crop:
        # Scale the raw features using the crop model's scaler
        x_crop_scaled = scaler_crop.transform(x)
        # Predict the crop name (e.g., "rice", "wheat")
        recommended_crop = crop_model.predict(x_crop_scaled)[0]
    else:
        # User chose a crop — use it directly
        recommended_crop = selected_crop

    # --- Step 2: Predict disease risk for the (chosen or recommended) crop ---
    # Encode the crop name to a numeric value using the LabelEncoder
    crop_encoded = crop_encoder.transform([recommended_crop])[0]

    # Concatenate the 7 numeric features with the encoded crop value
    # to create an 8-feature input vector for the risk model.
    # np.hstack joins the two arrays horizontally: (1,7) + (1,1) -> (1,8)
    x_risk = np.hstack([x, [[crop_encoded]]])

    # Scale the 8-feature vector using the risk model's scaler
    x_risk_scaled = scaler_risk.transform(x_risk)

    # Get probability predictions for all 3 risk classes (Low, Medium, High).
    # predict_proba() returns an array like [[0.1, 0.3, 0.6]] meaning
    # 10% Low, 30% Medium, 60% High.
    risk_proba = risk_model.predict_proba(x_risk_scaled)[0]

    # Find the index of the class with the highest probability
    risk_pred_idx = np.argmax(risk_proba)

    # Convert the integer index (0/1/2) back to the text label ("High"/"Low"/"Medium")
    risk_label = risk_encoder.inverse_transform([risk_pred_idx])[0]

    # Extract the confidence (probability) of the winning class as a float
    confidence = float(risk_proba[risk_pred_idx])

    # Get the top 3 most important features from the risk model's global feature importance.
    # This is a simple explainability approach: shows which input features
    # most influence the risk prediction across all trees in the forest.
    importances = FEATURE_IMPORTANCE["risk_model"]
    # Sort features by importance descending and take top 3
    top_features = sorted(importances.items(), key=lambda kv: kv[1], reverse=True)[:3]

    # Build and return the complete prediction result dictionary
    return {
        "recommended_crop": recommended_crop,           # Final crop name
        "disease_risk": risk_label,                     # "Low", "Medium", or "High"
        "confidence": round(confidence * 100, 1),       # Confidence as percentage (e.g., 72.5)
        "advice": RISK_ADVICE[risk_label],              # Actionable advisory text
        "top_features": [                               # Top 3 most influential features
            {"name": name, "importance": round(val * 100, 1)}
            for name, val in top_features
        ],
        "risk_probabilities": {                         # Probability breakdown for all risk classes
            cls: round(float(p) * 100, 1)
            for cls, p in zip(risk_encoder.classes_, risk_proba)
        },
    }
