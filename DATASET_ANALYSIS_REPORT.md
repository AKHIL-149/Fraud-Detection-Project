# Credit Card Transactions Dataset Analysis Report

## Executive Summary

This report presents a comprehensive analysis of the IBM credit card transactions dataset for fraud detection. The analysis covers 100,000 sample transactions from a total dataset of approximately 24 million transactions spanning from 1999 to 2020.

## Dataset Overview

### Basic Statistics
- **Total Transactions Analyzed**: 100,000 (sample)
- **Complete Dataset Size**: ~2.2 GB (24+ million transactions)
- **Date Range**: November 26, 1999 to February 28, 2020 (7,399 days / ~20 years)
- **Number of Features**: 15 original features + 1 derived datetime
- **Memory Footprint**: 32.59 MB (for sample)
- **Number of Users**: 2,000 unique users
- **Number of Cards**: 6,146 unique cards
- **Number of Merchants**: 2,172 unique merchants

### Data Structure

The dataset contains the following features:

1. **User** (int): User identifier
2. **Card** (int): Card identifier
3. **Year** (int): Transaction year
4. **Month** (int): Transaction month
5. **Day** (int): Transaction day
6. **Time** (string): Transaction time
7. **Amount** (float): Transaction amount in USD
8. **Use Chip** (string): Chip usage indicator (Swipe Transaction, Chip Transaction, Online Transaction)
9. **Merchant Name** (int): Obfuscated merchant identifier
10. **Merchant City** (string): Merchant city
11. **Merchant State** (string): Merchant state
12. **Zip** (float): Merchant zip code
13. **MCC** (int): Merchant Category Code
14. **Errors?** (string): Transaction errors
15. **Is Fraud?** (binary): Fraud indicator (0=No, 1=Yes)
16. **DateTime** (datetime): Derived full datetime field

## Fraud Distribution

### Class Distribution
- **Legitimate Transactions**: 99,874 (99.87%)
- **Fraudulent Transactions**: 126 (0.13%)
- **Class Imbalance Ratio**: 792.65:1

### Key Observations
This is a highly imbalanced dataset which is typical for fraud detection problems. The extreme imbalance means:
- Standard accuracy metrics will be misleading
- Need to use specialized techniques (SMOTE, class weights, stratified sampling)
- Focus on Precision, Recall, F1-Score, and AUC-ROC rather than accuracy
- May need to undersample majority class or oversample minority class

## Temporal Patterns

### Transaction Volume by Year
The dataset shows steady growth in transaction volume over time:
- **1999**: 79 transactions (dataset start)
- **2000-2001**: ~900 transactions per year
- **2002-2007**: Gradual increase from 3,198 to 4,716 transactions
- **2008-2019**: Stable volume between 4,985 and 6,415 transactions per year
- **2020**: 1,001 transactions (partial year, up to February)

### Hourly Transaction Patterns
Transaction activity shows distinct patterns:
- **Peak Hours**: 6 AM (15,201 transactions), 9 AM (11,770), 1 PM (8,805)
- **Low Activity**: 2 AM (99 transactions), 1 AM (187), 12 AM (267)
- **Business Hours**: Majority of transactions occur between 6 AM and 6 PM
- This pattern suggests primarily daytime/business hour activity

### Day of Week Distribution
Transactions are fairly evenly distributed across all days:
- Monday: 14,450
- Tuesday: 14,055
- Wednesday: 14,176
- Thursday: 14,333
- Friday: 14,475
- Saturday: 14,206
- Sunday: 14,305

No significant weekend drop-off, suggesting consistent consumer behavior throughout the week.

## Transaction Amount Analysis

### Amount Statistics
- **Mean**: $68.37
- **Median**: $46.52
- **Std Dev**: $130.31
- **Minimum**: -$500.00 (refunds/chargebacks)
- **Maximum**: $6,820.20

