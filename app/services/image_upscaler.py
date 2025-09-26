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
        self.upsampler = None
        self.model_available = False
        
        if not REAL_ESRGAN_AVAILABLE:
            logger.warning("Real-ESRGAN not available. Will use OpenCV for upscaling.")
        else:
            logger.info("Real-ESRGAN is available")
            # Define the local model path
            self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            self.model_path = os.path.join(self.base_dir, 'model', 'RealESRGAN_x4plus.pth')
            logger.info(f"Using local model path: {self.model_path}")
            
            # Check if local model file exists
            if not os.path.exists(self.model_path):
                logger.error(f"Local model file not found at {self.model_path}")
            else:
                logger.info("Local Real-ESRGAN model found")
                try:
                    # Initialize Real-ESRGAN model once
                    model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=4)
                    self.upsampler = RealESRGANer(
                        scale=4,
                        model_path=self.model_path,  # Using only local model path
                        model=model,
                        tile=128,  # Reduced tile size for better memory management
                        tile_pad=10,
                        pre_pad=0,
                        half=False
                    )
                    self.model_available = True
                    logger.info("Real-ESRGAN model initialized and ready to use")
                except Exception as e:
                    logger.error(f"Error initializing Real-ESRGAN model: {str(e)}", exc_info=True)
    
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
            if REAL_ESRGAN_AVAILABLE and self.model_available:
                logger.info("Attempting Real-ESRGAN upscaling with local model")
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
        Upscale image using Real-ESRGAN with local model only.
        
        Args:
            img (np.ndarray): Image as numpy array
            scale (int): Upscaling factor (2 or 4)
            
        Returns:
            np.ndarray: Upscaled image, or None if failed
        """
        try:
            logger.info(f"Upscaling image {scale}x with Real-ESRGAN (local model)...")
            # Use the pre-initialized upsampler
            output, _ = self.upsampler.enhance(img, outscale=scale)
            return output
        except Exception as e:
            logger.error(f"Error in Real-ESRGAN upscaling: {str(e)}", exc_info=True)
            # Try with smaller tile size as fallback
            try:
                logger.info("Trying with smaller tile size...")
                # Create a temporary upsampler with smaller tiles
                model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=4)
                upsampler = RealESRGANer(
                    scale=4,
                    model_path=self.model_path,  # Using only local model path
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