"""
Debug-enhanced views for all API features
This file shows how to integrate debugging utilities into your views
"""

from django.http import HttpResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import SignupSerializer, SigninSerializer, ImageSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from io import BytesIO
from PIL import Image

# Import debug utilities
from .debug import (
    debug_api_call, 
    log_user_action,
    AuthDebugger, 
    ProfileDebugger, 
    PredictionDebugger,
    SerializerDebugger,
    print_request_details,
    print_response_details,
    ErrorTracker,
    measure_execution_time
)


class SignupViewDebug(APIView):
    """Signup view with comprehensive debugging"""
    permission_classes = [AllowAny]
    
    @debug_api_call("Signup Feature")
    def post(self, request):
        # Log signup attempt
        AuthDebugger.log_signup_attempt(request.data)
        
        # Log serializer validation
        SerializerDebugger.log_validation_start("SignupSerializer", request.data)
        
        serializer = SignupSerializer(data=request.data)
        
        if serializer.is_valid():
            SerializerDebugger.log_validation_success("SignupSerializer")
            
            try:
                user = serializer.save()
                AuthDebugger.log_signup_success(user.username)
                return Response(
                    {'message': 'User created successfully.'}, 
                    status=status.HTTP_201_CREATED
                )
            except Exception as e:
                ErrorTracker.log_error('SignupError', str(e), {'data': request.data})
                AuthDebugger.log_signup_failure(str(e))
                return Response(
                    {'error': 'Failed to create user'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        SerializerDebugger.log_validation_failure("SignupSerializer", serializer.errors)
        AuthDebugger.log_signup_failure(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SigninViewDebug(APIView):
    """Signin view with comprehensive debugging"""
    permission_classes = [AllowAny]
    
    @debug_api_call("Signin Feature")
    def post(self, request):
        username = request.data.get('username', 'N/A')
        AuthDebugger.log_signin_attempt(username)
        
        SerializerDebugger.log_validation_start("SigninSerializer", request.data)
        
        serializer = SigninSerializer(data=request.data)
        
        if not serializer.is_valid():
            SerializerDebugger.log_validation_failure("SigninSerializer", serializer.errors)
            AuthDebugger.log_signin_failure(username)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        SerializerDebugger.log_validation_success("SigninSerializer")
        
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        
        user = authenticate(username=username, password=password)
        
        if user is not None:
            AuthDebugger.log_signin_success(username)
            AuthDebugger.log_token_generation(user)
            
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        
        AuthDebugger.log_signin_failure(username)
        ErrorTracker.log_error('AuthenticationError', 'Invalid credentials', {'username': username})
        return Response(
            {'error': 'Invalid credentials.'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )


class ChangePasswordViewDebug(APIView):
    """Password change view with comprehensive debugging"""
    permission_classes = [IsAuthenticated]
    
    @debug_api_call("Change Password Feature")
    @log_user_action("Password Change")
    def post(self, request):
        user = request.user
        ProfileDebugger.log_password_change_attempt(user)
        
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        
        # Validate required fields
        if not old_password or not new_password:
            reason = 'Missing required fields'
            ProfileDebugger.log_password_change_failure(user, reason)
            ErrorTracker.log_error('ValidationError', reason, {'user': user.username})
            return Response(
                {'error': 'Old and new password required.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify old password
        if not check_password(old_password, user.password):
            reason = 'Incorrect old password'
            ProfileDebugger.log_password_change_failure(user, reason)
            ErrorTracker.log_error('AuthenticationError', reason, {'user': user.username})
            return Response(
                {'error': 'Old password is incorrect.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update password
        try:
            user.set_password(new_password)
            user.save()
            ProfileDebugger.log_password_change_success(user)
            return Response(
                {'message': 'Password updated successfully.'}, 
                status=status.HTTP_200_OK
            )
        except Exception as e:
            ErrorTracker.log_error('PasswordUpdateError', str(e), {'user': user.username})
            return Response(
                {'error': 'Failed to update password'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ChangeUsernameViewDebug(APIView):
    """Username change view with comprehensive debugging"""
    permission_classes = [IsAuthenticated]
    
    @debug_api_call("Change Username Feature")
    @log_user_action("Username Change")
    def post(self, request):
        user = request.user
        old_username = user.username
        new_username = request.data.get('new_username')
        
        ProfileDebugger.log_username_change_attempt(old_username, new_username)
        
        # Validate new username
        if not new_username:
            reason = 'New username not provided'
            ProfileDebugger.log_username_change_failure(old_username, reason)
            ErrorTracker.log_error('ValidationError', reason, {'user': old_username})
            return Response(
                {'error': 'New username required.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if username is already taken
        if User.objects.filter(username=new_username).exclude(pk=user.pk).exists():
            reason = 'Username already taken'
            ProfileDebugger.log_username_change_failure(old_username, reason)
            ErrorTracker.log_error('ValidationError', reason, {
                'old_username': old_username,
                'new_username': new_username
            })
            return Response(
                {'error': 'Username already taken.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update username
        try:
            user.username = new_username
            user.save()
            ProfileDebugger.log_username_change_success(old_username, new_username)
            return Response(
                {'message': 'Username updated successfully.'}, 
                status=status.HTTP_200_OK
            )
        except Exception as e:
            ErrorTracker.log_error('UsernameUpdateError', str(e), {
                'old_username': old_username,
                'new_username': new_username
            })
            return Response(
                {'error': 'Failed to update username'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PredictViewDebug(APIView):
    """Image prediction view with comprehensive debugging"""
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]
    
    @debug_api_call("Image Prediction Feature")
    @measure_execution_time
    def post(self, request):
        PredictionDebugger.log_prediction_request(request)
        
        SerializerDebugger.log_validation_start("ImageSerializer", {'files': list(request.FILES.keys())})
        
        serializer = ImageSerializer(data=request.data)
        
        if serializer.is_valid():
            SerializerDebugger.log_validation_success("ImageSerializer")
            
            try:
                image_file = serializer.validated_data['image']
                
                # Log image details
                PredictionDebugger.log_image_details(image_file)
                
                # Process image
                PredictionDebugger.log_image_processing("Opening image")
                img = Image.open(image_file)
                
                PredictionDebugger.log_image_processing("Converting to grayscale", f"Mode: {img.mode} -> L")
                img = img.convert('L')
                
                PredictionDebugger.log_image_processing("Saving processed image")
                img_io = BytesIO()
                img.save(img_io, format="PNG")
                img_io.seek(0)
                
                # TODO: Add your model prediction here
                PredictionDebugger.log_image_processing("Model prediction", "Model not implemented yet")
                
                PredictionDebugger.log_prediction_success()
                return HttpResponse(img_io, content_type="image/png")
                
            except Exception as e:
                PredictionDebugger.log_prediction_failure(str(e))
                ErrorTracker.log_error('PredictionError', str(e), {
                    'files': list(request.FILES.keys())
                })
                return Response(
                    {'error': f'Prediction failed: {str(e)}'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        SerializerDebugger.log_validation_failure("ImageSerializer", serializer.errors)
        PredictionDebugger.log_prediction_failure(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ===========================
# DEBUG INFO ENDPOINT
# ===========================

class DebugInfoView(APIView):
    """
    Debug endpoint to get system information and recent errors
    WARNING: Disable this in production!
    """
    permission_classes = [AllowAny]  # Change to IsAdminUser in production
    
    def get(self, request):
        """Get debug information"""
        from django.conf import settings
        
        return Response({
            'debug_mode': settings.DEBUG,
            'recent_errors': ErrorTracker.get_recent_errors(10),
            'python_version': __import__('sys').version,
            'django_version': __import__('django').get_version(),
        })


"""
To use these debug views:

1. In urls.py, add debug routes:

from .views_debug import (
    SignupViewDebug, 
    SigninViewDebug, 
    ChangePasswordViewDebug, 
    ChangeUsernameViewDebug,
    PredictViewDebug,
    DebugInfoView
)

urlpatterns = [
    # Regular routes
    path('signup/', SignupView.as_view(), name='signup'),
    
    # Debug routes (use different paths)
    path('debug/signup/', SignupViewDebug.as_view(), name='signup-debug'),
    path('debug/signin/', SigninViewDebug.as_view(), name='signin-debug'),
    path('debug/change-password/', ChangePasswordViewDebug.as_view(), name='change-password-debug'),
    path('debug/change-username/', ChangeUsernameViewDebug.as_view(), name='change-username-debug'),
    path('debug/predict/', PredictViewDebug.as_view(), name='predict-debug'),
    path('debug/info/', DebugInfoView.as_view(), name='debug-info'),
]

2. Check the debug.log file for detailed logs

3. Use the /api/debug/info/ endpoint to see recent errors
"""
