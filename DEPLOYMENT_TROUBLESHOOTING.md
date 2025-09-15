# 🚨 Vercel Deployment Troubleshooting Guide

## Issue: "Production Domain is not serving traffic"

This error typically occurs when there are configuration issues with your Vercel deployment. Let's fix this step by step.

## 🔍 Common Causes & Solutions

### 1. **Vercel.json Configuration Issues**

Your current `vercel.json` might have routing problems. Let's create a simplified version:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/predict.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "/api/predict.py"
    },
    {
      "src": "/(.*)",
      "dest": "/public/$1"
    }
  ]
}
```

### 2. **Python Function Entry Point**

The API function needs a proper Vercel handler. Update `api/predict.py`:

**Add this at the end of your file:**
```python
# Vercel serverless function handler
def handler(event, context):
    """Vercel serverless function entry point"""
    app.config['ENV'] = 'production'
    return app(event, context)

# Alternative simple handler
app.config['ENV'] = 'production'
```

### 3. **File Structure Verification**

Ensure your structure exactly matches:
```
battery_health/
├── api/
│   └── predict.py
├── public/
│   ├── index.html
│   ├── style.css
│   └── script.js
├── models/
│   ├── battery_model.pkl
│   └── battery_scaler.pkl
├── vercel.json
└── requirements.txt
```

## 🛠️ Step-by-Step Fix

### Step 1: Check Vercel Build Logs
1. Go to your Vercel dashboard
2. Click on your project
3. Go to "Functions" tab
4. Check for any build errors

### Step 2: Simplify vercel.json
Replace your current `vercel.json` with the minimal version above.

### Step 3: Update API Function
Ensure your `api/predict.py` has the proper Flask-to-Vercel adapter.

### Step 4: Re-deploy
- Commit changes to GitHub
- Vercel will auto-redeploy
- Wait 2-3 minutes for propagation

## 🚀 Alternative: Simplified Deployment

If issues persist, try this ultra-simple approach:

### Option A: Single API File
Create a minimal `api/index.py`:

```python
from flask import Flask, request, jsonify
import pandas as pd
import joblib
import os

app = Flask(__name__)

# Load models (adjust paths as needed)
model = joblib.load('../models/battery_model.pkl')
scaler = joblib.load('../models/battery_scaler.pkl')

@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        # Your prediction logic here
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Vercel entry point
def handler(event, context):
    return app(event, context)
```

### Option B: Pure Python Function
Create `api/predict.py` as a pure function:

```python
def handler(event, context):
    # Direct HTTP handling without Flask
    import json
    
    try:
        # Parse request
        body = json.loads(event.get('body', '{}'))
        
        # Your ML prediction logic
        result = {"status": "Healthy ✅", "confidence": 95.5}
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(result)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({"error": str(e)})
        }
```

## 🔄 Quick Test Commands

After fixing, test your deployment:

```bash
# Test health endpoint
curl https://your-app.vercel.app/api/health

# Test prediction
curl -X POST https://your-app.vercel.app/api/predict \
  -H "Content-Type: application/json" \
  -d '{"voltage": 12.5, "current": 200, "temperature": 25, "age_months": 24}'
```

## 📞 Need Immediate Help?

1. **Check Vercel Dashboard Logs** - Look for specific error messages
2. **Try Basic HTML First** - Deploy just the frontend to test
3. **Test API Separately** - Create a simple "Hello World" API first
4. **Contact Vercel Support** - They're very responsive for deployment issues

## 🎯 Most Common Fix

**90% of the time, this works:**

1. Simplify `vercel.json` to minimal configuration
2. Add proper Vercel handler to your Python function
3. Ensure all file paths are correct relative to project root
4. Re-commit and redeploy

Let me know what specific error messages you're seeing in the Vercel dashboard!