"""
Script to invert colors in PNG images (black to white, white to black)
Reads from: api/reference_images/
Saves to: calligraphy/reference/
"""

import os
import sys
from pathlib import Path
from PIL import Image
import numpy as np


def invert_image_colors(input_path, output_path):
    """
    Invert colors in a PNG image (black becomes white, white becomes black)
    
    Args:
        input_path: Path to input PNG image
        output_path: Path to save inverted PNG image
    """
    try:
        # Open the image
        img = Image.open(input_path)
        
        # Convert to numpy array
        img_array = np.array(img)
        
        # Invert colors
        # For RGB/RGBA images, invert all color channels but preserve alpha if present
        if len(img_array.shape) == 3 and img_array.shape[2] == 4:  # RGBA
            # Invert RGB channels, keep alpha channel unchanged
            inverted_array = img_array.copy()
            inverted_array[:, :, :3] = 255 - img_array[:, :, :3]
        else:  # RGB or grayscale
            inverted_array = 255 - img_array
        
        # Convert back to PIL Image
        inverted_img = Image.fromarray(inverted_array.astype('uint8'))
        
        # Save the inverted image
        inverted_img.save(output_path)
        print(f"✓ Inverted: {input_path} -> {output_path}")
        return True
        
    except Exception as e:
        print(f"✗ Error processing {input_path}: {str(e)}")
        return False


def process_folder(input_folder, output_folder):
    """
    Process all PNG images in a folder
    
    Args:
        input_folder: Path to folder containing PNG images
        output_folder: Path to folder where inverted images will be saved
    """
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    # Get all PNG files in input folder
    png_files = [f for f in os.listdir(input_folder) if f.lower().endswith('.png')]
    
    if not png_files:
        print(f"No PNG files found in {input_folder}")
        return
    
    print(f"Found {len(png_files)} PNG file(s). Processing...\n")
    
    success_count = 0
    for filename in png_files:
        input_path = os.path.join(input_folder, filename)
        output_path = os.path.join(output_folder, filename)
        
        if invert_image_colors(input_path, output_path):
            success_count += 1
    
    print(f"\nProcessed {success_count}/{len(png_files)} images successfully")


def main():
    # Get script directory (project root)
    script_dir = Path(__file__).parent
    
    # Define input and output folders
    input_folder = script_dir / "api" / "reference_images"
    output_folder = script_dir / "reference_images_inverted"
    
    # Check if input folder exists
    if not input_folder.exists():
        print(f"Error: Input folder not found: {input_folder}")
        print("Expected folder structure: api/reference_images/")
        sys.exit(1)
    
    print(f"Input folder:  {input_folder}")
    print(f"Output folder: {output_folder}")
    print("-" * 60)
    
    # Process all PNG images from api/reference_images to calligraphy/reference
    process_folder(str(input_folder), str(output_folder))


if __name__ == "__main__":
    main()
