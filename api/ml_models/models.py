"""
Model architectures for Ranjana Script classification
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import models

from .config import NUM_CLASSES


class EfficientNetModel(nn.Module):
    """
    EfficientNet model (B0/B1) adapted for grayscale images
    """
    
    def __init__(self, num_classes: int = NUM_CLASSES, model_name: str = 'efficientnet_b0', pretrained: bool = True):
        super(EfficientNetModel, self).__init__()
        
        # Load EfficientNet
        if model_name == 'efficientnet_b0':
            self.efficientnet = models.efficientnet_b0(pretrained=pretrained)
        elif model_name == 'efficientnet_b1':
            self.efficientnet = models.efficientnet_b1(pretrained=pretrained)
        else:
            raise ValueError(f"Unknown model: {model_name}")
        
        # Modify first conv layer for grayscale input
        self.efficientnet.features[0][0] = nn.Conv2d(1, 32, kernel_size=3, stride=2, padding=1, bias=False)
        
        # Modify classifier for our num_classes
        num_features = self.efficientnet.classifier[1].in_features
        self.efficientnet.classifier[1] = nn.Linear(num_features, num_classes)
    
    def forward(self, x):
        return self.efficientnet(x)


def get_model(model_name: str, num_classes: int = NUM_CLASSES, pretrained: bool = True):
    """
    Factory function to get model by name
    
    Args:
        model_name: Model name (e.g., 'efficientnet_b0')
        num_classes: Number of output classes
        pretrained: Whether to use pretrained weights
    
    Returns:
        Model instance
    """
    if model_name in ['efficientnet_b0', 'efficientnet_b1']:
        return EfficientNetModel(num_classes, model_name, pretrained)
    else:
        raise ValueError(f"Unknown model: {model_name}")
