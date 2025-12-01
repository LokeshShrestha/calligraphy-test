"""
Model loader singleton for Django
Ensures model is loaded only once and reused across requests
"""
from pathlib import Path

# Global model instance
_classification_model = None
_siamese_preloaded = False


def get_classification_model(preload_siamese=True):
    """
    Get or initialize the classification model (singleton pattern)
    Also preloads Siamese model to avoid first-request delay.
    
    Args:
        preload_siamese: If True, also load Siamese model for similarity
    
    Returns:
        RanjanaInference: Loaded model instance
    """
    global _classification_model, _siamese_preloaded
    
    if _classification_model is None:
        # Lazy import to avoid loading PyTorch during Django startup
        from .inference import RanjanaInference
        
        model_path = Path(__file__).parent / 'weights'
        _classification_model = RanjanaInference(
            model_name='efficientnet_b0',
            device='cpu',  # Change to 'cuda' if GPU available
            checkpoint_path=str(model_path / 'efficientnet_b0_augmented_best.pth')
        )
        print("✓ Classification model loaded")
    
    # Preload Siamese model to avoid delay on first similarity request
    if preload_siamese and not _siamese_preloaded:
        try:
            _preload_siamese_model(_classification_model)
            _siamese_preloaded = True
        except Exception as e:
            print(f"Warning: Could not preload Siamese model: {e}")
    
    return _classification_model


def _preload_siamese_model(inference_instance):
    """Preload the Siamese model onto the inference instance"""
    import torch
    from .config import MODELS_DIR
    from .siamese_network import SiameseNetwork
    import glob
    
    if hasattr(inference_instance, 'siamese_model'):
        return  # Already loaded
    
    siamese_runs = sorted(glob.glob(str(MODELS_DIR / "*siamese*efficientnet*.pth")))
    if not siamese_runs:
        raise FileNotFoundError("No Siamese model checkpoint found!")
    siamese_checkpoint = siamese_runs[-1]
    
    print(f"Preloading Siamese model from: {siamese_checkpoint}")
    checkpoint = torch.load(siamese_checkpoint, map_location=inference_instance.device)
    
    backbone = checkpoint.get('backbone', 'efficientnet_b0')
    embedding_dim = checkpoint.get('embedding_dim', 128)
    
    inference_instance.siamese_model = SiameseNetwork(
        backbone=backbone,
        embedding_dim=embedding_dim,
        pretrained_path=None
    )
    inference_instance.siamese_model.load_state_dict(checkpoint['model_state_dict'])
    inference_instance.siamese_model = inference_instance.siamese_model.to(inference_instance.device)
    inference_instance.siamese_model.eval()
    inference_instance.optimal_threshold = 0.45
    print("✓ Siamese model preloaded")


def reload_model():
    """Force reload the model (useful for updates)"""
    global _classification_model, _siamese_preloaded
    _classification_model = None
    _siamese_preloaded = False
    return get_classification_model()
