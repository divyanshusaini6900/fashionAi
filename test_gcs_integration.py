#!/usr/bin/env python3
"""
Test script to verify Google Cloud Storage integration
"""

import os
import io
from app.core.config import settings
from app.utils.gcs_helpers import get_gcs_client, upload_file_to_gcs

def test_gcs_integration():
    """Test GCS integration by uploading a simple test file"""
    
    # Check if GCS is configured
    if not settings.GCS_BUCKET_NAME:
        print("GCS_BUCKET_NAME not configured. Skipping GCS test.")
        return True
        
    if not settings.GOOGLE_APPLICATION_CREDENTIALS:
        print("GOOGLE_APPLICATION_CREDENTIALS not configured. Skipping GCS test.")
        return True
    
    try:
        # Test GCS client initialization
        print("Testing GCS client initialization...")
        client = get_gcs_client()
        print("✓ GCS client initialized successfully")
        
        # Test bucket access
        print("Testing bucket access...")
        bucket = client.bucket(settings.GCS_BUCKET_NAME)
        if not bucket.exists():
            print(f"✗ Bucket {settings.GCS_BUCKET_NAME} does not exist")
            return False
        print(f"✓ Bucket {settings.GCS_BUCKET_NAME} exists and is accessible")
        
        # Test file upload
        print("Testing file upload...")
        test_content = b"This is a test file for GCS integration."
        test_file = io.BytesIO(test_content)
        object_name = "test/test_file.txt"
        
        url = upload_file_to_gcs(test_file, object_name)
        print(f"✓ File uploaded successfully. Public URL: {url}")
        
        return True
        
    except Exception as e:
        print(f"✗ GCS integration test failed: {e}")
        return False

if __name__ == "__main__":
    print("Running GCS integration test...")
    success = test_gcs_integration()
    if success:
        print("\n✓ All GCS integration tests passed!")
    else:
        print("\n✗ GCS integration tests failed!")
        exit(1)