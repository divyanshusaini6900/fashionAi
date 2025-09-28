import os
import base64
from openai import OpenAI
from PIL import Image
import glob

def encode_image_to_base64(image_path):
    """Convert image to base64 string"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def get_image_mime_type(image_path):
    """Get the MIME type of the image"""
    extension = os.path.splitext(image_path)[1].lower()
    mime_types = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg', 
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.webp': 'image/webp'
    }
    return mime_types.get(extension, 'image/jpeg')

def analyze_images_with_openai(image_directory, prompt, api_key):
    """
    Read images from directory and send to OpenAI GPT-4o for analysis
    
    Args:
        image_directory (str): Path to directory containing images
        prompt (str): Your custom prompt for image analysis
        api_key (str): Your OpenAI API key
    
    Returns:
        str: Analysis response from OpenAI
    """
    
    # Initialize OpenAI client
    client = OpenAI(api_key=api_key)
    
    # Supported image extensions
    image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.webp']
    
    # Find all images in directory
    image_paths = []
    for extension in image_extensions:
        image_paths.extend(glob.glob(os.path.join(image_directory, extension)))
        image_paths.extend(glob.glob(os.path.join(image_directory, extension.upper())))
    
    if len(image_paths) < 2:
        raise ValueError(f"Found only {len(image_paths)} image(s). Need at least 2 images.")
    
    print(f"Found {len(image_paths)} images: {[os.path.basename(path) for path in image_paths]}")
    
    # Prepare messages for OpenAI API
    message_content = [
        {
            "type": "text",
            "text": prompt
        }
    ]
    
    # Add each image to the message
    for image_path in image_paths:
        try:
            base64_image = encode_image_to_base64(image_path)
            mime_type = get_image_mime_type(image_path)
            
            message_content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:{mime_type};base64,{base64_image}"
                }
            })
            print(f"Added image: {os.path.basename(image_path)}")
            
        except Exception as e:
            print(f"Error processing image {image_path}: {str(e)}")
            continue
    
    # Send request to OpenAI
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": message_content
                }
            ],
            max_tokens=1500
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        raise Exception(f"Error calling OpenAI API: {str(e)}")

# Example usage
if __name__ == "__main__":
    # Configuration
    IMAGE_DIRECTORY = "/home/nawnit08k/listing_generator/test_images/shoes/shoe2"  # Update this path
    API_KEY = "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"      # Update with your API key
    
    # Your custom prompt
    PROMPT = """
    You are a forensic product inspector. Analyze these images with EXTREME precision for quality control validation.

    **STRICT COMPARISON PROTOCOL:**

    **SOLE ANALYSIS (CRITICAL):**
    - Image 1 sole color: Describe the exact shade (jet black, charcoal, dark brown, etc.)
    - Image 2 sole color: Describe the exact shade independently  
    - Image 3 sole color: Describe the exact shade independently
    - Are there ANY variations in sole color between images? Even subtle ones?
    - Side color vs bottom color consistency
    - Any color bleeding or tone differences?

    **MATERIAL VERIFICATION:**
    - Exact texture description for each image separately
    - Surface finish consistency (matte level, sheen variations)
    - Any signs of different material batches?

    **HARDWARE PRECISION:**
    - Count eyelets in each image separately (don't assume)
    - Eyelet finish: Exact color description (gold, bronze, brass, antique gold)
    - Any tarnishing or finish variations?

    **MANUFACTURING MARKERS:**
    - Stitching patterns identical?
    - Seam placement consistency?
    - Any batch/production differences visible?

    **PHOTOGRAPHIC FACTORS:**
    - Which differences could be lighting artifacts?
    - Which differences suggest actual product variations?
    - Are there details obscured by angles/lighting?

    **VALIDATION VERDICT:**
    Use this STRICT scale:
    - 10/10: Forensically identical (same product, same batch)
    - 8-9/10: Same model, possibly different production batches
    - 6-7/10: Same model, noticeable variations that affect quality
    - 4-5/10: Similar products but different specifications
    - 1-3/10: Different products entirely

    **FINAL REQUIREMENT:** 
    For validation purposes, score 7/10 or below = FAILED MATCH
    List ANY discrepancies that could indicate different products or poor AI generation quality.

    **RED FLAGS TO WATCH FOR:**
    - Color temperature differences not explained by lighting
    - Proportion inconsistencies
    - Hardware variations
    - Material texture changes
    """
    
    # PROMPT = """
    # I want to pass these images to flux-kontext-apps/multi-image-kontext-max and black-forest-labs/flux-kontext-pro on replicate.
    # The result which I want from the replicate models is some one wearing these shoes.
    # Since multi-image model takes two inputs, can you tell me which two are best for generating the best result and pro model takes one
    # image then which one is best image.
    # Give me a prompt as well, the prompt should be minimal like based on male or female shoes (make sure male or female is chosen based on images), generate a prompt a male/female model wearing this in some location.
    # Also mention in the prompt to use the reference image to match the design and quality etc.
    # give me result in json 
    # {
    #     model_name, image identity, prompt
    # }
    # """
    
    try:
        # Analyze images
        result = analyze_images_with_openai(
            image_directory=IMAGE_DIRECTORY,
            prompt=PROMPT,
            api_key=API_KEY
        )
        
        print("\n" + "="*50)
        print("OPENAI ANALYSIS RESULT:")
        print("="*50)
        print(result)
        
    except Exception as e:
        print(f"Error: {str(e)}")