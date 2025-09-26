#!/usr/bin/env python3
"""
Script to pre-download the specific Real-ESRGAN model for deployment environments
Downloads only: https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth
"""
import os
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_realesrgan_model():
    """Download the specific Real-ESRGAN model"""
    try:
        logger.info("Attempting to import Real-ESRGAN...")
        from basicsr.archs.rrdbnet_arch import RRDBNet
        from realesrgan import RealESRGANer
        import cv2
        import numpy as np
        logger.info("Real-ESRGAN imported successfully")
        
        # Create a dummy image for testing
        dummy_img = np.random.randint(0, 255, (64, 64, 3), dtype=np.uint8)
        
        # Download and test the specific x4 model
        logger.info("Downloading RealESRGAN_x4plus model...")
        try:
            model_x4 = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=4)
            upsampler_x4 = RealESRGANer(
                scale=4,
                model_path='https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth',
                model=model_x4,
                tile=64,
                tile_pad=10,
                pre_pad=0,
                half=False
            )
            
            output, _ = upsampler_x4.enhance(dummy_img, outscale=4)
            logger.info("RealESRGAN_x4plus model downloaded and tested successfully")
            return True
        except Exception as e:
            logger.error(f"Error with RealESRGAN_x4plus model: {e}")
            return False
            
    except ImportError as e:
        logger.error(f"Failed to import Real-ESRGAN: {e}")
        logger.info("Please install with: pip install realesrgan")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("Downloading Real-ESRGAN Model")
    print("=" * 40)
    print("Downloading: RealESRGAN_x4plus.pth")
    print("URL: https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth")
    print("=" * 40)
    
    success = download_realesrgan_model()
    
    if success:
        print("✅ Real-ESRGAN model downloaded successfully")
        print("The model is now cached and ready for use in VM deployments")
    else:
        print("❌ Failed to download Real-ESRGAN model")
        print("Please check your network connection and try again")