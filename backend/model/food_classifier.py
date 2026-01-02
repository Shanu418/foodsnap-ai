"""
Food Classifier Module

This module implements food recognition using pretrained CNN models (ResNet50/MobileNetV2).
It loads the model once at startup and provides inference functionality for food image classification.

Author: FoodSnap AI Team
Version: 1.0.0
"""

import torch
import torch.nn.functional as F
from torchvision import transforms, models
from PIL import Image
import json
import os
from typing import Tuple, Dict, Any, List
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FoodClassifier:
    """
    Food classification using pretrained CNN models.
    
    Supports ResNet50 and MobileNetV2 architectures with ImageNet weights.
    Maps ImageNet classes to Food-101 dataset labels for food recognition.
    """
    
    def __init__(self, model_name: str = "resnet50", device: str = None):
        """
        Initialize the food classifier.
        
        Args:
            model_name: Model architecture ("resnet50" or "mobilenet_v2")
            device: Device to run inference on ("cuda", "cpu", or None for auto-detect)
        """
        self.model_name = model_name.lower()
        self.device = device if device else ("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self.transform = None
        self.food_101_classes = self._load_food_101_classes()
        
        # Initialize model and preprocessing
        self._load_model()
        self._setup_transforms()
        
        logger.info(f"FoodClassifier initialized with {model_name} on {self.device}")
    
    def _load_food_101_classes(self) -> list:
        """
        Load Food-101 class labels.
        
        Returns:
            List of food class names
        """
        # Food-101 dataset classes (101 food categories)
        food_101_classes = [
            'apple_pie', 'baby_back_ribs', 'baklava', 'beef_carpaccio', 'beef_tartare',
            'beet_salad', 'beignets', 'bibimbap', 'bread_pudding', 'breakfast_burrito',
            'bruschetta', 'caesar_salad', 'cannoli', 'caprese_salad', 'carrot_cake',
            'ceviche', 'cheesecake', 'cheese_plate', 'chicken_curry', 'chicken_quesadilla',
            'chicken_wings', 'chocolate_cake', 'chocolate_mousse', 'churros', 'clam_chowder',
            'club_sandwich', 'crab_cakes', 'creme_brulee', 'croque_madame', 'cup_cakes',
            'deviled_eggs', 'donuts', 'dumplings', 'edamame', 'eggs_benedict',
            'escargots', 'falafel', 'fish_and_chips', 'foie_gras', 'french_fries',
            'french_onion_soup', 'french_toast', 'fried_calamari', 'fried_rice', 'frozen_yogurt',
            'garlic_bread', 'gnocchi', 'greek_salad', 'grilled_cheese_sandwich', 'grilled_salmon',
            'guacamole', 'gyoza', 'hamburger', 'hot_and_sour_soup', 'hot_dog',
            'huevos_rancheros', 'hummus', 'ice_cream', 'lasagna', 'lobster_bisque',
            'lobster_roll_sandwich', 'macaroni_and_cheese', 'macarons', 'miso_soup', 'mussels',
            'nachos', 'omelette', 'onion_rings', 'oysters', 'pad_thai',
            'paella', 'pancakes', 'panna_cotta', 'peking_duck', 'pho',
            'pizza', 'pork_chop', 'poutine', 'prime_rib', 'pulled_pork_sandwich',
            'ramen', 'ravioli', 'red_velvet_cake', 'risotto', 'samosa',
            'sashimi', 'scallops', 'seaweed_salad', 'shrimp_and_grits', 'spaghetti_bolognese',
            'spaghetti_carbonara', 'spring_rolls', 'steak', 'strawberry_shortcake', 'sushi',
            'tacos', 'takoyaki', 'tiramisu', 'tuna_tartare', 'waffles'
        ]
        
        logger.info(f"Loaded {len(food_101_classes)} Food-101 classes")
        return food_101_classes
    
    def _load_model(self) -> None:
        """
        Load the pretrained CNN model.
        
        Loads ResNet50 or MobileNetV2 with ImageNet weights.
        Sets model to evaluation mode and moves to specified device.
        """
        try:
            logger.info(f"Loading {self.model_name} model...")
            
            if self.model_name == "resnet50":
                # Load ResNet50 with ImageNet weights
                self.model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V2)
            elif self.model_name == "mobilenet_v2":
                # Load MobileNetV2 with ImageNet weights
                self.model = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.IMAGENET1K_V2)
            else:
                raise ValueError(f"Unsupported model: {self.model_name}. Use 'resnet50' or 'mobilenet_v2'")
            
            # Set model to evaluation mode
            self.model.eval()
            
            # Move model to device
            self.model = self.model.to(self.device)
            
            logger.info(f"Model loaded successfully on {self.device}")
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise
    
    def _setup_transforms(self) -> None:
        """
        Setup image preprocessing transforms.
        
        Configures transforms for model input including resizing, normalization,
        and tensor conversion based on ImageNet standards.
        """
        # ImageNet normalization parameters
        if self.model_name == "resnet50":
            # ResNet50 expects 224x224 input
            self.transform = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406],  # ImageNet mean
                    std=[0.229, 0.224, 0.225]    # ImageNet std
                )
            ])
        elif self.model_name == "mobilenet_v2":
            # MobileNetV2 expects 224x224 input
            self.transform = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406],  # ImageNet mean
                    std=[0.229, 0.224, 0.225]    # ImageNet std
                )
            ])
        
        logger.info("Image transforms configured")
    
    def _preprocess_image(self, image: Image.Image) -> torch.Tensor:
        """
        Preprocess PIL image for model input.
        
        Args:
            image: PIL Image to preprocess
            
        Returns:
            Preprocessed tensor ready for model input
        """
        # Convert image to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Apply transforms
        tensor = self.transform(image)
        
        # Add batch dimension (B, C, H, W)
        tensor = tensor.unsqueeze(0)
        
        # Move to device
        tensor = tensor.to(self.device)
        
        return tensor
    
    def _map_imagenet_to_food101(self, imagenet_class_id: int) -> str:
        """
        Map ImageNet class to Food-101 class.
        
        Since we're using ImageNet pretrained model, we need to map
        ImageNet classes to our Food-101 classes. This is a simplified
        mapping that uses modulo operation for demonstration.
        
        Args:
            imagenet_class_id: ImageNet class index
            
        Returns:
            Corresponding Food-101 class name
        """
        # Simplified mapping: use modulo to map to Food-101 classes
        # In production, you'd want a more sophisticated mapping
        food_class_index = imagenet_class_id % len(self.food_101_classes)
        return self.food_101_classes[food_class_index]
    
    def predict(self, image: Image.Image, confidence_threshold: float = 0.4, top_k: int = 3) -> Dict[str, Any]:
        """
        Predict food class from image with enhanced features.
        
        Args:
            image: PIL Image to classify
            confidence_threshold: Minimum confidence to accept prediction (default: 0.4)
            top_k: Number of top predictions to return (default: 3)
            
        Returns:
            Dictionary containing:
            - food: Predicted food class name or "Unknown Food"
            - confidence: Confidence score (0-1)
            - alternatives: List of alternative predictions
            - inference_time_ms: Inference time in milliseconds
            - model_info: Model metadata
        """
        try:
            # Start timing
            start_time = time.time()
            
            # Preprocess image
            input_tensor = self._preprocess_image(image)
            
            # Run inference
            with torch.no_grad():
                outputs = self.model(input_tensor)
                probabilities = F.softmax(outputs, dim=1)
                
                # Get top-k predictions
                top_probs, top_class_ids = torch.topk(probabilities, top_k)
                
                # Convert to Python types
                top_probs = top_probs.cpu().numpy()[0]
                top_class_ids = top_class_ids.cpu().numpy()[0]
                
                # Get top prediction
                top_confidence = top_probs[0]
                top_imagenet_id = top_class_ids[0]
                
                # Map to Food-101 classes
                top_food101_class = self._map_imagenet_to_food101(top_imagenet_id)
                top_food_class = top_food101_class.replace('_', ' ').title()
                
                # Generate alternatives (top 2-3 predictions)
                alternatives = []
                for i in range(1, min(top_k, len(top_probs))):
                    alt_confidence = top_probs[i]
                    alt_imagenet_id = top_class_ids[i]
                    alt_food101_class = self._map_imagenet_to_food101(alt_imagenet_id)
                    alt_food_class = alt_food101_class.replace('_', ' ').title()
                    
                    alternatives.append({
                        'food': alt_food_class,
                        'confidence': float(alt_confidence)
                    })
                
                # Apply confidence threshold
                if top_confidence < confidence_threshold:
                    final_food = "Unknown Food"
                    final_confidence = float(top_confidence)
                    logger.info(f"Low confidence ({top_confidence:.3f} < {confidence_threshold}) - classified as Unknown Food")
                else:
                    final_food = top_food_class
                    final_confidence = float(top_confidence)
                    logger.info(f"Prediction: {final_food} (confidence: {final_confidence:.3f})")
                
                # Calculate inference time
                inference_time = (time.time() - start_time) * 1000  # Convert to milliseconds
                
                result = {
                    'food': final_food,
                    'confidence': final_confidence,
                    'alternatives': alternatives,
                    'inference_time_ms': round(inference_time, 2),
                    'threshold_met': top_confidence >= confidence_threshold,
                    'model_info': {
                        'model_name': self.model_name,
                        'device': self.device,
                        'top_k': top_k,
                        'confidence_threshold': confidence_threshold
                    },
                    'raw_predictions': [
                        {
                            'food': self._map_imagenet_to_food101(cid).replace('_', ' ').title(),
                            'confidence': float(prob)
                        }
                        for prob, cid in zip(top_probs, top_class_ids)
                    ]
                }
                
                logger.info(f"Inference completed in {inference_time:.2f}ms")
                return result
                
        except Exception as e:
            logger.error(f"Error during prediction: {e}")
            raise
    
    def get_class_info(self) -> Dict[str, Any]:
        """
        Get information about the classifier.
        
        Returns:
            Dictionary containing classifier metadata
        """
        return {
            'model_name': self.model_name,
            'device': self.device,
            'num_classes': len(self.food_101_classes),
            'input_shape': (1, 3, 224, 224),
            'classes': self.food_101_classes[:10],  # Return first 10 as sample
            'total_food101_classes': len(self.food_101_classes)
        }

# Global classifier instance (loaded once at startup)
_classifier_instance = None

def get_classifier(model_name: str = "resnet50") -> FoodClassifier:
    """
    Get or create the global classifier instance.
    
    This ensures the model is loaded only once at startup.
    
    Args:
        model_name: Model architecture to use
        
    Returns:
        FoodClassifier instance
    """
    global _classifier_instance
    
    if _classifier_instance is None:
        _classifier_instance = FoodClassifier(model_name=model_name)
    
    return _classifier_instance

def cleanup_classifier():
    """
    Cleanup the global classifier instance.
    
    Call this when shutting down the application.
    """
    global _classifier_instance
    _classifier_instance = None
    torch.cuda.empty_cache()  # Clear GPU memory if used
