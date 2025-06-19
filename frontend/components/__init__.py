"""
Streamlit components package for fraud detection system
Provides reusable chart and table components for Streamlit dashboards
"""

__version__ = "1.0.0"
__author__ = "Fraud Detection Team"

# Common imports for all components
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import requests
import json

# Component configuration
COMPONENT_CONFIG = {
    "default_height": 400,
    "color_scheme": {
        "primary": "#007bff",
        "success": "#28a745",
        "danger": "#dc3545",
        "warning": "#ffc107",
        "info": "#17a2b8",
        "secondary": "#6c757d"
    },
    "chart_template": "plotly_white"
}

# API configuration
API_BASE_URL = "http://localhost:5000/api"

# Utility functions
def format_currency(amount):
    """Format currency values"""
    return f"${amount:,.2f}"

def format_percentage(value):
    """Format percentage values"""
    return f"{value:.2%}"

def get_risk_level_color(risk_score):
    """Get color based on risk level"""
    if risk_score >= 0.7:
        return COMPONENT_CONFIG["color_scheme"]["danger"]
    elif risk_score >= 0.3:
        return COMPONENT_CONFIG["color_scheme"]["warning"]
    else:
        return COMPONENT_CONFIG["color_scheme"]["success"]

def get_severity_color(severity):
    """Get color based on alert severity"""
    color_map = {
        'critical': COMPONENT_CONFIG["color_scheme"]["danger"],
        'high': '#fd7e14',
        'medium': COMPONENT_CONFIG["color_scheme"]["warning"],
        'low': COMPONENT_CONFIG["color_scheme"]["success"]
    }
    return color_map.get(severity, COMPONENT_CONFIG["color_scheme"]["secondary"])

# Common styling
COMPONENT_STYLE = """
<style>
    .metric-container {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    
    .chart-container {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    
    .table-container {
        background: white;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        overflow: hidden;
    }
    
    .risk-high {
        color: #dc3545;
        font-weight: bold;
    }
    
    .risk-medium {
        color: #ffc107;
        font-weight: bold;
    }
    
    .risk-low {
        color: #28a745;
        font-weight: bold;
    }
    
    .status-badge {
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        color: white;
        font-size: 0.8rem;
        font-weight: bold;
    }
</style>
"""