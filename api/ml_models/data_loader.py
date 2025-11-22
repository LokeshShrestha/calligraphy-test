"""
Simplified data loader for inference only
"""
from .config import IMAGE_SIZE, MEAN, STD


def get_transforms(augment: bool = False):
    """
    Get image transforms for inference
    
    Args:
        augment: Whether to apply data augmentation (always False for inference)
    
    Returns:
        Composed transforms
    """
    # Lazy import to avoid loading torchvision during startup
    from torchvision import transforms
    
    # Inference transforms (no augmentation)
    transform = transforms.Compose([
        transforms.Resize(IMAGE_SIZE),
        transforms.ToTensor(),
        transforms.Normalize(mean=[MEAN], std=[STD])
    ])
    
    return transform
