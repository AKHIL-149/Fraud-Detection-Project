"""
Flask-based Dashboard Application for Fraud Detection
Provides web interface for monitoring fraud detection system
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import requests
from datetime import datetime, timedelta
import os

# Create Flask app
dashboard_app = Flask(__name__,
                     template_folder='dashboard_templates',
                     static_folder='dashboard_static')
CORS(dashboard_app)

# API configuration
API_BASE_URL = 'http://localhost:5000'

@dashboard_app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@dashboard_app.route('/alerts')
def alerts():
    """Alerts management page"""
    return render_template('alerts.html')

@dashboard_app.route('/monitoring')
def monitoring():
    """Real-time monitoring page"""
    return render_template('monitoring.html')

@dashboard_app.route('/reports')
def reports():
    """Reports and analytics page"""
    return render_template('reports.html')

@dashboard_app.route('/predict')
def predict_page():
    """Prediction form page"""
    return render_template('predict.html')

# API proxy endpoints to avoid CORS issues
@dashboard_app.route('/api/proxy/statistics')
def proxy_statistics():
    """Proxy for statistics API"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/statistics", timeout=5)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_app.route('/api/proxy/alerts')
def proxy_alerts():
    """Proxy for alerts API"""
    try:
        severity = request.args.get('severity')
        limit = request.args.get('limit', 50)
        params = {'limit': limit}
        if severity:
            params['severity'] = severity

        response = requests.get(f"{API_BASE_URL}/api/dashboard/alerts", params=params, timeout=5)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_app.route('/api/proxy/transactions')
def proxy_transactions():
    """Proxy for transactions API"""
    try:
        limit = request.args.get('limit', 100)
        response = requests.get(f"{API_BASE_URL}/api/dashboard/recent-transactions",
                              params={'limit': limit}, timeout=5)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_app.route('/api/proxy/merchant-stats')
def proxy_merchant_stats():
    """Proxy for merchant statistics API"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/dashboard/merchant-stats", timeout=5)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_app.route('/api/proxy/hourly-stats')
def proxy_hourly_stats():
    """Proxy for hourly statistics API"""
    try:
        hours = request.args.get('hours', 24)
        response = requests.get(f"{API_BASE_URL}/api/dashboard/hourly-stats",
                              params={'hours': hours}, timeout=5)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_app.route('/api/proxy/risk-distribution')
def proxy_risk_distribution():
    """Proxy for risk distribution API"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/dashboard/risk-distribution", timeout=5)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_app.route('/api/proxy/predict', methods=['POST'])
def proxy_predict():
    """Proxy for prediction API"""
    try:
        data = request.get_json()
        response = requests.post(f"{API_BASE_URL}/api/predict", json=data, timeout=5)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_app.route('/health')
def health():
    """Dashboard health check"""
    return jsonify({
        'status': 'healthy',
        'service': 'fraud-detection-dashboard',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("=" * 80)
    print("Fraud Detection Dashboard")
    print("=" * 80)
    print(f"Dashboard URL: http://localhost:8080")
    print(f"API Backend: {API_BASE_URL}")
    print("=" * 80)
    dashboard_app.run(host='0.0.0.0', port=8080, debug=True)
