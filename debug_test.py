"""
Debug Test Script
Run this script to test all API features with debugging enabled
Usage: python manage.py shell < debug_test.py
"""

import sys
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'calligrapy.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from api.views_debug import (
    SignupViewDebug,
    SigninViewDebug,
    ChangePasswordViewDebug,
    ChangeUsernameViewDebug,
    PredictViewDebug
)
from api.debug import (
    TestDataGenerator,
    ErrorTracker,
    print_colored,
    Colors
)


def print_section(title):
    """Print section header"""
    print("\n" + "=" * 80)
    print_colored(title, Colors.HEADER)
    print("=" * 80 + "\n")


def test_signup():
    """Test signup with debugging"""
    print_section("TESTING SIGNUP FEATURE")
    
    factory = RequestFactory()
    view = SignupViewDebug.as_view()
    
    # Test with valid data
    print_colored("Test 1: Valid signup data", Colors.OKBLUE)
    data = TestDataGenerator.generate_signup_data()
    request = factory.post('/api/signup/', data)
    response = view(request)
    print(f"Response Status: {response.status_code}")
    print(f"Response Data: {response.data}\n")
    
    # Test with invalid data (passwords don't match)
    print_colored("Test 2: Invalid signup data (passwords don't match)", Colors.OKBLUE)
    invalid_data = data.copy()
    invalid_data['password2'] = 'DifferentPassword'
    request = factory.post('/api/signup/', invalid_data)
    response = view(request)
    print(f"Response Status: {response.status_code}")
    print(f"Response Data: {response.data}\n")
    
    # Test with missing fields
    print_colored("Test 3: Missing required fields", Colors.OKBLUE)
    incomplete_data = {'username': 'testuser'}
    request = factory.post('/api/signup/', incomplete_data)
    response = view(request)
    print(f"Response Status: {response.status_code}")
    print(f"Response Data: {response.data}\n")


def test_signin():
    """Test signin with debugging"""
    print_section("TESTING SIGNIN FEATURE")
    
    # Create a test user first
    try:
        User.objects.get(username='testuser').delete()
    except User.DoesNotExist:
        pass
    
    User.objects.create_user(
        username='testuser',
        email='testuser@example.com',
        password='TestPassword123!'
    )
    
    factory = RequestFactory()
    view = SigninViewDebug.as_view()
    
    # Test with valid credentials
    print_colored("Test 1: Valid signin credentials", Colors.OKBLUE)
    data = TestDataGenerator.generate_signin_data()
    request = factory.post('/api/signin/', data)
    response = view(request)
    print(f"Response Status: {response.status_code}")
    if response.status_code == 200:
        print("Tokens generated successfully")
        print(f"Access token present: {'access' in response.data}")
        print(f"Refresh token present: {'refresh' in response.data}\n")
    else:
        print(f"Response Data: {response.data}\n")
    
    # Test with invalid credentials
    print_colored("Test 2: Invalid signin credentials", Colors.OKBLUE)
    invalid_data = {
        'username': 'testuser',
        'password': 'WrongPassword'
    }
    request = factory.post('/api/signin/', invalid_data)
    response = view(request)
    print(f"Response Status: {response.status_code}")
    print(f"Response Data: {response.data}\n")


def test_change_password():
    """Test password change with debugging"""
    print_section("TESTING CHANGE PASSWORD FEATURE")
    
    # Ensure test user exists
    try:
        user = User.objects.get(username='testuser')
        user.set_password('TestPassword123!')
        user.save()
    except User.DoesNotExist:
        user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='TestPassword123!'
        )
    
    # Generate JWT token for the user
    from rest_framework_simplejwt.tokens import RefreshToken
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    
    factory = RequestFactory()
    view = ChangePasswordViewDebug.as_view()
    
    # Test with valid data
    print_colored("Test 1: Valid password change", Colors.OKBLUE)
    data = TestDataGenerator.generate_change_password_data()
    request = factory.post('/api/change-password/', data, HTTP_AUTHORIZATION=f'Bearer {access_token}')
    
    # Manually set the user (simulating JWT authentication)
    request.user = user
    
    response = view(request)
    print(f"Response Status: {response.status_code}")
    print(f"Response Data: {response.data}\n")
    
    # Test with incorrect old password
    print_colored("Test 2: Incorrect old password", Colors.OKBLUE)
    invalid_data = {
        'old_password': 'WrongPassword',
        'new_password': 'NewPassword456!'
    }
    
    # Reset password for next test
    user.set_password('NewPassword456!')
    user.save()
    
    request = factory.post('/api/change-password/', invalid_data, HTTP_AUTHORIZATION=f'Bearer {access_token}')
    request.user = user
    response = view(request)
    print(f"Response Status: {response.status_code}")
    print(f"Response Data: {response.data}\n")


