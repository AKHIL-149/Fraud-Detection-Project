"""
Table components for Streamlit fraud detection dashboard
Provides reusable table components with filtering, sorting, and pagination
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
from . import COMPONENT_CONFIG, COMPONENT_STYLE, format_currency, format_percentage, get_risk_level_color, get_severity_color

class TableComponents:
    """Collection of reusable table components for fraud detection dashboards"""
    
    def __init__(self):
        st.markdown(COMPONENT_STYLE, unsafe_allow_html=True)
        
    @staticmethod
    def transaction_table(data, show_filters=True, page_size=10, key_prefix="txn"):
        """
        Create an interactive transaction table
        
        Args:
            data: DataFrame with transaction data
            show_filters: Whether to show filter controls
            page_size: Number of rows per page
            key_prefix: Unique prefix for widget keys
        """
        if data.empty:
            st.warning("No transaction data available")
            return None
            
        # Filters
        if show_filters:
            st.subheader("🔍 Filter Transactions")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                category_filter = st.multiselect(
                    "Merchant Category",
                    options=data['merchant_category'].unique() if 'merchant_category' in data.columns else [],
                    default=data['merchant_category'].unique() if 'merchant_category' in data.columns else [],
                    key=f"{key_prefix}_category"
                )
                
            with col2:
                if 'amount' in data.columns:
                    amount_range = st.slider(
                        "Amount Range",
                        min_value=float(data['amount'].min()),
                        max_value=float(data['amount'].max()),
                        value=(float(data['amount'].min()), float(data['amount'].max())),
                        key=f"{key_prefix}_amount"
                    )
                else:
                    amount_range = (0, float('inf'))
                    
            with col3:
                if 'risk_score' in data.columns:
                    risk_filter = st.selectbox(
                        "Risk Level",
                        options=['All', 'High (>0.7)', 'Medium (0.3-0.7)', 'Low (<0.3)'],
                        key=f"{key_prefix}_risk"
                    )
                else:
                    risk_filter = 'All'
                    
            with col4:
                if 'is_fraud' in data.columns:
                    fraud_filter = st.selectbox(
                        "Transaction Type",
                        options=['All', 'Legitimate', 'Fraudulent'],
                        key=f"{key_prefix}_fraud"
                    )
                else:
                    fraud_filter = 'All'
                    
            # Apply filters
            filtered_data = data.copy()
            
            if 'merchant_category' in data.columns and category_filter:
                filtered_data = filtered_data[filtered_data['merchant_category'].isin(category_filter)]
                
            if 'amount' in data.columns:
                filtered_data = filtered_data[
                    (filtered_data['amount'] >= amount_range[0]) & 
                    (filtered_data['amount'] <= amount_range[1])
                ]
                
            if 'risk_score' in data.columns and risk_filter != 'All':
                if risk_filter == 'High (>0.7)':
                    filtered_data = filtered_data[filtered_data['risk_score'] > 0.7]
                elif risk_filter == 'Medium (0.3-0.7)':
                    filtered_data = filtered_data[
                        (filtered_data['risk_score'] >= 0.3) & (filtered_data['risk_score'] <= 0.7)
                    ]
                elif risk_filter == 'Low (<0.3)':
                    filtered_data = filtered_data[filtered_data['risk_score'] < 0.3]
                    
            if 'is_fraud' in data.columns and fraud_filter != 'All':
                if fraud_filter == 'Legitimate':
                    filtered_data = filtered_data[filtered_data['is_fraud'] == 0]
                elif fraud_filter == 'Fraudulent':
                    filtered_data = filtered_data[filtered_data['is_fraud'] == 1]
                    
        else:
            filtered_data = data
            
        # Display summary
        st.write(f"Showing {len(filtered_data):,} of {len(data):,} transactions")
        
        # Pagination
        total_pages = max(1, (len(filtered_data) - 1) // page_size + 1)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            page = st.number_input(
                "Page",
                min_value=1,
                max_value=total_pages,
                value=1,
                key=f"{key_prefix}_page"
            )
            
        with col2:
            st.write(f"Page {page} of {total_pages}")
            
        with col3:
            page_size = st.selectbox(
                "Rows per page",
                options=[5, 10, 25, 50, 100],
                index=1,
                key=f"{key_prefix}_page_size"
            )
            
        # Get page data
        start_idx = (page - 1) * page_size
        end_idx = min(start_idx + page_size, len(filtered_data))
        page_data = filtered_data.iloc[start_idx:end_idx].copy()
        
        # Format the data for display
        display_data = TableComponents._format_transaction_data(page_data)
        
        # Display table
        st.dataframe(
            display_data,
            use_container_width=True,
            column_config=TableComponents._get_transaction_column_config(),
            hide_index=True
        )
        
        # Action buttons
        if len(filtered_data) > 0:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📥 Export to CSV", key=f"{key_prefix}_export"):
                    csv = filtered_data.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name=f"transactions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        key=f"{key_prefix}_download"
                    )
                    
            with col2:
               if st.button("🔄 Refresh Data", key=f"{key_prefix}_refresh"):
                   st.rerun()
                   
            with col3:
               selected_count = len(filtered_data[filtered_data.get('selected', False) == True]) if 'selected' in filtered_data.columns else 0
               if selected_count > 0:
                   if st.button(f"⚡ Bulk Actions ({selected_count})", key=f"{key_prefix}_bulk"):
                       st.info("Bulk actions would be performed here")
       
        return filtered_data
       
    @staticmethod
    def alert_table(data, show_filters=True, page_size=10, key_prefix="alert"):
        """
        Create an interactive alert table
        
        Args:
            data: DataFrame with alert data
            show_filters: Whether to show filter controls
            page_size: Number of rows per page
            key_prefix: Unique prefix for widget keys
        """
        if data.empty:
            st.warning("No alert data available")
            return None
            
        # Filters
        if show_filters:
            st.subheader("🚨 Filter Alerts")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                severity_filter = st.multiselect(
                    "Severity",
                    options=['critical', 'high', 'medium', 'low'],
                    default=['critical', 'high', 'medium', 'low'],
                    key=f"{key_prefix}_severity"
                )
                
            with col2:
                status_filter = st.multiselect(
                    "Status",
                    options=['new', 'investigating', 'resolved', 'false_positive'],
                    default=['new', 'investigating'],
                    key=f"{key_prefix}_status"
                )
                
            with col3:
                date_filter = st.selectbox(
                    "Time Range",
                    options=['All Time', 'Last Hour', 'Last 6 Hours', 'Last 24 Hours', 'Last 7 Days'],
                    index=3,
                    key=f"{key_prefix}_date"
                )
                
            with col4:
                search_term = st.text_input(
                    "Search",
                    placeholder="Transaction ID, User ID...",
                    key=f"{key_prefix}_search"
                )
                
            # Apply filters
            filtered_data = data.copy()
            
            if severity_filter:
                filtered_data = filtered_data[filtered_data['severity'].isin(severity_filter)]
                
            if status_filter:
                filtered_data = filtered_data[filtered_data['status'].isin(status_filter)]
                
            if date_filter != 'All Time' and 'timestamp' in data.columns:
                now = datetime.now()
                if date_filter == 'Last Hour':
                    cutoff = now - timedelta(hours=1)
                elif date_filter == 'Last 6 Hours':
                    cutoff = now - timedelta(hours=6)
                elif date_filter == 'Last 24 Hours':
                    cutoff = now - timedelta(hours=24)
                elif date_filter == 'Last 7 Days':
                    cutoff = now - timedelta(days=7)
                    
                filtered_data = filtered_data[pd.to_datetime(filtered_data['timestamp']) >= cutoff]
                
            if search_term:
                # Search across multiple columns
                search_columns = ['transaction_id', 'user_id', 'description']
                mask = False
                for col in search_columns:
                    if col in filtered_data.columns:
                        mask |= filtered_data[col].astype(str).str.contains(search_term, case=False, na=False)
                filtered_data = filtered_data[mask]
                
        else:
            filtered_data = data
            
        # Display summary
        st.write(f"Showing {len(filtered_data):,} of {len(data):,} alerts")
        
        # Severity summary
        if not filtered_data.empty:
            severity_counts = filtered_data['severity'].value_counts()
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Critical", severity_counts.get('critical', 0))
            with col2:
                st.metric("High", severity_counts.get('high', 0))
            with col3:
                st.metric("Medium", severity_counts.get('medium', 0))
            with col4:
                st.metric("Low", severity_counts.get('low', 0))
                
        # Pagination
        total_pages = max(1, (len(filtered_data) - 1) // page_size + 1)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            page = st.number_input(
                "Page",
                min_value=1,
                max_value=total_pages,
                value=1,
                key=f"{key_prefix}_page"
            )
            
        with col2:
            st.write(f"Page {page} of {total_pages}")
            
        with col3:
            page_size = st.selectbox(
                "Rows per page",
                options=[5, 10, 25, 50],
                index=1,
                key=f"{key_prefix}_page_size"
            )
            
        # Get page data
        start_idx = (page - 1) * page_size
        end_idx = min(start_idx + page_size, len(filtered_data))
        page_data = filtered_data.iloc[start_idx:end_idx].copy()
        
        # Format the data for display
        display_data = TableComponents._format_alert_data(page_data)
        
        # Display table
        st.dataframe(
            display_data,
            use_container_width=True,
            column_config=TableComponents._get_alert_column_config(),
            hide_index=True
        )
        
        # Alert actions
        if len(page_data) > 0:
            st.subheader("🔧 Alert Actions")
            
            # Select alert for actions
            selected_alert = st.selectbox(
                "Select Alert for Action",
                options=page_data['id'].tolist(),
                format_func=lambda x: f"Alert {x}",
                key=f"{key_prefix}_select"
            )
            
            if selected_alert:
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    if st.button("🔍 Investigate", key=f"{key_prefix}_investigate"):
                        st.success(f"Investigation started for alert {selected_alert}")
                        
                with col2:
                    if st.button("✅ Resolve", key=f"{key_prefix}_resolve"):
                        st.success(f"Alert {selected_alert} resolved")
                        
                with col3:
                    if st.button("❌ False Positive", key=f"{key_prefix}_false_positive"):
                        st.warning(f"Alert {selected_alert} marked as false positive")
                        
                with col4:
                    if st.button("📤 Escalate", key=f"{key_prefix}_escalate"):
                        st.info(f"Alert {selected_alert} escalated")
        
        return filtered_data
        
    @staticmethod
    def user_risk_table(data, show_filters=True, page_size=10, key_prefix="user"):
        """
        Create a user risk profile table
        
        Args:
            data: DataFrame with user risk data
            show_filters: Whether to show filter controls
            page_size: Number of rows per page
            key_prefix: Unique prefix for widget keys
        """
        if data.empty:
            st.warning("No user data available")
            return None
            
        # Filters
        if show_filters:
            st.subheader("👥 Filter Users")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                risk_level_filter = st.selectbox(
                    "Risk Level",
                    options=['All', 'High Risk', 'Medium Risk', 'Low Risk'],
                    key=f"{key_prefix}_risk_level"
                )
                
            with col2:
                status_filter = st.multiselect(
                    "Status",
                    options=['active', 'flagged', 'suspended', 'under_review'],
                    default=['active', 'flagged', 'under_review'],
                    key=f"{key_prefix}_status"
                )
                
            with col3:
                min_transactions = st.number_input(
                    "Min Transactions",
                    min_value=0,
                    value=0,
                    key=f"{key_prefix}_min_txn"
                )
                
            # Apply filters
            filtered_data = data.copy()
            
            if risk_level_filter != 'All' and 'risk_score' in data.columns:
                if risk_level_filter == 'High Risk':
                    filtered_data = filtered_data[filtered_data['risk_score'] > 0.7]
                elif risk_level_filter == 'Medium Risk':
                    filtered_data = filtered_data[
                        (filtered_data['risk_score'] >= 0.3) & (filtered_data['risk_score'] <= 0.7)
                    ]
                elif risk_level_filter == 'Low Risk':
                    filtered_data = filtered_data[filtered_data['risk_score'] < 0.3]
                    
            if status_filter and 'status' in data.columns:
                filtered_data = filtered_data[filtered_data['status'].isin(status_filter)]
                
            if 'total_transactions' in data.columns:
                filtered_data = filtered_data[filtered_data['total_transactions'] >= min_transactions]
                
        else:
            filtered_data = data
            
        # Display summary
        st.write(f"Showing {len(filtered_data):,} of {len(data):,} users")
        
        # Risk level summary
        if not filtered_data.empty and 'risk_score' in filtered_data.columns:
            high_risk = len(filtered_data[filtered_data['risk_score'] > 0.7])
            medium_risk = len(filtered_data[
                (filtered_data['risk_score'] >= 0.3) & (filtered_data['risk_score'] <= 0.7)
            ])
            low_risk = len(filtered_data[filtered_data['risk_score'] < 0.3])
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("High Risk Users", high_risk)
            with col2:
                st.metric("Medium Risk Users", medium_risk)
            with col3:
                st.metric("Low Risk Users", low_risk)
                
        # Pagination and display
        display_data = TableComponents._paginate_and_display(
            filtered_data, page_size, key_prefix, 
            TableComponents._format_user_data,
            TableComponents._get_user_column_config
        )
        
        return filtered_data
        
    @staticmethod
    def merchant_risk_table(data, show_filters=True, page_size=10, key_prefix="merchant"):
        """
        Create a merchant risk analysis table
        
        Args:
            data: DataFrame with merchant data
            show_filters: Whether to show filter controls
            page_size: Number of rows per page
            key_prefix: Unique prefix for widget keys
        """
        if data.empty:
            st.warning("No merchant data available")
            return None
            
        # Filters
        if show_filters:
            st.subheader("🏪 Filter Merchants")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                category_filter = st.multiselect(
                    "Category",
                    options=data['category'].unique() if 'category' in data.columns else [],
                    default=data['category'].unique() if 'category' in data.columns else [],
                    key=f"{key_prefix}_category"
                )
                
            with col2:
                risk_threshold = st.slider(
                    "Max Risk Score",
                    min_value=0.0,
                    max_value=1.0,
                    value=1.0,
                    step=0.1,
                    key=f"{key_prefix}_risk_threshold"
                )
                
            with col3:
                min_volume = st.number_input(
                    "Min Transaction Volume",
                    min_value=0,
                    value=0,
                    key=f"{key_prefix}_min_volume"
                )
                
            # Apply filters
            filtered_data = data.copy()
            
            if category_filter and 'category' in data.columns:
                filtered_data = filtered_data[filtered_data['category'].isin(category_filter)]
                
            if 'risk_score' in data.columns:
                filtered_data = filtered_data[filtered_data['risk_score'] <= risk_threshold]
                
            if 'transaction_volume' in data.columns:
                filtered_data = filtered_data[filtered_data['transaction_volume'] >= min_volume]
                
        else:
            filtered_data = data
            
        # Display summary
        st.write(f"Showing {len(filtered_data):,} of {len(data):,} merchants")
        
        # Pagination and display
        display_data = TableComponents._paginate_and_display(
            filtered_data, page_size, key_prefix,
            TableComponents._format_merchant_data,
            TableComponents._get_merchant_column_config
        )
        
        return filtered_data
        
    @staticmethod
    def model_performance_table(data, key_prefix="model"):
        """
        Create a model performance comparison table
        
        Args:
            data: DataFrame with model performance data
            key_prefix: Unique prefix for widget keys
        """
        if data.empty:
            st.warning("No model performance data available")
            return None
            
        st.subheader("🤖 Model Performance Comparison")
        
        # Format the data for display
        display_data = data.copy()
        
        # Format percentage columns
        percentage_cols = ['accuracy', 'precision', 'recall', 'f1_score', 'auc_roc']
        for col in percentage_cols:
            if col in display_data.columns:
                display_data[col] = display_data[col].apply(lambda x: f"{x:.1%}")
                
        # Display table
        st.dataframe(
            display_data,
            use_container_width=True,
            column_config={
                'model_name': st.column_config.TextColumn("Model Name"),
                'accuracy': st.column_config.TextColumn("Accuracy"),
                'precision': st.column_config.TextColumn("Precision"),
                'recall': st.column_config.TextColumn("Recall"),
                'f1_score': st.column_config.TextColumn("F1 Score"),
                'auc_roc': st.column_config.TextColumn("AUC-ROC"),
                'training_time': st.column_config.NumberColumn("Training Time (min)", format="%.1f"),
                'last_updated': st.column_config.DatetimeColumn("Last Updated")
            },
            hide_index=True
        )
        
        return display_data
        
    # Helper methods
    @staticmethod
    def _format_transaction_data(data):
        """Format transaction data for display"""
        display_data = data.copy()
        
        # Format amount
        if 'amount' in display_data.columns:
            display_data['amount'] = display_data['amount'].apply(format_currency)
            
        # Format risk score
        if 'risk_score' in display_data.columns:
            display_data['risk_level'] = display_data['risk_score'].apply(
                lambda x: 'High' if x > 0.7 else 'Medium' if x > 0.3 else 'Low'
            )
            
        # Format fraud status
        if 'is_fraud' in display_data.columns:
            display_data['fraud_status'] = display_data['is_fraud'].apply(
                lambda x: '🚨 Fraud' if x == 1 else '✅ Legitimate'
            )
            
        # Format timestamp
        if 'timestamp' in display_data.columns:
            display_data['timestamp'] = pd.to_datetime(display_data['timestamp']).dt.strftime('%Y-%m-%d %H:%M')
            
        return display_data
        
    @staticmethod
    def _format_alert_data(data):
        """Format alert data for display"""
        display_data = data.copy()
        
        # Format severity with icons
        if 'severity' in display_data.columns:
            severity_icons = {
                'critical': '🔴 Critical',
                'high': '🟠 High',
                'medium': '🟡 Medium',
                'low': '🟢 Low'
            }
            display_data['severity_display'] = display_data['severity'].map(severity_icons)
            
        # Format status
        if 'status' in display_data.columns:
            status_icons = {
                'new': '🆕 New',
                'investigating': '🔍 Investigating',
                'resolved': '✅ Resolved',
                'false_positive': '❌ False Positive'
            }
            display_data['status_display'] = display_data['status'].map(status_icons)
            
        # Format risk score
        if 'risk_score' in display_data.columns:
            display_data['risk_score'] = display_data['risk_score'].apply(lambda x: f"{x:.1%}")
            
        # Format timestamp
        if 'timestamp' in display_data.columns:
            display_data['timestamp'] = pd.to_datetime(display_data['timestamp']).dt.strftime('%Y-%m-%d %H:%M')
            
        return display_data
        
    @staticmethod
    def _format_user_data(data):
        """Format user data for display"""
        display_data = data.copy()
        
        # Format risk score
        if 'risk_score' in display_data.columns:
            display_data['risk_level'] = display_data['risk_score'].apply(
                lambda x: '🔴 High' if x > 0.7 else '🟡 Medium' if x > 0.3 else '🟢 Low'
            )
            
        # Format last activity
        if 'last_activity' in display_data.columns:
            display_data['last_activity'] = pd.to_datetime(display_data['last_activity']).dt.strftime('%Y-%m-%d')
            
        return display_data
        
    @staticmethod
    def _format_merchant_data(data):
        """Format merchant data for display"""
        display_data = data.copy()
        
        # Format fraud rate
        if 'fraud_rate' in display_data.columns:
            display_data['fraud_rate'] = display_data['fraud_rate'].apply(lambda x: f"{x:.2%}")
            
        # Format risk score
        if 'risk_score' in display_data.columns:
            display_data['risk_level'] = display_data['risk_score'].apply(
                lambda x: '🔴 High' if x > 0.7 else '🟡 Medium' if x > 0.3 else '🟢 Low'
            )
            
        return display_data
        
    @staticmethod
    def _get_transaction_column_config():
        """Get column configuration for transaction table"""
        return {
            'transaction_id': st.column_config.TextColumn("Transaction ID"),
            'amount': st.column_config.TextColumn("Amount"),
            'user_id': st.column_config.TextColumn("User ID"),
            'merchant_category': st.column_config.TextColumn("Category"),
            'risk_score': st.column_config.ProgressColumn("Risk Score", min_value=0, max_value=1),
            'risk_level': st.column_config.TextColumn("Risk Level"),
            'fraud_status': st.column_config.TextColumn("Status"),
            'timestamp': st.column_config.TextColumn("Timestamp")
        }
        
    @staticmethod
    def _get_alert_column_config():
        """Get column configuration for alert table"""
        return {
            'id': st.column_config.TextColumn("Alert ID"),
            'severity_display': st.column_config.TextColumn("Severity"),
            'transaction_id': st.column_config.TextColumn("Transaction ID"),
            'description': st.column_config.TextColumn("Description"),
            'risk_score': st.column_config.TextColumn("Risk Score"),
            'status_display': st.column_config.TextColumn("Status"),
            'timestamp': st.column_config.TextColumn("Created")
        }
        
    @staticmethod
    def _get_user_column_config():
        """Get column configuration for user table"""
        return {
            'user_id': st.column_config.TextColumn("User ID"),
            'name': st.column_config.TextColumn("Name"),
            'email': st.column_config.TextColumn("Email"),
            'total_transactions': st.column_config.NumberColumn("Total Transactions"),
            'fraud_count': st.column_config.NumberColumn("Fraud Count"),
            'risk_score': st.column_config.ProgressColumn("Risk Score", min_value=0, max_value=1),
            'risk_level': st.column_config.TextColumn("Risk Level"),
            'status': st.column_config.TextColumn("Status"),
            'last_activity': st.column_config.TextColumn("Last Activity")
        }
        
    @staticmethod
    def _get_merchant_column_config():
        """Get column configuration for merchant table"""
        return {
            'merchant_id': st.column_config.TextColumn("Merchant ID"),
            'name': st.column_config.TextColumn("Name"),
            'category': st.column_config.TextColumn("Category"),
            'transaction_volume': st.column_config.NumberColumn("Volume"),
            'fraud_rate': st.column_config.TextColumn("Fraud Rate"),
            'risk_score': st.column_config.ProgressColumn("Risk Score", min_value=0, max_value=1),
            'risk_level': st.column_config.TextColumn("Risk Level"),
            'status': st.column_config.TextColumn("Status")
        }
        
    @staticmethod
    def _paginate_and_display(data, page_size, key_prefix, format_func, column_config_func):
        """Helper method to paginate and display data"""
        # Pagination
        total_pages = max(1, (len(data) - 1) // page_size + 1)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            page = st.number_input(
                "Page",
                min_value=1,
                max_value=total_pages,
                value=1,
                key=f"{key_prefix}_page"
            )
            
        with col2:
            st.write(f"Page {page} of {total_pages}")
            
        with col3:
            page_size = st.selectbox(
                "Rows per page",
                options=[5, 10, 25, 50],
                index=1,
                key=f"{key_prefix}_page_size"
            )
            
        # Get page data
        start_idx = (page - 1) * page_size
        end_idx = min(start_idx + page_size, len(data))
        page_data = data.iloc[start_idx:end_idx].copy()
        
        # Format the data for display
        display_data = format_func(page_data)
        
        # Display table
        st.dataframe(
            display_data,
            use_container_width=True,
            column_config=column_config_func(),
            hide_index=True
        )
        
        return display_data

    # Utility functions for generating sample data
    def generate_sample_transaction_data(num_rows=100):
        """Generate sample transaction data"""
        categories = ['grocery', 'gas', 'restaurant', 'online', 'retail', 'entertainment']
        
        data = []
        for i in range(num_rows):
            is_fraud = np.random.choice([0, 1], p=[0.95, 0.05])
            amount = np.random.lognormal(4, 1) if not is_fraud else np.random.lognormal(5, 1.5)
            
            data.append({
                'transaction_id': f'TXN_{i:06d}',
                'user_id': f'USER_{np.random.randint(1000, 9999)}',
                'amount': amount,
                'merchant_category': np.random.choice(categories),
                'risk_score': np.random.beta(2, 8) if not is_fraud else np.random.beta(8, 2),
                'is_fraud': is_fraud,
                'timestamp': datetime.now() - timedelta(days=np.random.randint(0, 30))
            })
            
        return pd.DataFrame(data)

    def generate_sample_alert_data(num_rows=50):
        """Generate sample alert data"""
        severities = ['critical', 'high', 'medium', 'low']
        statuses = ['new', 'investigating', 'resolved', 'false_positive']
        
        data = []
        for i in range(num_rows):
            severity = np.random.choice(severities, p=[0.1, 0.3, 0.4, 0.2])
            
            data.append({
                'id': f'ALERT_{i:06d}',
                'severity': severity,
                'status': np.random.choice(statuses),
                'transaction_id': f'TXN_{np.random.randint(100000, 999999)}',
                'user_id': f'USER_{np.random.randint(1000, 9999)}',
                'description': f'Fraud alert for transaction with {severity} risk level',
                'risk_score': np.random.uniform(0.3, 0.95),
                'timestamp': datetime.now() - timedelta(hours=np.random.randint(0, 72))
            })
            
        return pd.DataFrame(data)

    def generate_sample_user_data(num_rows=100):
        """Generate sample user data"""
        statuses = ['active', 'flagged', 'suspended', 'under_review']
        
        data = []
        for i in range(num_rows):
            total_txns = np.random.randint(10, 1000)
            fraud_count = np.random.randint(0, max(1, total_txns // 20))
            
            data.append({
                'user_id': f'USER_{i:06d}',
                'name': f'User {i}',
                'email': f'user{i}@example.com',
                'total_transactions': total_txns,
                'fraud_count': fraud_count,
                'risk_score': np.random.beta(2, 8),
                'status': np.random.choice(statuses, p=[0.7, 0.15, 0.05, 0.1]),
                'last_activity': datetime.now() - timedelta(days=np.random.randint(0, 90))
            })
            
        return pd.DataFrame(data)

    def generate_sample_merchant_data(num_rows=50):
        """Generate sample merchant data"""
        categories = ['grocery', 'gas', 'restaurant', 'online', 'retail', 'entertainment']
        statuses = ['active', 'flagged', 'suspended']
        
        data = []
        for i in range(num_rows):
            volume = np.random.randint(100, 10000)
            fraud_rate = np.random.uniform(0.01, 0.1)
            
            data.append({
                'merchant_id': f'MERCHANT_{i:06d}',
                'name': f'Merchant {i}',
                'category': np.random.choice(categories),
                'transaction_volume': volume,
                'fraud_rate': fraud_rate,
                'risk_score': np.random.beta(2, 8),
                'status': np.random.choice(statuses, p=[0.8, 0.15, 0.05])
            })
            
        return pd.DataFrame(data)