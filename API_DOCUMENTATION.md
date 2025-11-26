## Fraud Detection API Documentation

REST API for real-time credit card fraud detection using machine learning.

## Base URL

```
http://localhost:5000/api
```

## Authentication

Currently no authentication required (development mode).
In production, implement JWT or API key authentication.

## Endpoints

### 1. Health Check

Check if API is running and model is loaded.

**Endpoint:** `GET /api/health`

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T10:30:00",
  "model_loaded": true,
  "service": "fraud-detection-api"
}
```

---

### 2. Single Transaction Prediction

Predict fraud for a single transaction.

**Endpoint:** `POST /api/predict`

**Request Body:**
```json
{
  "User": 0,
  "Card": 0,
  "Amount": 150.75,
  "Merchant Name": 12345,
  "Merchant City": "New York",
  "Merchant State": "NY",
  "MCC": 5411,
  "Use Chip": "Chip Transaction",
  "DateTime": "2024-01-01T10:30:00"
}
```

**Required Fields:**
- `Amount` (float): Transaction amount

**Optional Fields:**
- `User` (int): User ID (default: 0)
- `Card` (int): Card ID (default: 0)
- `DateTime` (string): ISO format timestamp (default: now)
- `Merchant Name`, `Merchant City`, `Merchant State`, `MCC`, `Use Chip`

**Response:**
```json
{
  "is_fraud": true,
  "fraud_probability": 0.85,
  "risk_level": "high",
  "risk_score": 85.0,
  "transaction_id": "txn_1234567890",
  "amount": 150.75,
  "processed_at": "2024-01-01T10:30:01",
  "recommendation": "BLOCK: High fraud risk - block transaction and require manual review"
}
```

**Risk Levels:**
- `high`: probability >= 0.80 (Block transaction)
- `medium`: probability >= 0.50 (Require additional authentication)
- `low`: probability < 0.50 (Allow with monitoring)

---

### 3. Batch Prediction

Predict fraud for multiple transactions at once.

**Endpoint:** `POST /api/predict/batch`

**Request Body:**
```json
{
  "transactions": [
    {
      "Amount": 50.00,
      "Merchant State": "CA",
      "transaction_id": "txn_001"
    },
    {
      "Amount": 500.00,
      "Merchant State": "Italy",
      "transaction_id": "txn_002"
    }
  ]
}
```

**Response:**
```json
{
  "predictions": [
    {
      "transaction_id": "txn_001",
      "is_fraud": false,
      "fraud_probability": 0.15,
      "risk_level": "low"
    },
    {
      "transaction_id": "txn_002",
      "is_fraud": true,
      "fraud_probability": 0.92,
      "risk_level": "high"
    }
  ],
  "total": 2,
  "fraud_count": 1,
  "fraud_rate": 0.5,
  "processed_at": "2024-01-01T10:30:00"
}
```

---

### 4. Model Information

Get information about the loaded ML model.

**Endpoint:** `GET /api/model/info`

**Response:**
```json
{
  "model_type": "LGBMClassifier",
  "loaded_at": "2024-01-01T10:00:00",
  "model_path": "models/best_model.pkl",
  "version": "1.0.0"
}
```

---

### 5. Reload Model

Reload the model from disk (useful after retraining).

**Endpoint:** `POST /api/model/reload`

**Response:**
```json
{
  "message": "Model reloaded successfully",
  "timestamp": "2024-01-01T10:30:00"
}
```

---

### 6. Statistics

Get API usage statistics.

**Endpoint:** `GET /api/statistics`

**Response:**
```json
{
  "total_predictions": 1250,
  "fraud_detected": 15,
  "average_response_time_ms": 45,
  "model_version": "1.0.0",
  "uptime": "3 days"
}
```

---

## WebSocket Events

Connect to `ws://localhost:5000` for real-time updates.

### Client Events (Send)

**1. subscribe_alerts**
Subscribe to fraud alerts.
```javascript
socket.emit('subscribe_alerts', {});
```

**2. heartbeat**
Send heartbeat ping.
```javascript
socket.emit('heartbeat', {});
```

### Server Events (Receive)

