import cv2
import numpy as np
import logging
from typing import Optional
from io import BytesIO
import os

# Try to import Real-ESRGAN
try:
    from basicsr.archs.rrdbnet_arch import RRDBNet
    from realesrgan import RealESRGANer
    REAL_ESRGAN_AVAILABLE = True
except ImportError as e:
    REAL_ESRGAN_AVAILABLE = False
    print(f"Real-ESRGAN not available: {e}")
    print("Please install with: pip install realesrgan")

logger = logging.getLogger(__name__)

class ImageUpscaler:
    def __init__(self):
        """Initialize the image upscaler service."""
        if not REAL_ESRGAN_AVAILABLE:
            logger.warning("Real-ESRGAN not available. Will use OpenCV for upscaling.")
        else:
            logger.info("Real-ESRGAN is available")
    
    def upscale_image_bytes(self, image_bytes: bytes, scale: int = 4) -> Optional[bytes]:
        """
        Upscale an image directly from bytes.
        
        Args:
            image_bytes (bytes): Image data as bytes
            scale (int): Upscaling factor (2 or 4)
            
        Returns:
            bytes: Upscaled image as bytes, or None if failed
        """
        if not image_bytes:
            logger.error("No image bytes provided for upscaling")
            return None
            
        try:
            # Convert bytes to numpy array
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)
            
            if img is None:
                raise ValueError("Could not decode image from bytes")
            
            # Use Real-ESRGAN if available, otherwise fallback to OpenCV
            if REAL_ESRGAN_AVAILABLE:
                logger.info("Attempting Real-ESRGAN upscaling")
                upscaled_img = self._upscale_with_realesrgan(img, scale)
                if upscaled_img is not None:
                    logger.info("Real-ESRGAN upscaling successful")
                else:
                    logger.warning("Real-ESRGAN upscaling failed, falling back to OpenCV")
                    upscaled_img = self._upscale_with_opencv(img, scale)
            else:
                logger.info("Using OpenCV fallback for upscaling")
                upscaled_img = self._upscale_with_opencv(img, scale)
            
            if upscaled_img is None:
                logger.error("All upscaling methods failed")
                return None
                
            # Convert back to bytes
            _, buffer = cv2.imencode('.jpg', upscaled_img)
            upscaled_bytes = buffer.tobytes()
            
            logger.info(f"Successfully upscaled image {scale}x")
            return upscaled_bytes
            
        except Exception as e:
            logger.error(f"Error upscaling image from bytes: {str(e)}", exc_info=True)
            return None
    
    def _upscale_with_realesrgan(self, img: np.ndarray, scale: int = 4) -> Optional[np.ndarray]:
        """
        Upscale image using Real-ESRGAN.
        
        Args:
            img (np.ndarray): Image as numpy array
            scale (int): Upscaling factor (2 or 4)
            
        Returns:
            np.ndarray: Upscaled image, or None if failed
        """
        try:
            logger.info(f"Initializing Real-ESRGAN model with scale {scale}")
            
            # Log environment info
            logger.info(f"HOME directory: {os.environ.get('HOME', 'Not set')}")
            logger.info(f"USER: {os.environ.get('USER', 'Not set')}")
            logger.info(f"Current working directory: {os.getcwd()}")
            
            # Initialize Real-ESRGAN model with better memory management
            model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=scale)
            upsampler = RealESRGANer(
                scale=scale,
                model_path=f'https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x{scale}plus.pth',
                model=model,
                tile=128,  # Reduced tile size for better memory management
                tile_pad=10,
                pre_pad=0,
                half=False
            )
            
            logger.info(f"Upscaling image {scale}x with Real-ESRGAN...")
            # Upscale the image
            output, _ = upsampler.enhance(img, outscale=scale)
            
            return output
        except Exception as e:
            logger.error(f"Error in Real-ESRGAN upscaling: {str(e)}", exc_info=True)
            # Try with smaller tile size as fallback
            try:
                logger.info("Trying with smaller tile size...")
                upsampler = RealESRGANer(
                    scale=scale,
                    model_path=f'https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x{scale}plus.pth',
                    model=model,
                    tile=64,  # Even smaller tile size
                    tile_pad=10,
                    pre_pad=0,
                    half=False
                )
                output, _ = upsampler.enhance(img, outscale=scale)
                return output
            except Exception as e2:
                logger.error(f"Second attempt with smaller tiles also failed: {str(e2)}", exc_info=True)
                return None
    
    def _upscale_with_opencv(self, img: np.ndarray, scale: int = 2) -> Optional[np.ndarray]:
        """
        Upscale image using OpenCV (fallback method).
        
        Args:
            img (np.ndarray): Image as numpy array
            scale (int): Upscaling factor
            
        Returns:
            np.ndarray: Upscaled image, or None if failed
        """
        try:
            # Get original dimensions
            height, width = img.shape[:2]
            
            # Upscale using interpolation
            upscaled = cv2.resize(img, (width*scale, height*scale), interpolation=cv2.INTER_LANCZOS4)
            
            logger.info(f"Upscaled image {scale}x using OpenCV")
            return upscaled
        except Exception as e:
            logger.error(f"Error in OpenCV upscaling: {str(e)}", exc_info=True)
            return None