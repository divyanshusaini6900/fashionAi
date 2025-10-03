from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks, Request, Depends
from typing import List, Optional, Dict, Any
import uuid
import os
import logging
import time
from pathlib import Path
from app.core.config import settings
from app.utils.file_helpers import save_upload_files, cleanup_temp_files
from app.schemas import GenerationResponse, ProcessingStatus, ErrorResponse, GenerationResult, FileAccessResponse, GenerationRequest
from app.services.workflow_manager import WorkflowManager
from app.services.parallel_workflow_manager import ParallelWorkflowManager
from app.services.task_queue import task_queue
from app.core.api_key_middleware import verify_api_key
import json

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()
# Use parallel workflow manager for better performance
workflow_manager = ParallelWorkflowManager()

@router.post(
    "/generate/image",
    response_model=Dict[str, Any],  # Changed from GenerationResponse for immediate response
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    },
    dependencies=[Depends(verify_api_key)]
)
async def generate_fashion_image(
    background_tasks: BackgroundTasks,
    request: Request
):
    """
    Generate fashion output from input images with background array configuration.
    
    Args:
        background_tasks: FastAPI background tasks handler
        request: Request containing JSON data with background array configuration
        
    Returns:
        GenerationResponse with status and file URLs
    """
    try:
        # Parse JSON data from request
        json_data = await request.json()
        generation_request = GenerationRequest(**json_data)
        
        # Extract gender parameter with validation - accept woman/man and convert to female/male
        gender_raw = generation_request.gender if hasattr(generation_request, 'gender') else None
        if gender_raw:
            gender_map = {'woman': 'female', 'man': 'male', 'female': 'female', 'male': 'male'}
            gender = gender_map.get(gender_raw.lower(), None)
            if not gender:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid gender parameter. Must be 'male', 'female', 'man', or 'woman'."
                )
        else:
            gender = None
        
        # Extract upscale parameter (default to True)
        upscale = getattr(generation_request, 'upscale', True)
        
        # Extract aspect ratio parameter (default to "9:16")
        aspect_ratio = getattr(generation_request, 'aspectRatio', '9:16')
        valid_aspect_ratios = ["1:1", "16:9", "4:3", "3:4", "9:16"]
        if aspect_ratio not in valid_aspect_ratios:
            aspect_ratio = "9:16"  # Default to 9:16 if invalid
        
        # Generate a unique request ID
        request_id = str(uuid.uuid4())
        
        # 🚀 RETURN CONVERSION ID IMMEDIATELY - Process in background
        logger.info(f"📥 Received request, returning conversion_id immediately: {request_id}")
        
        # Start background processing
        background_tasks.add_task(
            process_generation_in_background,
            request_id=request_id,
            generation_request=generation_request,
            gender=gender,
            upscale=upscale,
            aspect_ratio=aspect_ratio
        )
        
        # Return conversion ID immediately for polling (Flutter app expects 'id')
        return {
            'id': request_id,
            'status': 'processing',
            'message': 'Generation started successfully'
        }
        
    except HTTPException as e:
        # Re-raise HTTP exceptions
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred during generation: {str(e)}"
        )

