"""
Controller for Skin Condition Analysis
Provides a clean interface for the skin analysis service
"""
from services.skin_condition import get_skin_condition_service, SkinConditionService
import numpy as np
import cv2
from typing import Dict, Any, Optional

class SkinController:
    """Controller class for skin condition analysis operations"""
    
    def __init__(self):
        self._service: Optional[SkinConditionService] = None
    
    @property
    def service(self) -> SkinConditionService:
        """Lazy load the skin condition service"""
        if self._service is None:
            self._service = get_skin_condition_service()
        return self._service
    
    def analyze_image_from_file(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze a skin image from a file path
        
        Args:
            file_path: Path to the image file
            
        Returns:
            Dictionary containing analysis results
        """
        # Read image
        bgr_image = cv2.imread(file_path)
        if bgr_image is None:
            raise ValueError(f"Could not read image from: {file_path}")
        
        return self.analyze_image_from_array(bgr_image)
    
    def analyze_image_from_array(self, bgr_image: np.ndarray) -> Dict[str, Any]:
        """
        Analyze a skin image from a BGR numpy array (OpenCV format)
        
        Args:
            bgr_image: Image in BGR format (as read by OpenCV)
            
        Returns:
            Dictionary containing analysis results
        """
        # Convert BGR to RGB for the model
        rgb_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB)
        
        # Get predictions from service
        probabilities = self.service.predict_classes(rgb_image)
        results = self.service.get_predictions_dict(probabilities)
        
        return {
            "success": True,
            "top_condition": results["top_condition"].strip(),
            "confidence": round(results["confidence"], 2),
            "all_conditions": {k.strip(): round(v, 2) for k, v in results["all_conditions"].items()},
            "predictions_list": results["condition_list"]
        }
    
    def analyze_image_from_bytes(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Analyze a skin image from raw bytes
        
        Args:
            image_bytes: Raw image bytes
            
        Returns:
            Dictionary containing analysis results
        """
        # Decode image from bytes
        nparr = np.frombuffer(image_bytes, np.uint8)
        bgr_image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if bgr_image is None:
            raise ValueError("Could not decode image from bytes")
        
        return self.analyze_image_from_array(bgr_image)
    
    def get_supported_conditions(self) -> list:
        """Get list of conditions the model can detect"""
        return list(self.service.index_to_label.values())
    
    def is_model_loaded(self) -> bool:
        """Check if the ML model is loaded"""
        return self.service._model is not None
    
    def preload_model(self) -> bool:
        """
        Preload the ML model
        
        Returns:
            True if model loaded successfully, False otherwise
        """
        try:
            self.service.load_model()
            return True
        except Exception:
            return False


# Singleton instance
_controller_instance: Optional[SkinController] = None

def get_controller() -> SkinController:
    """Get the singleton controller instance"""
    global _controller_instance
    if _controller_instance is None:
        _controller_instance = SkinController()
    return _controller_instance
