from gradio_client import Client, handle_file
from PIL import Image
import io
import numpy as np

class HuggingFaceMLClient:
    def __init__(self, space_url):
        """
        Initialize HF Space client
        space_url: Your HF Space URL, e.g., "https://your-username-calligraphy-ml-api.hf.space"
        """
        self.space_url = space_url.rstrip('/')
        self.client = Client(self.space_url)
    
    def predict(self, image_path, top_k=1, skip_preprocessing=False):
        """
        Predict character class
        
        Args:
            image_path: Path to image file
            top_k: Number of top predictions (not used, for API compatibility)
            skip_preprocessing: If True, image is already preprocessed (ignored for HF API)
        """
        try:
            # Call Gradio API - Classification interface
            result = self.client.predict(
                handle_file(image_path),
                api_name="/predict_class"
            )
            
            return {
                'class': result['predicted_class'],
                'confidence': result['confidence']
            }
        except Exception as e:
            raise Exception(f"HF API prediction failed: {str(e)}")
    
    def compute_similarity(self, image1_path, image2_path, siamese_checkpoint=None, skip_preprocessing=False):
        """
        Compute similarity between two images
        
        Args:
            image1_path: Path to first image
            image2_path: Path to second image
            siamese_checkpoint: Not used for HF API (for compatibility)
            skip_preprocessing: If True, images are already preprocessed (ignored for HF API)
        
        Returns:
            tuple: (similarity_score, distance, ref_image_pil, user_image_pil, overlay_image_pil)
        """
        try:
            # Call Gradio API - Similarity interface
            result = self.client.predict(
                handle_file(image1_path),
                handle_file(image2_path),
                api_name="/compute_similarity"
            )
            
            # Debug: print result structure
            print(f"HF API result type: {type(result)}")
            print(f"HF API result length: {len(result) if isinstance(result, (list, tuple)) else 'N/A'}")
            
            # result should be a tuple: (dict, ref_image, user_image, overlay_image)
            if not isinstance(result, (list, tuple)) or len(result) < 4:
                raise Exception(f"Unexpected HF API response format. Expected tuple with 4 elements, got: {type(result)} with length {len(result) if isinstance(result, (list, tuple)) else 'N/A'}")
            
            result_dict = result[0]
            ref_image_result = result[1]
            user_image_result = result[2]
            overlay_image_result = result[3]
            
            # Gradio returns file paths as strings, load them as PIL Images
            if isinstance(ref_image_result, str):
                ref_image = Image.open(ref_image_result)
            else:
                ref_image = ref_image_result
            
            if isinstance(user_image_result, str):
                user_image = Image.open(user_image_result)
            else:
                user_image = user_image_result
            
            if isinstance(overlay_image_result, str):
                overlay_image = Image.open(overlay_image_result)
            else:
                overlay_image = overlay_image_result
            
            return result_dict['similarity_score'], result_dict['distance'], ref_image, user_image, overlay_image
        except Exception as e:
            raise Exception(f"HF API similarity failed: {str(e)}")
    
    def _image_to_bytes(self, img):
        """Convert PIL Image to bytes"""
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        return buf.getvalue()

# Singleton instance
_hf_client = None

def get_hf_client():
    """Get or create HF client instance"""
    global _hf_client
    if _hf_client is None:
        import os
        space_url = os.getenv('HUGGINGFACE_SPACE_URL')
        if not space_url:
            raise ValueError("HUGGINGFACE_SPACE_URL environment variable not set")
        _hf_client = HuggingFaceMLClient(space_url)
    return _hf_client
