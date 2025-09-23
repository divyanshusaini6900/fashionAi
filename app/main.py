from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

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

# Mount static files directory for serving generated files
app.mount("/files", StaticFiles(directory="generated_files"), name="generated_files")

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
