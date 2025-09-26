"""
Concurrent Image Generator with Parallel Processing
Optimized for handling multiple image generation requests simultaneously
"""
import asyncio
import aiohttp
import logging
from typing import Dict, List, Optional, Tuple, Any
from concurrent.futures import ThreadPoolExecutor
import time
from dataclasses import dataclass

from app.services.image_generator import ImageGenerator
from app.services.task_queue import submit_task, wait_for_task
from app.core.config import settings

logger = logging.getLogger(__name__)

@dataclass
class ImageGenerationTask:
    """Data class for image generation tasks"""
    prompt: str
    reference_images: List[str]
    aspect_ratio: str
    task_id: str
    view_name: str
    background_type: str

class ConcurrentImageGenerator(ImageGenerator):
    """
    Enhanced image generator with concurrent processing capabilities
    """
    
    def __init__(self):
        super().__init__()
        self.session_pool = None
        self.executor = ThreadPoolExecutor(max_workers=5)  # For CPU-bound tasks
        self.max_concurrent_generations = 10  # Maximum concurrent image generations
        
    async def __aenter__(self):
        """Async context manager entry"""
        # Create persistent aiohttp session for better connection pooling
        connector = aiohttp.TCPConnector(
            limit=20,  # Total connection pool size
            limit_per_host=5,  # Max connections per host
            ttl_dns_cache=300,  # DNS cache TTL
            use_dns_cache=True,
            keepalive_timeout=30,
            enable_cleanup_closed=True
        )
        
        timeout = aiohttp.ClientTimeout(total=300, connect=30)  # 5 minute total timeout
        self.session_pool = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout
        )
        
        logger.info("ConcurrentImageGenerator session pool initialized")
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session_pool:
            await self.session_pool.close()
        self.executor.shutdown(wait=True)
        logger.info("ConcurrentImageGenerator session pool closed")
    
    async def _fetch_image_concurrent(self, url: str) -> Optional[bytes]:
        """Fetch image using persistent session pool"""
        try:
            if not self.session_pool:
                # Fallback to regular requests if session not initialized
                return await super()._fetch_image_from_url(url)
                
            async with self.session_pool.get(url) as response:
                response.raise_for_status()
                return await response.read()
                
        except Exception as e:
            logger.error(f"Error fetching image from {url}: {e}")
            return None
    
    async def _generate_single_image_concurrent(
        self,
        task: ImageGenerationTask
    ) -> Optional[bytes]:
        """Generate a single image with improved error handling and retries"""
        max_retries = 3
        base_delay = 1
        
        for attempt in range(max_retries):
            try:
                # Add jitter to prevent thundering herd
                if attempt > 0:
                    delay = base_delay * (2 ** attempt) + (asyncio.get_event_loop().time() % 1)
                    await asyncio.sleep(delay)
                
                logger.info(f"Generating image for {task.view_name}_{task.background_type} (attempt {attempt + 1})")
                
                # Use the existing generation method with timeout
                result = await asyncio.wait_for(
                    self._run_image_generation(task.prompt, task.reference_images, task.aspect_ratio),
                    timeout=180  # 3 minute timeout per generation
                )
                
                if result:
                    logger.info(f"Successfully generated image for {task.view_name}_{task.background_type}")
                    return result
                else:
                    logger.warning(f"No result from generation for {task.view_name}_{task.background_type}")
                    
            except asyncio.TimeoutError:
                logger.error(f"Timeout generating image for {task.view_name}_{task.background_type} (attempt {attempt + 1})")
            except Exception as e:
                logger.error(f"Error generating image for {task.view_name}_{task.background_type} (attempt {attempt + 1}): {e}")
        
        logger.error(f"Failed to generate image for {task.view_name}_{task.background_type} after {max_retries} attempts")
        return None
    
    async def generate_images_concurrent(
        self,
        product_data: Dict,
        reference_image_paths_dict: Dict[str, str],
        number_of_outputs: int = 1,
        aspect_ratio: str = "9:16",
        gender: str = None
    ) -> Tuple[Optional[bytes], Dict[str, bytes]]:
        """
        Generate images concurrently for better performance
        """
        if not reference_image_paths_dict:
            raise ValueError("At least one reference image is required.")

        all_variations: Dict[str, bytes] = {}
        tasks: List[ImageGenerationTask] = []
        
        # Detail view for high-quality reference
        detail_view_path = reference_image_paths_dict.get("detailview")

        # Create generation tasks for primary views
        plain_background = "clean studio with plain white background"
        views_to_generate = ["frontside", "backside", "sideview"]

        for view in views_to_generate:
            if view_path := reference_image_paths_dict.get(view):
                reference_images = [view_path]
                if detail_view_path:
                    reference_images.append(detail_view_path)
                
                prompt = self._create_generation_prompt(
                    product_data, 
                    f"{view} view in a {plain_background}", 
                    aspect_ratio, 
                    gender
                )
                
                task = ImageGenerationTask(
                    prompt=prompt,
                    reference_images=reference_images,
                    aspect_ratio=aspect_ratio,
                    task_id=f"{view}_plain",
                    view_name=view,
                    background_type="plain"
                )
                tasks.append(task)

        # Create tasks for lifestyle images
        if frontside_path := reference_image_paths_dict.get("frontside"):
            reference_images = [frontside_path]
            if detail_view_path:
                reference_images.append(detail_view_path)

            occasions = [
                "social_gathering", "formal_event", "casual_outing", 
                "party_venue", "outdoor_setting", "studio_portrait"
            ]
            
            for i in range(min(number_of_outputs, len(occasions))):
                occasion = occasions[i]
                prompt = self._create_generation_prompt(
                    product_data, 
                    f"frontside view for a {occasion.replace('_', ' ')}", 
                    aspect_ratio, 
                    gender
                )
                
                task = ImageGenerationTask(
                    prompt=prompt,
                    reference_images=reference_images,
                    aspect_ratio=aspect_ratio,
                    task_id=f"frontside_{occasion}",
                    view_name="frontside",
                    background_type=occasion
                )
                tasks.append(task)

        # Execute tasks concurrently with concurrency limit
        logger.info(f"Starting concurrent generation of {len(tasks)} images")
        
        # Use semaphore to limit concurrent generations
        semaphore = asyncio.Semaphore(min(self.max_concurrent_generations, len(tasks)))
        
        async def limited_generation(task: ImageGenerationTask):
            async with semaphore:
                return await self._generate_single_image_concurrent(task)
        
        # Run all generations concurrently
        start_time = time.time()
        results = await asyncio.gather(
            *[limited_generation(task) for task in tasks],
            return_exceptions=True
        )
        
        generation_time = time.time() - start_time
        logger.info(f"Completed {len(tasks)} concurrent image generations in {generation_time:.2f}s")
        
        # Process results
        successful_generations = 0
        for task, result in zip(tasks, results):
            if isinstance(result, Exception):
                logger.error(f"Task {task.task_id} failed with exception: {result}")
            elif result:
                # Map task to variation name
                if task.view_name == "frontside" and task.background_type != "plain":
                    if task.background_type == occasions[0]:
                        all_variations[f"frontside_{task.background_type}"] = result
                    else:
                        idx = occasions.index(task.background_type) + 1
                        all_variations[f"output_{idx}_{task.background_type}"] = result
                else:
                    all_variations[task.view_name] = result
                successful_generations += 1
            else:
                logger.warning(f"Task {task.task_id} returned no result")
        
        logger.info(f"Successfully generated {successful_generations}/{len(tasks)} images")
        
        if not all_variations:
            raise ValueError("All image generation tasks failed.")
        
        # Primary image selection
        primary_image = all_variations.get("frontside") or next(iter(all_variations.values()), None)
        
        return primary_image, all_variations

    async def generate_images_with_background_array_concurrent(
        self,
        product_data: Dict,
        reference_image_paths_dict: Dict[str, str],
        background_config: Dict[str, List[int]],
        number_of_outputs: int = 1,
        aspect_ratio: str = "9:16",
        gender: str = None
    ) -> Tuple[Optional[bytes], Dict[str, bytes]]:
        """
        Generate images with background array configuration using concurrent processing
        """
        if not reference_image_paths_dict:
            raise ValueError("At least one reference image is required.")

        all_variations: Dict[str, bytes] = {}
        tasks: List[ImageGenerationTask] = []
        
        detail_view_path = reference_image_paths_dict.get("detailview")

        # Create tasks for each view according to background array
        for view, background_array in background_config.items():
            if view not in reference_image_paths_dict:
                continue
                
            white_count, plain_count, random_count = background_array
            view_path = reference_image_paths_dict[view]
            
            reference_images = [view_path]
            if detail_view_path:
                reference_images.append(detail_view_path)
            
            # White background tasks
            for i in range(white_count):
                prompt = self._create_generation_prompt(
                    product_data, 
                    f"{view} view in a clean white studio background", 
                    aspect_ratio,
                    gender
                )
                task = ImageGenerationTask(
                    prompt=prompt,
                    reference_images=reference_images,
                    aspect_ratio=aspect_ratio,
                    task_id=f"{view}_white_{i+1}",
                    view_name=view,
                    background_type=f"white_{i+1}"
                )
                tasks.append(task)

            # Plain background tasks  
            for i in range(plain_count):
                prompt = self._create_generation_prompt(
                    product_data, 
                    f"{view} view in a plain colored background", 
                    aspect_ratio,
                    gender
                )
                task = ImageGenerationTask(
                    prompt=prompt,
                    reference_images=reference_images,
                    aspect_ratio=aspect_ratio,
                    task_id=f"{view}_plain_{i+1}",
                    view_name=view,
                    background_type=f"plain_{i+1}"
                )
                tasks.append(task)

            # Random lifestyle background tasks
            occasions = [
                "modern urban cafe with natural lighting",
                "peaceful garden setting with soft sunlight", 
                "contemporary living room with large windows",
                "elegant evening party venue with warm lighting",
                "upscale rooftop lounge at sunset",
                "luxurious indoor party setting with ambient lighting",
                "grand wedding venue with decorative elements",
                "outdoor garden wedding setup",
                "elegant ballroom with chandeliers",
                "scenic beach during golden hour",
                "tropical resort poolside",
                "beachfront terrace with ocean view",
                "sophisticated hotel lobby",
                "upscale restaurant interior",
                "classic architectural backdrop"
            ]
            
            for i in range(min(random_count, len(occasions))):
                occasion = occasions[i]
                prompt = self._create_generation_prompt(
                    product_data, 
                    f"{view} view in a {occasion}", 
                    aspect_ratio,
                    gender
                )
                task = ImageGenerationTask(
                    prompt=prompt,
                    reference_images=reference_images,
                    aspect_ratio=aspect_ratio,
                    task_id=f"{view}_random_{i+1}",
                    view_name=view,
                    background_type=f"random_{i+1}"
                )
                tasks.append(task)

        if not tasks:
            raise ValueError("No generation tasks created from background configuration.")

        # Execute tasks concurrently
        logger.info(f"Starting concurrent generation of {len(tasks)} images with background array")
        
        semaphore = asyncio.Semaphore(min(self.max_concurrent_generations, len(tasks)))
        
        async def limited_generation(task: ImageGenerationTask):
            async with semaphore:
                return await self._generate_single_image_concurrent(task)
        
        start_time = time.time()
        results = await asyncio.gather(
            *[limited_generation(task) for task in tasks],
            return_exceptions=True
        )
        
        generation_time = time.time() - start_time
        logger.info(f"Completed {len(tasks)} concurrent background array generations in {generation_time:.2f}s")
        
        # Process results
        successful_generations = 0
        for task, result in zip(tasks, results):
            if isinstance(result, Exception):
                logger.error(f"Task {task.task_id} failed with exception: {result}")
            elif result:
                all_variations[task.task_id] = result
                successful_generations += 1
            else:
                logger.warning(f"Task {task.task_id} returned no result")
        
        logger.info(f"Successfully generated {successful_generations}/{len(tasks)} background array images")
        
        if not all_variations:
            raise ValueError("All background array generation tasks failed.")
        
        # Primary image selection - first frontside image
        primary_image = None
        for key in all_variations:
            if key.startswith("frontside"):
                primary_image = all_variations[key]
                break
        
        if not primary_image:
            primary_image = next(iter(all_variations.values()), None)
        
        return primary_image, all_variations

    async def _fetch_image_from_url(self, url: str) -> Optional[bytes]:
        """Override parent method to use session pool if available"""
        if self.session_pool:
            return await self._fetch_image_concurrent(url)
        else:
            return await super()._fetch_image_from_url(url)
