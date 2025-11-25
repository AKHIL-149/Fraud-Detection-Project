# Dataset Setup Instructions

This project uses the IBM Credit Card Transactions dataset for fraud detection. The large dataset files are not included in the repository due to their size.

## Required Data Files

### Primary Dataset
Download from Kaggle: [Credit Card Transactions Dataset](https://www.kaggle.com/datasets/ealtman2019/credit-card-transactions)

**Files needed:**
- `credit_card_transactions-ibm_v2.csv` (2.2 GB)
- `sd254_cards.csv` (476 KB)
- `sd254_users.csv` (220 KB)

### Where to Place Files
After downloading, place all CSV files in the `detection_data/` directory:

```
Fraud-Detection-Project/
└── detection_data/
    ├── credit_card_transactions-ibm_v2.csv
    ├── sd254_cards.csv
    └── sd254_users.csv
```

## Setup Steps

1. **Download the dataset from Kaggle**
   - You'll need a Kaggle account
   - Download the zip file and extract it

2. **Place files in detection_data directory**
   ```bash
   cd Fraud-Detection-Project
   cp /path/to/downloaded/*.csv detection_data/
   ```

3. **Verify files are in place**
   ```bash
   ls -lh detection_data/
   ```

   You should see:
   - credit_card_transactions-ibm_v2.csv (~2.2 GB)
   - sd254_cards.csv (~476 KB)
   - sd254_users.csv (~220 KB)

4. **Run the analysis pipeline**
   ```bash
   python data_analysis.py
   python feature_engineering.py
   python model_training.py
   ```

## Alternative: Use Sample Data

For quick testing without downloading the full dataset, you can use a sample:

```python
# In data_analysis.py, modify the load_data call:
analyzer.load_data(sample_size=10000)  # Use 10K rows instead of full dataset
```

## Dataset Information

**Source:** IBM Synthetic Financial Transactions
**Size:** 24+ million transactions
**Time Range:** 1999-2020
**Features:** 15 original fields
**Fraud Rate:** 0.13% (highly imbalanced)

**Citation:**
```
@dataset{credit_card_transactions_2021,
  author = {Altman, E.},
  title = {Credit Card Transactions},
  year = {2021},
  publisher = {Kaggle},
  url = {https://www.kaggle.com/datasets/ealtman2019/credit-card-transactions}
}
```

## Generated Files (Not in Repo)

After running the pipeline, these files will be generated locally:

**Feature-Engineered Data:**
- `detection_data/transactions_with_features.csv` (~58 MB)

**Trained Models:**
- `models/best_model.pkl` (664 KB)
- `models/preprocessor.pkl` (12 KB)
- `models/lightgbm.pkl` (352 KB)
- `models/xgboost.pkl` (280 KB)
- `models/random_forest.pkl` (1.6 MB)
- `models/logistic_regression.pkl` (4 KB)

These are excluded from version control via `.gitignore` but will be created when you run the training scripts.

## Troubleshooting

**Issue:** "File not found" error
- **Solution:** Ensure CSV files are in `detection_data/` directory

**Issue:** Out of memory error
- **Solution:** Use smaller sample size or increase system RAM

**Issue:** Long processing time
- **Solution:** Start with sample_size=100000 for initial testing

## Questions?

See [README.md](README.md) for full project documentation or [DATASET_ANALYSIS_REPORT.md](DATASET_ANALYSIS_REPORT.md) for detailed dataset analysis.
