from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from typing import List, Optional
import uuid
import os
import logging
from app.core.config import settings
from app.utils.file_helpers import save_upload_files, cleanup_temp_files
from app.schemas import GenerationResponse, ProcessingStatus, ErrorResponse, GenerationResult
from app.services.workflow_manager import WorkflowManager

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()
workflow_manager = WorkflowManager()

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
    generate_video: bool = Form(False, description="Whether to generate a video"),
    numberOfOutputs: int = Form(1, description="Number of image outputs to generate (1-4)", ge=1, le=4),
    aspectRatio: str = Form("9:16", description="Aspect ratio for generated images", example="9:16"),
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
        
    Returns:
        GenerationResponse with status and file URLs
    """
    try:
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
            generate_video=generate_video,
            number_of_outputs=numberOfOutputs,
            aspect_ratio=aspectRatio
        )
        
        logger.info(f"Workflow completed for request_id: {request_id}")
        logger.info(f"Result keys: {list(result.keys()) if result else 'None'}")
        
        # Ensure we have the required fields
        output_image_url = result.get("output_image_url") or ""
        excel_report_url = result.get("excel_report_url") or ""
        
        if not output_image_url:
            logger.warning(f"No output_image_url in result for {request_id}")
        if not excel_report_url:
            logger.warning(f"No excel_report_url in result for {request_id}")
        
        response = GenerationResponse(
            request_id=request_id,
            output_image_url=output_image_url,
            image_variations=result.get("image_variations", []),
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