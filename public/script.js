
// Modern Battery Health Analyzer JavaScript
const form = document.getElementById("batteryForm");
const resultSection = document.getElementById("result"); // Fixed: was "result-section"
const apiStatusDiv = document.getElementById("apiStatus");
const analyzeBtn = document.querySelector(".analyze-btn");

// Check API status on page load
async function checkApiStatus() {
  try {
    const response = await fetch("/api/health");
    if (response.ok) {
      apiStatusDiv.innerHTML = '<span class="api-online">✅ API Online</span>';
      apiStatusDiv.className = "api-status api-online";
    }
  } catch (error) {
    apiStatusDiv.innerHTML = `
      <span class="api-offline">❌ API Offline</span>
      <small>Check deployment status</small>
    `;
    apiStatusDiv.className = "api-status api-offline";
  }
}

function startApiInstructions() {
  alert(`API is managed by Vercel automatically!
If you see this message:
1. Check your internet connection
2. Verify the Vercel deployment is active
3. Contact support if issues persist`);
}

// Check API status when page loads
window.addEventListener('load', checkApiStatus);

function validateInputs() {
  const voltage = parseFloat(document.getElementById("voltage").value);
  const current = parseFloat(document.getElementById("current").value);
  const temperature = parseFloat(document.getElementById("temperature").value);
  const age_months = parseInt(document.getElementById("age_months").value);
  const resistance = parseFloat(document.getElementById("resistance").value);

  let errors = [];
  if (isNaN(voltage) || voltage < 0) errors.push("Voltage must be >= 0V");
  if (isNaN(current) || current < 0) errors.push("Current must be >= 0A");
  if (isNaN(temperature) || temperature < -50 || temperature > 100) errors.push("Temperature must be between -50°C and 100°C");
  if (isNaN(age_months) || age_months < 0) errors.push("Age must be >= 0 months");
  if (isNaN(resistance) || resistance < 0) errors.push("Resistance must be >= 0Ω");
  return errors;
}

function showLoading() {
  analyzeBtn.classList.add('loading');
  analyzeBtn.disabled = true;
  resultSection.innerHTML = '';
}

function hideLoading() {
  analyzeBtn.classList.remove('loading');
  analyzeBtn.disabled = false;
}

function showResult(status, confidence = null) {
  hideLoading();
  
  let resultClass = "result-error";
  let icon = "❌";
  let title = "Unknown Status";
  
  if (status.includes("Healthy")) {
    resultClass = "result-healthy";
    icon = "✅";
    title = "Battery Healthy";
  } else if (status.includes("Weak")) {
    resultClass = "result-weak"; 
    icon = "⚠️";
    title = "Battery Weak";
  } else if (status.includes("Failed")) {
    resultClass = "result-failed";
    icon = "🔋";
    title = "Battery Failed";
  }
  
  const confidenceText = confidence ? `<br><small>Confidence: ${(confidence * 100).toFixed(1)}%</small>` : '';
  
  resultSection.innerHTML = `
    <div class="result-card ${resultClass}">
      <div class="result-icon">${icon}</div>
      <div class="result-title">${title}</div>
      <div class="result-status">${status}${confidenceText}</div>
    </div>
  `;
  
  // Add animation
  setTimeout(() => {
    document.querySelector('.result-card').style.opacity = '1';
    document.querySelector('.result-card').style.transform = 'translateY(0)';
  }, 100);
}

function showEnhancedResult(result) {
  hideLoading();
  
  let resultClass = "result-error";
  let icon = "❌";
  let title = "Unknown Status";
  
  if (result.status.includes("Healthy")) {
    resultClass = "result-healthy";
    icon = "✅";
    title = "Battery Healthy";
  } else if (result.status.includes("Weak")) {
    resultClass = "result-weak"; 
    icon = "⚠️";
    title = "Battery Weak";
  } else if (result.status.includes("Failed")) {
    resultClass = "result-failed";
    icon = "🔋";
    title = "Battery Failed";
  }
  
  const riskFactorsHtml = result.risk_factors.length > 0 ? `
    <div class="risk-factors">
      <h4>⚠️ Risk Factors</h4>
      <ul>${result.risk_factors.map(factor => `<li>${factor}</li>`).join('')}</ul>
    </div>
  ` : '';
  
  resultSection.innerHTML = `
    <div class="result-card ${resultClass}">
      <div class="result-icon">${icon}</div>
      <div class="result-title">${title}</div>
      <div class="result-status">${result.status}</div>
      <div class="confidence">Confidence: ${result.confidence}%</div>
      
      <div class="probabilities-grid">
        <div class="prob-item healthy">
          <span class="prob-label">Healthy</span>
          <span class="prob-value">${result.probabilities.healthy}%</span>
        </div>
        <div class="prob-item weak">
          <span class="prob-label">Weak</span>
          <span class="prob-value">${result.probabilities.weak}%</span>
        </div>
        <div class="prob-item failed">
          <span class="prob-label">Failed</span>
          <span class="prob-value">${result.probabilities.failed}%</span>
        </div>
      </div>
      
      ${riskFactorsHtml}
      
      <div class="recommendations">
        <h4>💡 Recommendations</h4>
        <ul>${result.recommendations.map(rec => `<li>${rec}</li>`).join('')}</ul>
      </div>
    </div>
  `;
  
  // Add animation
  setTimeout(() => {
    document.querySelector('.result-card').style.opacity = '1';
    document.querySelector('.result-card').style.transform = 'translateY(0)';
  }, 100);
}

function showError(message) {
  hideLoading();
  resultSection.innerHTML = `
    <div class="result-card result-error">
      <div class="result-icon">❌</div>
      <div class="result-title">Error</div>
      <div class="result-status">${message}</div>
    </div>
  `;
  
  // Add animation
  setTimeout(() => {
    document.querySelector('.result-card').style.opacity = '1';
    document.querySelector('.result-card').style.transform = 'translateY(0)';
  }, 100);
}

// Form submission handler
form.addEventListener("submit", async function(e) {
  e.preventDefault();
  console.log("Form submitted!"); // Debug log
  resultSection.innerHTML = "";
  
  // Validate inputs
  const errors = validateInputs();
  if (errors.length > 0) {
    console.log("Validation errors:", errors); // Debug log
    showError(errors.join('<br>'));
    return;
  }

  console.log("Starting prediction..."); // Debug log
  showLoading();

  // Collect form data
  const data = {
    voltage: parseFloat(document.getElementById("voltage").value),
    current: parseFloat(document.getElementById("current").value),
    temperature: parseFloat(document.getElementById("temperature").value),
    age_months: parseInt(document.getElementById("age_months").value),
    resistance: parseFloat(document.getElementById("resistance").value)
  };

  console.log("Sending data:", data); // Debug log

  try {
    const response = await fetch("/api/predict", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(data)
    });

    console.log("Response status:", response.status); // Debug log

    if (!response.ok) {
      throw new Error(`Server error: ${response.status}`);
    }

    const result = await response.json();
    console.log("Received result:", result); // Debug log
    
    // Enhanced result display with new API data
    showEnhancedResult(result);

  } catch (error) {
    console.error("Prediction error:", error); // Debug log
    showError(`Failed to analyze battery: ${error.message}`);
  }
});

// Add input animation effects
document.querySelectorAll('.input-group input').forEach(input => {
  input.addEventListener('focus', function() {
    this.parentElement.classList.add('focused');
  });
  
  input.addEventListener('blur', function() {
    this.parentElement.classList.remove('focused');
  });
});

// Periodic API status check
setInterval(checkApiStatus, 30000); // Check every 30 seconds