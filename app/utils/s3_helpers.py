import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError
from fastapi import HTTPException
from app.core.config import settings
import logging
from typing import IO

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_s3_client():
    """Initializes and returns an S3 client."""
    try:
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        return s3_client
    except (NoCredentialsError, PartialCredentialsError) as e:
        logger.error("AWS credentials not found or incomplete.", exc_info=True)
        raise HTTPException(status_code=500, detail="Server is not configured for S3 uploads.") from e

def upload_file_to_s3(file_obj: IO[bytes], object_name: str) -> str:
    """
    Upload a file-like object to an S3 bucket and return its public URL.
    This relies on a bucket policy to make objects public.

    Args:
        file_obj: File-like object to upload.
        object_name: The name of the object in the S3 bucket.

    Returns:
        The permanent URL of the uploaded file.
    """
    s3_client = get_s3_client()
    try:
        s3_client.upload_fileobj(
            file_obj,
            settings.S3_BUCKET_NAME,
            object_name
        )
        
        # Construct the permanent public URL
        file_url = f"https://{settings.S3_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{object_name}"
        
        logger.info(f"Successfully uploaded {object_name} to S3 bucket {settings.S3_BUCKET_NAME}.")
        return file_url
    except ClientError as e:
        logger.error(f"Failed to upload {object_name} to S3.", exc_info=True)
        raise HTTPException(status_code=500, detail=f"S3 operation failed: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred during S3 upload for {object_name}.", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}") 