@router.post(
    "/generate",
    response_model=GenerationResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    },
    dependencies=[Depends(verify_api_key)]
)
async def generate_fashion(
    background_tasks: BackgroundTasks,
    text: str = Form(..., description="Text description or instructions"),
    username: str = Form(..., description="Username for SKU ID generation"),
    product: str = Form(..., description="Product name for SKU ID generation"),
    isVideo: bool = Form(False, description="Whether to generate a video"),
    numberOfOutputs: int = Form(1, description="Number of image outputs to generate (1-4)", ge=1, le=4),
    aspectRatio: str = Form("9:16", description="Aspect ratio for generated images", example="9:16"),
    gender: str = Form(None, description="Gender of the model to display clothing on (male/female)"),
    upscale: bool = Form(True, description="Whether to upscale generated images"),
    frontside: UploadFile = File(..., description="Front side image of the fashion item."),
    backside: Optional[UploadFile] = File(None, description="Back side image of the fashion item."),
    sideview: Optional[UploadFile] = File(None, description="Side view image of the fashion item."),
    detailview: Optional[UploadFile] = File(None, description="Detailed view image of the fashion item."),

):
    """
    Generate fashion output from multiple input images and text description.
    
    Args:
        background_tasks: FastAPI background tasks handler
        images: List of image files to process
        text: Text description or instructions
        gender: Gender of the model to display clothing on (male/female)
        upscale: Whether to upscale generated images
        
    Returns:
        GenerationResponse with status and file URLs
    """
    try:
        # Validate gender parameter if provided
        if gender and gender.lower() not in ['male', 'female']:
            raise HTTPException(
                status_code=400,
                detail="Invalid gender parameter. Must be 'male' or 'female'."
            )
        
        # Collect all available images into a dictionary.
        images_dict = {
            "frontside": frontside,
            "backside": backside,
            "sideview": sideview,
            "detailview": detailview
        }
        
        # Filter out any None values (optional images that weren't provided)
        images_to_process = {k: v for k, v in images_dict.items() if v}

        # Input validation
        if not images_to_process:
            raise HTTPException(status_code=400, detail="No images provided. 'frontside' is required.")

        for image in images_to_process.values():
            if not image.content_type.startswith('image/'):
                raise HTTPException(
                    status_code=400,
                    detail=f"File {image.filename} is not an image"
                )
            
            # Check file size
            content = await image.read()
            await image.seek(0)  # Reset file pointer
            if len(content) > settings.MAX_UPLOAD_SIZE:
                raise HTTPException(
                    status_code=400,
                    detail=f"File {image.filename} is too large. Maximum size is {settings.MAX_UPLOAD_SIZE/1024/1024}MB"
                )

        # Validate aspectRatio parameter
        valid_aspect_ratios = ["1:1", "16:9", "4:3", "3:4", "9:16"]
        if aspectRatio not in valid_aspect_ratios:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid aspectRatio. Must be one of: {', '.join(valid_aspect_ratios)}"
            )

        # Generate a unique request ID
        request_id = str(uuid.uuid4())
        
        # Save uploaded files, preserving their view names
        saved_paths_dict = await save_upload_files(images_to_process, request_id)
        
        # Schedule cleanup of temporary files
        background_tasks.add_task(cleanup_temp_files, request_id)
        
        # Process through parallel workflow manager
        logger.info(f"Starting parallel workflow process for request_id: {request_id}")
        result = await workflow_manager.process_request_parallel(
            image_paths=saved_paths_dict,
            text_description=text,
            request_id=request_id,
            username=username,
            product=product,
            isVideo=isVideo,
            number_of_outputs=numberOfOutputs,
            aspect_ratio=aspectRatio,
            gender=gender,  # Pass gender parameter
            upscale=upscale  # Pass upscale parameter
        )
        
        logger.info(f"Workflow completed for request_id: {request_id}")
        logger.info(f"Result keys: {list(result.keys()) if result else 'None'}")
        
        # Ensure we have the required fields
        excel_report_url = result.get("excel_report_url") or ""
        
        if not excel_report_url:
            logger.warning(f"No excel_report_url in result for {request_id}")
        
        response = GenerationResponse(
            request_id=request_id,
            image_variations=result.get("image_variations", []),
            upscale_image=result.get("upscale_image", []),
            output_video_url=result.get("output_video_url"),
            excel_report_url=excel_report_url,
            metadata=result.get("metadata", {})
        )
        
        logger.info(f"Returning response for {request_id}: {type(response)}")
        return response
        
    except HTTPException as e:
        # Re-raise HTTP exceptions
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred during generation: {str(e)}"
        )

