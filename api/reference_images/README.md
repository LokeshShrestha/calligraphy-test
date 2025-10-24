# Reference Images Directory

This directory stores reference images for each Ranjana Script character class used in similarity comparison.

## Structure

Each reference image should be named using the pattern: `class_<number>.png`

Example:
```
class_0.png   # Reference image for class 0
class_1.png   # Reference image for class 1
class_2.png   # Reference image for class 2
...
class_61.png  # Reference image for class 61
```

## Requirements

- **Format**: PNG images
- **Classes**: 0 to 61 (62 total classes)
- **Naming**: Must follow `class_<number>.png` pattern exactly

## How It Works

1. User uploads an image to `/api/predict/` endpoint
2. Model predicts the class (e.g., class 15)
3. Frontend sends the same image + predicted class to `/api/similarity/`
4. Backend loads `class_15.png` from this directory
5. Model compares uploaded image with the reference image
6. Returns similarity score and whether they match

## Populating Reference Images

You need to add one representative image for each of the 62 classes. These should be:
- Clear, high-quality examples of each character
- Consistent in style
- Properly labeled with the correct class number

You can extract these from your training dataset or use the best examples from your validation set.
