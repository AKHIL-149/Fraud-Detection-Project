"""
Data Visualization Script for Credit Card Fraud Detection
Creates comprehensive visualizations to understand patterns and distributions in the dataset
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Set style for better looking plots
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (15, 10)

class FraudDataVisualizer:
    """
    Creates visualizations for fraud detection data analysis
    """

    def __init__(self, transactions_df):
        self.df = transactions_df
        # Extract temporal features if not already present
        if 'DateTime' in self.df.columns and 'hour' not in self.df.columns:
            self.df['hour'] = self.df['DateTime'].dt.hour
            self.df['day_of_week'] = self.df['DateTime'].dt.dayofweek
            self.df['year_analysis'] = self.df['DateTime'].dt.year

    def plot_fraud_distribution(self, save_path='plots/fraud_distribution.png'):
        """
        Visualize the distribution of fraud vs legitimate transactions
        """
        fig, axes = plt.subplots(1, 2, figsize=(15, 5))

        # Count plot
        fraud_counts = self.df['Is Fraud?'].value_counts()
        axes[0].bar(['Legitimate', 'Fraudulent'],
                   [fraud_counts[0], fraud_counts[1]],
                   color=['#2ecc71', '#e74c3c'])
        axes[0].set_ylabel('Count')
        axes[0].set_title('Transaction Distribution')
        axes[0].set_yscale('log')

        for i, v in enumerate([fraud_counts[0], fraud_counts[1]]):
            axes[0].text(i, v, f'{v:,}', ha='center', va='bottom')

        # Percentage pie chart
        axes[1].pie(fraud_counts, labels=['Legitimate', 'Fraudulent'],
                   autopct='%1.2f%%', colors=['#2ecc71', '#e74c3c'],
                   startangle=90)
        axes[1].set_title('Transaction Distribution (Percentage)')

        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Saved fraud distribution plot to {save_path}")

    def plot_amount_distribution(self, save_path='plots/amount_distribution.png'):
        """
        Visualize transaction amount distributions
        """
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))

        # Overall amount distribution (log scale due to outliers)
        axes[0, 0].hist(self.df['Amount'], bins=50, color='#3498db', edgecolor='black')
        axes[0, 0].set_xlabel('Transaction Amount ($)')
        axes[0, 0].set_ylabel('Frequency')
        axes[0, 0].set_title('Overall Amount Distribution')
        axes[0, 0].set_xlim(0, 500)

        # Amount distribution by fraud status
        legitimate = self.df[self.df['Is Fraud?'] == 0]['Amount']
        fraudulent = self.df[self.df['Is Fraud?'] == 1]['Amount']

        axes[0, 1].hist([legitimate, fraudulent], bins=50,
                       label=['Legitimate', 'Fraudulent'],
                       color=['#2ecc71', '#e74c3c'], alpha=0.7)
        axes[0, 1].set_xlabel('Transaction Amount ($)')
        axes[0, 1].set_ylabel('Frequency')
        axes[0, 1].set_title('Amount Distribution by Fraud Status')
        axes[0, 1].legend()
        axes[0, 1].set_xlim(0, 500)

        # Box plot comparison
        data_to_plot = [legitimate[legitimate < 500], fraudulent[fraudulent < 500]]
        axes[1, 0].boxplot(data_to_plot, labels=['Legitimate', 'Fraudulent'])
        axes[1, 0].set_ylabel('Transaction Amount ($)')
        axes[1, 0].set_title('Amount Distribution Box Plot (capped at $500)')

        # Average amount by fraud status
        avg_amounts = self.df.groupby('Is Fraud?')['Amount'].mean()
        axes[1, 1].bar(['Legitimate', 'Fraudulent'],
                      [avg_amounts[0], avg_amounts[1]],
                      color=['#2ecc71', '#e74c3c'])
        axes[1, 1].set_ylabel('Average Amount ($)')
        axes[1, 1].set_title('Average Transaction Amount by Type')

        for i, v in enumerate([avg_amounts[0], avg_amounts[1]]):
            axes[1, 1].text(i, v, f'${v:.2f}', ha='center', va='bottom')

        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Saved amount distribution plot to {save_path}")

    def plot_temporal_patterns(self, save_path='plots/temporal_patterns.png'):
        """
        Visualize temporal patterns in transactions
        """
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))

        # Transactions by hour
        hourly = self.df.groupby('hour').size()
        axes[0, 0].plot(hourly.index, hourly.values, marker='o', linewidth=2, color='#3498db')
        axes[0, 0].fill_between(hourly.index, hourly.values, alpha=0.3, color='#3498db')
        axes[0, 0].set_xlabel('Hour of Day')
        axes[0, 0].set_ylabel('Number of Transactions')
        axes[0, 0].set_title('Transaction Volume by Hour')
        axes[0, 0].grid(True, alpha=0.3)

        # Transactions by day of week
        dow_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        dow = self.df.groupby('day_of_week').size()
        axes[0, 1].bar(range(7), dow.values, color='#9b59b6')
        axes[0, 1].set_xticks(range(7))
        axes[0, 1].set_xticklabels(dow_names)
        axes[0, 1].set_ylabel('Number of Transactions')
        axes[0, 1].set_title('Transaction Volume by Day of Week')

        # Fraud rate by hour
        fraud_by_hour = self.df.groupby('hour')['Is Fraud?'].mean() * 100
        axes[1, 0].plot(fraud_by_hour.index, fraud_by_hour.values,
                       marker='o', linewidth=2, color='#e74c3c')
        axes[1, 0].fill_between(fraud_by_hour.index, fraud_by_hour.values,
                                alpha=0.3, color='#e74c3c')
        axes[1, 0].set_xlabel('Hour of Day')
        axes[1, 0].set_ylabel('Fraud Rate (%)')
        axes[1, 0].set_title('Fraud Rate by Hour')
        axes[1, 0].grid(True, alpha=0.3)

        # Transactions by year
        yearly = self.df.groupby('year_analysis').size()
        axes[1, 1].plot(yearly.index, yearly.values, marker='o', linewidth=2, color='#16a085')
        axes[1, 1].fill_between(yearly.index, yearly.values, alpha=0.3, color='#16a085')
        axes[1, 1].set_xlabel('Year')
        axes[1, 1].set_ylabel('Number of Transactions')
        axes[1, 1].set_title('Transaction Volume by Year')
        axes[1, 1].grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Saved temporal patterns plot to {save_path}")

    def plot_merchant_analysis(self, save_path='plots/merchant_analysis.png'):
        """
        Visualize merchant-related patterns
        """
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))

        # Top merchant categories by volume
        top_mcc = self.df['MCC'].value_counts().head(10)
        axes[0, 0].barh(range(len(top_mcc)), top_mcc.values, color='#3498db')
        axes[0, 0].set_yticks(range(len(top_mcc)))
        axes[0, 0].set_yticklabels(top_mcc.index)
        axes[0, 0].set_xlabel('Number of Transactions')
        axes[0, 0].set_title('Top 10 Merchant Categories (MCC)')
        axes[0, 0].invert_yaxis()

        # Top cities by volume
        top_cities = self.df['Merchant City'].value_counts().head(10)
        axes[0, 1].barh(range(len(top_cities)), top_cities.values, color='#9b59b6')
        axes[0, 1].set_yticks(range(len(top_cities)))
        axes[0, 1].set_yticklabels(top_cities.index)
        axes[0, 1].set_xlabel('Number of Transactions')
        axes[0, 1].set_title('Top 10 Merchant Cities')
        axes[0, 1].invert_yaxis()

        # Top states
        top_states = self.df['Merchant State'].value_counts().head(10)
        axes[1, 0].bar(range(len(top_states)), top_states.values, color='#e67e22')
        axes[1, 0].set_xticks(range(len(top_states)))
        axes[1, 0].set_xticklabels(top_states.index, rotation=45)
        axes[1, 0].set_ylabel('Number of Transactions')
        axes[1, 0].set_title('Top 10 Merchant States')

        # Fraud rate by chip usage
        chip_fraud = self.df.groupby('Use Chip')['Is Fraud?'].mean() * 100
        axes[1, 1].bar(range(len(chip_fraud)), chip_fraud.values, color='#e74c3c')
        axes[1, 1].set_xticks(range(len(chip_fraud)))
        axes[1, 1].set_xticklabels(chip_fraud.index, rotation=45)
        axes[1, 1].set_ylabel('Fraud Rate (%)')
        axes[1, 1].set_title('Fraud Rate by Transaction Type')

        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Saved merchant analysis plot to {save_path}")

    def plot_correlation_heatmap(self, save_path='plots/correlation_heatmap.png'):
        """
        Create correlation heatmap for numeric features
        """
        # Select numeric columns
        numeric_cols = ['Amount', 'Year', 'Month', 'Day', 'hour', 'day_of_week',
                       'MCC', 'Is Fraud?']
        correlation_data = self.df[numeric_cols].corr()

        plt.figure(figsize=(10, 8))
        sns.heatmap(correlation_data, annot=True, fmt='.2f', cmap='coolwarm',
                   center=0, square=True, linewidths=1)
        plt.title('Feature Correlation Heatmap')
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Saved correlation heatmap to {save_path}")

    def generate_all_plots(self):
        """
        Generate all visualization plots
        """
        import os
        os.makedirs('plots', exist_ok=True)

        print("Generating visualizations...")
        self.plot_fraud_distribution()
        self.plot_amount_distribution()
        self.plot_temporal_patterns()
        self.plot_merchant_analysis()
        self.plot_correlation_heatmap()
        print("\nAll plots generated successfully!")


if __name__ == "__main__":
    print("Loading dataset for visualization...")

    # Load analyzed data
    from data_analysis import CreditCardDataAnalyzer

    analyzer = CreditCardDataAnalyzer(data_dir='detection_data')
    analyzer.load_data(sample_size=100000)

    print("\nGenerating visualizations...")
    visualizer = FraudDataVisualizer(analyzer.transactions_df)
    visualizer.generate_all_plots()

    print("\nVisualization complete! Check the 'plots' directory for generated images.")
