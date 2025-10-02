#!/usr/bin/env python3
"""
Test script for x-api-key authentication
This script demonstrates how to use the x-api-key header with the Fashion AI API
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
BASE_URL = "http://localhost:8000"
ENDPOINT = "/api/v1/generate/image"

def test_with_valid_api_key():
    """Test API with valid x-api-key header"""
    print("🧪 Testing with valid x-api-key header...")
    
    # Use the service API key from environment or default
    api_key = os.getenv("SERVICE_API_KEY", "fashion-ai-service-key")
    
    # Sample test data
    test_data = {
        "inputImages": [
            {
                "url": "https://example.com/frontside.jpg",
                "view": "frontside",
                "backgrounds": [0, 0, 1]
            }
        ],
        "productType": "dress",
        "gender": "female",
        "text": "Elegant evening dress",
        "isVideo": False,
        "upscale": True,
        "numberOfOutputs": 1,
        "aspectRatio": "9:16"
    }
    
    print(f"   Endpoint: POST {BASE_URL}{ENDPOINT}")
    print("   Headers:")
    print(f"     x-api-key: {api_key}")
    print("   JSON Data:")
    print(json.dumps(test_data, indent=2))
    
    # Send the POST request with x-api-key header
    try:
        response = requests.post(
            f"{BASE_URL}{ENDPOINT}",
            json=test_data,
            headers={"x-api-key": api_key},
            timeout=30
        )
        
        print(f"\n📡 RESPONSE:")
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ API Test SUCCESS!")
            response_data = response.json()
            print("\n📋 RESPONSE BODY (JSON):")
            print(json.dumps(response_data, indent=2))
        elif response.status_code == 401:
            print("❌ Authentication failed - Invalid API key")
            print(f"   Response: {response.text}")
        else:
            print(f"❌ API Test Failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Could not connect to the server.")
        print("   Please make sure your FastAPI server is running:")
        print("   python -m uvicorn app.main:app --reload")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_without_api_key():
    """Test API without x-api-key header (should fail in production mode)"""
    print("\n🧪 Testing without x-api-key header...")
    
    # Sample test data
    test_data = {
        "inputImages": [
            {
                "url": "https://example.com/frontside.jpg",
                "view": "frontside",
                "backgrounds": [0, 0, 1]
            }
        ],
        "productType": "dress",
        "gender": "female",
        "text": "Elegant evening dress",
        "isVideo": False,
        "upscale": True,
        "numberOfOutputs": 1,
        "aspectRatio": "9:16"
    }
    
    print(f"   Endpoint: POST {BASE_URL}{ENDPOINT}")
    print("   Headers: None (no x-api-key)")
    print("   JSON Data:")
    print(json.dumps(test_data, indent=2))
    
    # Send the POST request without x-api-key header
    try:
        response = requests.post(
            f"{BASE_URL}{ENDPOINT}",
            json=test_data,
            timeout=30
        )
        
        print(f"\n📡 RESPONSE:")
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ API Test SUCCESS! (API key not required in development mode)")
            response_data = response.json()
            print("\n📋 RESPONSE BODY (JSON):")
            print(json.dumps(response_data, indent=2))
        elif response.status_code == 401:
            print("❌ Authentication failed - API key required")
            print(f"   Response: {response.text}")
        else:
            print(f"❌ API Test Failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Could not connect to the server.")
        print("   Please make sure your FastAPI server is running:")
        print("   python -m uvicorn app.main:app --reload")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_with_invalid_api_key():
    """Test API with invalid x-api-key header"""
    print("\n🧪 Testing with invalid x-api-key header...")
    
    # Invalid API key
    api_key = "invalid-api-key"
    
    # Sample test data
    test_data = {
        "inputImages": [
            {
                "url": "https://example.com/frontside.jpg",
                "view": "frontside",
                "backgrounds": [0, 0, 1]
            }
        ],
        "productType": "dress",
        "gender": "female",
        "text": "Elegant evening dress",
        "isVideo": False,
        "upscale": True,
        "numberOfOutputs": 1,
        "aspectRatio": "9:16"
    }
    
    print(f"   Endpoint: POST {BASE_URL}{ENDPOINT}")
    print("   Headers:")
    print(f"     x-api-key: {api_key}")
    print("   JSON Data:")
    print(json.dumps(test_data, indent=2))
    
    # Send the POST request with invalid x-api-key header
    try:
        response = requests.post(
            f"{BASE_URL}{ENDPOINT}",
            json=test_data,
            headers={"x-api-key": api_key},
            timeout=30
        )
        
        print(f"\n📡 RESPONSE:")
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ API Test SUCCESS! (Unexpected - invalid key accepted)")
            response_data = response.json()
            print("\n📋 RESPONSE BODY (JSON):")
            print(json.dumps(response_data, indent=2))
        elif response.status_code == 401:
            print("✅ Authentication correctly failed - Invalid API key rejected")
            print(f"   Response: {response.text}")
        else:
            print(f"❌ API Test Failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Could not connect to the server.")
        print("   Please make sure your FastAPI server is running:")
        print("   python -m uvicorn app.main:app --reload")
    except Exception as e:
        print(f"❌ Error: {e}")

def show_usage():
    """Show usage instructions"""
    print("""
🔧 Fashion AI x-api-key Authentication Test

This script tests the x-api-key authentication feature for the Fashion AI API.

Requirements:
  1. Fashion AI server running locally:
     python -m uvicorn app.main:app --reload
     
  2. Valid API keys in .env file:
     - OPENAI_API_KEY
     - REPLICATE_API_TOKEN
     - SERVICE_API_KEY (for x-api-key authentication)

Endpoints that require x-api-key:
  - POST /api/v1/generate/image
  - POST /api/v1/generate

Valid x-api-key values:
  - Any of your service API keys (OPENAI_API_KEY, REPLICATE_API_TOKEN, GEMINI_API_KEY)
  - SERVICE_API_KEY value from .env file
  - "fashion-ai-service-key" (default if not specified)

Examples:
  python test_api_key_auth.py

Note: In development mode (default), API keys are not strictly required.
To enable strict API key validation, set ENVIRONMENT=production in your .env file.
    """)

if __name__ == "__main__":
    show_usage()
    test_with_valid_api_key()
    test_without_api_key()
    test_with_invalid_api_key()
    print("\n✅ All tests completed!")