"""
FoodSnap AI Backend - FastAPI Application

This is the main entry point for the FoodSnap AI backend service.
It provides REST API endpoints for food image analysis and nutrition information.

Author: FoodSnap AI Team
Version: 1.0.0
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI application with metadata
app = FastAPI(
    title="FoodSnap AI API",
    description="API for food image analysis and nutrition information",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000",
        "http://localhost:5173",  # Vite default port
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """
    Health check endpoint for the API.
    
    Returns:
        dict: Basic API information and status
    """
    return {
        "message": "FoodSnap AI API is running",
        "status": "healthy",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
async def health_check():
    """
    Detailed health check endpoint.
    
    Returns:
        dict: Detailed health status including environment info
    """
    return {
        "status": "healthy",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "api_version": "1.0.0",
        "services": {
            "database": "not_implemented",
            "ml_model": "not_implemented",
            "nutrition_api": "not_implemented"
        }
    }

# Import and include routers (will be added as we implement features)
# from api.routes import food_analysis, nutrition
# app.include_router(food_analysis.router, prefix="/api/v1")
# app.include_router(nutrition.router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    
    # Server configuration
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    
    print(f"🚀 Starting FoodSnap AI API server...")
    print(f"📍 Server will be available at: http://{host}:{port}")
    print(f"📚 API Documentation: http://{host}:{port}/docs")
    print(f"🔍 Alternative Docs: http://{host}:{port}/redoc")
    
    # Run the FastAPI application with Uvicorn
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,  # Enable auto-reload for development
        log_level="info"
    )
