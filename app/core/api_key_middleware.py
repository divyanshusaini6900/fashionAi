from fastapi import Request, HTTPException, Depends, Response
from fastapi.security import APIKeyHeader
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from app.core.config import settings
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Define the API key header scheme
api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)

class APIKeyMiddleware(BaseHTTPMiddleware):
    """Middleware to handle API key authentication"""
    
    def __init__(self, app):
        super().__init__(app)
        # In a production environment, you would store and validate API keys in a database
        # For this implementation, we'll use a simple approach with environment variables
        self.api_keys = self._load_api_keys()
        logger.info(f"Loaded {len(self.api_keys)} valid API keys")
    
    def _load_api_keys(self):
        """Load valid API keys from environment or configuration"""
        # For now, we'll accept the same keys used for other services as valid API keys
        # In a real implementation, you would have a separate set of API keys
        keys = []
        
        # Add the existing API keys as valid x-api-keys
        if hasattr(settings, 'OPENAI_API_KEY') and settings.OPENAI_API_KEY:
            keys.append(settings.OPENAI_API_KEY)
        if hasattr(settings, 'REPLICATE_API_TOKEN') and settings.REPLICATE_API_TOKEN:
            keys.append(settings.REPLICATE_API_TOKEN)
        if hasattr(settings, 'GEMINI_API_KEY') and settings.GEMINI_API_KEY:
            keys.append(settings.GEMINI_API_KEY)
            
        # Add a specific API key for the service if defined
        if hasattr(settings, 'SERVICE_API_KEY') and settings.SERVICE_API_KEY:
            keys.append(settings.SERVICE_API_KEY)
            
        # Remove any empty keys
        keys = [key for key in keys if key]
        
        return keys
    
    async def dispatch(self, request: Request, call_next):
        """Process the request and validate API key if required"""
        # Only apply API key validation to specific endpoints
        protected_paths = [
            "/api/v1/generate/image",
            "/api/v1/generate"
        ]
        
        # Check if this path requires API key authentication
        if any(request.url.path.startswith(path) for path in protected_paths):
            # Get the API key from the header
            api_key = request.headers.get("x-api-key")
            
            logger.info(f"API key authentication required for {request.url.path}")
            
            # If no API key provided, check if we're in development mode
            if not api_key:
                if settings.ENVIRONMENT == "development":
                    # In development mode, allow requests without API key
                    logger.warning("No API key provided in development mode - allowing request")
                else:
                    # In production mode, reject requests without API key
                    logger.warning("API key is missing in production mode")
                    return JSONResponse(
                        status_code=401,
                        content={"detail": "API key is missing. Please provide x-api-key header."}
                    )
            else:
                # Validate the API key
                if not self._validate_api_key(api_key):
                    logger.warning(f"Invalid API key provided: {api_key[:10]}...")
                    return JSONResponse(
                        status_code=401,
                        content={"detail": "Invalid API key. Please provide a valid x-api-key header."}
                    )
                else:
                    logger.info("API key validated successfully")
        
        # Continue with the request
        response = await call_next(request)
        return response
    
    def _validate_api_key(self, api_key: str) -> bool:
        """Validate the provided API key"""
        # In a production environment, you would check against a database of valid keys
        # For this implementation, we check against our loaded keys
        is_valid = api_key in self.api_keys
        logger.debug(f"API key validation result: {is_valid}")
        return is_valid

# Create a dependency for use with specific endpoints
async def verify_api_key(api_key: str = Depends(api_key_header)):
    """Dependency to verify API key for specific endpoints"""
    # In development mode, allow missing API keys
    if not api_key and settings.ENVIRONMENT == "development":
        logger.info("No API key provided in development mode - allowing request (dependency)")
        return True
    
    # Create middleware instance to validate key
    middleware = APIKeyMiddleware(None)  # Pass None as app since we only need validation
    if not middleware._validate_api_key(api_key):
        logger.warning(f"Invalid API key provided in dependency: {api_key[:10]}...")
        raise HTTPException(
            status_code=401,
            detail="Invalid API key. Please provide a valid x-api-key header."
        )
    logger.info("API key validated successfully (dependency)")
    return True