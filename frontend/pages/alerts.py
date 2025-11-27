"""
Alerts management page for Streamlit dashboard
Provides comprehensive alert management and analysis
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
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import configuration - use try/except for compatibility
try:
    from config import API_BASE_URL
    ENDPOINTS = {"alerts": f"{API_BASE_URL}/monitoring/alerts"}
except ImportError:
    ENDPOINTS = {"alerts": "http://localhost:5000/api/monitoring/alerts"}

PAGE_CONFIG = {
    "page_title": "FraudGuard - Alerts",
    "page_icon": "🚨",
    "layout": "wide"
}

COMMON_STYLE = """
<style>
/* Import Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* Global Styles */
* {
    font-family: 'Inter', sans-serif;
}

/* Main App Background */
.main {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    background-attachment: fixed;
}

/* Content Container */
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    background: rgba(255, 255, 255, 0.95);
    border-radius: 20px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
    animation: fadeIn 0.6s ease-out;
}

/* Header Styling */
.main-header {
    font-size: 3rem;
    font-weight: 800;
    text-align: center;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 2rem;
    animation: slideInDown 0.8s ease-out;
}

/* Sidebar Styling */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    padding: 2rem 1rem;
}

[data-testid="stSidebar"] * {
    color: white !important;
}

/* Metric Cards */
[data-testid="stMetric"] {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 1.5rem;
    border-radius: 15px;
    box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    transition: all 0.3s ease;
    animation: fadeInUp 0.6s ease-out;
}

[data-testid="stMetric"]:hover {
    transform: translateY(-5px);
    box-shadow: 0 15px 40px rgba(102, 126, 234, 0.4);
}

[data-testid="stMetric"] label {
    color: rgba(255, 255, 255, 0.9) !important;
    font-weight: 600 !important;
}

[data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: white !important;
    font-weight: 700 !important;
    font-size: 2rem !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    font-weight: 600;
    padding: 0.75rem 2rem;
    border-radius: 10px;
    border: none;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    transition: all 0.3s ease;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
}

/* Input Fields */
.stTextInput input, .stNumberInput input, .stSelectbox select {
    border-radius: 10px;
    border: 2px solid #e0e0e0;
    padding: 0.75rem;
    transition: all 0.3s ease;
}

