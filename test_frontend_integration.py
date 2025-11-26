"""
Test frontend-backend integration

Verifies that the Streamlit frontend can communicate with the Flask API.
"""

import requests
import time

API_URL = "http://localhost:5000/api"
FRONTEND_URL = "http://localhost:8501"

def test_api_health():
    """Test if API is responding"""
    print("Testing API health...")
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("[PASS] API is healthy")
            print(f"  - Status: {data.get('status')}")
            print(f"  - Model loaded: {data.get('model_loaded')}")
            return True
        else:
            print(f"[FAIL] API returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"[FAIL] Cannot connect to API: {e}")
        return False

def test_frontend():
    """Test if frontend is responding"""
    print("\nTesting frontend...")
    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        if response.status_code == 200:
            print(f"[PASS] Frontend is accessible at {FRONTEND_URL}")
            return True
        else:
            print(f"[FAIL] Frontend returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"[FAIL] Cannot connect to frontend: {e}")
        print(f"  Make sure Streamlit is running: streamlit run frontend/app.py")
        return False

def test_prediction():
    """Test making a prediction through the API"""
    print("\nTesting fraud prediction...")
    try:
        transaction = {
            "Amount": 150.75,
            "Merchant State": "CA",
            "Merchant City": "San Francisco",
            "MCC": 5411,
            "Use Chip": "Chip Transaction"
        }

        response = requests.post(
            f"{API_URL}/predict",
            json=transaction,
            timeout=10
        )

        if response.status_code == 200:
            result = response.json()
            print("[PASS] Prediction successful")
            print(f"  - Is Fraud: {result.get('is_fraud')}")
            print(f"  - Fraud Probability: {result.get('fraud_probability'):.4%}")
            print(f"  - Risk Level: {result.get('risk_level')}")
            print(f"  - Recommendation: {result.get('recommendation')}")
            return True
        else:
            print(f"[FAIL] Prediction failed with status code: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    except Exception as e:
        print(f"[FAIL] Prediction error: {e}")
        return False

def test_model_info():
    """Test model info endpoint"""
    print("\nTesting model info...")
    try:
        response = requests.get(f"{API_URL}/model/info", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("[PASS] Model info retrieved")
            print(f"  - Model type: {data.get('model_type')}")
            print(f"  - Version: {data.get('version')}")
            print(f"  - Loaded at: {data.get('loaded_at')}")
            return True
        else:
            print(f"[FAIL] Model info request failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"[FAIL] Model info error: {e}")
        return False

def main():
    """Run all integration tests"""
    print("=" * 80)
    print("FRONTEND-BACKEND INTEGRATION TEST")
    print("=" * 80)
    print()

    results = {
        "API Health": test_api_health(),
        "Frontend Access": test_frontend(),
        "Fraud Prediction": test_prediction(),
        "Model Info": test_model_info()
    }

    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    passed = sum(results.values())
    total = len(results)

    for test_name, passed_test in results.items():
        status = "[PASS]" if passed_test else "[FAIL]"
        print(f"{test_name}: {status}")

    print()
    print(f"Total: {passed}/{total} tests passed")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    print()

    if passed == total:
        print("[SUCCESS] All integration tests passed!")
        print()
        print("You can now use the dashboard:")
        print(f"  Frontend: {FRONTEND_URL}")
        print(f"  API: {API_URL}")
    else:
        print("[ERROR] Some tests failed. Please check the errors above.")
        print()
        print("Make sure both servers are running:")
        print("  1. API: python run_api.py")
        print("  2. Frontend: streamlit run frontend/app.py")

    print("=" * 80)

if __name__ == "__main__":
    main()
