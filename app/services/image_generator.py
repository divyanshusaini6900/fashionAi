import replicate
import requests
import asyncio
from fastapi import HTTPException
from app.core.config import settings
from typing import List, Optional, Dict, Tuple
import base64
import logging
import os
import json
import re
from io import BytesIO
from PIL import Image

# Conditional imports based on configuration
if settings.USE_GEMINI_FOR_IMAGES or settings.USE_GEMINI_FOR_VIDEOS:
    from google import genai
    from google.genai import types

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImageGenerator:
    def __init__(self):
        """Initializes the image generator with both Gemini and Replicate support."""
        # Replicate configuration (fallback)
        self.primary_model = "flux-kontext-apps/multi-image-kontext-max"
        self.fallback_model = "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b"
        
        # Initialize Gemini client if enabled
        if settings.USE_GEMINI_FOR_IMAGES:
            try:
                self.gemini_client = genai.Client(api_key=settings.GEMINI_API_KEY)
                logger.info("Gemini API client initialized for image generation")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client: {e}")
                logger.info("Falling back to Replicate for image generation")
                settings.USE_GEMINI_FOR_IMAGES = False
        
        # Initialize Replicate if needed
        if not settings.USE_GEMINI_FOR_IMAGES:
            if not os.environ.get("REPLICATE_API_TOKEN"):
                os.environ["REPLICATE_API_TOKEN"] = settings.REPLICATE_API_TOKEN
            logger.info(f"ImageGenerator initialized with Replicate model: {self.primary_model}")
        
        logger.info(f"Image generation mode: {'Gemini' if settings.USE_GEMINI_FOR_IMAGES else 'Replicate'}")

    async def _generate_contextual_backgrounds(self, product_data: Dict, count: int = 5) -> List[str]:
        """
        Uses Gemini to generate contextually appropriate background descriptions.
        First checks if backgrounds are already provided in product_data from combined analysis,
        otherwise makes a separate API call.
        
        Args:
            product_data: Product information including description, occasion, gender, etc.
            count: Number of background descriptions to generate
            
        Returns:
            List of background descriptions
        """
        # Check if background recommendations are already provided (from combined analysis)
        if 'background_recommendations' in product_data and product_data['background_recommendations']:
            backgrounds = product_data['background_recommendations']
            # Ensure we have the right number
            backgrounds = backgrounds[:count]
            logger.info(f"Using {len(backgrounds)} pre-generated contextual backgrounds from combined analysis")
            return backgrounds
        
        # Also check for BackgroundRecommendations (alternative format)
        if 'BackgroundRecommendations' in product_data and product_data['BackgroundRecommendations']:
            backgrounds = product_data['BackgroundRecommendations']
            # Ensure we have the right number
            backgrounds = backgrounds[:count]
            logger.info(f"Using {len(backgrounds)} pre-generated contextual backgrounds from combined analysis")
            return backgrounds
        
        # If not, fall back to making a separate API call
        try:
            # Extract relevant product information
            product_description = product_data.get('Description', 'fashion product')
            occasion = product_data.get('Occasion', 'general')
            gender = product_data.get('Gender', 'women')
            key_features = product_data.get('Key Features', [])
            
            # Format key features as a string
            features_text = ""
            if key_features:
                if isinstance(key_features, list):
                    features_text = ", ".join(key_features[:3])  # Take first 3 features
                else:
                    features_text = str(key_features)
            
            # Create prompt for background generation
            prompt = f"""
            Generate {count} unique and detailed background descriptions for a fashion photo shoot.
            
            PRODUCT INFORMATION:
            - Description: {product_description}
            - Occasion: {occasion}
            - Gender: {gender}
            - Key Features: {features_text}
            
            REQUIREMENTS:
            1. Each background should complement the product and occasion
            2. Include specific details like lighting, setting, and mood
            3. No white or plain backgrounds
            4. Diverse range of environments that match the product style
            5. Professional photography quality
            6. Each background should be different from others
            7. Focus on creating immersive, lifestyle-appropriate scenes
            
            EXAMPLE FORMAT (do not use these exact examples):
            - "Luxury boutique interior with soft ambient lighting and marble floors"
            - "Urban rooftop terrace at golden hour with city skyline view"
            - "Elegant garden party setting with string lights and floral arrangements"
            
            RETURN FORMAT:
            Provide ONLY a JSON array of {count} strings, each being a unique background description.
            Example: ["background1", "background2", "background3"]
            """
            
            logger.info(f"Generating contextual backgrounds for: {product_description}")
            
            # Call Gemini API
            response = await asyncio.to_thread(
                self.gemini_client.models.generate_content,
                model="gemini-2.0-flash-exp",
                contents=prompt
            )
            
            # Parse response
            backgrounds_text = response.text
            logger.info(f"Raw Gemini response for backgrounds: {backgrounds_text}")
            
            # Extract JSON array from response
            json_match = re.search(r'\[.*\]', backgrounds_text, re.DOTALL)
            if json_match:
                backgrounds = json.loads(json_match.group(0))
                # Ensure we have the right number and they're strings
                backgrounds = [str(bg) for bg in backgrounds if isinstance(bg, str)][:count]
                logger.info(f"Generated {len(backgrounds)} contextual backgrounds")
                return backgrounds
            else:
                # Create dynamic backgrounds based on occasion if parsing fails
                logger.warning("Failed to parse Gemini response, generating dynamic backgrounds based on occasion")
                return self._generate_dynamic_backgrounds(occasion, count)
                
        except Exception as e:
            logger.error(f"Failed to generate contextual backgrounds: {e}", exc_info=True)
            # Fallback to minimal predefined backgrounds
            return self._get_background_variations(product_data.get('Occasion', 'casual'))[:count]

    def _generate_dynamic_backgrounds(self, occasion: str, count: int = 5) -> List[str]:
        """
        Generates dynamic background descriptions based on occasion when Gemini fails.
        This creates varied backgrounds programmatically based on the occasion type.
        """
        # Base adjectives and settings for variety
        adjectives = ["elegant", "modern", "stylish", "sophisticated", "contemporary", "luxurious", "trendy"]
        lighting = ["natural lighting", "studio lighting", "ambient lighting", "soft lighting", "dramatic lighting"]
        settings = ["indoor setting", "outdoor setting", "urban environment", "natural environment"]
        
        # Occasion-specific elements
        occasion_elements = {
            "casual": ["park", "cafe", "street", "home", "garden"],
            "party": ["nightclub", "rooftop", "lounge", "celebration venue", "entertainment area"],
            "wedding": ["ceremony venue", "reception hall", "garden setting", "chapel", "banquet hall"],
            "beach": ["seaside", "coastal area", "shoreline", "tropical location", "oceanfront"],
            "formal": ["business district", "corporate office", "upscale restaurant", "gala venue", "museum"]
        }
        
        # Get elements for the specific occasion or default to casual
        elements = occasion_elements.get(occasion.lower(), occasion_elements["casual"])
        
        # Generate backgrounds
        backgrounds = []
        for i in range(count):
            adj = adjectives[i % len(adjectives)]
            light = lighting[i % len(lighting)]
            setting = settings[i % len(settings)]
            element = elements[i % len(elements)]
            backgrounds.append(f"{adj} {element} with {light} in a {setting}")
        
        return backgrounds

    def _get_background_variations(self, occasion: str) -> List[str]:
        """
        Generates dynamic background variations using Gemini AI based on the occasion.
        This is a fallback method that should not be called if Gemini is working properly.
        """
        logger.warning("Gemini failed to generate backgrounds, using fallback background variations")
        # Base backgrounds - minimal fallback options
        backgrounds = [
            "professional studio with soft lighting",
            "neutral gradient background",
            "subtle textured background",
            "minimalist lifestyle setting"
        ]
        
        return backgrounds

    def _create_generation_prompt(self, product_data: Dict, background: str, aspect_ratio: str = "9:16", gender: str = None, view: str = None) -> str:
        """
        Creates a specific prompt for each background variation.
        """
        # Use the provided gender parameter, or fall back to product data analysis
        if gender and gender.lower() in ['male', 'female']:
            # Use the explicitly provided gender
            model_type = "Indian man" if gender.lower() == "male" else "Indian woman"
        else:
            # Fall back to the existing logic based on product analysis
            ideal_for = product_data.get('Ideal For', 'women')
            if 'women' in ideal_for.lower() or 'female' in ideal_for.lower():
                model_type = "Indian woman"
            elif 'men' in ideal_for.lower() or 'male' in ideal_for.lower():
                model_type = "Indian man"
            else:
                model_type = "Indian woman"  # Default to woman
        
        # Map aspect ratio to descriptive text with explicit emphasis
        aspect_ratio_descriptions = {
            "1:1": "EXACTLY square aspect ratio (1:1, equal width and height) - CRITICALLY IMPORTANT: Generate a perfectly square image with no cropping or distortion",
            "16:9": "EXACTLY landscape orientation with 16:9 aspect ratio (width 1.78x height) - CRITICALLY IMPORTANT: Generate a widescreen landscape image with precise 16:9 proportions",
            "4:3": "EXACTLY landscape orientation with 4:3 aspect ratio (width 1.33x height) - CRITICALLY IMPORTANT: Generate a standard landscape image with precise 4:3 proportions",
            "3:4": "EXACTLY portrait orientation with 3:4 aspect ratio (height 1.33x width) - CRITICALLY IMPORTANT: Generate a standard portrait image with precise 3:4 proportions",
            "9:16": "EXACTLY portrait orientation with 9:16 aspect ratio (height 1.78x width) - CRITICALLY IMPORTANT: Generate a mobile-optimized portrait image with precise 9:16 proportions"
        }
        
        # Get the aspect description with fallback to 9:16 if not found
        aspect_description = aspect_ratio_descriptions.get(aspect_ratio, aspect_ratio_descriptions["9:16"])
        
        # Get pose recommendation if available
        # First check for view-specific poses
        view_specific_poses = product_data.get('ViewSpecificPoses', {})
        if view and view in view_specific_poses:
            # Use the specific pose for this view
            pose = view_specific_poses[view]
        else:
            # Fall back to general pose recommendations
            pose_recommendations = product_data.get('RecommendedPoses', [])
            if pose_recommendations:
                # Randomly select one of the recommended poses for variety
                import random
                pose = random.choice(pose_recommendations)
            else:
                pose = "standing straight with confident, natural posture showcasing the outfit"
        
        # Check if this is a jeans product with distressing details
        product_description = product_data.get('Description', '').lower()
        is_jeans = 'jeans' in product_description or 'denim' in product_description
        has_distressing = 'distress' in product_description or 'ripped' in product_description or 'destroyed' in product_description
        
        # Enhanced prompt with advanced fashion photography techniques and specific pose
        if is_jeans and has_distressing:
            # Specialized prompt for jeans with distressing details
            prompt = f"""
Professional high-fashion photography of a single {model_type} model wearing the exact pair of jeans shown in the reference images, positioned in a {background}.

PHOTOGRAPHY DIRECTIVES:
- Show ONLY ONE person in the image with professional studio lighting
- Generate image with {aspect_description}
- The background MUST completely fill the frame with no white borders or margins

CRITICALLY IMPORTANT: The generated image MUST show the EXACT SAME pair of jeans as in the reference images. Do NOT modify, change, or alter the jeans in any way.

The model MUST be wearing the identical jeans from the reference images with no changes to:
  * Color, material, and design
  * All distressing details (rips, tears, fading, whiskering, etc.)
  * Specific distressing locations (knee tears, thigh rips, pocket wear, etc.)
  * Fit and silhouette (skinny, straight, tapered, etc.)
  * Wash type (dark, medium, light, black, etc.)
  * Hardware details (buttons, rivets, zippers, etc.)
  * Stitching patterns and thread color
  * All visual elements and styling

Use the reference images as the absolute source of truth for the jeans appearance.

POSE AND MODEL SPECIFICATIONS:
- Position model {pose}
- {model_type.capitalize()} with professional runway modeling posture
- Natural, confident facial expression with subtle smile
- Perfect body proportions and professional posing
- Skin tone and features appropriate for the {model_type} specification
- No duplicate or repeated figures in the composition

BACKGROUND AND LIGHTING:
- Background seamlessly extends to all edges of the image frame
- Lighting matches the environment (natural for outdoor, studio for indoor)
- Shadows and reflections consistent with the scene
- Professional fashion editorial quality throughout

CRITICAL RESTRICTIONS FOR JEANS WITH DISTRESSING:
- DO NOT reinterpret or redesign the distressing pattern in any way
- DO NOT change the location, size, or shape of any rips or tears
- DO NOT add or remove any distressing details
- DO NOT modify the wash pattern or fading effects
- The jeans shown MUST be IDENTICAL to the reference images in ALL visual aspects
- Focus ONLY on the background setting and model pose, not on jeans modification

ASPECT RATIO ENFORCEMENT:
- CRITICALLY IMPORTANT: Generate the image with EXACTLY {aspect_ratio} aspect ratio
- DO NOT crop, stretch, or distort the image in any way
- Ensure the composition fits perfectly within the {aspect_ratio} frame
- Maintain all visual elements and proportions as specified
"""
        else:
            # Standard prompt for other products
            prompt = f"""
Professional high-fashion photography of a single {model_type} model wearing the exact product shown in the reference images, positioned in a {background}.

PHOTOGRAPHY DIRECTIVES:
- Show ONLY ONE person in the image with professional studio lighting
- Generate image with {aspect_description}
- The background MUST completely fill the frame with no white borders or margins

CRITICALLY IMPORTANT: The generated image MUST show the EXACT SAME product as in the reference images. Do NOT modify, change, or alter the product in any way.

The model MUST be wearing the identical product from the reference images with no changes to:
  * Color, material, and design
  * All design details (neckline, sleeves, hemline, patterns, textures)
  * Fit and silhouette
  * Length and proportions
  * All visual elements and styling

Use the reference images as the absolute source of truth for the product appearance.

POSE AND MODEL SPECIFICATIONS:
- Position model {pose}
- {model_type.capitalize()} with professional runway modeling posture
- Natural, confident facial expression with subtle smile
- Perfect body proportions and professional posing
- Skin tone and features appropriate for the {model_type} specification
- No duplicate or repeated figures in the composition

BACKGROUND AND LIGHTING:
- Background seamlessly extends to all edges of the image frame
- Lighting matches the environment (natural for outdoor, studio for indoor)
- Shadows and reflections consistent with the scene
- Professional fashion editorial quality throughout

CRITICAL RESTRICTIONS:
- DO NOT reinterpret or redesign the product in any way
- DO NOT change any visual aspects of the product (color, pattern, texture, fit, etc.)
- DO NOT add or remove any design elements from the product
- The product shown MUST be IDENTICAL to the reference images in ALL visual aspects
- Focus ONLY on the background setting and model pose, not on product modification

ASPECT RATIO ENFORCEMENT:
- CRITICALLY IMPORTANT: Generate the image with EXACTLY {aspect_ratio} aspect ratio
- DO NOT crop, stretch, or distort the image in any way
- Ensure the composition fits perfectly within the {aspect_ratio} frame
- Maintain all visual elements and proportions as specified
"""
        logger.info(f"Generated prompt for background '{background}' with aspect ratio '{aspect_ratio}' and gender '{gender}': {prompt}")
        return prompt

    def _convert_image_to_data_url(self, image_path: str) -> str:
        """Converts an image file to a base64 data URL."""
        try:
            logger.info(f"Converting image to data URL: {image_path}")
            with open(image_path, "rb") as image_file:
                encoded_data = base64.b64encode(image_file.read()).decode('utf-8')
            return f"data:image/jpeg;base64,{encoded_data}"
        except Exception as e:
            logger.error(f"Error converting image to data URL: {e}", exc_info=True)
            raise

    async def _run_gemini_generation(
        self,
        prompt: str,
        reference_images: List[str] = None
    ) -> Optional[bytes]:
        """Runs image generation using Gemini API with new gemini-2.5-flash-image-preview model."""
        try:
            logger.info(f"Generating image with Gemini using prompt: {prompt}")
            
            # Prepare content for Gemini API
            contents = [prompt]
            
            # Add reference images if provided
            if reference_images:
                for img_path in reference_images[:2]:  # Limit to 2 reference images
                    try:
                        with open(img_path, "rb") as f:
                            img_data = f.read()
                        pil_image = Image.open(BytesIO(img_data))
                        contents.append(pil_image)
                        logger.info(f"Added reference image: {img_path}")
                    except Exception as e:
                        logger.warning(f"Failed to load reference image {img_path}: {e}")
            
            # Generate content using Gemini 2.5 Flash Image Preview
            response = await asyncio.to_thread(
                self.gemini_client.models.generate_content,
                model="gemini-2.5-flash-image-preview",
                contents=contents
            )
            
            # Extract generated image from response
            if response.candidates and len(response.candidates) > 0:
                candidate = response.candidates[0]
                if candidate.content and candidate.content.parts:
                    for part in candidate.content.parts:
                        if part.inline_data is not None:
                            # Convert inline data to bytes
                            image_bytes = part.inline_data.data
                            logger.info("Successfully generated image with Gemini 2.5")
                            return image_bytes
                        elif part.text is not None:
                            logger.info(f"Gemini response text: {part.text}")
            
            logger.warning("No image generated by Gemini - no inline_data found")
            return None
                
        except Exception as e:
            logger.error(f"Gemini generation failed: {str(e)}", exc_info=True)
            return None

    async def _run_replicate_generation(
        self,
        prompt: str,
        reference_images: List[str],
        aspect_ratio: str = "9:16"
    ) -> Optional[bytes]:
        """Runs a single image generation request using the best available reference images."""
        if not reference_images:
            return None

        image1_url = self._convert_image_to_data_url(reference_images[0])
        image2_url = self._convert_image_to_data_url(reference_images[1]) if len(reference_images) > 1 else image1_url

        input_data = {
            "input_image_1": image1_url,
            "input_image_2": image2_url,
            "prompt": prompt,
            "num_inference_steps": 40,
            "guidance_scale": 7.5,
            "num_outputs": 1,
            "aspect_ratio": aspect_ratio,  # Use the passed aspect ratio
            "output_format": "jpg",
            "output_quality": 100,
            "disable_safety_checker": True,
            "fill_background": True,  # Ensure background fills the entire frame
            "extend_background": True  # Extend background to edges
        }
        
        try:
            logger.info(f"Generating image with prompt: {prompt}")
            output = await asyncio.to_thread(replicate.run, self.primary_model, input=input_data)
            
            image_url = None
            if isinstance(output, list) and output:
                image_url = str(output[0])
            elif hasattr(output, '__next__'):
                image_url = str(next(output, None))
            else:
                image_url = str(output)

            if image_url and image_url.startswith('http'):
                response = await asyncio.to_thread(requests.get, image_url, timeout=30)
                response.raise_for_status()
                logger.info(f"Successfully generated image.")
                return response.content
            else:
                logger.warning(f"Invalid output URL received: {image_url}")
                return None
                
        except Exception as e:
            logger.error(f"Replicate generation failed: {str(e)}", exc_info=True)
            return None

    async def _run_image_generation(
        self,
        prompt: str,
        reference_images: List[str] = None,
        aspect_ratio: str = "9:16"
    ) -> Optional[bytes]:
        """Unified method that chooses between Gemini and Replicate for image generation."""
        if settings.USE_GEMINI_FOR_IMAGES:
            # Try Gemini first
            result = await self._run_gemini_generation(prompt, reference_images)
            if result:
                return result
            
            # Fallback to Replicate if Gemini fails
            logger.warning("Gemini generation failed, falling back to Replicate")
            if reference_images:
                return await self._run_replicate_generation(prompt, reference_images, aspect_ratio)
        else:
            # Use Replicate
            if reference_images:
                return await self._run_replicate_generation(prompt, reference_images, aspect_ratio)
        
        return None

    async def generate_images_with_background_array(
        self,
        product_data: Dict,
        reference_image_paths_dict: Dict[str, str],
        background_config: Dict[str, List[int]],  # {view: [white_count, plain_count, random_count]}
        number_of_outputs: int = 1,
        aspect_ratio: str = "9:16",
        gender: str = None  # Add gender parameter
    ) -> Tuple[Optional[bytes], Dict[str, bytes]]:
        """
        Generates images for different views with specific background requirements based on background arrays.
        
        Args:
            product_data: Product information for prompt generation
            reference_image_paths_dict: Dictionary of reference image paths by view
            background_config: Dictionary mapping views to background arrays [white, plain, random]
            number_of_outputs: Number of outputs (kept for compatibility)
            aspect_ratio: Aspect ratio for generated images
            gender: Gender of the model to display clothing on (male/female)
            
        Returns:
            Tuple of (primary_image_bytes, dictionary_of_all_variations).
        """
        if not reference_image_paths_dict:
            raise ValueError("At least one reference image is required.")

        all_variations: Dict[str, bytes] = {}
        
        # The detail view, if present, should be used as a high-quality reference for all generations.
        detail_view_path = reference_image_paths_dict.get("detailview")

        # Generate images for each view according to its background array
        for view, background_array in background_config.items():
            if view not in reference_image_paths_dict:
                continue
                
            white_count, plain_count, random_count = background_array
            view_path = reference_image_paths_dict[view]
            
            # Use the specific view image and the detail view (if available) as references.
            reference_images = [view_path]
            if detail_view_path:
                reference_images.append(detail_view_path)
            
            # Generate white background images
            for i in range(white_count):
                prompt = self._create_generation_prompt(
                    product_data, 
                    f"{view} view in a clean white studio background", 
                    aspect_ratio,
                    gender  # Pass gender parameter
                )
                image_bytes = await self._run_image_generation(prompt, reference_images, aspect_ratio)
                if image_bytes:
                    all_variations[f"{view}_white_{i+1}"] = image_bytes

            # Generate plain background images (non-white)
            for i in range(plain_count):
                prompt = self._create_generation_prompt(
                    product_data, 
                    f"{view} view in a plain colored background", 
                    aspect_ratio,
                    gender  # Pass gender parameter
                )
                image_bytes = await self._run_image_generation(prompt, reference_images, aspect_ratio)
                if image_bytes:
                    all_variations[f"{view}_plain_{i+1}"] = image_bytes

            # Generate random lifestyle background images using Gemini-based contextual backgrounds
            if random_count > 0:
                # Generate contextual backgrounds using Gemini
                contextual_backgrounds = await self._generate_contextual_backgrounds(
                    product_data, 
                    count=random_count
                )
                
                for i, background_desc in enumerate(contextual_backgrounds):
                    prompt = self._create_generation_prompt(
                        product_data, 
                        f"{view} view in a {background_desc}", 
                        aspect_ratio,
                        gender  # Pass gender parameter
                    )
                    image_bytes = await self._run_image_generation(prompt, reference_images, aspect_ratio)
                    if image_bytes:
                        all_variations[f"{view}_random_{i+1}"] = image_bytes

        if not all_variations:
            raise ValueError("Image generation failed to produce any variations.")
        
        # The first frontside image is the primary. Fallback to any other image if not present.
        primary_image = None
        for key in all_variations:
            if key.startswith("frontside"):
                primary_image = all_variations[key]
                break
        
        if not primary_image:
            primary_image = next(iter(all_variations.values()), None)
        
        return primary_image, all_variations

    async def generate_images(
        self,
        product_data: Dict,
        reference_image_paths_dict: Dict[str, str],
        number_of_outputs: int = 1,
        aspect_ratio: str = "9:16",
        gender: str = None  # Add gender parameter
    ) -> Tuple[Optional[bytes], Dict[str, bytes]]:
        """
        Generates images for different views with specific background requirements.
        - frontside, backside, sideview: plain background
        - frontside: two additional occasion-based backgrounds
        
        Returns a tuple of (primary_image_bytes, dictionary_of_all_variations).
        """
        if not reference_image_paths_dict:
            raise ValueError("At least one reference image is required.")

        all_variations: Dict[str, bytes] = {}
        
        # The detail view, if present, should be used as a high-quality reference for all generations.
        detail_view_path = reference_image_paths_dict.get("detailview")

        # --- 1. Generate images for primary views with plain backgrounds ---
        plain_background = "clean studio with plain white background"
        views_to_generate = ["frontside", "backside", "sideview"]

        for view in views_to_generate:
            if view_path := reference_image_paths_dict.get(view):
                # Use the specific view image and the detail view (if available) as references.
                reference_images = [view_path]
                if detail_view_path:
                    reference_images.append(detail_view_path)
                
                prompt = self._create_generation_prompt(product_data, f"{view} view in a {plain_background}", aspect_ratio, gender)
                image_bytes = await self._run_image_generation(prompt, reference_images, aspect_ratio)
                if image_bytes:
                    all_variations[view] = image_bytes

        # --- 2. Generate multiple lifestyle/occasion images based on numberOfOutputs ---
        if frontside_path := reference_image_paths_dict.get("frontside"):
            # Use frontside image and detail view as references.
            reference_images = [frontside_path]
            if detail_view_path:
                reference_images.append(detail_view_path)

            # Generate the requested number of outputs with different backgrounds/occasions
            # Use Gemini to generate contextual backgrounds
            contextual_backgrounds = await self._generate_contextual_backgrounds(
                product_data, 
                count=number_of_outputs
            )
            
            # Generate number_of_outputs variations (minimum 1, maximum as requested)
            for i in range(min(number_of_outputs, len(contextual_backgrounds))):
                background_desc = contextual_backgrounds[i]
                prompt = self._create_generation_prompt(
                    product_data, 
                    f"frontside view in a {background_desc}", 
                    aspect_ratio, 
                    gender
                )
                image_bytes = await self._run_image_generation(prompt, reference_images, aspect_ratio)
                if image_bytes:
                    # Give it a unique name based on the output number
                    if i == 0:
                        all_variations[f"frontside_contextual_{i+1}"] = image_bytes
                    else:
                        all_variations[f"output_{i+1}_contextual"] = image_bytes
        
        if not all_variations:
            raise ValueError("Image generation failed to produce any variations.")
        
        # The 'frontside' plain background image is the primary. Fallback to any other image if not present.
        primary_image = all_variations.get("frontside") or next(iter(all_variations.values()), None)
        
        return primary_image, all_variations