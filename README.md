# Ranjana Calligraphy Recognition API

A Django REST API backend for a mobile calligraphy learning application that recognizes and analyzes Ranjana script characters using deep learning. This API provides character recognition, handwriting similarity comparison, and visual feedback features to help users learn and practice Ranjana calligraphy.

## 🎯 Overview

This backend supports a mobile app that helps users learn Ranjana script (an ancient Nepali script) by:
- **Recognizing** handwritten characters using AI
- **Comparing** user's handwriting with reference samples
- **Providing visual feedback** through color-coded overlays

## 🚀 Features

### 1. Character Recognition
- **AI-powered recognition** of 62 Ranjana characters
- **99.5% accuracy** using EfficientNet-B0 architecture
- Input: 64x64 grayscale images
- Output: Character class (0-61) with confidence score

### 2. Handwriting Similarity Analysis
- **Compare user's handwriting** with reference samples
- **92.7% accuracy** using Siamese neural network
- Returns similarity percentage and visual comparison
- Color-coded overlay visualization:
  - 🔴 **Red**: Reference character strokes
  - 🟢 **Green**: User's strokes
  - 🟡 **Yellow**: Matching areas (overlap)

### 3. Deep Learning Models
- **Classification Model**: `efficientnet_b0_best.pth` (47 MB)
  - Identifies which character is written
- **Similarity Model**: `siamese_efficientnet_b0_best.pth` (25 MB)
  - Compares handwriting similarity using 128-dimensional embeddings

## 📋 Prerequisites

- Python 3.8+
- PostgreSQL database
- pip (Python package manager)

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd calligrapy
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Setup

Create a PostgreSQL database and update the `.env` file:

```bash
# Copy example environment file
copy example.env .env
```

Edit `.env` with your database credentials:
```env
DB_NAME=your_database_name
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

### 5. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Add Reference Images

Place reference character images in `api/reference_images/`:
- Filename format: `class_0.png`, `class_1.png`, ..., `class_61.png`
- Images should be 64x64 grayscale PNG files
- Total: 62 reference images (one per character class)

### 7. Run Development Server
```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/`

## 📡 API Endpoints

### Base URL
```
http://localhost:8000/api/
```

### 1. Character Recognition

**Endpoint:** `POST /api/predict/`

**Description:** Recognizes a Ranjana character from an uploaded image

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body:
  ```
  image: <image_file> (PNG/JPEG)
  ```

**Response:**
```json
{
  "success": true,
  "predicted_class": 23,
  "confidence": 98.5
}
```

**Example (cURL):**
```bash
curl -X POST http://localhost:8000/api/predict/ \
  -F "image=@character.png"
```

---

### 2. Handwriting Similarity Comparison

**Endpoint:** `POST /api/similarity/`

**Description:** Compares user's handwriting with a reference character

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body:
  ```
  image: <image_file> (PNG/JPEG)
  target_class: <integer> (0-61)
  ```

**Response:**
```json
{
  "success": true,
  "similarity_score": 87.32,
  "distance": 0.38,
  "is_same_character": true,
  "threshold": 0.45,
  "compared_with_class": 23,
  "comparison_image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUg..."
}
```

**Interpretation:**
- `similarity_score`: Percentage similarity (0-100%)
- `distance`: Euclidean distance between embeddings
- `is_same_character`: True if distance < 0.45 threshold
- `comparison_image`: Base64-encoded overlay visualization

**Example (cURL):**
```bash
curl -X POST http://localhost:8000/api/similarity/ \
  -F "image=@user_handwriting.png" \
  -F "target_class=23"
