#!/usr/bin/env python3
"""
Test script for the aspect ratio and view-specific pose features
"""
import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
BASE_URL = "http://127.0.0.1:8000"
ENDPOINT = "/api/v1/generate/image"

def test_aspect_ratio_and_view_pose_features():
    """Test the aspect ratio and view-specific pose features"""
    
    # Get API key from environment
    api_key = os.getenv("SERVICE_API_KEY", "fashion-ai-service-key")
    
    # Test data with the exact request from the user
    test_data = {
        "inputImages": [
            {
                "url": "https://firebasestorage.googleapis.com/v0/b/irongetnow-57465.appspot.com/o/WhatsApp%20Image%202025-09-19%20at%2011.35.31_d5ceb091.jpg?alt=media&token=ee5c5967-37c6-456a-9de0-02bd93689ae3",
                "view": "front",
                "backgrounds": [0, 0, 1]
            }
        ],
        "productType": "general",
        "gender": "male",
        "text": "",
        "isVideo": False,
        "upscale": False,
        "numberOfOutputs": 1,
        "generateCsv": True,
        "aspectRatio": "9:16"  # Adding aspect ratio parameter
    }
    
    try:
        print("🚀 Sending Request to API with Aspect Ratio and View-Specific Pose Features")
        print("=" * 80)
        print("📝 REQUEST DETAILS:")
        print(f"   URL: {BASE_URL}{ENDPOINT}")
        print(f"   Method: POST")
        print(f"   API Key: {api_key[:10]}...{api_key[-10:]}")  # Show partial key for security
        print("   JSON Data:")
        print(json.dumps(test_data, indent=2))
        
        # Send the POST request with x-api-key header
        response = requests.post(
            f"{BASE_URL}{ENDPOINT}",
            json=test_data,
            headers={"x-api-key": api_key},
            timeout=180  # 3 minutes timeout
        )
        
        # Process response
        print(f"\n📡 RESPONSE:")
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ API Test SUCCESS!")
            response_data = response.json()
            
            print("\n📋 RESPONSE BODY (JSON):")
            print(json.dumps(response_data, indent=2))
            
            # Print key results
            print(f"\n📄 Summary:")
            print(f"   Request ID: {response_data.get('request_id', 'N/A')}")
            
            if 'image_variations' in response_data and response_data['image_variations']:
                print(f"   🖼️ Image Variations ({len(response_data['image_variations'])} found):")
                for i, variation in enumerate(response_data['image_variations'], 1):
                    print(f"     {i}. {variation}")
            else:
                print(f"   ℹ️ No image variations generated")
                
            if 'excel_report_url' in response_data and response_data['excel_report_url']:
                print(f"   📊 Excel Report: {response_data['excel_report_url']}")
            else:
                print(f"   ⚠️ No Excel report generated")
                
            if response_data.get('output_video_url'):
                print(f"   🎥 Video Generated: {response_data['output_video_url']}")
            else:
                print(f"   ℹ️ No video requested")
            
            print(f"\n🎉 Test completed successfully!")
            return True
            
        else:
            print("❌ API Test FAILED")
            try:
                error_data = response.json()
                print("\n📋 ERROR RESPONSE (JSON):")
                print(json.dumps(error_data, indent=2))
            except:
                print(f"\n📋 RAW ERROR:")
                print(response.text)
            return False

    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server.")
        print("💡 Make sure the server is running: python -m uvicorn app.main:app --reload")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing FashionModelingAI Aspect Ratio and View-Specific Pose Features")
    print("=" * 80)
    
    # Test with the specific request
    success = test_aspect_ratio_and_view_pose_features()
    
    print(f"\n{'✅ TEST PASSED' if success else '❌ TEST FAILED'}")