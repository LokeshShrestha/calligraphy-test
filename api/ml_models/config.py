"""
Simplified configuration for Django integration
"""
from pathlib import Path

# Base directory for ml_models
BASE_DIR = Path(__file__).parent

# Model weights directory
MODELS_DIR = BASE_DIR / 'weights'

# Model parameters
NUM_CLASSES = 62
IMAGE_SIZE = (64, 64)
NUM_CHANNELS = 1  # Grayscale

# Device
DEVICE = 'cpu'  # Change to 'cuda' if you have GPU

# Normalization (default values for Ranjana dataset)
MEAN = 0.5
STD = 0.5
