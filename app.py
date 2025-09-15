import gradio as gr
import joblib
import numpy as np
from huggingface_hub import hf_hub_download

# Hugging Face repo info
REPO_ID = "nitin-y2309/battery_health"
MODEL_FILE = "battery_model.pkl"
SCALER_FILE = "battery_scaler.pkl"

# Download model files from Hugging Face Hub
model_path = hf_hub_download(repo_id=REPO_ID, filename=MODEL_FILE)
scaler_path = hf_hub_download(repo_id=REPO_ID, filename=SCALER_FILE)

model = joblib.load(model_path)
scaler = joblib.load(scaler_path)

status_map = {0: "Healthy ✅", 1: "Weak ⚠️", 2: "Failed ❌"}

# Prediction function

def predict(voltage, current, temperature, age_months, resistance):
    try:
        features = np.array([[voltage, current, temperature, age_months, resistance]])
        features_scaled = scaler.transform(features)
        prediction = model.predict(features_scaled)[0]
        probabilities = model.predict_proba(features_scaled)[0]
        status = status_map.get(prediction, "Unknown")
        confidence = float(probabilities[prediction]) * 100
        result = f"Status: {status}\nConfidence: {confidence:.1f}%\nProbabilities: Healthy {probabilities[0]*100:.1f}%, Weak {probabilities[1]*100:.1f}%, Failed {probabilities[2]*100:.1f}%"
        return result
    except Exception as e:
        return f"Error: {str(e)}"

# Gradio UI
iface = gr.Interface(
    fn=predict,
    inputs=[
        gr.Number(label="Voltage (V)", value=12.6),
        gr.Number(label="Current (A)", value=150),
        gr.Number(label="Temperature (°C)", value=25),
        gr.Number(label="Age (months)", value=24),
        gr.Number(label="Resistance (Ω)", value=0.03)
    ],
    outputs=gr.Textbox(label="Battery Health Prediction"),
    title="Battery Health Prediction",
    description="Enter your battery parameters to get an instant health assessment. Powered by Machine Learning."
)

iface.launch()
