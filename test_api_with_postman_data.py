#!/usr/bin/env python3
"""
Test script that demonstrates how to use the API with the same data 
that would be sent from Postman
"""
import requests
import os
import json

# Configuration
BASE_URL = "http://127.0.0.1:8000"
ENDPOINT = "/api/v1/generate"

def test_api_with_sample_data():
    """Test the API with sample data similar to what Postman would send"""
    
    # Test data
    text_input = "woman dress, stylish, elegant, event wear"
    username = "test_user"
    product = "dress"
    generate_video = False
    number_of_outputs = 1
    aspect_ratio = "9:16"  # New parameter
    
    # Prepare image files (using the test images that come with the project)
    test_images_dir = "tests/test_data"
    
    # Check if test images exist
    frontside_path = os.path.join(test_images_dir, "5.jpg")
    # detailview_path = os.path.join(test_images_dir, "usp1.jpg")
    
    if not os.path.exists(frontside_path):
        print(f"❌ Error: Required image file not found at {frontside_path}")
        print("Please make sure the test images exist in the tests/test_data directory")
        return False
        
    # if not os.path.exists(detailview_path):
    #     print(f"❌ Error: Required image file not found at {detailview_path}")
    #     print("Please make sure the test images exist in the tests/test_data directory")
    #     return False
    
    try:
        # Open the image files
        files = {
            'frontside': ('ref1.jpg', open(frontside_path, 'rb'), 'image/jpeg'),
            # 'detailview': ('usp1.jpg', open(detailview_path, 'rb'), 'image/jpeg'),
        }
        
        # Prepare form data
        data = {
            'text': text_input,
            'username': username,
            'product': product,
            'generate_video': str(generate_video).lower(),
            'numberOfOutputs': str(number_of_outputs),
            'aspectRatio': aspect_ratio  # New parameter
        }
        
        print("🚀 Sending Request to API")
        print("=" * 40)
        print("📝 REQUEST DETAILS:")
        print(f"   URL: {BASE_URL}{ENDPOINT}")
        print(f"   Method: POST")
        print("   Form Data:")
        for key, value in data.items():
            print(f"     {key}: {value}")
        print("   Files:")
        print(f"     frontside: {frontside_path}")
        # print(f"     detailview: {detailview_path}")
        
        # Send the POST request
        response = requests.post(
            f"{BASE_URL}{ENDPOINT}",
            files=files,
            data=data,
            timeout=180  # 3 minutes timeout
        )
        
        # Clean up file handles
        for _, file_tuple in files.items():
            file_tuple[1].close()
        
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
            
            # Explain the numberOfOutputs behavior
            print(f"\nℹ️  Note about numberOfOutputs={number_of_outputs}:")
            print(f"   The application generates a primary image plus lifestyle variations.")
            print(f"   numberOfOutputs controls how many lifestyle variations are created.")
            print(f"   Even with numberOfOutputs=1, you'll get at least 1 lifestyle variation.")
            
            print(f"\n📐 Aspect Ratio: {aspect_ratio}")
            print(f"   All generated images will use the {aspect_ratio} aspect ratio.")
            
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
    print("🧪 Testing FashionModelingAI API")
    print("=" * 40)
    success = test_api_with_sample_data()
    print(f"\n{'✅ TEST PASSED' if success else '❌ TEST FAILED'}")