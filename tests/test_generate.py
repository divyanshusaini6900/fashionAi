import os
import pytest
from fastapi.testclient import TestClient
from PIL import Image
import io

from app.main import app
from app.core.config import settings

client = TestClient(app)

@pytest.fixture
def test_image():
    """Create a test image"""
    img = Image.new('RGB', (100, 100), color='red')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_byte_arr = img_byte_arr.getvalue()
    return img_byte_arr

def test_generate_endpoint(test_image):
    """Test the generate endpoint with a single image"""
    
    # Prepare the files and data
    files = {
        'images': ('test.jpg', test_image, 'image/jpeg')
    }
    data = {
        'text': 'A red dress with floral pattern'
    }
    
    # Make the request
    response = client.post("/api/v1/generate", files=files, data=data)
    
    # Check response
    assert response.status_code == 200
    
    # Validate response structure
    json_response = response.json()
    assert "request_id" in json_response
    assert "status" in json_response
    assert json_response["num_images"] == 1
    
    # If generation completed
    if json_response["status"] == "completed":
        assert "output_image_url" in json_response
        assert "excel_report_url" in json_response
        
        # Verify URLs are accessible
        image_response = client.get(json_response["output_image_url"])
        assert image_response.status_code == 200
        
        excel_response = client.get(json_response["excel_report_url"])
        assert excel_response.status_code == 200

def test_generate_endpoint_validation():
    """Test input validation"""
    
    # Test without files
    response = client.post("/api/v1/generate", data={'text': 'test'})
    assert response.status_code == 400
    
    # Test without text
    files = {
        'images': ('test.txt', b'not an image', 'text/plain')
    }
    response = client.post("/api/v1/generate", files=files)
    assert response.status_code == 400
    
    # Test with invalid file type
    files = {
        'images': ('test.txt', b'not an image', 'text/plain')
    }
    data = {
        'text': 'test'
    }
    response = client.post("/api/v1/generate", files=files, data=data)
    assert response.status_code == 400
    assert "not an image" in response.json()["detail"] 