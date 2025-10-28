# Ranjana Calligraphy Recognition API

A Django REST API backend for a mobile calligraphy learning application that recognizes and analyzes Ranjana script characters using deep learning. This API provides character recognition, handwriting similarity comparison, user authentication, and learning progress tracking to help users master Ranjana calligraphy.

## 📋 Quick Reference

| Feature | Endpoint | Model | Accuracy |
|---------|----------|-------|----------|
| **Character Recognition** | `POST /api/predict/` | EfficientNet-B0 Augmented (47MB) | 99.5% |
| **Similarity Comparison** | `POST /api/similarity/` | Siamese Network (25MB) | 92.7% |
| **User Signup** | `POST /api/signup/` | - | - |
| **User Signin** | `POST /api/signin/` | JWT Auth | - |
| **Change Password** | `POST /api/change-password/` | JWT Auth | - |
| **Change Username** | `POST /api/change-username/` | JWT Auth | - |

**Authentication:** JWT Bearer Token required for password/username change endpoints only. ML endpoints are currently open for development (no authentication required)

**Note:** Model trained on **36 classes (0-35)** using augmented dataset

## 🎯 Overview

This backend supports a mobile app that helps users learn Ranjana script (an ancient Nepali script) by:
- **Recognizing** handwritten characters using AI (99.5% accuracy, 36 classes)
- **Comparing** user's handwriting with reference samples (92.7% accuracy)
- **Providing visual feedback** through three-panel comparison images (reference, user input, and blended overlay)
- **Authentication & User Management** with JWT-based security
- **Automatic image preprocessing** for optimal recognition results

## ✨ Key Capabilities

### API View Functions

1. **PredictView** (Recognition) → *"I see character 12"*
   - Identifies which Ranjana character is written (36 classes: 0-35)
   - Uses EfficientNet-B0 Augmented classification model
   - Returns class ID, confidence score, and preprocessed image
   - Includes automatic image preprocessing (thresholding, cropping, centering, resizing)

2. **SimilarityView** (Comparison) → *"Your writing is 87% like the reference"*
   - Compares user's handwriting with reference character
   - Uses Siamese neural network for similarity scoring
   - Returns three separate images: reference, user input, and blended overlay
   - Generates visual comparison with color-coded differences

3. **Authentication Views**
   - SignupView, SigninView (JWT-based)
   - ChangePasswordView, ChangeUsernameView (requires authentication)

## 🚀 Features

### 1. User Authentication & Management
- **JWT-based authentication** for secure API access
- **User signup/signin** with token-based sessions
- **Password management** with secure password change (requires authentication)
- **Username updates** for user customization (requires authentication)
- **Flexible security**: ML endpoints open for development, auth endpoints protected

### 2. Character Recognition (PredictView)
- **AI-powered recognition** of 36 Ranjana characters (classes 0-35)
- **99.5% accuracy** using EfficientNet-B0 Augmented architecture
- Input: Images in PNG/JPEG format (automatically preprocessed)
- Output: Character class (0-35) with confidence score and preprocessed image
- **Automatic preprocessing pipeline**:
  - Grayscale conversion
  - Otsu's thresholding
  - Contour detection and filtering
  - Smart cropping (removes noise while keeping relevant strokes)
  - Centering in square canvas
  - Resizing to 64x64 pixels
- **No authentication required** (development mode)

### 3. Handwriting Similarity Analysis (SimilarityView)
- **Compare user's handwriting** with reference samples
- **92.7% accuracy** using Siamese neural network
- Returns similarity percentage, distance, and three visual images
- **Three-panel visual output**:
  - **Reference Image**: Original reference character (grayscale, 256x256)
  - **User Image**: User's handwriting with inverted colors (grayscale, 256x256)
  - **Blended Overlay**: Composite comparison showing:
    - Reference strokes at full opacity
    - User strokes at 50% opacity (semi-transparent)
    - Overlapping areas show where handwriting matches
