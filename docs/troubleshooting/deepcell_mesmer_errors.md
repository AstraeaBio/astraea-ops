# DeepCell Mesmer Errors

## Overview

Troubleshooting guide for DeepCell Mesmer segmentation pipeline errors and issues.

## Symptoms

- Segmentation failures or crashes
- Out of memory errors during processing
- Incorrect or poor segmentation results
- Model loading failures
- GPU not detected or utilized

## Examples:
> Kernel keeps dying when running Mesmer  
> CUDA device not found  
> Out-of-memory errors on 20-core TMA

## Diagnosis

## Common Causes

1. Processing entire whole-slide instead of tiles
2. **Insufficient memory**: Large images exceeding available RAM/VRAM / Batch size too large for GPU memory
3. **Incorrect image format**: Input images not in expected format
4. **Model file corruption**: Downloaded model files incomplete or corrupted
5. **CUDA/GPU compatibility issues**: Driver or library version mismatches / Wrong CUDA / TensorFlow / driver combo
6. **Input channel mismatch**: Nuclear and cytoplasm channels incorrectly specified
7. Running on CPU instead of GPU.

## Solutions

### Solution 1: GPU Troubleshooting
1. **Confirm GPU visible**
```bash
nvidia-smi
```
2. Confirm Python can see GPU
- in python
```python
import tensorflow as tf
print(tf.config.list_physical_devices('GPU'))
```

3. Reduce workload
- Use smaller tiles.
- Reduce batch size.

4. Use a known-good env
- Use the environment file envs/deepcell_mesmer.yml (create and document this).
- Install exact DeepCell version listed there.

### Solution 2: Handle Memory Issues

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

### Solution 3: Verify Input Format

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

### Solution 4: Reinstall or Re-download Model

Clear cached models and reinstall:

```bash
# Remove cached models
rm -rf ~/.keras/models/

# Reinstall deepcell
pip uninstall deepcell
pip install deepcell
```

### Solution 5: Check GPU Configuration

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
