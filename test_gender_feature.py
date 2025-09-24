#!/usr/bin/env python3
"""
Test script for the gender-based clothing feature
"""
import requests
import json

# Configuration
BASE_URL = "http://127.0.0.1:8000"
ENDPOINT = "/api/v1/generate-with-background-array"

def test_male_model():
    """Test the gender feature with male model"""
    
    # Test data with male gender
    test_data = {
        "inputImages": [
            {
                "url": "https://firebasestorage.googleapis.com/v0/b/irongetnow-57465.appspot.com/o/WhatsApp%20Image%202025-09-19%20at%2012.36.01_0cca7d65.jpg?alt=media&token=704093fa-6d46-4006-a459-ed995cb423a2",
                "view": "front",
                "backgrounds": [1, 1, 1]  # 1 white, 1 plain, 1 random
            }
        ],
        "productType": "shirt",
        "gender": "male",  # Specify male gender
        "text": "Casual shirt for men",
        "isVideo": False,
        "upscale": True,
        "numberOfOutputs": 1,
        "generateCsv": True
    }
    
    try:
        print("🚀 Sending Request to API with Male Gender")
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
            
            if 'output_image_url' in response_data and response_data['output_image_url']:
                print(f"   ✅ Primary Image: {response_data['output_image_url']}")
            else:
                print(f"   ⚠️ No primary image generated")
                
            # Show all image variations
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

def test_female_model():
    """Test the gender feature with female model"""
    
    # Test data with female gender
    test_data = {
        "inputImages": [
            {
                "url": "https://firebasestorage.googleapis.com/v0/b/irongetnow-57465.appspot.com/o/WhatsApp%20Image%202025-09-19%20at%2012.36.01_0cca7d65.jpg?alt=media&token=704093fa-6d46-4006-a459-ed995cb423a2",
                "view": "front",
                "backgrounds": [1, 1, 1]  # 1 white, 1 plain, 1 random
            }
        ],
        "productType": "dress",
        "gender": "female",  # Specify female gender
        "text": "Elegant dress for women",
        "isVideo": False,
        "upscale": True,
        "numberOfOutputs": 1,
        "generateCsv": True
    }
    
    try:
        print("🚀 Sending Request to API with Female Gender")
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
            
            if 'output_image_url' in response_data and response_data['output_image_url']:
                print(f"   ✅ Primary Image: {response_data['output_image_url']}")
            else:
                print(f"   ⚠️ No primary image generated")
                
            # Show all image variations
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

def test_invalid_gender():
    """Test the gender feature with invalid gender"""
    
    # Test data with invalid gender
    test_data = {
        "inputImages": [
            {
                "url": "https://firebasestorage.googleapis.com/v0/b/irongetnow-57465.appspot.com/o/WhatsApp%20Image%202025-09-19%20at%2012.36.01_0cca7d65.jpg?alt=media&token=704093fa-6d46-4006-a459-ed995cb423a2",
                "view": "front",
                "backgrounds": [1, 0, 0]  # 1 white, 0 plain, 0 random
            }
        ],
        "productType": "general",
        "gender": "other",  # Invalid gender
        "text": "Test product",
        "isVideo": False,
        "upscale": True,
        "numberOfOutputs": 1,
        "generateCsv": True
    }
    
    try:
        print("🚀 Sending Request to API with Invalid Gender")
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
            timeout=180  # 3 minutes timeout
        )
        
        # Process response
        print(f"\n📡 RESPONSE:")
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 400:
            print("✅ Invalid gender correctly rejected!")
            try:
                error_data = response.json()
                print("\n📋 ERROR RESPONSE (JSON):")
                print(json.dumps(error_data, indent=2))
            except:
                print(f"\n📋 RAW ERROR:")
                print(response.text)
            return True
        else:
            print("❌ Invalid gender was not rejected")
            print("📋 RESPONSE:")
            try:
                response_data = response.json()
                print(json.dumps(response_data, indent=2))
            except:
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
    print("🧪 Testing FashionModelingAI Gender-Based Clothing Feature")
    print("=" * 60)
    
    # Test with male model
    print("\n Test 1: Male Model")
    success1 = test_male_model()
    
    # Test with female model
    print("\n Test 2: Female Model")
    success2 = test_female_model()
    
    # Test with invalid gender
    print("\n Test 3: Invalid Gender")
    success3 = test_invalid_gender()
    
    print(f"\n{'✅ ALL TESTS PASSED' if all([success1, success2, success3]) else '❌ SOME TESTS FAILED'}")