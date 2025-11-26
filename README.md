# Real-Time Fraud Detection System

A production-ready fraud detection system built with machine learning for real-time transaction analysis. This project implements a complete end-to-end pipeline from data analysis to model deployment via REST API and web dashboard.

## Project Overview

This fraud detection system processes credit card transactions in real-time to identify potentially fraudulent activity. The system uses LightGBM as the primary classifier, achieving 89.47% precision with only a 0.01% false positive rate.

### Key Features

- Real-time fraud prediction via REST API
- Comprehensive feature engineering (67 derived features from 15 base fields)
- Multiple ML models trained and evaluated (LightGBM, XGBoost, Random Forest, Logistic Regression)
- Interactive web dashboard for transaction analysis
- Sub-20ms prediction latency
- Automated model training and evaluation pipeline

## Technical Stack

**Backend:**
- Python 3.12
- Flask (REST API)
- LightGBM (primary model)
- scikit-learn (preprocessing)
- pandas, numpy (data processing)

**Frontend:**
- Streamlit (web dashboard)
- Plotly (visualizations)

**Data:**
- IBM Synthetic Credit Card Transactions Dataset
- 24M+ transactions spanning 1999-2020
- 0.13% fraud rate (highly imbalanced dataset)

## Project Structure

```
Fraud-Detection-Project/
├── app/                          # Flask API backend
│   ├── __init__.py              # API initialization
│   ├── routes.py                # REST endpoints
│   ├── model_loader.py          # Model caching and loading
│   └── feature_service.py       # Real-time feature computation
├── frontend/                     # Streamlit dashboard
│   ├── app.py                   # Main dashboard application
│   ├── pages/                   # Multi-page app sections
│   └── components/              # Reusable UI components
├── models/                       # Trained model files (gitignored)
├── detection_data/              # Dataset files (gitignored)
├── data_analysis.py             # Exploratory data analysis
├── feature_engineering.py       # Feature creation pipeline
├── data_preprocessing.py        # Data preparation and SMOTE
├── model_training.py            # Model training and evaluation
├── run_api.py                   # API server entry point
└── test_api.py                  # API integration tests
```

## Setup and Installation

### Prerequisites

- Python 3.11 or higher
- 4GB+ RAM (for model training)
- 3-4GB free disk space

### Installation Steps

1. Clone the repository
```bash
git clone https://github.com/yourusername/Fraud-Detection-Project.git
cd Fraud-Detection-Project
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Download the dataset

The project uses the IBM Credit Card Transactions dataset from Kaggle. Download these files and place them in `detection_data/`:
- credit_card_transactions-ibm_v2.csv
- sd254_cards.csv
- sd254_users.csv

See [DATA_SETUP.md](DATA_SETUP.md) for detailed instructions.

4. Train the models
```bash
# Run feature engineering
python feature_engineering.py

# Train and evaluate models
python model_training.py
```

## Usage

### Starting the API Server

```bash
python run_api.py
```

The API will start on http://localhost:5000

### Using the Web Dashboard

```bash
streamlit run frontend/app.py
```

Access the dashboard at http://localhost:8501

### Making Predictions via API

```python
import requests

response = requests.post('http://localhost:5000/api/predict', json={
    'Amount': 150.75,
    'Merchant State': 'CA',
    'Merchant City': 'San Francisco',
    'MCC': 5411,
    'Use Chip': 'Chip Transaction'
})

result = response.json()
print(f"Fraud: {result['is_fraud']}")
print(f"Probability: {result['fraud_probability']:.2%}")
```

## Model Performance

### Best Model: LightGBM

- **Precision:** 89.47%
- **Recall:** 68.00%
- **F1-Score:** 77.27%
- **False Positive Rate:** 0.01% (2 out of 19,975)
- **AUC-ROC:** 0.9984

### Model Comparison

| Model | Precision | Recall | F1-Score | FPR |
|-------|-----------|--------|----------|-----|
| LightGBM | 89.47% | 68.00% | 77.27% | 0.01% |
| XGBoost | 81.82% | 72.00% | 76.60% | 0.02% |
| Random Forest | 22.08% | 68.00% | 33.33% | 0.30% |
| Logistic Regression | 9.71% | 80.00% | 17.32% | 0.93% |

## Feature Engineering

The system creates 67 features from the base transaction data:

- **Temporal Features (8):** Hour, day of week, month, cyclical encodings
- **Amount Features (6):** Deviations from user/merchant norms
- **Merchant Features (8):** Risk scores, transaction counts
- **Geographic Features (6):** State/city risk indicators
- **Card Features (9):** Card type, chip usage patterns
- **User Behavioral Features (11):** Spending patterns, account age
- **Velocity Features (5):** Transaction frequency, time gaps
- **Risk Scores (5):** Composite risk indicators

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check and model status |
| `/api/predict` | POST | Single transaction prediction |
| `/api/predict/batch` | POST | Batch transaction predictions |
| `/api/model/info` | GET | Model metadata and version |
| `/api/statistics` | GET | API usage statistics |

Full API documentation: [API_DOCUMENTATION.md](API_DOCUMENTATION.md)

## Testing

Run the test suite:
```bash
python test_api.py
```

Expected output: 5/5 tests passing

## Development Approach

### Data Analysis

Started with comprehensive EDA to understand the dataset characteristics:
- Analyzed temporal patterns (fraud peaks during specific hours)
- Identified high-risk merchant categories
- Studied geographic distribution of fraud
- Examined transaction amount distributions

### Feature Engineering

Created features that capture:
- User spending behavior deviations
- Merchant risk patterns
- Temporal anomalies
- Transaction velocity (frequency of transactions in time windows)

### Model Training

Evaluated multiple algorithms to find the best balance between precision and recall:
1. Handled severe class imbalance (793:1) using SMOTE
2. Trained baseline models for comparison
3. Selected LightGBM for optimal false positive rate
4. Saved best model for production deployment

### Deployment

Built a production-ready API with:
- Lazy model loading for faster startup
- Feature computation on-the-fly
- Caching for improved performance
- Comprehensive error handling

## Future Improvements

- Implement model retraining pipeline with new data
- Add user authentication for API
- Deploy to cloud (AWS/Azure/GCP)
- Integrate monitoring and alerting
- Implement A/B testing framework for model versions

## Dataset Citation

```
@dataset{credit_card_transactions_2021,
  author = {Altman, E.},
  title = {Credit Card Transactions},
  year = {2021},
  publisher = {Kaggle},
  url = {https://www.kaggle.com/datasets/ealtman2019/credit-card-transactions}
}
```

## License

This project is available for educational and research purposes.

## Acknowledgments

- Dataset provided by Kaggle (IBM Synthetic Financial Transactions)
- Built as part of fraud detection research and ML pipeline development
