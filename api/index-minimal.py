"""
Pandas-free Vercel-compatible API for battery health prediction
"""
import json
import numpy as np
import joblib
from pathlib import Path

# Load models once when function starts
model_dir = Path(__file__).parent.parent / "models"
model = None
scaler = None

def load_models():
    """Load ML models"""
    global model, scaler
    try:
        if model is None:
            model = joblib.load(model_dir / "battery_model.pkl")
        if scaler is None:
            scaler = joblib.load(model_dir / "battery_scaler.pkl")
        return True
    except Exception as e:
        print(f"Model loading error: {e}")
        return False

def handler(event, context):
    """Vercel serverless function entry point"""
    try:
        # Load models if needed
        if not load_models():
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type'
                },
                'body': json.dumps({"error": "Failed to load ML models"})
            }
        
        # Parse request
        http_method = event.get('httpMethod', 'GET')
        path = event.get('path', '/')
        
        # Handle CORS preflight
        if http_method == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type'
                },
                'body': ''
            }
        
        # Health check endpoint
        if path.endswith('/health') or http_method == 'GET':
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    "status": "healthy",
                    "service": "Battery Health Prediction API",
                    "version": "2.1.0",
                    "model_loaded": True,
                    "framework": "pandas-free"
                })
            }
        
        # Prediction endpoint
        if http_method == 'POST':
            body = json.loads(event.get('body', '{}'))
            
            # Validate required fields
            required_fields = ['voltage', 'current', 'temperature', 'age_months']
            for field in required_fields:
                if field not in body:
                    return {
                        'statusCode': 400,
                        'headers': {
                            'Content-Type': 'application/json',
                            'Access-Control-Allow-Origin': '*'
                        },
                        'body': json.dumps({"error": f"Missing field: {field}"})
                    }
            
            # Extract and validate values
            try:
                voltage = float(body['voltage'])
                current = float(body['current'])
                temperature = float(body['temperature'])
                age_months = int(body['age_months'])
                resistance = float(body.get('resistance', 0.03))
            except (ValueError, TypeError):
                return {
                    'statusCode': 400,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({"error": "Invalid number format in input"})
                }
            
            # Validate ranges
            if not (10.5 <= voltage <= 13.0):
                return {
                    'statusCode': 400,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({"error": "Voltage must be between 10.5V and 13.0V"})
                }
            
            # Create feature array (no pandas)
            features = np.array([[voltage, current, temperature, age_months, resistance]])
            
            # Scale features and make prediction
            features_scaled = scaler.transform(features)
            prediction = model.predict(features_scaled)[0]
            probabilities = model.predict_proba(features_scaled)[0]
            
            # Generate response
            status_map = {0: "Healthy", 1: "Weak", 2: "Failed"}
            status_emoji = {0: "✅", 1: "⚠️", 2: "❌"}
            status_name = status_map.get(prediction, "Unknown")
            confidence = float(probabilities[prediction]) * 100
            
            # Risk factors
            risk_factors = []
            if voltage < 12.0:
                risk_factors.append("Low voltage")
            if age_months > 48:
                risk_factors.append("High age")
            if resistance > 0.05:
                risk_factors.append("High resistance")
            if temperature > 35:
                risk_factors.append("High temperature")
            
            # Recommendations
            recommendations = []
            if prediction == 0:
                recommendations.append("Battery is in good condition")
                recommendations.append("Regular maintenance recommended")
            elif prediction == 1:
                recommendations.append("Monitor battery performance closely")
                recommendations.append("Consider replacement soon")
            else:
                recommendations.append("Replace battery immediately")
                recommendations.append("Do not rely on this battery")
            
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
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type'
                },
                'body': json.dumps(response)
            }
        
        # Method not allowed
        return {
            'statusCode': 405,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({"error": "Method not allowed"})
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({"error": f"Server error: {str(e)}"})
        }