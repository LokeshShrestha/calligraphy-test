"""
Debug utilities for all API features
Created: October 22, 2025
Purpose: Comprehensive debugging tools for authentication, user management, and prediction features
"""

import logging
import json
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework import status
from functools import wraps
import traceback
from PIL import Image
from io import BytesIO
import time

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


# ===========================
# DECORATORS FOR DEBUGGING
# ===========================

def debug_api_call(feature_name):
    """
    Decorator to log all API calls with request/response details
    Usage: @debug_api_call("Signup Feature")
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, request, *args, **kwargs):
            logger.info(f"=" * 80)
            logger.info(f"[{feature_name}] Starting request")
            logger.info(f"Method: {request.method}")
            logger.info(f"Path: {request.path}")
            logger.info(f"User: {request.user}")
            logger.info(f"Headers: {dict(request.headers)}")
            
            # Log request data (be careful with sensitive info)
            if hasattr(request, 'data'):
                safe_data = {k: v for k, v in request.data.items() if k not in ['password', 'password2', 'old_password', 'new_password']}
                logger.info(f"Request Data: {safe_data}")
            
            start_time = time.time()
            
            try:
                response = func(self, request, *args, **kwargs)
                execution_time = time.time() - start_time
                
                logger.info(f"[{feature_name}] Request completed successfully")
                logger.info(f"Response Status: {response.status_code}")
                logger.info(f"Execution Time: {execution_time:.4f} seconds")
                
                return response
                
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(f"[{feature_name}] Request failed")
                logger.error(f"Error: {str(e)}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                logger.error(f"Execution Time: {execution_time:.4f} seconds")
                raise
            finally:
                logger.info(f"=" * 80)
                
        return wrapper
    return decorator


def log_user_action(action_name):
    """
    Decorator to log user-specific actions
    Usage: @log_user_action("Password Change")
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, request, *args, **kwargs):
            user = request.user if hasattr(request, 'user') else 'Anonymous'
            logger.info(f"User Action: {action_name} by {user}")
            return func(self, request, *args, **kwargs)
        return wrapper
    return decorator


# ===========================
# AUTHENTICATION DEBUGGING
# ===========================

class AuthDebugger:
    """Debug utilities for authentication features"""
    
    @staticmethod
    def log_signup_attempt(data):
        """Log signup attempt details"""
        logger.info("=" * 50)
        logger.info("SIGNUP ATTEMPT")
        logger.info(f"Username: {data.get('username', 'N/A')}")
        logger.info(f"Email: {data.get('email', 'N/A')}")
        logger.info(f"Password provided: {'Yes' if data.get('password') else 'No'}")
        logger.info(f"Password2 provided: {'Yes' if data.get('password2') else 'No'}")
        logger.info(f"Passwords match: {data.get('password') == data.get('password2')}")
        logger.info("=" * 50)
    
    @staticmethod
    def log_signup_success(username):
        """Log successful signup"""
        logger.info(f"✓ Signup successful for user: {username}")
    
    @staticmethod
    def log_signup_failure(errors):
        """Log signup failure"""
        logger.error(f"✗ Signup failed with errors: {errors}")
    
    @staticmethod
    def log_signin_attempt(username):
        """Log signin attempt"""
        logger.info(f"Signin attempt for username: {username}")
    
    @staticmethod
    def log_signin_success(username):
        """Log successful signin"""
        logger.info(f"✓ Signin successful for user: {username}")
    
    @staticmethod
    def log_signin_failure(username):
        """Log signin failure"""
        logger.warning(f"✗ Signin failed for user: {username}")
    
    @staticmethod
    def log_token_generation(user):
        """Log token generation"""
        logger.info(f"JWT tokens generated for user: {user.username}")


# ===========================
# USER PROFILE DEBUGGING
# ===========================

