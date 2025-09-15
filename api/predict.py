from flask import Flask, request, jsonify
import pandas as pd
import joblib
import os
from pathlib import Path

# Initialize Flask app
app = Flask(__name__)

# Load model and scaler (paths relative to project root)
model_dir = Path(__file__).parent.parent / "models"
model_path = model_dir / "battery_model.pkl"
scaler_path = model_dir / "battery_scaler.pkl"

# Global variables for model and scaler
model = None
scaler = None

def load_models():
    """Load the trained model and scaler"""
    global model, scaler
    try:
        if model is None:
            model = joblib.load(model_path)
        if scaler is None:
            scaler = joblib.load(scaler_path)
        return True
    except Exception as e:
        print(f"Error loading models: {e}")
        return False

@app.route('/api/predict', methods=['POST'])
def predict():
    """Enhanced battery prediction API endpoint with confidence scores"""
    try:
        # Load models if not already loaded
        if not load_models():
            return jsonify({"error": "Failed to load ML models"}), 500
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['voltage', 'current', 'temperature', 'age_months']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing field: {field}"}), 400
        
        # Extract values with default resistance
        voltage = float(data['voltage'])
        current = float(data['current'])
        temperature = float(data['temperature'])
        age_months = int(data['age_months'])
        resistance = float(data.get('resistance', 0.03))
        
        # Validate input ranges
        if not (10.5 <= voltage <= 13.0):
            return jsonify({"error": "Voltage must be between 10.5V and 13.0V"}), 400
        if not (50 <= current <= 350):
            return jsonify({"error": "Current must be between 50A and 350A"}), 400
        if not (-30 <= temperature <= 60):
            return jsonify({"error": "Temperature must be between -30°C and 60°C"}), 400
        if not (1 <= age_months <= 120):
            return jsonify({"error": "Age must be between 1 and 120 months"}), 400
        if not (0.01 <= resistance <= 0.15):
            return jsonify({"error": "Resistance must be between 0.01Ω and 0.15Ω"}), 400
        
        # Create feature dataframe and predict
        features = pd.DataFrame([{
            "voltage": voltage,
            "current": current,
            "temperature": temperature,
            "age_months": age_months,
            "resistance": resistance
        }])
        
        features_scaled = scaler.transform(features)
        prediction = model.predict(features_scaled)[0]
        probabilities = model.predict_proba(features_scaled)[0]
        
        # Enhanced status mapping with confidence
        status_map = {0: "Healthy", 1: "Weak", 2: "Failed"}
        status_emoji = {0: "✅", 1: "⚠️", 2: "❌"}
        status_name = status_map.get(prediction, "Unknown")
        confidence = float(probabilities[prediction]) * 100
        
        # Additional analysis
        risk_factors = []
        if voltage < 12.0:
            risk_factors.append("Low voltage")
        if age_months > 48:
            risk_factors.append("High age")
        if resistance > 0.05:
            risk_factors.append("High resistance")
        if temperature < -10 or temperature > 40:
            risk_factors.append("Extreme temperature")
        
        # Recommendations based on prediction
        recommendations = []
        if prediction == 0:  # Healthy
            recommendations.append("Battery is in good condition")
            recommendations.append("Regular maintenance recommended")
        elif prediction == 1:  # Weak
            recommendations.append("Monitor battery performance closely")
            recommendations.append("Consider replacement soon")
            recommendations.append("Check charging system")
        else:  # Failed
            recommendations.append("Replace battery immediately")
            recommendations.append("Do not rely on this battery")
            recommendations.append("Check vehicle electrical system")
        
        response = {
            "status": f"{status_name} {status_emoji[prediction]}",
            "prediction": int(prediction),
            "confidence": round(confidence, 1),
            "probabilities": {
                "healthy": round(float(probabilities[0]) * 100, 1),
                "weak": round(float(probabilities[1]) * 100, 1),
                "failed": round(float(probabilities[2]) * 100, 1)
            },
            "risk_factors": risk_factors,
            "recommendations": recommendations,
            "input_values": {
                "voltage": voltage,
                "current": current,
                "temperature": temperature,
                "age_months": age_months,
                "resistance": resistance
            }
        }
        
        return jsonify(response)
        
    except ValueError as e:
        return jsonify({"error": f"Invalid input: {e}"}), 400
    except Exception as e:
        return jsonify({"error": f"Prediction failed: {e}"}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Battery Health Prediction API",
        "version": "2.0.0",
        "model_loaded": model is not None and scaler is not None
    })

# Vercel serverless function handler
def handler(event, context):
    """Main handler for Vercel serverless function"""
    return app(event, context)

# Configure Flask for production
app.config['ENV'] = 'production'

# For local development
if __name__ == '__main__':
    load_models()
    app.run(debug=True, host='127.0.0.1', port=5000)