### Percentile Distribution
- **10th percentile**: $6.99 (small purchases)
- **25th percentile**: $18.19
- **50th percentile**: $46.52 (median transaction)
- **75th percentile**: $92.25
- **90th percentile**: $140.44
- **95th percentile**: $184.24
- **99th percentile**: $480.30

### Amount by Fraud Status
|               | Legitimate   | Fraudulent   |
|---------------|--------------|--------------|
| Mean          | $68.29       | $133.92      |
| Std Dev       | $129.76      | $356.59      |
| Median        | $46.51       | $71.42       |
| 75th %ile     | $92.19       | $155.80      |
| Maximum       | $6,820.20    | $3,750.60    |

**Key Finding**: Fraudulent transactions have:
- Higher mean amount (almost double)
- Much higher variance (more extreme values)
- Higher median (53% more than legitimate)
- This suggests fraudsters target higher value transactions

### Negative Amounts
- **Count**: 2,581 transactions (2.58%)
- **Interpretation**: Likely refunds, chargebacks, or reversals
- **Recommendation**: May need special handling in fraud detection model

## Merchant Analysis

### Merchant Distribution
- **Unique Merchants**: 2,172
- **Unique Cities**: 1,265
- **Unique States/Countries**: 93
- **Unique MCCs**: 108

### Top Merchant Categories (MCC)
1. **4784**: Financial Services (16,312 transactions - 16.3%)
2. **5411**: Grocery Stores (12,506 transactions - 12.5%)
3. **5912**: Drug Stores (7,991 transactions - 8.0%)
4. **5499**: Misc. Food Stores (7,100 transactions - 7.1%)
5. **5541**: Service Stations (6,250 transactions - 6.3%)

### Fraud Rate by MCC (minimum 10 transactions)
Highest risk merchant categories:
1. **5932**: Antique Shops (12.0% fraud rate)
2. **5045**: Computer/Software Stores (12.0% fraud rate)
3. **3006**: Air Carrier (10.0% fraud rate)
4. **5094**: Precious Stones/Metals (9.1% fraud rate)
5. **3008**: Credit Card Payments (7.1% fraud rate)

**Note**: Some high-risk categories are intuitively correct (online payments, high-value items)

## Geographic Analysis

### Top Merchant Cities
1. **ONLINE**: 21,635 transactions (21.6% - all online transactions)
2. **West Covina, CA**: 14,267 transactions
3. **San Francisco, CA**: 11,860 transactions
4. **La Verne, CA**: 10,874 transactions
5. **New York, NY**: 5,130 transactions

### State Distribution
- **California**: 55,086 transactions (55.1%)
- **New York**: 14,246 transactions (14.2%)
- **Texas**: 620 transactions (0.6%)
- **International**: Mexico (389), Italy (201), Poland (23), etc.

### Geographic Fraud Risk
- **Italy**: 21.4% fraud rate (43 fraudulent out of 201 transactions)
- **Ohio**: 0.56% fraud rate
- **New York**: 0.03% fraud rate
- **California**: 0.03% fraud rate

**Key Finding**: International transactions, especially to Italy, show significantly higher fraud rates.

## Missing Data

### Missing Value Analysis
| Column         | Missing Count | Percentage |
|----------------|---------------|------------|
| Errors?        | 98,293        | 98.3%      |
| Zip            | 23,494        | 23.5%      |
| Merchant State | 21,635        | 21.6%      |

### Observations
- **Errors? column**: Almost completely empty - likely only populated when errors occur
- **Zip/State missing**: Corresponds to online transactions (ONLINE merchant city)
- **No missing values** in critical fields (Amount, User, Card, Is Fraud?)

## User Demographics (from supplementary data)

### User Profile
- **Total Users**: 2,000
- **Age Range**: 43 to 81 years (sample)
- **Gender**: Mix of Male and Female
- **Credit Cards per User**: 1 to 5 cards
- **FICO Score Range**: 675 to 787 (sample)

### Geographic Distribution
Users primarily located in:
- California (La Verne, West Covina, San Francisco)
- New York (Little Neck, New York City)

