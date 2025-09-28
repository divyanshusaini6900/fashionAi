import requests
import asyncio
import os
import replicate
from fastapi import HTTPException
from app.core.config import settings
from typing import Dict
import base64
import time
from io import BytesIO
from PIL import Image

# Conditional imports based on configuration
if settings.USE_GEMINI_FOR_VIDEOS:
    from google import genai
    from google.genai import types

class VideoGenerator:
    def __init__(self):
        """Initializes the video generator with both Gemini and Replicate support."""
        # Replicate configuration (fallback)
        self.model_name = "kwaivgi/kling-v2.1"
        
        # Initialize Gemini client if enabled
        if settings.USE_GEMINI_FOR_VIDEOS:
            try:
                self.gemini_client = genai.Client(api_key=settings.GEMINI_API_KEY)
                print("Gemini API client initialized for video generation")
            except Exception as e:
                print(f"Failed to initialize Gemini client: {e}")
                print("Falling back to Replicate for video generation")
                settings.USE_GEMINI_FOR_VIDEOS = False
        
        # Initialize Replicate if needed
        if not settings.USE_GEMINI_FOR_VIDEOS:
            if not os.environ.get("REPLICATE_API_TOKEN"):
                os.environ["REPLICATE_API_TOKEN"] = settings.REPLICATE_API_TOKEN
            print(f"VideoGenerator initialized with Replicate model: {self.model_name}")
        
        print(f"Video generation mode: {'Gemini' if settings.USE_GEMINI_FOR_VIDEOS else 'Replicate'}")

    def _convert_image_to_data_url(self, image_path_or_url: str) -> str:
        """Converts an image file or URL to a base64 data URL."""
        try:
            if image_path_or_url.startswith("http"):
                response = requests.get(image_path_or_url)
                response.raise_for_status()
                image_bytes = response.content
            else:
                with open(image_path_or_url, "rb") as image_file:
                    image_bytes = image_file.read()
            
            encoded_data = base64.b64encode(image_bytes).decode('utf-8')
            return f"data:image/jpeg;base64,{encoded_data}"
        except Exception as e:
            print(f"Error converting image to data URL: {e}")
            raise

    async def _isVideo_with_gemini(
        self,
        image_path: str,
        prompt: str
    ) -> bytes:
        """Generate video using Gemini Veo API."""
        try:
            print("Generating video with Gemini Veo...")
            
            # Load the image
            if image_path.startswith("http"):
                response = requests.get(image_path)
                response.raise_for_status()
                image_bytes = response.content
                image = Image.open(BytesIO(image_bytes))
            else:
                image = Image.open(image_path)
            
            # Step 1: Generate a reference image using Imagen (if needed)
            imagen_response = await asyncio.to_thread(
                self.gemini_client.models.generate_images,
                model="imagen-4.0-generate-001",
                prompt=prompt,
            )
            
            # Step 2: Generate video with Veo 3 using the input image
            operation = await asyncio.to_thread(
                self.gemini_client.models.isVideos,
                model="veo-3.0-generate-001",
                prompt=prompt,
                image=image,
            )
            
            # Poll the operation status until the video is ready
            while not operation.done:
                print("Waiting for video generation to complete...")
                await asyncio.sleep(10)
                operation = await asyncio.to_thread(
                    self.gemini_client.operations.get,
                    operation
                )
            
            # Download the video
            video = operation.response.generated_videos[0]
            video_file = await asyncio.to_thread(
                self.gemini_client.files.download,
                file=video.video
            )
            
            # Read video bytes
            with open(video_file, "rb") as f:
                video_bytes = f.read()
            
            # Clean up temporary file
            os.remove(video_file)
            
            print("Successfully generated video with Gemini")
            return video_bytes
            
        except Exception as e:
            print(f"Gemini video generation failed: {str(e)}")
            raise

    async def _isVideo_with_replicate(
        self,
        image_path: str,
        prompt: str,
        video_length: int = 5
    ) -> bytes:
        """Generate video using Replicate API."""
        try:
            # Convert the local image or URL to a data URL
            image_data_url = self._convert_image_to_data_url(image_path)
            
            # Prepare the input payload for the Replicate API
            payload = {
                "start_image": image_data_url,
                "prompt": prompt,
                "duration": video_length,
                "mode": "standard", # 'standard' for 720p, 'pro' for 1080p
                "negative_prompt": "blurry, distorted, low quality, unrealistic movements, watermarks",
            }

            # Make the API call using the replicate client
            print("Submitting video generation request to Replicate...")
            output = await asyncio.to_thread(replicate.run, self.model_name, input=payload)
            
            # Check if the output is a URL and fetch the content
            if isinstance(output, str) and output.startswith('http'):
                response = await asyncio.to_thread(requests.get, output, timeout=60)
                response.raise_for_status()
                return response.content
            
            # Fallback for other possible output types
            if hasattr(output, 'read'):
                return await asyncio.to_thread(output.read)

            raise HTTPException(status_code=500, detail="Unexpected output from Replicate video generation API.")
            
        except Exception as e:
            print(f"Replicate video generation failed: {str(e)}")
            raise

    async def isVideo(
        self,
        image_path: str,
        product_data: Dict,
        video_length: int = 5
    ) -> bytes:
        """
        Generates a video using either Gemini or Replicate API based on configuration.
        
        Args:
            image_path: Path or URL to the input lifestyle image.
            product_data: Dictionary containing product information for the prompt.
            video_length: Length of the video in seconds (5 or 10).
            
        Returns:
            The generated video as bytes.
        """
        try:
            # Create a descriptive prompt from product data
            ideal_for = product_data.get('Ideal For', 'a person')
            occasion = product_data.get('Occasion', 'a professional')
            title = product_data.get('Title', 'fashion item')
            
            prompt = (
                f"A cinematic video of a {ideal_for.lower()} model wearing '{title}'. "
                "The model moves naturally and elegantly,towards the camera. Showcasing the product from only front angle (no side angles). "
                "The lighting is professional, and the video quality is high."
                "Maintain the consistency of the model's clothing and accessories."
                "Lighting should be natural and not too bright."
                "The background must be a clean, plain studio background, matching the input image."
            )

            # Choose API based on configuration
            if settings.USE_GEMINI_FOR_VIDEOS:
                try:
                    return await self._isVideo_with_gemini(image_path, prompt)
                except Exception as e:
                    print(f"Gemini video generation failed, falling back to Replicate: {e}")
                    return await self._isVideo_with_replicate(image_path, prompt, video_length)
            else:
                return await self._isVideo_with_replicate(image_path, prompt, video_length)
            
        except Exception as e:
            print(f"Video generation failed: {str(e)}")
            import traceback
            traceback.print_exc()
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate video: {str(e)}"
            ) 