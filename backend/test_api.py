"""
Test script for standardized API response format
"""

import requests
import json

def test_standardized_response():
    """Test the standardized API response format"""
    
    # Test the health endpoint
    print("=== Testing Health Endpoint ===")
    try:
        response = requests.get("http://localhost:8000/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n=== Testing Standardized Response Format ===")
    print("Expected format:")
    expected = {
        "food": "pizza",
        "confidence": 0.87,
        "calories": 266,
        "protein": 11,
        "carbs": 33,
        "fat": 10,
        "unit": "per 100g"
    }
    print(json.dumps(expected, indent=2))
    
    print("\n=== Error Handling Test Cases ===")
    error_cases = [
        ("Invalid file type", "Should return 400"),
        ("File too large", "Should return 413"),
        ("Empty file", "Should return 400"),
        ("Invalid image", "Should return 400"),
        ("Internal error", "Should return 500")
    ]
    
    for case, expected_status in error_cases:
        print(f"- {case}: {expected_status}")

if __name__ == "__main__":
    test_standardized_response()
