import os
import shutil
from pathlib import Path
from typing import List, Tuple, Dict
from fastapi import UploadFile
import aiofiles
from app.core.config import settings
import uuid
import logging
import io
from app.utils.s3_helpers import upload_file_to_s3

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def save_upload_files(files: Dict[str, UploadFile], request_id: str) -> Dict[str, str]:
    """
    Save uploaded files from a dictionary to a temporary directory,
    preserving their view names.
    
    Args:
        files: Dictionary of uploaded files (e.g., {"frontside": file1, "backside": file2})
        request_id: Unique identifier for the request
        
    Returns:
        Dictionary of saved file paths keyed by their view name
    """
    saved_paths = {}
    temp_dir = Path(settings.UPLOAD_DIR) / request_id
    
    # Create temporary directory for this request
    os.makedirs(temp_dir, exist_ok=True)
    
    for name, file in files.items():
        if not file:
            continue
            
        # Use the view name in the filename to preserve context
        file_ext = Path(file.filename).suffix
        safe_filename = f"{name}{file_ext}"
        file_path = temp_dir / safe_filename
        
        # Save file
        async with aiofiles.open(file_path, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)
            
        saved_paths[name] = str(file_path)
    
    return saved_paths

def cleanup_temp_files(request_id: str) -> None:
    """
    Remove temporary files for a given request.
    
    Args:
        request_id: Unique identifier for the request
    """
    temp_dir = Path(settings.UPLOAD_DIR) / request_id
    if temp_dir.exists():
        shutil.rmtree(temp_dir)

def _get_or_create_dir(path: str) -> None:
    """Ensures a directory exists, creating it if necessary."""
    if not os.path.exists(path):
        os.makedirs(path)

def save_generated_image(image_bytes: bytes, request_id: str) -> str:
    """
    Saves a single generated image locally or uploads to S3 based on USE_LOCAL_STORAGE setting.
    """
    filename = f"{request_id}_generated.jpg"
    
    if settings.USE_LOCAL_STORAGE:
        # Save directly to output folder
        output_dir = Path(settings.LOCAL_OUTPUT_DIR)
        _get_or_create_dir(str(output_dir))
        file_path = output_dir / filename
        
        with open(file_path, 'wb') as f:
            f.write(image_bytes)
        
        # Return the absolute file path instead of HTTP URL
        absolute_path = str(file_path.resolve())
        logger.info(f"Image saved locally to: {absolute_path}")
        return absolute_path
    else:
        # Upload to S3
        object_name = f"generated_files/{request_id}/{filename}"
        url = upload_file_to_s3(io.BytesIO(image_bytes), object_name)
        logger.info(f"Image uploaded to S3: {object_name}")
        return url

def save_generated_image_variations(image_bytes_dict: Dict[str, bytes], request_id: str) -> Dict[str, str]:
    """
    Saves a dictionary of image variations locally or uploads to S3 based on USE_LOCAL_STORAGE setting,
    and returns their file paths or URLs keyed by their view name.
    """
    paths_or_urls = {}
    
    if settings.USE_LOCAL_STORAGE:
        # Save directly to output folder
        output_dir = Path(settings.LOCAL_OUTPUT_DIR)
        _get_or_create_dir(str(output_dir))
        
        for view_name, image_bytes in image_bytes_dict.items():
            # Sanitize view_name to be used in a filename
            safe_view_name = view_name.replace(" ", "_").lower()
            filename = f"{request_id}_generated_{safe_view_name}.jpg"
            file_path = output_dir / filename
            
            with open(file_path, 'wb') as f:
                f.write(image_bytes)
            
            # Return the absolute file path instead of HTTP URL
            absolute_path = str(file_path.resolve())
            paths_or_urls[view_name] = absolute_path
            logger.info(f"Image variation saved locally to: {absolute_path}")
    else:
        # Upload to S3
        for view_name, image_bytes in image_bytes_dict.items():
            # Sanitize view_name to be used in a filename
            safe_view_name = view_name.replace(" ", "_").lower()
            filename = f"{request_id}_generated_{safe_view_name}.jpg"
            object_name = f"generated_files/{request_id}/{filename}"
            
            # Upload to S3
            url = upload_file_to_s3(io.BytesIO(image_bytes), object_name)
            paths_or_urls[view_name] = url
            logger.info(f"Image variation uploaded to S3: {object_name}")
    
    return paths_or_urls

def save_generated_video(video_bytes: bytes, request_id: str) -> str:
    """
    Saves a generated video locally or uploads to S3 based on USE_LOCAL_STORAGE setting.
    """
    filename = f"{request_id}_generated.mp4"
    
    if settings.USE_LOCAL_STORAGE:
        # Save directly to output folder
        output_dir = Path(settings.LOCAL_OUTPUT_DIR)
        _get_or_create_dir(str(output_dir))
        file_path = output_dir / filename
        
        with open(file_path, 'wb') as f:
            f.write(video_bytes)
        
        # Return the absolute file path instead of HTTP URL
        absolute_path = str(file_path.resolve())
        logger.info(f"Video saved locally to: {absolute_path}")
        return absolute_path
    else:
        # Upload to S3
        object_name = f"generated_files/{request_id}/{filename}"
        url = upload_file_to_s3(io.BytesIO(video_bytes), object_name)
        logger.info(f"Video uploaded to S3: {object_name}")
        return url

def save_excel_report(excel_bytes: bytes, request_id: str) -> str:
    """
    Saves a generated Excel report locally or uploads to S3 based on USE_LOCAL_STORAGE setting.
    """
    filename = f"{request_id}_report.xlsx"
    
    if settings.USE_LOCAL_STORAGE:
        # Save directly to output folder
        output_dir = Path(settings.LOCAL_OUTPUT_DIR)
        _get_or_create_dir(str(output_dir))
        file_path = output_dir / filename
        
        with open(file_path, 'wb') as f:
            f.write(excel_bytes)
        
        # Return the absolute file path instead of HTTP URL
        absolute_path = str(file_path.resolve())
        logger.info(f"Excel report saved locally to: {absolute_path}")
        return absolute_path
    else:
        # Upload to S3
        object_name = f"generated_files/{request_id}/{filename}"
        url = upload_file_to_s3(io.BytesIO(excel_bytes), object_name)
        logger.info(f"Excel report uploaded to S3: {object_name}")
        return url
