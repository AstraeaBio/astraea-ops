# DeepCell Mesmer Errors

## Overview

Troubleshooting guide for DeepCell Mesmer segmentation pipeline errors and issues.

## Symptoms

- Segmentation failures or crashes
- Out of memory errors during processing
- Incorrect or poor segmentation results
- Model loading failures
- GPU not detected or utilized

## Common Causes

1. **Insufficient memory**: Large images exceeding available RAM/VRAM
2. **Incorrect image format**: Input images not in expected format
3. **Model file corruption**: Downloaded model files incomplete or corrupted
4. **CUDA/GPU compatibility issues**: Driver or library version mismatches
5. **Input channel mismatch**: Nuclear and cytoplasm channels incorrectly specified

## Solutions

### Solution 1: Handle Memory Issues

For large images, process in tiles:

```python
from deepcell.applications import Mesmer

app = Mesmer()

# Use smaller batch sizes
predictions = app.predict(
    image,
    image_mpp=0.5,
    batch_size=1
)
```

Or resize images before processing if resolution allows:

```python
from skimage.transform import resize

# Downscale by factor of 2
image_small = resize(image, (image.shape[0]//2, image.shape[1]//2), preserve_range=True)
```

### Solution 2: Verify Input Format

Ensure correct input format for Mesmer:

```python
import numpy as np

# Image should be (batch, height, width, channels)
# Channels: [nuclear, cytoplasm]
print(f"Image shape: {image.shape}")
print(f"Image dtype: {image.dtype}")

# Normalize if needed
image = image.astype(np.float32)
```

### Solution 3: Reinstall or Re-download Model

Clear cached models and reinstall:

```bash
# Remove cached models
rm -rf ~/.keras/models/

# Reinstall deepcell
pip uninstall deepcell
pip install deepcell
```

### Solution 4: Check GPU Configuration

Verify TensorFlow GPU setup:

```python
import tensorflow as tf

print("GPUs Available:", tf.config.list_physical_devices('GPU'))
print("TensorFlow version:", tf.__version__)
```

## Prevention

- Monitor memory usage during processing
- Validate input images before running segmentation
- Keep DeepCell and dependencies updated
- Test on small images before full datasets

## Related Resources

- [DeepCell Documentation](https://deepcell.readthedocs.io/)
- [Segmentation Pipeline SOP](../sops/segmentation_pipeline.md)

## Last Updated

2025-12-05
