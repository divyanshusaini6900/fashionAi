from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import asyncio
from contextlib import asynccontextmanager

from app.services.task_queue import start_task_queue, stop_task_queue

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events"""
    # Startup
    print("🚀 Starting Fashion Modeling AI with Parallel Processing...")
    await start_task_queue()
    print("✅ Task queue system initialized")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down Fashion Modeling AI...")
    await stop_task_queue()
    print("✅ Task queue system stopped")

app = FastAPI(
    title="Fashion Modeling AI API",
    description="API for processing fashion images and generating reports",
    version="1.0.0",
    lifespan=lifespan
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