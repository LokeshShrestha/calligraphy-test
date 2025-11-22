
import os
import tempfile
import base64
import numpy as np
import cv2 as cv
from PIL import Image, ImageOps
from io import BytesIO
from celery import shared_task
from django.core.files.base import ContentFile
from django.conf import settings

from .ml_models import get_classification_model
from .models import PredictionHistory, SimilarityHistory


def preprocess_image(image_path):
    try:
        img = cv.imread(image_path)
        if img is None:
            raise ValueError(f"Error: Could not read image from {image_path}")
        
        img_gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        
        _, thresh = cv.threshold(img_gray, 0, 255, cv.THRESH_BINARY_INV + cv.THRESH_OTSU)
        
        kernel = np.ones((2, 2), np.uint8)
        thresh = cv.erode(thresh, kernel, iterations=1)
        
        contours, _ = cv.findContours(thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        if not contours:
            raise ValueError("No contours found in image")
        
        filtered = [c for c in contours if cv.contourArea(c) > 100]
        if not filtered:
            raise ValueError("No significant contours found after filtering")
        
        main_contour = max(filtered, key=cv.contourArea)
        x_main, y_main, w_main, h_main = cv.boundingRect(main_contour)
        main_box = np.array([x_main, y_main, x_main + w_main, y_main + h_main])
        
        close_contours = [main_contour]
        
        for cnt in filtered:
            if cnt is main_contour:
                continue
            x, y, w, h = cv.boundingRect(cnt)
            if not (x + w < main_box[0] - 10 or x > main_box[2] + 10 or
                    y + h < main_box[1] - 10 or y > main_box[3] + 10):
                close_contours.append(cnt)
        
        all_points = np.vstack(close_contours)
        
        x, y, w, h = cv.boundingRect(all_points)
        
        cropped = thresh[y:y+h, x:x+w]
        
        side = max(w, h)
        square = np.zeros((side, side), dtype=np.uint8)
        start_x = (side - w) // 2
        start_y = (side - h) // 2
        square[start_y:start_y+h, start_x:start_x+w] = cropped

        resized = cv.resize(square, (64, 64), interpolation=cv.INTER_AREA)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_processed:
            processed_path = tmp_processed.name
            cv.imwrite(processed_path, resized)
        
        _, buffer = cv.imencode('.png', resized)
        img_base64 = base64.b64encode(buffer).decode('utf-8')
        
        return processed_path, img_base64
    
    except Exception as e:
        print(f"Preprocessing error: {str(e)}. Using original image.")
        img = Image.open(image_path)
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
        return image_path, img_base64


@shared_task(name='api.tasks.predict_character')
def predict_character(image_data):
    tmp_path = None
    processed_image_path = None
    
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
            if isinstance(image_data, str) and image_data.startswith('data:image'):
              
                format, imgstr = image_data.split(';base64,')
                image_bytes = base64.b64decode(imgstr)
                tmp.write(image_bytes)
            else:
                tmp.write(image_data)
            tmp_path = tmp.name
        
        processed_image_path, processed_image_base64 = preprocess_image(tmp_path)
        
        model = get_classification_model()
        result = model.predict(processed_image_path, top_k=1)
        
        predicted_class = result['class']
        
        if predicted_class < 0 or predicted_class > 35:
            raise ValueError(f'Model predicted invalid class {predicted_class}. Expected 0-35.')
        
        return {
            'success': True,
            'predicted_class': predicted_class,
            'confidence': round(result['confidence'], 2),
            'processed_image': f'data:image/png;base64,{processed_image_base64}',
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
    
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)
        if processed_image_path and processed_image_path != tmp_path and os.path.exists(processed_image_path):
            os.unlink(processed_image_path)


def create_comparison_overlay(user_image_path, reference_image_path):
    user_img = Image.open(user_image_path).convert('L')
    ref_img = Image.open(reference_image_path).convert('L')
    
    user_img = ImageOps.invert(user_img)
    
    size = (256, 256)
    user_img = user_img.resize(size, Image.Resampling.LANCZOS)
    ref_img = ref_img.resize(size, Image.Resampling.LANCZOS)
    ref_output = ref_img.convert('RGB')
    user_output = user_img.convert('RGB')
    ref_rgba = ref_img.convert('RGBA')
    user_rgba = user_img.convert('RGBA')
    blended = Image.new('RGBA', size, (255, 255, 255, 255))
    ref_with_alpha = Image.new('RGBA', size, (255, 255, 255, 0))
    ref_with_alpha.paste(ref_rgba, (0, 0))
    ref_array = np.array(ref_with_alpha)
    ref_array[:, :, 3] = (255 - ref_array[:, :, 0]) * 1  # 50% opacity on strokes
    ref_with_alpha = Image.fromarray(ref_array.astype('uint8'), 'RGBA')
    blended = Image.alpha_composite(blended, ref_with_alpha)
    user_with_alpha = Image.new('RGBA', size, (255, 255, 255, 0))
    user_with_alpha.paste(user_rgba, (0, 0))
    user_array = np.array(user_with_alpha)
    user_array[:, :, 3] = (255 - user_array[:, :, 0]) * 0.8  # 80% opacity on strokes
    user_with_alpha = Image.fromarray(user_array.astype('uint8'), 'RGBA')
    blended = Image.alpha_composite(blended, user_with_alpha)
    blended_output = blended.convert('RGB')
    return ref_output, user_output, blended_output


@shared_task(name='api.tasks.compute_similarity')
def compute_similarity(image_data, target_class):
    tmp_path = None
    
    try:
        if target_class < 0 or target_class > 35:
            raise ValueError(f'Invalid target_class {target_class}. Model supports classes 0-35 only.')
        
        reference_images_dir = os.path.join(settings.BASE_DIR, 'api', 'reference_images')
        reference_image_path = os.path.join(reference_images_dir, f'class_{target_class}.png')
        
        if not os.path.exists(reference_image_path):
            raise FileNotFoundError(f'Reference image for class {target_class} not found.')
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
            if isinstance(image_data, str) and image_data.startswith('data:image'):
                format, imgstr = image_data.split(';base64,')
                image_bytes = base64.b64decode(imgstr)
                tmp.write(image_bytes)
            else:
                tmp.write(image_data)
            tmp_path = tmp.name
        
        model = get_classification_model()
        similarity_score, distance = model.compute_similarity(tmp_path, reference_image_path)
        
        threshold = 0.45
        is_same = distance < threshold
        
        ref_img, user_img, blended_img = create_comparison_overlay(tmp_path, reference_image_path)
        
        ref_buffered = BytesIO()
        ref_img.save(ref_buffered, format="PNG")
        ref_base64 = base64.b64encode(ref_buffered.getvalue()).decode('utf-8')
        
        user_buffered = BytesIO()
        user_img.save(user_buffered, format="PNG")
        user_base64 = base64.b64encode(user_buffered.getvalue()).decode('utf-8')
        
        blended_buffered = BytesIO()
        blended_img.save(blended_buffered, format="PNG")
        blended_base64 = base64.b64encode(blended_buffered.getvalue()).decode('utf-8')
        
        # Generate simple feedback based on similarity score
        if similarity_score >= 90:
            feedback = "Excellent work! Your calligraphy closely matches the reference. The stroke consistency and overall form are very well executed."
        elif similarity_score >= 75:
            feedback = "Great job! Your calligraphy shows good understanding of the character form. Focus on refining the stroke endings and maintaining consistent pressure throughout."
        elif similarity_score >= 60:
            feedback = "Good effort! You've captured the basic structure well. Work on the stroke angles and spacing to improve similarity with the reference."
        else:
            feedback = "Keep practicing! Focus on the fundamental stroke order and basic shape. Study the reference image carefully and practice the individual strokes before attempting the full character."
        
        return {
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
            'feedback': feedback,
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
    
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)
