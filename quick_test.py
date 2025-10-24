"""
Quick Test Script - Test with Sample Images
Tests the ML model with actual Ranjana character images
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'calligrapy.settings')
django.setup()

from pathlib import Path
import requests
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken


def print_header(text):
    print("\n" + "=" * 70)
    print(text)
    print("=" * 70)


def get_auth_token():
    """Get JWT token for testing"""
    # Create or get test user
    try:
        user = User.objects.get(username='testuser')
    except User.DoesNotExist:
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!'
        )
        print("✓ Created test user")
    
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)


def find_sample_images():
    """Find sample images from Project_1 or create test images"""
    # Try to find images from Project_1
    project1_path = Path(__file__).parent / 'Project_1' / 'data' / 'Ranjana 64' / '3 Testing'
    
    sample_images = []
    
    if project1_path.exists():
        # Find first available image from each of first 3 classes
        for class_dir in sorted(project1_path.iterdir())[:3]:
            if class_dir.is_dir():
                images = list(class_dir.glob('*.png'))
                if images:
                    sample_images.append(images[0])
        
        if sample_images:
            print(f"✓ Found {len(sample_images)} sample images from Project_1")
            return sample_images
    
    print("⚠ No Project_1 images found, will use generated test images")
    return None


def test_with_curl_examples():
    """Show curl examples for manual testing"""
    print_header("CURL EXAMPLES FOR MANUAL TESTING")
    
    token = get_auth_token()
    
    print("\n1. Test Classification:")
    print(f'''
curl -X POST http://localhost:8000/api/predict/ \\
  -H "Authorization: Bearer {token}" \\
  -F "image=@your_character_image.png"
''')
    
    print("\n2. Test Similarity:")
    print(f'''
curl -X POST http://localhost:8000/api/similarity/ \\
  -H "Authorization: Bearer {token}" \\
  -F "image1=@character1.png" \\
  -F "image2=@character2.png"
''')
    
    print("\n3. Test Grad-CAM:")
    print(f'''
curl -X POST http://localhost:8000/api/gradcam/ \\
  -H "Authorization: Bearer {token}" \\
  -F "image=@your_character_image.png"
''')
    
    print("\n" + "=" * 70)


def test_with_python():
    """Test using Python requests"""
    print_header("PYTHON REQUESTS TEST")
    
    print("\nMake sure Django server is running:")
    print("  python manage.py runserver")
    print("\nPress Enter to continue, or Ctrl+C to cancel...")
    try:
        input()
    except KeyboardInterrupt:
        print("\n\nTest cancelled.")
        return
    
    base_url = "http://localhost:8000"
    token = get_auth_token()
    headers = {'Authorization': f'Bearer {token}'}
    
    # Find sample images
    sample_images = find_sample_images()
    
    if not sample_images:
        print("\n⚠ No sample images available")
        print("Please provide your own Ranjana character images to test")
        print("\nOr run the automated test:")
        print("  python ml_model_test.py")
        return
    
    # Test 1: Classification
    print("\n1. Testing Classification...")
    try:
        with open(sample_images[0], 'rb') as f:
            files = {'image': f}
            response = requests.post(f"{base_url}/api/predict/", 
                                   headers=headers, files=files)
        
        if response.status_code == 200:
            data = response.json()
            print("✓ Success!")
            print(f"  Predicted class: {data.get('predicted_class')}")
            print(f"  Confidence: {data.get('confidence')}%")
        else:
            print(f"✗ Failed: {response.status_code}")
            print(f"  {response.text}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 2: Similarity (if we have 2+ images)
    if len(sample_images) >= 2:
        print("\n2. Testing Similarity...")
        try:
            with open(sample_images[0], 'rb') as f1, open(sample_images[1], 'rb') as f2:
                files = {'image1': f1, 'image2': f2}
                response = requests.post(f"{base_url}/api/similarity/", 
                                       headers=headers, files=files)
            
            if response.status_code == 200:
                data = response.json()
                print("✓ Success!")
                print(f"  Similarity: {data.get('similarity_score')}%")
                print(f"  Same character: {data.get('is_same_character')}")
            else:
                print(f"✗ Failed: {response.status_code}")
                print(f"  {response.text}")
        except Exception as e:
            print(f"✗ Error: {e}")
    
    # Test 3: Grad-CAM
    print("\n3. Testing Grad-CAM...")
    try:
        with open(sample_images[0], 'rb') as f:
            files = {'image': f}
            response = requests.post(f"{base_url}/api/gradcam/", 
                                   headers=headers, files=files)
        
        if response.status_code == 200:
            data = response.json()
            print("✓ Success!")
            print(f"  Predicted class: {data.get('predicted_class')}")
            print(f"  Confidence: {data.get('confidence')}%")
            print(f"  Heatmap image: {'✓' if 'gradcam_image' in data else '✗'}")
        else:
            print(f"✗ Failed: {response.status_code}")
            print(f"  {response.text}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print("\n" + "=" * 70)


def show_postman_guide():
    """Show guide for testing with Postman"""
    print_header("POSTMAN TESTING GUIDE")
    
    token = get_auth_token()
    
    print("""
1. SETUP POSTMAN:
   - Create a new request
   - Set Authorization: Bearer Token
   - Token: (see below)

2. TEST /api/predict/
   - Method: POST
   - URL: http://localhost:8000/api/predict/
   - Body: form-data
   - Add key: "image" (type: File)
   - Select a Ranjana character PNG image
   - Send

3. TEST /api/similarity/
   - Method: POST
   - URL: http://localhost:8000/api/similarity/
   - Body: form-data
   - Add key: "image1" (type: File)
   - Add key: "image2" (type: File)
   - Select two PNG images
   - Send

4. TEST /api/gradcam/
   - Method: POST
   - URL: http://localhost:8000/api/gradcam/
   - Body: form-data
   - Add key: "image" (type: File)
   - (Optional) Add key: "target_class" (type: Text, value: 0-61)
   - Send
""")
    
    print(f"\nYour JWT Token (copy this):")
    print("-" * 70)
    print(token)
    print("-" * 70)
    print("\n(Token is valid for 5 minutes)")
    print("=" * 70)


def main():
    """Main test function"""
    print("""
╔════════════════════════════════════════════════════════════════════╗
║         RANJANA ML MODEL - QUICK TEST GUIDE                        ║
╚════════════════════════════════════════════════════════════════════╝
""")
    
    print("Choose a testing method:")
    print("  1. Show cURL examples")
    print("  2. Test with Python requests (requires server running)")
    print("  3. Show Postman testing guide")
    print("  4. Run automated test (recommended)")
    print("  5. Exit")
    
    choice = input("\nEnter choice (1-5): ").strip()
    
    if choice == '1':
        test_with_curl_examples()
    elif choice == '2':
        test_with_python()
    elif choice == '3':
        show_postman_guide()
    elif choice == '4':
        print("\nRunning automated tests...\n")
        os.system('python ml_model_test.py')
    else:
        print("Exiting...")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest cancelled by user.")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
