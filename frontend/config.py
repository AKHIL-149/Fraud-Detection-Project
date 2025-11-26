"""
Frontend Configuration

Centralized configuration for the Streamlit frontend.
"""

# API Configuration
API_BASE_URL = "http://localhost:5000/api"

# Available API Endpoints (from our actual Flask API)
API_ENDPOINTS = {
    "health": f"{API_BASE_URL}/health",
    "predict": f"{API_BASE_URL}/predict",
    "predict_batch": f"{API_BASE_URL}/predict/batch",
    "model_info": f"{API_BASE_URL}/model/info",
    "statistics": f"{API_BASE_URL}/statistics",
}

# Page Configuration
PAGE_CONFIG = {
    "page_title": "FraudGuard - Fraud Detection",
    "page_icon": "🔒",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# Chart Colors
COLORS = {
    "primary": "#1f77b4",
    "success": "#28a745",
    "warning": "#ffc107",
    "danger": "#dc3545",
    "info": "#17a2b8",
    "secondary": "#6c757d",
    "light": "#f8f9fa",
    "dark": "#343a40"
}

# Risk Level Configuration
RISK_LEVELS = {
    "low": {
        "color": COLORS["success"],
        "threshold": 0.5,
        "label": "Low Risk"
    },
    "medium": {
        "color": COLORS["warning"],
        "threshold": 0.8,
        "label": "Medium Risk"
    },
    "high": {
        "color": COLORS["danger"],
        "threshold": 1.0,
        "label": "High Risk"
    }
}

# Merchant Category Codes (Common MCCs)
MCC_CODES = {
    5411: "Grocery Stores",
    5812: "Eating Places, Restaurants",
    5912: "Drug Stores, Pharmacies",
    5932: "Antique Shops",
    5999: "Miscellaneous Retail",
    7011: "Hotels, Motels",
    4111: "Local/Suburban Commuter",
    5541: "Service Stations",
    5814: "Fast Food Restaurants",
    5921: "Package Stores - Beer, Wine, Liquor"
}

# Refresh Intervals (in seconds)
REFRESH_INTERVALS = {
    "fast": 5,
    "normal": 10,
    "slow": 30,
    "very_slow": 60
}
