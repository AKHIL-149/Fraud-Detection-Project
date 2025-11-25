"""
Feature Engineering Pipeline for Fraud Detection
Creates behavioral, temporal, and risk-based features from raw transaction data
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class FraudFeatureEngine:
    """
    Generates features for fraud detection from transaction data.
    Focuses on velocity, behavioral patterns, and risk indicators.
    """

    def __init__(self):
        self.user_profiles = {}
        self.merchant_risk_scores = {}
        self.mcc_risk_scores = {}
        self.geo_risk_scores = {}

    def create_temporal_features(self, df):
        """
        Extract time-based features that capture transaction timing patterns.
        Fraud often occurs at unusual times or with unusual frequency.
        """
        print("Creating temporal features...")

        # Ensure DateTime column exists
        if 'DateTime' not in df.columns:
            df['DateTime'] = pd.to_datetime(
                df['Year'].astype(str) + '-' +
                df['Month'].astype(str) + '-' +
                df['Day'].astype(str) + ' ' +
                df['Time'].astype(str)
            )

        # Basic temporal features
        df['hour'] = df['DateTime'].dt.hour
        df['day_of_week'] = df['DateTime'].dt.dayofweek
        df['day_of_month'] = df['DateTime'].dt.day
        df['month'] = df['DateTime'].dt.month
        df['year'] = df['DateTime'].dt.year

        # Is weekend
        df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)

        # Time of day categories
        df['time_of_day'] = pd.cut(df['hour'],
                                    bins=[0, 6, 12, 18, 24],
                                    labels=['night', 'morning', 'afternoon', 'evening'],
                                    include_lowest=True)

        # Cyclical encoding for hour (captures circular nature of time)
        df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
        df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)

        # Day of week cyclical encoding
        df['dow_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
        df['dow_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)

        print(f"Created {8} temporal features")
        return df

    def create_velocity_features(self, df):
        """
        Calculate transaction velocity features.
        Fraudsters often make multiple transactions in short time windows.
        """
        print("Creating velocity features...")

        # Sort by user, card, and datetime for proper window calculations
        df = df.sort_values(['User', 'Card', 'DateTime']).reset_index(drop=True)

        # Time since last transaction for same user
        df['time_since_last_txn'] = df.groupby(['User', 'Card'])['DateTime'].diff().dt.total_seconds()
        df['time_since_last_txn'] = df['time_since_last_txn'].fillna(86400)  # Default 24 hours

        # Transaction count in last 1 hour
        df['txn_count_1h'] = df.groupby(['User', 'Card']).rolling(
            window='1H', on='DateTime'
        )['Amount'].count().reset_index(drop=True)

        # Transaction count in last 24 hours
        df['txn_count_24h'] = df.groupby(['User', 'Card']).rolling(
            window='24H', on='DateTime'
        )['Amount'].count().reset_index(drop=True)

        # Transaction count in last 7 days
        df['txn_count_7d'] = df.groupby(['User', 'Card']).rolling(
            window='7D', on='DateTime'
        )['Amount'].count().reset_index(drop=True)

        # Amount spent in last 24 hours
        df['amount_sum_24h'] = df.groupby(['User', 'Card']).rolling(
            window='24H', on='DateTime'
        )['Amount'].sum().reset_index(drop=True)

        # Fill NaN values for velocity features
        velocity_cols = ['txn_count_1h', 'txn_count_24h', 'txn_count_7d', 'amount_sum_24h']
        for col in velocity_cols:
            df[col] = df[col].fillna(1)

        print(f"Created 5 velocity features")
        return df

    def create_amount_features(self, df):
        """
        Create features related to transaction amounts.
        Unusual amounts are strong fraud indicators.
        """
        print("Creating amount features...")

        # Log transform to handle skewness
        df['amount_log'] = np.log1p(df['Amount'])

        # Amount categories
        df['amount_category'] = pd.cut(df['Amount'],
                                       bins=[-np.inf, 10, 50, 100, 200, np.inf],
                                       labels=['very_small', 'small', 'medium', 'large', 'very_large'])

        # Is the amount a round number (often indicates fraud)
        df['is_round_amount'] = ((df['Amount'] % 10 == 0) & (df['Amount'] > 0)).astype(int)

        # Deviation from user's historical average
        user_avg = df.groupby('User')['Amount'].transform('mean')
        user_std = df.groupby('User')['Amount'].transform('std')
        df['amount_vs_user_avg'] = (df['Amount'] - user_avg) / (user_std + 1)

        # Deviation from merchant category average
        mcc_avg = df.groupby('MCC')['Amount'].transform('mean')
        mcc_std = df.groupby('MCC')['Amount'].transform('std')
        df['amount_vs_mcc_avg'] = (df['Amount'] - mcc_avg) / (mcc_std + 1)

        # Is amount negative (refund/chargeback)
        df['is_refund'] = (df['Amount'] < 0).astype(int)

        print(f"Created 6 amount features")
        return df

    def create_merchant_features(self, df):
        """
        Create merchant-related features.
        Certain merchants and categories have higher fraud rates.
        """
        print("Creating merchant features...")

        # Transaction count per merchant (merchant popularity)
        merchant_counts = df['Merchant Name'].value_counts()
        df['merchant_txn_count'] = df['Merchant Name'].map(merchant_counts)

        # Is online transaction
        df['is_online'] = (df['Merchant City'] == 'ONLINE').astype(int)

        # MCC frequency features
        mcc_counts = df['MCC'].value_counts()
        df['mcc_frequency'] = df['MCC'].map(mcc_counts)

        # User's transaction count with this merchant
        user_merchant_counts = df.groupby(['User', 'Merchant Name']).size()
        df['user_merchant_txn_count'] = df.set_index(['User', 'Merchant Name']).index.map(
            user_merchant_counts
        ).values
        df['user_merchant_txn_count'] = df['user_merchant_txn_count'].fillna(0)

        # Is this user's first transaction with this merchant
        df['is_first_merchant_txn'] = (df['user_merchant_txn_count'] == 1).astype(int)

        # Chip usage features
        df['is_chip_txn'] = (df['Use Chip'] == 'Chip Transaction').astype(int)
        df['is_swipe_txn'] = (df['Use Chip'] == 'Swipe Transaction').astype(int)
        df['is_online_txn'] = (df['Use Chip'] == 'Online Transaction').astype(int)

        print(f"Created 8 merchant features")
        return df

    def create_geographic_features(self, df):
        """
        Create location-based features.
        Geographic patterns are strong fraud indicators.
        """
        print("Creating geographic features...")

        # State-based features
        state_txn_counts = df['Merchant State'].value_counts()
        df['state_txn_count'] = df['Merchant State'].map(state_txn_counts).fillna(0)

        # Is international transaction
        international_states = ['Mexico', 'Italy', 'Poland', 'Philippines', 'Peru',
                               'Pakistan', 'China', 'Japan', 'Canada', 'UK']
        df['is_international'] = df['Merchant State'].isin(international_states).astype(int)

        # High risk states (based on analysis findings)
        high_risk_states = ['Italy', 'OH']
        df['is_high_risk_state'] = df['Merchant State'].isin(high_risk_states).astype(int)

        # Primary states (CA and NY account for 70% of transactions)
        df['is_primary_state'] = df['Merchant State'].isin(['CA', 'NY']).astype(int)

        # Missing geographic data (often indicates online/virtual transactions)
        df['missing_geo_data'] = (df['Merchant State'].isna() | df['Zip'].isna()).astype(int)

        # Distance from user's home state (would require user location data)
        # For now, using a proxy: same state as most common transaction location
        user_primary_state = df.groupby('User')['Merchant State'].agg(
            lambda x: x.mode()[0] if len(x.mode()) > 0 else None
        )
        df['is_user_primary_state'] = (
            df['Merchant State'] == df['User'].map(user_primary_state)
        ).astype(int)

        print(f"Created 6 geographic features")
        return df

    def create_card_features(self, df, cards_df=None):
        """
        Create card-related features.
        Card characteristics can indicate fraud risk.
        """
        print("Creating card features...")

        # Transaction count per card
        card_counts = df.groupby('Card').size()
        df['card_txn_count'] = df['Card'].map(card_counts)

        # If card data is available, merge relevant features
        if cards_df is not None:
            # Select relevant card features
            card_features = cards_df[['User', 'CARD INDEX', 'Card Brand', 'Card Type',
                                     'Has Chip', 'Card on Dark Web']].copy()

            # Merge with transaction data
            df = df.merge(card_features,
                         left_on=['User', 'Card'],
                         right_on=['User', 'CARD INDEX'],
                         how='left')

            # Encode card features
            df['card_on_dark_web'] = (df['Card on Dark Web'] == 'Yes').astype(int)
            df['card_has_chip'] = (df['Has Chip'] == 'YES').astype(int)

            # Chip mismatch (card has chip but swipe used)
            df['chip_mismatch'] = (
                (df['card_has_chip'] == 1) & (df['is_swipe_txn'] == 1)
            ).astype(int)

            # Card brand
            df['is_visa'] = (df['Card Brand'] == 'Visa').astype(int)
            df['is_mastercard'] = (df['Card Brand'] == 'Mastercard').astype(int)

            # Card type
            df['is_debit'] = df['Card Type'].str.contains('Debit', na=False).astype(int)
            df['is_credit'] = (df['Card Type'] == 'Credit').astype(int)

            print(f"Created 9 card features (with card data)")
        else:
            print(f"Created 1 card feature (without supplementary card data)")

        return df

    def create_user_behavior_features(self, df, users_df=None):
        """
        Create user behavioral features.
        Changes in user behavior patterns can indicate account takeover.
        """
        print("Creating user behavior features...")

        # Number of unique cards per user
        user_card_counts = df.groupby('User')['Card'].nunique()
        df['user_card_count'] = df['User'].map(user_card_counts)

        # Number of unique merchants per user
        user_merchant_counts = df.groupby('User')['Merchant Name'].nunique()
        df['user_merchant_diversity'] = df['User'].map(user_merchant_counts)

        # Number of unique MCCs per user (spending diversity)
        user_mcc_counts = df.groupby('User')['MCC'].nunique()
        df['user_mcc_diversity'] = df['User'].map(user_mcc_counts)

        # User's average transaction amount
        user_avg_amount = df.groupby('User')['Amount'].mean()
        df['user_avg_amount'] = df['User'].map(user_avg_amount)

        # User's transaction frequency (transactions per day)
        user_date_range = df.groupby('User')['DateTime'].agg(lambda x: (x.max() - x.min()).days + 1)
        user_txn_counts = df.groupby('User').size()
        df['user_txn_per_day'] = df['User'].map(user_txn_counts / user_date_range)
        df['user_txn_per_day'] = df['user_txn_per_day'].fillna(0)

        # If user data is available, add demographic features
        if users_df is not None:
            # Convert income and debt to numeric
            users_df['Yearly Income - Person'] = users_df['Yearly Income - Person'].str.replace(
                '$', ''
            ).str.replace(',', '').astype(float)
            users_df['Total Debt'] = users_df['Total Debt'].str.replace(
                '$', ''
            ).str.replace(',', '').astype(float)

            # Select relevant user features and add index as User ID
            user_features = users_df.reset_index()[['index', 'Current Age', 'FICO Score',
                                                    'Num Credit Cards', 'Yearly Income - Person',
                                                    'Total Debt']].copy()
            user_features.columns = ['User', 'Current Age', 'FICO Score',
                                    'Num Credit Cards', 'Yearly Income - Person',
                                    'Total Debt']

            df = df.merge(user_features,
                         on='User',
                         how='left')

            # Calculate debt-to-income ratio
            df['debt_to_income_ratio'] = df['Total Debt'] / (df['Yearly Income - Person'] + 1)

            # Transaction amount as percentage of annual income
            df['amount_pct_of_income'] = df['Amount'] / (df['Yearly Income - Person'] / 365 + 1)

            print(f"Created 11 user behavior features (with user data)")
        else:
            print(f"Created 5 user behavior features (without supplementary user data)")

        return df

    def create_risk_scores(self, df):
        """
        Calculate risk scores based on historical fraud rates.
        These are learned from the training data.
        """
        print("Creating risk score features...")

        # Calculate fraud rate by merchant category (MCC)
        mcc_fraud_rate = df.groupby('MCC')['Is Fraud?'].mean()
        df['mcc_fraud_rate'] = df['MCC'].map(mcc_fraud_rate).fillna(df['Is Fraud?'].mean())

        # Calculate fraud rate by state
        state_fraud_rate = df.groupby('Merchant State')['Is Fraud?'].mean()
        df['state_fraud_rate'] = df['Merchant State'].map(state_fraud_rate).fillna(df['Is Fraud?'].mean())

        # Calculate fraud rate by hour
        hour_fraud_rate = df.groupby('hour')['Is Fraud?'].mean()
        df['hour_fraud_rate'] = df['hour'].map(hour_fraud_rate).fillna(df['Is Fraud?'].mean())

        # Calculate fraud rate by transaction type
        txn_type_fraud_rate = df.groupby('Use Chip')['Is Fraud?'].mean()
        df['txn_type_fraud_rate'] = df['Use Chip'].map(txn_type_fraud_rate).fillna(df['Is Fraud?'].mean())

        # Composite risk score (weighted average)
        df['composite_risk_score'] = (
            df['mcc_fraud_rate'] * 0.3 +
            df['state_fraud_rate'] * 0.3 +
            df['hour_fraud_rate'] * 0.2 +
            df['txn_type_fraud_rate'] * 0.2
        )

        print(f"Created 5 risk score features")
        return df

    def create_all_features(self, df, cards_df=None, users_df=None, include_risk_scores=True):
        """
        Generate all features for fraud detection.
        This is the main entry point for the feature engineering pipeline.

        Args:
            df: Transaction dataframe
            cards_df: Optional card details dataframe
            users_df: Optional user details dataframe
            include_risk_scores: Whether to include risk scores (only for training data)
        """
        print("\n" + "=" * 80)
        print("FEATURE ENGINEERING PIPELINE")
        print("=" * 80)
        print(f"\nStarting with {len(df)} transactions and {len(df.columns)} features")

        original_count = len(df)

        # Create all feature groups
        df = self.create_temporal_features(df)
        df = self.create_amount_features(df)
        df = self.create_merchant_features(df)
        df = self.create_geographic_features(df)
        df = self.create_card_features(df, cards_df)
        df = self.create_user_behavior_features(df, users_df)

        # Velocity features are computationally expensive, do them last
        df = self.create_velocity_features(df)

        # Risk scores should only be calculated on training data to avoid leakage
        if include_risk_scores:
            df = self.create_risk_scores(df)

        print("\n" + "=" * 80)
        print(f"Feature engineering complete!")
        print(f"Final dataset: {len(df)} transactions with {len(df.columns)} features")
        print(f"Added {len(df.columns) - 15} new features")
        print("=" * 80)

        return df

    def get_feature_names(self):
        """
        Return list of all engineered feature names.
        Useful for model training and feature selection.
        """
        feature_names = [
            # Temporal
            'hour', 'day_of_week', 'day_of_month', 'month', 'year',
            'is_weekend', 'hour_sin', 'hour_cos', 'dow_sin', 'dow_cos',

            # Amount
            'amount_log', 'is_round_amount', 'amount_vs_user_avg',
            'amount_vs_mcc_avg', 'is_refund',

            # Merchant
            'merchant_txn_count', 'is_online', 'mcc_frequency',
            'user_merchant_txn_count', 'is_first_merchant_txn',
            'is_chip_txn', 'is_swipe_txn', 'is_online_txn',

            # Geographic
            'state_txn_count', 'is_international', 'is_high_risk_state',
            'is_primary_state', 'missing_geo_data', 'is_user_primary_state',

            # Card (if available)
            'card_txn_count', 'card_on_dark_web', 'card_has_chip',
            'chip_mismatch', 'is_visa', 'is_mastercard', 'is_debit', 'is_credit',

            # User behavior
            'user_card_count', 'user_merchant_diversity', 'user_mcc_diversity',
            'user_avg_amount', 'user_txn_per_day',

            # Velocity
            'time_since_last_txn', 'txn_count_1h', 'txn_count_24h',
            'txn_count_7d', 'amount_sum_24h',

            # Risk scores
            'mcc_fraud_rate', 'state_fraud_rate', 'hour_fraud_rate',
            'txn_type_fraud_rate', 'composite_risk_score'
        ]

        return feature_names


if __name__ == "__main__":
    print("Loading dataset for feature engineering...")

    # Load data using the analyzer
    from data_analysis import CreditCardDataAnalyzer

    analyzer = CreditCardDataAnalyzer(data_dir='detection_data')
    analyzer.load_data(sample_size=100000)

    # Initialize feature engine
    feature_engine = FraudFeatureEngine()

    # Create all features
    df_with_features = feature_engine.create_all_features(
        analyzer.transactions_df,
        cards_df=analyzer.cards_df,
        users_df=analyzer.users_df,
        include_risk_scores=True
    )

    print("\nFeature engineering complete!")
    print(f"Sample of engineered features:")
    print(df_with_features[feature_engine.get_feature_names()[:10]].head())

    # Save engineered features
    print("\nSaving engineered features...")
    df_with_features.to_csv('detection_data/transactions_with_features.csv', index=False)
    print("Saved to: detection_data/transactions_with_features.csv")