.stTextInput input:focus, .stNumberInput input:focus, .stSelectbox select:focus {
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

/* Headers */
h1, h2, h3 {
    color: #2d3748;
    font-weight: 700;
}

/* Success/Error/Warning Messages */
.stSuccess, .stError, .stWarning, .stInfo {
    border-radius: 10px;
    padding: 1rem;
    animation: slideInLeft 0.5s ease-out;
}

/* Animations */
@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes slideInDown {
    from {
        opacity: 0;
        transform: translateY(-30px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes slideInLeft {
    from {
        opacity: 0;
        transform: translateX(-20px);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}

/* Custom Scrollbar */
::-webkit-scrollbar {
    width: 10px;
    height: 10px;
}

::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 10px;
}

::-webkit-scrollbar-thumb {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 10px;
}

/* Plotly Charts */
.js-plotly-plot {
    border-radius: 15px;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
}
</style>
"""

class AlertsPage:
    def __init__(self):
        self.setup_page()
        
    def setup_page(self):
        """Configure the Streamlit page"""
        st.set_page_config(**PAGE_CONFIG)
        st.markdown(COMMON_STYLE, unsafe_allow_html=True)
        
    def render(self):
        """Render the alerts page"""
        st.markdown("""
        <div class="main-header">
            <h1>🚨 Alert Management Center</h1>
            <p>Comprehensive fraud alert management and analysis</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Create main layout
        self.create_alert_overview()
        self.create_alert_filters()
        self.create_alert_analytics()
        self.create_alert_management()
        self.create_alert_history()
        
    def create_alert_overview(self):
        """Create alerts overview dashboard"""
        st.subheader("📊 Alert Overview")
        
        # Fetch alert statistics
        alert_stats = self.fetch_alert_statistics()
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric(
                "Total Alerts Today",
                alert_stats.get('total_today', 0),
                delta=alert_stats.get('total_delta', 0)
            )
            
        with col2:
            st.metric(
                "Critical Alerts",
                alert_stats.get('critical', 0),
                delta=alert_stats.get('critical_delta', 0)
            )
            
        with col3:
            resolution_rate = alert_stats.get('resolution_rate', 0) * 100
            st.metric(
                "Resolution Rate",
                f"{resolution_rate:.1f}%",
                delta=f"{alert_stats.get('resolution_delta', 0)*100:+.1f}%"
            )
            
        with col4:
            avg_response = alert_stats.get('avg_response_time', 0)
            st.metric(
                "Avg Response Time",
                f"{avg_response:.1f} min",
                delta=f"{alert_stats.get('response_delta', 0):+.1f} min"
            )
            
        with col5:
            false_positive_rate = alert_stats.get('false_positive_rate', 0) * 100
            st.metric(
                "False Positive Rate",
                f"{false_positive_rate:.1f}%",
                delta=f"{alert_stats.get('fp_delta', 0)*100:+.1f}%"
            )
            
        # Alert trend chart
        self.create_alert_trend_chart()
        
    def create_alert_trend_chart(self):
        """Create alert trend visualization"""
        col1, col2 = st.columns(2)
        
        with col1:
            # Alert volume over time
            alert_volume = self.fetch_alert_volume()
            
            fig_volume = go.Figure()
            
            severities = ['critical', 'high', 'medium', 'low']
            colors = ['#dc3545', '#fd7e14', '#ffc107', '#28a745']
            
            for severity, color in zip(severities, colors):
                if severity in alert_volume.columns:
                    fig_volume.add_trace(go.Scatter(
                        x=alert_volume['timestamp'],
                        y=alert_volume[severity],
                        mode='lines+markers',
                        name=severity.title(),
                        line=dict(color=color, width=2),
                        stackgroup='one'
                    ))
                    
            fig_volume.update_layout(
                title="Alert Volume by Severity (Last 7 Days)",
                xaxis_title="Date",
                yaxis_title="Number of Alerts",
                height=400,
                hovermode='x unified'
            )
            
            st.plotly_chart(fig_volume, use_container_width=True)
            
        with col2:
            # Alert status distribution
            status_data = self.fetch_alert_status_distribution()
            
            fig_status = px.pie(
                status_data,
                values='count',
                names='status',
                title="Alert Status Distribution",
                color_discrete_map={
                    'new': '#007bff',
                    'investigating': '#ffc107',
                    'resolved': '#28a745',
                    'false_positive': '#6c757d'
                }
            )
            
            fig_status.update_layout(height=400)
            st.plotly_chart(fig_status, use_container_width=True)
            
    def create_alert_filters(self):
        """Create alert filtering interface"""
        st.subheader("🔍 Filter Alerts")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            severity_filter = st.multiselect(
                "Severity",
                ['critical', 'high', 'medium', 'low'],
                default=['critical', 'high']
            )
            
        with col2:
            status_filter = st.multiselect(
                "Status",
                ['new', 'investigating', 'resolved', 'false_positive'],
                default=['new', 'investigating']
            )
            
        with col3:
            date_range = st.selectbox(
                "Time Range",
                ['Last Hour', 'Last 6 Hours', 'Last 24 Hours', 'Last 7 Days', 'Last 30 Days'],
                index=2
            )
            
        with col4:
            risk_range = st.slider(
                "Risk Score Range",
                0.0, 1.0, (0.3, 1.0), 0.1
            )
            
        with col5:
            search_term = st.text_input(
                "Search",
                placeholder="Transaction ID, User ID, etc."
            )
            
        # Store filters in session state
        st.session_state.alert_filters = {
            'severity': severity_filter,
            'status': status_filter,
            'date_range': date_range,
            'risk_range': risk_range,
            'search': search_term
        }
        
    def create_alert_analytics(self):
        """Create alert analytics section"""
        st.subheader("📈 Alert Analytics")
        
        tab1, tab2, tab3, tab4 = st.tabs(["Severity Analysis", "Time Patterns", "Risk Correlation", "Performance Metrics"])
        
        with tab1:
            self.create_severity_analysis()
            
        with tab2:
            self.create_time_pattern_analysis()
            
        with tab3:
            self.create_risk_correlation_analysis()
            
        with tab4:
            self.create_performance_metrics()
            
    def create_severity_analysis(self):
        """Create severity analysis charts"""
        severity_data = self.fetch_severity_analysis()
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Severity distribution by hour
            fig_heatmap = px.density_heatmap(
                severity_data,
                x='hour',
                y='severity',
                z='count',
                title="Alert Severity by Hour of Day",
                color_continuous_scale="Reds"
            )
            
            fig_heatmap.update_layout(height=300)
            st.plotly_chart(fig_heatmap, use_container_width=True)
            
        with col2:
            # Average resolution time by severity
            resolution_data = severity_data.groupby('severity')['resolution_time'].mean().reset_index()
            
            fig_resolution = px.bar(
                resolution_data,
                x='severity',
                y='resolution_time',
                title="Average Resolution Time by Severity",
                color='severity',
                color_discrete_map={
                    'critical': '#dc3545',
                    'high': '#fd7e14',
                    'medium': '#ffc107',
                    'low': '#28a745'
                }
            )
            
            fig_resolution.update_layout(height=300)
            st.plotly_chart(fig_resolution, use_container_width=True)
            
    def create_time_pattern_analysis(self):
        """Create time pattern analysis"""
        time_data = self.fetch_time_patterns()
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Alerts by day of week
            fig_weekday = px.bar(
                time_data['weekday_data'],
                x='day_name',
                y='alert_count',
                title="Alerts by Day of Week",
                color='alert_count',
                color_continuous_scale="Blues"
            )
            
            fig_weekday.update_layout(height=300)
            st.plotly_chart(fig_weekday, use_container_width=True)
            
        with col2:
            # Hourly alert pattern
            fig_hourly = px.line(
                time_data['hourly_data'],
                x='hour',
                y='alert_count',
                title="Alert Pattern by Hour",
                markers=True
            )
            
            fig_hourly.add_hline(
                y=time_data['hourly_data']['alert_count'].mean(),
                line_dash="dash",
                line_color="red",
                annotation_text="Average"
            )
            
            fig_hourly.update_layout(height=300)
            st.plotly_chart(fig_hourly, use_container_width=True)
            
    def create_risk_correlation_analysis(self):
        """Create risk correlation analysis"""
        correlation_data = self.fetch_risk_correlation()
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Risk score vs Alert severity correlation
            fig_scatter = px.scatter(
                correlation_data,
                x='risk_score',
                y='severity_numeric',
                size='transaction_amount',
                color='merchant_category',
                title="Risk Score vs Alert Severity",
                hover_data=['transaction_id', 'user_id']
            )
            
            fig_scatter.update_layout(height=350)
            st.plotly_chart(fig_scatter, use_container_width=True)
            
        with col2:
            # Feature importance for alerts
            feature_importance = correlation_data.groupby('feature')['importance'].mean().sort_values(ascending=True)
            
            fig_importance = px.bar(
                x=feature_importance.values,
                y=feature_importance.index,
                orientation='h',
                title="Feature Importance for Alert Generation"
            )
            
            fig_importance.update_layout(height=350)
            st.plotly_chart(fig_importance, use_container_width=True)
            
    def create_performance_metrics(self):
        """Create performance metrics analysis"""
        performance_data = self.fetch_performance_metrics()
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Alert processing time distribution
            fig_processing = px.histogram(
                performance_data,
                x='processing_time',
                nbins=30,
                title="Alert Processing Time Distribution",
                marginal="box"
            )
            
            fig_processing.update_layout(height=350)
            st.plotly_chart(fig_processing, use_container_width=True)
            
        with col2:
            # Model performance over time
            model_performance = performance_data.groupby('date').agg({
                'precision': 'mean',
                'recall': 'mean',
                'f1_score': 'mean'
            }).reset_index()
            
            fig_model = go.Figure()
            
            for metric in ['precision', 'recall', 'f1_score']:
                fig_model.add_trace(go.Scatter(
                    x=model_performance['date'],
                    y=model_performance[metric],
                    mode='lines+markers',
                    name=metric.replace('_', ' ').title()
                ))
                
            fig_model.update_layout(
                title="Model Performance Over Time",
                xaxis_title="Date",
                yaxis_title="Score",
                height=350
            )
            
            st.plotly_chart(fig_model, use_container_width=True)
            
    def create_alert_management(self):
        """Create alert management interface"""
        st.subheader("🛠️ Alert Management")
        
        # Bulk actions
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🔄 Refresh Alerts", type="primary"):
                st.rerun()
                
        with col2:
            if st.button("✅ Bulk Resolve", help="Resolve selected alerts"):
                self.bulk_resolve_alerts()
                
        with col3:
            if st.button("📊 Export Report"):
                self.export_alert_report()
                
        with col4:
            if st.button("⚙️ Configure Rules"):
                self.show_rule_configuration()
                
        # Fetch and display alerts
        alerts_df = self.fetch_filtered_alerts()
        
        if not alerts_df.empty:
            # Add selection checkboxes
            selected_alerts = []
            
            for idx, alert in alerts_df.iterrows():
                with st.container():
                    col1, col2 = st.columns([1, 15])
                    
                    with col1:
                        if st.checkbox("", key=f"select_{alert['id']}"):
                            selected_alerts.append(alert['id'])
                            
                    with col2:
                        self.render_alert_card(alert)
                        
            # Store selected alerts
            st.session_state.selected_alerts = selected_alerts
            
        else:
            st.info("No alerts match the current filters")
            
    def render_alert_card(self, alert):
        """Render individual alert card"""
        severity_colors = {
            'critical': '#dc3545',
            'high': '#fd7e14',
            'medium': '#ffc107',
            'low': '#28a745'
        }
        
        severity_color = severity_colors.get(alert['severity'], '#6c757d')
        
        # Create alert card
        with st.expander(
            f"🚨 {alert['title']} - {alert['severity'].upper()}",
            expanded=alert['severity'] in ['critical', 'high']
        ):
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.markdown(f"""
                **Alert ID:** {alert['id']}  
                **Description:** {alert['description']}  
                **Transaction ID:** {alert['transaction_id']}  
                **User ID:** {alert.get('user_id', 'N/A')}  
                **Amount:** ${alert.get('amount', 0):,.2f}  
                **Risk Score:** {alert['risk_score']:.3f}  
                **Created:** {alert['timestamp']}  
                **Status:** {alert['status'].title()}
                """)
                
            with col2:
                # Risk gauge
                fig_gauge = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=alert['risk_score'],
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "Risk Level"},
                    gauge={
                        'axis': {'range': [None, 1]},
                        'bar': {'color': severity_color},
                        'steps': [
                            {'range': [0, 0.3], 'color': "lightgreen"},
                            {'range': [0.3, 0.7], 'color': "yellow"},
                            {'range': [0.7, 1], 'color': "red"}
                        ]
                    }
                ))
                
                fig_gauge.update_layout(height=200, margin=dict(l=20, r=20, t=20, b=20))
                st.plotly_chart(fig_gauge, use_container_width=True)
                
            with col3:
                st.markdown("**Actions:**")
                
                if alert['status'] == 'new':
                    if st.button("🔍 Investigate", key=f"investigate_{alert['id']}"):
                        self.investigate_alert(alert['id'])
                        
                if alert['status'] in ['new', 'investigating']:
                    if st.button("✅ Resolve", key=f"resolve_{alert['id']}"):
                        self.resolve_alert(alert['id'])
                        
                if st.button("❌ False Positive", key=f"fp_{alert['id']}"):
                    self.mark_false_positive(alert['id'])
                    
                if st.button("📝 Add Note", key=f"note_{alert['id']}"):
                    self.add_alert_note(alert['id'])
                    
                if st.button("📤 Escalate", key=f"escalate_{alert['id']}"):
                    self.escalate_alert(alert['id'])
                    
            # Show alert details if available
            if 'details' in alert and alert['details']:
                st.markdown("**Additional Details:**")
                st.json(alert['details'])
                
    def create_alert_history(self):
        """Create alert history visualization"""
        st.subheader("📜 Alert History & Trends")
        
        history_data = self.fetch_alert_history()
        
        # Historical trends
        col1, col2 = st.columns(2)
        
        with col1:
            # Monthly alert trends
            monthly_trends = history_data.groupby(['month', 'severity']).size().reset_index(name='count')
            
            fig_monthly = px.line(
                monthly_trends,
                x='month',
                y='count',
                color='severity',
                title="Monthly Alert Trends by Severity",
                color_discrete_map={
                    'critical': '#dc3545',
                    'high': '#fd7e14',
                    'medium': '#ffc107',
                    'low': '#28a745'
                }
            )
            
            fig_monthly.update_layout(height=350)
            st.plotly_chart(fig_monthly, use_container_width=True)
            
        with col2:
            # Alert resolution efficiency
            resolution_trends = history_data.groupby('month').agg({
                'resolution_time': 'mean',
                'false_positive_rate': 'mean'
            }).reset_index()
            
            fig_efficiency = make_subplots(
                rows=2, cols=1,
                subplot_titles=("Avg Resolution Time", "False Positive Rate"),
                vertical_spacing=0.12
            )
            
            fig_efficiency.add_trace(
                go.Scatter(
                    x=resolution_trends['month'],
                    y=resolution_trends['resolution_time'],
                    mode='lines+markers',
                    name='Resolution Time',
                    line=dict(color='#007bff')
                ),
                row=1, col=1
            )
            
            fig_efficiency.add_trace(
                go.Scatter(
                    x=resolution_trends['month'],
                    y=resolution_trends['false_positive_rate'],
                    mode='lines+markers',
                    name='False Positive Rate',
                    line=dict(color='#dc3545')
                ),
                row=2, col=1
            )
            
            fig_efficiency.update_layout(height=350, showlegend=False)
            st.plotly_chart(fig_efficiency, use_container_width=True)
            
    # Data fetching methods
    def fetch_alert_statistics(self):
        """Fetch alert statistics"""
        try:
            response = requests.get(f"{ENDPOINTS['alerts']}/statistics")
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            st.error(f"Error fetching alert statistics: {e}")
            
        # Mock data
        return {
            'total_today': np.random.randint(50, 150),
            'critical': np.random.randint(5, 20),
            'resolution_rate': np.random.uniform(0.7, 0.95),
            'avg_response_time': np.random.uniform(5, 30),
            'false_positive_rate': np.random.uniform(0.05, 0.15),
            'total_delta': np.random.randint(-10, 20),
            'critical_delta': np.random.randint(-3, 5),
            'resolution_delta': np.random.uniform(-0.05, 0.05),
            'response_delta': np.random.uniform(-5, 5),
            'fp_delta': np.random.uniform(-0.02, 0.02)
        }
        
    def fetch_alert_volume(self):
        """Fetch alert volume data"""
        try:
            response = requests.get(f"{ENDPOINTS['alerts']}/volume")
            if response.status_code == 200:
                return pd.DataFrame(response.json())
        except Exception as e:
            st.error(f"Error fetching alert volume: {e}")
            
        # Mock data
        dates = pd.date_range(
            start=datetime.now() - timedelta(days=7),
            end=datetime.now(),
            freq='D'
        )
        
        data = {
            'timestamp': dates,
            'critical': np.random.poisson(3, len(dates)),
            'high': np.random.poisson(8, len(dates)),
            'medium': np.random.poisson(15, len(dates)),
            'low': np.random.poisson(5, len(dates))
        }
        
        return pd.DataFrame(data)
        
    def fetch_alert_status_distribution(self):
        """Fetch alert status distribution"""
        # Mock data
        return pd.DataFrame({
            'status': ['new', 'investigating', 'resolved', 'false_positive'],
            'count': [25, 15, 120, 8]
        })
        
    def fetch_severity_analysis(self):
        """Fetch severity analysis data"""
        # Mock data
        data = []
        for _ in range(1000):
            data.append({
                'hour': np.random.randint(0, 24),
                'severity': np.random.choice(['critical', 'high', 'medium', 'low']),
                'count': np.random.randint(1, 10),
                'resolution_time': np.random.uniform(5, 60)
            })
        return pd.DataFrame(data)
        
    def fetch_time_patterns(self):
        """Fetch time pattern data"""
        weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        return {
            'weekday_data': pd.DataFrame({
                'day_name': weekdays,
                'alert_count': np.random.poisson(20, 7)
            }),
            'hourly_data': pd.DataFrame({
                'hour': range(24),
                'alert_count': np.random.poisson(5, 24)
            })
        }
        
    def fetch_risk_correlation(self):
        """Fetch risk correlation data"""
        # Mock data
        data = []
        for _ in range(500):
            data.append({
                'risk_score': np.random.beta(2, 3),
                'severity_numeric': np.random.choice([1, 2, 3, 4]),
                'transaction_amount': np.random.uniform(10, 10000),
                'merchant_category': np.random.choice(['grocery', 'gas', 'restaurant', 'online']),
                'transaction_id': f'TXN_{np.random.randint(1000, 9999)}',
                'user_id': f'USER_{np.random.randint(1000, 9999)}',
                'feature': np.random.choice(['amount', 'velocity', 'location', 'time']),
                'importance': np.random.uniform(0, 1)
            })
        return pd.DataFrame(data)
        
    def fetch_performance_metrics(self):
        """Fetch performance metrics data"""
        dates = pd.date_range(
            start=datetime.now() - timedelta(days=30),
            end=datetime.now(),
            freq='D'
        )
        
        data = []
        for date in dates:
            for _ in range(np.random.randint(10, 50)):
                data.append({
                    'date': date,
                    'processing_time': np.random.gamma(2, 2),
                    'precision': np.random.uniform(0.8, 0.95),
                    'recall': np.random.uniform(0.75, 0.92),
                    'f1_score': np.random.uniform(0.77, 0.93)
                })
        return pd.DataFrame(data)
        
    def fetch_filtered_alerts(self):
        """Fetch alerts based on current filters"""
        try:
            # Get filters from session state
            filters = st.session_state.get('alert_filters', {})
            severity = filters.get('severity', [])

            # Call the real API endpoint
            api_url = "http://localhost:5000/api/dashboard/alerts"
            params = {}

            # Apply severity filter if specified
            if severity and len(severity) == 1:
                params['severity'] = severity[0]

            response = requests.get(api_url, params=params, timeout=5)

            if response.status_code == 200:
                alerts_data = response.json().get('alerts', [])
                if alerts_data:
                    # Convert to DataFrame and add required fields
                    df = pd.DataFrame(alerts_data)

                    # Add user_id and details if not present
                    if 'user_id' not in df.columns:
                        df['user_id'] = 'N/A'
                    if 'details' not in df.columns:
                        df['details'] = None

                    return df

        except requests.RequestException as e:
            st.warning(f"Could not fetch real-time alerts: {e}. Using fallback data.")
        except Exception as e:
            st.warning(f"Error processing alerts: {e}")

        # Return empty dataframe if no data available
        return pd.DataFrame(columns=[
            'id', 'title', 'description', 'severity', 'status',
            'transaction_id', 'user_id', 'amount', 'risk_score',
            'timestamp', 'details'
        ])
        
    def fetch_alert_history(self):
        """Fetch historical alert data"""
        # Mock historical data
        months = pd.date_range(
            start=datetime.now() - timedelta(days=365),
            end=datetime.now(),
            freq='M'
        )
        
        data = []
        for month in months:
            for severity in ['critical', 'high', 'medium', 'low']:
                for _ in range(np.random.randint(20, 100)):
                    data.append({
                        'month': month,
                        'severity': severity,
                        'resolution_time': np.random.uniform(5, 120),
                        'false_positive_rate': np.random.uniform(0.05, 0.2)
                    })
                    
        return pd.DataFrame(data)
        
    # Action methods
    def investigate_alert(self, alert_id):
        """Investigate an alert"""
        st.success(f"Investigation started for alert {alert_id}")
        time.sleep(1)
        st.rerun()
        
    def resolve_alert(self, alert_id):
        """Resolve an alert"""
        st.success(f"Alert {alert_id} has been resolved")
        time.sleep(1)
        st.rerun()
        
    def mark_false_positive(self, alert_id):
        """Mark alert as false positive"""
        st.warning(f"Alert {alert_id} marked as false positive")
        time.sleep(1)
        st.rerun()
        
    def add_alert_note(self, alert_id):
        """Add note to alert"""
        note = st.text_area(f"Add note for alert {alert_id}")
        if st.button("Save Note"):
            st.success("Note added successfully")
            
    def escalate_alert(self, alert_id):
        """Escalate alert"""
        st.warning(f"Alert {alert_id} has been escalated to senior analyst")
        
    def bulk_resolve_alerts(self):
        """Bulk resolve selected alerts"""
        selected = st.session_state.get('selected_alerts', [])
        if selected:
            st.success(f"Resolved {len(selected)} alerts")
        else:
            st.warning("No alerts selected")
            
    def export_alert_report(self):
        """Export alert report"""
        st.success("Alert report exported successfully")
        
    def show_rule_configuration(self):
        """Show rule configuration interface"""
        with st.expander("Alert Rule Configuration", expanded=True):
            st.markdown("### Configure Alert Rules")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Risk Thresholds")
                critical_threshold = st.slider("Critical Alert Threshold", 0.0, 1.0, 0.9, 0.05)
                high_threshold = st.slider("High Alert Threshold", 0.0, 1.0, 0.7, 0.05)
                medium_threshold = st.slider("Medium Alert Threshold", 0.0, 1.0, 0.5, 0.05)
                
            with col2:
                st.subheader("Alert Conditions")
                velocity_enabled = st.checkbox("Enable Velocity Alerts", value=True)
                amount_enabled = st.checkbox("Enable Amount Alerts", value=True)
                location_enabled = st.checkbox("Enable Location Alerts", value=True)
                device_enabled = st.checkbox("Enable Device Alerts", value=True)
                
            if st.button("Save Configuration"):
                st.success("Alert rules updated successfully")

# Main execution
def main():
  alerts_page = AlertsPage()
  alerts_page.render()

if __name__ == "__main__":
   main()