"""
API Routes for Fraud Detection Service
Defines all REST API endpoints
"""

from flask import request, jsonify
from app import app
from app.model_loader import model_loader
from app.feature_service import feature_service
from app import database as db
import pandas as pd
import numpy as np
from datetime import datetime
import traceback
import time

@app.route('/')
def index():
    """API root endpoint"""
    return jsonify({
        'service': 'Fraud Detection API',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': {
            'health': '/api/health',
            'predict': '/api/predict',
            'batch_predict': '/api/predict/batch',
            'model_info': '/api/model/info',
            'statistics': '/api/statistics'
        }
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring"""
    try:
        model_loaded = model_loader.is_model_loaded()

        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'model_loaded': model_loaded,
            'service': 'fraud-detection-api'
        }), 200
    except Exception as e:
        app.logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

@app.route('/api/predict', methods=['POST'])
def predict_fraud():
    """
    Predict fraud for a single transaction.

    Expected JSON body:
    {
        "User": 0,
        "Card": 0,
        "Amount": 100.50,
        "Merchant Name": 12345,
        "Merchant City": "New York",
        "Merchant State": "NY",
        "MCC": 5411,
        "Use Chip": "Chip Transaction",
        "DateTime": "2024-01-01T10:30:00" (optional, defaults to now)
    }

    Returns:
    {
        "is_fraud": true/false,
        "fraud_probability": 0.85,
        "risk_level": "high/medium/low",
        "transaction_id": "...",
        "processed_at": "..."
    }
    """
    try:
        # Get transaction data
        transaction = request.get_json()

        if not transaction:
            return jsonify({'error': 'No transaction data provided'}), 400

        # Validate required fields
        required_fields = ['Amount']
        missing_fields = [field for field in required_fields if field not in transaction]
        if missing_fields:
            return jsonify({
                'error': 'Missing required fields',
                'missing': missing_fields
            }), 400

        # Add timestamp if not provided
        if 'DateTime' not in transaction:
            transaction['DateTime'] = datetime.now()

        # Load model if not already loaded
        model = model_loader.load_model()
        preprocessor = model_loader.load_preprocessor()

        # Compute features
        features = feature_service.compute_features(transaction)

        # Create feature dataframe
        feature_df = pd.DataFrame([features])

        # Get feature columns expected by model
        expected_features = preprocessor['feature_columns']

        # Add missing features with default values
        for col in expected_features:
            if col not in feature_df.columns:
                feature_df[col] = 0

        # Select and order features to match training
        feature_df = feature_df[expected_features]

        # Scale features
        features_scaled = preprocessor['scaler'].transform(feature_df)

        # Track prediction time
        start_time = time.time()

        # Make prediction
        prediction = model.predict(features_scaled)[0]
        probability = model.predict_proba(features_scaled)[0][1]

        prediction_time_ms = (time.time() - start_time) * 1000

        # Determine risk level
        if probability >= 0.80:
            risk_level = 'high'
        elif probability >= 0.50:
            risk_level = 'medium'
        else:
            risk_level = 'low'

        # Generate transaction ID
        transaction_id = transaction.get('transaction_id', f"txn_{int(datetime.now().timestamp() * 1000)}")

        # Prepare response
        result = {
            'is_fraud': bool(prediction),
            'fraud_probability': float(probability),
            'risk_level': risk_level,
            'risk_score': float(probability * 100),
            'transaction_id': transaction_id,
            'amount': float(transaction['Amount']),
            'processed_at': datetime.now().isoformat(),
            'recommendation': _get_recommendation(probability)
        }

        # Save prediction to database
        try:
            db_record = {
                'transaction_id': transaction_id,
                'amount': float(transaction['Amount']),
                'merchant_state': transaction.get('Merchant State'),
                'merchant_city': transaction.get('Merchant City'),
                'merchant_category': transaction.get('Merchant Category'),
                'mcc': transaction.get('MCC'),
                'use_chip': transaction.get('Use Chip'),
                'user_id': transaction.get('User'),
                'card_id': transaction.get('Card'),
                'is_fraud': bool(prediction),
                'fraud_probability': float(probability),
                'risk_score': float(probability * 100),
                'risk_level': risk_level,
                'prediction_time_ms': prediction_time_ms,
                'model_version': '1.0.0'
            }
            db.save_prediction(db_record)
        except Exception as e:
            app.logger.warning(f"Failed to save prediction to database: {str(e)}")

        app.logger.info(f"Prediction: {result['is_fraud']}, Probability: {probability:.4f}")

        return jsonify(result), 200

    except Exception as e:
        app.logger.error(f"Prediction error: {str(e)}\n{traceback.format_exc()}")
        return jsonify({
            'error': 'Prediction failed',
            'message': str(e)
        }), 500

@app.route('/api/predict/batch', methods=['POST'])
def predict_batch():
    """
    Predict fraud for multiple transactions.

    Expected JSON body:
    {
        "transactions": [
            {...transaction1...},
            {...transaction2...}
        ]
    }

    Returns:
    {
        "predictions": [...],
        "total": 10,
        "fraud_count": 2
    }
    """
    try:
        data = request.get_json()
        transactions = data.get('transactions', [])

        if not transactions:
            return jsonify({'error': 'No transactions provided'}), 400

        # Load model
        model = model_loader.load_model()
        preprocessor = model_loader.load_preprocessor()

        results = []
        fraud_count = 0

        for txn in transactions:
            # Compute features
            features = feature_service.compute_features(txn)
            feature_df = pd.DataFrame([features])

            # Prepare features
            expected_features = preprocessor['feature_columns']
            for col in expected_features:
                if col not in feature_df.columns:
                    feature_df[col] = 0
            feature_df = feature_df[expected_features]

            # Scale and predict
            features_scaled = preprocessor['scaler'].transform(feature_df)
            prediction = model.predict(features_scaled)[0]
            probability = model.predict_proba(features_scaled)[0][1]

            if prediction:
                fraud_count += 1

            results.append({
                'transaction_id': txn.get('transaction_id', f"txn_{len(results)}"),
                'is_fraud': bool(prediction),
                'fraud_probability': float(probability),
                'risk_level': 'high' if probability >= 0.80 else 'medium' if probability >= 0.50 else 'low'
            })

        return jsonify({
            'predictions': results,
            'total': len(transactions),
            'fraud_count': fraud_count,
            'fraud_rate': fraud_count / len(transactions) if transactions else 0,
            'processed_at': datetime.now().isoformat()
        }), 200

    except Exception as e:
        app.logger.error(f"Batch prediction error: {str(e)}\n{traceback.format_exc()}")
        return jsonify({
            'error': 'Batch prediction failed',
            'message': str(e)
        }), 500

@app.route('/api/model/info', methods=['GET'])
def model_info():
    """Get information about the loaded model"""
    try:
        info = model_loader.get_model_info()
        return jsonify(info), 200
    except Exception as e:
        return jsonify({
            'error': 'Failed to get model info',
            'message': str(e)
        }), 500

@app.route('/api/model/reload', methods=['POST'])
def reload_model():
    """Reload the model from disk"""
    try:
        model_loader.reload_model()
        return jsonify({
            'message': 'Model reloaded successfully',
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'error': 'Failed to reload model',
            'message': str(e)
        }), 500

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Get API usage statistics from real predictions"""
    try:
        stats = db.get_fraud_statistics(hours=24)

        total = stats.get('total', 0)
        fraud_count = stats.get('fraud_count', 0)

        return jsonify({
            'total_predictions': total,
            'fraud_detected': fraud_count,
            'fraud_rate': (fraud_count / total * 100) if total > 0 else 0,
            'amount_at_risk': stats.get('fraud_amount', 0),
            'average_fraud_probability': stats.get('avg_fraud_prob', 0),
            'model_version': '1.0.0',
            'period_hours': 24
        }), 200
    except Exception as e:
        app.logger.error(f"Statistics error: {str(e)}")
        return jsonify({
            'total_predictions': 0,
            'fraud_detected': 0,
            'fraud_rate': 0
        }), 200

# Dashboard endpoints for real-time data
@app.route('/api/dashboard/alerts', methods=['GET'])
def get_alerts():
    """Get fraud alerts for dashboard"""
    try:
        severity = request.args.get('severity')
        limit = int(request.args.get('limit', 50))

        alerts = db.get_alerts(severity=severity, limit=limit)

        # Transform for frontend
        formatted_alerts = []
        for alert in alerts:
            severity_level = 'critical' if alert['fraud_probability'] >= 0.9 else \
                           'high' if alert['fraud_probability'] >= 0.7 else 'medium'

            formatted_alerts.append({
                'id': alert['id'],
                'transaction_id': alert['transaction_id'],
                'title': f"Fraud Alert - {severity_level.upper()}",
                'description': f"Transaction of ${alert['amount']:.2f} flagged with {alert['fraud_probability']:.1%} fraud probability",
                'severity': severity_level,
                'timestamp': alert['timestamp'],
                'amount': alert['amount'],
                'merchant_city': alert['merchant_city'],
                'merchant_state': alert['merchant_state'],
                'risk_score': alert['fraud_probability'],
                'status': 'active'
            })

        return jsonify({'alerts': formatted_alerts}), 200

    except Exception as e:
        app.logger.error(f"Alerts error: {str(e)}")
        return jsonify({'alerts': []}), 200

@app.route('/api/dashboard/recent-transactions', methods=['GET'])
def get_recent_transactions():
    """Get recent transactions for monitoring dashboard"""
    try:
        limit = int(request.args.get('limit', 100))
        predictions = db.get_recent_predictions(limit=limit)

        # Format for frontend
        transactions = []
        for pred in predictions:
            transactions.append({
                'transaction_id': pred['transaction_id'],
                'timestamp': pred['timestamp'],
                'amount': pred['amount'],
                'merchant_state': pred['merchant_state'],
                'merchant_city': pred['merchant_city'],
                'merchant_category': pred['merchant_category'],
                'risk_score': pred['fraud_probability'],
                'is_fraud': bool(pred['is_fraud']),
                'risk_level': pred['risk_level'],
                'confidence': pred['fraud_probability']
            })

        return jsonify({'transactions': transactions}), 200

    except Exception as e:
        app.logger.error(f"Recent transactions error: {str(e)}")
        return jsonify({'transactions': []}), 200

@app.route('/api/dashboard/hourly-stats', methods=['GET'])
def get_hourly_stats():
    """Get hourly statistics for charts"""
    try:
        hours = int(request.args.get('hours', 24))
        stats = db.get_hourly_statistics(hours=hours)

        return jsonify({'hourly_stats': stats}), 200

    except Exception as e:
        app.logger.error(f"Hourly stats error: {str(e)}")
        return jsonify({'hourly_stats': []}), 200

@app.route('/api/dashboard/risk-distribution', methods=['GET'])
def get_risk_dist():
    """Get risk level distribution"""
    try:
        distribution = db.get_risk_distribution()
        return jsonify({'distribution': distribution}), 200

    except Exception as e:
        app.logger.error(f"Risk distribution error: {str(e)}")
        return jsonify({'distribution': []}), 200

@app.route('/api/dashboard/merchant-stats', methods=['GET'])
def get_merchant_stats():
    """Get merchant statistics"""
    try:
        stats = db.get_merchant_statistics()
        return jsonify({'merchant_stats': stats}), 200

    except Exception as e:
        app.logger.error(f"Merchant stats error: {str(e)}")
        return jsonify({'merchant_stats': []}), 200

def _get_recommendation(probability):
    """Get action recommendation based on fraud probability"""
    if probability >= 0.80:
        return "BLOCK: High fraud risk - block transaction and require manual review"
    elif probability >= 0.50:
        return "CHALLENGE: Medium risk - require additional authentication (2FA/SMS)"
    else:
        return "ALLOW: Low risk - approve transaction with passive monitoring"

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    app.logger.error(f"Internal server error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500
