import requests
import json
import os
from PIL import Image
import io

# --- Configuration ---
BASE_URL = "http://127.0.0.1:8000"
ENDPOINT = "/api/v1/generate"
TEST_IMAGES_DIR = "tests/test_data"

# Ensure your FastAPI server is running before executing this script.
# You can run it with: uvicorn app.main:app --reload

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

def run_api_test():
    """
    Sends a test request to the fashion modeling API with local images.
    Now supports both Gemini and Replicate APIs based on configuration.
    """
    print(f"🚀 Starting LOCAL API test against {BASE_URL}{ENDPOINT}")
    print("📍 Testing with LOCAL STORAGE (No AWS required)")
    print("🤖 API will use Gemini for image/video generation (configurable)")
    
    # Ensure test images exist
    ensure_test_images()

    # 1. Define the input data
    text_input = "woman dress, stylish, elegant, event wear"
    username = "Mene"  # Using your name
    product = "lengha"
    generate_video = "false"  # Set to "true" to test video generation (takes longer)
    
    # 2. Prepare the image files for the multipart/form-data request
    image_definitions = {
        "frontside": os.path.join(TEST_IMAGES_DIR, "ref1.jpg"),
        # "backside": os.path.join(TEST_IMAGES_DIR, "usp1.jpg"),
        # "sideview": os.path.join(TEST_IMAGES_DIR, "side.jpg"), # Optional
        "detailview": os.path.join(TEST_IMAGES_DIR, "usp1.jpg") # Optional
    }
    
    files_to_upload = {}
    try:
        for name, path in image_definitions.items():
            if not os.path.exists(path):
                # Frontside is required, others are optional.
                if name == "frontside":
                    print(f"❌ Error: Required image file not found at {path}")
                    return
                print(f"⚠️ Warning: Optional image file not found at {path}, skipping.")
                continue
            
            # The format for 'files' dict is:
            # 'field_name': ('filename', file_object, 'content_type')
            files_to_upload[name] = (os.path.basename(path), open(path, "rb"), "image/jpeg")

        if "frontside" not in files_to_upload:
            print("❌ Error: 'frontside' image is mandatory.")
            # Clean up any already opened files
            for _, file_tuple in files_to_upload.items():
                file_tuple[1].close()
            return

        print(f"✅ Prepared {len(files_to_upload)} images for upload: {list(files_to_upload.keys())}")
        print(f"📝 Text input: '{text_input}'")
        print(f"👤 Username: '{username}'")
        print(f"📦 Product: '{product}'")

        # 3. Send the POST request
        response = requests.post(
            f"{BASE_URL}{ENDPOINT}",
            files=files_to_upload,
            data={
                "text": text_input,
                "username": username,
                "product": product,
                "generate_video": generate_video
            },
            timeout=600  # Increased timeout for video generation
        )

        # 4. Clean up the opened files
        for _, file_tuple in files_to_upload.items():
            file_tuple[1].close()

        # 5. Process and print the response
        print(f"\nSTATUS CODE: {response.status_code}")
        
        if response.status_code == 200:
            print("\n✅ API Test Successful!")
            response_data = response.json()
            print(json.dumps(response_data, indent=2))

            # You can now use these URLs to access the generated files
            print(f"\n🔗 Access the generated image at: {response_data['output_image_url']}")
            if response_data.get('output_video_url'):
                print(f"🔗 Access the generated video at: {response_data['output_video_url']}")
            print(f"🔗 Access the generated Excel report at: {response_data['excel_report_url']}")
        else:
            print("\n❌ API Test Failed.")
            try:
                # Try to print JSON error detail if available
                print("Error Response:")
                print(json.dumps(response.json(), indent=2))
            except json.JSONDecodeError:
                # Print raw text if not JSON
                print(f"Raw Error Response:\n{response.text}")

    except requests.exceptions.ConnectionError as e:
        print("\n❌ Connection Error: Could not connect to the server.")
        print("Please make sure your FastAPI server is running on 'uvicorn app.main:app --reload'.")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")

if __name__ == "__main__":
    run_api_test() 