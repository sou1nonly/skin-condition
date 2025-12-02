# SkinAI - Skin Condition Analyzer

An AI-powered web application that analyzes skin conditions using deep learning (MobileNetV2).

## Features

- 🔍 **Skin Analysis**: Detects 6 different skin conditions:
  - Acne
  - Dry Skin
  - Pigmentation
  - Wrinkles
  - Dark Circles
  - Normal/Healthy Skin

- 📸 **Multiple Input Options**: 
  - Upload images from your device
  - Take photos using your webcam
  - Drag and drop support

- 💡 **Personalized Recommendations**: Get skincare tips and ingredient suggestions based on your analysis

- 📊 **Detailed Reports**: View confidence scores for all detected conditions and download reports

## Project Structure

```
skin condition/
├── app.py                    # Flask application
├── requirements.txt          # Python dependencies
├── model/
│   └── mobilenet_final.h5    # Trained MobileNetV2 model
├── services/
│   └── skin_condition.py     # ML model service
├── controller/
│   └── controller.py         # Business logic controller
├── templates/
│   └── index.html            # Main frontend page
├── static/
│   ├── css/
│   │   └── style.css         # Styling
│   └── js/
│       └── app.js            # Frontend JavaScript
└── skin-analysis-new.ipynb   # Model training notebook
```

## Installation

1. **Clone or navigate to the project directory**

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Ensure the model file exists**:
   - The trained model should be at `model/mobilenet_final.h5`
   - If not present, run the training notebook to create it

## Running the Application

1. **Start the Flask server**:
   ```bash
   python app.py
   ```

2. **Open your browser** and navigate to:
   ```
   http://localhost:5000
   ```

3. **Upload an image** of skin and click "Analyze Skin" to get results

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main frontend page |
| `/api/analyze` | POST | Analyze skin image (accepts multipart form or JSON with base64) |
| `/api/health` | GET | Health check endpoint |
| `/api/conditions` | GET | List of detectable conditions |

### Example API Usage

```python
import requests

# Upload image file
with open('skin_image.jpg', 'rb') as f:
    response = requests.post(
        'http://localhost:5000/api/analyze',
        files={'image': f}
    )
    print(response.json())
```

## Model Details

- **Architecture**: MobileNetV2 (transfer learning)
- **Input Size**: 224x224 RGB images
- **Output**: 6 skin condition classes
- **Preprocessing**: MobileNet standard normalization ([-1, 1] range)

## Technologies Used

- **Backend**: Flask, TensorFlow/Keras
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **ML Model**: MobileNetV2
- **Image Processing**: OpenCV, Pillow

## Disclaimer

⚠️ **This tool is for educational purposes only.** The analysis provided should not be considered medical advice. Always consult a dermatologist or healthcare professional for proper diagnosis and treatment of skin conditions.

## License

This project is for educational and personal use.