class ProfileDebugger:
    """Debug utilities for profile update features"""
    
    @staticmethod
    def log_password_change_attempt(user):
        """Log password change attempt"""
        logger.info(f"Password change attempt by user: {user.username}")
    
    @staticmethod
    def log_password_change_success(user):
        """Log successful password change"""
        logger.info(f"✓ Password changed successfully for user: {user.username}")
    
    @staticmethod
    def log_password_change_failure(user, reason):
        """Log password change failure"""
        logger.warning(f"✗ Password change failed for user: {user.username} - Reason: {reason}")
    
    @staticmethod
    def log_username_change_attempt(old_username, new_username):
        """Log username change attempt"""
        logger.info(f"Username change attempt: {old_username} -> {new_username}")
    
    @staticmethod
    def log_username_change_success(old_username, new_username):
        """Log successful username change"""
        logger.info(f"✓ Username changed successfully: {old_username} -> {new_username}")
    
    @staticmethod
    def log_username_change_failure(username, reason):
        """Log username change failure"""
        logger.warning(f"✗ Username change failed for {username} - Reason: {reason}")


# ===========================
# IMAGE PREDICTION DEBUGGING
# ===========================

class PredictionDebugger:
    """Debug utilities for image prediction feature"""
    
    @staticmethod
    def log_prediction_request(request):
        """Log prediction request details"""
        logger.info("=" * 50)
        logger.info("IMAGE PREDICTION REQUEST")
        logger.info(f"Content-Type: {request.content_type}")
        logger.info(f"Files in request: {list(request.FILES.keys())}")
        logger.info("=" * 50)
    
    @staticmethod
    def log_image_details(image_file):
        """Log uploaded image details"""
        try:
            img = Image.open(image_file)
            logger.info(f"Image format: {img.format}")
            logger.info(f"Image size: {img.size}")
            logger.info(f"Image mode: {img.mode}")
            logger.info(f"Image file size: {image_file.size} bytes")
            image_file.seek(0)  # Reset file pointer
        except Exception as e:
            logger.error(f"Error reading image details: {str(e)}")
    
    @staticmethod
    def log_image_processing(step, details=""):
        """Log image processing steps"""
        logger.info(f"Image Processing - {step}: {details}")
    
    @staticmethod
    def log_prediction_success():
        """Log successful prediction"""
        logger.info("✓ Prediction completed successfully")
    
    @staticmethod
    def log_prediction_failure(error):
        """Log prediction failure"""
        logger.error(f"✗ Prediction failed: {str(error)}")


# ===========================
# SERIALIZER DEBUGGING
# ===========================

class SerializerDebugger:
    """Debug utilities for serializers"""
    
    @staticmethod
    def log_validation_start(serializer_name, data):
        """Log serializer validation start"""
        logger.debug(f"Validating {serializer_name}")
        safe_data = {k: v for k, v in data.items() if 'password' not in k.lower()}
        logger.debug(f"Data to validate: {safe_data}")
    
    @staticmethod
    def log_validation_success(serializer_name):
        """Log successful validation"""
        logger.debug(f"✓ {serializer_name} validation successful")
    
    @staticmethod
    def log_validation_failure(serializer_name, errors):
        """Log validation failure"""
        logger.warning(f"✗ {serializer_name} validation failed: {errors}")


# ===========================
# GENERAL DEBUGGING UTILITIES
# ===========================

def print_request_details(request):
    """Print comprehensive request details"""
    print("\n" + "=" * 80)
    print("REQUEST DETAILS")
    print("=" * 80)
    print(f"Method: {request.method}")
    print(f"Path: {request.path}")
    print(f"User: {request.user}")
    print(f"Authenticated: {request.user.is_authenticated if hasattr(request.user, 'is_authenticated') else 'N/A'}")
    print(f"Content-Type: {request.content_type}")
    print(f"Headers:")
    for key, value in request.headers.items():
        if 'authorization' not in key.lower():
            print(f"  {key}: {value}")
    print("=" * 80 + "\n")


