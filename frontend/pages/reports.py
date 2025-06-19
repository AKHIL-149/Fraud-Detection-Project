"""
Reports and analytics page for Streamlit dashboard
Provides comprehensive reporting and data visualization
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
import io
import base64
from . import COMMON_STYLE, ENDPOINTS, PAGE_CONFIG

class ReportsPage:
    def __init__(self):
        self.setup_page()
        
    def setup_page(self):
        """Configure the Streamlit page"""
        st.set_page_config(**PAGE_CONFIG)
        st.markdown(COMMON_STYLE, unsafe_allow_html=True)
        
    def render(self):
        """Render the reports page"""
        st.markdown("""
        <div class="main-header">
            <h1>📊 Reports & Analytics</h1>
            <p>Comprehensive fraud detection analytics and reporting</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Create main layout
        self.create_report_controls()
        self.create_executive_summary()
        self.create_detailed_analytics()
        self.create_custom_reports()
        
    def create_report_controls(self):
        """Create report control panel"""
        st.subheader("🎛️ Report Configuration")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            report_type = st.selectbox(
                "Report Type",
                ["Executive Summary", "Detailed Analytics", "Fraud Analysis", "Performance Report", "Custom Report"]
            )
            
        with col2:
            date_range = st.selectbox(
                "Date Range",
                ["Last 24 Hours", "Last 7 Days", "Last 30 Days", "Last 90 Days", "Custom Range"]
            )
            
        with col3:
            if date_range == "Custom Range":
                start_date = st.date_input("Start Date", datetime.now() - timedelta(days=30))
                end_date = st.date_input("End Date", datetime.now())
            else:
                start_date, end_date = self.get_date_range(date_range)
                
        with col4:
            export_format = st.selectbox(
                "Export Format",
                ["PDF", "Excel", "CSV", "JSON"]
            )
            
        with col5:
            st.write("")  # Spacing
            if st.button("📥 Generate Report", type="primary"):
                self.generate_report(report_type, start_date, end_date, export_format)
                
        # Store report parameters
        st.session_state.report_params = {
            'type': report_type,
            'start_date': start_date,
            'end_date': end_date,
            'format': export_format
        }
        
    def create_executive_summary(self):
        """Create executive summary dashboard"""
        st.subheader("📋 Executive Summary")
        
        # Key metrics
        summary_data = self.fetch_executive_summary()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Transactions",
                f"{summary_data.get('total_transactions', 0):,}",
                delta=f"{summary_data.get('txn_change', 0):+,}"
            )
            
        with col2:
            fraud_detected = summary_data.get('fraud_detected', 0)
            st.metric(
                "Fraud Cases Detected",
                f"{fraud_detected:,}",
                delta=f"{summary_data.get('fraud_change', 0):+,}"
            )
            
        with col3:
            amount_saved = summary_data.get('amount_saved', 0)
            st.metric(
                "Amount Saved",
                f"${amount_saved:,.0f}",
                delta=f"${summary_data.get('amount_change', 0):+,.0f}"
            )
            
        with col4:
            fraud_rate = summary_data.get('fraud_rate', 0) * 100
            st.metric(
                "Fraud Rate",
                f"{fraud_rate:.2f}%",
                delta=f"{summary_data.get('rate_change', 0)*100:+.2f}%"
            )
            
        # Executive charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Fraud trend over time
            fraud_trend = self.fetch_fraud_trend()
            
            fig_trend = go.Figure()
            
            fig_trend.add_trace(go.Scatter(
                x=fraud_trend['date'],
                y=fraud_trend['fraud_amount'],
                mode='lines+markers',
                name='Fraud Amount',
                line=dict(color='#dc3545', width=3),
                yaxis='y'
            ))
            
            fig_trend.add_trace(go.Scatter(
                x=fraud_trend['date'],
                y=fraud_trend['fraud_rate'] * 100,
                mode='lines+markers',
                name='Fraud Rate (%)',
                line=dict(color='#ffc107', width=2),
                yaxis='y2'
            ))
            
            fig_trend.update_layout(
                title="Fraud Trend Analysis",
                xaxis_title="Date",
                yaxis=dict(title="Fraud Amount ($)", side="left"),
                yaxis2=dict(title="Fraud Rate (%)", side="right", overlaying="y"),
                height=400
            )
            
            st.plotly_chart(fig_trend, use_container_width=True)
            
        with col2:
            # Model performance summary
            model_perf = self.fetch_model_performance_summary()
            
            categories = ['Precision', 'Recall', 'F1-Score', 'AUC-ROC']
            
            fig_radar = go.Figure()
            
            fig_radar.add_trace(go.Scatterpolar(
                r=model_perf['current'],
                theta=categories,
                fill='toself',
                name='Current Period',
                line_color='#007bff'
            ))
            
            fig_radar.add_trace(go.Scatterpolar(
                r=model_perf['previous'],
                theta=categories,
                fill='toself',
                name='Previous Period',
                line_color='#6c757d'
            ))
            
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 1]
                    )),
                title="Model Performance Comparison",
                height=400
            )
            
            st.plotly_chart(fig_radar, use_container_width=True)
            
    def create_detailed_analytics(self):
        """Create detailed analytics section"""
        st.subheader("📈 Detailed Analytics")
        
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "Transaction Analysis", 
            "Geographic Analysis", 
            "Temporal Patterns", 
            "Risk Analysis",
            "Model Performance"
        ])
        
        with tab1:
            self.create_transaction_analysis()
            
        with tab2:
            self.create_geographic_analysis()
            
        with tab3:
            self.create_temporal_analysis()
            
        with tab4:
            self.create_risk_analysis()
            
        with tab5:
            self.create_model_performance_analysis()
            
    def create_transaction_analysis(self):
        """Create transaction analysis charts"""
        transaction_data = self.fetch_transaction_analysis()
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Transaction volume by category
            category_data = transaction_data.groupby('merchant_category').agg({
                'amount': 'sum',
                'is_fraud': 'sum',
                'transaction_id': 'count'
            }).reset_index()
            
            category_data['fraud_rate'] = category_data['is_fraud'] / category_data['transaction_id']
           
            fig_category = px.bar(
                category_data,
                x='merchant_category',
                y='amount',
                color='fraud_rate',
                title="Transaction Volume by Category",
                color_continuous_scale="Reds",
                hover_data=['transaction_id', 'is_fraud']
            )
            
            fig_category.update_layout(height=400)
            st.plotly_chart(fig_category, use_container_width=True)
            
        with col2:
            # Amount distribution analysis
            fig_amount = make_subplots(
                rows=2, cols=1,
                subplot_titles=("Legitimate Transactions", "Fraudulent Transactions"),
                vertical_spacing=0.15
            )
            
            legitimate_amounts = transaction_data[transaction_data['is_fraud'] == 0]['amount']
            fraud_amounts = transaction_data[transaction_data['is_fraud'] == 1]['amount']
            
            fig_amount.add_trace(
                go.Histogram(x=legitimate_amounts, name="Legitimate", nbinsx=30, marker_color='#28a745'),
                row=1, col=1
            )
            
            fig_amount.add_trace(
                go.Histogram(x=fraud_amounts, name="Fraudulent", nbinsx=30, marker_color='#dc3545'),
                row=2, col=1
            )
            
            fig_amount.update_layout(height=400, showlegend=False)
            fig_amount.update_xaxes(title_text="Transaction Amount ($)")
            fig_amount.update_yaxes(title_text="Frequency")
            
            st.plotly_chart(fig_amount, use_container_width=True)
            
        # Detailed transaction table
        st.subheader("Transaction Details")
        
        # Add filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            category_filter = st.multiselect(
                "Filter by Category",
                transaction_data['merchant_category'].unique(),
                default=transaction_data['merchant_category'].unique()[:3]
            )
            
        with col2:
            amount_range = st.slider(
                "Amount Range ($)",
                float(transaction_data['amount'].min()),
                float(transaction_data['amount'].max()),
                (float(transaction_data['amount'].min()), float(transaction_data['amount'].max()))
            )
            
        with col3:
            fraud_only = st.checkbox("Show Fraud Only", value=False)
            
        # Filter data
        filtered_data = transaction_data[
            (transaction_data['merchant_category'].isin(category_filter)) &
            (transaction_data['amount'] >= amount_range[0]) &
            (transaction_data['amount'] <= amount_range[1])
        ]
        
        if fraud_only:
            filtered_data = filtered_data[filtered_data['is_fraud'] == 1]
            
        # Display filtered table
        st.dataframe(
            filtered_data.head(100),
            use_container_width=True,
            column_config={
                "amount": st.column_config.NumberColumn(
                    "Amount",
                    format="$%.2f"
                ),
                "risk_score": st.column_config.ProgressColumn(
                    "Risk Score",
                    min_value=0,
                    max_value=1
                ),
                "is_fraud": st.column_config.CheckboxColumn("Fraud")
            }
        )
        
    def create_geographic_analysis(self):
        """Create geographic analysis charts"""
        geo_data = self.fetch_geographic_analysis()
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Choropleth map of fraud by state
            fig_map = px.choropleth(
                geo_data,
                locations='state_code',
                color='fraud_rate',
                hover_name='state_name',
                hover_data=['total_transactions', 'fraud_count'],
                color_continuous_scale="Reds",
                scope="usa",
                title="Fraud Rate by State"
            )
            
            fig_map.update_layout(height=400)
            st.plotly_chart(fig_map, use_container_width=True)
            
        with col2:
            # Top cities by fraud amount
            city_data = geo_data.groupby('city').agg({
                'fraud_amount': 'sum',
                'fraud_count': 'sum'
            }).sort_values('fraud_amount', ascending=False).head(10).reset_index()
            
            fig_cities = px.bar(
                city_data,
                x='fraud_amount',
                y='city',
                orientation='h',
                title="Top 10 Cities by Fraud Amount",
                color='fraud_count',
                color_continuous_scale="Reds"
            )
            
            fig_cities.update_layout(height=400)
            st.plotly_chart(fig_cities, use_container_width=True)
            
        # Geographic insights
        st.subheader("Geographic Insights")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            highest_fraud_state = geo_data.loc[geo_data['fraud_rate'].idxmax()]
            st.metric(
                "Highest Fraud Rate State",
                highest_fraud_state['state_name'],
                f"{highest_fraud_state['fraud_rate']:.2%}"
            )
            
        with col2:
            total_fraud_amount = geo_data['fraud_amount'].sum()
            st.metric(
                "Total Geographic Fraud",
                f"${total_fraud_amount:,.0f}"
            )
            
        with col3:
            avg_fraud_rate = geo_data['fraud_rate'].mean()
            st.metric(
                "Average Fraud Rate",
                f"{avg_fraud_rate:.2%}"
            )
            
    def create_temporal_analysis(self):
        """Create temporal pattern analysis"""
        temporal_data = self.fetch_temporal_analysis()
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Hourly fraud patterns
            hourly_data = temporal_data.groupby('hour').agg({
                'fraud_count': 'sum',
                'total_count': 'sum'
            }).reset_index()
            hourly_data['fraud_rate'] = hourly_data['fraud_count'] / hourly_data['total_count']
            
            fig_hourly = make_subplots(specs=[[{"secondary_y": True}]])
            
            fig_hourly.add_trace(
                go.Bar(x=hourly_data['hour'], y=hourly_data['fraud_count'], name="Fraud Count"),
                secondary_y=False,
            )
            
            fig_hourly.add_trace(
                go.Scatter(x=hourly_data['hour'], y=hourly_data['fraud_rate'], 
                            mode='lines+markers', name="Fraud Rate", line=dict(color='red')),
                secondary_y=True,
            )
            
            fig_hourly.update_xaxes(title_text="Hour of Day")
            fig_hourly.update_yaxes(title_text="Fraud Count", secondary_y=False)
            fig_hourly.update_yaxes(title_text="Fraud Rate", secondary_y=True)
            fig_hourly.update_layout(title="Hourly Fraud Patterns", height=400)
            
            st.plotly_chart(fig_hourly, use_container_width=True)
            
        with col2:
            # Day of week patterns
            dow_data = temporal_data.groupby('day_of_week').agg({
                'fraud_count': 'sum',
                'fraud_amount': 'sum'
            }).reset_index()
            
            fig_dow = px.bar(
                dow_data,
                x='day_of_week',
                y='fraud_amount',
                title="Fraud Amount by Day of Week",
                color='fraud_count',
                color_continuous_scale="Reds"
            )
            
            fig_dow.update_layout(height=400)
            st.plotly_chart(fig_dow, use_container_width=True)
            
        # Seasonal analysis
        st.subheader("Seasonal Trends")
        
        seasonal_data = temporal_data.groupby('month').agg({
            'fraud_count': 'sum',
            'fraud_amount': 'sum',
            'total_count': 'sum'
        }).reset_index()
        seasonal_data['fraud_rate'] = seasonal_data['fraud_count'] / seasonal_data['total_count']
        
        fig_seasonal = px.line(
            seasonal_data,
            x='month',
            y=['fraud_count', 'fraud_amount', 'fraud_rate'],
            title="Seasonal Fraud Trends",
            facet_col='variable',
            facet_col_wrap=3
        )
        
        fig_seasonal.update_layout(height=300)
        st.plotly_chart(fig_seasonal, use_container_width=True)
        
    def create_risk_analysis(self):
        """Create risk analysis visualizations"""
        risk_data = self.fetch_risk_analysis()
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Risk score distribution
            fig_risk_dist = px.histogram(
                risk_data,
                x='risk_score',
                color='is_fraud',
                nbins=20,
                title="Risk Score Distribution",
                color_discrete_map={0: '#28a745', 1: '#dc3545'},
                marginal="box"
            )
            
            fig_risk_dist.update_layout(height=400)
            st.plotly_chart(fig_risk_dist, use_container_width=True)
            
        with col2:
            # ROC Curve
            roc_data = self.calculate_roc_curve(risk_data)
            
            fig_roc = px.line(
                roc_data,
                x='fpr',
                y='tpr',
                title=f"ROC Curve (AUC = {roc_data['auc'].iloc[0]:.3f})",
                labels={'fpr': 'False Positive Rate', 'tpr': 'True Positive Rate'}
            )
            
            # Add diagonal line
            fig_roc.add_trace(
                go.Scatter(x=[0, 1], y=[0, 1], mode='lines', name='Random', 
                            line=dict(dash='dash', color='gray'))
            )
            
            fig_roc.update_layout(height=400)
            st.plotly_chart(fig_roc, use_container_width=True)
            
        # Feature importance analysis
        st.subheader("Feature Importance Analysis")
        
        feature_importance = self.fetch_feature_importance()
        
        fig_importance = px.bar(
            feature_importance.sort_values('importance', ascending=True),
            x='importance',
            y='feature',
            orientation='h',
            title="Feature Importance for Fraud Detection",
            color='importance',
            color_continuous_scale="Blues"
        )
        
        fig_importance.update_layout(height=500)
        st.plotly_chart(fig_importance, use_container_width=True)
        
        # Risk threshold analysis
        st.subheader("Risk Threshold Analysis")
        
        threshold_data = self.analyze_risk_thresholds(risk_data)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_threshold = px.line(
                threshold_data,
                x='threshold',
                y=['precision', 'recall', 'f1_score'],
                title="Performance Metrics vs Risk Threshold"
            )
            
            fig_threshold.update_layout(height=350)
            st.plotly_chart(fig_threshold, use_container_width=True)
            
        with col2:
            # Optimal threshold
            optimal_threshold = threshold_data.loc[threshold_data['f1_score'].idxmax()]
            
            st.metric(
                "Optimal Threshold",
                f"{optimal_threshold['threshold']:.3f}",
                help="Threshold that maximizes F1-score"
            )
            
            st.metric(
                "Precision at Optimal",
                f"{optimal_threshold['precision']:.3f}"
            )
            
            st.metric(
                "Recall at Optimal",
                f"{optimal_threshold['recall']:.3f}"
            )
            
    def create_model_performance_analysis(self):
        """Create model performance analysis"""
        model_data = self.fetch_model_performance_data()
        
        # Performance over time
        col1, col2 = st.columns(2)
        
        with col1:
            fig_perf_time = px.line(
                model_data,
                x='date',
                y=['accuracy', 'precision', 'recall', 'f1_score'],
                title="Model Performance Over Time"
            )
            
            fig_perf_time.update_layout(height=400)
            st.plotly_chart(fig_perf_time, use_container_width=True)
            
        with col2:
            # Confusion matrix
            confusion_data = model_data.iloc[-1]  # Latest data
            
            confusion_matrix = np.array([
                [confusion_data['true_negative'], confusion_data['false_positive']],
                [confusion_data['false_negative'], confusion_data['true_positive']]
            ])
            
            fig_confusion = px.imshow(
                confusion_matrix,
                text_auto=True,
                aspect="auto",
                title="Confusion Matrix (Latest)",
                x=['Predicted Negative', 'Predicted Positive'],
                y=['Actual Negative', 'Actual Positive']
            )
            
            fig_confusion.update_layout(height=400)
            st.plotly_chart(fig_confusion, use_container_width=True)
            
        # Model comparison
        st.subheader("Model Comparison")
        
        model_comparison = self.fetch_model_comparison()
        
        fig_comparison = px.bar(
            model_comparison,
            x='model_name',
            y=['accuracy', 'precision', 'recall', 'f1_score'],
            title="Model Performance Comparison",
            barmode='group'
        )
        
        fig_comparison.update_layout(height=400)
        st.plotly_chart(fig_comparison, use_container_width=True)
        
    def create_custom_reports(self):
        """Create custom reporting interface"""
        st.subheader("🛠️ Custom Report Builder")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("### Report Configuration")
            
            # Metric selection
            available_metrics = [
                'Transaction Volume', 'Fraud Rate', 'Amount at Risk',
                'Model Accuracy', 'Alert Count', 'Resolution Time',
                'False Positive Rate', 'Geographic Distribution'
            ]
            
            selected_metrics = st.multiselect(
                "Select Metrics",
                available_metrics,
                default=['Fraud Rate', 'Transaction Volume']
            )
            
            # Visualization type
            viz_types = {
                'Line Chart': 'line',
                'Bar Chart': 'bar',
                'Area Chart': 'area',
                'Scatter Plot': 'scatter',
                'Heatmap': 'heatmap',
                'Pie Chart': 'pie'
            }
            
            selected_viz = st.selectbox(
                "Visualization Type",
                list(viz_types.keys())
            )
            
            # Grouping options
            group_by = st.selectbox(
                "Group By",
                ['Hour', 'Day', 'Week', 'Month', 'Category', 'Location', 'Risk Level']
            )
            
            # Filters
            st.markdown("### Filters")
            
            risk_filter = st.slider("Risk Score Range", 0.0, 1.0, (0.0, 1.0))
            amount_filter = st.number_input("Minimum Amount", value=0.0)
            
            if st.button("Generate Custom Report"):
                self.generate_custom_report(selected_metrics, selected_viz, group_by, risk_filter, amount_filter)
                
        with col2:
            # Preview area
            st.markdown("### Report Preview")
            
            if 'custom_report_data' in st.session_state:
                # Display the custom report
                report_data = st.session_state.custom_report_data
                
                if selected_viz in ['Line Chart', 'Bar Chart', 'Area Chart']:
                    fig = getattr(px, viz_types[selected_viz])(
                        report_data,
                        x='x',
                        y='y',
                        title=f"Custom Report: {', '.join(selected_metrics)}"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                elif selected_viz == 'Pie Chart':
                    fig = px.pie(
                        report_data,
                        values='y',
                        names='x',
                        title=f"Custom Report: {', '.join(selected_metrics)}"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                # Show data table
                st.dataframe(report_data, use_container_width=True)
                
            else:
                st.info("Configure your report settings and click 'Generate Custom Report' to see the preview.")
                
    # Data fetching methods
    def get_date_range(self, range_str):
        """Convert date range string to start and end dates"""
        now = datetime.now()
        
        if range_str == "Last 24 Hours":
            return now - timedelta(days=1), now
        elif range_str == "Last 7 Days":
            return now - timedelta(days=7), now
        elif range_str == "Last 30 Days":
            return now - timedelta(days=30), now
        elif range_str == "Last 90 Days":
            return now - timedelta(days=90), now
        else:
            return now - timedelta(days=30), now
            
    def fetch_executive_summary(self):
        """Fetch executive summary data"""
        # Mock data
        return {
            'total_transactions': np.random.randint(50000, 100000),
            'fraud_detected': np.random.randint(500, 2000),
            'amount_saved': np.random.uniform(500000, 2000000),
            'fraud_rate': np.random.uniform(0.01, 0.05),
            'txn_change': np.random.randint(-5000, 10000),
            'fraud_change': np.random.randint(-100, 200),
            'amount_change': np.random.uniform(-100000, 300000),
            'rate_change': np.random.uniform(-0.01, 0.02)
        }
        
    def fetch_fraud_trend(self):
        """Fetch fraud trend data"""
        dates = pd.date_range(
            start=datetime.now() - timedelta(days=30),
            end=datetime.now(),
            freq='D'
        )
        
        return pd.DataFrame({
            'date': dates,
            'fraud_amount': np.random.uniform(10000, 50000, len(dates)),
            'fraud_rate': np.random.uniform(0.01, 0.05, len(dates))
        })
        
    def fetch_model_performance_summary(self):
        """Fetch model performance summary"""
        return {
            'current': [0.92, 0.89, 0.91, 0.95],
            'previous': [0.90, 0.87, 0.88, 0.93]
        }
        
    def fetch_transaction_analysis(self):
        """Fetch transaction analysis data"""
        # Mock transaction data
        categories = ['grocery', 'gas', 'restaurant', 'online', 'retail', 'entertainment']
        
        data = []
        for _ in range(5000):
            is_fraud = np.random.choice([0, 1], p=[0.95, 0.05])
            amount = np.random.lognormal(4, 1) if not is_fraud else np.random.lognormal(5, 1.5)
            
            data.append({
                'transaction_id': f'TXN_{np.random.randint(100000, 999999)}',
                'amount': amount,
                'merchant_category': np.random.choice(categories),
                'is_fraud': is_fraud,
                'risk_score': np.random.beta(2, 8) if not is_fraud else np.random.beta(8, 2),
                'user_id': f'USER_{np.random.randint(1000, 9999)}',
                'timestamp': datetime.now() - timedelta(days=np.random.randint(0, 30))
            })
            
        return pd.DataFrame(data)
        
    def fetch_geographic_analysis(self):
        """Fetch geographic analysis data"""
        states = [
            {'state_code': 'CA', 'state_name': 'California', 'city': 'Los Angeles'},
            {'state_code': 'NY', 'state_name': 'New York', 'city': 'New York City'},
            {'state_code': 'TX', 'state_name': 'Texas', 'city': 'Houston'},
            {'state_code': 'FL', 'state_name': 'Florida', 'city': 'Miami'},
            {'state_code': 'IL', 'state_name': 'Illinois', 'city': 'Chicago'},
        ]
        
        data = []
        for state in states:
            for _ in range(100):
                data.append({
                    **state,
                    'total_transactions': np.random.randint(1000, 5000),
                    'fraud_count': np.random.randint(10, 100),
                    'fraud_amount': np.random.uniform(5000, 50000),
                    'fraud_rate': np.random.uniform(0.01, 0.08)
                })
                
        return pd.DataFrame(data)
        
    def fetch_temporal_analysis(self):
        """Fetch temporal analysis data"""
        data = []
        
        for month in range(1, 13):
            for day in range(7):
                for hour in range(24):
                    data.append({
                        'month': month,
                        'day_of_week': day,
                        'hour': hour,
                        'fraud_count': np.random.poisson(5),
                        'total_count': np.random.poisson(100),
                        'fraud_amount': np.random.uniform(1000, 10000)
                    })
                    
        return pd.DataFrame(data)
        
    def fetch_risk_analysis(self):
        """Fetch risk analysis data"""
        n_samples = 10000
        
        # Generate legitimate transactions
        legitimate = pd.DataFrame({
            'risk_score': np.random.beta(2, 8, int(n_samples * 0.95)),
            'is_fraud': 0
        })
        
        # Generate fraudulent transactions
        fraudulent = pd.DataFrame({
            'risk_score': np.random.beta(8, 2, int(n_samples * 0.05)),
            'is_fraud': 1
        })
        
        return pd.concat([legitimate, fraudulent], ignore_index=True)
        
    def calculate_roc_curve(self, data):
        """Calculate ROC curve data"""
        # Simplified ROC calculation
        thresholds = np.linspace(0, 1, 100)
        tpr_values = []
        fpr_values = []
        
        for threshold in thresholds:
            predictions = (data['risk_score'] >= threshold).astype(int)
            
            tp = ((predictions == 1) & (data['is_fraud'] == 1)).sum()
            fp = ((predictions == 1) & (data['is_fraud'] == 0)).sum()
            tn = ((predictions == 0) & (data['is_fraud'] == 0)).sum()
            fn = ((predictions == 0) & (data['is_fraud'] == 1)).sum()
            
            tpr = tp / (tp + fn) if (tp + fn) > 0 else 0
            fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
            
            tpr_values.append(tpr)
            fpr_values.append(fpr)
            
        # Calculate AUC using trapezoidal rule
        auc = np.trapz(tpr_values, fpr_values)
        
        return pd.DataFrame({
            'fpr': fpr_values,
            'tpr': tpr_values,
            'auc': auc
        })
        
    def fetch_feature_importance(self):
        """Fetch feature importance data"""
        features = [
            'transaction_amount', 'merchant_risk_score', 'velocity_1h',
            'geographic_risk', 'device_risk', 'time_of_day',
            'day_of_week', 'user_history', 'amount_deviation'
        ]
        
        importance_values = np.random.uniform(0.05, 0.25, len(features))
        importance_values = importance_values / importance_values.sum()  # Normalize
        
        return pd.DataFrame({
            'feature': features,
            'importance': importance_values
        })
        
    def analyze_risk_thresholds(self, data):
        """Analyze performance at different risk thresholds"""
        thresholds = np.linspace(0.1, 0.9, 50)
        results = []
        
        for threshold in thresholds:
            predictions = (data['risk_score'] >= threshold).astype(int)
            
            tp = ((predictions == 1) & (data['is_fraud'] == 1)).sum()
            fp = ((predictions == 1) & (data['is_fraud'] == 0)).sum()
            tn = ((predictions == 0) & (data['is_fraud'] == 0)).sum()
            fn = ((predictions == 0) & (data['is_fraud'] == 1)).sum()
            
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0
            f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
            
            results.append({
                'threshold': threshold,
                'precision': precision,
                'recall': recall,
                'f1_score': f1_score
            })
            
        return pd.DataFrame(results)
        
    def fetch_model_performance_data(self):
        """Fetch model performance data over time"""
        dates = pd.date_range(
            start=datetime.now() - timedelta(days=30),
            end=datetime.now(),
            freq='D'
        )
        
        data = []
        for date in dates:
            data.append({
                'date': date,
                'accuracy': np.random.uniform(0.90, 0.95),
                'precision': np.random.uniform(0.85, 0.92),
                'recall': np.random.uniform(0.88, 0.94),
                'f1_score': np.random.uniform(0.86, 0.93),
                'true_positive': np.random.randint(80, 120),
                'false_positive': np.random.randint(10, 30),
                'true_negative': np.random.randint(8000, 9000),
                'false_negative': np.random.randint(5, 20)
            })
            
        return pd.DataFrame(data)
        
    def fetch_model_comparison(self):
        """Fetch model comparison data"""
        models = ['Random Forest', 'XGBoost', 'Neural Network', 'Logistic Regression', 'SVM']
        
        data = []
        for model in models:
            data.append({
                'model_name': model,
                'accuracy': np.random.uniform(0.85, 0.95),
                'precision': np.random.uniform(0.80, 0.92),
                'recall': np.random.uniform(0.82, 0.94),
                'f1_score': np.random.uniform(0.81, 0.93)
            })
            
        return pd.DataFrame(data)
        
    # Action methods
    def generate_report(self, report_type, start_date, end_date, export_format):
        """Generate and download report"""
        st.success(f"Generating {report_type} report from {start_date} to {end_date} in {export_format} format...")
        
        # Simulate report generation
        time.sleep(2)
        
        # Create download link
        report_data = self.create_report_data(report_type, start_date, end_date)
        
        if export_format == "CSV":
            csv = report_data.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV Report",
                data=csv,
                file_name=f"fraud_report_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        elif export_format == "JSON":
            json_data = report_data.to_json(orient='records', indent=2)
            st.download_button(
                label="📥 Download JSON Report",
                data=json_data,
                file_name=f"fraud_report_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )
            
    def create_report_data(self, report_type, start_date, end_date):
        """Create report data based on type"""
        # Mock report data
        return pd.DataFrame({
            'date': pd.date_range(start_date, end_date, freq='D'),
            'transactions': np.random.randint(1000, 5000, (end_date - start_date).days + 1),
            'fraud_count': np.random.randint(10, 100, (end_date - start_date).days + 1),
            'fraud_amount': np.random.uniform(5000, 50000, (end_date - start_date).days + 1)
        })
        
    def generate_custom_report(self, metrics, viz_type, group_by, risk_filter, amount_filter):
        """Generate custom report"""
        # Mock custom report data
        if group_by == 'Hour':
            x_values = list(range(24))
        elif group_by == 'Day':
            x_values = list(range(1, 32))
        elif group_by == 'Month':
            x_values = list(range(1, 13))
        else:
            x_values = ['Category A', 'Category B', 'Category C', 'Category D']
            
        y_values = np.random.uniform(10, 100, len(x_values))
        
        custom_data = pd.DataFrame({
            'x': x_values,
            'y': y_values
        })
        
        st.session_state.custom_report_data = custom_data
        st.success("Custom report generated successfully!")

# Main execution
def main():
   reports_page = ReportsPage()
   reports_page.render()

if __name__ == "__main__":
   main()