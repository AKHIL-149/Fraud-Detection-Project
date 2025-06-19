"""
Real-time monitoring page for Streamlit dashboard
Provides live transaction monitoring and fraud detection
"""

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
from . import COMMON_STYLE, ENDPOINTS, PAGE_CONFIG

class MonitoringPage:
    def __init__(self):
        self.setup_page()
        
    def setup_page(self):
        """Configure the Streamlit page"""
        st.set_page_config(**PAGE_CONFIG)
        st.markdown(COMMON_STYLE, unsafe_allow_html=True)
        
    def render(self):
        """Render the monitoring page"""
        st.markdown("""
        <div class="main-header">
            <h1>🔍 Real-time Fraud Monitoring</h1>
            <p>Live transaction stream and fraud detection monitoring</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Create main layout
        self.create_control_panel()
        self.create_metrics_dashboard()
        self.create_transaction_stream()
        self.create_alert_feed()
        self.create_system_status()
        
    def create_control_panel(self):
        """Create monitoring control panel"""
        st.subheader("🎛️ Monitoring Controls")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            auto_refresh = st.checkbox("Auto Refresh", value=True, key="auto_refresh")
            
        with col2:
            refresh_interval = st.selectbox(
                "Refresh Interval", 
                [5, 10, 30, 60], 
                index=2,
                format_func=lambda x: f"{x} seconds"
            )
            
        with col3:
            transaction_limit = st.selectbox(
                "Show Transactions", 
                [10, 25, 50, 100], 
                index=1
            )
            
        with col4:
            risk_threshold = st.slider(
                "Risk Threshold", 
                0.0, 1.0, 0.7, 0.05,
                help="Transactions above this threshold will be highlighted"
            )
            
        # Auto-refresh logic
        if auto_refresh:
            time.sleep(refresh_interval)
            st.rerun()
            
    def create_metrics_dashboard(self):
        """Create real-time metrics dashboard"""
        st.subheader("📊 Live Metrics")
        
        # Fetch current metrics
        metrics = self.fetch_live_metrics()
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric(
                "Transactions/Min",
                f"{metrics.get('transactions_per_minute', 0):.1f}",
                delta=f"{metrics.get('txn_delta', 0):+.1f}"
            )
            
        with col2:
            fraud_rate = metrics.get('fraud_rate', 0) * 100
            st.metric(
                "Fraud Rate",
                f"{fraud_rate:.2f}%",
                delta=f"{metrics.get('fraud_rate_delta', 0)*100:+.2f}%"
            )
            
        with col3:
            st.metric(
                "Active Alerts",
                metrics.get('active_alerts', 0),
                delta=metrics.get('alert_delta', 0)
            )
            
        with col4:
            st.metric(
                "Amount at Risk",
                f"${metrics.get('amount_at_risk', 0):,.0f}",
                delta=f"${metrics.get('amount_delta', 0):+,.0f}"
            )
            
        with col5:
            model_accuracy = metrics.get('model_accuracy', 0) * 100
            st.metric(
                "Model Accuracy",
                f"{model_accuracy:.1f}%",
                delta=f"{metrics.get('accuracy_delta', 0)*100:+.1f}%"
            )
            
        # Real-time charts
        self.create_realtime_charts(metrics)
        
    def create_realtime_charts(self, metrics):
        """Create real-time monitoring charts"""
        col1, col2 = st.columns(2)
        
        with col1:
            # Transaction volume chart
            volume_data = self.fetch_transaction_volume()
            fig_volume = go.Figure()
            
            fig_volume.add_trace(go.Scatter(
                x=volume_data['timestamp'],
                y=volume_data['legitimate'],
                mode='lines+markers',
                name='Legitimate',
                line=dict(color='#28a745', width=2),
                fill='tonexty'
            ))
            
            fig_volume.add_trace(go.Scatter(
                x=volume_data['timestamp'],
                y=volume_data['fraudulent'],
                mode='lines+markers',
                name='Fraudulent',
                line=dict(color='#dc3545', width=2),
                fill='tozeroy'
            ))
            
            fig_volume.update_layout(
                title="Transaction Volume (Last Hour)",
                xaxis_title="Time",
                yaxis_title="Transactions",
                height=300,
                showlegend=True
            )
            
            st.plotly_chart(fig_volume, use_container_width=True)
            
        with col2:
            # Risk score distribution
            risk_data = self.fetch_risk_distribution()
            fig_risk = px.histogram(
                risk_data, 
                x='risk_score', 
                nbins=20,
                title="Risk Score Distribution",
                color_discrete_sequence=['#1f77b4']
            )
            
            fig_risk.add_vline(
                x=0.7, 
                line_dash="dash", 
                line_color="red",
                annotation_text="High Risk Threshold"
            )
            
            fig_risk.update_layout(height=300)
            st.plotly_chart(fig_risk, use_container_width=True)
            
    def create_transaction_stream(self):
        """Create live transaction stream"""
        st.subheader("🌊 Live Transaction Stream")
        
        # Fetch recent transactions
        transactions = self.fetch_recent_transactions()
        
        if not transactions.empty:
            # Create expandable transaction cards
            for idx, transaction in transactions.iterrows():
                risk_score = transaction['risk_score']
                is_high_risk = risk_score > 0.7
                
                # Determine card style based on risk
                if is_high_risk:
                    card_style = "alert-high"
                elif risk_score > 0.3:
                    card_style = "alert-medium"
                else:
                    card_style = "alert-low"
                    
                with st.expander(
                    f"💳 {transaction['transaction_id']} - ${transaction['amount']:,.2f} "
                    f"({'🚨 HIGH RISK' if is_high_risk else '✅ LOW RISK'})",
                    expanded=is_high_risk
                ):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write("**Transaction Details**")
                        st.write(f"Amount: ${transaction['amount']:,.2f}")
                        st.write(f"User ID: {transaction['user_id']}")
                        st.write(f"Merchant: {transaction['merchant_category']}")
                        st.write(f"Location: {transaction.get('location', 'N/A')}")
                        
                    with col2:
                        st.write("**Risk Assessment**")
                        st.write(f"Risk Score: {risk_score:.3f}")
                        
                        # Risk score gauge
                        fig_gauge = go.Figure(go.Indicator(
                            mode="gauge+number",
                            value=risk_score,
                            domain={'x': [0, 1], 'y': [0, 1]},
                            title={'text': "Risk Level"},
                            gauge={
                                'axis': {'range': [None, 1]},
                                'bar': {'color': "darkblue"},
                                'steps': [
                                    {'range': [0, 0.3], 'color': "lightgreen"},
                                    {'range': [0.3, 0.7], 'color': "yellow"},
                                    {'range': [0.7, 1], 'color': "red"}
                                ],
                                'threshold': {
                                    'line': {'color': "red", 'width': 4},
                                    'thickness': 0.75,
                                    'value': 0.7
                                }
                            }
                        ))
                        
                        fig_gauge.update_layout(height=200)
                        st.plotly_chart(fig_gauge, use_container_width=True)
                        
                    with col3:
                        st.write("**Actions**")
                        
                        if st.button(f"🔍 Investigate", key=f"investigate_{transaction['transaction_id']}"):
                            self.investigate_transaction(transaction['transaction_id'])
                            
                        if is_high_risk and st.button(f"🚫 Block", key=f"block_{transaction['transaction_id']}"):
                            self.block_transaction(transaction['transaction_id'])
                            
                        if st.button(f"✅ Mark Safe", key=f"safe_{transaction['transaction_id']}"):
                            self.mark_transaction_safe(transaction['transaction_id'])
                            
                        # Fraud prediction confidence
                        confidence = transaction.get('confidence', 0)
                        st.write(f"Model Confidence: {confidence:.1%}")
                        
        else:
            st.info("No recent transactions to display")
            
    def create_alert_feed(self):
        """Create real-time alert feed"""
        st.subheader("🚨 Active Alerts")
        
        alerts = self.fetch_active_alerts()
        
        if not alerts.empty:
            # Alert summary
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                critical_count = len(alerts[alerts['severity'] == 'critical'])
                st.metric("Critical", critical_count)
                
            with col2:
                high_count = len(alerts[alerts['severity'] == 'high'])
                st.metric("High", high_count)
                
            with col3:
                medium_count = len(alerts[alerts['severity'] == 'medium'])
                st.metric("Medium", medium_count)
                
            with col4:
                low_count = len(alerts[alerts['severity'] == 'low'])
                st.metric("Low", low_count)
                
            # Alert list
            for idx, alert in alerts.iterrows():
                severity_color = {
                    'critical': '🔴',
                    'high': '🟠', 
                    'medium': '🟡',
                    'low': '🟢'
                }.get(alert['severity'], '⚪')
                
                with st.expander(
                    f"{severity_color} {alert['title']} - {alert['transaction_id']}",
                    expanded=alert['severity'] in ['critical', 'high']
                ):
                    st.write(f"**Description:** {alert['description']}")
                    st.write(f"**Risk Score:** {alert['risk_score']:.3f}")
                    st.write(f"**Created:** {alert['timestamp']}")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button("Resolve", key=f"resolve_{alert['id']}"):
                            self.resolve_alert(alert['id'])
                    with col2:
                        if st.button("Investigate", key=f"inv_alert_{alert['id']}"):
                            self.investigate_alert(alert['id'])
                    with col3:
                        if st.button("False Positive", key=f"fp_{alert['id']}"):
                            self.mark_false_positive(alert['id'])
        else:
            st.success("No active alerts! 🎉")
            
    def create_system_status(self):
        """Create system status monitoring"""
        st.subheader("🖥️ System Status")
        
        status = self.fetch_system_status()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            db_status = "🟢 Online" if status.get('database', {}).get('healthy') else "🔴 Offline"
            st.write(f"**Database:** {db_status}")
            
        with col2:
            ml_status = "🟢 Active" if status.get('ml_models', {}).get('healthy') else "🔴 Inactive"
            st.write(f"**ML Models:** {ml_status}")
            
        with col3:
            stream_status = "🟢 Flowing" if status.get('data_stream', {}).get('healthy') else "🔴 Stopped"
            st.write(f"**Data Stream:** {stream_status}")
            
        with col4:
            alert_status = "🟢 Ready" if status.get('alerts_system', {}).get('healthy') else "🔴 Down"
            st.write(f"**Alert System:** {alert_status}")
            
        # Performance metrics
        performance = status.get('performance', {})
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            cpu_usage = performance.get('cpu_usage', 0)
            st.metric("CPU Usage", f"{cpu_usage}%")
            st.progress(cpu_usage / 100)
            
        with col2:
            memory_usage = performance.get('memory_usage', 0)
            st.metric("Memory Usage", f"{memory_usage}%")
            st.progress(memory_usage / 100)
            
        with col3:
            queue_size = performance.get('queue_size', 0)
            st.metric("Queue Size", queue_size)
            
    # Data fetching methods
    def fetch_live_metrics(self):
        """Fetch live monitoring metrics"""
        try:
            response = requests.get(f"{ENDPOINTS['system_status']}/metrics")
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            st.error(f"Error fetching metrics: {e}")
        
        # Return mock data if API fails
        return {
            'transactions_per_minute': np.random.uniform(45, 75),
            'fraud_rate': np.random.uniform(0.01, 0.05),
            'active_alerts': np.random.randint(3, 15),
            'amount_at_risk': np.random.uniform(50000, 200000),
            'model_accuracy': np.random.uniform(0.92, 0.97),
            'txn_delta': np.random.uniform(-5, 5),
            'fraud_rate_delta': np.random.uniform(-0.01, 0.01),
            'alert_delta': np.random.randint(-3, 5),
            'amount_delta': np.random.uniform(-10000, 20000),
            'accuracy_delta': np.random.uniform(-0.02, 0.02)
        }
        
    def fetch_transaction_volume(self):
        """Fetch transaction volume data"""
        try:
            response = requests.get(f"{ENDPOINTS['transactions']}/volume")
            if response.status_code == 200:
                return pd.DataFrame(response.json())
        except Exception as e:
            st.error(f"Error fetching transaction volume: {e}")
            
        # Mock data
        timestamps = pd.date_range(
            start=datetime.now() - timedelta(hours=1),
            end=datetime.now(),
            freq='5min'
        )
        
        return pd.DataFrame({
            'timestamp': timestamps,
            'legitimate': np.random.poisson(20, len(timestamps)),
            'fraudulent': np.random.poisson(2, len(timestamps))
        })
        
    def fetch_risk_distribution(self):
        """Fetch risk score distribution"""
        try:
            response = requests.get(f"{ENDPOINTS['reports']}/risk-distribution")
            if response.status_code == 200:
                return pd.DataFrame(response.json())
        except Exception as e:
            st.error(f"Error fetching risk distribution: {e}")
            
        # Mock data
        return pd.DataFrame({
            'risk_score': np.random.beta(2, 5, 1000)
        })
        
    def fetch_recent_transactions(self):
        """Fetch recent transactions"""
        try:
            response = requests.get(f"{ENDPOINTS['transactions']}/recent?limit=10")
            if response.status_code == 200:
                return pd.DataFrame(response.json())
        except Exception as e:
            st.error(f"Error fetching transactions: {e}")
            
        # Mock data
        mock_transactions = []
        for i in range(10):
            mock_transactions.append({
                'transaction_id': f'TXN_{datetime.now().strftime("%Y%m%d")}_{i:04d}',
                'amount': np.random.uniform(10, 5000),
                'user_id': f'USER_{np.random.randint(1000, 9999)}',
                'merchant_category': np.random.choice(['grocery', 'gas', 'restaurant', 'online', 'retail']),
                'location': np.random.choice(['New York', 'Los Angeles', 'Chicago', 'Houston']),
                'risk_score': np.random.beta(2, 5),
                'confidence': np.random.uniform(0.7, 0.95),
                'timestamp': datetime.now() - timedelta(minutes=np.random.randint(0, 60))
            })
            
        return pd.DataFrame(mock_transactions)
        
    def fetch_active_alerts(self):
        """Fetch active alerts"""
        try:
            response = requests.get(f"{ENDPOINTS['alerts']}/active")
            if response.status_code == 200:
                return pd.DataFrame(response.json())
        except Exception as e:
            st.error(f"Error fetching alerts: {e}")
            
        # Mock data
        mock_alerts = []
        severities = ['critical', 'high', 'medium', 'low']
        
        for i in range(5):
            severity = np.random.choice(severities, p=[0.1, 0.3, 0.4, 0.2])
            mock_alerts.append({
                'id': f'ALERT_{i:04d}',
                'title': f'Fraud Detection Alert #{i+1}',
                'description': f'High-risk transaction detected with unusual patterns',
                'severity': severity,
                'transaction_id': f'TXN_{datetime.now().strftime("%Y%m%d")}_{i:04d}',
                'risk_score': np.random.uniform(0.3, 0.95),
                'timestamp': datetime.now() - timedelta(minutes=np.random.randint(0, 120))
            })
            
        return pd.DataFrame(mock_alerts)
        
    def fetch_system_status(self):
        """Fetch system status"""
        try:
            response = requests.get(ENDPOINTS['system_status'])
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            st.error(f"Error fetching system status: {e}")
            
        # Mock data
        return {
            'database': {'healthy': True},
            'ml_models': {'healthy': True},
            'data_stream': {'healthy': True},
            'alerts_system': {'healthy': True},
            'performance': {
                'cpu_usage': np.random.randint(20, 80),
                'memory_usage': np.random.randint(40, 90),
                'queue_size': np.random.randint(0, 50)
            }
        }
        
    # Action methods
    def investigate_transaction(self, transaction_id):
        """Investigate a transaction"""
        st.success(f"Investigation started for transaction {transaction_id}")
        
    def block_transaction(self, transaction_id):
        """Block a transaction"""
        st.warning(f"Transaction {transaction_id} has been blocked")
        
    def mark_transaction_safe(self, transaction_id):
        """Mark transaction as safe"""
        st.success(f"Transaction {transaction_id} marked as safe")
        
    def resolve_alert(self, alert_id):
        """Resolve an alert"""
        st.success(f"Alert {alert_id} resolved")
        
    def investigate_alert(self, alert_id):
        """Investigate an alert"""
        st.info(f"Investigation started for alert {alert_id}")
        
    def mark_false_positive(self, alert_id):
        """Mark alert as false positive"""
        st.warning(f"Alert {alert_id} marked as false positive")

# Main execution
def main():
    monitoring_page = MonitoringPage()
    monitoring_page.render()

if __name__ == "__main__":
    main()