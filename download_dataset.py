"""
Quick script to download the fraud detection dataset from Kaggle.

Prerequisites:
1. Install kaggle: pip install kaggle
2. Setup Kaggle API credentials:
   - Go to https://www.kaggle.com/settings
   - Click "Create New API Token"
   - Place kaggle.json in: C:\Users\<username>\.kaggle\kaggle.json

Usage:
    python download_dataset.py
"""

import os
import zipfile
import subprocess
import sys

def download_dataset():
    print("=" * 80)
    print("DOWNLOADING FRAUD DETECTION DATASET")
    print("=" * 80)

    # Check if kaggle is installed
    try:
        import kaggle
    except ImportError:
        print("\nKaggle package not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "kaggle"])
        import kaggle

    # Dataset details
    dataset_name = "ealtman2019/credit-card-transactions"
    download_path = "detection_data/"

    # Create directory if it doesn't exist
    os.makedirs(download_path, exist_ok=True)

    print(f"\nDataset: {dataset_name}")
    print(f"Destination: {download_path}")
    print("\nDownloading... (this may take several minutes for 2.2 GB)")

    try:
        # Download the dataset
        from kaggle.api.kaggle_api_extended import KaggleApi
        api = KaggleApi()
        api.authenticate()

        api.dataset_download_files(
            dataset_name,
            path=download_path,
            unzip=True
        )

        print("\n" + "=" * 80)
        print("DOWNLOAD COMPLETE")
        print("=" * 80)

        # List downloaded files
        files = os.listdir(download_path)
        csv_files = [f for f in files if f.endswith('.csv')]

        print("\nDownloaded files:")
        for f in csv_files:
            file_path = os.path.join(download_path, f)
            size_mb = os.path.getsize(file_path) / (1024 * 1024)
            print(f"  - {f} ({size_mb:.1f} MB)")

        # Verify required files
        required_files = [
            'credit_card_transactions-ibm_v2.csv',
            'sd254_cards.csv',
            'sd254_users.csv'
        ]

        missing_files = [f for f in required_files if f not in csv_files]

        if missing_files:
            print("\nWARNING: Missing required files:")
            for f in missing_files:
                print(f"  - {f}")
        else:
            print("\nAll required files downloaded successfully!")
            print("\nNext steps:")
            print("  1. python feature_engineering.py")
            print("  2. python model_training.py")
            print("  3. python test_api.py")

    except Exception as e:
        print(f"\nERROR: {e}")
        print("\nIf you see authentication errors:")
        print("1. Go to https://www.kaggle.com/settings")
        print("2. Click 'Create New API Token'")
        print("3. Place kaggle.json in: C:\\Users\\<username>\\.kaggle\\")
        print("\nAlternatively, download manually from:")
        print("https://www.kaggle.com/datasets/ealtman2019/credit-card-transactions")
        return False

    return True

if __name__ == "__main__":
    success = download_dataset()
    sys.exit(0 if success else 1)
