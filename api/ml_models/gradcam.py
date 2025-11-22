"""
Grad-CAM (Gradient-weighted Class Activation Mapping) Implementation
For visualizing model attention on Ranjana character images
"""
import torch
import torch.nn.functional as F
import numpy as np
import cv2
from typing import Optional, Tuple


class GradCAM:
    """
    Grad-CAM: Visual Explanations from Deep Networks
    Generates heatmaps showing important image regions for predictions
    """
    
    def __init__(self, model: torch.nn.Module, target_layer: Optional[torch.nn.Module] = None):
        self.model = model
        self.model.eval()
        
        # Storage for activations and gradients
        self.activations = None
        self.gradients = None
        
        # Find target layer
        if target_layer is None:
            target_layer = self._find_target_layer()
        
        self.target_layer = target_layer
        self._register_hooks()
    
    def _find_target_layer(self) -> torch.nn.Module:
        """Find the last convolutional layer"""
        if hasattr(self.model, 'efficientnet'):
            base_model = self.model.efficientnet
        else:
            base_model = self.model
        
        if hasattr(base_model, 'features'):
            last_conv = None
            for module in base_model.features.modules():
                if isinstance(module, torch.nn.Conv2d):
                    last_conv = module
            if last_conv is not None:
                return last_conv
        
        raise ValueError("Could not find convolutional layers in model")
    
    def _register_hooks(self):
        """Register forward and backward hooks"""
        def forward_hook(module, input, output):
            self.activations = output.detach()
        
        def backward_hook(module, grad_input, grad_output):
            self.gradients = grad_output[0].detach()
        
        self.target_layer.register_forward_hook(forward_hook)
        self.target_layer.register_full_backward_hook(backward_hook)
    
    def generate_cam(self, input_tensor: torch.Tensor, target_class: Optional[int] = None) -> np.ndarray:
        """Generate Class Activation Map"""
        # Forward pass
        self.model.zero_grad()
        output = self.model(input_tensor)
        
        # Get target class
        if target_class is None:
            target_class = output.argmax(dim=1).item()
        
        # Backward pass
        output[:, target_class].backward()
        
        # Get activations and gradients
        activations = self.activations
        gradients = self.gradients
        
        # Weighted combination
        weights = gradients.mean(dim=(2, 3), keepdim=True)
        cam = (weights * activations).sum(dim=1, keepdim=True)
        
        # Apply ReLU and normalize
        cam = F.relu(cam)
        cam = cam.squeeze().cpu().numpy()
        cam = cam - cam.min()
        cam = cam / (cam.max() + 1e-8)
        
        return cam
    
    def overlay_heatmap(self, image: np.ndarray, cam: np.ndarray, 
                       alpha: float = 0.5, colormap: int = cv2.COLORMAP_JET) -> np.ndarray:
        """Overlay CAM heatmap on original image"""
        # Resize CAM to match input image
        cam_resized = cv2.resize(cam, (image.shape[1], image.shape[0]))
        
        # Convert to heatmap
        heatmap = np.uint8(255 * cam_resized)
        heatmap = cv2.applyColorMap(heatmap, colormap)
        heatmap = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)
        
        # Convert grayscale to RGB if needed
        if len(image.shape) == 2:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        
        # Normalize image
        if image.dtype != np.uint8:
            if image.max() <= 1.0:
                image = np.uint8(255 * image)
            else:
                image = np.uint8(image)
        
        heatmap = heatmap.astype(np.uint8)
        
        # Blend
        overlay = cv2.addWeighted(image, 1 - alpha, heatmap, alpha, 0)
        
        return overlay
    
    def __call__(self, input_tensor: torch.Tensor, target_class: Optional[int] = None,
                 return_cam_only: bool = False) -> Tuple[np.ndarray, np.ndarray]:
        """Generate Grad-CAM visualization"""
        cam = self.generate_cam(input_tensor, target_class)
        
        if return_cam_only:
            return cam, None
        
        # Convert input tensor to numpy image
        image = input_tensor.squeeze().cpu().numpy()
        
        # Create overlay
        overlay = self.overlay_heatmap(image, cam)
        
        return cam, overlay
