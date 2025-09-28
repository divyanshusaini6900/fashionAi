"""
Concurrent Image Upscaler with Parallel Processing
Optimized for upscaling multiple images simultaneously
"""
import asyncio
import logging
from typing import Dict, Optional, List, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from dataclasses import dataclass

from app.services.image_upscaler import ImageUpscaler

logger = logging.getLogger(__name__)

@dataclass
class UpscaleTask:
    """Data class for upscale tasks"""
    key: str
    image_bytes: bytes
    scale: int = 4

class ConcurrentUpscaler:
    """
    Concurrent image upscaler for processing multiple images in parallel
    """
    
    def __init__(self, max_workers: int = 3):
        """
        Initialize concurrent upscaler
        
        Args:
            max_workers: Maximum number of parallel upscaling threads
        """
        self.upscaler = ImageUpscaler()
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        logger.info(f"ConcurrentUpscaler initialized with {max_workers} workers")
    
    def __del__(self):
        """Cleanup executor on destruction"""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)
    
    async def upscale_images_concurrent(
        self, 
        images_dict: Dict[str, bytes], 
        scale: int = 4
    ) -> Dict[str, bytes]:
        """
        Upscale multiple images concurrently
        
        Args:
            images_dict: Dictionary of {key: image_bytes}
            scale: Upscaling factor
            
        Returns:
            Dict[str, bytes]: Dictionary of upscaled images
        """
        if not images_dict:
            logger.warning("No images provided for upscaling")
            return {}
        
        logger.info(f"Starting concurrent upscaling of {len(images_dict)} images with scale {scale}x")
        start_time = time.time()
        
        # Create upscale tasks
        tasks = [
            UpscaleTask(key=key, image_bytes=image_bytes, scale=scale)
            for key, image_bytes in images_dict.items()
        ]
        
        # Submit tasks to thread pool
        future_to_task = {
            self.executor.submit(self._upscale_single, task): task 
            for task in tasks
        }
        
        # Collect results as they complete
        upscaled_images = {}
        completed_count = 0
        failed_count = 0
        
        # Use asyncio to wait for futures
        for future in as_completed(future_to_task):
            task = future_to_task[future]
            try:
                result = future.result()
                if result:
                    upscaled_images[task.key] = result
                    completed_count += 1
                    logger.info(f"Successfully upscaled {task.key} ({completed_count}/{len(tasks)})")
                else:
                    failed_count += 1
                    logger.warning(f"Failed to upscale {task.key}")
                    # Keep original image if upscaling fails
                    upscaled_images[task.key] = task.image_bytes
                    
            except Exception as e:
                failed_count += 1
                logger.error(f"Error upscaling {task.key}: {e}", exc_info=True)
                # Keep original image if upscaling fails
                upscaled_images[task.key] = task.image_bytes
            
            # Allow other coroutines to run
            await asyncio.sleep(0)
        
        total_time = time.time() - start_time
        logger.info(f"Completed concurrent upscaling: {completed_count} successful, {failed_count} failed, {total_time:.2f}s total")
        
        return upscaled_images
    
    def _upscale_single(self, task: UpscaleTask) -> Optional[bytes]:
        """
        Upscale a single image (runs in thread pool)
        
        Args:
            task: UpscaleTask containing image data
            
        Returns:
            bytes: Upscaled image bytes or None if failed
        """
        try:
            logger.debug(f"Upscaling {task.key} with scale {task.scale}x")
            result = self.upscaler.upscale_image_bytes(task.image_bytes, task.scale)
            
            if result:
                logger.debug(f"Successfully upscaled {task.key}")
                return result
            else:
                logger.warning(f"Upscaling returned None for {task.key}")
                return None
                
        except Exception as e:
            logger.error(f"Exception during upscaling {task.key}: {e}", exc_info=True)
            return None
    
    async def upscale_with_fallback(
        self, 
        images_dict: Dict[str, bytes], 
        scale: int = 4
    ) -> Tuple[Dict[str, bytes], Dict[str, bytes]]:
        """
        Upscale images with fallback to original on failure
        
        Args:
            images_dict: Dictionary of {key: image_bytes}
            scale: Upscaling factor
            
        Returns:
            Tuple of (upscaled_images, original_images)
        """
        original_images = images_dict.copy()
        
        if not images_dict:
            return {}, original_images
        
        logger.info(f"Upscaling {len(images_dict)} images with fallback")
        
        # Create tasks with retry logic
        tasks = []
        for key, image_bytes in images_dict.items():
            task = UpscaleTask(key=key, image_bytes=image_bytes, scale=scale)
            tasks.append(task)
        
        # Process with concurrency limit
        semaphore = asyncio.Semaphore(self.max_workers)
        
        async def limited_upscale(task: UpscaleTask):
            async with semaphore:
                # Run in thread pool
                loop = asyncio.get_event_loop()
                try:
                    result = await loop.run_in_executor(
                        self.executor,
                        self._upscale_with_retry,
                        task
                    )
                    return task.key, result
                except Exception as e:
                    logger.error(f"Error in limited upscale for {task.key}: {e}")
                    return task.key, None
        
        # Execute all upscaling tasks
        start_time = time.time()
        results = await asyncio.gather(
            *[limited_upscale(task) for task in tasks],
            return_exceptions=True
        )
        
        # Process results
        upscaled_images = {}
        successful_count = 0
        
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Upscaling task failed with exception: {result}")
                continue
                
            key, upscaled_bytes = result
            if upscaled_bytes:
                upscaled_images[key] = upscaled_bytes
                successful_count += 1
            else:
                # Fallback to original
                upscaled_images[key] = original_images[key]
                logger.warning(f"Using original image for {key} due to upscaling failure")
        
        total_time = time.time() - start_time
        logger.info(f"Upscaling completed: {successful_count}/{len(tasks)} successful in {total_time:.2f}s")
        
        return upscaled_images, original_images
    
    def _upscale_with_retry(self, task: UpscaleTask, max_retries: int = 2) -> Optional[bytes]:
        """
        Upscale with retry logic
        
        Args:
            task: UpscaleTask to process
            max_retries: Maximum retry attempts
            
        Returns:
            bytes: Upscaled image or None
        """
        last_error = None
        
        for attempt in range(max_retries + 1):
            try:
                if attempt > 0:
                    logger.info(f"Retrying upscale for {task.key} (attempt {attempt + 1})")
                
                result = self.upscaler.upscale_image_bytes(task.image_bytes, task.scale)
                
                if result:
                    if attempt > 0:
                        logger.info(f"Upscale retry successful for {task.key}")
                    return result
                else:
                    logger.warning(f"Upscale returned None for {task.key} on attempt {attempt + 1}")
                    
            except Exception as e:
                last_error = e
                logger.warning(f"Upscale attempt {attempt + 1} failed for {task.key}: {e}")
                
                if attempt < max_retries:
                    # Brief delay before retry
                    time.sleep(0.5 * (attempt + 1))
        
        logger.error(f"All upscale attempts failed for {task.key}. Last error: {last_error}")
        return None
    
    def shutdown(self):
        """Shutdown the executor"""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=True)
            logger.info("ConcurrentUpscaler executor shutdown complete")

