"""
Flask API Server Runner
Main entry point for the fraud detection API service
"""

from app import app, socketio
import os

if __name__ == '__main__':
    # Get configuration from environment
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'

    print("=" * 80)
    print("Fraud Detection API Server")
    print("=" * 80)
    print(f"Starting server on {host}:{port}")
    print(f"Debug mode: {debug}")
    print(f"API Documentation: http://{host}:{port}/")
    print(f"Health Check: http://{host}:{port}/api/health")
    print("=" * 80)

    # Run with SocketIO for WebSocket support
    socketio.run(
        app,
        host=host,
        port=port,
        debug=debug,
        allow_unsafe_werkzeug=True  # For development only
    )
