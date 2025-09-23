from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, HttpUrl, Field

class ProcessingStatus(str, Enum):
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class GenerationResponse(BaseModel):
    request_id: str
    output_image_url: str  # Primary image (first variation with white background)
    image_variations: List[str] = []  # Additional image variations with different backgrounds, default empty list
    output_video_url: Optional[str] = None
    excel_report_url: str
    metadata: Dict

class ErrorResponse(BaseModel):
    detail: str

class GenerationResult(BaseModel):
    output_image_url: str = Field(..., description="URL to the generated image")
    excel_report_url: str = Field(..., description="URL to the generated Excel report")
    metadata: dict = Field(default_factory=dict, description="Additional metadata about the generation")
