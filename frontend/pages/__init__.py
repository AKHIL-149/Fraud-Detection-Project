"""
Streamlit pages package for fraud detection system
Provides alternative dashboard interfaces using Streamlit
"""

__version__ = "1.0.0"
__author__ = "Fraud Detection Team"

# Page configuration
PAGE_CONFIG = {
    "page_title": "FraudGuard Dashboard",
    "page_icon": "🛡️",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# Common styling
COMMON_STYLE = """
<style>
    .main-header {
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #1f77b4;
    }
    
    .alert-high {
        border-left-color: #dc3545 !important;
    }
    
    .alert-medium {
        border-left-color: #ffc107 !important;
    }
    
    .alert-low {
        border-left-color: #28a745 !important;
    }
    
    .stSelectbox > div > div {
        background-color: #f8f9fa;
    }
    
    .fraud-detected {
        color: #dc3545;
        font-weight: bold;
    }
    
    .legitimate {
        color: #28a745;
        font-weight: bold;
    }
</style>
"""

# API endpoints configuration
API_BASE_URL = "http://localhost:5000/api"

ENDPOINTS = {
    "transactions": f"{API_BASE_URL}/transactions",
    "alerts": f"{API_BASE_URL}/monitoring/alerts",
    "reports": f"{API_BASE_URL}/reports",
    "system_status": f"{API_BASE_URL}/monitoring/system-status",
    "fraud_test": f"{API_BASE_URL}/transactions/test-fraud"
}

# Common imports for all pages
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
from datetime import datetime, timedelta
import time
import json