# Utility functions for easy usage
async def upscale_images_parallel(
    images_dict: Dict[str, bytes], 
    scale: int = 4,
    max_workers: int = 3
) -> Dict[str, bytes]:
    """
    Utility function to upscale images in parallel
    
    Args:
        images_dict: Dictionary of images to upscale
        scale: Upscaling factor
        max_workers: Maximum concurrent workers
        
    Returns:
        Dict[str, bytes]: Upscaled images
    """
    upscaler = ConcurrentUpscaler(max_workers=max_workers)
    try:
        return await upscaler.upscale_images_concurrent(images_dict, scale)
    finally:
        upscaler.shutdown()

async def upscale_with_original_fallback(
    images_dict: Dict[str, bytes], 
    scale: int = 4,
    max_workers: int = 3
) -> Tuple[Dict[str, bytes], Dict[str, bytes]]:
    """
    Utility function to upscale images with original image fallback
    
    Args:
        images_dict: Dictionary of images to upscale
        scale: Upscaling factor  
        max_workers: Maximum concurrent workers
        
    Returns:
        Tuple of (upscaled_images, original_images)
    """
    upscaler = ConcurrentUpscaler(max_workers=max_workers)
    try:
        return await upscaler.upscale_with_fallback(images_dict, scale)
    finally:
        upscaler.shutdown()
