"""
Test script to verify the updated GET endpoint works with GCS-stored files.
"""

import requests
import json

def test_gcs_file_access():
    """Test the updated GET endpoint with a request_id that should have GCS-stored files."""
    
    base_url = "http://localhost:8000"
    
    print("=" * 70)
    print("TESTING UPDATED GET ENDPOINT WITH GCS-STORED FILES")
    print("=" * 70)
    
    # Test with the request_id from your example
    request_id = "816a2f03-999f-4b37-9250-4fe855495ab9"
    print(f"Testing with Request ID: {request_id}")
    print(f"This request_id should have files stored in GCS")
    
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
            
    elif response.status_code == 404:
        print("❌ No files found for this request_id")
        print(f"   Response: {response.json()}")
        print("\nThis could be because:")
        print("  1. The files are not actually stored in GCS with this request_id")
        print("  2. There was an error accessing GCS")
        print("  3. The request_id is incorrect")
        
    elif response.status_code == 400:
        print("❌ Invalid request_id format")
        print(f"   Response: {response.json()}")
        
    elif response.status_code == 500:
        print("❌ Server error when trying to access files")
        print(f"   Response: {response.json()}")
        
    else:
        print(f"❌ Request failed with status {response.status_code}")
        print(f"   Response: {response.text}")

def test_local_file_access():
    """Test the updated GET endpoint with a request_id that should have local files."""
    
    base_url = "http://localhost:8000"
    
    print("\n\n" + "=" * 70)
    print("TESTING UPDATED GET ENDPOINT WITH LOCAL FILES (FALLBACK)")
    print("=" * 70)
    
    # Test with a request_id that should have local files
    request_id = "4c1e1d10-a130-440a-aaae-290d10c286f4"
    print(f"Testing with Request ID: {request_id}")
    print(f"This request_id should have files stored locally")
    
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
            
    elif response.status_code == 404:
        print("❌ No files found for this request_id")
        print(f"   Response: {response.json()}")
        
    elif response.status_code == 400:
        print("❌ Invalid request_id format")
        print(f"   Response: {response.json()}")
        
    else:
        print(f"❌ Request failed with status {response.status_code}")
        print(f"   Response: {response.text}")

if __name__ == "__main__":
    test_gcs_file_access()
    test_local_file_access()
    
    print("\n" + "=" * 70)
    print("TESTING COMPLETE")
    print("=" * 70)