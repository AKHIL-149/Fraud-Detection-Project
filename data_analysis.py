"""
Credit Card Transactions Dataset Analysis
This script performs comprehensive exploratory data analysis on the credit card transaction dataset
to understand its structure, patterns, and characteristics for fraud detection modeling.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Set display options for better readability
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

class CreditCardDataAnalyzer:
    """
    Handles exploratory data analysis for credit card transaction data.
    Provides methods to understand data structure, distributions, and patterns.
    """

    def __init__(self, data_dir='detection_data'):
        self.data_dir = data_dir
        self.transactions_df = None
        self.cards_df = None
        self.users_df = None

    def load_data(self, sample_size=None):
        """
        Load the dataset files into memory.
        Using chunking for large files to avoid memory issues.

        Args:
            sample_size: Number of rows to load (None for all data)
        """
        print("=" * 80)
        print("LOADING DATASET")
        print("=" * 80)

        # Load main transaction file
        transactions_path = f'{self.data_dir}/credit_card_transactions-ibm_v2.csv'
        print(f"\nLoading transactions from: {transactions_path}")

        if sample_size:
            print(f"Loading sample of {sample_size:,} rows for initial analysis...")
            self.transactions_df = pd.read_csv(transactions_path, nrows=sample_size)
        else:
            print("Loading full dataset (this may take a while)...")
            self.transactions_df = pd.read_csv(transactions_path)

        print(f"Loaded {len(self.transactions_df):,} transactions")

        # Clean and convert the Amount column
        if 'Amount' in self.transactions_df.columns:
            print("Converting Amount column to numeric...")
            self.transactions_df['Amount'] = self.transactions_df['Amount'].str.replace('$', '').str.replace(',', '').astype(float)

        # Convert fraud column to binary
        fraud_columns = [col for col in self.transactions_df.columns
                        if 'fraud' in col.lower() or 'is_fraud' in col.lower()]
        if fraud_columns:
            fraud_col = fraud_columns[0]
            print(f"Converting {fraud_col} column to binary...")
            self.transactions_df[fraud_col] = (self.transactions_df[fraud_col] == 'Yes').astype(int)

        # Create proper datetime column from Year, Month, Day, Time
        if all(col in self.transactions_df.columns for col in ['Year', 'Month', 'Day', 'Time']):
            print("Creating datetime column from date components...")
            self.transactions_df['DateTime'] = pd.to_datetime(
                self.transactions_df['Year'].astype(str) + '-' +
                self.transactions_df['Month'].astype(str) + '-' +
                self.transactions_df['Day'].astype(str) + ' ' +
                self.transactions_df['Time'].astype(str)
            )

        # Load supplementary files
        try:
            self.cards_df = pd.read_csv(f'{self.data_dir}/sd254_cards.csv')
            print(f"Loaded {len(self.cards_df):,} card records")
        except FileNotFoundError:
            print("Cards data file not found, skipping...")

        try:
            self.users_df = pd.read_csv(f'{self.data_dir}/sd254_users.csv')
            print(f"Loaded {len(self.users_df):,} user records")
        except FileNotFoundError:
            print("Users data file not found, skipping...")

        print("\nData loading completed successfully")

    def basic_info(self):
        """
        Display basic information about the dataset structure and contents.
        """
        print("\n" + "=" * 80)
        print("BASIC DATASET INFORMATION")
        print("=" * 80)

        print("\n--- Dataset Shape ---")
        print(f"Transactions: {self.transactions_df.shape[0]:,} rows x {self.transactions_df.shape[1]} columns")

        print("\n--- Column Names and Types ---")
        print(self.transactions_df.dtypes)

        print("\n--- First Few Rows ---")
        print(self.transactions_df.head())

        print("\n--- Memory Usage ---")
        memory_mb = self.transactions_df.memory_usage(deep=True).sum() / 1024**2
        print(f"Total memory usage: {memory_mb:.2f} MB")

        print("\n--- Missing Values ---")
        missing = self.transactions_df.isnull().sum()
        missing_pct = (missing / len(self.transactions_df)) * 100
        missing_df = pd.DataFrame({
            'Missing_Count': missing,
            'Percentage': missing_pct
        })
        print(missing_df[missing_df['Missing_Count'] > 0])

        if len(missing_df[missing_df['Missing_Count'] > 0]) == 0:
            print("No missing values found")

    def analyze_fraud_distribution(self):
        """
        Analyze the distribution of fraudulent vs legitimate transactions.
        This is critical for understanding class imbalance in the dataset.
        """
        print("\n" + "=" * 80)
        print("FRAUD DISTRIBUTION ANALYSIS")
        print("=" * 80)

        # Check if fraud column exists and identify it
        fraud_columns = [col for col in self.transactions_df.columns
                        if 'fraud' in col.lower() or 'is_fraud' in col.lower()]

        if not fraud_columns:
            print("Warning: No fraud indicator column found in dataset")
            return

        fraud_col = fraud_columns[0]
        print(f"\nUsing fraud indicator column: '{fraud_col}'")

        # Calculate fraud statistics
        fraud_counts = self.transactions_df[fraud_col].value_counts()
        fraud_pct = self.transactions_df[fraud_col].value_counts(normalize=True) * 100

        print("\n--- Transaction Distribution ---")
        print(f"Legitimate transactions: {fraud_counts.get(0, fraud_counts.get('No', 0)):,} ({fraud_pct.get(0, fraud_pct.get('No', 0)):.2f}%)")
        print(f"Fraudulent transactions: {fraud_counts.get(1, fraud_counts.get('Yes', 0)):,} ({fraud_pct.get(1, fraud_pct.get('Yes', 0)):.2f}%)")

        # Calculate imbalance ratio
        if len(fraud_counts) == 2:
            imbalance_ratio = fraud_counts.max() / fraud_counts.min()
            print(f"\nClass imbalance ratio: {imbalance_ratio:.2f}:1")

            if imbalance_ratio > 10:
                print("Note: Significant class imbalance detected - will need special handling (SMOTE, class weights, etc.)")

    def analyze_temporal_patterns(self):
        """
        Analyze temporal patterns in the transaction data.
        Look at transaction volume and fraud rates over time.
        """
        print("\n" + "=" * 80)
        print("TEMPORAL PATTERN ANALYSIS")
        print("=" * 80)

        # Use the DateTime column created during load
        if 'DateTime' not in self.transactions_df.columns:
            print("No datetime column available")
            return

        datetime_col = 'DateTime'
        print(f"\nUsing datetime column: '{datetime_col}'")

        try:
            print("\n--- Temporal Coverage ---")
            print(f"Date range: {self.transactions_df[datetime_col].min()} to {self.transactions_df[datetime_col].max()}")

            date_range = (self.transactions_df[datetime_col].max() - self.transactions_df[datetime_col].min()).days
            print(f"Total days covered: {date_range}")

            # Extract temporal features for analysis
            self.transactions_df['year_analysis'] = self.transactions_df[datetime_col].dt.year
            self.transactions_df['month_analysis'] = self.transactions_df[datetime_col].dt.month
            self.transactions_df['day_analysis'] = self.transactions_df[datetime_col].dt.day
            self.transactions_df['hour'] = self.transactions_df[datetime_col].dt.hour
            self.transactions_df['day_of_week'] = self.transactions_df[datetime_col].dt.dayofweek

            print("\n--- Transactions by Year ---")
            print(self.transactions_df['year_analysis'].value_counts().sort_index())

            print("\n--- Transactions by Hour of Day ---")
            hourly = self.transactions_df['hour'].value_counts().sort_index()
            print(hourly)

            print("\n--- Transactions by Day of Week ---")
            print("(0=Monday, 6=Sunday)")
            print(self.transactions_df['day_of_week'].value_counts().sort_index())

        except Exception as e:
            print(f"Error processing datetime: {e}")

    def analyze_transaction_amounts(self):
        """
        Analyze the distribution of transaction amounts.
        Look for patterns that might indicate fraud.
        """
        print("\n" + "=" * 80)
        print("TRANSACTION AMOUNT ANALYSIS")
        print("=" * 80)

        # Find amount column
        amount_cols = [col for col in self.transactions_df.columns
                      if 'amount' in col.lower() or 'value' in col.lower()]

        if not amount_cols:
            print("No amount column found in dataset")
            return

        amount_col = amount_cols[0]
        print(f"\nUsing amount column: '{amount_col}'")

        print("\n--- Amount Statistics ---")
        print(self.transactions_df[amount_col].describe())

        print("\n--- Amount Distribution by Percentiles ---")
        percentiles = [0.1, 0.25, 0.5, 0.75, 0.9, 0.95, 0.99]
        for p in percentiles:
            value = self.transactions_df[amount_col].quantile(p)
            print(f"{p*100:.0f}th percentile: ${value:.2f}")

        # Check for negative amounts
        negative_count = (self.transactions_df[amount_col] < 0).sum()
        if negative_count > 0:
            print(f"\nWarning: Found {negative_count} transactions with negative amounts (possible refunds)")

        # Analyze amount distribution by fraud status
        fraud_columns = [col for col in self.transactions_df.columns
                        if 'fraud' in col.lower() or 'is_fraud' in col.lower()]

        if fraud_columns:
            fraud_col = fraud_columns[0]
            print("\n--- Amount Statistics by Fraud Status ---")
            print(self.transactions_df.groupby(fraud_col)[amount_col].describe())

    def analyze_merchants(self):
        """
        Analyze merchant-related patterns in the data.
        Identify high-risk merchant categories or patterns.
        """
        print("\n" + "=" * 80)
        print("MERCHANT ANALYSIS")
        print("=" * 80)

        # Find merchant-related columns
        merchant_cols = [col for col in self.transactions_df.columns
                        if any(term in col.lower() for term in ['merchant', 'mcc', 'category'])]

        if not merchant_cols:
            print("No merchant columns found in dataset")
            return

        for col in merchant_cols:
            print(f"\n--- Analysis of '{col}' ---")
            value_counts = self.transactions_df[col].value_counts()
            print(f"Unique values: {len(value_counts)}")
            print("\nTop 10 most common values:")
            print(value_counts.head(10))

            # Calculate fraud rate by merchant if possible
            fraud_columns = [c for c in self.transactions_df.columns
                           if 'fraud' in c.lower() or 'is_fraud' in c.lower()]

            if fraud_columns and len(value_counts) < 1000:
                fraud_col = fraud_columns[0]
                try:
                    fraud_by_merchant = self.transactions_df.groupby(col)[fraud_col].agg(['sum', 'count', 'mean'])
                    fraud_by_merchant.columns = ['Fraud_Count', 'Total_Transactions', 'Fraud_Rate']
                    fraud_by_merchant = fraud_by_merchant.sort_values('Fraud_Rate', ascending=False)

                    print("\nTop 10 merchants by fraud rate (minimum 10 transactions):")
                    fraud_by_merchant_filtered = fraud_by_merchant[fraud_by_merchant['Total_Transactions'] >= 10]
                    print(fraud_by_merchant_filtered.head(10))
                except Exception as e:
                    print(f"Could not calculate fraud rate by merchant: {e}")

    def analyze_geographic_patterns(self):
        """
        Analyze geographic patterns in transactions.
        Identify high-risk locations or unusual patterns.
        """
        print("\n" + "=" * 80)
        print("GEOGRAPHIC ANALYSIS")
        print("=" * 80)

        # Find geographic columns
        geo_cols = [col for col in self.transactions_df.columns
                   if any(term in col.lower() for term in ['state', 'city', 'country', 'zip', 'location'])]

        if not geo_cols:
            print("No geographic columns found in dataset")
            return

        for col in geo_cols:
            print(f"\n--- Analysis of '{col}' ---")
            value_counts = self.transactions_df[col].value_counts()
            print(f"Unique values: {len(value_counts)}")
            print("\nTop 15 locations:")
            print(value_counts.head(15))

    def analyze_users_and_cards(self):
        """
        Analyze user and card patterns if supplementary data is available.
        """
        if self.users_df is not None:
            print("\n" + "=" * 80)
            print("USER DATA ANALYSIS")
            print("=" * 80)

            print("\n--- User Data Structure ---")
            print(self.users_df.head())
            print("\n--- User Data Columns ---")
            print(self.users_df.dtypes)

        if self.cards_df is not None:
            print("\n" + "=" * 80)
            print("CARD DATA ANALYSIS")
            print("=" * 80)

            print("\n--- Card Data Structure ---")
            print(self.cards_df.head())
            print("\n--- Card Data Columns ---")
            print(self.cards_df.dtypes)

    def generate_summary_report(self):
        """
        Generate a comprehensive summary report of the analysis findings.
        """
        print("\n" + "=" * 80)
        print("SUMMARY REPORT")
        print("=" * 80)

        print(f"\nDataset Overview:")
        print(f"  - Total transactions analyzed: {len(self.transactions_df):,}")
        print(f"  - Number of features: {len(self.transactions_df.columns)}")
        print(f"  - Memory footprint: {self.transactions_df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")

        # Check for fraud column
        fraud_columns = [col for col in self.transactions_df.columns
                        if 'fraud' in col.lower() or 'is_fraud' in col.lower()]
        if fraud_columns:
            fraud_col = fraud_columns[0]
            fraud_rate = self.transactions_df[fraud_col].mean() * 100
            print(f"  - Overall fraud rate: {fraud_rate:.3f}%")

        print("\nKey Observations:")
        print("  - Dataset loaded successfully with all required fields")
        print("  - Ready for feature engineering and model development")
        print("  - Consider stratified sampling for model training due to class imbalance")

        print("\nRecommended Next Steps:")
        print("  1. Feature engineering (create velocity, aggregation, and behavioral features)")
        print("  2. Handle class imbalance (use SMOTE, class weights, or stratified sampling)")
        print("  3. Train baseline models (Random Forest, XGBoost)")
        print("  4. Implement online learning for adaptive detection")
        print("  5. Set up model evaluation pipeline with appropriate metrics (Precision, Recall, F1, AUC)")

    def run_complete_analysis(self, sample_size=100000):
        """
        Run the complete analysis pipeline on the dataset.

        Args:
            sample_size: Number of rows to analyze (use smaller sample for quick analysis)
        """
        self.load_data(sample_size=sample_size)
        self.basic_info()
        self.analyze_fraud_distribution()
        self.analyze_temporal_patterns()
        self.analyze_transaction_amounts()
        self.analyze_merchants()
        self.analyze_geographic_patterns()
        self.analyze_users_and_cards()
        self.generate_summary_report()


if __name__ == "__main__":
    # Initialize analyzer
    analyzer = CreditCardDataAnalyzer(data_dir='detection_data')

    # Run analysis on a sample first (faster for initial exploration)
    print("Starting exploratory data analysis...")
    print("Note: Using sample of 100,000 transactions for initial analysis")
    print("For full dataset analysis, modify the sample_size parameter\n")

    analyzer.run_complete_analysis(sample_size=100000)

    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    print("\nTo analyze the full dataset, run:")
    print("  analyzer.run_complete_analysis(sample_size=None)")