- **Distance threshold**: < 0.45 indicates same character
- **No authentication required** (development mode)

### 4. Automatic Image Preprocessing
- **Smart preprocessing pipeline** for optimal recognition
- **Grayscale conversion** and thresholding
- **Contour-based cropping** removes noise while preserving character strokes
- **Selective contour merging** keeps nearby strokes together
- **Automatic centering** in square canvas
- **Standardized output**: All images resized to 64x64 pixels
- **Fallback mechanism**: Uses original image if preprocessing fails

### 5. Deep Learning Models
- **Classification Model**: `efficientnet_b0_augmented_best.pth` (47 MB)
  - Identifies which character is written (36 classes: 0-35)
  - Uses EfficientNet-B0 architecture with augmented training data
- **Similarity Model**: `siamese_efficientnet_b0_best.pth` (25 MB)
  - Compares handwriting similarity using 128-dimensional embeddings
  - Twin encoder architecture for robust comparison

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
- Filename format: `class_0.png`, `class_1.png`, ..., `class_35.png`
- Images should be 64x64 grayscale PNG files
- Total: 36 reference images (one per character class)

**Note:** Model supports classes 0-35 only (36 classes total)

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

### Authentication Endpoints

#### 1. User Signup

**Endpoint:** `POST /api/signup/`

**Description:** Create a new user account

**Request:**
- Method: `POST`
- Content-Type: `application/json`
- Body:
  ```json
  {
    "username": "your_username",
    "email": "your_email@example.com",
    "password": "your_password",
    "password2": "your_password"
  }
  ```

**Response:**
```json
{
  "message": "User created successfully."
}
```

---

#### 2. User Signin

**Endpoint:** `POST /api/signin/`

**Description:** Authenticate user and receive JWT tokens

**Request:**
- Method: `POST`
- Content-Type: `application/json`
- Body:
  ```json
  {
    "username": "your_username",
    "password": "your_password"
  }
  ```

**Response:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Note:** Use the `access` token in subsequent requests as: `Authorization: Bearer <access_token>`

---

#### 3. Change Password

**Endpoint:** `POST /api/change-password/`

**Description:** Update user's password

**Authentication:** Required (Bearer Token)

**Request:**
- Method: `POST`
- Content-Type: `application/json`
- Headers: `Authorization: Bearer <access_token>`
- Body:
  ```json
  {
    "old_password": "current_password",
    "new_password": "new_password"
  }
  ```

**Response:**
```json
{
  "message": "Password updated successfully."
}
```

---

#### 4. Change Username

**Endpoint:** `POST /api/change-username/`

**Description:** Update user's username

**Authentication:** Required (Bearer Token)

**Request:**
- Method: `POST`
- Content-Type: `application/json`
- Headers: `Authorization: Bearer <access_token>`
- Body:
  ```json
  {
    "new_username": "new_username"
  }
  ```

**Response:**
```json
{
  "message": "Username updated successfully."
}
```

---

### Machine Learning Endpoints

#### 5. Character Recognition (Predict)

**Endpoint:** `POST /api/predict/`

**Description:** Recognizes a Ranjana character from an uploaded image using EfficientNet-B0 classification model

**Authentication:** Not required (development mode)

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body:
  ```
  image: <image_file> (PNG/JPEG, any size - will be auto-preprocessed)
  ```

**Process Flow:**
1. User uploads image (any size, any format)
2. Image validated via ImageSerializer
3. Saved to temporary file
4. **Automatic preprocessing**:
   - Convert to grayscale
   - Apply Otsu's thresholding
   - Detect and filter contours
   - Merge nearby contours (remove noise)
   - Crop to bounding box
   - Center in square canvas
   - Resize to 64x64
5. EfficientNet-B0 model loaded
6. Prediction executed on preprocessed image
7. Returns class ID, confidence, and preprocessed image (base64)
8. Temporary file deleted

