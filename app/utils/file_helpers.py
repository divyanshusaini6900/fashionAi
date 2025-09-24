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

# Conditional import for Google Cloud Storage
if not settings.USE_LOCAL_STORAGE and settings.GCS_BUCKET_NAME:
    from app.utils.gcs_helpers import upload_file_to_gcs

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
    Saves a single generated image locally or uploads to Google Cloud Storage based on USE_LOCAL_STORAGE setting.
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
        # Upload to Google Cloud Storage
        object_name = f"generated_files/{request_id}/{filename}"
        if settings.GCS_BUCKET_NAME:
            url = upload_file_to_gcs(io.BytesIO(image_bytes), object_name)
            logger.info(f"Image uploaded to GCS: {object_name}")
            return url
        else:
            # Fallback to local storage if no cloud storage is configured
            output_dir = Path(settings.LOCAL_OUTPUT_DIR)
            _get_or_create_dir(str(output_dir))
            file_path = output_dir / filename
            
            with open(file_path, 'wb') as f:
                f.write(image_bytes)
            
            absolute_path = str(file_path.resolve())
            logger.info(f"Image saved locally to: {absolute_path} (fallback)")
            return absolute_path

def save_generated_image_variations(image_bytes_dict: Dict[str, bytes], request_id: str) -> Dict[str, str]:
    """
    Saves a dictionary of image variations locally or uploads to Google Cloud Storage based on USE_LOCAL_STORAGE setting,
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
        # Upload to Google Cloud Storage
        for view_name, image_bytes in image_bytes_dict.items():
            # Sanitize view_name to be used in a filename
            safe_view_name = view_name.replace(" ", "_").lower()
            filename = f"{request_id}_generated_{safe_view_name}.jpg"
            object_name = f"generated_files/{request_id}/{filename}"
            
            # Upload to Google Cloud Storage
            if settings.GCS_BUCKET_NAME:
                url = upload_file_to_gcs(io.BytesIO(image_bytes), object_name)
                paths_or_urls[view_name] = url
                logger.info(f"Image variation uploaded to GCS: {object_name}")
            else:
                # Fallback to local storage if no cloud storage is configured
                output_dir = Path(settings.LOCAL_OUTPUT_DIR)
                _get_or_create_dir(str(output_dir))
                file_path = output_dir / filename
                
                with open(file_path, 'wb') as f:
                    f.write(image_bytes)
                
                absolute_path = str(file_path.resolve())
                paths_or_urls[view_name] = absolute_path
                logger.info(f"Image variation saved locally to: {absolute_path} (fallback)")
    
    return paths_or_urls

def save_generated_video(video_bytes: bytes, request_id: str) -> str:
    """
    Saves a generated video locally or uploads to Google Cloud Storage based on USE_LOCAL_STORAGE setting.
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
        # Upload to Google Cloud Storage
        object_name = f"generated_files/{request_id}/{filename}"
        if settings.GCS_BUCKET_NAME:
            url = upload_file_to_gcs(io.BytesIO(video_bytes), object_name)
            logger.info(f"Video uploaded to GCS: {object_name}")
            return url
        else:
            # Fallback to local storage if no cloud storage is configured
            output_dir = Path(settings.LOCAL_OUTPUT_DIR)
            _get_or_create_dir(str(output_dir))
            file_path = output_dir / filename
            
            with open(file_path, 'wb') as f:
                f.write(video_bytes)
            
            absolute_path = str(file_path.resolve())
            logger.info(f"Video saved locally to: {absolute_path} (fallback)")
            return absolute_path

