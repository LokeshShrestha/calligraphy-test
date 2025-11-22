# Ranjana Calligraphy Recognition API

A Django REST API backend for a mobile calligraphy learning application that recognizes and analyzes Ranjana script characters using deep learning. This API provides character recognition, handwriting similarity comparison, user authentication, and learning progress tracking to help users master Ranjana calligraphy.

## � New: Asynchronous Processing with Celery + Redis

This API now supports **multiple concurrent users** with asynchronous task processing!

📖 **Quick Start Guides:**
- [Quick Reference Card](QUICK_REFERENCE.md) - Get started in 3 steps
- [Full Celery Setup Guide](CELERY_SETUP.md) - Complete installation and configuration
- [Changes Summary](CHANGES_SUMMARY.md) - What's new and what changed

## �📋 Quick Reference

| Feature | Endpoint | Model | Accuracy |
|---------|----------|-------|----------|
| **Character Recognition** | `POST /api/predict/` | EfficientNet-B0 Augmented (47MB) | 99.5% |
| **Similarity Comparison** | `POST /api/similarity/` | Siamese Network (25MB) | 92.7% |
| **Task Status Check** | `GET /api/task-status/<task_id>/` | - | - |
| **User Signup** | `POST /api/signup/` | - | - |
| **User Signin** | `POST /api/signin/` | JWT Auth | - |
| **Change Password** | `POST /api/change-password/` | JWT Auth | - |
| **Change Username** | `POST /api/change-username/` | JWT Auth | - |
| **Prediction History** | `GET /api/history/predictions/` | - | - |
| **Similarity History** | `GET /api/history/similarities/` | - | - |

**Authentication:** 
- JWT Bearer Token required for: password/username change endpoints, history endpoints
- ML endpoints (predict, similarity) are currently open for development (no authentication required)

**Note:** History saving to database is currently disabled in views.py (commented out). History endpoints are functional but will return empty data until saving is re-enabled.

**Note:** Model trained on **36 classes (0-35)** using augmented dataset

## 🎯 Overview

This backend supports a mobile app that helps users learn Ranjana script (an ancient Nepali script) by:
- **Recognizing** handwritten characters using AI (99.5% accuracy, 36 classes)
- **Comparing** user's handwriting with reference samples (92.7% accuracy)
- **Providing visual feedback** through three-panel comparison images (reference, user input, and blended overlay)
- **Authentication & User Management** with JWT-based security
- **Automatic image preprocessing** for optimal recognition results
- **History Tracking** of predictions and similarity comparisons (available, currently not saving data)

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

4. **History Views**
   - PredictionHistoryView, SimilarityHistoryView (requires authentication)
   - Endpoints are active, but data saving is currently disabled
   - Database models are in place and ready to use

## 🚀 Features

### 0. Asynchronous Task Processing with Celery & Redis
- **Concurrent user support** - Multiple users can process images simultaneously
- **Non-blocking API** - Immediate response with task ID, results retrieved separately
- **Scalable architecture** - Easy to add more workers for increased load
- **Task monitoring** - Track task status (PENDING, STARTED, SUCCESS, FAILURE)
- **Reliability** - Tasks persisted in Redis, won't be lost on server restart
- **Production-ready** - Configured with django-celery-results for task tracking

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

### 5. Learning Progress Tracking (Available but Disabled)
- **Database models ready**: PredictionHistory and SimilarityHistory models exist
- **History endpoints active**: GET endpoints for retrieving history are functional
- **Saving disabled**: Data saving is currently commented out in views.py
- **To enable**: Uncomment the database save sections in PredictView and SimilarityView
- **Features when enabled**:
  - Track all character recognitions with images and confidence scores
  - Review past handwriting comparisons with visual overlays
  - Timestamped records for progress monitoring
  - Organized media storage (predictions/, similarity/, references/, blended/)

### 6. Deep Learning Models
- **Classification Model**: `efficientnet_b0_augmented_best.pth` (47 MB)
  - Identifies which character is written (36 classes: 0-35)
  - Uses EfficientNet-B0 architecture with augmented training data
- **Similarity Model**: `siamese_efficientnet_b0_best.pth` (25 MB)
  - Compares handwriting similarity using 128-dimensional embeddings
  - Twin encoder architecture for robust comparison

## 📋 Prerequisites

- Python 3.8+
- PostgreSQL database
- Redis (for Celery task queue)
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

### 4. Install and Start Redis

Redis is required for Celery task queue to support concurrent users.

**Windows:**
```bash
# Option 1: Download from https://github.com/microsoftarchive/redis/releases
# Option 2: Use Docker
docker run -d -p 6379:6379 redis:latest
```

**Linux/macOS:**
```bash
# Ubuntu/Debian
sudo apt-get install redis-server
redis-server

# macOS
brew install redis
redis-server
```