**Response:**
```json
{
  "success": true,
  "predicted_class": 12,
  "confidence": 98.5,
  "processed_image": "data:image/png;base64,iVBORw0KGgo..."
}
```

**Note:** 
- Model supports classes 0-35 only (36 total classes)
- Preprocessing is automatic - no need to manually resize or convert images
- Returns the preprocessed image for verification

**Use Case:** *"What character is this?"*

**Example (cURL):**
```bash
curl -X POST http://localhost:8000/api/predict/ \
  -F "image=@character.png"
```

---

#### 6. Handwriting Similarity Comparison

**Endpoint:** `POST /api/similarity/`

**Description:** Compares user's handwriting with a reference character using Siamese neural network

**Authentication:** Not required (development mode)

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body:
  ```
  image: <image_file> (PNG/JPEG, any size)
  target_class: <integer> (0-35)
  ```

**Note:** `target_class` must be between 0-35 (36 classes total)

**Process Flow:**
1. User uploads image and specifies target class (0-35)
2. Image validated via SimilaritySerializer
3. Reference image loaded from database (api/reference_images/class_X.png)
4. Both images saved to temporary files
5. Siamese neural network loaded
6. Extract 128-dimensional embeddings for each image
7. Calculate Euclidean distance between embeddings
8. Convert distance to similarity percentage
9. Check if same character (distance < 0.45 threshold)
10. Generate three comparison images:
    - Reference image (grayscale, 256x256)
    - User image with inverted colors (grayscale, 256x256)
    - Blended overlay (reference at full opacity + user at 50% opacity)
11. Return results with all three images as base64
12. Delete temporary files

**Response:**
```json
{
  "success": true,
  "similarity_score": 87.32,
  "distance": 0.38,
  "is_same_character": true,
  "threshold": 0.45,
  "compared_with_class": 12,
  "reference_image": "data:image/png;base64,iVBORw0KGgo...",
  "user_image": "data:image/png;base64,iVBORw0KGgo...",
  "blended_overlay": "data:image/png;base64,iVBORw0KGgo..."
}
```

**Interpretation:**
- `similarity_score`: Percentage similarity (0-100%)
- `distance`: Euclidean distance between embeddings (lower = more similar)
- `is_same_character`: True if distance < 0.45 threshold
- `reference_image`: Base64-encoded reference character (grayscale, 256x256)
- `user_image`: Base64-encoded user's handwriting with inverted colors (grayscale, 256x256)
- `blended_overlay`: Base64-encoded composite image showing:
  - Reference strokes at full opacity
  - User strokes at 50% opacity (semi-transparent)
  - Overlapping areas show where handwriting matches

**Use Case:** *"How similar is the student's handwriting to the reference?"*

**Example (cURL):**
```bash
curl -X POST http://localhost:8000/api/similarity/ \
  -F "image=@user_handwriting.png" \
  -F "target_class=12"
```

**Note:** `target_class` must be 0-35 (model trained on 36 classes)

---

## 🏗️ Project Structure