def print_response_details(response):
    """Print comprehensive response details"""
    print("\n" + "=" * 80)
    print("RESPONSE DETAILS")
    print("=" * 80)
    print(f"Status Code: {response.status_code}")
    print(f"Content-Type: {response.get('Content-Type', 'N/A')}")
    if hasattr(response, 'data'):
        print(f"Response Data: {response.data}")
    print("=" * 80 + "\n")


def debug_database_query(query_description, queryset):
    """Debug database queries"""
    logger.debug(f"Database Query: {query_description}")
    logger.debug(f"Query: {queryset.query}")
    logger.debug(f"Count: {queryset.count()}")


def measure_execution_time(func):
    """Decorator to measure function execution time"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logger.debug(f"{func.__name__} executed in {end_time - start_time:.4f} seconds")
        return result
    return wrapper


# ===========================
# TEST DATA GENERATORS
# ===========================

class TestDataGenerator:
    """Generate test data for debugging"""
    
    @staticmethod
    def generate_signup_data():
        """Generate sample signup data"""
        return {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'TestPassword123!',
            'password2': 'TestPassword123!'
        }
    
    @staticmethod
    def generate_signin_data():
        """Generate sample signin data"""
        return {
            'username': 'testuser',
            'password': 'TestPassword123!'
        }
    
    @staticmethod
    def generate_change_password_data():
        """Generate sample password change data"""
        return {
            'old_password': 'TestPassword123!',
            'new_password': 'NewPassword456!'
        }
    
    @staticmethod
    def generate_change_username_data():
        """Generate sample username change data"""
        return {
            'new_username': 'newtestuser'
        }
    
    @staticmethod
    def generate_test_image():
        """Generate a test image for prediction"""
        img = Image.new('RGB', (100, 100), color='white')
        img_io = BytesIO()
        img.save(img_io, format='PNG')
        img_io.seek(0)
        return img_io


# ===========================
# ERROR TRACKING
# ===========================

class ErrorTracker:
    """Track and log errors"""
    
    errors = []
    
    @classmethod
    def log_error(cls, error_type, error_message, context=None):
        """Log an error with context"""
        error_entry = {
            'timestamp': time.time(),
            'type': error_type,
            'message': error_message,
            'context': context or {}
        }
        cls.errors.append(error_entry)
        logger.error(f"Error tracked: {error_type} - {error_message}")
    
    @classmethod
    def get_recent_errors(cls, count=10):
        """Get recent errors"""
        return cls.errors[-count:]
    
    @classmethod
    def clear_errors(cls):
        """Clear error log"""
        cls.errors = []
        logger.info("Error log cleared")


# ===========================
# DEBUGGING MIDDLEWARE (Optional)
# ===========================

class DebugMiddleware:
    """Middleware for debugging all requests"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Log request
        logger.debug(f"Incoming request: {request.method} {request.path}")
        
        # Process request
        response = self.get_response(request)
        
        # Log response
        logger.debug(f"Outgoing response: {response.status_code}")
        
        return response


# ===========================
# CONSOLE COLORS (For better readability)
# ===========================

class Colors:
    """ANSI color codes for console output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_colored(message, color=Colors.OKGREEN):
    """Print colored message to console"""
    print(f"{color}{message}{Colors.ENDC}")


# ===========================
# USAGE EXAMPLES
# ===========================

"""
USAGE EXAMPLES:

1. In views.py, wrap your view methods:
   
   from .debug import debug_api_call, AuthDebugger
   
   class SignupView(APIView):
       @debug_api_call("Signup Feature")
       def post(self, request):
           AuthDebugger.log_signup_attempt(request.data)
           # ... rest of the code

2. Use debugging utilities:
   
   from .debug import print_request_details, ProfileDebugger
   
   ProfileDebugger.log_password_change_attempt(user)

3. Generate test data:
   
   from .debug import TestDataGenerator
   
   test_data = TestDataGenerator.generate_signup_data()

4. Track errors:
   
   from .debug import ErrorTracker
   
   ErrorTracker.log_error('ValidationError', 'Invalid data', {'field': 'username'})
"""
