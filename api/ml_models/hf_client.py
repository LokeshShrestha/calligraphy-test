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
    
    def predict(self, image_path, top_k=1):
        """Predict character class"""
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
    
    def compute_similarity(self, image1_path, image2_path):
        """Compute similarity between two images"""
        try:
            # Call Gradio API - Similarity interface
            result = self.client.predict(
                handle_file(image1_path),
                handle_file(image2_path),
                api_name="/compute_similarity"
            )
            
            return result['similarity_score'], result['distance']
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