```
calligrapy/
├── api/                          # Main API application
│   ├── ml_models/               # Machine learning models
│   │   ├── weights/             # Pre-trained model weights
│   │   │   ├── efficientnet_b0_augmented_best.pth (36 classes)
│   │   │   └── siamese_efficientnet_b0_best.pth
│   │   ├── config.py            # Model configurations (NUM_CLASSES=36)
│   │   ├── data_loader.py       # Data preprocessing
│   │   ├── inference.py         # Prediction logic
│   │   ├── models.py            # Model architectures
│   │   └── siamese_network.py   # Siamese network implementation
│   ├── reference_images/        # Reference character samples (36 images)
│   │   └── class_0.png ... class_35.png
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

### 1. Classification Model (efficientnet_b0_augmented_best.pth - 47 MB)

**Purpose:** Character Recognition

**What it does:** Identifies which of the 36 Ranjana characters the input image represents

**Architecture:** EfficientNet-B0 with custom classifier, trained on augmented dataset

**Specifications:**
- **Input**: Single 64x64 grayscale image
- **Output**: Class prediction (0-35) with confidence scores
- **Accuracy**: 99.5%
- **Classes**: 36 (range 0-35)

**Use Case:** *"What character is this?"*

**Model View:** `PredictView` → Recognition → "I see character 12"

---

### 2. Siamese Network (siamese_efficientnet_b0_best.pth - 25 MB)

**Purpose:** Similarity/Comparison Model

**What it does:**
- Compares two images to see how similar they are
- Extracts 128-dimensional feature embeddings
- Determines if two characters are the same or different

**Architecture:** Twin EfficientNet-B0 encoders with embedding comparison

**Specifications:**
- **Input**: Two 64x64 grayscale images
- **Output**: 
  - Similarity score (0-100%)
  - Euclidean distance between embeddings
  - 128-dimensional feature vectors
- **Accuracy**: 92.7%
- **Threshold**: Distance < 0.45 indicates same character

**Use Cases:**
- "Are these two characters the same?"
- "How similar is the student's handwriting to the reference?"
- "Find similar characters in a database"
- Character similarity comparison
- Handwriting quality assessment
- Learning progress tracking

**Model View:** `SimilarityView` → Comparison → "Your writing is 87% like the reference"

## 📦 Dependencies

Key packages (see `requirements.txt` for complete list):

```
Django==5.2+                      # Web framework
djangorestframework               # REST API toolkit
djangorestframework-simplejwt     # JWT authentication
torch>=2.0.0                      # PyTorch (deep learning)
torchvision>=0.15.0               # Vision models and transforms
opencv-python>=4.8.0              # Image processing
Pillow                            # Image manipulation
numpy>=1.24.0                     # Numerical computing
psycopg                           # PostgreSQL adapter
python-decouple                   # Environment variable management
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
        'rest_framework.permissions.IsAuthenticated',  # Secure by default
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}

# JWT Settings
from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
}

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        # Credentials loaded from .env file
    }
}
```

### URL Configuration

The API has the following endpoint structure:

```python
# api/urls.py
urlpatterns = [
    # Authentication (AllowAny)
    path('signup/', SignupView.as_view()),
    path('signin/', SigninView.as_view()),
    
    # User Management (IsAuthenticated)
    path('change-password/', ChangePasswordView.as_view()),
    path('change-username/', ChangeUsernameView.as_view()),
    
    # Machine Learning (AllowAny - development mode)
    path('predict/', PredictView.as_view()),
    path('similarity/', SimilarityView.as_view()),
    
    # History endpoints (currently commented out)
    # path('history/predictions/', PredictionHistoryView.as_view()),
    # path('history/similarities/', SimilarityHistoryView.as_view()),
]
```

**Note:** History endpoints are available in the code but currently disabled

## 📱 Mobile App Integration

### Request Format
ML API requests (predict, similarity) currently do not require authentication (development mode).
Auth endpoints (change password, change username) require JWT authentication:

```javascript
// Example: React Native / Flutter

// For character recognition (NO AUTH REQUIRED)
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
.then(data => {
  console.log(`Predicted class: ${data.predicted_class}`);
  console.log(`Confidence: ${data.confidence}%`);
  // Display processed_image (base64 encoded)
});

// For similarity comparison (NO AUTH REQUIRED)
formData.append('target_class', '23');
fetch('http://your-server.com/api/similarity/', {
  method: 'POST',
  body: formData,
  headers: {
    'Content-Type': 'multipart/form-data',
  },
})
.then(response => response.json())
.then(data => {
  console.log(`Similarity: ${data.similarity_score}%`);
  // Display three images:
  // - data.reference_image (reference character)
  // - data.user_image (user's handwriting, inverted)
  // - data.blended_overlay (comparison overlay)
});
```

### Authentication Flow

```javascript
// 1. User signup
const signupData = {
  username: 'user123',
  email: 'user@example.com',
  password: 'securepass',
  password2: 'securepass'
};

