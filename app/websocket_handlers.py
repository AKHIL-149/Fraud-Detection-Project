"""
WebSocket Handlers for Real-time Updates
Handles Socket.IO events for live fraud detection alerts
"""

from flask_socketio import emit, join_room, leave_room
from app import socketio, app
from datetime import datetime
import random

# Store connected clients
connected_clients = set()

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    client_id = request.sid
    connected_clients.add(client_id)
    app.logger.info(f"Client connected: {client_id}")

    emit('connection_response', {
        'status': 'connected',
        'client_id': client_id,
        'timestamp': datetime.now().isoformat(),
        'message': 'Connected to Fraud Detection API'
    })

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    client_id = request.sid
    if client_id in connected_clients:
        connected_clients.remove(client_id)
    app.logger.info(f"Client disconnected: {client_id}")

@socketio.on('subscribe_alerts')
def handle_subscribe_alerts(data):
    """Subscribe client to fraud alerts"""
    client_id = request.sid
    join_room('fraud_alerts')
    app.logger.info(f"Client {client_id} subscribed to fraud alerts")

    emit('subscription_confirmed', {
        'room': 'fraud_alerts',
        'timestamp': datetime.now().isoformat()
    })

@socketio.on('unsubscribe_alerts')
def handle_unsubscribe_alerts():
    """Unsubscribe client from fraud alerts"""
    client_id = request.sid
    leave_room('fraud_alerts')
    app.logger.info(f"Client {client_id} unsubscribed from fraud alerts")

@socketio.on('heartbeat')
def handle_heartbeat():
    """Handle client heartbeat ping"""
    emit('heartbeat_response', {
        'timestamp': datetime.now().isoformat(),
        'status': 'alive'
    })

def broadcast_fraud_alert(transaction_data, prediction_result):
    """
    Broadcast fraud alert to all subscribed clients.
    Called when a fraudulent transaction is detected.

    Args:
        transaction_data: Original transaction data
        prediction_result: Prediction results from model
    """
    alert = {
        'alert_id': f"alert_{datetime.now().timestamp()}",
        'timestamp': datetime.now().isoformat(),
        'transaction_id': transaction_data.get('transaction_id', 'unknown'),
        'amount': transaction_data.get('Amount', 0),
        'user_id': transaction_data.get('User', 0),
        'merchant': transaction_data.get('Merchant City', 'Unknown'),
        'fraud_probability': prediction_result['fraud_probability'],
        'risk_level': prediction_result['risk_level'],
        'severity': _calculate_severity(prediction_result['fraud_probability'], transaction_data.get('Amount', 0))
    }

    socketio.emit('fraud_alert', alert, room='fraud_alerts')
    app.logger.info(f"Fraud alert broadcast: {alert['alert_id']}")

def broadcast_transaction_update(transaction_data):
    """
    Broadcast transaction update to all clients.
    Used for real-time monitoring dashboard.

    Args:
        transaction_data: Transaction details with prediction
    """
    socketio.emit('transaction_update', transaction_data, broadcast=True)

def broadcast_system_status(status_data):
    """
    Broadcast system status update.

    Args:
        status_data: System metrics and status
    """
    socketio.emit('system_status', status_data, broadcast=True)

def _calculate_severity(probability, amount):
    """
    Calculate alert severity based on probability and amount.

    Returns:
        str: 'critical', 'high', 'medium', or 'low'
    """
    if probability >= 0.90 and amount > 500:
        return 'critical'
    elif probability >= 0.80:
        return 'high'
    elif probability >= 0.50:
        return 'medium'
    else:
        return 'low'

# Import request from flask
from flask import request
