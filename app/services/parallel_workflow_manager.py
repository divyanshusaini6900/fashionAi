"""
Parallel Workflow Manager
Orchestrates the entire fashion AI pipeline with concurrent processing
"""
import asyncio
import logging
import time
from typing import Dict, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor
import json

from fastapi import HTTPException

from app.services.workflow_manager import WorkflowManager
from app.services.concurrent_image_generator import ConcurrentImageGenerator
from app.services.concurrent_upscaler import ConcurrentUpscaler
from app.services.task_queue import submit_task, wait_for_task, TaskStatus
from app.services.video_generator import VideoGenerator
from app.services.excel_generator import ExcelGenerator
from app.utils.file_helpers import (
    save_generated_image_variations,
    save_original_and_upscaled_images,
    save_generated_video,
    save_excel_report
)
from app.core.config import settings

logger = logging.getLogger(__name__)

class ParallelWorkflowManager(WorkflowManager):
    """
    Enhanced workflow manager with parallel processing capabilities
    """
    
    def __init__(self):
        """Initialize with concurrent services"""
        super().__init__()
        self.concurrent_upscaler = ConcurrentUpscaler(max_workers=4)
        self.thread_executor = ThreadPoolExecutor(max_workers=6)
        
    def __del__(self):
        """Cleanup resources"""
        if hasattr(self, 'concurrent_upscaler'):
            self.concurrent_upscaler.shutdown()
        if hasattr(self, 'thread_executor'):
            self.thread_executor.shutdown(wait=False)
    
    async def process_request_parallel(
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
        Orchestrates the full process with parallel processing optimizations
        """
        try:
            logger.info(f"Starting parallel workflow for request_id: {request_id}")
            start_time = time.time()
            
            # Step 1: AI Analysis (this needs to be sequential as other steps depend on it)
            logger.info("Step 1: Running AI analysis")
            analysis_start = time.time()
            
            # Use combined analysis for optimization (single API call for both product analysis and background/pose recommendations)
            if settings.USE_GEMINI_FOR_TEXT:
                analysis_json = await self._analyze_with_gemini_combined(image_paths, text_description, username, product, number_of_outputs)
            else:
                # For OpenAI, we still need separate calls
                analysis_json = await self._analyze_with_openai(image_paths, text_description, username, product)
            
            product_data = analysis_json.get("product_data", {})
            image_analysis = analysis_json.get("image_analysis", {})
            analysis_time = time.time() - analysis_start
            logger.info(f"AI analysis completed in {analysis_time:.2f}s")
            
            # Step 2: Concurrent Image Generation
            logger.info("Step 2: Starting concurrent image generation")
            generation_start = time.time()
            
            async with ConcurrentImageGenerator() as concurrent_generator:
                primary_image_bytes, all_variations_bytes_dict = await concurrent_generator.generate_images_concurrent(
                    product_data=product_data,
                    reference_image_paths_dict=image_paths,
                    number_of_outputs=number_of_outputs,
                    aspect_ratio=aspect_ratio,
                    gender=gender
                )
            
            if not primary_image_bytes:
                raise ValueError("Failed to generate a primary image.")
            
            generation_time = time.time() - generation_start
            logger.info(f"Concurrent image generation completed in {generation_time:.2f}s")
            
            # Step 3: Parallel Post-Processing Tasks
            logger.info("Step 3: Starting parallel post-processing")
            post_processing_start = time.time()
            
            # Create tasks for parallel execution
            tasks = []
            
            # Task 1: Upscaling (if requested)
            original_variations_bytes_dict = all_variations_bytes_dict.copy()
            upscaled_variations_dict = None
            upscaled_primary = primary_image_bytes
            
            if upscale:
                upscale_task = self._create_upscaling_task(all_variations_bytes_dict, primary_image_bytes)
                tasks.append(("upscaling", upscale_task))
            
            # Task 2: Video generation (if requested and independent)
            video_task = None
            if isVideo:
                video_task = self._create_video_generation_task(primary_image_bytes, product_data)
                tasks.append(("video", video_task))
            
            # Execute parallel tasks
            if tasks:
                parallel_results = await self._execute_parallel_tasks(tasks)
                
                # Process upscaling results
                if upscale and "upscaling" in parallel_results:
                    upscale_result = parallel_results["upscaling"]
                    if upscale_result:
                        upscaled_variations_dict, upscaled_primary = upscale_result
                        all_variations_bytes_dict = upscaled_variations_dict
                        primary_image_bytes = upscaled_primary
            
            post_processing_time = time.time() - post_processing_start
            logger.info(f"Parallel post-processing completed in {post_processing_time:.2f}s")
            
            # Step 4: File Saving and Final Tasks
            logger.info("Step 4: Saving files and generating reports")
            saving_start = time.time()
            
            # Save images
            if upscale:
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
            
            # Get primary image URL
            primary_image_url = variation_urls_dict.get("frontside") or next(iter(variation_urls_dict.values()), None)
            
            if not primary_image_url:
                raise ValueError("Failed to obtain a primary image URL after saving.")
            
            # Keep all variations for Excel generation (don't exclude primary image)
            all_variations_dict = variation_urls_dict.copy()
            
            # Get additional variations
            additional_variations_dict = {
                view: url for view, url in variation_urls_dict.items() if url != primary_image_url
            }
            
            # Handle video generation result
            video_url = None
            if isVideo and "video" in parallel_results:
                video_result = parallel_results["video"]
                if video_result:
                    video_url = save_generated_video(video_result, request_id)
                    logger.info(f"Video generation successful. URL: {video_url}")
                else:
                    logger.warning("Video generation failed")
            
            # Generate Excel report (this can be done in parallel with video in future)
            excel_url = await self._generate_excel_report_async(
                product_data, primary_image_url, all_variations_dict, video_url, request_id
            )
            
            saving_time = time.time() - saving_start
            logger.info(f"File saving and report generation completed in {saving_time:.2f}s")
            
            # Prepare clean response with separated original and upscaled images
            original_image_urls = list(original_variation_urls_dict.values())
            upscaled_image_urls = list(upscaled_variation_urls_dict.values()) if upscale else []
            
            total_time = time.time() - start_time
            logger.info(f"Parallel workflow completed for {request_id} in {total_time:.2f}s")
            
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
                        "analysis": analysis_time,
                        "generation": generation_time,
                        "post_processing": post_processing_time,
                        "saving": saving_time,
                        "total": total_time
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Parallel workflow failed for request {request_id}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"An error occurred in the parallel processing workflow: {str(e)}"
            )
    
    async def process_request_with_background_array_parallel(
        self,
        image_paths: Dict[str, str],
        background_config: Dict[str, List[int]],
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
        Orchestrates the full process with background array support and parallel processing
        """
        try:
            logger.info(f"Starting parallel workflow with background array for request_id: {request_id}")
            start_time = time.time()
            
            # Step 1: AI Analysis
            logger.info("Step 1: Running AI analysis")
            analysis_start = time.time()
            
            # Use combined analysis for optimization (single API call for both product analysis and background/pose recommendations)
            if settings.USE_GEMINI_FOR_TEXT:
                analysis_json = await self._analyze_with_gemini_combined(image_paths, text_description, username, product, number_of_outputs)
            else:
                # For OpenAI, we still need separate calls
                analysis_json = await self._analyze_with_openai(image_paths, text_description, username, product)
            
            product_data = analysis_json.get("product_data", {})
            analysis_time = time.time() - analysis_start
            logger.info(f"AI analysis completed in {analysis_time:.2f}s")
            
            # Step 2: Concurrent Image Generation with Background Array
            logger.info("Step 2: Starting concurrent image generation with background array")
            generation_start = time.time()
            
            async with ConcurrentImageGenerator() as concurrent_generator:
                primary_image_bytes, all_variations_bytes_dict = await concurrent_generator.generate_images_with_background_array_concurrent(
                    product_data=product_data,
                    reference_image_paths_dict=image_paths,
                    background_config=background_config,
                    number_of_outputs=number_of_outputs,
                    aspect_ratio=aspect_ratio,
                    gender=gender
                )
            
            if not primary_image_bytes:
                raise ValueError("Failed to generate a primary image.")
            
            generation_time = time.time() - generation_start
            logger.info(f"Concurrent background array generation completed in {generation_time:.2f}s")
            
            # Step 3: Parallel Post-Processing
            logger.info("Step 3: Starting parallel post-processing")
            post_processing_start = time.time()
            
            tasks = []
            original_variations_bytes_dict = all_variations_bytes_dict.copy()
            
            # Upscaling task
            if upscale:
                upscale_task = self._create_upscaling_task(all_variations_bytes_dict, primary_image_bytes)
                tasks.append(("upscaling", upscale_task))
            
            # Video generation task
            if isVideo:
                video_task = self._create_video_generation_task(primary_image_bytes, product_data)
                tasks.append(("video", video_task))
            
            # Execute parallel tasks
            parallel_results = {}
            if tasks:
                parallel_results = await self._execute_parallel_tasks(tasks)
                
                if upscale and "upscaling" in parallel_results:
                    upscale_result = parallel_results["upscaling"]
                    if upscale_result:
                        upscaled_variations_dict, upscaled_primary = upscale_result
                        all_variations_bytes_dict = upscaled_variations_dict
                        primary_image_bytes = upscaled_primary
            
            post_processing_time = time.time() - post_processing_start
            logger.info(f"Parallel post-processing completed in {post_processing_time:.2f}s")
            
            # Step 4: File Saving and Report Generation
            logger.info("Step 4: Saving files and generating reports")
            saving_start = time.time()
            
            # Save images
            if upscale:
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
            
            # Primary image selection
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
            
            additional_variations_dict = {
                view: url for view, url in variation_urls_dict.items() if url != primary_image_url
            }
            
            # Handle video result
            video_url = None
            if isVideo and "video" in parallel_results:
                video_result = parallel_results["video"]
                if video_result:
                    video_url = save_generated_video(video_result, request_id)
                    logger.info(f"Video generation successful. URL: {video_url}")
                else:
                    logger.warning("Video generation failed")
            
            # Generate Excel report
            excel_url = await self._generate_excel_report_async(
                product_data, primary_image_url, all_variations_dict, video_url, request_id
            )
            
            saving_time = time.time() - saving_start
            logger.info(f"File saving and report generation completed in {saving_time:.2f}s")
            
            # Prepare clean response with separated original and upscaled images
            original_image_urls = list(original_variation_urls_dict.values())
            upscaled_image_urls = list(upscaled_variation_urls_dict.values()) if upscale else []
            
            total_time = time.time() - start_time
            logger.info(f"Parallel background array workflow completed for {request_id} in {total_time:.2f}s")
            
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
                        "analysis": analysis_time,
                        "generation": generation_time,
                        "post_processing": post_processing_time,
                        "saving": saving_time,
                        "total": total_time
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Parallel background array workflow failed for request {request_id}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"An error occurred in the parallel background array workflow: {str(e)}"
            )
    
    def _create_upscaling_task(self, images_dict: Dict[str, bytes], primary_image: bytes) -> asyncio.Task:
        """Create upscaling task for parallel execution"""
        async def upscale():
            try:
                logger.info(f"Starting parallel upscaling of {len(images_dict)} images")
                upscaled_dict, _ = await self.concurrent_upscaler.upscale_with_fallback(images_dict)
                
                # Find upscaled primary image
                upscaled_primary = primary_image
                for key, original_bytes in images_dict.items():
                    if original_bytes == primary_image:
                        upscaled_primary = upscaled_dict.get(key, primary_image)
                        break
                
                return upscaled_dict, upscaled_primary
            except Exception as e:
                logger.error(f"Upscaling task failed: {e}", exc_info=True)
                return None
        
        return asyncio.create_task(upscale())
    
    def _create_video_generation_task(self, primary_image_bytes: bytes, product_data: Dict) -> asyncio.Task:
        """Create video generation task for parallel execution"""
        async def generate_video():
            try:
                logger.info("Starting parallel video generation")
                # Save primary image temporarily for video generation
                import tempfile
                with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                    temp_file.write(primary_image_bytes)
                    temp_path = temp_file.name
                
                try:
                    video_bytes = await self.video_generator.isVideo(
                        image_path=temp_path,
                        product_data=product_data
                    )
                    return video_bytes
                finally:
                    import os
                    try:
                        os.unlink(temp_path)
                    except:
                        pass
                        
            except Exception as e:
                logger.error(f"Video generation task failed: {e}", exc_info=True)
                return None
        
        return asyncio.create_task(generate_video())
    
    async def _execute_parallel_tasks(self, tasks: List[Tuple[str, asyncio.Task]]) -> Dict:
        """Execute multiple tasks in parallel and return results"""
        if not tasks:
            return {}
        
        logger.info(f"Executing {len(tasks)} parallel tasks")
        
        # Extract tasks and names
        task_names = [name for name, _ in tasks]
        task_coroutines = [task for _, task in tasks]
        
        # Execute all tasks concurrently
        start_time = time.time()
        results = await asyncio.gather(*task_coroutines, return_exceptions=True)
        execution_time = time.time() - start_time
        
        # Process results
        task_results = {}
        for name, result in zip(task_names, results):
            if isinstance(result, Exception):
                logger.error(f"Parallel task '{name}' failed: {result}")
                task_results[name] = None
            else:
                task_results[name] = result
                logger.info(f"Parallel task '{name}' completed successfully")
        
        logger.info(f"All parallel tasks completed in {execution_time:.2f}s")
        return task_results
    
    async def _generate_excel_report_async(
        self,
        product_data: Dict,
        primary_image_url: str,
        all_variations_dict: Dict,
        video_url: Optional[str],
        request_id: str
    ) -> str:
        """Generate Excel report asynchronously"""
        try:
            logger.info("Creating Excel report...")
            
            # Run Excel generation in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            # Create a wrapper function to call create_report with keyword arguments
            def create_excel_report():
                return self.excel_generator.create_report(
                    product_data=product_data,
                    variation_urls=all_variations_dict,
                    video_url=video_url
                )
            
            excel_bytes = await loop.run_in_executor(
                self.thread_executor,
                create_excel_report
            )
            
            # Save the Excel report
            excel_url = save_excel_report(excel_bytes, request_id)
            logger.info(f"Excel report saved successfully: {excel_url}")
            
            return excel_url
            
        except Exception as e:
            logger.error(f"Excel generation failed: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate Excel report: {str(e)}"
            )