### Financial Profile
- **Income levels**: Range from $33,483 to $249,925 per year
- **Debt levels**: Range from $196 to $202,328
- **Credit limits**: Vary widely by card

## Card Information

### Card Distribution
- **Total Cards**: 6,146
- **Card Brands**: Visa, Mastercard
- **Card Types**: Debit, Credit, Debit (Prepaid)
- **Chip Enabled**: Majority have chip capability
- **Dark Web Exposure**: Some cards flagged as "Card on Dark Web"

### Card Features Potentially Useful for Fraud Detection
- Account age (from Acct Open Date)
- Time since PIN change
- Credit limit
- Card type (debit vs credit)
- Chip capability vs actual chip usage
- Dark web exposure status

## Data Quality Assessment

### Strengths
1. **Complete fraud labels**: Every transaction labeled
2. **Rich temporal data**: 20 years of history
3. **Detailed merchant info**: MCC codes, location data
4. **Supplementary data**: User demographics and card details
5. **Natural values**: Minimal obfuscation (except merchant names)
6. **Large scale**: 24+ million transactions in full dataset

### Limitations
1. **Synthetic data**: Generated by simulation, not real transactions
2. **Merchant names obfuscated**: Numeric identifiers instead of names
3. **Geographic concentration**: Heavy California/New York bias
4. **Time range**: Data ends in early 2020, may not reflect current fraud patterns
5. **Class imbalance**: Extreme (793:1) requires special handling

## Key Findings and Insights

### Critical Observations for Fraud Detection

1. **Fraud Characteristics**:
   - Higher transaction amounts
   - Higher variance in amounts
   - Certain merchant categories (antique shops, computer stores, airlines)
   - International transactions (especially Italy)

2. **Temporal Patterns**:
   - Peak fraud hours need investigation
   - Day of week analysis for fraud patterns
   - Long-term trend analysis

3. **Feature Engineering Opportunities**:
   - Velocity features (transactions per hour/day)
   - Amount deviation from user's normal behavior
   - Geographic risk scores
   - Time since last transaction
   - MCC-based risk scores
   - Card age and usage patterns
   - Chip usage vs card capability mismatches

4. **Model Considerations**:
   - Must handle extreme class imbalance
   - Need to capture temporal patterns (LSTM/GRU)
   - Ensemble methods likely beneficial
   - Online learning for concept drift
   - Anomaly detection approaches

## Recommendations

### Immediate Actions
1. **Create stratified train/test split** preserving fraud rate
2. **Implement SMOTE or similar** for class balance
3. **Engineer temporal and behavioral features**
4. **Set up proper evaluation metrics** (Precision, Recall, F1, AUC-ROC)

### Feature Engineering Priorities
1. User-level aggregations (avg amount, txn frequency, typical MCC)
2. Card-level features (age, chip usage patterns, credit utilization)
3. Velocity features (transactions in last hour/day/week)
4. Geographic risk scores
5. Time-based features (hour, day, weekend, holiday)
6. Amount deviation features (vs user avg, vs MCC avg)
7. Merchant risk scores

### Modeling Strategy
1. **Baseline**: Random Forest with class weights
2. **Advanced**: XGBoost with SMOTE
3. **Deep Learning**: LSTM for sequence modeling
4. **Ensemble**: Combine multiple model predictions
5. **Online Learning**: Implement adaptive model updates

### Deployment Considerations
1. Real-time prediction latency requirements
2. Feature computation in streaming context
3. Model retraining frequency
4. Alert threshold optimization
5. False positive cost analysis

## Conclusion

The credit card transactions dataset is well-suited for building a fraud detection system. It provides:
- Sufficient volume for training
- Rich feature set for model development
- Realistic class imbalance
- Temporal patterns for concept drift detection

The main challenges are:
- Extreme class imbalance requiring specialized techniques
- Need for sophisticated feature engineering
- Computational requirements for full dataset
- Real-time deployment considerations

With proper feature engineering and modeling techniques, this dataset should support development of an effective adaptive fraud detection system as outlined in the project objectives.
