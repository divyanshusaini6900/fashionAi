import os
from google.cloud import storage
from google.cloud.exceptions import GoogleCloudError
from fastapi import HTTPException
from app.core.config import settings
import logging
import io

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_gcs_client():
    """Initializes and returns a GCS client."""
    try:
        # Set the credentials path
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = settings.GOOGLE_APPLICATION_CREDENTIALS
        client = storage.Client()
        return client
    except Exception as e:
        logger.error("Failed to initialize GCS client.", exc_info=True)
        raise HTTPException(status_code=500, detail="Server is not configured for GCS uploads.") from e

def upload_file_to_gcs(file_obj: io.BytesIO, object_name: str) -> str:
    """
    Upload a file-like object to a GCS bucket and return its public URL.

    Args:
        file_obj: File-like object to upload.
        object_name: The name of the object in the GCS bucket.

    Returns:
        The permanent URL of the uploaded file.
    """
    client = get_gcs_client()
    try:
        bucket = client.bucket(settings.GCS_BUCKET_NAME)
        blob = bucket.blob(object_name)
        
        # Reset file pointer to beginning
        file_obj.seek(0)
        blob.upload_from_file(file_obj)
        
        # Make the blob publicly readable
        blob.make_public()
        
        logger.info(f"Successfully uploaded {object_name} to GCS bucket {settings.GCS_BUCKET_NAME}.")
        return blob.public_url
    except GoogleCloudError as e:
        logger.error(f"Failed to upload {object_name} to GCS.", exc_info=True)
        raise HTTPException(status_code=500, detail=f"GCS operation failed: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred during GCS upload for {object_name}.", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")