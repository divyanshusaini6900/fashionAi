from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI(
    title="Fashion Modeling AI API",
    description="API for processing fashion images and generating reports",
    version="1.0.0"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure the output directory exists
os.makedirs("output", exist_ok=True)

# Mount static files directory for serving generated files
# Images are saved to 'output' directory, so we mount that instead of 'generated_files'
app.mount("/files", StaticFiles(directory="output"), name="generated_files")

@app.get("/")
async def root():
    return {
        "message": "Fashion Modeling AI API is running",
        "status": "healthy",
        "version": "1.0.0"
    }

# Import and include API routers
from app.api.v1.endpoints import generate

app.include_router(
    generate.router,
    prefix="/api/v1",
    tags=["generation"]
)