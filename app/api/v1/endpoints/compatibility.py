"""
Compatibility endpoint for Flutter app integration
This provides backwards compatibility with the old polling-based API format
while using the new direct generation system under the hood.
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from typing import Dict, List
import uuid
import asyncio
from app.core.api_key_middleware import verify_api_key
from app.services.parallel_workflow_manager import ParallelWorkflowManager
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
workflow_manager = ParallelWorkflowManager()

# Store conversion jobs in memory (in production, use Redis or database)
conversion_jobs: Dict[str, Dict] = {}

@router.post("/generate/image", dependencies=[Depends(verify_api_key)])
async def generate_with_polling_compatibility(
    background_tasks: BackgroundTasks,
    request_data: Dict
):
    """
    Compatibility endpoint that mimics the old polling-based API
    Returns immediately with a conversion ID, processes in background
    """
    try:
        # Generate a unique conversion ID
        conversion_id = str(uuid.uuid4())
        
        logger.info(f"📥 Received compatibility request with conversion_id: {conversion_id}")
        logger.info(f"📋 Request data: {request_data}")
        
        # Extract request parameters
        input_images = request_data.get('inputImages', [])
        text = request_data.get('text', '')
        number_of_outputs = request_data.get('numberOfOutputs', 1)
        is_video = request_data.get('isVideo', False)
        generate_csv = request_data.get('generateCsv', True)
        product_type = request_data.get('productType', 'product')
        
        # Handle gender parameter - convert woman/man to female/male
        gender_raw = request_data.get('gender')
        if gender_raw:
            gender_map = {'woman': 'female', 'man': 'male', 'female': 'female', 'male': 'male'}
            gender = gender_map.get(gender_raw.lower(), None)
        else:
            gender = None
            
        upscale = request_data.get('upscale', True)
        aspect_ratio = request_data.get('aspectRatio', '9:16')
        
        # Initialize job status
        conversion_jobs[conversion_id] = {
            'id': conversion_id,
            'status': 'processing',
            'progress': 0.1,
            'message': 'Generation started...',
            'result': None
        }
        
        # Start background processing
        background_tasks.add_task(
            process_generation,
            conversion_id=conversion_id,
            input_images=input_images,
            text=text,
            number_of_outputs=number_of_outputs,
            is_video=is_video,
            generate_csv=generate_csv,
            product_type=product_type,
            gender=gender,
            upscale=upscale,
            aspect_ratio=aspect_ratio
        )
        
        logger.info(f"✅ Started background processing for conversion_id: {conversion_id}")
        
        # Return conversion ID immediately (polling-based response)
        return {
            'id': conversion_id,
            'status': 'processing',
            'message': 'Generation started successfully'
        }
        
    except Exception as e:
        logger.error(f"❌ Error in compatibility endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/generate/image", dependencies=[Depends(verify_api_key)])
async def check_generation_status(id: str = None):
    """
    Check the status of a generation job (for polling)
    """
    if not id:
        raise HTTPException(status_code=400, detail="Missing 'id' parameter")
    
    conversion_id = id
    
    if conversion_id not in conversion_jobs:
        raise HTTPException(status_code=404, detail=f"Conversion {conversion_id} not found")
    
    job = conversion_jobs[conversion_id]
    
    logger.info(f"📊 Status check for {conversion_id}: {job['status']}")
    
    if job['status'] == 'completed':
        # Return completed result
        result = job['result']
        return {
            'id': conversion_id,
            'status': 'completed',
            'output': result
        }
    elif job['status'] == 'failed':
        return {
            'id': conversion_id,
            'status': 'failed',
            'error': job.get('error', 'Unknown error')
        }
    else:
        # Still processing
        return {
            'id': conversion_id,
            'status': 'processing',
            'progress': job.get('progress', 0.5),
            'message': job.get('message', 'Processing...')
        }


async def process_generation(
    conversion_id: str,
    input_images: List[Dict],
    text: str,
    number_of_outputs: int,
    is_video: bool,
    generate_csv: bool,
    product_type: str,
    gender: str,
    upscale: bool,
    aspect_ratio: str
):
    """
    Background task to process the generation
    """
    try:
        logger.info(f"🔄 Starting processing for conversion_id: {conversion_id}")
        
        # Update progress
        conversion_jobs[conversion_id]['progress'] = 0.2
        conversion_jobs[conversion_id]['message'] = 'Preparing images...'
        
        # Convert input_images format to match new API
        # Old format: [{"url": "...", "view": "front_view"}]
        # New format needs: image_paths dict and background_config
        
        image_paths = {}
        background_config = {}
        
        for img in input_images:
            url = img.get('url', '')
            view = img.get('view', 'frontside')
            backgrounds = img.get('backgrounds', [0, 0, 1])
            
            # Download image from URL and save temporarily
            import aiohttp
            import os
            from pathlib import Path
            
            temp_dir = Path("output/temp") / conversion_id
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        file_path = temp_dir / f"{view}.jpg"
                        with open(file_path, 'wb') as f:
                            f.write(await resp.read())
                        
                        image_paths[view] = str(file_path)
                        background_config[view] = backgrounds
        
        logger.info(f"📸 Downloaded {len(image_paths)} images")
        
        # Update progress
        conversion_jobs[conversion_id]['progress'] = 0.4
        conversion_jobs[conversion_id]['message'] = 'Generating AI content...'
        
        # Call the actual generation workflow
        result = await workflow_manager.process_request_with_background_array_parallel(
            image_paths=image_paths,
            background_config=background_config,
            text_description=text,
            request_id=conversion_id,
            username="api_user",
            product=product_type,
            isVideo=is_video,
            number_of_outputs=number_of_outputs,
            aspect_ratio=aspect_ratio,
            gender=gender,
            upscale=upscale
        )
        
        logger.info(f"✅ Generation completed for conversion_id: {conversion_id}")
        
        # Update job with completed status
        conversion_jobs[conversion_id]['status'] = 'completed'
        conversion_jobs[conversion_id]['progress'] = 1.0
        conversion_jobs[conversion_id]['message'] = 'Generation completed successfully!'
        conversion_jobs[conversion_id]['result'] = result
        
        # Clean up temp files
        import shutil
        temp_dir = Path("output/temp") / conversion_id
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        
    except Exception as e:
        logger.error(f"❌ Error processing conversion {conversion_id}: {e}", exc_info=True)
        conversion_jobs[conversion_id]['status'] = 'failed'
        conversion_jobs[conversion_id]['error'] = str(e)
        conversion_jobs[conversion_id]['message'] = f'Generation failed: {str(e)}'

