"""
Model loader singleton for Django
Ensures model is loaded only once and reused across requests
"""
from pathlib import Path
from .inference import RanjanaInference

# Global model instance
_classification_model = None


def get_classification_model():
    """
    Get or initialize the classification model (singleton pattern)
    
    Returns:
        RanjanaInference: Loaded model instance
    """
    global _classification_model
    
    if _classification_model is None:
        model_path = Path(__file__).parent / 'weights'
        _classification_model = RanjanaInference(
            model_name='efficientnet_b0',
            device='cpu',  # Change to 'cuda' if GPU available
            checkpoint_path=str(model_path / 'efficientnet_b0_augmented_best.pth')
        )
    
    return _classification_model


def reload_model():
    """Force reload the model (useful for updates)"""
    global _classification_model
    _classification_model = None
    return get_classification_model()
