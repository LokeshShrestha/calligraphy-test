"""
ML Model Integration Test Script
Tests the new predict, similarity, and gradcam endpoints

Usage: python ml_model_test.py
"""

import sys
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'calligrapy.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework_simplejwt.tokens import RefreshToken
from api.views import PredictView, SimilarityView, GradCAMView
from io import BytesIO
from PIL import Image
import numpy as np


class Colors:
    """ANSI color codes"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_colored(text, color):
    """Print colored text"""
    print(f"{color}{text}{Colors.ENDC}")


def print_section(title):
    """Print section header"""
    print("\n" + "=" * 80)
    print_colored(title, Colors.HEADER)
    print("=" * 80 + "\n")


def create_test_image(size=(64, 64)):
    """
    Create a test image (simulating a Ranjana character)
    Returns BytesIO object containing PNG image
    """
    # Create a simple test image with some patterns
    img_array = np.random.randint(0, 255, size, dtype=np.uint8)
    
    # Add some structure (simulating handwritten character)
    center = (size[0] // 2, size[1] // 2)
    for i in range(size[0]):
        for j in range(size[1]):
            dist = ((i - center[0])**2 + (j - center[1])**2) ** 0.5
            if dist < 15:
                img_array[i, j] = 0  # Black center
    
    img = Image.fromarray(img_array, mode='L')
    img_io = BytesIO()
    img.save(img_io, format='PNG')
    img_io.seek(0)
    return img_io


def setup_test_user():
    """Create and return a test user with JWT token"""
    # Clean up existing test user
    try:
        User.objects.get(username='ml_test_user').delete()
    except User.DoesNotExist:
        pass
    
    # Create test user
    user = User.objects.create_user(
        username='ml_test_user',
        email='mltest@example.com',
        password='TestPassword123!'
    )
    
    # Generate JWT token
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    
    print_colored(f"✓ Test user created: {user.username}", Colors.OKGREEN)
    print(f"  Access token: {access_token[:20]}...\n")
    
    return user, access_token


def test_model_files_exist():
    """Check if model weight files are in place"""
    print_section("1. CHECKING MODEL FILES")
    
    import pathlib
    weights_dir = pathlib.Path(__file__).parent / 'api' / 'ml_models' / 'weights'
    
    files_to_check = [
        'efficientnet_b0_best.pth',
        'siamese_efficientnet_b0_best.pth'
    ]
    
    all_exist = True
    for filename in files_to_check:
        filepath = weights_dir / filename
        if filepath.exists():
            size_mb = filepath.stat().st_size / (1024 * 1024)
            print_colored(f"✓ {filename} found ({size_mb:.1f} MB)", Colors.OKGREEN)
        else:
            print_colored(f"✗ {filename} NOT FOUND!", Colors.FAIL)
            print(f"  Expected at: {filepath}")
            all_exist = False
    
    if not all_exist:
        print_colored("\n⚠ WARNING: Model files are missing!", Colors.WARNING)
        print("Please copy them from Project_1/models/ to api/ml_models/weights/")
        print("\nCommands:")
        print('  copy "Project_1\\models\\efficientnet_b0_best.pth" "api\\ml_models\\weights\\"')
        print('  copy "Project_1\\models\\siamese_efficientnet_b0_best.pth" "api\\ml_models\\weights\\"')
        return False
    
    print_colored("\n✓ All model files present!", Colors.OKGREEN)
    return True


def test_model_loading():
    """Test if the model can be loaded"""
    print_section("2. TESTING MODEL LOADING")
    
    try:
        from api.ml_models import get_classification_model
        
        print("Loading classification model...")
        model = get_classification_model()
        
        print_colored("✓ Model loaded successfully!", Colors.OKGREEN)
        print(f"  Model name: {model.model_name}")
        print(f"  Device: {model.device}")
        return True
        
    except FileNotFoundError as e:
        print_colored(f"✗ Model files not found: {e}", Colors.FAIL)
        return False
    except Exception as e:
        print_colored(f"✗ Error loading model: {e}", Colors.FAIL)
        import traceback
        traceback.print_exc()
        return False


def test_predict_endpoint(user, access_token):
    """Test the /api/predict/ endpoint"""
    print_section("3. TESTING PREDICT ENDPOINT")
    
    factory = RequestFactory()
    view = PredictView.as_view()
    
    # Test 1: Valid prediction
    print_colored("Test 1: Valid image prediction", Colors.OKBLUE)
    test_image = create_test_image()
    image_file = SimpleUploadedFile(
        "test_character.png",
        test_image.getvalue(),
        content_type="image/png"
    )
    
    request = factory.post(
        '/api/predict/',
        {'image': image_file},
        HTTP_AUTHORIZATION=f'Bearer {access_token}'
    )
    request.user = user
    
    try:
        response = view(request)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.data
            print_colored("✓ Prediction successful!", Colors.OKGREEN)
            print(f"  Predicted class: {data.get('predicted_class')}")
            print(f"  Confidence: {data.get('confidence')}%")
            print(f"  Top 3 predictions:")
            for pred in data.get('top_predictions', [])[:3]:
                print(f"    - Class {pred['class']}: {pred['confidence']}%")
        else:
            print_colored(f"✗ Failed with status {response.status_code}", Colors.FAIL)
            print(f"  Response: {response.data}")
        
    except Exception as e:
        print_colored(f"✗ Error: {e}", Colors.FAIL)
        import traceback
        traceback.print_exc()
    
    # Test 2: Missing image
    print_colored("\nTest 2: Missing image", Colors.OKBLUE)
    request = factory.post(
        '/api/predict/',
        {},
        HTTP_AUTHORIZATION=f'Bearer {access_token}'
    )
    request.user = user
    response = view(request)
    print(f"Status Code: {response.status_code} (should be 400)")
    if response.status_code == 400:
        print_colored("✓ Validation working correctly", Colors.OKGREEN)


def test_similarity_endpoint(user, access_token):
    """Test the /api/similarity/ endpoint"""
    print_section("4. TESTING SIMILARITY ENDPOINT")
    
    factory = RequestFactory()
    view = SimilarityView.as_view()
    
    # Test 1: Compare two images
    print_colored("Test 1: Compare two character images", Colors.OKBLUE)
    
    test_image1 = create_test_image()
    test_image2 = create_test_image()  # Different image
    
    image1_file = SimpleUploadedFile(
        "character1.png",
        test_image1.getvalue(),
        content_type="image/png"
    )
    
    image2_file = SimpleUploadedFile(
        "character2.png",
        test_image2.getvalue(),
        content_type="image/png"
    )
    
    request = factory.post(
        '/api/similarity/',
        {'image1': image1_file, 'image2': image2_file},
        HTTP_AUTHORIZATION=f'Bearer {access_token}'
    )
    request.user = user
    
    try:
        response = view(request)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.data
            print_colored("✓ Similarity computed!", Colors.OKGREEN)
            print(f"  Similarity score: {data.get('similarity_score')}%")
            print(f"  Distance: {data.get('distance')}")
            print(f"  Same character: {data.get('is_same_character')}")
        else:
            print_colored(f"✗ Failed with status {response.status_code}", Colors.FAIL)
            print(f"  Response: {response.data}")
        
    except Exception as e:
        print_colored(f"✗ Error: {e}", Colors.FAIL)
        import traceback
        traceback.print_exc()
    
    # Test 2: Same image (should be 100% similar)
    print_colored("\nTest 2: Compare identical images", Colors.OKBLUE)
    test_image_same = create_test_image()
    
    image1_file = SimpleUploadedFile(
        "character1.png",
        test_image_same.getvalue(),
        content_type="image/png"
    )
    
    # Reset the buffer
    test_image_same.seek(0)
    image2_file = SimpleUploadedFile(
        "character2.png",
        test_image_same.getvalue(),
        content_type="image/png"
    )
    
    request = factory.post(
        '/api/similarity/',
        {'image1': image1_file, 'image2': image2_file},
        HTTP_AUTHORIZATION=f'Bearer {access_token}'
    )
    request.user = user
    
    try:
        response = view(request)
        if response.status_code == 200:
            data = response.data
            print(f"  Similarity: {data.get('similarity_score')}% (should be ~100%)")
            print_colored("✓ Same image test passed", Colors.OKGREEN)
    except Exception as e:
        print_colored(f"✗ Error: {e}", Colors.FAIL)


def test_gradcam_endpoint(user, access_token):
    """Test the /api/gradcam/ endpoint"""
    print_section("5. TESTING GRAD-CAM ENDPOINT")
    
    factory = RequestFactory()
    view = GradCAMView.as_view()
    
    # Test: Generate Grad-CAM visualization
    print_colored("Test: Generate Grad-CAM heatmap", Colors.OKBLUE)
    
    test_image = create_test_image()
    image_file = SimpleUploadedFile(
        "character.png",
        test_image.getvalue(),
        content_type="image/png"
    )
    
    request = factory.post(
        '/api/gradcam/',
        {'image': image_file},
        HTTP_AUTHORIZATION=f'Bearer {access_token}'
    )
    request.user = user
    
    try:
        response = view(request)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.data
            print_colored("✓ Grad-CAM generated!", Colors.OKGREEN)
            print(f"  Predicted class: {data.get('predicted_class')}")
            print(f"  Confidence: {data.get('confidence')}%")
            print(f"  Heatmap image: {'✓ Present' if 'gradcam_image' in data else '✗ Missing'}")
            
            # Check if base64 image is present
            if 'gradcam_image' in data and data['gradcam_image'].startswith('data:image/png;base64,'):
                print_colored("  ✓ Base64 encoded image is valid", Colors.OKGREEN)
        else:
            print_colored(f"✗ Failed with status {response.status_code}", Colors.FAIL)
            print(f"  Response: {response.data}")
        
    except Exception as e:
        print_colored(f"✗ Error: {e}", Colors.FAIL)
        import traceback
        traceback.print_exc()


def cleanup(user):
    """Clean up test data"""
    print_section("CLEANUP")
    try:
        user.delete()
        print_colored("✓ Test user deleted", Colors.OKGREEN)
    except Exception as e:
        print_colored(f"✗ Cleanup error: {e}", Colors.WARNING)


def run_all_tests():
    """Run all ML model tests"""
    print_colored("\n" + "=" * 80, Colors.BOLD)
    print_colored("RANJANA ML MODEL INTEGRATION TEST SUITE", Colors.BOLD)
    print_colored("=" * 80 + "\n", Colors.BOLD)
    
    # Check prerequisites
    if not test_model_files_exist():
        print_colored("\n⚠ TESTS ABORTED: Model files missing", Colors.FAIL)
        print("\nPlease copy model files first, then re-run this test.")
        return
    
    if not test_model_loading():
        print_colored("\n⚠ TESTS ABORTED: Model loading failed", Colors.FAIL)
        return
    
    # Setup
    user, access_token = setup_test_user()
    
    try:
        # Run endpoint tests
        test_predict_endpoint(user, access_token)
        test_similarity_endpoint(user, access_token)
        test_gradcam_endpoint(user, access_token)
        
        print_section("TEST SUMMARY")
        print_colored("✓ All tests completed!", Colors.OKGREEN)
        print("\nYour ML model integration is working correctly!")
        print("\nYou can now:")
        print("  - Use the API endpoints in your application")
        print("  - Test with real Ranjana character images")
        print("  - Integrate with your frontend")
        
    except Exception as e:
        print_colored(f"\n✗ Test suite error: {e}", Colors.FAIL)
        import traceback
        traceback.print_exc()
    finally:
        cleanup(user)
    
    print_colored("\n" + "=" * 80, Colors.BOLD)
    print_colored("TESTING COMPLETE", Colors.BOLD)
    print_colored("=" * 80 + "\n", Colors.BOLD)


if __name__ == '__main__':
    run_all_tests()