fetch('http://your-server.com/api/signup/', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify(signupData)
});

// 2. User signin to get tokens
const signinData = {
  username: 'user123',
  password: 'securepass'
};

fetch('http://your-server.com/api/signin/', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify(signinData)
})
.then(response => response.json())
.then(data => {
  const accessToken = data.access;
  const refreshToken = data.refresh;
  // Store tokens securely
  AsyncStorage.setItem('access_token', accessToken);
  AsyncStorage.setItem('refresh_token', refreshToken);
});

// 3. Use access token for authenticated requests
const accessToken = await AsyncStorage.getItem('access_token');
// Include in headers as shown above
```

### Image Preprocessing
Mobile apps can send images in any format - the backend handles preprocessing automatically:
1. **Automatic grayscale conversion**
2. **Automatic thresholding** (Otsu's method)
3. **Smart cropping** (removes noise, keeps character strokes)
4. **Auto-resizing** to 64x64 pixels
5. **Centering** in square canvas

For best results, provide:
- **Clear images** with good contrast
- **White or light background** (will be auto-inverted if needed)
- **Dark/black strokes** for the character
- **PNG or JPEG** format
- Any size (will be auto-processed)

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

**Current Status**: 
- API uses JWT (JSON Web Token) authentication for user management endpoints
- ML endpoints (predict, similarity) are **currently open** (AllowAny) for development/testing
- Auth management endpoints (change password, change username) require authentication (IsAuthenticated)
- Signup/signin endpoints are public (AllowAny)

**Authentication Flow:**
1. User signs up via `/api/signup/`
2. User signs in via `/api/signin/` to receive JWT tokens
3. Access token used for password/username change API calls
4. Token included in header: `Authorization: Bearer <access_token>`
5. **ML endpoints do not require authentication** (development mode)

**For Production**:
1. ✅ JWT authentication enabled (already implemented)
2. **TODO**: Enable authentication for ML endpoints by changing permission_classes in views.py:
   ```python
   # Change from:
   permission_classes = [AllowAny]
   # To:
   permission_classes = [IsAuthenticated]
   ```
3. Add CORS middleware for mobile app origins
4. Use HTTPS for all API calls
5. Set `DEBUG = False` in settings
6. Configure `ALLOWED_HOSTS` properly
7. Use environment variables for all secrets
8. Enable rate limiting for API endpoints
9. Implement token refresh mechanism
10. Add request validation and sanitization
11. Configure secure media file storage
12. Consider implementing API key authentication for additional security

## 📊 Database Models

### User Model (Django's built-in)
Django's default User model with fields:
- `username`: Unique username
- `email`: User's email address
- `password`: Hashed password
- JWT tokens generated on signin

### PredictionHistory
Stores user's character recognition history:
- **user**: Foreign key to User
- **image**: Uploaded image file
- **predicted_class**: Class ID (0-35) returned by model
- **confidence**: Prediction confidence score (0-100)
- **created_at**: Timestamp of prediction

**Status:** Model exists but history saving is **currently disabled** (commented out in views.py)

**Purpose:** Track learning progress and review past recognitions (when enabled)

### SimilarityHistory
Stores handwriting comparison history:
- **user**: Foreign key to User
- **user_image**: User's uploaded handwriting image
- **reference_image**: Reference character image
- **blended_overlay**: Composite comparison image
- **target_class**: Class ID (0-35) of reference character
- **similarity_score**: Similarity percentage (0-100)
- **distance**: Euclidean distance between embeddings
- **is_same_character**: Boolean (True if distance < 0.45)
- **created_at**: Timestamp of comparison

**Status:** Model exists but history saving is **currently disabled** (commented out in views.py)

**Purpose:** Track handwriting improvement and provide visual feedback history (when enabled)

**Note:** To enable history tracking, uncomment the relevant code blocks in `api/views.py` (PredictView and SimilarityView)

## 🎨 Visual Feedback System

The API provides comprehensive visual feedback for both prediction and similarity endpoints:

### Prediction Endpoint
Returns the **preprocessed image** showing exactly what the model analyzed:
- **Grayscale** 64x64 image
- **Thresholded** and cleaned (noise removed)
- **Cropped** to character bounding box
- **Centered** in square canvas
- Returned as **base64-encoded PNG**

### Similarity Endpoint
Returns **three separate images** for comprehensive comparison:

1. **Reference Image**: 
   - Original reference character from database
   - Grayscale, 256x256 pixels
   - Shows the "correct" form

2. **User Image**: 
   - User's handwriting with **inverted colors**
   - Grayscale, 256x256 pixels
   - Inverted to match reference orientation

3. **Blended Overlay**: 
   - Composite image showing both characters
   - **Reference strokes**: Full opacity (100%)
   - **User strokes**: Semi-transparent (50% opacity)
   - **Overlapping areas**: Show where handwriting matches
   - White background for clarity

All images are encoded as **base64** and can be displayed directly in mobile apps, making it easy to:
- See the reference character clearly
- Compare user's writing side-by-side
- Identify specific areas that need improvement through the overlay


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
- Check filename format: `class_0.png` through `class_35.png`
- All 36 reference images must be present (classes 0-35)
- Model does not support classes beyond 35

**2. Database connection errors**
- Verify PostgreSQL is running: `pg_ctl status` or check services
- Check `.env` file credentials match your database
- Run migrations: `python manage.py migrate`
- Create database if it doesn't exist: `createdb your_database_name`

**3. Model loading errors**
- Ensure model weights exist in `api/ml_models/weights/`
- Check file sizes: efficientnet_b0_augmented_best.pth (47MB), siamese_efficientnet_b0_best.pth (25MB)
- Verify PyTorch is installed correctly: `pip show torch`
- Try re-downloading model weights if corrupted
- Make sure you're using the augmented model, not the old 62-class model

**4. Image processing errors**
- Check image format (PNG/JPEG supported)
- Ensure image is not corrupted
- Try reducing image size before upload
- Recommended: 64x64 grayscale images

**5. Authentication errors**
- "Authentication credentials not provided": Include `Authorization: Bearer <token>` header
- "Token is invalid or expired": Sign in again to get new tokens
- "User not found": Check username/password during signin
- JWT token lifetime: Access tokens expire after 1 hour (refresh available for 7 days)

**6. Media file errors**
- Ensure `MEDIA_ROOT` directory exists and is writable
- Check disk space for storing uploaded images
- Verify media URL configuration in settings

**7. CORS errors (when accessing from mobile app)**
- Install django-cors-headers: `pip install django-cors-headers`
- Add to `INSTALLED_APPS` in settings.py
- Configure `CORS_ALLOWED_ORIGINS` for your mobile app

**8. ImportError or module not found**
- Ensure all dependencies installed: `pip install -r requirements.txt`
- Activate virtual environment before running
- Check Python version compatibility (3.8+)

**9. Invalid class errors**
- "Invalid target_class X. Model supports classes 0-35 only"
  - Model trained on 36 classes (0-35), not 62
  - Use only valid class IDs (0-35)
  - Check MODEL_UPDATE_SUMMARY.md for migration details
- "Model predicted invalid class X"
  - This shouldn't happen with correct model file
  - Ensure you're using `efficientnet_b0_augmented_best.pth`

**10. Preprocessing errors**
- If automatic preprocessing fails, the API falls back to using the original image
- Check server logs for preprocessing error messages
- Ensure images have clear contrast and visible character strokes
- Very small or very large images may have issues - optimal range is 100x100 to 1000x1000

---

**Last Updated**: October 28, 2025  
**API Version**: 1.0  
**Model Version**: Augmented (36 classes)  
**Features**: Auto-preprocessing, JWT Auth, ML inference without auth (dev mode)
