# Ranjana Calligraphy Recognition API

A Django REST API backend for a mobile calligraphy learning application that recognizes and analyzes Ranjana script characters using deep learning. This API provides character recognition, handwriting similarity comparison, user authentication, and learning progress tracking to help users master Ranjana calligraphy.

---

## 📖 Documentation Quick Links

- **[Quick Start Guide](QUICK_START.md)** - Get running in 5 minutes
- **[Full API Documentation](#-api-endpoints)** - Complete endpoint reference (below)

---

## 🚀 Production Readiness Status

**Current Status: ~80% Production Ready** - Core functionality stable with HuggingFace integration

### ✅ Production-Ready Components
- **Core ML Models**: EfficientNet-B0 (99.5% accuracy) and Siamese Network (92.7% accuracy) - fully tested and optimized
- **HuggingFace Spaces Integration**: ML inference offloaded to HuggingFace Spaces with Gradio API
- **REST API Architecture**: Well-structured Django REST Framework with proper serialization and validation
- **Authentication System**: JWT-based authentication fully implemented with token refresh
- **Database**: PostgreSQL with proper migrations and relationships
- **Image Processing Pipeline**: Robust preprocessing with fallback mechanisms
- **AI-Powered Feedback**: Gemini API integration for personalized calligraphy feedback
- **User History Tracking**: Full prediction and similarity history with statistics
- **CORS Configuration**: Properly configured for cross-origin requests
- **Static File Serving**: WhiteNoise configured for production static files
- **Deployment Ready**: Procfile and gunicorn configured for Heroku/Render

### ⚠️ Needs Production Hardening
1. **HuggingFace API Configuration**
   - ✅ Gradio Client integration implemented
   - ✅ API endpoints properly configured with api_name
   - ⚠️ Requires gradio-client package installation in production
   - ⚠️ HUGGINGFACE_SPACE_URL must be set in environment variables
   - ⚠️ HuggingFace Space must be running and accessible

2. **Security Enhancements Needed**
   - DEBUG mode enabled by default (set to False in production)
   - SECRET_KEY in settings (should only be in .env)
   - No rate limiting implemented (vulnerable to abuse)
   - No input validation limits (file size, resolution)
   - Missing security headers (X-Frame-Options, CSP, etc.)

3. **Logging & Monitoring**
   - No structured logging configured
   - No error tracking (Sentry, etc.)
   - No performance monitoring
   - Print statements instead of proper logging

4. **Testing Coverage**
   - Basic tests exist but limited coverage
   - No integration tests for authentication flows
   - No load testing performed
   - No CI/CD pipeline configured

5. **Environment Configuration**
   - .env.example exists but incomplete
   - Missing HUGGINGFACE_SPACE_URL configuration example
   - No environment-specific settings separation

6. **Documentation Gaps**
   - API versioning strategy not defined
   - No API changelog or migration guide
   - Missing deployment instructions for AWS/GCP
   - No backup/disaster recovery procedures

### 🔧 Quick Production Checklist

Before deploying to production, complete these critical tasks:

```bash
# 1. HuggingFace Setup
□ Deploy Gradio app to HuggingFace Spaces
□ Set HUGGINGFACE_SPACE_URL in .env
□ Set USE_HUGGINGFACE_API=True in .env
□ Install gradio-client in production environment
□ Test HuggingFace API connectivity

# 2. Security
□ Set DEBUG=False in .env
□ Generate new SECRET_KEY and store only in .env
□ Add rate limiting (django-ratelimit)
□ Configure HTTPS/SSL certificates
□ Set secure cookie settings

# 3. Logging
□ Configure Django logging to file/service
□ Add Sentry or similar error tracking
□ Implement request/response logging

# 4. Performance
□ Configure database connection pooling
□ Add caching (Redis/Memcached)
□ Optimize media storage (S3/CloudFront)
□ Set up CDN for static files

# 5. Infrastructure
□ Configure database backups
□ Set up monitoring (New Relic/DataDog)
□ Configure auto-scaling rules
□ Set up load balancer
```

## 📋 Note: ML Inference Architecture

**Current Setup**: The application uses **HuggingFace Spaces** for ML inference:
- ✅ `api/ml_models/hf_client.py` implements Gradio Client for API calls
- ✅ `huggingface_space/app.py` contains Gradio interface with models
- ✅ Confidence values automatically converted from 0-1 to 0-100 range
- ⚠️ Requires `USE_HUGGINGFACE_API=True` and `HUGGINGFACE_SPACE_URL` in environment

**Benefits**:
- No need to load heavy ML models in Django server
- Reduced memory footprint for main application
- Scalable inference through HuggingFace infrastructure
- Easy model updates without redeploying Django app

## 📋 Quick Reference

| Feature | Endpoint | Model | Status | Auth Required |
|---------|----------|-------|--------|---------------|
| **Character Recognition** | `POST /api/predict/` | EfficientNet-B0 via HF (99.5%) | ✅ Working | ✅ Required |
| **Similarity Comparison** | `POST /api/similarity/` | Siamese Network via HF (92.7%) | ✅ Working | ✅ Required |
| **AI Feedback** | `POST /api/feedback/` | Gemini 2.5 Flash | ✅ Working | ✅ Required |
| **User Signup** | `POST /api/signup/` | - | ✅ Working | ❌ None |
| **User Signin** | `POST /api/signin/` | JWT Auth | ✅ Working | ❌ None |
| **Change Password** | `POST /api/change-password/` | JWT Auth | ✅ Working | ✅ Required |
| **Change Username** | `POST /api/change-username/` | JWT Auth | ✅ Working | ✅ Required |
| **Prediction History** | `GET /api/history/predictions/` | - | ✅ Working | ✅ Required |
| **Similarity History** | `GET /api/history/similarities/` | - | ✅ Working | ✅ Required |
| **Delete History Item** | `DELETE /api/history/similarities/<id>/` | - | ✅ Working | ✅ Required |
| **User Statistics** | `GET /api/statistics/` | - | ✅ Working | ✅ Required |

**Authentication:** JWT Bearer Token (`Authorization: Bearer <token>`)

**Key Features:**
- ✅ Full user authentication and session management
- ✅ HuggingFace Spaces integration for ML inference
- ✅ History tracking with database persistence
- ✅ AI-powered personalized feedback via Gemini API
- ✅ Advanced statistics and progress tracking
- ✅ Image preprocessing and optimization
- ✅ Model trained on **36 classes (0-35)** using augmented dataset
- ✅ Confidence values automatically normalized to 0-100 range

## 🎯 Overview

This backend supports a mobile app that helps users learn Ranjana script (an ancient Nepali script) by:
- **Recognizing** handwritten characters using AI (99.5% accuracy, 36 classes) via HuggingFace Spaces
- **Comparing** user's handwriting with reference samples (92.7% accuracy) via HuggingFace Spaces
- **Providing visual feedback** through three-panel comparison images (reference, user input, and blended overlay)
- **Authentication & User Management** with JWT-based security
- **Automatic image preprocessing** for optimal recognition results
- **History Tracking** of predictions and similarity comparisons with full database persistence

## ✨ Key Capabilities

### API View Functions

1. **PredictView** (Recognition) → *"I see character 12"*
   - Identifies which Ranjana character is written (36 classes: 0-35)
   - Uses EfficientNet-B0 Augmented classification model
   - Returns class ID, confidence score, and preprocessed image
   - Includes automatic image preprocessing (thresholding, cropping, centering, resizing)
   - **Status**: ✅ Production ready, requires authentication

2. **SimilarityView** (Comparison) → *"Your writing is 87% like the reference"*
   - Compares user's handwriting with reference character
   - Uses Siamese neural network for similarity scoring
   - Returns three separate images: reference, user input, and blended overlay
   - Generates visual comparison with color-coded differences
   - Integrates Gemini API for AI-powered personalized feedback
   - **Status**: ✅ Production ready, requires authentication

3. **FeedbackView** (AI Analysis) → *"Focus on stroke consistency"*
   - Analyzes blended overlay images using Google Gemini 2.5 Flash
   - Provides actionable, structured feedback in 4 focus points
   - Tailored advice for improving calligraphy technique
   - **Status**: ✅ Working, requires GEMINI_API_KEY in .env

4. **Authentication Views**
   - SignupView, SigninView (JWT-based)
   - ChangePasswordView, ChangeUsernameView (requires authentication)
   - **Status**: ✅ Production ready, fully tested

5. **History Views**
   - PredictionHistoryView, SimilarityHistoryView (requires authentication)
   - Delete individual history items
   - **Status**: ✅ Fully functional with database persistence

6. **UserStatisticsView** (Progress Tracking)
   - Comprehensive learning analytics and progress metrics
   - Filter by character, date range, or time period
   - Average scores, match rates, and performance trends
   - **Status**: ✅ Production ready

## 🚀 Features

### 1. User Authentication & Management ✅
- **JWT-based authentication** for secure API access
- **User signup/signin** with token-based sessions
- **Password management** with secure password change
- **Username updates** for user customization
- **All endpoints protected** with proper authentication
- **Token lifetime**: 1 hour (access), 7 days (refresh)

### 2. Character Recognition (PredictView) ✅
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
- **Status**: Production ready with authentication

### 3. Handwriting Similarity Analysis (SimilarityView) ✅
- **Compare user's handwriting** with reference samples
- **92.7% accuracy** using Siamese neural network
- Returns similarity percentage, distance, and three visual images
- **Three-panel visual output**:
  - **Reference Image**: Original reference character (grayscale, 256x256)
  - **User Image**: User's handwriting with inverted colors (grayscale, 256x256)
  - **Blended Overlay**: Composite comparison showing stroke alignment
- **AI-Powered Feedback**: Integrates Gemini API for personalized improvement suggestions
- **Distance threshold**: < 0.45 indicates same character
- **Status**: Production ready with authentication

### 4. AI-Powered Feedback System (FeedbackView) ✅
- **Google Gemini 2.5 Flash integration** for intelligent calligraphy analysis
- **Structured feedback format**: 
  - General assessment
  - 4 specific focus points for improvement
- **Automatic integration**: Feedback generated during similarity analysis
- **Standalone endpoint**: Can analyze any blended image independently
- **Status**: Working, requires GEMINI_API_KEY environment variable

### 5. Learning Progress Tracking ✅
- **Full database persistence**: All predictions and comparisons saved automatically
- **History endpoints active**: Retrieve complete user history with images
- **Delete functionality**: Users can remove individual history items
- **Organized media storage**: predictions/, similarity/, references/, blended/
- **Timestamped records**: Track progress over time
- **Status**: Fully functional and production ready

### 6. User Statistics & Analytics ✅
- **Comprehensive metrics**: Average scores, match rates, best performances
- **Character-level insights**: Most practiced characters, success rates
- **Flexible filtering**: By character class, date range, or time period
- **Score distribution**: High scores (≥90%), good (75-89%), needs practice (<75%)
- **Recent activity tracking**: Monitor user engagement
- **Status**: Production ready with advanced query capabilities

### 7. Deep Learning Models ✅
- **Classification Model**: `efficientnet_b0_augmented_best.pth` (47 MB)
  - Identifies which character is written (36 classes: 0-35)
  - Uses EfficientNet-B0 architecture with augmented training data
  - 99.5% accuracy on test set
- **Similarity Model**: `siamese_efficientnet_b0_best.pth` (25 MB)
  - Compares handwriting similarity using 128-dimensional embeddings
  - Twin encoder architecture for robust comparison
  - 92.7% accuracy on validation set

### 8. Security & Production Features ✅
- **JWT Authentication**: Secure token-based access control
- **CORS Configuration**: Properly configured for cross-origin requests
- **Password Hashing**: Django's secure password storage
- **Input Validation**: Serializers validate all user inputs
- **File Upload Security**: Type checking and size limits
- **PostgreSQL Database**: Robust relational database with migrations

### ⚠️ Not Yet Implemented
- **Asynchronous Task Processing**: Celery code exists but not configured
  - No background workers for concurrent users
  - No task queue or broker setup
  - All processing currently synchronous
- **Rate Limiting**: No protection against API abuse
- **Structured Logging**: Using print() instead of proper logging
- **Error Monitoring**: No Sentry or similar integration
- **Caching Layer**: No Redis/Memcached for performance optimization

## 📋 Prerequisites

- Python 3.11+ (configured in runtime.txt)
- PostgreSQL database
- pip (Python package manager)
- Google Gemini API key (for AI feedback feature)

**Note**: Redis and Celery are NOT required despite being mentioned in legacy documentation. The application runs synchronously.

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

Create a PostgreSQL database and configure environment variables:

```bash
# Copy example environment file
copy .env.example .env
```

Edit `.env` with your database credentials and API keys:
```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourhost.com,localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=https://your-frontend-domain.vercel.app,http://localhost:5173

# Database (PostgreSQL)
DB_NAME=your_database_name
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

# Gemini API (Required for AI feedback)
GEMINI_API_KEY=your_gemini_api_key_here
```

**Get Gemini API Key**: Visit [Google AI Studio](https://makersuite.google.com/app/apikey) to obtain a free API key.

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

### 7. Run the Application

**Single Command** - Start Django development server:
```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/`

**Optional** - For development with frontend:
```bash
# Terminal 1 - Backend
python manage.py runserver

# Terminal 2 - Frontend (if you have the React frontend)
cd frontend
npm install
npm run dev
```

**Note**: Despite references to Celery in the codebase, it is NOT configured. All processing happens synchronously in the Django server. To enable async processing, Celery configuration must be added to `calligrapy/settings.py` and a `celery.py` file must be created.

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

**Description:** Recognizes a Ranjana character from an uploaded image using EfficientNet-B0 classification model. Processes the image and returns results immediately.

**Authentication:** Required (Bearer Token)

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Headers: `Authorization: Bearer <access_token>`
- Body:
  ```
  image: <image_file> (PNG/JPEG, any size - will be auto-preprocessed)
  ```

**Response (200 OK):**
```json
{
  "success": true,
  "predicted_class": 12,
  "confidence": 98.5,
  "processed_image": "data:image/png;base64,iVBORw0KGgo..."
}
```

**Process:**
1. User uploads image
2. Server processes immediately:
   - Saves to temporary file
   - Automatic preprocessing (grayscale, threshold, crop, resize to 64x64)
   - EfficientNet-B0 model prediction
   - Returns class ID and confidence
3. Response returned directly (synchronous)

**Note:** 
- Model supports classes 0-35 only (36 total classes)
- Preprocessing is automatic with fallback to original if it fails
- Processing time: typically 1-3 seconds

**Use Case:** *"What character is this?"*

---

#### 6. Handwriting Similarity Comparison

**Endpoint:** `POST /api/similarity/`

**Description:** Compares user's handwriting with a reference character using Siamese neural network and generates AI-powered feedback. Processes and returns results immediately.

**Authentication:** Required (Bearer Token)

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Headers: `Authorization: Bearer <access_token>`
- Body:
  ```
  image: <image_file> (PNG/JPEG, any size)
  target_class: <integer> (0-35)
  processed_image_base64: <base64_string> (optional - from predict endpoint)
  ```

**Note:** `target_class` must be between 0-35 (36 classes total)

**Response (200 OK):**
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
  "gradcam_image": "data:image/png;base64,iVBORw0KGgo...",
  "blended_overlay": "data:image/png;base64,iVBORw0KGgo...",
  "feedback": "Great job! Your calligraphy shows good understanding...\n\nFocus points for correction:\n1. Improve stroke angle at the top curve\n2. Maintain consistent pressure on vertical strokes\n3. Extend the bottom tail slightly more\n4. Smooth out the connection between upper and lower parts"
}
```

**Interpretation:**
- `similarity_score`: Percentage similarity (0-100%)
- `distance`: Euclidean distance between embeddings (lower = more similar)
- `is_same_character`: True if distance < 0.45 threshold
- `reference_image`: Base64-encoded reference character (grayscale, 256x256)
- `user_image`: Base64-encoded user's handwriting with inverted colors (grayscale, 256x256)
- `blended_overlay`: Base64-encoded composite image showing stroke alignment
- `feedback`: AI-generated personalized feedback with 4 specific improvement points

**Process:**
1. User uploads image + target class
2. Server processes immediately:
   - Validates target class (0-35)
   - Loads reference image
   - Extracts 128-dimensional embeddings for both images
   - Calculates Euclidean distance
   - Generates three comparison images (reference, user, blended)
   - Calls Gemini API for AI feedback analysis
   - Saves to database history
3. Response returned directly (synchronous)

**Processing Time:** 
- Without AI feedback: 2-4 seconds
- With Gemini API feedback: 5-10 seconds (includes API call)

**Use Case:** *"How similar is the student's handwriting to the reference?"*

---

#### 7. AI Feedback Analysis

**Endpoint:** `POST /api/feedback/`

**Description:** Analyzes a blended comparison image using Google Gemini AI to provide personalized calligraphy improvement feedback.

**Authentication:** Required (Bearer Token)

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Headers: `Authorization: Bearer <access_token>`
- Body:
  ```
  image: <blended_image_file> (PNG/JPEG - typically the blended overlay from similarity)
  ```

**Response (200 OK):**
```json
{
  "success": true,
  "feedback": "Your calligraphy demonstrates good overall structure, but there's room for refinement.\n\nFocus points for correction:\n1. Increase consistency in stroke thickness throughout the character\n2. Improve the curvature at the top-right section to match the reference more closely\n3. Extend the lower stroke slightly further to achieve better balance\n4. Pay attention to stroke endings - make them more defined and deliberate"
}
```

**Note:** 
- Requires `GEMINI_API_KEY` in environment variables
- Processing time: 3-7 seconds (depends on Gemini API response)
- Feedback is automatically included in similarity endpoint responses
- This standalone endpoint is useful for re-analyzing saved history images

**Use Case:** *"What can I improve in my calligraphy technique?"*

---

### History Endpoints

#### 8. Get Prediction History

**Endpoint:** `GET /api/history/predictions/`

**Description:** Retrieve user's character recognition history with images and results

**Authentication:** Required (Bearer Token)

**Request:**
- Method: `GET`
- Headers: `Authorization: Bearer <access_token>`

**Response:**
```json
{
  "success": true,
  "count": 15,
  "predictions": [
    {
      "id": 1,
      "image_url": "http://localhost:8000/media/predictions/2025/11/22/image.png",
      "predicted_class": 12,
      "confidence": 98.5,
      "created_at": "2025-11-22T10:30:00Z"
    }
  ]
}
```

**Status**: ✅ Fully functional with automatic database persistence

---

#### 9. Get Similarity History

**Endpoint:** `GET /api/history/similarities/`

**Description:** Retrieve user's handwriting comparison history with all three comparison images and AI feedback

**Authentication:** Required (Bearer Token)

**Request:**
- Method: `GET`
- Headers: `Authorization: Bearer <access_token>`

**Response:**
```json
{
  "success": true,
  "count": 8,
  "similarities": [
    {
      "id": 1,
      "user_image_url": "http://localhost:8000/media/similarity/2025/11/22/user_12.png",
      "reference_image_url": "http://localhost:8000/media/references/2025/11/22/ref_12.png",
      "blended_overlay_url": "http://localhost:8000/media/blended/2025/11/22/blended_12.png",
      "target_class": 12,
      "similarity_score": 87.32,
      "distance": 0.38,
      "is_same_character": true,
      "feedback": "Great job! Your calligraphy shows good understanding...",
      "created_at": "2025-11-22T11:45:00Z"
    }
  ]
}
```

**Status**: ✅ Fully functional with automatic database persistence and AI feedback storage

---

#### 10. Delete History Item

**Endpoint:** `DELETE /api/history/similarities/<history_id>/`

**Description:** Delete a specific similarity history item and its associated images

**Authentication:** Required (Bearer Token)

**Request:**
- Method: `DELETE`
- Headers: `Authorization: Bearer <access_token>`
- URL Parameter: `history_id` (integer)

**Response:**
```json
{
  "success": true,
  "message": "History item deleted successfully"
}
```

**Note:** This permanently deletes the database record and all associated image files from storage.

---

#### 11. Get User Statistics

**Endpoint:** `GET /api/statistics/`

**Description:** Retrieve comprehensive learning analytics and progress metrics

**Authentication:** Required (Bearer Token)

**Request:**
- Method: `GET`
- Headers: `Authorization: Bearer <access_token>`
- Optional Query Parameters:
  - `target_class` (integer): Filter by specific character class (0-35)
  - `days` (integer): Filter to last N days
  - `start_date` (ISO datetime): Filter from this date
  - `end_date` (ISO datetime): Filter to this date

**Example Requests:**
```
GET /api/statistics/
GET /api/statistics/?target_class=12
GET /api/statistics/?days=7
GET /api/statistics/?start_date=2025-11-15T00:00:00Z&end_date=2025-11-22T23:59:59Z
```

**Response:**
```json
{
  "success": true,
  "statistics": {
    "total_analyses": 45,
    "average_score": 84.56,
    "match_rate": 78.5,
    "best_score": 96.8,
    "total_matches": 35,
    "total_mismatches": 10,
    "most_practiced_character": 12,
    "characters_attempted": 18,
    "high_scores": 15,
    "good_scores": 20,
    "needs_practice": 10,
    "recent_activity": "2025-11-22T14:30:00Z"
  }
}
```

**Metrics Explanation:**
- `total_analyses`: Total number of similarity comparisons
- `average_score`: Mean similarity score across all comparisons
- `match_rate`: Percentage of comparisons that matched (distance < 0.45)
- `best_score`: Highest similarity score achieved
- `total_matches`: Count of successful matches
- `total_mismatches`: Count of unsuccessful matches
- `most_practiced_character`: Most frequently practiced character class
- `characters_attempted`: Number of unique characters practiced
- `high_scores`: Count of scores ≥ 90% (excellent)
- `good_scores`: Count of scores 75-89% (good)
- `needs_practice`: Count of scores < 75%
- `recent_activity`: Timestamp of last analysis

**Status**: ✅ Production ready with advanced filtering capabilities

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

Database, media files, and REST framework settings are configured in `calligrapy/settings.py`.

Key configurations:
- PostgreSQL database (credentials in `.env`)
- JWT authentication with 1-hour access tokens, 7-day refresh tokens
- Media files stored in `media/` directory
- Default permission: IsAuthenticated (overridden to AllowAny for ML endpoints in development)

API endpoints are defined in `api/urls.py` with 8 active endpoints.

## 📱 Mobile App Integration

### Authentication Flow
1. User signs up via `/api/signup/`
2. User signs in via `/api/signin/` → receives JWT tokens
3. Use access token in `Authorization: Bearer <token>` header for protected endpoints
4. ML endpoints currently don't require authentication (development mode)

### API Response Format
All responses include a `success` boolean field and relevant data or error messages.

### Image Handling
Mobile apps can send images in any format - automatic preprocessing handles:
- Grayscale conversion and thresholding
- Smart cropping (removes noise, keeps character strokes)
- Centering and resizing to 64x64 pixels

All images are returned as base64-encoded strings for easy display.

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

**Current Development Status**: 
- ML endpoints (predict, similarity): **Open access** (AllowAny)
- User management (change password/username): **Protected** (IsAuthenticated)
- History endpoints: **Protected** (IsAuthenticated)
- JWT authentication: Active for protected endpoints
- Token lifetime: 1 hour (access), 7 days (refresh)

**For Production Deployment**:
1. Enable authentication for ML endpoints (change AllowAny to IsAuthenticated in views.py)
2. Configure CORS for mobile app
3. Enable HTTPS
4. Set DEBUG=False
5. Configure ALLOWED_HOSTS
6. Secure all environment variables
7. Enable rate limiting
8. Configure secure media storage

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

**Status**: ✅ Fully functional with automatic persistence

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
- **feedback**: AI-generated personalized feedback text
- **created_at**: Timestamp of comparison

**Status**: ✅ Fully functional with automatic persistence and AI feedback storage

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

All images are encoded as **base64** and can be displayed directly in mobile apps.

## 📊 Database Models

### User Model
Django's default User model for authentication.

### PredictionHistory
- Fields: user, image, predicted_class (0-35), confidence, created_at
- Storage: `media/predictions/YYYY/MM/DD/`
- **Status:** Endpoint active, saving disabled (uncomment in views.py to enable)

### SimilarityHistory
- Fields: user, prediction, user_image, reference_image, target_class (0-35), similarity_score, distance, is_same_character, blended_overlay, created_at
- Storage: `media/similarity/`, `media/references/`, `media/blended/` (organized by date)
- **Status:** Endpoint active, saving disabled (uncomment in views.py to enable)

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
- Recommended: Clear, high-contrast images for best preprocessing results

**5. Authentication errors**
- "Authentication credentials not provided": Include `Authorization: Bearer <token>` header
- "Token is invalid or expired": Sign in again to get new tokens (access token expires after 1 hour)
- "User not found": Check username/password during signin

**6. Gemini API errors**
- "GEMINI_API_KEY not found": Add API key to `.env` file
- "API request failed": Check API key validity and quota at [Google AI Studio](https://makersuite.google.com/app/apikey)
- If Gemini fails, similarity endpoint provides fallback feedback based on similarity score

**7. Media file errors**
- Ensure `media/` directory exists and is writable
- Check disk space for storing uploaded images
- Verify MEDIA_ROOT and MEDIA_URL settings in settings.py

**8. CORS errors (when accessing from frontend)**
- Check CORS_ALLOWED_ORIGINS in .env matches your frontend URL
- For development: CORS allows all origins when DEBUG=True
- For production: Add specific origins to CORS_ALLOWED_ORIGINS

**9. ImportError or module not found**
- Ensure all dependencies installed: `pip install -r requirements.txt`
- Activate virtual environment before running: `venv\Scripts\activate` (Windows)
- Check Python version: Python 3.11+ required

**10. Invalid class errors**
- Model trained on 36 classes (0-35 only)
- Ensure you're using `efficientnet_b0_augmented_best.pth`
- Verify target_class parameter is within valid range

**11. Preprocessing errors**
- If automatic preprocessing fails, API falls back to original image
- Check server console output for detailed error messages
- Ensure images have clear contrast and visible strokes for best results

**12. Performance/timeout issues**
- Similarity endpoint with Gemini API: 5-10 seconds normal
- Without Gemini: 2-4 seconds normal
- Large images: Preprocessing takes longer (resize before upload for faster processing)
- Database queries: Ensure migrations are applied and indexes exist

---

## 🚀 Production Deployment Guide

### Security Hardening

```python
# settings.py - Production configuration
DEBUG = False  # Never run with DEBUG=True in production
SECRET_KEY = os.getenv('SECRET_KEY')  # From environment only
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']

# Add security middleware
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

### Recommended Production Stack

1. **Web Server**: Gunicorn (already configured in Procfile)
2. **Reverse Proxy**: Nginx for static files and load balancing
3. **Database**: PostgreSQL with connection pooling (pgbouncer)
4. **Media Storage**: AWS S3 or CloudFront CDN
5. **Caching**: Redis for session storage and query caching
6. **Monitoring**: Sentry for error tracking, New Relic for APM
7. **Logging**: Centralized logging (e.g., CloudWatch, Papertrail)

### Deployment Platforms

**Render.com** (Recommended for beginners):
```bash
# Procfile already configured
# Add environment variables in Render dashboard
# Automatic deployment from Git
```

**Heroku**:
```bash
# Procfile already configured
heroku create your-app-name
heroku addons:create heroku-postgresql:mini
heroku config:set DEBUG=False
heroku config:set SECRET_KEY=your-secret-key
heroku config:set GEMINI_API_KEY=your-api-key
git push heroku main
```

**AWS/GCP/Azure**:
- Use Docker containers with provided configuration
- Set up load balancers and auto-scaling groups
- Configure RDS/Cloud SQL for database
- Use S3/Cloud Storage for media files

### Environment Variables Checklist

```bash
# Required for production
SECRET_KEY=<generate-new-key>
DEBUG=False
ALLOWED_HOSTS=yourdomain.com
DB_NAME=<production-db>
DB_USER=<production-user>
DB_PASSWORD=<strong-password>
DB_HOST=<db-host>
DB_PORT=5432
GEMINI_API_KEY=<your-api-key>
CORS_ALLOWED_ORIGINS=https://yourdomain.com

# Optional
SENTRY_DSN=<sentry-project-dsn>
AWS_ACCESS_KEY_ID=<for-s3>
AWS_SECRET_ACCESS_KEY=<for-s3>
AWS_STORAGE_BUCKET_NAME=<bucket-name>
```

### Performance Optimization

1. **Database Indexing**: Add indexes to frequently queried fields
2. **Query Optimization**: Use `select_related()` and `prefetch_related()`
3. **Image Optimization**: Consider image compression before storage
4. **CDN**: Serve static and media files through CDN
5. **Caching**: Implement Redis caching for frequent queries
6. **Rate Limiting**: Add django-ratelimit to prevent abuse

---

**Last Updated**: November 22, 2025  
**API Version**: 2.0  
**Model Version**: Augmented (36 classes: 0-35)  
**Status**: Production ready (75%) - Core features stable, async processing not configured