def test_change_username():
    """Test username change with debugging"""
    print_section("TESTING CHANGE USERNAME FEATURE")
    
    # Ensure test user exists
    try:
        user = User.objects.get(username='testuser')
    except User.DoesNotExist:
        user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='TestPassword123!'
        )
    
    # Generate JWT token for the user
    from rest_framework_simplejwt.tokens import RefreshToken
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    
    factory = RequestFactory()
    view = ChangeUsernameViewDebug.as_view()
    
    # Test with valid new username
    print_colored("Test 1: Valid username change", Colors.OKBLUE)
    data = TestDataGenerator.generate_change_username_data()
    request = factory.post('/api/change-username/', data, HTTP_AUTHORIZATION=f'Bearer {access_token}')
    
    # Manually set the user (simulating JWT authentication)
    request.user = user
    
    response = view(request)
    print(f"Response Status: {response.status_code}")
    print(f"Response Data: {response.data}\n")
    
    # Reset username
    user.username = 'testuser'
    user.save()
    
    # Test with taken username
    print_colored("Test 2: Username already taken", Colors.OKBLUE)
    # Create another user
    try:
        User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='TestPassword123!'
        )
    except:
        pass
    
    invalid_data = {'new_username': 'existinguser'}
    request = factory.post('/api/change-username/', invalid_data, HTTP_AUTHORIZATION=f'Bearer {access_token}')
    request.user = user
    response = view(request)
    print(f"Response Status: {response.status_code}")
    print(f"Response Data: {response.data}\n")


def test_image_prediction():
    """Test image prediction with debugging"""
    print_section("TESTING IMAGE PREDICTION FEATURE")
    
    from django.core.files.uploadedfile import SimpleUploadedFile
    
    factory = RequestFactory()
    view = PredictViewDebug.as_view()
    
    # Test with valid image
    print_colored("Test 1: Valid image upload", Colors.OKBLUE)
    test_image = TestDataGenerator.generate_test_image()
    image_file = SimpleUploadedFile(
        "test_image.png",
        test_image.getvalue(),
        content_type="image/png"
    )
    
    request = factory.post('/api/predict/', {'image': image_file})
    response = view(request)
    print(f"Response Status: {response.status_code}")
    print(f"Content-Type: {response.get('Content-Type', 'N/A')}\n")
    
    # Test with missing image
    print_colored("Test 2: Missing image", Colors.OKBLUE)
    request = factory.post('/api/predict/', {})
    response = view(request)
    print(f"Response Status: {response.status_code}")
    print(f"Response Data: {response.data}\n")


def display_error_summary():
    """Display summary of all errors"""
    print_section("ERROR SUMMARY")
    
    errors = ErrorTracker.get_recent_errors(20)
    
    if not errors:
        print_colored("No errors recorded!", Colors.OKGREEN)
    else:
        print_colored(f"Total errors: {len(errors)}", Colors.WARNING)
        for i, error in enumerate(errors, 1):
            print(f"\n{i}. {error['type']}")
            print(f"   Message: {error['message']}")
            print(f"   Context: {error.get('context', {})}")


def cleanup():
    """Cleanup test data"""
    print_section("CLEANUP")
    
    print("Cleaning up test users...")
    User.objects.filter(username__in=['testuser', 'newtestuser', 'existinguser']).delete()
    print_colored("Cleanup complete!", Colors.OKGREEN)
    
    # Clear error tracker
    ErrorTracker.clear_errors()


def run_all_tests():
    """Run all debug tests"""
    print_colored("\n" + "=" * 80, Colors.BOLD)
    print_colored("CALLIGRAPHY API - DEBUG TEST SUITE", Colors.BOLD)
    print_colored("=" * 80 + "\n", Colors.BOLD)
    
    try:
        test_signup()
        test_signin()
        test_change_password()
        test_change_username()
        test_image_prediction()
        display_error_summary()
    finally:
        cleanup()
    
    print_colored("\n" + "=" * 80, Colors.BOLD)
    print_colored("ALL TESTS COMPLETED", Colors.BOLD)
    print_colored("=" * 80 + "\n", Colors.BOLD)
    print("\nCheck 'debug.log' file for detailed logs")


if __name__ == '__main__':
    run_all_tests()
