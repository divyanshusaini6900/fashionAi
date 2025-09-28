from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class InputImage(BaseModel):
    url: str
    view: str
    backgrounds: List[int] = [0, 0, 1]  # Default to [0, 0, 1] as requested

class GenerationRequest(BaseModel):
    inputImages: List[InputImage]
    productType: str
    gender: str
    text: str
    isVideo: bool = False
    upscale: bool = True
    numberOfOutputs: int = 1
    generateCsv: bool = True
    aspectRatio: str = "9:16"  # Add aspect ratio field with default value

class GenerationResult(BaseModel):
    image_variations: List[str] = []  # All gemini generated images
    upscale_image: List[str] = []  # Upscaled images when upscale=True
    output_video_url: Optional[str] = None
    excel_report_url: Optional[str] = None
    metadata: Dict[str, Any] = {}

class ProcessingStatus(BaseModel):
    status: str
    message: str
    progress: Optional[float] = None

class GenerationResponse(BaseModel):
    request_id: str
    image_variations: List[str] = []  # All gemini generated images
    upscale_image: List[str] = []  # Upscaled images when upscale=True
    output_video_url: Optional[str] = None
    excel_report_url: Optional[str] = None
    metadata: Dict[str, Any] = {}
    
    class Config:
        schema_extra = {
            "example": {
                "request_id": "123e4567-e89b-12d3-a456-426614174000",
                "image_variations": [
                    "http://localhost:8000/files/generated/123e4567-e89b-12d3-a456-426614174000/variation1.jpg"
                ],
                "upscale_image": [  # Upscaled images when upscale=True
                    "http://localhost:8000/files/generated/123e4567-e89b-12d3-a456-426614174000/upscaled_image.jpg"
                ],
                "output_video_url": None,
                "excel_report_url": "http://localhost:8000/files/generated/123e4567-e89b-12d3-a456-426614174000/report.xlsx",
                "metadata": {
                    "processing_time": 45.2,
                    "model_used": "stable-diffusion-v3"
                }
            }
        }

class ErrorResponse(BaseModel):
    detail: str
    
    class Config:
        schema_extra = {
            "example": {
                "detail": "Error message describing what went wrong"
            }
        }

class FileAccessResponse(BaseModel):
    request_id: str
    files: List[Dict[str, str]]
    count: int
    
    class Config:
        schema_extra = {
            "example": {
                "request_id": "123e4567-e89b-12d3-a456-426614174000",
                "files": [
                    {
                        "filename": "image.jpg",
                        "url": "http://YOUR-IP-ADDRESS/files/generated/123e4567-e89b-12d3-a456-426614174000/image.jpg",
                        "type": "image"
                    },
                    {
                        "filename": "report.xlsx",
                        "url": "http://YOUR-IP-ADDRESS/files/generated/123e4567-e89b-12d3-a456-426614174000/report.xlsx",
                        "type": "excel"
                    }
                ],
                "count": 2
            }
        }