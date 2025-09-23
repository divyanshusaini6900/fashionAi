from typing import List
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, validator
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get the base directory of the project
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class Settings(BaseSettings):
    # Base Directory
    BASE_DIR: str = BASE_DIR
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Fashion Modeling AI"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # CORS Configuration
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str] | str:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # API Keys and External Services
    OPENAI_API_KEY: str
    REPLICATE_API_TOKEN: str
    GEMINI_API_KEY: str
    
    # AI Model Configuration
    USE_GEMINI_FOR_IMAGES: bool = True  # Set to False to use Replicate
    USE_GEMINI_FOR_VIDEOS: bool = True  # Set to False to use Replicate
    USE_GEMINI_FOR_TEXT: bool = True    # Set to False to use OpenAI

    # Storage Configuration
    USE_LOCAL_STORAGE: bool = True  # Set to False for S3
    LOCAL_BASE_URL: str = "http://localhost:8000"  # Base URL for local files
    LOCAL_OUTPUT_DIR: str = "output"  # Direct output folder for local files
    
    # S3 Configuration (optional for local development)
    S3_BUCKET_NAME: str = ""
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "ap-south-1"

    # File Storage Configuration
    GENERATED_FILES_DIR: str = "generated_files"
    UPLOAD_DIR: str = "generated_files/temp"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB

    class Config:
        case_sensitive = True
        env_file = ".env"

# Create global settings instance
settings = Settings()
