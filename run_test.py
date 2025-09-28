#!/usr/bin/env python3
"""
Simple test script to verify the image generation with upscaling works
"""
import requests
import json
import time

# Configuration
BASE_URL = "http://127.0.0.1:8000"
ENDPOINT = "/api/v1/generate/image"

def test_simple_request():
    """Test a simple request to verify the endpoint works"""
    
    # Simple test data
    test_data = {
        "inputImages": [
            {
                "url": "https://firebasestorage.googleapis.com/v0/b/irongetnow-57465.appspot.com/o/WhatsApp%20Image%202025-09-19%20at%2012.36.01_0cca7d65.jpg?alt=media&token=704093fa-6d46-4006-a459-ed995cb423a2",
                "view": "front",
                "backgrounds": [0, 0, 1]
            }
        ],
        "productType": "general",
        "gender": "male",
        "text": "A modern t-shirt",
        "upscale": True
    }
    
    try:
        print("Sending test request...")
        response = requests.post(
            f"{BASE_URL}{ENDPOINT}",
            json=test_data,
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("SUCCESS! Response:")
            print(json.dumps(response.json(), indent=2))
            return True
        else:
            print("ERROR! Response:")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"Exception occurred: {e}")
        return False

if __name__ == "__main__":
    print("Testing image generation with upscaling...")
    success = test_simple_request()
    print(f"Test {'PASSED' if success else 'FAILED'}")