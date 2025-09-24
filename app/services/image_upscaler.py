import cv2
import numpy as np
import logging
from typing import Optional
from io import BytesIO

# Try to import Real-ESRGAN
try:
    from basicsr.archs.rrdbnet_arch import RRDBNet
    from realesrgan import RealESRGANer
    REAL_ESRGAN_AVAILABLE = True
except ImportError:
    REAL_ESRGAN_AVAILABLE = False
    print("Real-ESRGAN not available. Please install with: pip install realesrgan")

logger = logging.getLogger(__name__)

class ImageUpscaler:
    def __init__(self):
        """Initialize the image upscaler service."""
        if not REAL_ESRGAN_AVAILABLE:
            logger.warning("Real-ESRGAN not available. Will use OpenCV for upscaling.")
    
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
                upscaled_img = self._upscale_with_realesrgan(img, scale)
            else:
                upscaled_img = self._upscale_with_opencv(img, scale)
            
            if upscaled_img is None:
                return None
                
            # Convert back to bytes
            _, buffer = cv2.imencode('.jpg', upscaled_img)
            upscaled_bytes = buffer.tobytes()
            
            logger.info(f"Successfully upscaled image {scale}x")
            return upscaled_bytes
            
        except Exception as e:
            logger.error(f"Error upscaling image from bytes: {str(e)}")
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
            # Initialize Real-ESRGAN model
            model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=scale)
            upsampler = RealESRGANer(
                scale=scale,
                model_path=f'https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x{scale}plus.pth',
                model=model,
                tile=0,
                tile_pad=10,
                pre_pad=0,
                half=False
            )
            
            logger.info(f"Upscaling image {scale}x with Real-ESRGAN...")
            # Upscale the image
            output, _ = upsampler.enhance(img, outscale=scale)
            
            return output
        except Exception as e:
            logger.error(f"Error in Real-ESRGAN upscaling: {str(e)}")
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
            logger.error(f"Error in OpenCV upscaling: {str(e)}")
            return None