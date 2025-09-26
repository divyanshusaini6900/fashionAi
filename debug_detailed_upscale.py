#!/usr/bin/env python3
"""
Detailed debug script for image upscaler
"""
import sys
import os
import logging
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent))

# Set up logging to see detailed output
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Specifically enable logging for the upscaler
logging.getLogger('app.services.image_upscaler').setLevel(logging.DEBUG)

logger = logging.getLogger(__name__)

def test_upscaler_detailed():
    """Test the image upscaler service with detailed logging"""
    try:
        from app.services.image_upscaler import ImageUpscaler
        import cv2
        import numpy as np
        
        logger.info("=== Testing ImageUpscaler Initialization ===")
        
        # Create upscaler instance
        upscaler = ImageUpscaler()
        logger.info(f"Upscaler model available: {upscaler.model_available}")
        
        if not upscaler.model_available:
            logger.error("Real-ESRGAN model is not available!")
            return False
            
        logger.info("=== Creating Test Image ===")
        # Create a simple test image (smaller for faster testing)
        test_img = np.random.randint(0, 255, (50, 50, 3), dtype=np.uint8)
        
        # Encode as JPEG bytes
        _, img_bytes = cv2.imencode('.jpg', test_img)
        img_bytes = img_bytes.tobytes()
        
        logger.info(f"Test image created: {len(img_bytes)} bytes, shape: {test_img.shape}")
        
        logger.info("=== Testing Upscaling ===")
        # Test upscaling with scale factor 2 (faster)
        upscaled_bytes = upscaler.upscale_image_bytes(img_bytes, scale=2)
        
        if upscaled_bytes:
            logger.info(f"Upscaling successful: {len(upscaled_bytes)} bytes")
            print("✅ Image upscaler is working correctly")
            return True
        else:
            logger.error("Upscaling failed - returned None")
            print("❌ Image upscaler failed")
            return False
            
    except Exception as e:
        logger.error(f"Error testing image upscaler: {e}", exc_info=True)
        print(f"❌ Error testing image upscaler: {e}")
        return False

if __name__ == "__main__":
    print("Detailed Debugging of Image Upscaler Service")
    print("=" * 50)
    success = test_upscaler_detailed()
    print("=" * 50)
    if success:
        print("🎉 All tests passed!")
    else:
        print("💥 Some tests failed!")