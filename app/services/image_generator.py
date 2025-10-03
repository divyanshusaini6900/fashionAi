import replicate
import requests
import asyncio
import re
import json
from fastapi import HTTPException
from app.core.config import settings
from typing import List, Optional, Dict, Tuple
import base64
import logging
import os
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

    def _get_view_specific_pose(self, view: str) -> str:
        """
        Returns pose recommendations based on the view of the image.
        """
        view_pose_mapping = {
            "front": [
                "Standing straight with arms relaxed at sides, showcasing the full front of the outfit",
                "Confident pose with hands on hips, emphasizing the fit and design of the garment",
                "Front-facing three-quarter view with slight body turn for dynamic composition"
            ],
            "back": [
                "Standing straight with back facing camera, showing the complete back design",
                "Casual pose with hands behind back, highlighting back details and fit",
                "Three-quarter back view with slight turn to show side profile"
            ],
            "side": [
                "Profile view showing the side silhouette of the outfit",
                "Side view with one arm raised to showcase sleeve design",
                "Dynamic side pose with weight on one leg for natural body curve"
            ],
            "detail": [
                "Close-up pose focusing on specific garment details",
                "Static pose allowing clear visibility of textures and patterns",
                "Controlled positioning to highlight unique design elements"
            ]
        }
        
        # Normalize view names
        normalized_view = view.lower().strip()
        if normalized_view in ["frontside", "front"]:
            pose_list = view_pose_mapping["front"]
        elif normalized_view in ["backside", "back"]:
            pose_list = view_pose_mapping["back"]
        elif normalized_view in ["sideview", "side"]:
            pose_list = view_pose_mapping["side"]
        elif normalized_view in ["detailview", "detail"]:
            pose_list = view_pose_mapping["detail"]
        else:
            # Default to front poses if view is not recognized
            pose_list = view_pose_mapping["front"]
            
        # Return the first pose recommendation as a string
        return pose_list[0] if pose_list else "Standing straight with natural posture showcasing the outfit"

    async def _get_background_variations(self, occasion: str, product_data: Dict, aspect_ratio: str = "9:16") -> List[str]:
        """
        Dynamically generates background variations based on the occasion using Gemini AI.
        Returns a list of background descriptions.
        """
        # Base backgrounds - always include a plain studio background
        backgrounds = ["clean studio with plain white background"]
        
        # Map aspect ratio to descriptive text for background generation
        aspect_ratio_descriptions = {
            "1:1": "square format (equal width and height)",
            "16:9": "wide landscape format (width 1.78x height)",
            "4:3": "standard landscape format (width 1.33x height)",
            "3:4": "portrait format (height 1.33x width)",
            "9:16": "tall portrait format (height 1.78x width)"
        }
        
        aspect_description = aspect_ratio_descriptions.get(aspect_ratio, "tall portrait format (height 1.78x width)")
        
        # Only generate dynamic backgrounds if Gemini is enabled for images
        if settings.USE_GEMINI_FOR_IMAGES and hasattr(self, 'gemini_client'):
            try:
                # Create a prompt for Gemini to generate background ideas
                prompt = f"""You are a creative fashion photographer and set designer. Based on the following product information, occasion, and aspect ratio, generate 3 unique and creative background ideas that would perfectly complement this fashion item for a lifestyle photo shoot.

Product Information:
- Title: {product_data.get('Title', 'Fashion Item')}
- Description: {product_data.get('Description', 'A stylish fashion item')}
- Occasion: {occasion}
- Ideal For: {product_data.get('Ideal For', 'General Use')}
- Image Format: {aspect_description}

Please provide 3 background descriptions that would enhance the visual appeal of this product for the specified occasion and aspect ratio. Each background should be a complete, detailed description that a photographer could use directly. Make them creative and specific. Consider how the aspect ratio affects the composition and background design.

Return your response as a JSON array of 3 strings, like this:
["background1 description", "background2 description", "background3 description"]"""
                
                # Call Gemini to generate background ideas
                logger.info(f"Requesting Gemini to generate background ideas for occasion: {occasion}")
                response = await asyncio.to_thread(
                    self.gemini_client.models.generate_content,
                    model="gemini-2.0-flash-exp",
                    contents=[prompt]
                )
                
                # Parse the response
                if response.text:
                    # Try to extract JSON array from response
                    import re
                    import json
                    
                    # Look for JSON array in the response
                    json_match = re.search(r'\[[^\]]*\]', response.text)
                    if json_match:
                        background_array = json.loads(json_match.group())
                        backgrounds.extend(background_array[:3])  # Add up to 3 generated backgrounds
                        logger.info(f"Successfully generated {len(background_array[:3])} background variations with Gemini")
                    else:
                        # Fallback: use the whole response as a single background
                        backgrounds.append(response.text[:200])  # Limit length
                        logger.warning("Could not parse JSON from Gemini response, using raw text")
                
            except Exception as e:
                logger.error(f"Failed to generate backgrounds with Gemini: {e}")
                # Fallback to predefined backgrounds if Gemini fails
                occasion_backgrounds = {
                    "casual": [
                        "modern urban cafe with natural lighting",
                        "peaceful garden setting with soft sunlight",
                        "contemporary living room with large windows"
                    ],
                    "party": [
                        "elegant evening party venue with warm lighting",
                        "upscale rooftop lounge at sunset",
                        "luxurious indoor party setting with ambient lighting"
                    ],
                    "wedding": [
                        "grand wedding venue with decorative elements",
                        "outdoor garden wedding setup",
                        "elegant ballroom with chandeliers"
                    ],
                    "beach": [
                        "scenic beach during golden hour",
                        "tropical resort poolside",
                        "beachfront terrace with ocean view"
                    ],
                    "formal": [
                        "sophisticated hotel lobby",
                        "upscale restaurant interior",
                        "classic architectural backdrop"
                    ]
                }
                
                # Get background options based on occasion, defaulting to casual if not found
                additional_backgrounds = occasion_backgrounds.get(
                    occasion.lower(),
                    occasion_backgrounds["casual"]
                )
                
                # Add three background variations
                backgrounds.extend(additional_backgrounds[:3])
        else:
            # Fallback to predefined backgrounds if Gemini is not enabled
            occasion_backgrounds = {
                "casual": [
                    "modern urban cafe with natural lighting",
                    "peaceful garden setting with soft sunlight",
                    "contemporary living room with large windows"
                ],
                "party": [
                    "elegant evening party venue with warm lighting",
                    "upscale rooftop lounge at sunset",
                    "luxurious indoor party setting with ambient lighting"
                ],
                "wedding": [
                    "grand wedding venue with decorative elements",
                    "outdoor garden wedding setup",
                    "elegant ballroom with chandeliers"
                ],
                "beach": [
                    "scenic beach during golden hour",
                    "tropical resort poolside",
                    "beachfront terrace with ocean view"
                ],
                "formal": [
                    "sophisticated hotel lobby",
                    "upscale restaurant interior",
                    "classic architectural backdrop"
                ]
            }
            
            # Get background options based on occasion, defaulting to casual if not found
            additional_backgrounds = occasion_backgrounds.get(
                occasion.lower(),
                occasion_backgrounds["casual"]
            )
            
            # Add three background variations
            backgrounds.extend(additional_backgrounds[:3])
        
        return backgrounds[:4]  # Ensure we only return 4 variations

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
        
        # Map aspect ratio to descriptive text
        aspect_ratio_descriptions = {
            "1:1": "square aspect ratio (1:1, equal width and height)",
            "16:9": "landscape orientation with 16:9 aspect ratio (width 1.78x height)",
            "4:3": "landscape orientation with 4:3 aspect ratio (width 1.33x height)",
            "3:4": "portrait orientation with 3:4 aspect ratio (height 1.33x width)",
            "9:16": "portrait orientation with 9:16 aspect ratio (height 1.78x width)"
        }
        
        aspect_description = aspect_ratio_descriptions.get(aspect_ratio, "portrait orientation with 9:16 aspect ratio (height 1.78x width)")
        
        # Get model pose recommendations from product data, if available
        model_poses = product_data.get('ModelPoses', [])
        pose_description = ""
        if model_poses and len(model_poses) > 0:
            # Use the first pose recommendation
            pose_description = f"- Position model in a {model_poses[0]}"
        else:
            # Default pose guidance
            pose_description = "- Position model with confident, natural posture showcasing the outfit"

        # Get view-specific pose recommendations
        if view:
            pose_description = f"- Position model in a {self._get_view_specific_pose(view)}"
        else:
            # Use default pose guidance if no view is specified
            pose_description = "- Position model with confident, natural posture showcasing the outfit"

        # Check if this is a Jeans product and get distressing details
        distressing_details = product_data.get('DistressingDetails', [])
        distressing_description = ""
        if distressing_details and len(distressing_details) > 0:
            distressing_text = "\nDISTRESSING DETAILS:\n"
            for detail in distressing_details:
                location = detail.get('location', 'unknown area')
                distress_type = detail.get('type', 'distressed')
                severity = detail.get('severity', 'medium')
                description = detail.get('description', '')
                distressing_text += f"- {location}: {distress_type} ({severity} severity) - {description}\n"
            distressing_description = distressing_text
        
        # Enhanced prompt with advanced fashion photography techniques
        prompt = f"""
Professional high-fashion photography of a single {model_type} model wearing the exact product from the reference images, positioned in a {background}.

PHOTOGRAPHY DIRECTIVES:
- Show ONLY ONE person in the image with professional studio lighting
- Generate image with {aspect_description}
- The background MUST completely fill the frame with no white borders or margins
- Follow the reference images exactly for:
  * Dress color, material, and design
  * All design details (neckline, sleeves, hemline)
  * Pattern and fabric texture
  * Fit and silhouette
  * Length and proportions{distressing_description}

ADVANCED FASHION PHOTOGRAPHY TECHNIQUES:
- Use cinematic lighting with dramatic shadows to highlight fabric texture
- Apply golden hour lighting principles for natural skin tones
{pose_description}
- Ensure perfect color matching between reference and generated clothing
- Capture intricate details like stitching, embroidery, and fabric weave
- Use shallow depth of field to focus on the garment while blurring background slightly

MODEL SPECIFICATIONS:
- {model_type.capitalize()} with professional runway modeling posture
- Natural, confident facial expression with subtle smile
- Perfect body proportions and professional posing
- Skin tone and features appropriate for the {model_type} specification
- No duplicate or repeated figures in the composition

ENVIRONMENTAL INTEGRATION:
- Background seamlessly extends to all edges of the image frame
- Lighting matches the environment (natural for outdoor, studio for indoor)
- Shadows and reflections consistent with the scene
- Professional fashion editorial quality throughout
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
                    gender,  # Pass gender parameter
                    view      # Pass view parameter for pose-specific generation
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
                    gender,  # Pass gender parameter
                    view      # Pass view parameter for pose-specific generation
                )
                image_bytes = await self._run_image_generation(prompt, reference_images, aspect_ratio)
                if image_bytes:
                    all_variations[f"{view}_plain_{i+1}"] = image_bytes

            # Generate random lifestyle background images using dynamic backgrounds from Gemini
            # Extract occasion from product data for background generation
            occasion = product_data.get('Occasion', 'casual').lower()
            dynamic_backgrounds = await self._get_background_variations(occasion, product_data, aspect_ratio)
            
            # Skip the first background (studio) and use the dynamic ones
            lifestyle_backgrounds = dynamic_backgrounds[1:] if len(dynamic_backgrounds) > 1 else dynamic_backgrounds
            
            for i in range(min(random_count, len(lifestyle_backgrounds))):
                background_desc = lifestyle_backgrounds[i]
                prompt = self._create_generation_prompt(
                    product_data, 
                    f"{view} view in a {background_desc}", 
                    aspect_ratio,
                    gender,  # Pass gender parameter
                    view      # Pass view parameter for pose-specific generation
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
                
                prompt = self._create_generation_prompt(product_data, f"{view} view in a {plain_background}", aspect_ratio, gender, view)
                image_bytes = await self._run_image_generation(prompt, reference_images, aspect_ratio)
                if image_bytes:
                    all_variations[view] = image_bytes

        # --- 2. Generate multiple lifestyle/occasion images based on numberOfOutputs ---
        if frontside_path := reference_image_paths_dict.get("frontside"):
            # Use frontside image and detail view as references.
            reference_images = [frontside_path]
            if detail_view_path:
                reference_images.append(detail_view_path)

            # Generate the requested number of outputs with dynamic backgrounds from Gemini
            # Extract occasion from product data for background generation
            occasion = product_data.get('Occasion', 'casual').lower()
            dynamic_backgrounds = await self._get_background_variations(occasion, product_data, aspect_ratio)
            
            # Skip the first background (studio) and use the dynamic ones
            lifestyle_backgrounds = dynamic_backgrounds[1:] if len(dynamic_backgrounds) > 1 else dynamic_backgrounds
            
            # Generate number_of_outputs variations (minimum 1, maximum as requested)
            for i in range(min(number_of_outputs, len(lifestyle_backgrounds))):
                background_desc = lifestyle_backgrounds[i]
                # Clean up the background description for naming
                clean_name = background_desc.replace(' ', '_').replace('-', '_')[:30]  # Limit length
                prompt = self._create_generation_prompt(product_data, f"frontside view in a {background_desc}", aspect_ratio, gender, "frontside")
                image_bytes = await self._run_image_generation(prompt, reference_images, aspect_ratio)
                if image_bytes:
                    # Give it a unique name based on the background
                    if i == 0:
                        all_variations[f"frontside_{clean_name}"] = image_bytes
                    else:
                        all_variations[f"output_{i+1}_{clean_name}"] = image_bytes
        
        if not all_variations:
            raise ValueError("Image generation failed to produce any variations.")
        
        # The 'frontside' plain background image is the primary. Fallback to any other image if not present.
        primary_image = all_variations.get("frontside") or next(iter(all_variations.values()), None)
        
        return primary_image, all_variations
