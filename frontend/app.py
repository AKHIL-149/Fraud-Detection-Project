"""
FraudGuard - Real-time Fraud Detection Dashboard

Main Streamlit application entry point.
Provides fraud prediction interface and navigation to monitoring pages.
"""

import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import json

# Page configuration
st.set_page_config(
    page_title="FraudGuard - Fraud Detection",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API configuration
API_BASE_URL = "http://localhost:5000/api"

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .risk-low {
        color: #28a745;
        font-weight: bold;
    }
    .risk-medium {
        color: #ffc107;
        font-weight: bold;
    }
    .risk-high {
        color: #dc3545;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

def check_api_health():
    """Check if API server is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=2)
        if response.status_code == 200:
            data = response.json()
            return data.get('status') == 'healthy', data.get('model_loaded', False)
    except:
        pass
    return False, False

def predict_fraud(transaction_data):
    """Make fraud prediction API call"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/predict",
            json=transaction_data,
            timeout=10
        )
        if response.status_code == 200:
            return response.json(), None
        else:
            return None, f"API Error: {response.status_code} - {response.text}"
    except Exception as e:
        return None, f"Connection Error: {str(e)}"

def create_risk_gauge(fraud_probability):
    """Create a gauge chart for fraud probability"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=fraud_probability * 100,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Fraud Probability", 'font': {'size': 24}},
        delta={'reference': 50},
        gauge={
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "darkblue"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 50], 'color': '#d4edda'},
                {'range': [50, 80], 'color': '#fff3cd'},
                {'range': [80, 100], 'color': '#f8d7da'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 80
            }
        }
    ))

    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=40, b=20)
    )

    return fig

def main():
    """Main application"""

    # Header
    st.markdown('<h1 class="main-header">FraudGuard - Fraud Detection System</h1>', unsafe_allow_html=True)

    # Check API health
    api_healthy, model_loaded = check_api_health()

    # API Status in sidebar
    with st.sidebar:
        st.header("System Status")

        if api_healthy:
            st.success("API Server: Online")
        else:
            st.error("API Server: Offline")
            st.warning("Make sure the API server is running:\n```bash\npython run_api.py\n```")

        if model_loaded:
            st.success("ML Model: Loaded")
        else:
            st.warning("ML Model: Not Loaded")

        st.divider()

        st.header("Navigation")
        st.markdown("""
        **Available Pages:**
        - Home (Prediction)
        - Alerts
        - Monitoring
        - Reports

        Use the pages in the sidebar to navigate.
        """)

        st.divider()

        st.header("Quick Stats")
        try:
            health_response = requests.get(f"{API_BASE_URL}/health", timeout=2)
            if health_response.status_code == 200:
                st.metric("Status", "Healthy", delta="Online")
        except:
            st.metric("Status", "Unknown", delta="Check API")

    # Main content
    if not api_healthy:
        st.error("Cannot connect to API server. Please start the API server first:")
        st.code("python run_api.py", language="bash")
        st.info("The API server should be running on http://localhost:5000")
        return

    # Create two columns
    col1, col2 = st.columns([1, 1])

    with col1:
        st.header("Transaction Analysis")

        with st.form("prediction_form"):
            st.subheader("Enter Transaction Details")

            # Transaction amount
            amount = st.number_input(
                "Transaction Amount ($)",
                min_value=0.01,
                max_value=100000.0,
                value=150.75,
                step=0.01,
                help="Enter the transaction amount in USD"
            )

            # Merchant information
            col_a, col_b = st.columns(2)

            with col_a:
                merchant_state = st.text_input(
                    "Merchant State/Country",
                    value="CA",
                    help="Two-letter state code or country name"
                )

            with col_b:
                merchant_city = st.text_input(
                    "Merchant City",
                    value="San Francisco",
                    help="City where merchant is located"
                )

            # MCC and transaction type
            col_c, col_d = st.columns(2)

            with col_c:
                mcc = st.number_input(
                    "Merchant Category Code (MCC)",
                    min_value=0,
                    max_value=9999,
                    value=5411,
                    help="MCC code (e.g., 5411 for Grocery)"
                )

            with col_d:
                use_chip = st.selectbox(
                    "Transaction Type",
                    ["Chip Transaction", "Online Transaction", "Swipe Transaction"],
                    help="How the card was used"
                )

            # Additional fields (optional)
            with st.expander("Additional Information (Optional)"):
                user_id = st.number_input("User ID", min_value=0, value=0)
                card_id = st.number_input("Card ID", min_value=0, value=0)

            # Submit button
            submitted = st.form_submit_button("Analyze Transaction", use_container_width=True)

        if submitted:
            # Prepare transaction data
            transaction_data = {
                "Amount": amount,
                "Merchant State": merchant_state,
                "Merchant City": merchant_city,
                "MCC": mcc,
                "Use Chip": use_chip
            }

            if user_id > 0:
                transaction_data["User"] = user_id
            if card_id > 0:
                transaction_data["Card"] = card_id

            # Make prediction
            with st.spinner("Analyzing transaction..."):
                result, error = predict_fraud(transaction_data)

            if error:
                st.error(f"Error: {error}")
            elif result:
                # Store result in session state for display in col2
                st.session_state['last_result'] = result
                st.session_state['last_transaction'] = transaction_data

    with col2:
        st.header("Analysis Results")

        if 'last_result' in st.session_state:
            result = st.session_state['last_result']
            transaction = st.session_state['last_transaction']

            # Risk level
            is_fraud = result.get('is_fraud', False)
            fraud_prob = result.get('fraud_probability', 0)
            risk_level = result.get('risk_level', 'unknown')
            recommendation = result.get('recommendation', 'No recommendation')

            # Display verdict
            if is_fraud:
                st.error("**FRAUD DETECTED**")
            else:
                st.success("**TRANSACTION APPROVED**")

            # Risk metrics
            metric_col1, metric_col2, metric_col3 = st.columns(3)

            with metric_col1:
                st.metric(
                    "Fraud Probability",
                    f"{fraud_prob:.2%}",
                    delta=f"{fraud_prob*100:.2f}%"
                )

            with metric_col2:
                risk_color = "risk-low" if risk_level == "low" else "risk-medium" if risk_level == "medium" else "risk-high"
                st.metric(
                    "Risk Level",
                    risk_level.upper()
                )

            with metric_col3:
                st.metric(
                    "Risk Score",
                    f"{result.get('risk_score', 0):.2f}"
                )

            # Gauge chart
            st.plotly_chart(create_risk_gauge(fraud_prob), use_container_width=True)

            # Recommendation
            st.subheader("Recommendation")
            if risk_level == "low":
                st.success(recommendation)
            elif risk_level == "medium":
                st.warning(recommendation)
            else:
                st.error(recommendation)

            # Transaction details
            st.subheader("Transaction Details")

            details_col1, details_col2 = st.columns(2)

            with details_col1:
                st.markdown(f"""
                **Amount:** ${transaction.get('Amount', 0):.2f}
                **Merchant State:** {transaction.get('Merchant State', 'N/A')}
                **Merchant City:** {transaction.get('Merchant City', 'N/A')}
                """)

            with details_col2:
                st.markdown(f"""
                **MCC:** {transaction.get('MCC', 'N/A')}
                **Transaction Type:** {transaction.get('Use Chip', 'N/A')}
                **Transaction ID:** {result.get('transaction_id', 'N/A')}
                """)

            # Raw response
            with st.expander("View Raw API Response"):
                st.json(result)

        else:
            st.info("Enter transaction details and click 'Analyze Transaction' to see results here.")

            # Example transactions
            st.subheader("Try These Examples")

            st.markdown("""
            **Low Risk Transaction:**
            - Amount: $45.50
            - State: CA
            - City: San Francisco
            - MCC: 5411 (Grocery)
            - Type: Chip Transaction

            **Higher Risk Transaction:**
            - Amount: $1,500
            - State: Italy
            - City: ONLINE
            - MCC: 5932 (Antique Shop)
            - Type: Online Transaction
            """)

    # Footer with info
    st.divider()

    st.markdown("""
    ### About FraudGuard

    This fraud detection system uses machine learning to analyze transactions in real-time:
    - **Model:** LightGBM with 67 engineered features
    - **Performance:** 89.47% precision, 68% recall
    - **Response Time:** <20ms per prediction
    - **False Positive Rate:** 0.01%

    Navigate to other pages using the sidebar to:
    - **Alerts:** View and manage fraud alerts
    - **Monitoring:** Real-time transaction monitoring
    - **Reports:** Generate analytics and reports
    """)

if __name__ == "__main__":
    main()
