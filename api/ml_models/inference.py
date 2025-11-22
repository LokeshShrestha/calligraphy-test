"""
Inference utilities for Ranjana Script classification and similarity
"""
# Lazy imports - PyTorch and heavy dependencies loaded on first use
import numpy as np
from PIL import Image


class RanjanaInference:
    """
    Main inference pipeline for Ranjana Script recognition
    """
    
    def __init__(self, model_name: str, device: str = 'cuda', checkpoint_path: str = None):
        """
        Initialize the inference model
        
        Args:
            model_name: Name of trained model ('efficientnet_b0')
            device: Device to run inference on ('cuda' or 'cpu')
            checkpoint_path: Optional custom checkpoint path
        """
        # Lazy import of heavy dependencies
        import torch
        from .config import MODELS_DIR
        from .models import get_model
        from .data_loader import get_transforms
        
        self.device = torch.device(device if torch.cuda.is_available() else 'cpu')
        self.model_name = model_name
        self.transform = get_transforms(augment=False)
        
        # Load classification model
        self.model = get_model(model_name, pretrained=False)
        
        # Determine checkpoint path
        if checkpoint_path is None:
            checkpoint_path = MODELS_DIR / f"{model_name}_best.pth"
        
        checkpoint = torch.load(checkpoint_path, map_location=self.device)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.model = self.model.to(self.device)
        self.model.eval()
    
    def preprocess_image(self, image_path):
        """Preprocess image for inference"""
        image = Image.open(image_path)
        
        # Convert to grayscale
        if image.mode == 'RGBA':
            background = Image.new('RGB', image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[3])
            image = background.convert('L')
        elif image.mode != 'L':
            image = image.convert('L')
        
        # Apply transforms
        image_tensor = self.transform(image).unsqueeze(0)
        return image_tensor, image
    
    def classify(self, image_path: str, top_k: int = 5):
        """
        Classify an image
        
        Args:
            image_path: Path to image
            top_k: Number of top predictions to return
        
        Returns:
            top_classes: Array of top k class indices
            top_probs: Array of top k probabilities
        """
        import torch
        import torch.nn.functional as F
        
        image_tensor, _ = self.preprocess_image(image_path)
        image_tensor = image_tensor.to(self.device)
        
        with torch.no_grad():
            outputs = self.model(image_tensor)
            probs = F.softmax(outputs, dim=1)
        
        # Get top k predictions
        top_probs, top_classes = torch.topk(probs, top_k)
        top_probs = top_probs.cpu().numpy()[0]
        top_classes = top_classes.cpu().numpy()[0]
        
        return top_classes, top_probs
    
    def predict(self, image_path: str, top_k: int = 5):
        """
        User-friendly prediction with dict return format
        
        Args:
            image_path: Path to image
            top_k: Number of top predictions
        
        Returns:
            dict: {
                'class': int (predicted class 0-35),
                'confidence': float (percentage),
                'top_classes': list[int],
                'top_confidences': list[float]
            }
        """
        top_classes, top_probs = self.classify(image_path, top_k)
        
        return {
            'class': int(top_classes[0]),
            'confidence': float(top_probs[0] * 100),
            'top_classes': top_classes.tolist(),
            'top_confidences': (top_probs * 100).tolist()
        }
    
    def compute_similarity(self, image1_path: str, image2_path: str, 
                          siamese_checkpoint: str = None):
        """
        Compute similarity between two images using Siamese Network
        
        Args:
            image1_path: Path to first image
            image2_path: Path to second image
            siamese_checkpoint: Path to Siamese model checkpoint
        
        Returns:
            similarity_score: Similarity percentage [0, 100]
            distance: Euclidean distance between embeddings
        """
        import torch
        import torch.nn.functional as F
        from .config import MODELS_DIR
        from .siamese_network import SiameseNetwork
        
        # Load Siamese model if not already loaded
        if not hasattr(self, 'siamese_model'):
            if siamese_checkpoint is None:
                import glob
                siamese_runs = sorted(glob.glob(str(MODELS_DIR / "*siamese*efficientnet*.pth")))
                if not siamese_runs:
                    raise FileNotFoundError("No Siamese model checkpoint found!")
                siamese_checkpoint = siamese_runs[-1]
            
            print(f"Loading Siamese model from: {siamese_checkpoint}")
            checkpoint = torch.load(siamese_checkpoint, map_location=self.device)
            
            # Use default values if not in checkpoint
            backbone = checkpoint.get('backbone', 'efficientnet_b0')
            embedding_dim = checkpoint.get('embedding_dim', 128)
            
            self.siamese_model = SiameseNetwork(
                backbone=backbone,
                embedding_dim=embedding_dim,
                pretrained_path=None
            )
            self.siamese_model.load_state_dict(checkpoint['model_state_dict'])
            self.siamese_model = self.siamese_model.to(self.device)
            self.siamese_model.eval()
            self.optimal_threshold = 0.45
            print("✓ Siamese model loaded")
        
        # Preprocess both images
        img1_tensor, _ = self.preprocess_image(image1_path)
        img2_tensor, _ = self.preprocess_image(image2_path)
        img1_tensor = img1_tensor.to(self.device)
        img2_tensor = img2_tensor.to(self.device)
        
        # Get embeddings and compute distance
        import torch
        import torch.nn.functional as F
        
        with torch.no_grad():
            emb1, emb2 = self.siamese_model(img1_tensor, img2_tensor)
            distance = F.pairwise_distance(emb1, emb2).item()
            
            # Convert distance to similarity percentage
            max_distance = self.optimal_threshold * 2
            similarity_score = max(0, 100 * (1 - distance / max_distance))
        
        return similarity_score, distance
    
    def generate_gradcam(self, image_path: str, target_class: int = None, save_path: str = None):
        """
        Generate Grad-CAM heatmap visualization
        
        Args:
            image_path: Path to image
            target_class: Target class for Grad-CAM (None = predicted class)
            save_path: Optional path to save visualization
        
        Returns:
            dict: {
                'predicted_class': int,
                'confidence': float,
                'cam': np.ndarray,
                'overlay': np.ndarray,
                'save_path': str (if saved)
            }
        """
        import torch
        import torch.nn.functional as F
        from .gradcam import GradCAM
        
        # Load image
        image = Image.open(image_path).convert('L')
        input_tensor = self.transform(image).unsqueeze(0).to(self.device)
        
        # Get prediction
        self.model.eval()
        with torch.no_grad():
            output = self.model(input_tensor)
            probabilities = F.softmax(output, dim=1)
            predicted_class = output.argmax(dim=1).item()
            confidence = probabilities[0, predicted_class].item()
        
        # Generate Grad-CAM
        gradcam = GradCAM(self.model)
        cam, overlay = gradcam(input_tensor, target_class)
        
        result = {
            'predicted_class': predicted_class,
            'confidence': confidence,
            'cam': cam,
            'overlay': overlay
        }
        
        # Save if requested
        if save_path:
            Image.fromarray(overlay).save(save_path)
            result['save_path'] = save_path
        
        return result
    
    def get_embedding(self, image_path: str, siamese_checkpoint: str = None):
        """
        Extract 128-dimensional feature embedding
        
        Args:
            image_path: Path to image
            siamese_checkpoint: Path to Siamese checkpoint
        
        Returns:
            numpy.ndarray: 128-dimensional embedding vector
        """
        import torch
        from .config import MODELS_DIR
        from .siamese_network import SiameseNetwork
        
        # Load Siamese model if not already loaded
        if not hasattr(self, 'siamese_model'):
            if siamese_checkpoint is None:
                import glob
                siamese_runs = sorted(glob.glob(str(MODELS_DIR / "*siamese*efficientnet*.pth")))
                if not siamese_runs:
                    raise FileNotFoundError("No Siamese model checkpoint found!")
                siamese_checkpoint = siamese_runs[-1]
            
            self.siamese_model = SiameseNetwork(
                backbone_name='efficientnet_b0',
                pretrained=False,
                num_classes=1,
                embedding_dim=128
            )
            
            checkpoint = torch.load(siamese_checkpoint, map_location=self.device)
            self.siamese_model.load_state_dict(checkpoint['model_state_dict'])
            self.siamese_model.to(self.device)
            self.siamese_model.eval()
        
        # Extract embedding
        image = Image.open(image_path).convert('L')
        input_tensor = self.transform(image).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            embedding = self.siamese_model.forward_once(input_tensor)
        
        return embedding.cpu().numpy().flatten()
