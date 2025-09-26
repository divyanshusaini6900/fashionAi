#!/usr/bin/env python3
"""
Test script to verify local Real-ESRGAN model usage
"""
import os
import sys
import logging
import cv2
import numpy as np

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from services.image_upscaler import ImageUpscaler

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_local_model():
    """Test the local Real-ESRGAN model"""
    # Create a simple test image (64x64 random image)
    test_img = np.random.randint(0, 255, (64, 64, 3), dtype=np.uint8)
    
    # Encode as JPEG bytes
    _, buffer = cv2.imencode('.jpg', test_img)
    image_bytes = buffer.tobytes()
    
    logger.info(f"Test image size: {len(image_bytes)} bytes")
    
    # Initialize upscaler
    upscaler = ImageUpscaler()
    
    # Test upscaling
    logger.info("Testing image upscaling with local model...")
    upscaled_bytes = upscaler.upscale_image_bytes(image_bytes, scale=4)
    
    if upscaled_bytes:
        logger.info(f"Upscaling successful! Upscaled image size: {len(upscaled_bytes)} bytes")
        print("✅ Local model test passed!")
        return True
    else:
        logger.error("Upscaling failed!")
        print("❌ Local model test failed!")
        return False

if __name__ == "__main__":
    print("Testing local Real-ESRGAN model usage")
    print("=" * 40)
    success = test_local_model()
    if success:
        print("\n🎉 The local model is working correctly!")
    else:
        print("\n💥 There was an issue with the local model.")