from django.http import HttpResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import SignupSerializer, SigninSerializer, ImageSerializer, SimilaritySerializer
from rest_framework.parsers import MultiPartParser, FormParser
from io import BytesIO
from PIL import Image, ImageOps
import tempfile
import os
import base64
import numpy as np
from django.core.files.base import ContentFile
from .models import PredictionHistory, SimilarityHistory

from .ml_models import get_classification_model

class SignupView(APIView):
	permission_classes = [AllowAny]
	def post(self, request):
		serializer = SignupSerializer(data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response({'message': 'User created successfully.'}, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



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
			try:
				from .ml_models import get_classification_model
				
				image_file = serializer.validated_data['image']

				with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
					tmp.write(image_file.read())
					tmp_path = tmp.name
				
				try:
					model = get_classification_model()
					result = model.predict(tmp_path, top_k=1)
					
					predicted_class = result['class']
					
					if predicted_class < 0 or predicted_class > 35:
						return Response({
							'success': False,
							'error': f'Model predicted invalid class {predicted_class}. Expected 0-35.'
						}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
					
					# Save to database
					# prediction = PredictionHistory.objects.create(
					# 	user=request.user,
					# 	image=image_file,
					# 	predicted_class=result['class'],
					# 	confidence=result['confidence']
					# )
					
					return Response({
						'success': True,
						# 'prediction_id': prediction.id,
						'predicted_class': predicted_class,
						'confidence': round(result['confidence'], 2),
						'note': 'Model trained on 36 classes (0-35)'
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
	permission_classes = [AllowAny]
	parser_classes = [MultiPartParser, FormParser]
	
	def _create_comparison_overlay(self, user_image_path, reference_image_path):
		# Load images
		user_img = Image.open(user_image_path).convert('L')
		ref_img = Image.open(reference_image_path).convert('L')
		# Resize to same dimensions
		size = (256, 256)
		user_img = user_img.resize(size, Image.Resampling.LANCZOS)
		ref_img = ref_img.resize(size, Image.Resampling.LANCZOS)
		# Convert to RGB for output
		ref_output = ref_img.convert('RGB')
		user_output = user_img.convert('RGB')
		# Convert to RGBA for alpha blending
		ref_rgba = ref_img.convert('RGBA')
		user_rgba = user_img.convert('RGBA')
		# Create a white background
		blended = Image.new('RGBA', size, (255, 255, 255, 255))
		# Apply reference image with high opacity (80%)
		ref_with_alpha = Image.new('RGBA', size, (255, 255, 255, 0))
		ref_with_alpha.paste(ref_rgba, (0, 0))
		# Adjust alpha channel for reference (high opacity = 204 out of 255)
		ref_array = np.array(ref_with_alpha)
		ref_array[:, :, 3] = (255 - ref_array[:, :, 0]) * 0.8  # 80% opacity on strokes
		ref_with_alpha = Image.fromarray(ref_array.astype('uint8'), 'RGBA')
		# Blend reference onto background
		blended = Image.alpha_composite(blended, ref_with_alpha)
		# Apply user image with low opacity (30%)
		user_with_alpha = Image.new('RGBA', size, (255, 255, 255, 0))
		user_with_alpha.paste(user_rgba, (0, 0))
		# Adjust alpha channel for user input (low opacity = 76 out of 255)
		user_array = np.array(user_with_alpha)
		user_array[:, :, 3] = (255 - user_array[:, :, 0]) * 0.3  # 30% opacity on strokes
		user_with_alpha = Image.fromarray(user_array.astype('uint8'), 'RGBA')
		# Blend user input on top
		blended = Image.alpha_composite(blended, user_with_alpha)
		# Convert back to RGB for display
		blended_output = blended.convert('RGB')
		# Return all three images as tuple
		return ref_output, user_output, blended_output
	
	def post(self, request):
		serializer = SimilaritySerializer(data=request.data)
		if serializer.is_valid():
			try:
				from .ml_models import get_classification_model
				from django.conf import settings
				
				image_file = serializer.validated_data['image']
				target_class = serializer.validated_data['target_class']
				
				if target_class < 0 or target_class > 35:
					return Response({
						'success': False,
						'error': f'Invalid target_class {target_class}. Model supports classes 0-35 only.'
					}, status=status.HTTP_400_BAD_REQUEST)
				
				reference_images_dir = os.path.join(settings.BASE_DIR, 'api', 'reference_images')
				reference_image_path = os.path.join(reference_images_dir, f'class_{target_class}.png')
				
				if not os.path.exists(reference_image_path):
					return Response({
						'success': False,
						'error': f'Reference image for class {target_class} not found. Please ensure reference images exist for classes 0-35.'
					}, status=status.HTTP_404_NOT_FOUND)
				
				with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
					tmp.write(image_file.read())
					tmp_path = tmp.name
				
				try:
					model = get_classification_model()
					similarity_score, distance = model.compute_similarity(tmp_path, reference_image_path)
					
					threshold = 0.45
					is_same = distance < threshold
					
					# Get all three images: reference, user, and blended overlay
					ref_img, user_img, blended_img = self._create_comparison_overlay(tmp_path, reference_image_path)
					# Convert reference image to base64
					ref_buffered = BytesIO()
					ref_img.save(ref_buffered, format="PNG")
					ref_base64 = base64.b64encode(ref_buffered.getvalue()).decode('utf-8')
					# Convert user image to base64
					user_buffered = BytesIO()
					user_img.save(user_buffered, format="PNG")
					user_base64 = base64.b64encode(user_buffered.getvalue()).decode('utf-8')
					# Convert blended overlay to base64
					blended_buffered = BytesIO()
					blended_img.save(blended_buffered, format="PNG")
					blended_base64 = base64.b64encode(blended_buffered.getvalue()).decode('utf-8')
					# Create ContentFile objects for saving
					user_file = ContentFile(user_buffered.getvalue(), name=f'user_{target_class}.png')
					ref_file = ContentFile(ref_buffered.getvalue(), name=f'ref_{target_class}.png')
					blended_file = ContentFile(blended_buffered.getvalue(), name=f'blended_{target_class}.png')
					
					# similarity_history = SimilarityHistory.objects.create(
					# 	user=request.user,
					# 	user_image=user_file,
					# 	reference_image=ref_file,
					# 	target_class=target_class,
					# 	similarity_score=similarity_score,
					# 	distance=distance,
					# 	is_same_character=is_same,
					# 	blended_overlay=blended_file
					# )
					
					return Response({
						'success': True,
						# 'history_id': similarity_history.id, # comment if no history
						'similarity_score': round(similarity_score, 2),
						'distance': round(distance, 4),
						'is_same_character': is_same,
						'threshold': threshold,
						'compared_with_class': target_class,
						'reference_image': f'data:image/png;base64,{ref_base64}',
						'user_image': f'data:image/png;base64,{user_base64}',
						'blended_overlay': f'data:image/png;base64,{blended_base64}',
						'note': 'Model trained on 36 classes (0-35)'
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



# class PredictionHistoryView(APIView):
# 	permission_classes = [IsAuthenticated]
	
# 	def get(self, request):
# 		predictions = PredictionHistory.objects.filter(user=request.user)
		
# 		data = [{
# 			'id': pred.id,
# 			'image_url': request.build_absolute_uri(pred.image.url) if pred.image else None,
# 			'predicted_class': pred.predicted_class,
# 			'confidence': round(pred.confidence, 2),
# 			'created_at': pred.created_at.isoformat()
# 		} for pred in predictions]
		
# 		return Response({
# 			'success': True,
# 			'count': len(data),
# 			'predictions': data
# 		}, status=status.HTTP_200_OK)


# class SimilarityHistoryView(APIView):
# 	permission_classes = [IsAuthenticated]
	
# 	def get(self, request):
# 		similarities = SimilarityHistory.objects.filter(user=request.user)
		
# 		data = [{
# 			'id': sim.id,
# 			'user_image_url': request.build_absolute_uri(sim.user_image.url) if sim.user_image else None,
# 			'reference_image_url': request.build_absolute_uri(sim.reference_image.url) if sim.reference_image else None,
# 			'blended_overlay_url': request.build_absolute_uri(sim.blended_overlay.url) if sim.blended_overlay else None,
# 			'target_class': sim.target_class,
# 			'similarity_score': round(sim.similarity_score, 2),
# 			'distance': round(sim.distance, 4),
# 			'is_same_character': sim.is_same_character,
# 			'created_at': sim.created_at.isoformat()
# 		} for sim in similarities]
		
# 		return Response({
# 			'success': True,
# 			'count': len(data),
# 			'similarities': data
# 		}, status=status.HTTP_200_OK)
	
	