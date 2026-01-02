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
import logging
from PIL import Image

# Import food classifier and nutrition service
from model.food_classifier import get_classifier
from services.nutrition_service import get_nutrition_service

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

# Initialize nutrition service
nutrition_service = get_nutrition_service()

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
    nutrition_info = nutrition_service.get_service_info()
    
    return {
        "status": "healthy",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "api_version": "1.0.0",
        "services": {
            "database": "not_implemented",
            "ml_model": "implemented",
            "nutrition_api": "implemented" if nutrition_info["api_available"] else "mock_only"
        },
        "classifier": classifier_info,
        "nutrition_service": nutrition_info
    }

@app.post("/analyze-food")
async def analyze_food(file: UploadFile = File(...)):
    """
    Analyze food image and return standardized classification with nutrition data.
    
    Args:
        file: Uploaded image file
        
    Returns:
        dict: Standardized food analysis response
    """
    # Validate file type
    if not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=400, 
            detail="Invalid file type. Please upload an image file (JPG, PNG, etc.)"
        )
    
    # Validate file size (max 10MB)
    max_size = 10 * 1024 * 1024  # 10MB
    content = await file.read()
    file_size = len(content)
    
    if file_size > max_size:
        raise HTTPException(
            status_code=413,  # Payload Too Large
            detail=f"File too large. Maximum size is 10MB. Current size: {file_size / (1024*1024):.2f}MB"
        )
    
    if file_size == 0:
        raise HTTPException(
            status_code=400,
            detail="Empty file uploaded. Please select a valid image file."
        )
    
    try:
        # Open and process image
        image = Image.open(io.BytesIO(content))
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Run enhanced food classification
        prediction_result = classifier.predict(
            image, 
            confidence_threshold=0.4, 
            top_k=3
        )
        
        # Get real nutrition data from USDA API
        food_name = prediction_result["food"]
        if food_name != "Unknown Food":
            nutrition_data = nutrition_service.get_nutrition_for_food(food_name)
        else:
            # For unknown foods, use generic mock data
            nutrition_data = nutrition_service._get_mock_nutrition_data("Unknown Food")
        
        # Extract nutrition values
        nutrition = nutrition_data["nutrition"]
        
        # Return standardized response format
        return JSONResponse(content={
            "food": food_name,
            "confidence": round(prediction_result["confidence"], 2),
            "calories": round(nutrition["calories"]),
            "protein": round(nutrition["protein"], 1),
            "carbs": round(nutrition["carbs"], 1),
            "fat": round(nutrition["fat"], 1),
            "unit": "per 100g"
        })
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Image.UnidentifiedImageError:
        raise HTTPException(
            status_code=400,
            detail="Invalid image file. The uploaded file could not be processed as an image."
        )
    except Exception as e:
        logger.error(f"Unexpected error during food analysis: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error occurred while processing the image. Please try again."
        )

@app.post("/analyze-food-debug")
async def analyze_food_debug(file: UploadFile = File(...)):
    """
    Debug version of food analysis with detailed information.
    
    Args:
        file: Uploaded image file
        
    Returns:
        dict: Detailed food analysis with all metadata and debug info
    """
    # Validate file type
    if not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=400, 
            detail="Invalid file type. Please upload an image file (JPG, PNG, etc.)"
        )
    
    # Validate file size (max 10MB)
    max_size = 10 * 1024 * 1024  # 10MB
    content = await file.read()
    file_size = len(content)
    
    if file_size > max_size:
        raise HTTPException(
            status_code=413,  # Payload Too Large
            detail=f"File too large. Maximum size is 10MB. Current size: {file_size / (1024*1024):.2f}MB"
        )
    
    if file_size == 0:
        raise HTTPException(
            status_code=400,
            detail="Empty file uploaded. Please select a valid image file."
        )
    
    try:
        # Open and process image
        image = Image.open(io.BytesIO(content))
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Run enhanced food classification
        prediction_result = classifier.predict(
            image, 
            confidence_threshold=0.4, 
            top_k=3
        )
        
        # Extract alternatives (food names only)
        alternatives = [alt['food'] for alt in prediction_result['alternatives']]
        
        # Get real nutrition data from USDA API
        food_name = prediction_result["food"]
        if food_name != "Unknown Food":
            nutrition_data = nutrition_service.get_nutrition_for_food(food_name)
        else:
            # For unknown foods, use generic mock data
            nutrition_data = nutrition_service._get_mock_nutrition_data("Unknown Food")
        
        # Extract nutrition values
        nutrition = nutrition_data["nutrition"]
        
        # Return detailed debug response
        return JSONResponse(content={
            # Standardized format
            "food": food_name,
            "confidence": round(prediction_result["confidence"], 2),
            "calories": round(nutrition["calories"]),
            "protein": round(nutrition["protein"], 1),
            "carbs": round(nutrition["carbs"], 1),
            "fat": round(nutrition["fat"], 1),
            "unit": "per 100g",
            
            # Additional debug information
            "debug": {
                "alternatives": alternatives,
                "threshold_met": prediction_result["threshold_met"],
                "inference_time_ms": prediction_result["inference_time_ms"],
                "model_info": prediction_result["model_info"],
                "raw_predictions": prediction_result["raw_predictions"],
                "nutrition_source": nutrition_data["source"],
                "nutrition_metadata": {
                    "fdc_id": nutrition_data.get("fdc_id"),
                    "data_type": nutrition_data.get("data_type"),
                    "all_nutrients_count": nutrition_data.get("all_nutrients_count", 0)
                },
                "file_info": {
                    "file_size_mb": round(file_size / (1024*1024), 2),
                    "image_mode": image.mode,
                    "image_size": image.size
                },
                "service_status": {
                    "usda_api_available": nutrition_service.get_service_info()["api_available"]
                }
            }
        })
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Image.UnidentifiedImageError:
        raise HTTPException(
            status_code=400,
            detail="Invalid image file. The uploaded file could not be processed as an image."
        )
    except Exception as e:
        logger.error(f"Unexpected error during food analysis debug: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error occurred while processing the image. Please try again."
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
