#!/usr/bin/env python3
"""
Test script for the image upscaler service
"""
import sys
import os
import logging
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent))

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_image_upscaler():
    """Test the image upscaler service"""
    try:
        from app.services.image_upscaler import ImageUpscaler
        import cv2
        import numpy as np
        
        # Create upscaler instance
        upscaler = ImageUpscaler()
        logger.info("ImageUpscaler initialized successfully")
        
        # Create a simple test image (100x100 RGB image)
        test_img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        
        # Encode as JPEG bytes
        _, img_bytes = cv2.imencode('.jpg', test_img)
        img_bytes = img_bytes.tobytes()
        
        logger.info(f"Test image created: {len(img_bytes)} bytes")
        
        # Test upscaling
        logger.info("Testing upscaling...")
        upscaled_bytes = upscaler.upscale_image_bytes(img_bytes, scale=2)
        
        if upscaled_bytes:
            logger.info(f"Upscaling successful: {len(upscaled_bytes)} bytes")
            print("✅ Image upscaler is working correctly")
            return True
        else:
            logger.error("Upscaling failed")
            print("❌ Image upscaler failed")
            return False
            
    except Exception as e:
        logger.error(f"Error testing image upscaler: {e}", exc_info=True)
        print(f"❌ Error testing image upscaler: {e}")
        return False

if __name__ == "__main__":
    print("Testing Image Upscaler Service")
    print("=" * 40)
    success = test_image_upscaler()
    print("=" * 40)
    if success:
        print("🎉 All tests passed!")
    else:
        print("💥 Some tests failed!")