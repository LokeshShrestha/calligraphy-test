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
from PIL import Image, ImageOps
import tempfile
import os
import base64
import numpy as np
from django.core.files.base import ContentFile
from .models import PredictionHistory, SimilarityHistory


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
					result = model.predict(tmp_path, top_k=1)
					
					# Save to database
					prediction = PredictionHistory.objects.create(
						user=request.user,
						image=image_file,
						predicted_class=result['class'],
						confidence=result['confidence']
					)
					
					return Response({
						'success': True,
						# 'prediction_id': prediction.id,
						'predicted_class': result['class'],
						'confidence': round(result['confidence'], 2)
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
	
	def _create_comparison_overlay(self, user_image_path, reference_image_path):
		# Load images and convert to grayscale
		user_img = Image.open(user_image_path).convert('L')
		ref_img = Image.open(reference_image_path).convert('L')
		
		# Resize to same dimensions (larger for better visibility)
		target_size = (256, 256)
		user_img = user_img.resize(target_size, Image.Resampling.LANCZOS)
		ref_img = ref_img.resize(target_size, Image.Resampling.LANCZOS)
		
		# Convert to numpy arrays
		user_array = np.array(user_img)
		ref_array = np.array(ref_img)
		
		# Invert so that strokes are white (255) and background is black (0)
		user_array = 255 - user_array
		ref_array = 255 - ref_array
		
		# Normalize to 0-1 range
		user_norm = user_array.astype(float) / 255.0
		ref_norm = ref_array.astype(float) / 255.0
		
		height, width = user_array.shape
		overlay = np.zeros((height, width, 3), dtype=np.uint8)
		
		overlay[:, :, 0] = (ref_norm * 255).astype(np.uint8)
		
		overlay[:, :, 1] = (user_norm * 255).astype(np.uint8)
		
		# Where both overlap, it becomes YELLOW (R+G)
		# Where only reference: RED
		# Where only user: GREEN
		# Background: BLACK
		
		comparison_image = Image.fromarray(overlay, 'RGB')
		
		return comparison_image
	
	def post(self, request):
		serializer = SimilaritySerializer(data=request.data)
		if serializer.is_valid():
			try:
				from .ml_models import get_classification_model
				from django.conf import settings
				
				image_file = serializer.validated_data['image']
				target_class = serializer.validated_data['target_class']
				
				# Path to reference image for the predicted class
				reference_images_dir = os.path.join(settings.BASE_DIR, 'api', 'reference_images')
				reference_image_path = os.path.join(reference_images_dir, f'class_{target_class}.png')
				
				# Check if reference image exists
				if not os.path.exists(reference_image_path):
					return Response({
						'success': False,
						'error': f'Reference image for class {target_class} not found. Please upload reference images.'
					}, status=status.HTTP_404_NOT_FOUND)
				
				# Save user's uploaded image temporarily
				with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
					tmp.write(image_file.read())
					tmp_path = tmp.name
				
				try:
					model = get_classification_model()
					similarity_score, distance = model.compute_similarity(tmp_path, reference_image_path)
					
					threshold = 0.45
					is_same = distance < threshold
					
					# Generate comparison visualization
					comparison_image = self._create_comparison_overlay(tmp_path, reference_image_path)
					
					# Convert to base64 for response
					buffered = BytesIO()
					comparison_image.save(buffered, format="PNG")
					comparison_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
					
					# Save comparison image to file for database
					comparison_file = ContentFile(buffered.getvalue(), name=f'comparison_{target_class}.png')
					
					# Save to database
					similarity_history = SimilarityHistory.objects.create(
						user=request.user,
						user_image=image_file,
						target_class=target_class,
						similarity_score=similarity_score,
						distance=distance,
						is_same_character=is_same,
						comparison_image=comparison_file
					)
					
					return Response({
						'success': True,
						'history_id': similarity_history.id, # comment if no history
						'similarity_score': round(similarity_score, 2),
						'distance': round(distance, 4),
						'is_same_character': is_same,
						'threshold': threshold,
						'compared_with_class': target_class,
						'comparison_image': f'data:image/png;base64,{comparison_base64}'
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



class PredictionHistoryView(APIView):
	"""Get user's prediction history"""
	permission_classes = [IsAuthenticated]
	
	def get(self, request):
		"""Get all predictions for the current user"""
		predictions = PredictionHistory.objects.filter(user=request.user)
		
		data = [{
			'id': pred.id,
			'image_url': request.build_absolute_uri(pred.image.url) if pred.image else None,
			'predicted_class': pred.predicted_class,
			'confidence': round(pred.confidence, 2),
			'created_at': pred.created_at.isoformat()
		} for pred in predictions]
		
		return Response({
			'success': True,
			'count': len(data),
			'predictions': data
		}, status=status.HTTP_200_OK)


class SimilarityHistoryView(APIView):
	"""Get user's similarity comparison history"""
	permission_classes = [IsAuthenticated]
	
	def get(self, request):
		"""Get all similarity comparisons for the current user"""
		similarities = SimilarityHistory.objects.filter(user=request.user)
		
		data = [{
			'id': sim.id,
			'user_image_url': request.build_absolute_uri(sim.user_image.url) if sim.user_image else None,
			'comparison_image_url': request.build_absolute_uri(sim.comparison_image.url) if sim.comparison_image else None,
			'target_class': sim.target_class,
			'similarity_score': round(sim.similarity_score, 2),
			'distance': round(sim.distance, 4),
			'is_same_character': sim.is_same_character,
			'created_at': sim.created_at.isoformat()
		} for sim in similarities]
		
		return Response({
			'success': True,
			'count': len(data),
			'similarities': data
		}, status=status.HTTP_200_OK)
	
	
# class GradCAMView(APIView):
# 	permission_classes = [IsAuthenticated]
# 	parser_classes = [MultiPartParser, FormParser]
	
# 	def post(self, request):
# 		serializer = GradCAMSerializer(data=request.data)
# 		if serializer.is_valid():
# 			try:
# 				from .ml_models import get_classification_model
				
# 				image_file = serializer.validated_data['image']
# 				target_class = serializer.validated_data.get('target_class', None)
				
# 				with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
# 					tmp.write(image_file.read())
# 					tmp_path = tmp.name
				
# 				gradcam_path = tmp_path.replace('.png', '_gradcam.png')
				
# 				try:
# 					model = get_classification_model()
# 					result = model.generate_gradcam(tmp_path, target_class=target_class, save_path=gradcam_path)
					
# 					with open(gradcam_path, 'rb') as f:
# 						gradcam_base64 = base64.b64encode(f.read()).decode('utf-8')
					
# 					return Response({
# 						'success': True,
# 						'predicted_class': result['predicted_class'],
# 						'confidence': round(result['confidence'] * 100, 2),
# 						'gradcam_image': f'data:image/png;base64,{gradcam_base64}'
# 					}, status=status.HTTP_200_OK)
				
# 				finally:
# 					if os.path.exists(tmp_path):
# 						os.unlink(tmp_path)
# 					if os.path.exists(gradcam_path):
# 						os.unlink(gradcam_path)
			
# 			except Exception as e:
# 				return Response({
# 					'success': False,
# 					'error': str(e)
# 				}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
		
# 		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




