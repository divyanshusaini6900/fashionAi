#!/usr/bin/env python3
"""
Test script to verify the schema changes
"""
import sys
import os
import json

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from schemas import GenerationResponse

def test_schema_changes():
    """Test that the schema changes are working correctly"""
    
    # Test data that matches the new schema
    test_data = {
        "request_id": "123e4567-e89b-12d3-a456-426614174000",
        "image_variations": [
            "http://localhost:8000/files/generated/123e4567-e89b-12d3-a456-426614174000/variation1.jpg",
            "http://localhost:8000/files/generated/123e4567-e89b-12d3-a456-426614174000/variation2.jpg"
        ],
        "upscaled_images": [  # Changed from single string to array
            "http://localhost:8000/files/generated/123e4567-e89b-12d3-a456-426614174000/upscaled_image.jpg"
        ],
        "output_video_url": None,
        "excel_report_url": "http://localhost:8000/files/generated/123e4567-e89b-12d3-a456-426614174000/report.xlsx",
        "metadata": {
            "processing_time": 45.2,
            "model_used": "stable-diffusion-v3"
        }
    }
    
    # Validate the data against the schema
    try:
        response = GenerationResponse(**test_data)
        print("✅ Schema validation passed!")
        print(f"Request ID: {response.request_id}")
        print(f"Number of image variations: {len(response.image_variations)}")
        print(f"Number of upscaled images: {len(response.upscaled_images)}")  # Changed
        print(f"Excel report URL: {response.excel_report_url}")
        return True
    except Exception as e:
        print(f"❌ Schema validation failed: {e}")
        return False

def test_without_upscaled_images():
    """Test the schema when upscale is False"""
    
    # Test data without upscaled_images (when upscale=False)
    test_data = {
        "request_id": "123e4567-e89b-12d3-a456-426614174000",
        "image_variations": [
            "http://localhost:8000/files/generated/123e4567-e89b-12d3-a456-426614174000/variation1.jpg",
            "http://localhost:8000/files/generated/123e4567-e89b-12d3-a456-426614174000/variation2.jpg"
        ],
        "upscaled_images": [],  # Now an empty array instead of None
        "output_video_url": None,
        "excel_report_url": "http://localhost:8000/files/generated/123e4567-e89b-12d3-a456-426614174000/report.xlsx",
        "metadata": {
            "processing_time": 45.2,
            "model_used": "stable-diffusion-v3",
            "upscaled": False
        }
    }
    
    # Validate the data against the schema
    try:
        response = GenerationResponse(**test_data)
        print("✅ Schema validation without upscaled images passed!")
        print(f"Request ID: {response.request_id}")
        print(f"Number of image variations: {len(response.image_variations)}")
        print(f"Number of upscaled images: {len(response.upscaled_images)}")  # Changed
        print(f"Excel report URL: {response.excel_report_url}")
        return True
    except Exception as e:
        print(f"❌ Schema validation without upscaled images failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing Schema Changes")
    print("=" * 40)
    
    success1 = test_schema_changes()
    print()
    success2 = test_without_upscaled_images()
    
    print("\n" + "=" * 40)
    if success1 and success2:
        print("🎉 All schema tests passed!")
    else:
        print("💥 Some schema tests failed!")