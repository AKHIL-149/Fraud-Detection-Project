"""
Generate sample fraud predictions to populate the database
Run this script to create test data for the dashboards
"""

import requests
import time
import random
from datetime import datetime

API_URL = "http://localhost:5000/api/predict"

# Sample transaction templates
SAMPLE_TRANSACTIONS = [
    # Low risk transactions
    {"Amount": 45.50, "Merchant State": "CA", "Merchant City": "San Francisco", "MCC": 5411, "Use Chip": "Chip Transaction"},
    {"Amount": 23.99, "Merchant State": "NY", "Merchant City": "New York", "MCC": 5912, "Use Chip": "Chip Transaction"},
    {"Amount": 67.25, "Merchant State": "TX", "Merchant City": "Austin", "MCC": 5814, "Use Chip": "Chip Transaction"},
    {"Amount": 15.00, "Merchant State": "FL", "Merchant City": "Miami", "MCC": 5541, "Use Chip": "Chip Transaction"},

    # Medium risk transactions
    {"Amount": 250.00, "Merchant State": "NV", "Merchant City": "Las Vegas", "MCC": 7995, "Use Chip": "Online Transaction"},
    {"Amount": 180.50, "Merchant State": "CA", "Merchant City": "Los Angeles", "MCC": 5611, "Use Chip": "Swipe Transaction"},
    {"Amount": 320.00, "Merchant State": "IL", "Merchant City": "Chicago", "MCC": 5651, "Use Chip": "Online Transaction"},

    # High risk transactions
    {"Amount": 999.99, "Merchant State": "DE", "Merchant City": "Wilmington", "MCC": 5932, "Use Chip": "Online Transaction"},
    {"Amount": 1500.00, "Merchant State": "NV", "Merchant City": "Las Vegas", "MCC": 7995, "Use Chip": "Swipe Transaction"},
    {"Amount": 2500.00, "Merchant State": "FL", "Merchant City": "Miami", "MCC": 5944, "Use Chip": "Online Transaction"},
]

def generate_predictions(count=50):
    """Generate sample predictions"""
    print(f"Generating {count} sample predictions...")
    print("=" * 80)

    successful = 0
    failed = 0

    for i in range(count):
        # Pick a random transaction template
        template = random.choice(SAMPLE_TRANSACTIONS)

        # Add some variation to the amount
        transaction = template.copy()
        transaction['Amount'] = transaction['Amount'] * random.uniform(0.8, 1.2)
        transaction['User'] = random.randint(1, 1000)
        transaction['Card'] = random.randint(1, 5000)

        try:
            response = requests.post(API_URL, json=transaction, timeout=5)

            if response.status_code == 200:
                result = response.json()
                fraud_status = "FRAUD" if result['is_fraud'] else "LEGIT"
                prob = result['fraud_probability']
                risk = result['risk_level']

                print(f"[{i+1}/{count}] {fraud_status} | ${transaction['Amount']:.2f} | "
                      f"Prob: {prob:.2%} | Risk: {risk.upper()}")
                successful += 1
            else:
                print(f"[{i+1}/{count}] ERROR: {response.status_code}")
                failed += 1

        except Exception as e:
            print(f"[{i+1}/{count}] FAILED: {str(e)}")
            failed += 1

        # Small delay to avoid overwhelming the API
        time.sleep(0.1)

    print("=" * 80)
    print(f"\nGeneration complete!")
    print(f"  Successful: {successful}")
    print(f"  Failed: {failed}")
    print(f"\nDatabase now contains real prediction data for dashboards.")
    print(f"You can now view the data in the Alerts, Monitoring, and Reports pages!")

if __name__ == "__main__":
    print("Sample Data Generator for Fraud Detection Dashboards")
    print("=" * 80)
    print("\nThis script will generate sample fraud predictions to populate your")
    print("dashboard with real data from the ML model.\n")

    try:
        # Test API connection
        response = requests.get("http://localhost:5000/api/health", timeout=2)
        if response.status_code != 200:
            print("ERROR: API is not responding correctly")
            print("Make sure the API server is running: python run_api.py")
            exit(1)

        print("API Connection: OK\n")

        # Get user input for number of predictions
        try:
            count = input("How many sample predictions to generate? (default: 50): ").strip()
            count = int(count) if count else 50
        except ValueError:
            count = 50

        generate_predictions(count)

    except requests.ConnectionError:
        print("\nERROR: Cannot connect to API server")
        print("Make sure the API is running on http://localhost:5000")
        print("\nStart the API with: python run_api.py")
    except KeyboardInterrupt:
        print("\n\nGeneration cancelled by user")
