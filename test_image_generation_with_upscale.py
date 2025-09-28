#!/usr/bin/env python3
"""
Test script for image generation with upscaling
"""
import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
ENDPOINT = "/api/v1/generate/image"

def test_image_generation_with_upscale():
    """Test image generation with upscaling enabled"""
    
    # Test data with background arrays for single viewdw
    test_data = {
        "inputImages": [
            {
                "url": "https://firebasestorage.googleapis.com/v0/b/irongetnow-57465.appspot.com/o/WhatsApp%20Image%202025-09-19%20at%2011.35.31_d5ceb091.jpg?alt=media&token=ee5c5967-37c6-456a-9de0-02bd93689ae3",
                "view": "front",
                "backgrounds": [0, 0, 1]  # 1 random background
            }
        ],
        "productType": "general",
        "gender": "male",
        "text": "",
        "isVideo": False,
        "upscale": False,  # Enable upscaling
        "numberOfOutputs": 1,
        "generateCsv": True,
    }
    
    try:
        print("🚀 Sending Request to API for Image Generation with Upscaling")
        print("=" * 60)
        print("📝 REQUEST DETAILS:")
        print(f"   URL: {BASE_URL}{ENDPOINT}")
        print(f"   Method: POST")
        print("   JSON Data:")
        print(json.dumps(test_data, indent=2))
        
        # Send the POST request
        response = requests.post(
            f"{BASE_URL}{ENDPOINT}",
            json=test_data,
            timeout=800  # 3 minutes timeout
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
            
            # Show all image variations
            if 'image_variations' in response_data and response_data['image_variations']:
                print(f"   🖼️ Image Variations ({len(response_data['image_variations'])} found):")
                for i, variation in enumerate(response_data['image_variations'], 1):
                    print(f"     {i}. {variation}")
            else:
                print(f"   ℹ️ No image variations generated")
                
            # Show all upscaled images
            if 'upscale_image' in response_data and response_data['upscale_image']:
                print(f"   🔍 Upscaled Images ({len(response_data['upscale_image'])} found):")
                for i, upscaled in enumerate(response_data['upscale_image'], 1):
                    print(f"     {i}. {upscaled}")
            else:
                print(f"   ℹ️ No upscaled images generated")
                
            # Check if images were upscaled
            metadata = response_data.get('metadata', {})
            if metadata.get('upscaled'):
                print(f"   📈 Images were upscaled: ✅")
            else:
                print(f"   📈 Images were upscaled: ❌")
                
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
    print("🧪 Testing FashionModelingAI Image Generation with Upscaling")
    print("=" * 60)
    
    # Test with single view image
    success = test_image_generation_with_upscale()
    
    print(f"\n{'✅ TEST PASSED' if success else '❌ TEST FAILED'}")