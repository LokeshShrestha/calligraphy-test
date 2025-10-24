from django.http import HttpResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import SignupSerializer, SigninSerializer, ImageSerializer, SimilaritySerializer, GradCAMSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from io import BytesIO
from PIL import Image
import tempfile
import os
import base64


class SignupView(APIView):
	permission_classes = [AllowAny]
	def post(self, request):
		serializer = SignupSerializer(data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response({'message': 'User created successfully.'}, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
	permission_classes = [IsAuthenticated]
	parser_classes = [MultiPartParser, FormParser]
	
	def post(self, request):
		serializer = ImageSerializer(data=request.data)
		if serializer.is_valid():
			try:
				from .ml_models import get_classification_model
				import tempfile
				import os
				image_file = serializer.validated_data['image']

				with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
					tmp.write(image_file.read())
					tmp_path = tmp.name
				
				try:
					model = get_classification_model()
					result = model.predict(tmp_path, top_k=5)
					
					return Response({
						'success': True,
						'predicted_class': result['class'],
						'confidence': round(result['confidence'], 2),
						'top_predictions': [
							{
								'class': int(cls),
								'confidence': round(conf, 2)
							}
							for cls, conf in zip(result['top_classes'], result['top_confidences'])
						]
					}, status=status.HTTP_200_OK)
				
				finally:
					if os.path.exists(tmp_path):
						os.unlink(tmp_path)
			
			except Exception as e:
				return Response({
					'success': False,
					'error': str(e)
				}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
		
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SimilarityView(APIView):
	permission_classes = [IsAuthenticated]
	parser_classes = [MultiPartParser, FormParser]
	
	def post(self, request):
		serializer = SimilaritySerializer(data=request.data)
		if serializer.is_valid():
			try:
				from .ml_models import get_classification_model
				
				image1_file = serializer.validated_data['image1']
				image2_file = serializer.validated_data['image2']
				
				with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp1:
					tmp1.write(image1_file.read())
					tmp1_path = tmp1.name
				
				with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp2:
					tmp2.write(image2_file.read())
					tmp2_path = tmp2.name
				
				try:
					model = get_classification_model()
					similarity_score, distance = model.compute_similarity(tmp1_path, tmp2_path)
					
					threshold = 0.45
					is_same = distance < threshold
					
					return Response({
						'success': True,
						'similarity_score': round(similarity_score, 2),
						'distance': round(distance, 4),
						'is_same_character': is_same,
						'threshold': threshold
					}, status=status.HTTP_200_OK)
				
				finally:
					if os.path.exists(tmp1_path):
						os.unlink(tmp1_path)
					if os.path.exists(tmp2_path):
						os.unlink(tmp2_path)
			
			except Exception as e:
				return Response({
					'success': False,
					'error': str(e)
				}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
		
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GradCAMView(APIView):
	permission_classes = [IsAuthenticated]
	parser_classes = [MultiPartParser, FormParser]
	
	def post(self, request):
		serializer = GradCAMSerializer(data=request.data)
		if serializer.is_valid():
			try:
				from .ml_models import get_classification_model
				
				image_file = serializer.validated_data['image']
				target_class = serializer.validated_data.get('target_class', None)
				
				with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
					tmp.write(image_file.read())
					tmp_path = tmp.name
				
				gradcam_path = tmp_path.replace('.png', '_gradcam.png')
				
				try:
					model = get_classification_model()
					result = model.generate_gradcam(tmp_path, target_class=target_class, save_path=gradcam_path)
					
					with open(gradcam_path, 'rb') as f:
						gradcam_base64 = base64.b64encode(f.read()).decode('utf-8')
					
					return Response({
						'success': True,
						'predicted_class': result['predicted_class'],
						'confidence': round(result['confidence'] * 100, 2),
						'gradcam_image': f'data:image/png;base64,{gradcam_base64}'
					}, status=status.HTTP_200_OK)
				
				finally:
					if os.path.exists(tmp_path):
						os.unlink(tmp_path)
					if os.path.exists(gradcam_path):
						os.unlink(gradcam_path)
			
			except Exception as e:
				return Response({
					'success': False,
					'error': str(e)
				}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
		
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




