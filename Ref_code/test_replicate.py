import os
import replicate
import glob
import base64
from io import BytesIO
from PIL import Image

def convert_image_to_data_url(image_path):
    """Convert image file to data URL format"""
    with open(image_path, "rb") as image_file:
        image_data = image_file.read()
        base64_encoded = base64.b64encode(image_data).decode('utf-8')
        
        # Determine MIME type
        extension = os.path.splitext(image_path)[1].lower()
        mime_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg', 
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp'
        }
        mime_type = mime_types.get(extension, 'image/jpeg')
        
        return f"data:{mime_type};base64,{base64_encoded}"

def process_images_with_flux_kontext(image_directory, prompt, api_key):
    """
    Read 2 images from directory and process with Replicate flux-kontext model
    
    Args:
        image_directory (str): Path to directory containing images
        prompt (str): Your custom prompt for image processing
        api_key (str): Your Replicate API key
    
    Returns:
        str: Output from Replicate model
    """
    
    # Set up Replicate client
    os.environ["REPLICATE_API_TOKEN"] = api_key
    
    # Supported image extensions
    image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.webp']
    
    # Find all images in directory
    image_paths = []
    for extension in image_extensions:
        image_paths.extend(glob.glob(os.path.join(image_directory, extension)))
        image_paths.extend(glob.glob(os.path.join(image_directory, extension.upper())))
    
    if len(image_paths) < 2:
        raise ValueError(f"Found only {len(image_paths)} image(s). Need at least 2 images.")
    
    # Take only first 2 images for this model
    image_paths = image_paths[:2]
    print(f"Processing 2 images: {[os.path.basename(path) for path in image_paths]}")
    
    try:
        # Convert images to data URLs
        image1_data_url = convert_image_to_data_url(image_paths[0])
        image2_data_url = convert_image_to_data_url(image_paths[1])
        
        print(f"Converted image 1: {os.path.basename(image_paths[0])}")
        print(f"Converted image 2: {os.path.basename(image_paths[1])}")
        
        # Run the model
        output = replicate.run(
            "flux-kontext-apps/multi-image-kontext-max",
            input={
                "input_image_1": image1_data_url,
                "input_image_2": image2_data_url,
                "prompt": prompt,
                # Add other parameters as needed for the specific model
                # You may need to adjust these based on model requirements
                "num_inference_steps": 40,
                "guidance_scale": 7.5,
                "num_outputs": 1,
                "aspect_ratio": "9:16",
                "output_format": "jpg",
                "output_quality": 100,
                "disable_safety_checker": True
            }
        )
        
        return output
        
    except Exception as e:
        raise Exception(f"Error calling Replicate API: {str(e)}")

def save_output_images(output, save_directory="./replicate_output"):
    """
    Save output images from Replicate to local directory
    
    Args:
        output: Output from Replicate (usually list of URLs)
        save_directory (str): Directory to save images
    """
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)
    
    if isinstance(output, list):
        for i, image_url in enumerate(output):
            # Download and save each image
            import requests
            response = requests.get(image_url)
            if response.status_code == 200:
                image_path = os.path.join(save_directory, f"output_image_{i+1}.jpg")
                with open(image_path, "wb") as f:
                    f.write(response.content)
                print(f"Saved: {image_path}")
    else:
        # Single image output
        import requests
        response = requests.get(output)
        if response.status_code == 200:
            image_path = os.path.join(save_directory, "output_image1.jpg")
            with open(image_path, "wb") as f:
                f.write(response.content)
            print(f"Saved: {image_path}")

# Example usage
if __name__ == "__main__":
    # Configuration
    IMAGE_DIRECTORY = "/home/nawnit08k/listing_generator/test_images/shoes/shoe2"  # Update this path
    API_KEY = "r8_Nqq9h7dHI3bTviOfEge3HmrLNPUcoQS23et0O"   # Update with your API key
    
    # Your custom prompt
    PROMPT = """
    A female model wearing these shoes in a garden setting. Use the reference images to match the design, quality, color etc.
    Do not change any part of the reference image and match different attributes closely.
    """
    
    try:
        # Process images
        result = process_images_with_flux_kontext(
            image_directory=IMAGE_DIRECTORY,
            prompt=PROMPT,
            api_key=API_KEY
        )
        
        print("\n" + "="*50)
        print("REPLICATE FLUX KONTEXT RESULT:")
        print("="*50)
        print("Output URLs:", result)
        
        # Save output images locally
        save_output_images(result)
        print("\nImages saved to ./replicate_output directory")
        
    except Exception as e:
        print(f"Error: {str(e)}")