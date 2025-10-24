"""
Siamese Network for similarity scoring
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from .models import get_model


class SiameseNetwork(nn.Module):
    """
    Siamese Network with shared encoder for similarity measurement
    """
    
    def __init__(self, backbone='efficientnet_b0', embedding_dim=128, pretrained_path=None):
        """
        Args:
            backbone: Base model architecture
            embedding_dim: Size of the embedding vector
            pretrained_path: Path to pretrained classification model checkpoint
        """
        super(SiameseNetwork, self).__init__()
        
        self.backbone_name = backbone
        self.embedding_dim = embedding_dim
        
        # Load base model (without classification head)
        base_model = get_model(backbone, pretrained=False)
        
        # Load pretrained weights if provided
        if pretrained_path:
            checkpoint = torch.load(pretrained_path, map_location='cpu')
            base_model.load_state_dict(checkpoint['model_state_dict'])
        
        # Remove classification head and extract feature extractor
        if 'efficientnet' in backbone:
            self.encoder = nn.Sequential(*list(base_model.children())[:-1])
            with torch.no_grad():
                dummy_input = torch.randn(1, 1, 64, 64)
                features = self.encoder(dummy_input)
                feature_dim = features.view(features.size(0), -1).size(1)
        else:
            raise ValueError(f"Unsupported backbone: {backbone}")
        
        # Projection head: maps features to embedding space
        self.projection_head = nn.Sequential(
            nn.Flatten(),
            nn.Linear(feature_dim, 512),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(512, embedding_dim),
            nn.LayerNorm(embedding_dim)
        )
    
    def forward_once(self, x):
        """Forward pass for one image - returns normalized embedding"""
        features = self.encoder(x)
        embedding = self.projection_head(features)
        # L2 normalize embeddings
        embedding = F.normalize(embedding, p=2, dim=1)
        return embedding
    
    def forward(self, img1, img2):
        """Forward pass for image pair"""
        embedding1 = self.forward_once(img1)
        embedding2 = self.forward_once(img2)
        return embedding1, embedding2
