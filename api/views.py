from django.http import HttpResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from rest_framework_simplejwt.tokens import RefreshToken
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .serializers import SignupSerializer, SigninSerializer, ImageSerializer, SimilaritySerializer, FeedbackSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from io import BytesIO
from PIL import Image, ImageOps
import tempfile
import os
import base64
import numpy as np
import cv2 as cv
from django.core.files.base import ContentFile
from .models import PredictionHistory, SimilarityHistory
import google.generativeai as genai
from django.conf import settings
from django.db.models import Avg, Count, Max, Q
from datetime import datetime, timedelta

# Use HuggingFace Space API instead of local models
_hf_client = None
_use_hf_api = None
_reference_image_cache = {}  # Cache for reference images

def get_ml_client():
	global _hf_client, _use_hf_api
	if _hf_client is None:
		# Check if we should use HF or local models
		_use_hf_api = os.getenv('USE_HUGGINGFACE_API', 'False') == 'True'
		if _use_hf_api:
			from .ml_models.hf_client import get_hf_client
			_hf_client = get_hf_client()
		else:
			# Fallback to local models
			from .ml_models import get_classification_model
			_hf_client = get_classification_model()
	return _hf_client

def is_using_hf_api():
	"""Check if using HuggingFace API"""
	global _use_hf_api
	if _use_hf_api is None:
		_use_hf_api = os.getenv('USE_HUGGINGFACE_API', 'False') == 'True'
	return _use_hf_api

def get_reference_image_path(target_class):
	"""Get reference image path with validation"""
	reference_images_dir = os.path.join(settings.BASE_DIR, 'api', 'reference_images')
	reference_image_path = os.path.join(reference_images_dir, f'class_{target_class}.png')
	return reference_image_path if os.path.exists(reference_image_path) else None

