#!/usr/bin/env python3
"""
Modified API test with better timeout and progress tracking
"""
import requests
import json
import os
import time
from PIL import Image
import io

# Configuration
BASE_URL = "http://127.0.0.1:8000"
ENDPOINT = "/api/v1/generate"
TEST_IMAGES_DIR = "tests/test_data"

def create_test_image(color='red', size=(200, 200)):
    """Create a test image if real images are not available."""
    img = Image.new('RGB', size, color=color)
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)
    return img_byte_arr

def ensure_test_images():
    """Create test images if they don't exist."""
    os.makedirs(TEST_IMAGES_DIR, exist_ok=True)
    
    test_files = {
        "ref1.jpg": "red",
        "usp1.jpg": "blue"
    }
    
    for filename, color in test_files.items():
        filepath = os.path.join(TEST_IMAGES_DIR, filename)
        if not os.path.exists(filepath):
            print(f"📸 Creating test image: {filename}")
            img = Image.new('RGB', (200, 200), color=color)
            img.save(filepath, 'JPEG')

def run_simple_api_test():
    """
    Run a simplified API test with better progress tracking
    """
    print(f"🚀 Starting Fashion AI API Test")
    print(f"📍 Server: {BASE_URL}{ENDPOINT}")
    print(f"🤖 Using Gemini APIs for all processing")
    
    # Ensure test images exist
    ensure_test_images()

    # Test data - using your name as specified in memory
    text_input = "woman dress, stylish, elegant, event wear"
    username = "Mene"  # Using the name from memory
    product = "lengha"
    generate_video = "false"  # Start without video for faster testing
    
    # Prepare image files
    image_definitions = {
        "frontside": os.path.join(TEST_IMAGES_DIR, "ref1.jpg"),
        "detailview": os.path.join(TEST_IMAGES_DIR, "usp1.jpg")
    }
    
    files_to_upload = {}
    try:
        for name, path in image_definitions.items():
            if not os.path.exists(path):
                print(f"❌ Error: Required image file not found at {path}")
                return False
            files_to_upload[name] = (os.path.basename(path), open(path, "rb"), "image/jpeg")

        print(f"✅ Prepared {len(files_to_upload)} images")
        print(f"📝 Text: '{text_input}'")
        print(f"👤 Username: '{username}'")
        print(f"📦 Product: '{product}'")
        print("\n⏳ Sending request to API... (This may take 30-60 seconds)")
        
        start_time = time.time()
        
        # Send the POST request with progress tracking
        response = requests.post(
            f"{BASE_URL}{ENDPOINT}",
            files=files_to_upload,
            data={
                "text": text_input,
                "username": username,
                "product": product,
                "generate_video": generate_video
            },
            timeout=180  # 3 minutes timeout
        )
        
        elapsed_time = time.time() - start_time
        print(f"⏱️ Request completed in {elapsed_time:.1f} seconds")

        # Clean up file handles
        for _, file_tuple in files_to_upload.items():
            file_tuple[1].close()

        # Process response
        print(f"\n📡 STATUS CODE: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ API Test SUCCESS!")
            response_data = response.json()
            
            # Print key results
            print(f"\n📋 Test Results:")
            print(f"   Request ID: {response_data.get('request_id', 'N/A')}")
            
            if 'output_image_url' in response_data and response_data['output_image_url']:
                print(f"   ✅ Image Generated: {response_data['output_image_url']}")
            else:
                print(f"   ⚠️ No image generated")
                
            if 'excel_report_url' in response_data and response_data['excel_report_url']:
                print(f"   ✅ Excel Report: {response_data['excel_report_url']}")
            else:
                print(f"   ⚠️ No Excel report generated")
                
            if response_data.get('output_video_url'):
                print(f"   ✅ Video Generated: {response_data['output_video_url']}")
            else:
                print(f"   ℹ️ No video requested")
            
            # Show metadata if available
            if 'metadata' in response_data:
                metadata = response_data['metadata']
                if 'analysis' in metadata:
                    analysis = metadata['analysis']
                    if 'product_data' in analysis:
                        product_data = analysis['product_data']
                        print(f"\n🔍 Product Analysis (via Gemini):")
                        print(f"   SKU ID: {product_data.get('SKU_ID', 'N/A')}")
                        print(f"   Description: {product_data.get('Description', 'N/A')[:80]}...")
                        print(f"   Gender: {product_data.get('Gender', 'N/A')}")
                        print(f"   Occasion: {product_data.get('Occasion', 'N/A')}")
            
            print(f"\n🎉 Test completed successfully! All Gemini APIs are working.")
            return True
            
        else:
            print("❌ API Test FAILED")
            try:
                error_data = response.json()
                print("Error Details:")
                print(json.dumps(error_data, indent=2))
            except:
                print(f"Raw Error: {response.text}")
            return False

    except requests.exceptions.Timeout:
        print("❌ Request timed out. The API might be processing heavy operations.")
        print("💡 Try again or increase timeout value.")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server.")
        print("💡 Make sure the server is running: python -m uvicorn app.main:app --reload")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    finally:
        # Clean up any remaining file handles
        for _, file_tuple in files_to_upload.items():
            try:
                file_tuple[1].close()
            except:
                pass

if __name__ == "__main__":
    success = run_simple_api_test()
    print(f"\n{'✅ TEST PASSED' if success else '❌ TEST FAILED'}")
    exit(0 if success else 1)