**1. connection_response**
Received upon connection.
```json
{
  "status": "connected",
  "client_id": "abc123",
  "timestamp": "2024-01-01T10:30:00"
}
```

**2. fraud_alert**
Real-time fraud detection alert.
```json
{
  "alert_id": "alert_1234567890",
  "timestamp": "2024-01-01T10:30:00",
  "transaction_id": "txn_001",
  "amount": 500.00,
  "user_id": 123,
  "merchant": "Online Store",
  "fraud_probability": 0.92,
  "risk_level": "high",
  "severity": "critical"
}
```

**3. transaction_update**
Real-time transaction processing update.
```json
{
  "transaction_id": "txn_001",
  "is_fraud": false,
  "amount": 50.00,
  "timestamp": "2024-01-01T10:30:00"
}
```

---

## Error Responses

All error responses follow this format:

```json
{
  "error": "Error type",
  "message": "Detailed error message"
}
```

**Common Status Codes:**
- `200`: Success
- `400`: Bad Request (missing/invalid data)
- `404`: Endpoint not found
- `500`: Internal Server Error

---

## Usage Examples

### Python

```python
import requests

# Single prediction
response = requests.post('http://localhost:5000/api/predict', json={
    'Amount': 150.75,
    'Merchant State': 'CA',
    'MCC': 5411
})
result = response.json()
print(f"Fraud: {result['is_fraud']}, Probability: {result['fraud_probability']}")

# Batch prediction
response = requests.post('http://localhost:5000/api/predict/batch', json={
    'transactions': [
        {'Amount': 50.00},
        {'Amount': 500.00, 'Merchant State': 'Italy'}
    ]
})
results = response.json()
print(f"Fraud rate: {results['fraud_rate']}")
```

### JavaScript

```javascript
// Single prediction
fetch('http://localhost:5000/api/predict', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        Amount: 150.75,
        'Merchant State': 'CA',
        MCC: 5411
    })
})
.then(res => res.json())
.then(data => console.log('Fraud:', data.is_fraud));

// WebSocket connection
const socket = io('http://localhost:5000');
socket.on('fraud_alert', (alert) => {
    console.log('Fraud detected:', alert);
});
socket.emit('subscribe_alerts', {});
```

### cURL

```bash
# Health check
curl http://localhost:5000/api/health

# Single prediction
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"Amount": 150.75, "Merchant State": "CA"}'

# Model info
curl http://localhost:5000/api/model/info
```

---

## Performance

- **Average Response Time**: 30-50ms per prediction
- **Throughput**: ~1000 predictions/second
- **WebSocket Latency**: < 10ms for real-time alerts

---

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Train model (if not already done):**
   ```bash
   python model_training.py
   ```

3. **Start API server:**
   ```bash
   python run_api.py
   ```

4. **Verify it's running:**
   ```bash
   curl http://localhost:5000/api/health
   ```

---

## Configuration

Set environment variables:

```bash
export FLASK_HOST=0.0.0.0
export FLASK_PORT=5000
export FLASK_DEBUG=True
export SECRET_KEY=your-secret-key
```

---

## Monitoring

Logs are written to `logs/fraud_api.log` with rotation (10MB per file, 10 backups).

**Log levels:**
- INFO: Normal operations
- WARNING: Potential issues
- ERROR: Failures and exceptions

---

## Production Deployment

### Recommendations:
1. Use **Gunicorn** or **uWSGI** instead of Flask dev server
2. Set up **Nginx** as reverse proxy
3. Enable **HTTPS** with SSL certificates
4. Implement **authentication** (JWT/API keys)
5. Add **rate limiting**
6. Set up **monitoring** (Prometheus, Grafana)
7. Use **containerization** (Docker)

### Production Command:
```bash
gunicorn --worker-class eventlet -w 1 run_api:app --bind 0.0.0.0:5000
```

---

## Support

For issues or questions, see:
- [PROJECT_STATUS.md](PROJECT_STATUS.md) for project overview
- [MODEL_TRAINING_REPORT.md](MODEL_TRAINING_REPORT.md) for model details
- [README.md](README.md) for general documentation
