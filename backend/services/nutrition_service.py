"""
Nutrition Service Module

This module handles integration with the USDA FoodData Central API
to fetch nutritional information for food items.

Author: FoodSnap AI Team
Version: 1.0.0
"""

import requests
import os
import logging
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NutritionService:
    """
    Service for fetching nutrition data from USDA FoodData Central API.
    
    Provides methods to search for foods and extract nutritional information
    normalized to 100g portions.
    """
    
    def __init__(self):
        """Initialize the nutrition service with API configuration."""
        self.api_key = os.getenv("USDA_API_KEY")
        self.base_url = "https://api.nal.usda.gov/fdc/v1/foods/search"
        self.food_details_url = "https://api.nal.usda.gov/fdc/v1/food/"
        
        if not self.api_key:
            logger.warning("USDA_API_KEY not found in environment variables. Using mock data.")
        else:
            logger.info("USDA FoodData Central API service initialized")
    
    def _make_api_request(self, url: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Make a request to the USDA API with error handling.
        
        Args:
            url: API endpoint URL
            params: Query parameters
            
        Returns:
            API response data or None if request fails
        """
        try:
            params["api_key"] = self.api_key
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"USDA API request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in API request: {e}")
            return None
    
    def search_food(self, food_name: str, page_size: int = 5) -> Optional[List[Dict[str, Any]]]:
        """
        Search for foods by name in USDA database.
        
        Args:
            food_name: Name of the food to search for
            page_size: Number of results to return
            
        Returns:
            List of food items or None if search fails
        """
        if not self.api_key:
            logger.warning("No USDA API key available")
            return None
        
        params = {
            "query": food_name,
            "dataType": ["Foundation", "SR Legacy", "Survey (FNDDS)"],
            "pageSize": page_size,
            "sortBy": "dataType.keyword"
        }
        
        logger.info(f"Searching USDA database for: {food_name}")
        response_data = self._make_api_request(self.base_url, params)
        
        if response_data and "foods" in response_data:
            foods = response_data["foods"]
            logger.info(f"Found {len(foods)} results for '{food_name}'")
            return foods
        
        logger.warning(f"No results found for '{food_name}'")
        return None
    
    def get_food_details(self, fdc_id: int) -> Optional[Dict[str, Any]]:
        """
        Get detailed nutritional information for a specific food.
        
        Args:
            fdc_id: USDA FoodData Central ID
            
        Returns:
            Detailed food information or None if request fails
        """
        if not self.api_key:
            return None
        
        url = f"{self.food_details_url}{fdc_id}"
        logger.info(f"Fetching details for FDC ID: {fdc_id}")
        
        return self._make_api_request(url, {})
    
    def _extract_nutrient_value(self, nutrients: List[Dict[str, Any]], nutrient_names: List[str]) -> Optional[float]:
        """
        Extract nutrient value from nutrients list by checking multiple possible names.
        
        Args:
            nutrients: List of nutrient objects from USDA API
            nutrient_names: List of possible nutrient names to check
            
        Returns:
            Nutrient value or None if not found
        """
        for nutrient in nutrients:
            nutrient_name = nutrient.get("nutrientName", "").lower()
            unit = nutrient.get("unitName", "").lower()
            
            for target_name in nutrient_names:
                if target_name.lower() in nutrient_name:
                    value = nutrient.get("value")
                    if value is not None:
                        # Convert to 100g if needed
                        if "per 100 g" not in nutrient_name.lower():
                            # Check if we have serving size info
                            serving_size = nutrient.get("servingSize", 100)
                            if serving_size and serving_size != 100:
                                value = (value / serving_size) * 100
                        return float(value)
        
        return None
    
    def _normalize_to_100g(self, food_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Extract and normalize nutritional values to 100g portion.
        
        Args:
            food_data: Food data from USDA API
            
        Returns:
            Dictionary of normalized nutritional values
        """
        nutrients = food_data.get("foodNutrients", [])
        
        # Extract calories (Energy)
        calorie_names = ["energy", "calories", "energy (atwater)"]
        calories = self._extract_nutrient_value(nutrients, calorie_names)
        
        # Extract protein
        protein_names = ["protein", "total protein"]
        protein = self._extract_nutrient_value(nutrients, protein_names)
        
        # Extract carbohydrates
        carb_names = ["carbohydrate", "total carbohydrate", "carbs"]
        carbs = self._extract_nutrient_value(nutrients, carb_names)
        
        # Extract fat
        fat_names = ["total lipid", "fat", "total fat"]
        fat = self._extract_nutrient_value(nutrients, fat_names)
        
        return {
            "calories": calories or 0.0,
            "protein": protein or 0.0,
            "carbs": carbs or 0.0,
            "fat": fat or 0.0
        }
    
    def get_nutrition_for_food(self, food_name: str) -> Dict[str, Any]:
        """
        Get nutritional information for a food item.
        
        Args:
            food_name: Name of the food to search for
            
        Returns:
            Dictionary containing nutritional information and metadata
        """
        # Try to find the food in USDA database
        foods = self.search_food(food_name)
        
        if foods and len(foods) > 0:
            # Use the first (most relevant) result
            best_food = foods[0]
            fdc_id = best_food.get("fdcId")
            description = best_food.get("description", "Unknown")
            data_type = best_food.get("dataType", "Unknown")
            
            logger.info(f"Using USDA data: {description} (FDC ID: {fdc_id})")
            
            # Get detailed nutrition info
            nutrition = self._normalize_to_100g(best_food)
            
            return {
                "success": True,
                "food_name": description,
                "fdc_id": fdc_id,
                "data_type": data_type,
                "nutrition": nutrition,
                "source": "usda_api",
                "portion_size": "100g",
                "all_nutrients_count": len(best_food.get("foodNutrients", []))
            }
        
        # Fallback to mock data if no API key or no results
        logger.warning(f"Using mock nutrition data for: {food_name}")
        return self._get_mock_nutrition_data(food_name)
    
    def _get_mock_nutrition_data(self, food_name: str) -> Dict[str, Any]:
        """
        Generate mock nutrition data when USDA API is unavailable.
        
        Args:
            food_name: Name of the food for mock data
            
        Returns:
            Mock nutritional information
        """
        # Simple mock data based on food categories
        food_lower = food_name.lower()
        
        if any(x in food_lower for x in ["apple", "banana", "orange", "fruit"]):
            nutrition = {"calories": 52, "protein": 0.3, "carbs": 14, "fat": 0.2}
        elif any(x in food_lower for x in ["pizza", "burger", "fries", "fast food"]):
            nutrition = {"calories": 285, "protein": 12, "carbs": 35, "fat": 12}
        elif any(x in food_lower for x in ["salad", "vegetable", "broccoli", "carrot"]):
            nutrition = {"calories": 35, "protein": 2.0, "carbs": 7, "fat": 0.2}
        elif any(x in food_lower for x in ["chicken", "meat", "beef", "pork"]):
            nutrition = {"calories": 165, "protein": 25, "carbs": 0, "fat": 7}
        elif any(x in food_lower for x in ["bread", "rice", "pasta", "carb"]):
            nutrition = {"calories": 130, "protein": 4, "carbs": 25, "fat": 1}
        else:
            # Default generic food
            nutrition = {"calories": 150, "protein": 5.0, "carbs": 20.0, "fat": 3.0}
        
        return {
            "success": True,
            "food_name": food_name,
            "fdc_id": None,
            "data_type": "Mock Data",
            "nutrition": nutrition,
            "source": "mock_data",
            "portion_size": "100g",
            "all_nutrients_count": 4
        }
    
    def get_service_info(self) -> Dict[str, Any]:
        """
        Get information about the nutrition service.
        
        Returns:
            Service configuration and status
        """
        return {
            "api_available": bool(self.api_key),
            "base_url": self.base_url,
            "supported_data_types": ["Foundation", "SR Legacy", "Survey (FNDDS)"],
            "normalization": "per_100g",
            "extracted_nutrients": ["calories", "protein", "carbs", "fat"]
        }

# Global nutrition service instance
_nutrition_service = None

def get_nutrition_service() -> NutritionService:
    """
    Get or create the global nutrition service instance.
    
    Returns:
        NutritionService instance
    """
    global _nutrition_service
    
    if _nutrition_service is None:
        _nutrition_service = NutritionService()
    
    return _nutrition_service
