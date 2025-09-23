"""
Simple script to demonstrate the GET request functionality with an existing request_id.
"""

import requests
import json

def simple_get_demo():
    """Demonstrate the GET request functionality with an existing request_id."""
    
    base_url = "http://localhost:8000"
    
    print("=" * 70)
    print("FASHION AI DEMONSTRATION - GET REQUEST TO ACCESS FILES BY REQUEST_ID")
    print("=" * 70)
    
    # Use an existing request_id from the output directory
    request_id = "4c1e1d10-a130-440a-aaae-290d10c286f4"
    print(f"Using existing Request ID: {request_id}")
    
    # Make the GET request
    print(f"\nMaking GET request to: {base_url}/api/v1/files/{request_id}")
    response = requests.get(f"{base_url}/api/v1/files/{request_id}")
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("\n✅ SUCCESS! Files found for this request_id:")
        print(f"   Request ID: {result['request_id']}")
        print(f"   Total Files: {result['count']}")
        print("\n   Files:")
        for i, file_info in enumerate(result['files'], 1):
            print(f"     {i}. {file_info['filename']} ({file_info['type']})")
            print(f"        URL: {file_info['url']}")
            
        print("\n" + "-" * 50)
        print("You can access these files directly in your browser:")
        for i, file_info in enumerate(result['files'], 1):
            print(f"     {i}. {file_info['url']}")
            
    elif response.status_code == 404:
        print("❌ No files found for this request_id")
        print(f"   Response: {response.json()}")
        
    elif response.status_code == 400:
        print("❌ Invalid request_id format")
        print(f"   Response: {response.json()}")
        
    else:
        print(f"❌ Request failed with status {response.status_code}")
        print(f"   Response: {response.text}")

def test_invalid_request_id():
    """Test with an invalid request_id to show error handling."""
    
    base_url = "http://localhost:8000"
    
    print("\n\n" + "=" * 70)
    print("TESTING ERROR HANDLING - INVALID REQUEST_ID")
    print("=" * 70)
    
    # Test with an invalid request_id
    invalid_request_id = "not-a-valid-uuid"
    print(f"Using invalid Request ID: {invalid_request_id}")
    
    # Make the GET request
    print(f"\nMaking GET request to: {base_url}/api/v1/files/{invalid_request_id}")
    response = requests.get(f"{base_url}/api/v1/files/{invalid_request_id}")
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 400:
        print("✅ Correctly handled invalid request_id format")
        print(f"   Response: {response.json()}")
    else:
        print(f"Unexpected response: {response.status_code}")
        print(f"   Response: {response.text}")

def test_nonexistent_request_id():
    """Test with a valid but nonexistent request_id to show error handling."""
    
    base_url = "http://localhost:8000"
    
    print("\n\n" + "=" * 70)
    print("TESTING ERROR HANDLING - NONEXISTENT REQUEST_ID")
    print("=" * 70)
    
    # Test with a valid UUID format but nonexistent request_id
    nonexistent_request_id = "00000000-0000-0000-0000-000000000000"
    print(f"Using nonexistent Request ID: {nonexistent_request_id}")
    
    # Make the GET request
    print(f"\nMaking GET request to: {base_url}/api/v1/files/{nonexistent_request_id}")
    response = requests.get(f"{base_url}/api/v1/files/{nonexistent_request_id}")
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 404:
        print("✅ Correctly handled nonexistent request_id")
        print(f"   Response: {response.json()}")
    else:
        print(f"Unexpected response: {response.status_code}")
        print(f"   Response: {response.text}")

if __name__ == "__main__":
    simple_get_demo()
    test_invalid_request_id()
    test_nonexistent_request_id()
    
    print("\n" + "=" * 70)
    print("DEMONSTRATION COMPLETE")
    print("=" * 70)
    print("\nSUMMARY:")
    print("✅ Valid request_ids with existing files return file information")
    print("✅ Invalid request_id formats return 400 Bad Request")
    print("✅ Valid request_ids with no files return 404 Not Found")
    print("\nThe system allows you to access all generated files using just the request_id!")