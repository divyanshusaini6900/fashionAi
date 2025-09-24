import cv2
import numpy as np
from PIL import Image
import argparse
import os

try:
    from basicsr.archs.rrdbnet_arch import RRDBNet
    from realesrgan import RealESRGANer
    REAL_ESRGAN_AVAILABLE = True
except ImportError:
    REAL_ESRGAN_AVAILABLE = False
    print("Real-ESRGAN not available. Please install with: pip install realesrgan")

def upscale_saree_image(input_path, output_path, scale=4):
    """
    Upscale saree images with intricate designs using Real-ESRGAN
    Preserves fine details like fabric patterns and jewelry
    
    Args:
        input_path (str): Path to input saree image
        output_path (str): Path to save upscaled image
        scale (int): Upscaling factor (2 or 4)
    """
    if not REAL_ESRGAN_AVAILABLE:
        print("Real-ESRGAN not installed. Cannot upscale image.")
        return None
        
    try:
        # Load the image
        img = cv2.imread(input_path, cv2.IMREAD_UNCHANGED)
        if img is None:
            raise ValueError(f"Could not load image from {input_path}")
        
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
        
        print(f"Upscaling image {scale}x...")
        # Upscale the image
        output, _ = upsampler.enhance(img, outscale=scale)
        
        # Save the upscaled image
        cv2.imwrite(output_path, output)
        print(f"Saved upscaled image to {output_path}")
        
        return output_path
    except Exception as e:
        print(f"Error upscaling image: {str(e)}")
        return None

def upscale_with_opencv(input_path, output_path, scale=2):
    """
    Alternative upscaling method using OpenCV (free but lower quality)
    """
    try:
        # Load image
        img = cv2.imread(input_path)
        if img is None:
            raise ValueError(f"Could not load image from {input_path}")
        
        # Get original dimensions
        height, width = img.shape[:2]
        
        # Upscale using interpolation
        upscaled = cv2.resize(img, (width*scale, height*scale), interpolation=cv2.INTER_LANCZOS4)
        
        # Save result
        cv2.imwrite(output_path, upscaled)
        print(f"Saved upscaled image to {output_path} using OpenCV")
        
        return output_path
    except Exception as e:
        print(f"Error upscaling with OpenCV: {str(e)}")
        return None

def upscale_image_bytes(image_bytes, output_path, scale=4):
    """
    Upscale an image directly from bytes
    
    Args:
        image_bytes (bytes): Image data as bytes
        output_path (str): Path to save upscaled image
        scale (int): Upscaling factor (2 or 4)
    """
    if not REAL_ESRGAN_AVAILABLE:
        print("Real-ESRGAN not installed. Cannot upscale image.")
        return None
    
    try:
        # Convert bytes to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)
        
        if img is None:
            raise ValueError("Could not decode image from bytes")
        
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
        
        print(f"Upscaling image {scale}x...")
        # Upscale the image
        output, _ = upsampler.enhance(img, outscale=scale)
        
        # Save the upscaled image
        cv2.imwrite(output_path, output)
        print(f"Saved upscaled image to {output_path}")
        
        return output_path
    except Exception as e:
        print(f"Error upscaling image from bytes: {str(e)}")
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upscale saree images with intricate designs")
    parser.add_argument("input", help="Path to input image")
    parser.add_argument("-o", "--output", help="Path to output image (default: adds '_upscaled' to filename)")
    parser.add_argument("-s", "--scale", type=int, default=4, help="Upscaling factor (2 or 4, default: 4)")
    parser.add_argument("--opencv", action="store_true", help="Use OpenCV instead of Real-ESRGAN")
    
    args = parser.parse_args()
    
    # Validate input file
    if not os.path.exists(args.input):
        print(f"Error: Input file {args.input} does not exist")
        exit(1)
    
    # Set output path if not provided
    if not args.output:
        name, ext = os.path.splitext(args.input)
        args.output = f"{name}_upscaled{ext}"
    
    # Process image
    if args.opencv:
        result = upscale_with_opencv(args.input, args.output, args.scale)
    else:
        result = upscale_saree_image(args.input, args.output, args.scale)
    
    if result:
        print("Upscaling completed successfully!")
    else:
        print("Upscaling failed!")