```

---

## 🏗️ Project Structure

```
calligrapy/
├── api/                          # Main API application
│   ├── ml_models/               # Machine learning models
│   │   ├── weights/             # Pre-trained model weights
│   │   │   ├── efficientnet_b0_best.pth
│   │   │   └── siamese_efficientnet_b0_best.pth
│   │   ├── config.py            # Model configurations
│   │   ├── data_loader.py       # Data preprocessing
│   │   ├── inference.py         # Prediction logic
│   │   ├── models.py            # Model architectures
│   │   └── siamese_network.py   # Siamese network implementation
│   ├── reference_images/        # Reference character samples
│   │   └── class_0.png ... class_61.png
│   ├── models.py                # Database models
│   ├── serializers.py           # API serializers
│   ├── views.py                 # API endpoints
│   └── urls.py                  # URL routing
├── calligrapy/                  # Django project settings
│   ├── settings.py              # Main settings
│   ├── urls.py                  # Root URL configuration
│   └── wsgi.py                  # WSGI configuration
├── media/                       # User uploaded images
├── manage.py                    # Django management script
├── requirements.txt             # Python dependencies
├── example.env                  # Environment variables template
└── README.md                    # This file
```

## 🧠 Machine Learning Models

### Classification Model (EfficientNet-B0)
- **Architecture**: EfficientNet-B0 with custom classifier
- **Input**: 64x64 grayscale image
- **Output**: 62 class probabilities + confidence score
- **Accuracy**: 99.5%
- **Use Case**: "What character is this?"

### Siamese Network
- **Architecture**: Twin EfficientNet-B0 encoders
- **Input**: Two 64x64 grayscale images
- **Output**: 128-dimensional embeddings + similarity score
- **Accuracy**: 92.7%
- **Use Cases**:
  - Character similarity comparison
  - Handwriting quality assessment
  - Learning progress tracking

## 📦 Dependencies

Key packages (see `requirements.txt` for complete list):

```
Django==5.2+              # Web framework
djangorestframework       # REST API toolkit
torch>=2.0.0             # PyTorch (deep learning)
torchvision>=0.15.0      # Vision models and transforms
opencv-python>=4.8.0     # Image processing
Pillow                   # Image manipulation
numpy>=1.24.0            # Numerical computing
psycopg                  # PostgreSQL adapter
```

## 🔧 Configuration

### Django Settings
Key settings in `calligrapy/settings.py`:

```python
# Media files (uploaded images)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',  # Current: Open access
    ],
}

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        # Credentials loaded from .env file
    }
}
```

## 📱 Mobile App Integration

### Request Format
All API requests should use `multipart/form-data` for image uploads:

```javascript
// Example: React Native / Flutter
const formData = new FormData();
formData.append('image', {
  uri: imageUri,
  type: 'image/png',
  name: 'character.png'
});

fetch('http://your-server.com/api/predict/', {
  method: 'POST',
  body: formData,
  headers: {
    'Content-Type': 'multipart/form-data',
  },
})
.then(response => response.json())
.then(data => console.log(data));
```

### Image Preprocessing
For best results, mobile apps should:
1. Convert images to **grayscale**
2. Resize to **64x64 pixels**
3. Ensure **white background, black strokes** (or will be auto-inverted)
4. Use **PNG or JPEG** format

## 🚦 Error Handling

API returns consistent error responses:

```json
{
  "success": false,
  "error": "Error description here"
}
```

Common HTTP status codes:
- `200 OK`: Successful request
- `400 Bad Request`: Invalid input (missing image, invalid format)
- `404 Not Found`: Reference image not found for target class
- `500 Internal Server Error`: Model or processing error

## 🔐 Security Notes

**Current Status**: API is configured with `AllowAny` permissions for development.

**For Production**:
1. Enable JWT authentication (already configured but commented out)
2. Add CORS middleware for mobile app origins
3. Use HTTPS for all API calls
4. Set `DEBUG = False` in settings
5. Configure `ALLOWED_HOSTS`
6. Use environment variables for secrets

## 🧪 Testing

Test the API using cURL, Postman, or Python:

```python
import requests

# Test character recognition
with open('test_character.png', 'rb') as img:
    response = requests.post(
        'http://localhost:8000/api/predict/',
        files={'image': img}
    )
    print(response.json())

# Test similarity comparison
with open('user_handwriting.png', 'rb') as img:
    response = requests.post(
        'http://localhost:8000/api/similarity/',
        files={'image': img},
        data={'target_class': 23}
    )
    print(response.json())
```

## 📊 Database Models

### PredictionHistory (Currently Disabled)
Stores user's character recognition history:
- User reference
- Uploaded image
- Predicted class
- Confidence score
- Timestamp

### SimilarityHistory (Currently Disabled)
Stores handwriting comparison history:
- User reference
- User's image
- Target class
- Similarity score
- Distance metric
- Comparison overlay image
- Timestamp

*Note: History features are commented out but can be enabled by uncommenting relevant code in `views.py` and enabling authentication.*

## 🎨 Visual Feedback System

The similarity endpoint provides a color-coded overlay image that helps users understand their writing:

- **Red pixels**: Reference character strokes only (areas to add)
- **Green pixels**: User's strokes only (possible errors or variations)
- **Yellow pixels**: Matching areas (correct strokes)
- **Black pixels**: Background (no strokes)

This visual feedback is encoded as base64 and can be displayed directly in mobile apps.


## 👥 Authors

Lokesh Shrestha 

## 🙏 Acknowledgments

- Ranjana script dataset and reference images
- EfficientNet architecture by Google
- PyTorch and Django communities

---

## 🆘 Troubleshooting

### Common Issues

**1. "Reference image not found" error**
- Ensure reference images are in `api/reference_images/`
- Check filename format: `class_0.png` through `class_61.png`

**2. Database connection errors**
- Verify PostgreSQL is running
- Check `.env` file credentials
- Run migrations: `python manage.py migrate`

**3. Model loading errors**
- Ensure model weights exist in `api/ml_models/weights/`
- Check file sizes: efficientnet (47MB), siamese (25MB)
- Verify PyTorch is installed correctly

**4. Image processing errors**
- Check image format (PNG/JPEG)
- Ensure image is not corrupted
- Try reducing image size before upload

---

**Last Updated**: October 2025
**API Version**: 1.0