def save_excel_report(excel_bytes: bytes, request_id: str) -> str:
    """
    Saves a generated Excel report locally or uploads to Google Cloud Storage based on USE_LOCAL_STORAGE setting.
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
        # Upload to Google Cloud Storage
        object_name = f"generated_files/{request_id}/{filename}"
        if settings.GCS_BUCKET_NAME:
            url = upload_file_to_gcs(io.BytesIO(excel_bytes), object_name)
            logger.info(f"Excel report uploaded to GCS: {object_name}")
            return url
        else:
            # Fallback to local storage if no cloud storage is configured
            output_dir = Path(settings.LOCAL_OUTPUT_DIR)
            _get_or_create_dir(str(output_dir))
            file_path = output_dir / filename
            
            with open(file_path, 'wb') as f:
                f.write(excel_bytes)
            
            absolute_path = str(file_path.resolve())
            logger.info(f"Excel report saved locally to: {absolute_path} (fallback)")
            return absolute_path

def save_original_and_upscaled_images(
    original_bytes_dict: Dict[str, bytes], 
    upscaled_bytes_dict: Dict[str, bytes], 
    request_id: str
) -> Dict[str, Dict[str, str]]:
    """
    Saves both original and upscaled images with distinct naming conventions.
    
    Args:
        original_bytes_dict: Dictionary of original image bytes keyed by view name
        upscaled_bytes_dict: Dictionary of upscaled image bytes keyed by view name
        request_id: Unique request identifier
        
    Returns:
        Dictionary with 'original' and 'upscaled' keys, each containing
        a dictionary of file paths/urls keyed by view name
    """
    result = {
        'original': {},
        'upscaled': {}
    }
    
    # Save original images
    if original_bytes_dict:
        for view_name, image_bytes in original_bytes_dict.items():
            # Sanitize view_name to be used in a filename
            safe_view_name = view_name.replace(" ", "_").lower()
            filename = f"{request_id}_original_{safe_view_name}.jpg"
            
            if settings.USE_LOCAL_STORAGE:
                # Save directly to output folder
                output_dir = Path(settings.LOCAL_OUTPUT_DIR)
                _get_or_create_dir(str(output_dir))
                file_path = output_dir / filename
                
                with open(file_path, 'wb') as f:
                    f.write(image_bytes)
                
                # Return the absolute file path instead of HTTP URL
                absolute_path = str(file_path.resolve())
                result['original'][view_name] = absolute_path
                logger.info(f"Original image saved locally to: {absolute_path}")
            else:
                # Upload to Google Cloud Storage
                object_name = f"generated_files/{request_id}/{filename}"
                if settings.GCS_BUCKET_NAME:
                    url = upload_file_to_gcs(io.BytesIO(image_bytes), object_name)
                    result['original'][view_name] = url
                    logger.info(f"Original image uploaded to GCS: {object_name}")
                else:
                    # Fallback to local storage if no cloud storage is configured
                    output_dir = Path(settings.LOCAL_OUTPUT_DIR)
                    _get_or_create_dir(str(output_dir))
                    file_path = output_dir / filename
                    
                    with open(file_path, 'wb') as f:
                        f.write(image_bytes)
                    
                    absolute_path = str(file_path.resolve())
                    result['original'][view_name] = absolute_path
                    logger.info(f"Original image saved locally to: {absolute_path} (fallback)")
    
    # Save upscaled images
    if upscaled_bytes_dict:
        for view_name, image_bytes in upscaled_bytes_dict.items():
            # Sanitize view_name to be used in a filename
            safe_view_name = view_name.replace(" ", "_").lower()
            filename = f"{request_id}_upscaled_{safe_view_name}.jpg"
            
            if settings.USE_LOCAL_STORAGE:
                # Save directly to output folder
                output_dir = Path(settings.LOCAL_OUTPUT_DIR)
                _get_or_create_dir(str(output_dir))
                file_path = output_dir / filename
                
                with open(file_path, 'wb') as f:
                    f.write(image_bytes)
                
                # Return the absolute file path instead of HTTP URL
                absolute_path = str(file_path.resolve())
                result['upscaled'][view_name] = absolute_path
                logger.info(f"Upscaled image saved locally to: {absolute_path}")
            else:
                # Upload to Google Cloud Storage
                object_name = f"generated_files/{request_id}/{filename}"
                if settings.GCS_BUCKET_NAME:
                    url = upload_file_to_gcs(io.BytesIO(image_bytes), object_name)
                    result['upscaled'][view_name] = url
                    logger.info(f"Upscaled image uploaded to GCS: {object_name}")
                else:
                    # Fallback to local storage if no cloud storage is configured
                    output_dir = Path(settings.LOCAL_OUTPUT_DIR)
                    _get_or_create_dir(str(output_dir))
                    file_path = output_dir / filename
                    
                    with open(file_path, 'wb') as f:
                        f.write(image_bytes)
                    
                    absolute_path = str(file_path.resolve())
                    result['upscaled'][view_name] = absolute_path
                    logger.info(f"Upscaled image saved locally to: {absolute_path} (fallback)")
    
    return result