@method_decorator(csrf_exempt, name='dispatch')
class SignupView(APIView):
	permission_classes = [AllowAny]
	def post(self, request):
		serializer = SignupSerializer(data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response({'message': 'User created successfully.'}, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@method_decorator(csrf_exempt, name='dispatch')
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


def preprocess_image(image_path):
	try:
		# Read image
		img = cv.imread(image_path)
		if img is None:
			raise ValueError(f"Error: Could not read image from {image_path}")
		
		# Convert to grayscale
		img_gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
		
		# Threshold: white letter on black background
		_, thresh = cv.threshold(img_gray, 0, 255, cv.THRESH_BINARY_INV + cv.THRESH_OTSU)
		
		# Optional clean-up: remove tiny dots or gaps
		kernel = np.ones((2, 2), np.uint8)
		thresh = cv.erode(thresh, kernel, iterations=1)
		
		# Find contours
		contours, _ = cv.findContours(thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
		if not contours:
			raise ValueError("No contours found in image")
		
		# Filter out very small areas (noise)
		filtered = [c for c in contours if cv.contourArea(c) > 100]
		if not filtered:
			raise ValueError("No significant contours found after filtering")
		
		# Selective merging: keep contours that are near the largest one
		main_contour = max(filtered, key=cv.contourArea)
		x_main, y_main, w_main, h_main = cv.boundingRect(main_contour)
		main_box = np.array([x_main, y_main, x_main + w_main, y_main + h_main])
		
		close_contours = [main_contour]
		
		for cnt in filtered:
			if cnt is main_contour:
				continue
			x, y, w, h = cv.boundingRect(cnt)
			# Compute overlap or closeness
			if not (x + w < main_box[0] - 10 or x > main_box[2] + 10 or
					y + h < main_box[1] - 10 or y > main_box[3] + 10):
				close_contours.append(cnt)
		
		# Merge selected contours
		all_points = np.vstack(close_contours)
		
		# Get bounding box around merged contours
		x, y, w, h = cv.boundingRect(all_points)
		
		# Crop the region
		cropped = thresh[y:y+h, x:x+w]
		
		# Center the cropped region in a square
		side = max(w, h)
		square = np.zeros((side, side), dtype=np.uint8)
		start_x = (side - w) // 2
		start_y = (side - h) // 2
		square[start_y:start_y+h, start_x:start_x+w] = cropped
		
		# Resize to 64x64
		resized = cv.resize(square, (64, 64), interpolation=cv.INTER_AREA)
		
		# Save processed image to temporary file
		with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_processed:
			processed_path = tmp_processed.name
			cv.imwrite(processed_path, resized)
		
		# Convert to base64 for frontend
		_, buffer = cv.imencode('.png', resized)
		img_base64 = base64.b64encode(buffer).decode('utf-8')
		
		return processed_path, img_base64
	
	except Exception as e:
		# If preprocessing fails, return original image
		print(f"Preprocessing error: {str(e)}. Using original image.")
		img = Image.open(image_path)
		buffered = BytesIO()
		img.save(buffered, format="PNG")
		img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
		return image_path, img_base64
		# Fallback: minimal preprocessing
		print(f"Preprocessing error: {str(e)}. Using fallback.")
		try:
			img = cv.imread(image_path, cv.IMREAD_GRAYSCALE)
			if img is None:
				raise
			# Apply threshold and resize without cropping
			_, thresh = cv.threshold(img, 0, 255, cv.THRESH_BINARY_INV + cv.THRESH_OTSU)
			resized = cv.resize(thresh, (64, 64), interpolation=cv.INTER_AREA)
			_, buffer = cv.imencode('.png', resized)
			img_base64 = base64.b64encode(buffer.tobytes()).decode('utf-8')
			
			# Save fallback
			with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_processed:
				fallback_path = tmp_processed.name
				cv.imwrite(fallback_path, resized)
			
			return fallback_path, img_base64
		except:
			# Ultimate fallback - just resize original
			img = Image.open(image_path).convert('L')
			img = img.resize((64, 64), Image.Resampling.LANCZOS)
			buffered = BytesIO()
			img.save(buffered, format="PNG")
			img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
			return image_path, img_base64


class FeedbackView(APIView):
	permission_classes = [IsAuthenticated]
	parser_classes = [MultiPartParser, FormParser]
	
	def gemini_api_request(self, image_path, prompt):
		try:
			# Configure Gemini API
			api_key = os.getenv('GEMINI_API_KEY')
			if not api_key:
				raise ValueError("GEMINI_API_KEY not found in environment variables")
			
			genai.configure(api_key=api_key)
			
			# Use gemini-pro-vision for image analysis
			model = genai.GenerativeModel('gemini-2.5-flash')
			
			img = Image.open(image_path)
			try:
				response = model.generate_content([prompt, img])
				result = response.text
			finally:
				img.close() 
			
			return result
		
		except Exception as e:
			raise Exception(f"Gemini API request failed: {str(e)}")
	
	def post(self, request):
		serializer = FeedbackSerializer(data=request.data)
		if serializer.is_valid():
			try:
				# Extract base64 images and decode them
				user_image_base64 = serializer.validated_data['user_image'].replace('data:image/png;base64,', '')
				reference_image_base64 = serializer.validated_data['reference_image'].replace('data:image/png;base64,', '')
				blended_overlay_base64 = serializer.validated_data['blended_overlay'].replace('data:image/png;base64,', '')
				
				target_class = serializer.validated_data['target_class']
				similarity_score = serializer.validated_data['similarity_score']
				distance = serializer.validated_data['distance']
				is_same_character = serializer.validated_data['is_same_character']
				
				# Decode blended image for Gemini API
				blended_image_data = base64.b64decode(blended_overlay_base64)
				
				with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
					tmp.write(blended_image_data)
					tmp_path = tmp.name
				
				try:
					prompt = (
						"Analyze the attached blended image (white=reference, blackish=input). "
						"Provide only an actionable feedback summary. The summary must consist of "
						"a general assessment sentence followed by a list of 4 specific focus points "
						"for correction in the next attempt. Format the response as follows:<br><br>"
						"[General assessment sentence]<br><br>"
						"Focus points for correction:<br>"
						"1. [First point]<br>"
						"2. [Second point]<br>"
						"3. [Third point]<br>"
						"4. [Fourth point]<br><br>"
						"Do not provide a detailed section-by-section analysis or any introductory/closing remarks."
					)
					
					feedback = self.gemini_api_request(tmp_path, prompt)
					
					# Save to history if user is authenticated
					if request.user.is_authenticated:
						# Convert base64 back to image files for storage
						user_image_data = base64.b64decode(user_image_base64)
						reference_image_data = base64.b64decode(reference_image_base64)
						
						user_image_content = ContentFile(user_image_data, name=f'user_{target_class}.png')
						ref_image_content = ContentFile(reference_image_data, name=f'ref_{target_class}.png')
						blended_image_content = ContentFile(blended_image_data, name=f'blended_{target_class}.png')
						
						SimilarityHistory.objects.create(
							user=request.user,
							user_image=user_image_content,
							reference_image=ref_image_content,
							target_class=target_class,
							similarity_score=similarity_score,
							distance=distance,
							is_same_character=is_same_character,
							blended_overlay=blended_image_content,
							feedback=feedback
						)
					
					return Response({
						'success': True,
						'feedback': feedback
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
class PredictView(APIView):
	permission_classes = [IsAuthenticated]
	parser_classes = [MultiPartParser, FormParser]
	
	def post(self, request):
		serializer = ImageSerializer(data=request.data)
		if serializer.is_valid():
			try:
				
				image_file = serializer.validated_data['image']

				with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
					tmp.write(image_file.read())
					tmp_path = tmp.name
				
				try:
					model = get_ml_client()
					
					if is_using_hf_api():
						# HF Space now has OpenCV preprocessing - send original image
						processed_image_path = tmp_path
						# Still generate base64 for frontend display
						img = Image.open(tmp_path)
						buffered = BytesIO()
						img.save(buffered, format="PNG")
						processed_image_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
						
						result = model.predict(processed_image_path, top_k=1)
					else:
						# Local model - do OpenCV preprocessing locally
						processed_image_path, processed_image_base64 = preprocess_image(tmp_path)
						result = model.predict(processed_image_path, top_k=1, skip_preprocessing=True)
					
					predicted_class = result['class']
					
					if predicted_class < 0 or predicted_class > 35:
						return Response({
							'success': False,
							'error': f'Model predicted invalid class {predicted_class}. Expected 0-35.'
						}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
					
					# Save to history if user is authenticated
					# Convert confidence from 0-1 to 0-100 if needed
					confidence = result['confidence']
					if confidence <= 1.0:
						confidence = confidence * 100
					
					if request.user.is_authenticated:
						prediction_history = PredictionHistory.objects.create(
							user=request.user,
							image=image_file,
							predicted_class=predicted_class,
							confidence=confidence
						)
					
					return Response({
						'success': True,
						'predicted_class': predicted_class,
						'confidence': round(confidence, 2),
						'processed_image': f'data:image/png;base64,{processed_image_base64}',
					}, status=status.HTTP_200_OK)
				
				finally:
					if os.path.exists(tmp_path):
						os.unlink(tmp_path)
					if 'processed_image_path' in locals() and processed_image_path != tmp_path and os.path.exists(processed_image_path):
						os.unlink(processed_image_path)
			
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
		"""Create comparison overlay with preprocessed user image and original reference"""
		# Preprocess only user image
		user_processed_path, _ = preprocess_image(user_image_path)
		
		# Open preprocessed user and original reference
		user_img = Image.open(user_processed_path).convert('L')
		ref_img = Image.open(reference_image_path).convert('L')
		
		# Invert user image
		user_img = ImageOps.invert(user_img)
		
		# Resize to display size
		size = (256, 256)
		user_img = user_img.resize(size, Image.Resampling.LANCZOS)
		ref_img = ref_img.resize(size, Image.Resampling.LANCZOS)
		
		# Create display versions
		ref_output = ref_img.convert('RGB')
		user_output = user_img.convert('RGB')
		
		# Create overlay
		ref_rgba = ref_img.convert('RGBA')
		user_rgba = user_img.convert('RGBA')
		blended = Image.new('RGBA', size, (255, 255, 255, 255))
		
		# Reference layer (full opacity)
		ref_with_alpha = Image.new('RGBA', size, (255, 255, 255, 0))
		ref_with_alpha.paste(ref_rgba, (0, 0))
		ref_array = np.array(ref_with_alpha)
		ref_array[:, :, 3] = (255 - ref_array[:, :, 0]) * 1
		ref_with_alpha = Image.fromarray(ref_array.astype('uint8'), 'RGBA')
		blended = Image.alpha_composite(blended, ref_with_alpha)
		
		# User layer (80% opacity)
		user_with_alpha = Image.new('RGBA', size, (255, 255, 255, 0))
		user_with_alpha.paste(user_rgba, (0, 0))
		user_array = np.array(user_with_alpha)
		user_array[:, :, 3] = (255 - user_array[:, :, 0]) * 0.8
		user_with_alpha = Image.fromarray(user_array.astype('uint8'), 'RGBA')
		blended = Image.alpha_composite(blended, user_with_alpha)
		
		blended_output = blended.convert('RGB')
		
		# Clean up temp file
		try:
			os.unlink(user_processed_path)
		except:
			pass
		
		return ref_output, user_output, blended_output
	
	def post(self, request):
		serializer = SimilaritySerializer(data=request.data)
		if serializer.is_valid():
			try:
				target_class = serializer.validated_data['target_class']
				processed_image_base64 = serializer.validated_data.get('processed_image_base64')
				image_file = serializer.validated_data.get('image')
				
				if target_class < 0 or target_class > 35:
					return Response({
						'success': False,
						'error': f'Invalid target_class {target_class}. Model supports classes 0-35 only.'
					}, status=status.HTTP_400_BAD_REQUEST)
				
				# Use helper function for reference image
				reference_image_path = get_reference_image_path(target_class)
				if not reference_image_path:
					return Response({
						'success': False,
						'error': f'Reference image for class {target_class} not found.'
					}, status=status.HTTP_404_NOT_FOUND)
				
				# Use processed image if provided, otherwise process the uploaded image
				if processed_image_base64:
					# Decode base64 and save to temp file
					import base64 as b64
					image_data = b64.b64decode(processed_image_base64)
					with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
						tmp.write(image_data)
						tmp_path = tmp.name
				else:
					# Process the uploaded image
					with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
						tmp.write(image_file.read())
						tmp_path = tmp.name
				
				try:
					model = get_ml_client()
					
					if is_using_hf_api():
						# HF Space returns everything: score, distance, and all images
						similarity_score, distance, ref_img, user_img, blended_img = model.compute_similarity(
							tmp_path, 
							reference_image_path
						)
						# Ensure they are PIL Images
						if not isinstance(ref_img, Image.Image):
							raise ValueError(f"HF API returned invalid ref_img type: {type(ref_img)}")
						if not isinstance(user_img, Image.Image):
							raise ValueError(f"HF API returned invalid user_img type: {type(user_img)}")
						if not isinstance(blended_img, Image.Image):
							raise ValueError(f"HF API returned invalid blended_img type: {type(blended_img)}")
					else:
						# Local model - images already preprocessed, skip ML preprocessing
						similarity_score, distance = model.compute_similarity(
							tmp_path, 
							reference_image_path,
							skip_preprocessing=True
						)
						# Create overlay locally
						ref_img, user_img, blended_img = self._create_comparison_overlay(tmp_path, reference_image_path)
					
					threshold = 0.45
					is_same = distance < threshold
					ref_buffered = BytesIO()
					ref_img.save(ref_buffered, format="PNG")
					ref_base64 = base64.b64encode(ref_buffered.getvalue()).decode('utf-8')
					user_buffered = BytesIO()
					user_img.save(user_buffered, format="PNG")
					user_base64 = base64.b64encode(user_buffered.getvalue()).decode('utf-8')
					blended_buffered = BytesIO()
					blended_img.save(blended_buffered, format="PNG")
					blended_base64 = base64.b64encode(blended_buffered.getvalue()).decode('utf-8')
					
					return Response({
						'success': True,
						'similarity_score': round(similarity_score, 2),
						'distance': round(distance, 4),
						'is_same_character': is_same,
						'threshold': threshold,
						'compared_with_class': target_class,
						'reference_image': f'data:image/png;base64,{ref_base64}',
						'user_image': f'data:image/png;base64,{user_base64}',
						'gradcam_image': f'data:image/png;base64,{blended_base64}',
						'blended_overlay': f'data:image/png;base64,{blended_base64}',
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
	permission_classes = [IsAuthenticated]
	
	def get(self, request):
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
	permission_classes = [IsAuthenticated]
	
	def get(self, request):
		similarities = SimilarityHistory.objects.filter(user=request.user)
		
		data = [{
			'id': sim.id,
			'user_image_url': request.build_absolute_uri(sim.user_image.url) if sim.user_image else None,
			'reference_image_url': request.build_absolute_uri(sim.reference_image.url) if sim.reference_image else None,
			'blended_overlay_url': request.build_absolute_uri(sim.blended_overlay.url) if sim.blended_overlay else None,
			'target_class': sim.target_class,
			'similarity_score': round(sim.similarity_score, 2),
			'distance': round(sim.distance, 4),
			'is_same_character': sim.is_same_character,
			'feedback': sim.feedback,
			'created_at': sim.created_at.isoformat()
		} for sim in similarities]
		
		return Response({
			'success': True,
			'count': len(data),
			'similarities': data
		}, status=status.HTTP_200_OK)
	
	def delete(self, request, history_id=None):
		try:
			if not history_id:
				return Response({
					'success': False,
					'error': 'History ID is required'
				}, status=status.HTTP_400_BAD_REQUEST)
			
			history_item = SimilarityHistory.objects.get(id=history_id, user=request.user)
			
			# Delete associated image files from storage
			if history_item.user_image:
				if os.path.isfile(history_item.user_image.path):
					os.remove(history_item.user_image.path)
			
			if history_item.reference_image:
				if os.path.isfile(history_item.reference_image.path):
					os.remove(history_item.reference_image.path)
			
			if history_item.blended_overlay:
				if os.path.isfile(history_item.blended_overlay.path):
					os.remove(history_item.blended_overlay.path)
			
			# Delete the database record
			history_item.delete()
			
			return Response({
				'success': True,
				'message': 'History item deleted successfully'
			}, status=status.HTTP_200_OK)
			
		except SimilarityHistory.DoesNotExist:
			return Response({
				'success': False,
				'error': 'History item not found'
			}, status=status.HTTP_404_NOT_FOUND)
		except Exception as e:
			return Response({
				'success': False,
				'error': str(e)
			}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserStatisticsView(APIView):
	permission_classes = [IsAuthenticated]
	
	def get(self, request):
		try:
			target_class = request.query_params.get('target_class')
			days = request.query_params.get('days')
			start_date = request.query_params.get('start_date')
			end_date = request.query_params.get('end_date')
			
			similarities = SimilarityHistory.objects.filter(user=request.user)
			
			if target_class is not None:
				try:
					target_class = int(target_class)
					similarities = similarities.filter(target_class=target_class)
				except (ValueError, TypeError):
					return Response({
						'success': False,
						'error': 'Invalid target_class parameter'
					}, status=status.HTTP_400_BAD_REQUEST)
			
			if days:
				try:
					days = int(days)
					cutoff_date = datetime.now() - timedelta(days=days)
					similarities = similarities.filter(created_at__gte=cutoff_date)
				except (ValueError, TypeError):
					return Response({
						'success': False,
						'error': 'Invalid days parameter'
					}, status=status.HTTP_400_BAD_REQUEST)
			
			if start_date:
				try:
					start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
					similarities = similarities.filter(created_at__gte=start)
				except (ValueError, TypeError):
					return Response({
						'success': False,
						'error': 'Invalid start_date parameter (use ISO format)'
					}, status=status.HTTP_400_BAD_REQUEST)
			
			if end_date:
				try:
					end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
					similarities = similarities.filter(created_at__lte=end)
				except (ValueError, TypeError):
					return Response({
						'success': False,
						'error': 'Invalid end_date parameter (use ISO format)'
					}, status=status.HTTP_400_BAD_REQUEST)
			
			total_count = similarities.count()
			
			if total_count == 0:
				return Response({
					'success': True,
					'statistics': {
						'total_analyses': 0,
						'average_score': 0,
						'match_rate': 0,
						'best_score': 0,
						'total_matches': 0,
						'total_mismatches': 0,
						'most_practiced_character': None,
						'characters_attempted': 0,
						'high_scores': 0,
						'good_scores': 0,
						'needs_practice': 0,
						'recent_activity': None
					}
				}, status=status.HTTP_200_OK)
			
			# Basic statistics
			avg_score = similarities.aggregate(Avg('similarity_score'))['similarity_score__avg'] or 0
			best_score = similarities.aggregate(Max('similarity_score'))['similarity_score__max'] or 0
			total_matches = similarities.filter(is_same_character=True).count()
			total_mismatches = similarities.filter(is_same_character=False).count()
			match_rate = (total_matches / total_count * 100) if total_count > 0 else 0
			
			# Character statistics
			character_counts = similarities.values('target_class').annotate(count=Count('id')).order_by('-count')
			most_practiced = character_counts.first()['target_class'] if character_counts else None
			characters_attempted = similarities.values('target_class').distinct().count()
			
			# Score distribution
			high_scores = similarities.filter(similarity_score__gte=90).count()
			good_scores = similarities.filter(similarity_score__gte=75, similarity_score__lt=90).count()
			needs_practice = similarities.filter(similarity_score__lt=75).count()
			
			# Recent activity
			last_analysis = similarities.order_by('-created_at').first()
			recent_activity = last_analysis.created_at.isoformat() if last_analysis else None
			
			return Response({
				'success': True,
				'statistics': {
					'total_analyses': total_count,
					'average_score': round(avg_score, 2),
					'match_rate': round(match_rate, 2),
					'best_score': round(best_score, 2),
					'total_matches': total_matches,
					'total_mismatches': total_mismatches,
					'most_practiced_character': most_practiced,
					'characters_attempted': characters_attempted,
					'high_scores': high_scores,
					'good_scores': good_scores,
					'needs_practice': needs_practice,
					'recent_activity': recent_activity
				}
			}, status=status.HTTP_200_OK)
			
		except Exception as e:
			return Response({
				'success': False,
				'error': str(e)
			}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
	
	