@router.get("/files/{request_id}", response_model=FileAccessResponse)
async def get_files_by_request_id(request_id: str):
    """
    Retrieve all files associated with a specific request_id.
    
    Args:
        request_id: The unique identifier for the generation request
        
    Returns:
        FileAccessResponse with all file URLs for the request
    """
    try:
        # Validate request_id format (UUID)
        try:
            uuid.UUID(request_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid request_id format")
        
        files = []
        
        if settings.USE_LOCAL_STORAGE:
            # Check local storage
            output_dir = Path(settings.LOCAL_OUTPUT_DIR)
            if not output_dir.exists():
                raise HTTPException(status_code=500, detail="Output directory does not exist")
            
            # Find all files that contain the request_id in their filename
            for file_path in output_dir.iterdir():
                if file_path.is_file() and request_id in file_path.name:
                    # Construct the URL for accessing the file
                    file_url = f"{settings.LOCAL_BASE_URL}/files/{file_path.name}"
                    files.append({
                        "filename": file_path.name,
                        "url": file_url,
                        "type": get_file_type(file_path.name)
                    })
        else:
            # Check GCS storage
            try:
                from app.utils.gcs_helpers import get_gcs_client
                client = get_gcs_client()
                bucket = client.bucket(settings.GCS_BUCKET_NAME)
                
                # List all blobs in the bucket with the request_id prefix
                prefix = f"generated_files/{request_id}/"
                blobs = bucket.list_blobs(prefix=prefix)
                
                for blob in blobs:
                    if blob.name.endswith('/') or blob.name == prefix:
                        continue  # Skip directories and prefix itself
                    files.append({
                        "filename": blob.name.split('/')[-1],
                        "url": blob.public_url,
                        "type": get_file_type(blob.name)
                    })
            except Exception as e:
                logger.error(f"Error accessing GCS files for request_id {request_id}: {str(e)}")
                # Fall back to local storage if GCS fails
                output_dir = Path(settings.LOCAL_OUTPUT_DIR)
                if output_dir.exists():
                    for file_path in output_dir.iterdir():
                        if file_path.is_file() and request_id in file_path.name:
                            file_url = f"{settings.LOCAL_BASE_URL}/files/{file_path.name}"
                            files.append({
                                "filename": file_path.name,
                                "url": file_url,
                                "type": get_file_type(file_path.name)
                            })
        
        if not files:
            raise HTTPException(status_code=404, detail="No files found for this request_id")
        
        return {
            "request_id": request_id,
            "files": files,
            "count": len(files)
        }
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving files: {str(e)}")

def get_file_type(filename: str) -> str:
    """Determine file type based on extension."""
    ext = filename.lower().split('.')[-1] if '.' in filename else ''
    if ext in ['jpg', 'jpeg', 'png', 'gif']:
        return 'image'
    elif ext in ['mp4', 'avi', 'mov']:
        return 'video'
    elif ext in ['xlsx', 'xls']:
        return 'excel'
    elif ext in ['pdf']:
        return 'pdf'
    else:
        return 'other'

# Dictionary to store generation results for polling
generation_results = {}

async def process_generation_in_background(
    request_id: str,
    generation_request,
    gender: str,
    upscale: bool,
    aspect_ratio: str
):
    """Background task to process the generation"""
    try:
        logger.info(f"🔄 Starting background processing for request_id: {request_id}")
        
        # Initialize result status (using 'id' for Flutter app compatibility)
        generation_results[request_id] = {
            'id': request_id,
            'status': 'processing',
            'progress': 0.2,
            'message': 'Downloading images...'
        }
        
        # Download images from URLs and save them
        saved_paths_dict = {}
        background_config = {}
        
        for input_image in generation_request.inputImages:
            # Download image from URL
            import requests
            response = requests.get(input_image.url)
            response.raise_for_status()
            
            # Save image to temporary location using existing settings
            temp_dir = Path(settings.BASE_DIR) / settings.UPLOAD_DIR / request_id
            temp_dir.mkdir(parents=True, exist_ok=True)
            image_path = temp_dir / f"{input_image.view}.jpg"
            
            with open(image_path, "wb") as f:
                f.write(response.content)
            
            saved_paths_dict[input_image.view] = str(image_path)
            background_config[input_image.view] = input_image.backgrounds
        
        logger.info(f"📸 Downloaded {len(saved_paths_dict)} images for request_id: {request_id}")
        
        # Update progress
        generation_results[request_id]['progress'] = 0.4
        generation_results[request_id]['message'] = 'Generating AI content...'
        
        # Process through parallel workflow manager with background array support
        logger.info(f"Starting parallel workflow process with background array for request_id: {request_id}")
        result = await workflow_manager.process_request_with_background_array_parallel(
            image_paths=saved_paths_dict,
            background_config=background_config,
            text_description=generation_request.text,
            request_id=request_id,
            username="api_user",
            product=generation_request.productType,
            isVideo=generation_request.isVideo,
            number_of_outputs=generation_request.numberOfOutputs,
            aspect_ratio=aspect_ratio,
            gender=gender,
            upscale=upscale
        )
        
        logger.info(f"✅ Workflow completed for request_id: {request_id}")
        
        # Store completed result (using 'id' for Flutter app compatibility)
        generation_results[request_id] = {
            'id': request_id,
            'status': 'completed',
            'output': result
        }
        
        # Clean up temp files
        import shutil
        temp_dir = Path(settings.BASE_DIR) / settings.UPLOAD_DIR / request_id
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
            
    except Exception as e:
        logger.error(f"❌ Error processing request_id {request_id}: {e}", exc_info=True)
        generation_results[request_id] = {
            'id': request_id,
            'status': 'failed',
            'error': str(e)
        }

@router.get("/generate/image", dependencies=[Depends(verify_api_key)])
async def check_generation_status(id: str = None):
    """
    Check the status of a generation job (for polling)
    """
    if not id:
        raise HTTPException(status_code=400, detail="Missing 'id' parameter")
    
    request_id = id
    
    if request_id not in generation_results:
        raise HTTPException(status_code=404, detail=f"Request {request_id} not found")
    
    result = generation_results[request_id]
    
    logger.info(f"📊 Status check for {request_id}: {result.get('status')}")
    
    return result

@router.get("/status/queue")
async def get_queue_status():
    """
    Get current status of the parallel processing queue system.
    """
    try:
        status = task_queue.get_queue_status()
        return {
            "status": "success",
            "queue_info": status,
            "parallel_processing": "enabled",
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"Error getting queue status: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "parallel_processing": "unknown"
        }