Verify Redis is running:
```bash
redis-cli ping
# Should return: PONG
```

### 5. Database Setup

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

# Redis for Celery
REDIS_URL=redis://localhost:6379/0
```

### 6. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Add Reference Images

Place reference character images in `api/reference_images/`:
- Filename format: `class_0.png`, `class_1.png`, ..., `class_35.png`
- Images should be 64x64 grayscale PNG files
- Total: 36 reference images (one per character class)

**Note:** Model supports classes 0-35 only (36 classes total)

### 8. Run the Application

You need to run **THREE** separate processes for full functionality:

**Terminal 1 - Django Server:**
```bash
python manage.py runserver
```

**Terminal 2 - Celery Worker:**
```bash
# Windows
celery -A calligrapy worker --pool=solo --loglevel=info

# Linux/macOS
celery -A calligrapy worker --loglevel=info
```

**Terminal 3 - Optional: Celery Flower (Monitoring):**
```bash
pip install flower
celery -A calligrapy flower
# Visit: http://localhost:5555
```

The API will be available at `http://localhost:8000/`

> **Quick Start:** Run `start.bat` (Windows) or `bash start.sh` (Linux/Mac) for automated setup checks.

> **📖 For detailed Celery setup instructions, see [CELERY_SETUP.md](CELERY_SETUP.md)**

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

**Description:** Asynchronously recognizes a Ranjana character from an uploaded image using EfficientNet-B0 classification model. Returns a task ID immediately, then process the image in the background.

**Authentication:** Not required (development mode)

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body:
  ```
  image: <image_file> (PNG/JPEG, any size - will be auto-preprocessed)
  ```

**Immediate Response (202 ACCEPTED):**
```json
{
  "success": true,
  "task_id": "abc123-def456-ghi789",
  "message": "Prediction task started. Use the task_id to check status."
}
```

**Process Flow:**
1. User uploads image → Receives task ID immediately
2. Background worker processes the task:
   - Saves to temporary file
   - Automatic preprocessing (grayscale, threshold, crop, resize to 64x64)
   - EfficientNet-B0 model prediction
   - Returns class ID and confidence
3. User polls `/api/task-status/<task_id>/` to get results

**To Get Results:**
Poll `GET /api/task-status/<task_id>/` until status is SUCCESS:

```json
{
  "task_id": "abc123-def456-ghi789",
  "status": "SUCCESS",
  "message": "Task completed successfully",
  "result": {
    "success": true,
    "predicted_class": 12,
    "confidence": 98.5,
    "processed_image": "data:image/png;base64,iVBORw0KGgo..."
  }
}
```

**Benefits:**
- Non-blocking: API responds immediately
- Concurrent: Multiple users can process images simultaneously
- Scalable: Add more workers to handle more users

**Note:** 
- Model supports classes 0-35 only (36 total classes)
- Preprocessing is automatic
- Task results are stored in database for retrieval

**Use Case:** *"What character is this?"* (Async version)

---

#### 6. Handwriting Similarity Comparison

**Endpoint:** `POST /api/similarity/`

**Description:** Asynchronously compares user's handwriting with a reference character using Siamese neural network. Returns a task ID immediately, then processes the comparison in the background.

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

**Immediate Response (202 ACCEPTED):**
```json
{
  "success": true,
  "task_id": "xyz789-abc123-def456",
  "message": "Similarity computation task started. Use the task_id to check status."
}
```

**Process Flow:**
1. User uploads image + target class → Receives task ID immediately
2. Background worker processes the task:
   - Validates target class (0-35)
   - Loads reference image
   - Extracts 128-dimensional embeddings for both images
   - Calculates Euclidean distance
   - Generates three comparison images (reference, user, blended)
   - Returns similarity score and all images
3. User polls `/api/task-status/<task_id>/` to get results

**To Get Results:**
Poll `GET /api/task-status/<task_id>/` until status is SUCCESS:

```json
{
  "task_id": "xyz789-abc123-def456",
  "status": "SUCCESS",
  "message": "Task completed successfully",
  "result": {
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

**Benefits:**
- Non-blocking: API responds immediately
- Concurrent: Multiple users can compare images simultaneously
- Scalable: Handles high load with multiple workers

**Use Case:** *"How similar is the student's handwriting to the reference?"* (Async version)

---

### Task Management Endpoints

#### 7. Check Task Status

**Endpoint:** `GET /api/task-status/<task_id>/`

**Description:** Check the status of any asynchronous task (prediction or similarity)

**Authentication:** Not required (development mode)

**Request:**
- Method: `GET`
- URL Parameter: `task_id` (received from predict or similarity endpoint)

**Response - Task Pending:**
```json
{
  "task_id": "abc123-def456-ghi789",
  "status": "PENDING",
  "message": "Task is waiting to be processed"
}
```

**Response - Task In Progress:**
```json
{
  "task_id": "abc123-def456-ghi789",
  "status": "STARTED",
  "message": "Task is currently being processed"
}
```

**Response - Task Completed Successfully:**
```json
{
  "task_id": "abc123-def456-ghi789",
  "status": "SUCCESS",
  "message": "Task completed successfully",
  "result": {
    "success": true,
    "predicted_class": 12,
    "confidence": 98.5,
    "processed_image": "data:image/png;base64,..."
  }
}
```

**Response - Task Failed:**
```json
{
  "task_id": "abc123-def456-ghi789",
  "status": "FAILURE",
  "message": "Task failed",
  "error": "Error description here"
}
```

**Task Status Values:**
- `PENDING`: Task is waiting in the queue
- `STARTED`: Task is currently being processed by a worker
- `SUCCESS`: Task completed successfully (result available)
- `FAILURE`: Task failed with an error
- `RETRY`: Task is being retried after failure
- `REVOKED`: Task was cancelled

**Polling Example:**
```javascript
async function waitForResult(taskId) {
  while (true) {
    const response = await fetch(`/api/task-status/${taskId}/`);
    const data = await response.json();
    
    if (data.status === 'SUCCESS') {
      return data.result;
    } else if (data.status === 'FAILURE') {
      throw new Error(data.error);
    }
    
    // Wait 1 second before checking again
    await new Promise(r => setTimeout(r, 1000));
  }
}
```

**Use Case:** *"Is my prediction/similarity task done yet?"*

---

### History Endpoints

#### 8. Get Prediction History

**Endpoint:** `GET /api/history/predictions/`

**Description:** Retrieve user's character recognition history

**Authentication:** Required (Bearer Token)

**Status:** Endpoint is active, but data saving is currently disabled. Will return empty results until saving is re-enabled in views.py.

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
      "image_url": "http://localhost:8000/media/predictions/2025/10/28/image.png",
      "predicted_class": 12,
      "confidence": 98.5,
      "created_at": "2025-10-28T10:30:00Z"
    }
  ]
}
```

**Note:** All `predicted_class` values will be 0-35

**To Enable Data Saving:**
Uncomment the following section in `api/views.py` (PredictView):
```python
prediction = PredictionHistory.objects.create(
    user=request.user,
    image=image_file,
    predicted_class=result['class'],
    confidence=result['confidence']
)
```

---

#### 9. Get Similarity History

**Endpoint:** `GET /api/history/similarities/`

**Description:** Retrieve user's handwriting comparison history with all three comparison images

**Authentication:** Required (Bearer Token)

**Status:** Endpoint is active, but data saving is currently disabled. Will return empty results until saving is re-enabled in views.py.

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
      "user_image_url": "http://localhost:8000/media/similarity/2025/10/28/user_12.png",
      "reference_image_url": "http://localhost:8000/media/references/2025/10/28/ref_12.png",
      "blended_overlay_url": "http://localhost:8000/media/blended/2025/10/28/blended_12.png",
      "target_class": 12,
      "similarity_score": 87.32,
      "distance": 0.38,
      "is_same_character": true,
      "created_at": "2025-10-28T11:45:00Z"
    }
  ]
}
```

**Note:** All `target_class` values will be 0-35

**To Enable Data Saving:**
Uncomment the following section in `api/views.py` (SimilarityView):
```python
similarity_history = SimilarityHistory.objects.create(
    user=request.user,
    user_image=user_file,
    reference_image=ref_file,
    target_class=target_class,
    similarity_score=similarity_score,
    distance=distance,
    is_same_character=is_same,
    blended_overlay=blended_file
)
```

Also uncomment in the response:
```python
'history_id': similarity_history.id,
```

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
- Recommended: 64x64 grayscale images

**5. Authentication errors**
- "Authentication credentials not provided": Include `Authorization: Bearer <token>` header for protected endpoints
- "Token is invalid or expired": Sign in again to get new tokens
- "User not found": Check username/password during signin
- Note: ML endpoints currently don't require authentication (development mode)

**6. Media file errors**
- Ensure `media/` directory exists and is writable
- Check disk space for storing uploaded images

**7. CORS errors (when accessing from mobile app)**
- Install and configure django-cors-headers package
- Add allowed origins in settings.py

**8. ImportError or module not found**
- Ensure all dependencies installed: `pip install -r requirements.txt`
- Activate virtual environment before running

**9. Invalid class errors**
- Model trained on 36 classes (0-35 only)
- Ensure you're using `efficientnet_b0_augmented_best.pth`

**10. Preprocessing errors**
- If automatic preprocessing fails, API falls back to original image
- Check server logs for error messages
- Ensure images have clear contrast and visible strokes

---

**Last Updated**: October 28, 2025  
**API Version**: 1.0  
**Model Version**: Augmented (36 classes)  
**Status**: Development mode (ML endpoints open, history saving disabled)
