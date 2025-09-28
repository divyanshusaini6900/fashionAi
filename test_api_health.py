#!/usr/bin/env python3
"""
Simple API health test for Fashion AI project
"""
import requests
import json
import time

def test_server_health():
    """Test if the server is responding."""
    try:
        print("🏥 Testing server health...")
        response = requests.get("http://127.0.0.1:8000/docs", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running and accessible!")
            return True
        else:
            print(f"❌ Server returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to connect to server: {e}")
        return False

def test_api_endpoint():
    """Test the API endpoint with minimal data."""
    try:
        print("\n🧪 Testing API endpoint health...")
        
        # Just test the endpoint exists
        url = "http://127.0.0.1:8000/api/v1/generate"
        
        # Send a simple HEAD request to check if endpoint exists
        response = requests.head(url, timeout=5)
        print(f"📡 API endpoint status: {response.status_code}")
        
        if response.status_code in [200, 405, 422]:  # These are expected for HEAD/OPTIONS
            print("✅ API endpoint is accessible!")
            return True
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to reach API endpoint: {e}")
        return False

def main():
    """Run all health tests."""
    print("🚀 Fashion AI API Health Check")
    print("=" * 50)
    
    # Test 1: Server Health
    server_ok = test_server_health()
    
    # Test 2: API Endpoint
    api_ok = test_api_endpoint()
    
    # Summary
    print("\n📊 Health Check Results:")
    print("=" * 50)
    print(f"🏥 Server Health: {'✅ PASS' if server_ok else '❌ FAIL'}")
    print(f"📡 API Endpoint: {'✅ PASS' if api_ok else '❌ FAIL'}")
    
    if server_ok and api_ok:
        print("\n🎉 All health checks passed! API is ready for testing.")
        print("💡 You can now run the full test: python tests\\run_api_test.py")
        return True
    else:
        print("\n⚠️  Some health checks failed. Please check server status.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)