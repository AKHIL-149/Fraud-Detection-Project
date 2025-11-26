"""
API Testing Script
Tests the fraud detection API endpoints to verify functionality
"""

import requests
import json
from datetime import datetime
import time

BASE_URL = 'http://localhost:5000'

def test_health_check():
    """Test health check endpoint"""
    print("\n" + "=" * 80)
    print("TEST: Health Check")
    print("=" * 80)

    response = requests.get(f'{BASE_URL}/api/health')
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    assert response.status_code == 200
    assert response.json()['status'] == 'healthy'
    print("PASSED")

def test_single_prediction():
    """Test single transaction prediction"""
    print("\n" + "=" * 80)
    print("TEST: Single Transaction Prediction")
    print("=" * 80)

    # Test case 1: Low risk transaction
    transaction = {
        'Amount': 45.50,
        'Merchant State': 'CA',
        'Merchant City': 'San Francisco',
        'MCC': 5411,
        'Use Chip': 'Chip Transaction'
    }

    print("Test Case 1: Low Risk Transaction")
    print(f"Request: {json.dumps(transaction, indent=2)}")

    response = requests.post(f'{BASE_URL}/api/predict', json=transaction)
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    assert response.status_code == 200
    assert 'fraud_probability' in response.json()
    print("PASSED")

    # Test case 2: High risk transaction
    print("\n" + "-" * 80)
    print("Test Case 2: High Risk Transaction")

    high_risk_transaction = {
        'Amount': 1500.00,
        'Merchant State': 'Italy',
        'Merchant City': 'ONLINE',
        'MCC': 5932,  # Antique shop (high risk)
        'Use Chip': 'Online Transaction'
    }

    print(f"Request: {json.dumps(high_risk_transaction, indent=2)}")

    response = requests.post(f'{BASE_URL}/api/predict', json=high_risk_transaction)
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    assert response.status_code == 200
    print("PASSED")

def test_batch_prediction():
    """Test batch transaction prediction"""
    print("\n" + "=" * 80)
    print("TEST: Batch Prediction")
    print("=" * 80)

    transactions = [
        {
            'transaction_id': 'txn_001',
            'Amount': 25.00,
            'Merchant State': 'CA'
        },
        {
            'transaction_id': 'txn_002',
            'Amount': 500.00,
            'Merchant State': 'Italy',
            'MCC': 5932
        },
        {
            'transaction_id': 'txn_003',
            'Amount': 75.00,
            'Merchant State': 'NY'
        }
    ]

    request_data = {'transactions': transactions}
    print(f"Request: {json.dumps(request_data, indent=2)}")

    response = requests.post(f'{BASE_URL}/api/predict/batch', json=request_data)
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    assert response.status_code == 200
    assert len(response.json()['predictions']) == 3
    assert response.json()['total'] == 3
    print("PASSED")

def test_model_info():
    """Test model info endpoint"""
    print("\n" + "=" * 80)
    print("TEST: Model Info")
    print("=" * 80)

    response = requests.get(f'{BASE_URL}/api/model/info')
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    assert response.status_code == 200
    assert 'model_type' in response.json()
    print("PASSED")

def test_error_handling():
    """Test API error handling"""
    print("\n" + "=" * 80)
    print("TEST: Error Handling")
    print("=" * 80)

    # Test missing required field
    print("Test Case: Missing Required Field")
    response = requests.post(f'{BASE_URL}/api/predict', json={})
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    assert response.status_code == 400
    print("PASSED")

    # Test invalid endpoint
    print("\nTest Case: Invalid Endpoint")
    response = requests.get(f'{BASE_URL}/api/invalid')
    print(f"Status Code: {response.status_code}")

    assert response.status_code == 404
    print("PASSED")

def run_all_tests():
    """Run all API tests"""
    print("\n" + "=" * 80)
    print("FRAUD DETECTION API TEST SUITE")
    print("=" * 80)
    print(f"Testing API at: {BASE_URL}")
    print(f"Started at: {datetime.now()}")

    tests = [
        test_health_check,
        test_model_info,
        test_single_prediction,
        test_batch_prediction,
        test_error_handling
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"\nFAILED: {str(e)}")
            failed += 1

    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Total Tests: {len(tests)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {(passed/len(tests)*100):.1f}%")
    print(f"Completed at: {datetime.now()}")
    print("=" * 80)

if __name__ == '__main__':
    print("\nMake sure the API server is running:")
    print("  python run_api.py")
    print("\nWaiting 3 seconds before starting tests...")
    time.sleep(3)

    try:
        run_all_tests()
    except requests.exceptions.ConnectionError:
        print("\nERROR: Could not connect to API server")
        print("Please start the server first: python run_api.py")
    except Exception as e:
        print(f"\nERROR: {str(e)}")
