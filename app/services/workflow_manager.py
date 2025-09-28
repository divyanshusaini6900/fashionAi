from typing import Dict, List
import os
import logging
import asyncio
import base64
import json
import re
import uuid
from fastapi import HTTPException
from openai import OpenAI
from app.core.config import settings
from app.services.image_generator import ImageGenerator
from app.services.video_generator import VideoGenerator
from app.services.excel_generator import ExcelGenerator
from app.services.image_upscaler import ImageUpscaler  # Add this import
from app.utils.file_helpers import (
    save_generated_image,
    save_generated_video,
    save_excel_report,
    save_generated_image_variations,
    save_original_and_upscaled_images
)
from PIL import Image
from io import BytesIO

# Conditional imports based on configuration
if settings.USE_GEMINI_FOR_TEXT:
    from google import genai

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WorkflowManager:
    def __init__(self):
        """Initialize the workflow manager with required services."""
        self.image_generator = ImageGenerator()
        self.video_generator = VideoGenerator()
        self.excel_generator = ExcelGenerator()
        self.image_upscaler = ImageUpscaler()  # Add upscaler service
        
        # Initialize text analysis clients based on configuration
        if settings.USE_GEMINI_FOR_TEXT:
            try:
                self.gemini_client = genai.Client(api_key=settings.GEMINI_API_KEY)
                logger.info("Gemini API client initialized for text analysis")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client for text: {e}")
                logger.info("Falling back to OpenAI for text analysis")
                settings.USE_GEMINI_FOR_TEXT = False
        
        # Initialize OpenAI if needed
        if not settings.USE_GEMINI_FOR_TEXT:
            self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
            logger.info("OpenAI client initialized for text analysis")
        
        logger.info(f"Text analysis mode: {'Gemini' if settings.USE_GEMINI_FOR_TEXT else 'OpenAI'}")
        
    def _generate_sku_id(self, username: str, product: str) -> str:
        """
        Generates a unique SKU ID based on username, product, and a UUID.
        Format: username[0:3] + product[0:3] + uuid
        """
        uuid_part = str(uuid.uuid4())[:8]
        
        sku_id = f"{username[:3].lower()}{product[:3].lower()}{uuid_part}"
        return sku_id
        
    def _parse_ai_response(self, response_text: str) -> Dict:
        """
        Parses the raw text from AI (OpenAI/Gemini) to extract the JSON object.
        Handles both markdown-wrapped and raw JSON responses.
        """
        try:
            # First try to find JSON block in markdown
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                return json.loads(json_str)

            # If no markdown block, try to parse the whole string as JSON
            return json.loads(response_text)
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {str(e)}")
            logger.error(f"Raw response: {response_text}")
            raise ValueError("Failed to parse AI response as JSON")
        
    async def _analyze_with_gemini(self, image_paths: Dict[str, str], text_description: str, username: str, product: str) -> Dict:
        """
        Analyzes product images and text description using Gemini's Gemini-Pro-Vision model.
        
        Args:
            image_paths: Dictionary of paths to product images, keyed by view name
            text_description: Text description of the product
            username: Username for SKU generation
            product: Product name for SKU generation
            
        Returns:
            Dictionary containing structured product data and image analysis
        """
        # Generate a unique product ID
        sku_id = self._generate_sku_id(username, product)
        logger.info(f"Generated SKU_ID: {sku_id}")

        try:
            logger.info("Starting Gemini analysis...")
            
            # Construct the detailed prompt
            prompt = f"""You are an expert e-commerce product data analyst and fashion photography consultant. Your task is to provide a DETAILED and COMPREHENSIVE analysis of the fashion product shown in the images and described in the text.

**PRODUCT DESCRIPTION PROVIDED:**
{text_description}

**YOUR TASK:**
Analyze the images and description thoroughly to generate the required product data, including appropriate model poses for different occasions.

**ANALYSIS REQUIREMENTS:**

1. **Description**: 
   - Write a concise and compelling product description (around 50-70 words) that highlights the product's key features and benefits.

2. **Key Features**:
   - Highlight the main features of the product in bullet points. These should be full sentences.

3. **Search Keywords**:
   - Generate specific, relevant search keywords.

4. **Model Pose Recommendations**:
   - Based on the product type, occasion, and gender, recommend appropriate model poses that would best showcase the product.
   - Provide 3 different pose recommendations that would work well for lifestyle images.
   - Each pose should be described in detail (e.g., "standing straight with hands clasped", "sitting gracefully with one leg crossed", "walking confidently with product flowing naturally").

**CRITICAL INSTRUCTIONS:**
1. Be SPECIFIC and DETAILED in every field.
2. Use the provided SKU_ID: {sku_id}
3. Ensure the output is a valid JSON object.

**EXAMPLE OUTPUT FORMAT:**
```json
{{
    "product_data": {{
        "SKU_ID": "{sku_id}",
        "Description": "This stunning lehenga choli set is perfect for weddings and special occasions. Crafted with care, the ensemble features intricate embroidery on a rich, vibrant orange fabric, offering an elegant and fashionable look.",
        "Key Features": [
            "Perfect for weddings and special occasions",
            "Intricate embroidery on rich, vibrant fabric",
            "Elegant and fashionable design"
        ],
        "Search Keywords": [
            "Lehenga Choli",
            "Wedding Outfit",
            "Embroidered Dress",
            "Festive Wear",
            "Traditional Indian Wear"
        ],
        "Gender": "Women",
        "Occasion": "Wedding",
        "RecommendedPoses": [
            "Standing straight with hands gently clasped in front, showcasing the full length and embroidery of the lehenga",
            "Sitting gracefully on a chair with one leg crossed, allowing the dupatta to drape elegantly behind",
            "Twirling slightly to show the flow and movement of the lehenga fabric"
        ]
    }},
    "image_analysis": {{
        "quality": "High quality product images with good lighting",
        "lighting": "Natural lighting with good visibility",
        "background": "Clean background suitable for e-commerce",
        "key_features": ["Detailed view of embroidery", "Clear fabric texture"],
        "suggested_improvements": ["Additional angle shots could be beneficial"]
    }}
}}
```

CRITICAL: 
- Provide detailed, specific information for each field.
- Only return valid JSON."""
            
            # Load images for Gemini
            images = []
            for image_path in list(image_paths.values())[:5]:  # Limit to 5 images
                try:
                    img = Image.open(image_path)
                    images.append(img)
                except Exception as e:
                    logger.warning(f"Failed to process image {image_path}: {str(e)}")
            
            if not images:
                raise ValueError("No valid images found for analysis")
                
            # Call Gemini API with text and images
            logger.info("Calling Gemini API...")
            response = await asyncio.to_thread(
                self.gemini_client.models.generate_content,
                model="gemini-2.0-flash-exp",
                contents={
                    "parts": [
                        {"text": prompt},
                        *[{"inline_data": {
                            "mime_type": "image/jpeg",
                            "data": self._image_to_base64(img)
                        }} for img in images]
                    ]
                }
            )
            
            # Parse the response
            analysis_text = response.text
            logger.info("Successfully received Gemini analysis")
            logger.info(f"Raw Gemini response: {analysis_text}")
            
            # Parse and validate the response
            analysis_data = self._parse_ai_response(analysis_text)
            logger.info(f"Parsed analysis data: {json.dumps(analysis_data, indent=2)}")
            
            # Ensure 'product_data' exists before modification
            if "product_data" not in analysis_data:
                raise ValueError("`product_data` not in Gemini response")
            
            # Always use the locally generated SKU_ID for consistency and control.
            analysis_data["product_data"]["SKU_ID"] = sku_id
            
            return analysis_data
            
        except Exception as e:
            logger.error(f"Error in Gemini analysis: {str(e)}", exc_info=True)
            raise ValueError(f"Failed during Gemini analysis: {e}")
    
    def _image_to_base64(self, image: Image) -> str:
        """Convert PIL Image to base64 string."""
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        return base64.b64encode(buffered.getvalue()).decode('utf-8')
        
    async def _analyze_with_gemini_combined(self, image_paths: Dict[str, str], text_description: str, username: str, product: str, number_of_outputs: int = 1) -> Dict:
        """
        Analyzes product images and text description using Gemini's Gemini-Pro-Vision model.
        This combined method generates background and pose recommendations in a single API call.
        
        Args:
            image_paths: Dictionary of paths to product images, keyed by view name
            text_description: Text description of the product
            username: Username for SKU generation
            product: Product name for SKU generation
            number_of_outputs: Number of background/pose combinations to generate
            
        Returns:
            Dictionary containing structured product data, image analysis, and background/pose recommendations
        """
        # Generate a unique product ID
        sku_id = self._generate_sku_id(username, product)
        logger.info(f"Generated SKU_ID: {sku_id}")

        try:
            logger.info("Starting combined Gemini analysis for background and pose only...")
            
            # Construct the detailed prompt that focuses only on background and pose generation
            prompt = f"""You are an expert fashion photography consultant. Your task is to analyze the fashion product shown in the images and described in the text, and provide ONLY background settings and model pose recommendations that would best showcase this product.

**PRODUCT INFORMATION:**
{text_description}

**YOUR TASK:**
Based on the product type, occasion, and gender, generate appropriate background settings and model poses for different occasions.

**GENERATION REQUIREMENTS:**

1. **Model Information**:
   - Determine the appropriate gender for the model based on the product
   - Identify the primary occasion for wearing this product

2. **Model Pose Recommendations**:
   - Based on the product type, occasion, and gender, recommend appropriate model poses that would best showcase the product.
   - Provide 3 different pose recommendations that would work well for lifestyle images.
   - Each pose should be described in detail (e.g., "standing straight with hands clasped", "sitting gracefully with one leg crossed", "walking confidently with product flowing naturally").
   - IMPORTANT: Focus on poses that showcase the product as it appears in the reference images, without modifying its appearance.

3. **View-Specific Poses**:
   - Recommend specific poses for different product views:
     * frontside view: Pose that clearly shows the front of the garment
     * backside view: Pose that clearly shows the back of the garment
     * sideview: Pose that clearly shows the side profile and fit of the garment
   - Each view-specific pose should be described in detail.
   - IMPORTANT: These poses should showcase the exact product as shown in the reference images.

4. **Background Settings**:
   - Generate {number_of_outputs} unique and detailed background descriptions that complement the product and occasion.
   - Include specific details like lighting, setting, and mood.
   - Each background should be different from others.
   - Focus on creating immersive, lifestyle-appropriate scenes.
   - IMPORTANT: Backgrounds should complement the product without overshadowing it or requiring any changes to the product appearance.

**CRITICAL INSTRUCTIONS:**
1. Be SPECIFIC and DETAILED in every field.
2. DO NOT modify or reinterpret the product appearance in any way - focus only on poses and backgrounds that showcase the product as it is.
3. Ensure the output is a valid JSON object.

**EXAMPLE OUTPUT FORMAT:**
```json
{{
    "product_data": {{
        "SKU_ID": "{sku_id}",
        "Gender": "Women",
        "Occasion": "Wedding",
        "RecommendedPoses": [
            "Standing straight with hands gently clasped in front, showcasing the full length and embroidery of the lehenga",
            "Sitting gracefully on a chair with one leg crossed, allowing the dupatta to drape elegantly behind",
            "Twirling slightly to show the flow and movement of the lehenga fabric"
        ],
        "ViewSpecificPoses": {{
            "frontside": "Standing straight facing forward with arms slightly away from the body to showcase the front design and embroidery",
            "backside": "Standing straight with back facing the camera, hands clasped behind to highlight the back design and fit",
            "sideview": "Standing in profile with one hand on hip to show the silhouette and side details of the garment"
        }}
    }},
    "background_recommendations": [
        "Grand ballroom with crystal chandeliers and marble floors, bathed in warm golden lighting",
        "Romantically lit garden terrace with string lights and blooming flowers at twilight",
        "Luxurious hotel suite with floor-to-ceiling windows overlooking a city skyline at sunset"
    ]
}}
```

CRITICAL: 
- Provide detailed, specific information for each field.
- Only return valid JSON.
- DO NOT modify or reinterpret the product appearance in any way.
"""

            # Load images for Gemini
            images = []
            for image_path in list(image_paths.values())[:5]:  # Limit to 5 images
                try:
                    img = Image.open(image_path)
                    images.append(img)
                except Exception as e:
                    logger.warning(f"Failed to process image {image_path}: {str(e)}")
            
            if not images:
                raise ValueError("No valid images found for analysis")
                
            # Call Gemini API with text and images
            logger.info("Calling Gemini API for combined analysis...")
            response = await asyncio.to_thread(
                self.gemini_client.models.generate_content,
                model="gemini-2.0-flash-exp",
                contents={
                    "parts": [
                        {"text": prompt},
                        *[{"inline_data": {
                            "mime_type": "image/jpeg",
                            "data": self._image_to_base64(img)
                        }} for img in images]
                    ]
                }
            )
            
            # Parse the response
            analysis_text = response.text
            logger.info("Successfully received combined Gemini analysis")
            logger.info(f"Raw Gemini response: {analysis_text}")
            
            # Parse and validate the response
            analysis_data = self._parse_ai_response(analysis_text)
            logger.info(f"Parsed combined analysis data: {json.dumps(analysis_data, indent=2)}")
            
            # Ensure 'product_data' exists before modification
            if "product_data" not in analysis_data:
                raise ValueError("`product_data` not in Gemini response")
            
            # Always use the locally generated SKU_ID for consistency and control.
            analysis_data["product_data"]["SKU_ID"] = sku_id
            
            return analysis_data
            
        except Exception as e:
            logger.error(f"Error in combined Gemini analysis: {str(e)}", exc_info=True)
            raise ValueError(f"Failed during combined Gemini analysis: {e}")
        
    async def _analyze_with_openai(self, image_paths: Dict[str, str], text_description: str, username: str, product: str) -> Dict:
        """
        Analyzes product images and text description using OpenAI's GPT-4 Vision model.
        
        Args:
            image_paths: Dictionary of paths to product images, keyed by view name
            text_description: Text description of the product
            
        Returns:
            Dictionary containing structured product data and image analysis
        """
        # Generate a unique product ID
        sku_id = self._generate_sku_id(username, product)
        logger.info(f"Generated SKU_ID: {sku_id}")

        try:
            logger.info("Starting OpenAI analysis...")
            
            # Construct the detailed prompt
            prompt = f"""You are an expert e-commerce product data analyst and fashion photography consultant. Your task is to provide a DETAILED and COMPREHENSIVE analysis of the fashion product shown in the images and described in the text.

**PRODUCT DESCRIPTION PROVIDED:**
{text_description}

**YOUR TASK:**
Analyze the images and description thoroughly to generate the required product data, including appropriate model poses for different occasions.

**ANALYSIS REQUIREMENTS:**

1.  **Description**: 
    - Write a concise and compelling product description (around 50-70 words) that highlights the product's key features and benefits, as shown in the example.

2.  **Key Features**:
    - Highlight the main features of the product in bullet points. These should be full sentences.

3.  **Search Keywords**:
    - Generate specific, relevant search keywords.

4.  **Model Pose Recommendations**:
    - Based on the product type, occasion, and gender, recommend appropriate model poses that would best showcase the product.
    - Provide 3 different pose recommendations that would work well for lifestyle images.
    - Each pose should be described in detail (e.g., "standing straight with hands clasped", "sitting gracefully with one leg crossed", "walking confidently with product flowing naturally").

**CRITICAL INSTRUCTIONS:**
1.  Be SPECIFIC and DETAILED in every field.
2.  Use the provided SKU_ID.
3.  Ensure the output is a valid JSON object.

**EXAMPLE OUTPUT FORMAT:**
```json
{{
    "product_data": {{
        "SKU_ID": "gen-prod-a1b2c3d4",
        "Description": "This stunning lehenga choli set is perfect for weddings and special occasions. Crafted with care, the ensemble features intricate embroidery on a rich, vibrant orange fabric, offering an elegant and fashionable look. The semi-sheer dupatta adds a touch of sophistication, while the embellished border adds a luxurious finish. Ideal for women seeking a blend of traditional and contemporary style.",
        "Key Features": [
            "This stunning lehenga choli set is perfect for weddings and special occasions.",
            "Crafted with care, the ensemble features intricate embroidery on a rich, vibrant fabric, offering an elegant and fashionable look.",
            "The semi-sheer dupatta adds a touch of sophistication, while the embellished border adds a luxurious finish."
        ],
        "Search Keywords": [
            "Lehenga Choli",
            "Wedding Outfit",
            "Embroidered Dress",
            "Festive Wear",
            "Traditional Indian Wear"
        ],
        "Gender": "Women",
        "Occasion": "Wedding",
        "RecommendedPoses": [
            "Standing straight with hands gently clasped in front, showcasing the full length and embroidery of the lehenga",
            "Sitting gracefully on a chair with one leg crossed, allowing the dupatta to drape elegantly behind",
            "Twirling slightly to show the flow and movement of the lehenga fabric"
        ]
    }},
    "image_analysis": {{
        "quality": "Detailed image quality assessment",
        "lighting": "Specific lighting conditions",
        "background": "Background description",
        "key_features": ["List of notable product features"],
        "suggested_improvements": ["Specific photography improvement suggestions"]
    }}
}}
```

CRITICAL: 
- Provide detailed, specific information for each field.
"""
            
            # Prepare the message content with text and images
            message_content = [{"type": "text", "text": prompt}]
            
            # Add images to the message (up to 5 images)
            for image_path in list(image_paths.values())[:5]:  # GPT-4 Vision can handle up to 5 images
                try:
                    with open(image_path, "rb") as image_file:
                        base64_image = base64.b64encode(image_file.read()).decode('utf-8')
                        message_content.append({
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        })
                except Exception as e:
                    logger.warning(f"Failed to process image {image_path}: {str(e)}")

            # Call OpenAI API
            logger.info("Calling OpenAI API...")
            response = await asyncio.to_thread(
                self.openai_client.chat.completions.create,
                model="gpt-4o",
                messages=[{
                    "role": "user",
                    "content": message_content
                }],
                max_tokens=4096,  # Increased token limit for more detailed analysis
                temperature=0.7,  # Added temperature for balanced creativity and accuracy
            )
            
            # Parse the response
            analysis_text = response.choices[0].message.content
            logger.info("Successfully received OpenAI analysis")
            logger.info(f"Raw OpenAI response: {analysis_text}")
            
            # Parse and validate the response
            analysis_data = self._parse_ai_response(analysis_text)
            logger.info(f"Parsed analysis data: {json.dumps(analysis_data, indent=2)}")
            
            # Ensure 'product_data' exists before modification
            if "product_data" not in analysis_data:
                raise ValueError("`product_data` not in OpenAI response")
            
            # Always use the locally generated SKU_ID for consistency and control.
            analysis_data["product_data"]["SKU_ID"] = sku_id

            # List of all expected fields
            expected_fields = [
                "SKU_ID", "Description", "Key Features", "Search Keywords", "Gender", "Occasion"
            ]
            
            # Required fields that must have meaningful values
            required_fields = [
                "SKU_ID", "Description", "Key Features", "Search Keywords", "Gender", "Occasion"
            ]
            
            # Check all expected fields exist
            if "product_data" not in analysis_data:
                raise ValueError("`product_data` not in OpenAI response")

            for field in expected_fields:
                if field not in analysis_data["product_data"]:
                    logger.warning(f"Missing field in OpenAI response: {field}")
                    analysis_data["product_data"][field] = "Not Visible"
            
            # Validate required fields have meaningful values
            for field in required_fields:
                if field not in analysis_data["product_data"] or analysis_data["product_data"][field] in ["", "Not Specified", "Not Visible", None]:
                    logger.error(f"Required field '{field}' missing or empty in OpenAI response")
                    raise ValueError(f"Required field '{field}' missing or empty in OpenAI response")
            
            # Convert any string "None" or empty strings to "Not Visible"
            for key, value in analysis_data["product_data"].items():
                if value in ["None", "", None]:
                    analysis_data["product_data"][key] = "Not Visible"
                elif isinstance(value, list) and (not value or all(v in ["None", "", None] for v in value)):
                    analysis_data["product_data"][key] = ["Not Specified"]
            
            return analysis_data
            
        except Exception as e:
            logger.error(f"Error in OpenAI analysis: {str(e)}", exc_info=True)
            logger.error(f"Raw response was: {analysis_text if 'analysis_text' in locals() else 'No response received'}")
            # Re-raise the exception to be caught by the main workflow handler
            raise ValueError(f"Failed during OpenAI analysis: {e}")
        
    async def process_request_with_background_array(
        self,
        image_paths: Dict[str, str],
        background_config: Dict[str, List[int]],  # {view: [white_count, plain_count, random_count]}
        text_description: str,
        request_id: str,
        username: str,
        product: str,
        isVideo: bool = False,
        number_of_outputs: int = 1,
        aspect_ratio: str = "9:16",
        gender: str = None,  # Add gender parameter
        upscale: bool = True  # Add upscale parameter
    ) -> Dict:
        """
        Orchestrates the full process from analysis to generation with background array support.
        
        Args:
            image_paths: Dictionary of paths to input images, keyed by view name
            background_config: Dictionary mapping views to background arrays [white, plain, random]
            text_description: Text description of the product
            request_id: Unique identifier for this request
            isVideo: Whether to generate a video (default: False)
            number_of_outputs: Number of image variations to generate (default: 1)
            aspect_ratio: Aspect ratio for generated images (default: "9:16")
            gender: Gender of the model to display clothing on (male/female)
            upscale: Whether to upscale generated images (default: True)
            
        Returns:
            Dictionary containing URLs to generated files and metadata
        """
        try:
            logger.info(f"Starting workflow with background array for request_id: {request_id}")
            
            # 1. Analyze inputs with AI to get detailed JSON
            # Use combined analysis for optimization (single API call for both product analysis and background/pose recommendations)
            if settings.USE_GEMINI_FOR_TEXT:
                analysis_json = await self._analyze_with_gemini_combined(image_paths, text_description, username, product, number_of_outputs)
            else:
                # For OpenAI, we still need separate calls
                analysis_json = await self._analyze_with_openai(image_paths, text_description, username, product)
            
            product_data = analysis_json.get("product_data", {})
            image_analysis = analysis_json.get("image_analysis", {})

            # 2. Generate lifestyle images based on the analysis and background arrays
            primary_image_bytes, all_variations_bytes_dict = await self.image_generator.generate_images_with_background_array(
                product_data=product_data,
                reference_image_paths_dict=image_paths,
                background_config=background_config,
                number_of_outputs=number_of_outputs,
                aspect_ratio=aspect_ratio,
                gender=gender  # Pass gender parameter
            )

            if not primary_image_bytes:
                raise ValueError("Failed to generate a primary image.")

            # 3. Save original images and upscale if requested
            original_variations_bytes_dict = all_variations_bytes_dict.copy()  # Keep a copy of original images
            
            if upscale:
                logger.info("Upscaling generated images...")
                # Upscale all variations (including the primary image which is part of variations)
                for key, image_bytes in all_variations_bytes_dict.items():
                    upscaled_bytes = self.image_upscaler.upscale_image_bytes(image_bytes)
                    if upscaled_bytes:
                        all_variations_bytes_dict[key] = upscaled_bytes
                        logger.info(f"Variation {key} upscaled successfully")
                        # Update primary image if this variation contains it
                        if image_bytes == primary_image_bytes:
                            primary_image_bytes = upscaled_bytes
                            logger.info("Primary image upscaled successfully")

            # 4. Save both original and upscaled images with distinct names
            if upscale:
                # Save both original and upscaled images
                saved_images_result = save_original_and_upscaled_images(
                    original_variations_bytes_dict, 
                    all_variations_bytes_dict, 
                    request_id
                )
                # Use upscaled images for the rest of the workflow
                variation_urls_dict = saved_images_result['upscaled']
                # Store original image URLs in metadata
                original_image_urls = saved_images_result['original']
            else:
                # Save only generated images (no upscaling)
                variation_urls_dict = save_generated_image_variations(all_variations_bytes_dict, request_id)
                original_image_urls = {}
            
            # The primary image URL is the first frontside image, or the first one saved.
            primary_image_url = None
            for key, url in variation_urls_dict.items():
                if key.startswith("frontside"):
                    primary_image_url = url
                    break
            
            if not primary_image_url:
                primary_image_url = next(iter(variation_urls_dict.values()), None)

            if not primary_image_url:
                raise ValueError("Failed to obtain a primary image URL after saving.")

            # Keep all variations for Excel generation (don't exclude primary image)
            all_variations_dict = variation_urls_dict.copy()
            
            # Also create additional variations for other purposes (excluding primary image)
            additional_variations_dict = {
                view: url for view, url in variation_urls_dict.items() if url != primary_image_url
            }

            # 5. Generate and save video if requested (using primary image)
            video_url = None
            if isVideo:
                try:
                    logger.info("Starting video generation...")
                    # Use the primary generated image URL as input for video generation
                    video_bytes = await self.video_generator.isVideo(
                        image_path=primary_image_url,
                        product_data=product_data
                    )
                    video_url = save_generated_video(video_bytes, request_id)
                    logger.info(f"Video generation successful. URL: {video_url}")
                except Exception as e:
                    logger.error("Video generation failed, continuing without video.", exc_info=True)
            
            # 6. Create an Excel report from the detailed product data
            try:
                logger.info("Creating Excel report...")
                logger.info(f"Product data for Excel: {product_data}")
                logger.info(f"Primary image URL: {primary_image_url}")
                logger.info(f"Variation URLs: {additional_variations_dict}")
                
                excel_bytes = self.excel_generator.create_report(
                    product_data=product_data,
                    variation_urls=all_variations_dict,
                    video_url=video_url
                )
                
                # 7. Save the Excel report and get its URL
                excel_url = save_excel_report(excel_bytes, request_id)
                logger.info(f"Excel report saved successfully: {excel_url}")
                
                # For the new schema, we include all variations in image_variations
                # and all upscaled images in upscale_image array
                all_variation_urls = list(variation_urls_dict.values())
                upscaled_image_urls = [primary_image_url] if upscale and primary_image_url else []
                
                return {
                    "image_variations": all_variation_urls,  # All gemini generated images
                    "upscale_image": upscaled_image_urls,  # Upscaled images when upscale=True
                    "output_video_url": video_url,
                    "excel_report_url": excel_url,
                    "metadata": {
                        "analysis": analysis_json,
                        "request_id": request_id,
                        "total_variations": len(variation_urls_dict),
                        "upscaled": upscale,
                        "original_image_urls": original_image_urls
                    }
                }
            except Exception as excel_error:
                logger.error(f"Excel generation failed: {str(excel_error)}", exc_info=True)
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to generate Excel report: {str(excel_error)}"
                )
        except Exception as e:
            logger.error(f"Workflow failed for request {request_id}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"An error occurred in the processing workflow: {str(e)}"
            )

    async def process_request(
        self,
        image_paths: Dict[str, str],
        text_description: str,
        request_id: str,
        username: str,
        product: str,
        isVideo: bool = False,
        number_of_outputs: int = 1,
        aspect_ratio: str = "9:16",
        gender: str = None,
        upscale: bool = True
    ) -> Dict:
        """
        Orchestrates the full process from analysis to generation.
        
        Args:
            image_paths: Dictionary of paths to input images, keyed by view name
            text_description: Text description of the product
            request_id: Unique identifier for this request
            isVideo: Whether to generate a video (default: False)
            number_of_outputs: Number of image variations to generate (default: 1)
            aspect_ratio: Aspect ratio for generated images (default: "9:16")
            gender: Gender of the model to display clothing on (male/female)
            upscale: Whether to upscale generated images (default: True)
            
        Returns:
            Dictionary containing URLs to generated files and metadata
        """
        try:
            logger.info(f"Starting workflow for request_id: {request_id}")
            
            # 1. Analyze inputs with AI to get detailed JSON
            # Use combined analysis for optimization (single API call for both product analysis and background/pose recommendations)
            if settings.USE_GEMINI_FOR_TEXT:
                analysis_json = await self._analyze_with_gemini_combined(image_paths, text_description, username, product, number_of_outputs)
            else:
                # For OpenAI, we still need separate calls
                analysis_json = await self._analyze_with_openai(image_paths, text_description, username, product)
            
            product_data = analysis_json.get("product_data", {})
            image_analysis = analysis_json.get("image_analysis", {})

            # 2. Generate lifestyle images based on the analysis
            primary_image_bytes, all_variations_bytes_dict = await self.image_generator.generate_images(
                product_data=product_data,
                reference_image_paths_dict=image_paths,
                number_of_outputs=number_of_outputs,
                aspect_ratio=aspect_ratio,
                gender=gender  # Pass gender parameter
            )

            if not primary_image_bytes:
                raise ValueError("Failed to generate a primary image.")

            # 3. Save original images and upscale if requested
            original_variations_bytes_dict = all_variations_bytes_dict.copy()  # Keep a copy of original images
            
            if upscale:
                logger.info("Upscaling generated images...")
                # Upscale all variations (including the primary image which is part of variations)
                for key, image_bytes in all_variations_bytes_dict.items():
                    upscaled_bytes = self.image_upscaler.upscale_image_bytes(image_bytes)
                    if upscaled_bytes:
                        all_variations_bytes_dict[key] = upscaled_bytes
                        logger.info(f"Variation {key} upscaled successfully")
                        # Update primary image if this variation contains it
                        if image_bytes == primary_image_bytes:
                            primary_image_bytes = upscaled_bytes
                            logger.info("Primary image upscaled successfully")

            # 4. Save both original and upscaled images with distinct names
            if upscale:
                # Save both original and upscaled images
                saved_images_result = save_original_and_upscaled_images(
                    original_variations_bytes_dict, 
                    all_variations_bytes_dict, 
                    request_id
                )
                # Keep original and upscaled URLs separate
                original_variation_urls_dict = saved_images_result['original']
                upscaled_variation_urls_dict = saved_images_result['upscaled']
                
                # For Excel generation, use upscaled images
                variation_urls_dict = upscaled_variation_urls_dict
            else:
                # Save only generated images (no upscaling)
                original_variation_urls_dict = save_generated_image_variations(all_variations_bytes_dict, request_id)
                upscaled_variation_urls_dict = {}
                variation_urls_dict = original_variation_urls_dict
            
            # The primary image URL is the one associated with the 'frontside' view, or the first one saved.
            primary_image_url = variation_urls_dict.get("frontside") or next(iter(variation_urls_dict.values()), None)

            if not primary_image_url:
                raise ValueError("Failed to obtain a primary image URL after saving.")

            # Keep all variations for Excel generation (don't exclude primary image)
            all_variations_dict = variation_urls_dict.copy()
            
            # Also create additional variations for other purposes (excluding primary image)
            additional_variations_dict = {
                view: url for view, url in variation_urls_dict.items() if url != primary_image_url
            }

            # 5. Generate and save video if requested (using primary image)
            video_url = None
            if isVideo:
                try:
                    logger.info("Starting video generation...")
                    # Use the primary generated image URL as input for video generation
                    video_bytes = await self.video_generator.isVideo(
                        image_path=primary_image_url,
                        product_data=product_data
                    )
                    video_url = save_generated_video(video_bytes, request_id)
                    logger.info(f"Video generation successful. URL: {video_url}")
                except Exception as e:
                    logger.error("Video generation failed, continuing without video.", exc_info=True)
            
            # 6. Create an Excel report from the detailed product data
            try:
                logger.info("Creating Excel report...")
                logger.info(f"Product data for Excel: {product_data}")
                logger.info(f"Primary image URL: {primary_image_url}")
                logger.info(f"Variation URLs: {additional_variations_dict}")
                
                excel_bytes = self.excel_generator.create_report(
                    product_data=product_data,
                    variation_urls=all_variations_dict,
                    video_url=video_url
                )
                
                # 7. Save the Excel report and get its URL
                excel_url = save_excel_report(excel_bytes, request_id)
                logger.info(f"Excel report saved successfully: {excel_url}")
                
                # Separate original and upscaled image URLs for clean response
                original_image_urls = list(original_variation_urls_dict.values())
                upscaled_image_urls = list(upscaled_variation_urls_dict.values()) if upscale else []
                
                return {
                    "image_variations": original_image_urls,  # Original generated images only
                    "upscale_image": upscaled_image_urls,  # Upscaled images only (when upscale=True)
                    "output_video_url": video_url,
                    "excel_report_url": excel_url,
                    "metadata": {
                        "analysis": analysis_json,
                        "request_id": request_id,
                        "total_variations": len(original_variation_urls_dict),
                        "upscaled": upscale,
                        "processing_times": {
                            # Add processing times if available
                        }
                    }
                }
            except Exception as excel_error:
                logger.error(f"Excel generation failed: {str(excel_error)}", exc_info=True)
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to generate Excel report: {str(excel_error)}"
                )
        except Exception as e:
            logger.error(f"Workflow failed for request {request_id}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"An error occurred in the processing workflow: {str(e)}"
            )