#!/usr/bin/env python3
"""
Debug script to verify Google Cloud Storage credentials
"""

import os
import json
from google.cloud import storage

def debug_gcs_credentials():
    """Debug GCS credentials and permissions"""
    
    # Load environment variables
    from app.core.config import settings
    
    print("Current Configuration:")
    print(f"USE_LOCAL_STORAGE: {settings.USE_LOCAL_STORAGE}")
    print(f"GCS_BUCKET_NAME: {settings.GCS_BUCKET_NAME}")
    print(f"GOOGLE_APPLICATION_CREDENTIALS: {settings.GOOGLE_APPLICATION_CREDENTIALS}")
    
    if settings.USE_LOCAL_STORAGE:
        print("\n⚠️  Using local storage, not GCS")
        return
    
    # Check if credentials file exists
    creds_file = settings.GOOGLE_APPLICATION_CREDENTIALS
    if not os.path.exists(creds_file):
        print(f"\n❌ Credentials file does not exist: {creds_file}")
        return
    
    print(f"\n✅ Credentials file exists: {creds_file}")
    
    # Read and display service account info
    try:
        with open(creds_file, 'r') as f:
            creds_data = json.load(f)
        
        print(f"Service Account Email: {creds_data.get('client_email', 'N/A')}")
        print(f"Project ID: {creds_data.get('project_id', 'N/A')}")
    except Exception as e:
        print(f"❌ Failed to read credentials file: {e}")
        return
    
    # Try to initialize GCS client
    try:
        print("\n🔄 Attempting to initialize GCS client...")
        client = storage.Client.from_service_account_json(creds_file)
        print("✅ GCS client initialized successfully")
        
        # Try to list buckets (requires minimal permissions)
        print("\n🔄 Attempting to list buckets...")
        buckets = list(client.list_buckets())
        print(f"✅ Successfully listed {len(buckets)} buckets")
        
        # Try to access the specific bucket
        print(f"\n🔄 Attempting to access bucket: {settings.GCS_BUCKET_NAME}")
        bucket = client.bucket(settings.GCS_BUCKET_NAME)
        
        # Check if bucket exists (requires storage.buckets.get permission)
        try:
            if bucket.exists():
                print(f"✅ Bucket {settings.GCS_BUCKET_NAME} exists")
            else:
                print(f"❌ Bucket {settings.GCS_BUCKET_NAME} does not exist")
        except Exception as e:
            print(f"❌ Failed to check if bucket exists: {e}")
            print("This usually means the service account doesn't have storage.buckets.get permission")
            
    except Exception as e:
        print(f"❌ Failed to initialize GCS client: {e}")
        return

if __name__ == "__main__":
    debug_gcs_credentials()