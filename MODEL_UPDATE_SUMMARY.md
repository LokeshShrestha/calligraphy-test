# Model Update Summary - 36 Classes

## Overview
Updated the entire API to use the **augmented EfficientNet-B0 model** trained on **36 classes** instead of the previous 62 classes.

---

## Changes Made

### 1. **Model Configuration** (`api/ml_models/config.py`)
- ✅ Updated `NUM_CLASSES` from `62` to `36`
- Model now expects classes in range **0-35**

### 2. **Model Loader** (`api/ml_models/__init__.py`)
- ✅ Changed checkpoint from `efficientnet_b0_best.pth` to `efficientnet_b0_augmented_best.pth`
- ✅ Added note: "Classification model initialized and cached (augmented, 36 classes)"

### 3. **Inference** (`api/ml_models/inference.py`)
- ✅ Updated docstring: `predicted class 0-61` → `predicted class 0-35`

### 4. **Serializers** (`api/serializers.py`)
- ✅ Updated `SimilaritySerializer.target_class` validation: `max_value=61` → `max_value=35`

### 5. **Views** (`api/views.py`)

#### PredictView:
- ✅ Added validation: Check predicted class is within 0-35
- ✅ Returns error if model predicts invalid class
- ✅ Added note to response: `'note': 'Model trained on 36 classes (0-35)'`

#### SimilarityView:
- ✅ Added validation: Check target_class is within 0-35
- ✅ Returns 400 error if target_class > 35
- ✅ Updated error message for missing reference images
- ✅ Added note to response: `'note': 'Model trained on 36 classes (0-35)'`

### 6. **Debug Script** (`debug_models.py`)
- ✅ Added `NUM_CLASSES = 36` constant
- ✅ Updated comments to reflect 0-35 valid range

---

## Important Notes

### ⚠️ Reference Images Required
You need reference images for **classes 0-35** only:
- `api/reference_images/class_0.png`
- `api/reference_images/class_1.png`
- ...
- `api/reference_images/class_35.png`

**Classes 36-61 are no longer supported.**

### ⚠️ Database History
If you have existing database records with `predicted_class` or `target_class` values > 35, they are from the old 62-class model and should be considered invalid.

### ⚠️ Model File
Make sure you have the augmented model file:
```
api/ml_models/weights/efficientnet_b0_augmented_best.pth
```

---

## API Response Changes

### Before:
```json
{
  "success": true,
  "predicted_class": 45,
  "confidence": 92.5
}
```

### After:
```json
{
  "success": true,
  "predicted_class": 12,
  "confidence": 92.5,
  "note": "Model trained on 36 classes (0-35)"
}
```

### Error for Invalid Class:
```json
{
  "success": false,
  "error": "Invalid target_class 50. Model supports classes 0-35 only."
}
```

---

## Testing

Run the debug script to test all endpoints:
```bash
python manage.py runserver
# In another terminal:
python debug_models.py
```

The script will automatically test with class 0, which is valid for the 36-class model.

---

## Migration Steps

If you're migrating from the 62-class model:

1. ✅ Ensure `efficientnet_b0_augmented_best.pth` exists in `api/ml_models/weights/`
2. ✅ Remove or rename old reference images (class_36.png through class_61.png)
3. ✅ Ensure reference images exist for classes 0-35
4. ✅ Restart Django server to reload model
5. ✅ Test with `python debug_models.py`

---

## Summary

All components now consistently use:
- **Model**: `efficientnet_b0_augmented_best.pth`
- **Classes**: 36 (range 0-35)
- **Validation**: Enforced at serializer and view levels
- **Error Messages**: Clear and informative for out-of-range classes
