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


class SignupView(APIView):
	permission_classes = [AllowAny]
	def post(self, request):
		serializer = SignupSerializer(data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response({'message': 'User created successfully.'}, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Request Example
{
  "username": "",
  "email": "",
  "password": "",
  "password2": ""
}

class SigninView(APIView):
	permission_classes = [AllowAny]
	def post(self, request):
		serializer = SigninSerializer(data=request.data)
		if not serializer.is_valid():
			return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
		username = serializer.validated_data['username']
		password = serializer.validated_data['password']
		user = authenticate(username=username, password=password)
		# user email and username to generate token
		if user is not None:
			refresh = RefreshToken.for_user(user)
			return Response({
				'refresh': str(refresh),
				'access': str(refresh.access_token),
			}, status=status.HTTP_200_OK)
		return Response({'error': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)
# Request Example


{
	"username": "",
    "password": ""
}


# Profile update views
class ChangePasswordView(APIView):
	permission_classes = [IsAuthenticated]

	def post(self, request):
		user = request.user
		old_password = request.data.get('old_password')
		new_password = request.data.get('new_password')
		if not old_password or not new_password:
			return Response({'error': 'Old and new password required.'}, status=status.HTTP_400_BAD_REQUEST)
		if not check_password(old_password, user.password):
			return Response({'error': 'Old password is incorrect.'}, status=status.HTTP_400_BAD_REQUEST)
		user.set_password(new_password)
		user.save()
		return Response({'message': 'Password updated successfully.'}, status=status.HTTP_200_OK)


class ChangeUsernameView(APIView):
	permission_classes = [IsAuthenticated]
	def post(self, request):
		user = request.user
		new_username = request.data.get('new_username')
		if not new_username:
			return Response({'error': 'New username required.'}, status=status.HTTP_400_BAD_REQUEST)
		if User.objects.filter(username=new_username).exclude(pk=user.pk).exists():
			return Response({'error': 'Username already taken.'}, status=status.HTTP_400_BAD_REQUEST)
		user.username = new_username
		user.save()
		return Response({'message': 'Username updated successfully.'}, status=status.HTTP_200_OK)
	

class PredictView(APIView):
	permission_classes = [AllowAny]
	parser_classes = [MultiPartParser, FormParser]
	def post(self, request):
		serializer = ImageSerializer(data=request.data)
		if serializer.is_valid():
			image_file = serializer.validated_data['image']  
			img = Image.open(image_file)
			img = img.convert('L')
			img_io = BytesIO()
			img.save(img_io, format="PNG")
			img_io.seek(0)
			return HttpResponse(img_io, content_type="image/png")
		return Response(serializer.errors, status=400)