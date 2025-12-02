import numpy as np
import tensorflow as tf
import logging
from typing import Dict, Any
import os
import cv2

logger = logging.getLogger(__name__)

def detect_skin_in_image(bgr_image):
    """
    Simple skin detection function using HSV color space.
    Returns True if skin is detected, False otherwise.
    """
    # Convert BGR to HSV
    hsv = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2HSV)
    
    # Define skin color range in HSV
    # These ranges work for most skin tones
    lower_skin1 = np.array([0, 20, 70], dtype=np.uint8)
    upper_skin1 = np.array([20, 255, 255], dtype=np.uint8)
    
    lower_skin2 = np.array([170, 20, 70], dtype=np.uint8)
    upper_skin2 = np.array([180, 255, 255], dtype=np.uint8)
    
    # Create masks for skin detection
    mask1 = cv2.inRange(hsv, lower_skin1, upper_skin1)
    mask2 = cv2.inRange(hsv, lower_skin2, upper_skin2)
    mask = cv2.bitwise_or(mask1, mask2)
    
    # Check if skin pixels are present (at least 1% of image)
    skin_pixels = cv2.countNonZero(mask)
    total_pixels = bgr_image.shape[0] * bgr_image.shape[1]
    skin_ratio = skin_pixels / total_pixels
    
    return skin_ratio > 0.01  # At least 1% skin detected

class SkinConditionService:
    """Service for skin condition analysis using custom ML model"""
    
    def __init__(self):
        self._model = None
        # Use absolute path relative to the current file's directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        self.model_path = os.path.join(project_root, "model", "mobilenet_final.h5")
        
        # Label mapping for skin conditions - EXACT mapping from training
        self.index_to_label = {
            0: 'dry ',
            1: 'acne',
            2: 'pigmentation',
            3: 'wrinkle',
            4: 'dark circles',
            5: 'normal'
        }
    
    def load_model(self):
        """Load the TensorFlow model for skin condition analysis."""
        if self._model is None:
            try:
                self._model = tf.keras.models.load_model(self.model_path)
                logger.info("Skin condition model loaded successfully from mobilenet_final.h5")
            except Exception as e:
                logger.error(f"Failed to load skin condition model: {str(e)}")
                raise ValueError(f"Model loading failed: {str(e)}")
        return self._model
    
    def preprocess_for_model(self, rgb_image: np.ndarray) -> tf.Tensor:
        """Apply MobileNet standard preprocessing"""
        # Convert numpy array to tensor
        img = tf.convert_to_tensor(rgb_image, dtype=tf.float32)
        
        # Resize to model input size (224x224)
        img = tf.image.resize(img, [224, 224])
        
        # MobileNet standard preprocessing: normalize to [-1, 1] range
        img = tf.cast(img, tf.float32)
        img = (img / 127.5) - 1.0  # Scale to [-1, 1] instead of [0, 1]
        
        # Add batch dimension
        img = tf.expand_dims(img, axis=0)
        
        return img
    
    def predict_classes(self, rgb_image: np.ndarray) -> np.ndarray:
        """Get prediction probabilities from the model using RGB image array"""
        # Convert RGB back to BGR for skin detection (OpenCV format)
        bgr_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR)
        
        # Check if skin is present in the image
        if not detect_skin_in_image(bgr_image):
            raise ValueError("No skin detected in the image")
        
        model = self.load_model()
        
        # Apply model-specific preprocessing
        preprocessed_img = self.preprocess_for_model(rgb_image)
        
        # Get predictions
        preds = model.predict(preprocessed_img)
        
        # Return probabilities (assuming model outputs probabilities, not logits)
        return preds[0]
    
    def get_predictions_dict(self, probabilities: np.ndarray) -> Dict[str, Any]:
        """Convert model probabilities to formatted predictions dictionary"""
        # Create sorted predictions with probabilities as percentages
        sorted_preds = sorted(
            [(self.index_to_label[i], float(probabilities[i]) * 100) for i in range(len(probabilities))],
            key=lambda x: x[1],
            reverse=True
        )
        
        predictions_list = [f"{label}: {prob:.2f}%" for label, prob in sorted_preds]
        top_prediction = sorted_preds[0]
        all_predictions = {label: prob for label, prob in sorted_preds}
        
        return {
            "top_condition": top_prediction[0],
            "confidence": top_prediction[1],  # Percentage value
            "all_conditions": all_predictions,
            "condition_list": predictions_list,
            "sorted_predictions": sorted_preds
        }

# Global service instance - using lazy loading to avoid circular imports
_skin_condition_service = None

def get_skin_condition_service() -> SkinConditionService:
    """Get the skin condition service instance with lazy loading"""
    global _skin_condition_service
    if _skin_condition_service is None:
        _skin_condition_service = SkinConditionService()
    return _skin_condition_service

# For backward compatibility
skin_condition_service = get_skin_condition_service()
