from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks, Request
from typing import List, Optional, Dict
import uuid
import os
import logging
from pathlib import Path
from app.core.config import settings
from app.utils.file_helpers import save_upload_files, cleanup_temp_files
from app.schemas import GenerationResponse, ProcessingStatus, ErrorResponse, GenerationResult, FileAccessResponse, GenerationRequest
from app.services.workflow_manager import WorkflowManager
import json

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()
workflow_manager = WorkflowManager()

@router.post(
    "/generate/image",
    response_model=GenerationResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
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
        
        # Extract gender parameter with validation
        gender = generation_request.gender if hasattr(generation_request, 'gender') else None
        if gender and gender.lower() not in ['male', 'female']:
            raise HTTPException(
                status_code=400,
                detail="Invalid gender parameter. Must be 'male' or 'female'."
            )
        
        # Extract upscale parameter (default to True)
        upscale = getattr(generation_request, 'upscale', True)
        
        # Generate a unique request ID
        request_id = str(uuid.uuid4())
        
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
        
        # Schedule cleanup of temporary files
        background_tasks.add_task(cleanup_temp_files, request_id)
        
        # Process through workflow manager with background array support
        logger.info(f"Starting workflow process with background array for request_id: {request_id}")
        result = await workflow_manager.process_request_with_background_array(
            image_paths=saved_paths_dict,
            background_config=background_config,
            text_description=generation_request.text,
            request_id=request_id,
            username="api_user",  # Default username for API requests
            product=generation_request.productType,
            isVideo=generation_request.isVideo,
            number_of_outputs=generation_request.numberOfOutputs,
            aspect_ratio="9:16",  # Default aspect ratio
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
            upscale_image=result.get("upscale_image", []),  # Upscaled images when upscale=True
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

@router.post(
    "/generate",
    response_model=GenerationResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
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
        
        # Process through workflow manager
        logger.info(f"Starting workflow process for request_id: {request_id}")
        result = await workflow_manager.process_request(
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