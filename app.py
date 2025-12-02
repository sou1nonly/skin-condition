"""
Flask Application for Skin Condition Analysis
"""
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import numpy as np
import cv2
import base64
import os
import logging
from services.skin_condition import get_skin_condition_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Initialize the skin condition service
skin_service = get_skin_condition_service()

@app.route('/')
def index():
    """Serve the main frontend page"""
    return render_template('index.html')

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "model_loaded": skin_service._model is not None
    })

@app.route('/api/analyze', methods=['POST'])
def analyze_skin():
    """
    Analyze skin condition from uploaded image
    
    Accepts:
    - Multipart form data with 'image' file
    - JSON with base64 encoded 'image' data
    """
    try:
        # Get image from request
        if 'image' in request.files:
            # Handle file upload
            file = request.files['image']
            if file.filename == '':
                return jsonify({"error": "No file selected"}), 400
            
            # Read image file
            file_bytes = np.frombuffer(file.read(), np.uint8)
            bgr_image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
            
        elif request.is_json and 'image' in request.json:
            # Handle base64 encoded image
            image_data = request.json['image']
            # Remove data URL prefix if present
            if ',' in image_data:
                image_data = image_data.split(',')[1]
            
            # Decode base64
            image_bytes = base64.b64decode(image_data)
            file_bytes = np.frombuffer(image_bytes, np.uint8)
            bgr_image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        else:
            return jsonify({"error": "No image provided"}), 400
        
        if bgr_image is None:
            return jsonify({"error": "Invalid image format"}), 400
        
        # Convert BGR to RGB for the model
        rgb_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB)
        
        # Get predictions
        probabilities = skin_service.predict_classes(rgb_image)
        results = skin_service.get_predictions_dict(probabilities)
        
        # Format response
        response = {
            "success": True,
            "top_condition": results["top_condition"].strip(),
            "confidence": round(results["confidence"], 2),
            "all_conditions": {k.strip(): round(v, 2) for k, v in results["all_conditions"].items()},
            "recommendations": get_recommendations(results["top_condition"].strip())
        }
        
        return jsonify(response)
        
    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        return jsonify({"error": "An error occurred during analysis"}), 500

def get_recommendations(condition: str) -> dict:
    """Get skincare recommendations based on detected condition"""
    recommendations = {
        "acne": {
            "description": "Acne is caused by clogged pores from oil, dead skin cells, and bacteria.",
            "tips": [
                "Use a gentle, non-comedogenic cleanser twice daily",
                "Apply benzoyl peroxide or salicylic acid treatments",
                "Avoid touching your face frequently",
                "Use oil-free moisturizers and sunscreen",
                "Consider consulting a dermatologist for persistent acne"
            ],
            "ingredients_to_look_for": ["Salicylic Acid", "Benzoyl Peroxide", "Niacinamide", "Tea Tree Oil"],
            "ingredients_to_avoid": ["Heavy oils", "Comedogenic ingredients", "Alcohol-based products"]
        },
        "dry": {
            "description": "Dry skin lacks moisture and natural oils, leading to flakiness and tightness.",
            "tips": [
                "Use a gentle, hydrating cleanser",
                "Apply a rich moisturizer immediately after washing",
                "Use a humidifier in dry environments",
                "Avoid hot showers and harsh soaps",
                "Drink plenty of water to stay hydrated"
            ],
            "ingredients_to_look_for": ["Hyaluronic Acid", "Ceramides", "Glycerin", "Shea Butter"],
            "ingredients_to_avoid": ["Alcohol", "Fragrances", "Harsh sulfates"]
        },
        "pigmentation": {
            "description": "Hyperpigmentation is darkening of skin areas due to excess melanin production.",
            "tips": [
                "Use broad-spectrum SPF 30+ sunscreen daily",
                "Apply vitamin C serum in the morning",
                "Use products with niacinamide or arbutin",
                "Consider chemical exfoliants like AHAs",
                "Be patient - results take 6-8 weeks minimum"
            ],
            "ingredients_to_look_for": ["Vitamin C", "Niacinamide", "Alpha Arbutin", "Kojic Acid"],
            "ingredients_to_avoid": ["Harsh physical scrubs", "Irritating ingredients"]
        },
        "wrinkle": {
            "description": "Wrinkles are creases in the skin caused by aging, sun damage, and loss of collagen.",
            "tips": [
                "Use retinol or retinoid products at night",
                "Apply SPF 30+ sunscreen every day",
                "Keep skin well-hydrated with hyaluronic acid",
                "Consider peptide-rich products",
                "Get adequate sleep and manage stress"
            ],
            "ingredients_to_look_for": ["Retinol", "Peptides", "Hyaluronic Acid", "Vitamin C"],
            "ingredients_to_avoid": ["Excessive sun exposure", "Smoking", "Harsh products"]
        },
        "dark circles": {
            "description": "Dark circles under the eyes can be caused by fatigue, genetics, or aging.",
            "tips": [
                "Get 7-9 hours of quality sleep",
                "Use eye creams with caffeine or vitamin K",
                "Apply cold compresses to reduce puffiness",
                "Stay hydrated and limit salt intake",
                "Use concealer with peach or orange undertones"
            ],
            "ingredients_to_look_for": ["Caffeine", "Vitamin K", "Retinol", "Peptides"],
            "ingredients_to_avoid": ["Rubbing eyes", "Allergens", "Excessive screen time before bed"]
        },
        "normal": {
            "description": "Your skin appears healthy and balanced. Keep up the good work!",
            "tips": [
                "Maintain your current skincare routine",
                "Continue using sunscreen daily",
                "Stay hydrated and eat a balanced diet",
                "Get regular exercise and adequate sleep",
                "Consider preventive anti-aging products"
            ],
            "ingredients_to_look_for": ["Antioxidants", "SPF", "Gentle cleansers", "Light moisturizers"],
            "ingredients_to_avoid": ["Over-exfoliation", "Unnecessary harsh treatments"]
        }
    }
    
    return recommendations.get(condition.lower(), recommendations["normal"])

@app.route('/api/conditions', methods=['GET'])
def get_conditions():
    """Get list of detectable skin conditions"""
    conditions = [
        {"id": "acne", "name": "Acne", "description": "Inflammatory skin condition with pimples and blemishes"},
        {"id": "dry", "name": "Dry Skin", "description": "Skin that lacks moisture and natural oils"},
        {"id": "pigmentation", "name": "Pigmentation", "description": "Dark spots or uneven skin tone"},
        {"id": "wrinkle", "name": "Wrinkles", "description": "Lines and creases in the skin"},
        {"id": "dark_circles", "name": "Dark Circles", "description": "Darkening under the eyes"},
        {"id": "normal", "name": "Normal/Healthy", "description": "Balanced, healthy-looking skin"}
    ]
    return jsonify({"conditions": conditions})

if __name__ == '__main__':
    # Pre-load the model
    logger.info("Pre-loading skin condition model...")
    try:
        skin_service.load_model()
        logger.info("Model loaded successfully!")
    except Exception as e:
        logger.error(f"Failed to pre-load model: {e}")
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)
