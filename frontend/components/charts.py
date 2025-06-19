"""
Chart components for Streamlit fraud detection dashboard
Provides reusable chart components with consistent styling and functionality
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import requests
from . import COMPONENT_CONFIG, COMPONENT_STYLE, format_currency, format_percentage, get_risk_level_color

class ChartComponents:
    """Collection of reusable chart components for fraud detection dashboards"""
    
    def __init__(self):
        st.markdown(COMPONENT_STYLE, unsafe_allow_html=True)
        
    @staticmethod
    def fraud_rate_timeline(data, title="Fraud Rate Over Time", height=400):
        """
        Create a fraud rate timeline chart
        
        Args:
            data: DataFrame with columns ['timestamp', 'fraud_rate', 'transaction_count']
            title: Chart title
            height: Chart height in pixels
        """
        if data.empty:
            st.warning("No data available for fraud rate timeline")
            return
            
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Fraud rate line
        fig.add_trace(
            go.Scatter(
                x=data['timestamp'],
                y=data['fraud_rate'] * 100,
                mode='lines+markers',
                name='Fraud Rate (%)',
                line=dict(color=COMPONENT_CONFIG["color_scheme"]["danger"], width=3),
                marker=dict(size=6)
            ),
            secondary_y=False,
        )
        
        # Transaction volume bars
        fig.add_trace(
            go.Bar(
                x=data['timestamp'],
                y=data['transaction_count'],
                name='Transaction Count',
                opacity=0.3,
                marker_color=COMPONENT_CONFIG["color_scheme"]["info"]
            ),
            secondary_y=True,
        )
        
        fig.update_xaxes(title_text="Time")
        fig.update_yaxes(title_text="Fraud Rate (%)", secondary_y=False)
        fig.update_yaxes(title_text="Transaction Count", secondary_y=True)
        
        fig.update_layout(
            title=title,
            height=height,
            hovermode='x unified',
            template=COMPONENT_CONFIG["chart_template"]
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    @staticmethod
    def risk_score_distribution(data, title="Risk Score Distribution", height=400):
        """
        Create a risk score distribution histogram
        
        Args:
            data: DataFrame with columns ['risk_score', 'is_fraud']
            title: Chart title
            height: Chart height in pixels
        """
        if data.empty:
            st.warning("No data available for risk score distribution")
            return
            
        fig = px.histogram(
            data,
            x='risk_score',
            color='is_fraud',
            nbins=30,
            title=title,
            color_discrete_map={
                0: COMPONENT_CONFIG["color_scheme"]["success"],
                1: COMPONENT_CONFIG["color_scheme"]["danger"]
            },
            labels={
                'is_fraud': 'Transaction Type',
                'risk_score': 'Risk Score'
            },
            marginal="box"
        )
        
        # Add threshold lines
        fig.add_vline(x=0.3, line_dash="dash", line_color="orange", 
                     annotation_text="Medium Risk")
        fig.add_vline(x=0.7, line_dash="dash", line_color="red", 
                     annotation_text="High Risk")
        
        fig.update_layout(height=height, template=COMPONENT_CONFIG["chart_template"])
        
        st.plotly_chart(fig, use_container_width=True)
        
    @staticmethod
    def transaction_volume_by_category(data, title="Transaction Volume by Category", height=400):
        """
        Create a transaction volume chart by merchant category
        
        Args:
            data: DataFrame with columns ['merchant_category', 'transaction_count', 'fraud_count', 'total_amount']
            title: Chart title
            height: Chart height in pixels
        """
        if data.empty:
            st.warning("No data available for transaction volume by category")
            return
            
        # Calculate fraud rate
        data['fraud_rate'] = data['fraud_count'] / data['transaction_count']
        
        fig = px.bar(
            data,
            x='merchant_category',
            y='total_amount',
            color='fraud_rate',
            title=title,
            color_continuous_scale="Reds",
            hover_data=['transaction_count', 'fraud_count'],
            labels={
                'merchant_category': 'Merchant Category',
                'total_amount': 'Total Amount ($)',
                'fraud_rate': 'Fraud Rate'
            }
        )
        
        fig.update_layout(height=height, template=COMPONENT_CONFIG["chart_template"])
        
        st.plotly_chart(fig, use_container_width=True)
        
    @staticmethod
    def geographic_fraud_heatmap(data, title="Geographic Fraud Distribution", height=500):
        """
        Create a geographic heatmap of fraud distribution
        
        Args:
            data: DataFrame with columns ['state_code', 'state_name', 'fraud_rate', 'fraud_count']
            title: Chart title
            height: Chart height in pixels
        """
        if data.empty:
            st.warning("No data available for geographic fraud distribution")
            return
            
        fig = px.choropleth(
            data,
            locations='state_code',
            color='fraud_rate',
            hover_name='state_name',
            hover_data={'fraud_count': True, 'fraud_rate': ':.2%'},
            color_continuous_scale="Reds",
            scope="usa",
            title=title,
            labels={'fraud_rate': 'Fraud Rate'}
        )
        
        fig.update_layout(height=height, template=COMPONENT_CONFIG["chart_template"])
        
        st.plotly_chart(fig, use_container_width=True)
        
    @staticmethod
    def alert_severity_breakdown(data, chart_type="pie", title="Alert Severity Breakdown", height=400):
        """
        Create alert severity breakdown chart
        
        Args:
            data: DataFrame with columns ['severity', 'count']
            chart_type: 'pie' or 'bar'
            title: Chart title
            height: Chart height in pixels
        """
        if data.empty:
            st.warning("No data available for alert severity breakdown")
            return
            
        colors = {
            'critical': COMPONENT_CONFIG["color_scheme"]["danger"],
            'high': '#fd7e14',
            'medium': COMPONENT_CONFIG["color_scheme"]["warning"],
            'low': COMPONENT_CONFIG["color_scheme"]["success"]
        }
        
        if chart_type == "pie":
            fig = px.pie(
                data,
                values='count',
                names='severity',
                title=title,
                color='severity',
                color_discrete_map=colors
            )
        else:
            fig = px.bar(
                data,
                x='severity',
                y='count',
                title=title,
                color='severity',
                color_discrete_map=colors
            )
            
        fig.update_layout(height=height, template=COMPONENT_CONFIG["chart_template"])
        
        st.plotly_chart(fig, use_container_width=True)
        
    @staticmethod
    def model_performance_radar(data, title="Model Performance Metrics", height=400):
        """
        Create a radar chart for model performance metrics
        
        Args:
            data: Dict with metrics like {'precision': 0.92, 'recall': 0.89, 'f1_score': 0.90, 'accuracy': 0.94}
            title: Chart title
            height: Chart height in pixels
        """
        if not data:
            st.warning("No data available for model performance")
            return
            
        categories = list(data.keys())
        values = list(data.values())
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name='Current Model',
            line_color=COMPONENT_CONFIG["color_scheme"]["primary"]
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )),
            title=title,
            height=height,
            template=COMPONENT_CONFIG["chart_template"]
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    @staticmethod
    def risk_gauge(risk_score, title="Risk Level", height=300):
        """
        Create a gauge chart for risk score
        
        Args:
            risk_score: Float between 0 and 1
            title: Chart title
            height: Chart height in pixels
        """
        color = get_risk_level_color(risk_score)
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=risk_score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': title},
            delta={'reference': 0.5},
            gauge={
                'axis': {'range': [None, 1]},
                'bar': {'color': color},
                'steps': [
                    {'range': [0, 0.3], 'color': "lightgreen"},
                    {'range': [0.3, 0.7], 'color': "yellow"},
                    {'range': [0.7, 1], 'color': "lightcoral"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 0.7
                }
            }
        ))
        
        fig.update_layout(height=height, template=COMPONENT_CONFIG["chart_template"])
        
        st.plotly_chart(fig, use_container_width=True)
        
    @staticmethod
    def time_series_anomaly(data, title="Transaction Anomaly Detection", height=400):
        """
        Create a time series chart with anomaly detection
        
        Args:
            data: DataFrame with columns ['timestamp', 'value', 'is_anomaly', 'upper_bound', 'lower_bound']
            title: Chart title
            height: Chart height in pixels
        """
        if data.empty:
            st.warning("No data available for anomaly detection")
            return
            
        fig = go.Figure()
        
        # Normal points
        normal_data = data[data['is_anomaly'] == False]
        fig.add_trace(go.Scatter(
            x=normal_data['timestamp'],
            y=normal_data['value'],
            mode='markers',
            name='Normal',
            marker=dict(color=COMPONENT_CONFIG["color_scheme"]["primary"], size=6)
        ))
        
        # Anomalous points
        anomaly_data = data[data['is_anomaly'] == True]
        if not anomaly_data.empty:
            fig.add_trace(go.Scatter(
                x=anomaly_data['timestamp'],
                y=anomaly_data['value'],
                mode='markers',
                name='Anomaly',
                marker=dict(color=COMPONENT_CONFIG["color_scheme"]["danger"], size=8, symbol='x')
            ))
            
        # Confidence bounds
        if 'upper_bound' in data.columns and 'lower_bound' in data.columns:
            fig.add_trace(go.Scatter(
                x=data['timestamp'],
                y=data['upper_bound'],
                mode='lines',
                name='Upper Bound',
                line=dict(color='gray', dash='dash'),
                showlegend=False
            ))
            
            fig.add_trace(go.Scatter(
                x=data['timestamp'],
                y=data['lower_bound'],
                mode='lines',
                name='Lower Bound',
                line=dict(color='gray', dash='dash'),
                fill='tonexty',
                fillcolor='rgba(128,128,128,0.1)',
                showlegend=False
            ))
            
        fig.update_layout(
            title=title,
            xaxis_title="Time",
            yaxis_title="Value",
            height=height,
            template=COMPONENT_CONFIG["chart_template"]
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    @staticmethod
    def correlation_heatmap(correlation_matrix, title="Feature Correlation Matrix", height=500):
        """
        Create a correlation heatmap
        
        Args:
            correlation_matrix: DataFrame correlation matrix
            title: Chart title
            height: Chart height in pixels
        """
        if correlation_matrix.empty:
            st.warning("No data available for correlation matrix")
            return
            
        fig = px.imshow(
            correlation_matrix,
            text_auto=True,
            aspect="auto",
            title=title,
            color_continuous_scale="RdBu",
            zmin=-1,
            zmax=1
        )
        
        fig.update_layout(height=height, template=COMPONENT_CONFIG["chart_template"])
        
        st.plotly_chart(fig, use_container_width=True)
        
    @staticmethod
    def feature_importance_chart(data, title="Feature Importance", height=400, orientation="h"):
        """
        Create a feature importance chart
        
        Args:
            data: DataFrame with columns ['feature', 'importance']
            title: Chart title
            height: Chart height in pixels
            orientation: 'h' for horizontal or 'v' for vertical
        """
        if data.empty:
            st.warning("No data available for feature importance")
            return
            
        # Sort by importance
        data = data.sort_values('importance', ascending=(orientation == 'h'))
        
        if orientation == 'h':
            fig = px.bar(
                data,
                x='importance',
                y='feature',
                orientation='h',
                title=title,
                color='importance',
                color_continuous_scale="Blues"
            )
        else:
            fig = px.bar(
                data,
                x='feature',
                y='importance',
                title=title,
                color='importance',
                color_continuous_scale="Blues"
            )
            fig.update_xaxes(tickangle=45)
            
        fig.update_layout(height=height, template=COMPONENT_CONFIG["chart_template"])
        
        st.plotly_chart(fig, use_container_width=True)
        
    @staticmethod
    def confusion_matrix(cm_data, title="Confusion Matrix", height=400):
        """
        Create a confusion matrix heatmap
        
        Args:
            cm_data: 2D array or DataFrame representing confusion matrix
            title: Chart title
            height: Chart height in pixels
        """
        if cm_data is None or len(cm_data) == 0:
            st.warning("No data available for confusion matrix")
            return
            
        labels = ['Legitimate', 'Fraudulent']
        
        fig = px.imshow(
            cm_data,
            text_auto=True,
            aspect="auto",
            title=title,
            x=labels,
            y=labels,
            color_continuous_scale="Blues"
        )
        
        fig.update_layout(
            height=height,
            xaxis_title="Predicted",
            yaxis_title="Actual",
            template=COMPONENT_CONFIG["chart_template"]
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    @staticmethod
    def roc_curve(fpr, tpr, auc_score, title="ROC Curve", height=400):
        """
        Create an ROC curve chart
        
        Args:
            fpr: False positive rates
            tpr: True positive rates
            auc_score: AUC score
            title: Chart title
            height: Chart height in pixels
        """
        fig = go.Figure()
        
        # ROC curve
        fig.add_trace(go.Scatter(
            x=fpr,
            y=tpr,
            mode='lines',
            name=f'ROC Curve (AUC = {auc_score:.3f})',
            line=dict(color=COMPONENT_CONFIG["color_scheme"]["primary"], width=3)
        ))
        
        # Diagonal line (random classifier)
        fig.add_trace(go.Scatter(
            x=[0, 1],
            y=[0, 1],
            mode='lines',
            name='Random Classifier',
            line=dict(color='gray', dash='dash')
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title="False Positive Rate",
            yaxis_title="True Positive Rate",
            height=height,
            template=COMPONENT_CONFIG["chart_template"]
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    @staticmethod
    def create_metric_cards(metrics_data):
        """
        Create a row of metric cards
        
        Args:
            metrics_data: List of dicts with keys ['title', 'value', 'delta', 'format']
        """
        if not metrics_data:
            st.warning("No metrics data provided")
            return
            
        cols = st.columns(len(metrics_data))
        
        for i, metric in enumerate(metrics_data):
            with cols[i]:
                # Format value based on type
                if metric.get('format') == 'currency':
                    formatted_value = format_currency(metric['value'])
                elif metric.get('format') == 'percentage':
                    formatted_value = format_percentage(metric['value'])
                else:
                    formatted_value = f"{metric['value']:,}"
                    
                st.metric(
                    label=metric['title'],
                    value=formatted_value,
                    delta=metric.get('delta')
                )

# Utility functions for chart creation
def generate_sample_data(chart_type, num_points=100):
    """Generate sample data for testing charts"""
    
    if chart_type == "fraud_timeline":
        dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='D')
        return pd.DataFrame({
            'timestamp': dates,
            'fraud_rate': np.random.uniform(0.01, 0.05, len(dates)),
            'transaction_count': np.random.randint(1000, 5000, len(dates))
        })
        
    elif chart_type == "risk_distribution":
        legitimate = pd.DataFrame({
            'risk_score': np.random.beta(2, 8, int(num_points * 0.95)),
            'is_fraud': 0
        })
        fraudulent = pd.DataFrame({
            'risk_score': np.random.beta(8, 2, int(num_points * 0.05)),
            'is_fraud': 1
        })
        return pd.concat([legitimate, fraudulent], ignore_index=True)
        
    elif chart_type == "category_volume":
        categories = ['grocery', 'gas', 'restaurant', 'online', 'retail']
        return pd.DataFrame({
            'merchant_category': categories,
            'transaction_count': np.random.randint(1000, 10000, len(categories)),
            'fraud_count': np.random.randint(10, 200, len(categories)),
            'total_amount': np.random.uniform(50000, 500000, len(categories))
        })
        
    elif chart_type == "geographic":
        states = ['CA', 'NY', 'TX', 'FL', 'IL', 'PA', 'OH', 'MI', 'GA', 'NC']
        return pd.DataFrame({
            'state_code': states,
            'state_name': [f'State {code}' for code in states],
            'fraud_rate': np.random.uniform(0.01, 0.08, len(states)),
            'fraud_count': np.random.randint(50, 500, len(states))
        })
        
    elif chart_type == "alert_severity":
        return pd.DataFrame({
            'severity': ['critical', 'high', 'medium', 'low'],
            'count': np.random.randint(5, 50, 4)
        })
        
    elif chart_type == "model_performance":
        return {
            'precision': np.random.uniform(0.85, 0.95),
            'recall': np.random.uniform(0.80, 0.92),
            'f1_score': np.random.uniform(0.82, 0.93),
            'accuracy': np.random.uniform(0.88, 0.96)
        }
        
    elif chart_type == "feature_importance":
        features = ['amount', 'velocity', 'location_risk', 'time_anomaly', 'merchant_risk', 
                   'user_history', 'device_risk', 'behavioral_score']
        importance = np.random.uniform(0.05, 0.25, len(features))
        importance = importance / importance.sum()  # Normalize
        
        return pd.DataFrame({
            'feature': features,
            'importance': importance
        })
        
    else:
        return pd.DataFrame()  # Empty DataFrame for unknown types