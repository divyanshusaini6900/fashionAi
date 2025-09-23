#!/usr/bin/env python3
"""
Script to validate environment configuration for FashionModelingAI
"""

import os
from app.core.config import settings

def validate_environment():
    """Validate that all required environment variables are set"""
    
    print("Validating FashionModelingAI environment configuration...")
    print("=" * 60)
    
    # Check API keys
    required_keys = ['OPENAI_API_KEY', 'REPLICATE_API_TOKEN', 'GEMINI_API_KEY']
    missing_keys = []
    
    for key in required_keys:
        value = getattr(settings, key, None)
        if not value:
            missing_keys.append(key)
            print(f"❌ {key}: NOT SET")
        else:
            print(f"✅ {key}: SET (length: {len(value)})")
    
    # Check storage configuration
    print("\nStorage Configuration:")
    if settings.USE_LOCAL_STORAGE:
        print("✅ Using Local Storage")
        print(f"   Local Base URL: {settings.LOCAL_BASE_URL}")
    else:
        print("☁️  Using Cloud Storage")
        if settings.GCS_BUCKET_NAME:
            print(f"   GCS Bucket: {settings.GCS_BUCKET_NAME}")
            if settings.GOOGLE_APPLICATION_CREDENTIALS:
                print(f"   GCS Credentials: {settings.GOOGLE_APPLICATION_CREDENTIALS}")
            else:
                print("   ⚠️  GCS Credentials: NOT SET")
        else:
            print("   ⚠️  No cloud storage configured, will use local storage as fallback")
    
    # Summary
    print("\n" + "=" * 60)
    if missing_keys:
        print(f"❌ Validation FAILED. Missing required API keys: {', '.join(missing_keys)}")
        print("\nPlease set these environment variables in your .env file.")
        return False
    else:
        print("✅ Validation PASSED. All required environment variables are set.")
        return True

if __name__ == "__main__":
    success = validate_environment()
    if not success:
        exit(1)