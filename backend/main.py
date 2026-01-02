"""
FoodSnap AI Backend - FastAPI Application

This is the main entry point for the FoodSnap AI backend service.
It provides REST API endpoints for food image analysis and nutrition information.

Author: FoodSnap AI Team
Version: 1.0.0
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os
import io
from PIL import Image

# Import food classifier
from model.food_classifier import get_classifier

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

# Initialize food classifier (loaded once at startup)
classifier = get_classifier(model_name="resnet50")

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
    classifier_info = classifier.get_class_info()
    
    return {
        "status": "healthy",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "api_version": "1.0.0",
        "services": {
            "database": "not_implemented",
            "ml_model": "implemented",
            "nutrition_api": "not_implemented"
        },
        "classifier": classifier_info
    }

@app.post("/analyze-food")
async def analyze_food(file: UploadFile = File(...)):
    """
    Analyze food image and return classification results.
    
    Args:
        file: Uploaded image file
        
    Returns:
        dict: Food classification results with confidence score
    """
    # Validate file type
    if not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=400, 
            detail="File must be an image (JPG, PNG, etc.)"
        )
    
    # Validate file size (max 10MB)
    max_size = 10 * 1024 * 1024  # 10MB
    file_size = 0
    content = await file.read()
    file_size = len(content)
    
    if file_size > max_size:
        raise HTTPException(
            status_code=400,
            detail=f"File size must be less than 10MB. Current size: {file_size / (1024*1024):.2f}MB"
        )
    
    try:
        # Open and process image
        image = Image.open(io.BytesIO(content))
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Run food classification
        prediction_result = classifier.predict(image)
        
        # Return results
        return JSONResponse(content={
            "success": True,
            "food_name": prediction_result["predicted_class"],
            "confidence": prediction_result["confidence"],
            "model_info": {
                "model_name": prediction_result["model_name"],
                "device": prediction_result["device"]
            },
            "portion_size": "100g",  # Fixed portion size for MVP
            "nutrition": {
                "calories": 150,  # Mock nutrition data for now
                "protein": 5.0,
                "carbs": 20.0,
                "fat": 3.0,
                "source": "mock_data"
            }
        })
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error processing image: {str(e)}"
        )

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
