# Stage 2 — Segmentation

This document describes how this stage is **currently** performed across projects.

## Objectives

- Generate cell and/or tissue segmentations from raw images using DeepCell Mesmer
- Prepare segmentation outputs (labeled masks) for downstream feature extraction and phenotyping
- Ensure reproducible, QC-driven segmentation with version-locked environments
- Maintain traceability through logs, metadata, and QC visualizations

## Common Inputs

### Input File Types and Formats

1. **OME-TIFF or TIFF multiplex images:**
   - Nuclear channel (DAPI, Hoechst, etc.)
   - Cytoplasm/membrane channel (Pan-Cytokeratin, CD45, membrane markers)
   - Image dimensions: typically 2048×2048 to 8192×8192 pixels
   - Microns per pixel (mpp): 0.325-0.5µm typical for multiplex imaging

2. **Metadata files:**
   - Channel definitions (which markers in which channels)
   - Imaging parameters (mpp, tile overlap, Z-stack info if applicable)
   - Sample/slide identifiers

3. **Project folder structure (mandatory):**
   ```
   project_root/
     raw/
       image.ome.tiff
     segmentation/
       logs/
       qc/
       masks/
       metadata.json
   ```

## Current Scripts / Tools

### Primary Tools

1. **DeepCell Mesmer (v0.12.0)** - See [segmentation_pipeline.md](../sops/segmentation_pipeline.md)
   - Deep learning-based whole-cell and nuclear segmentation
   - Pretrained on diverse tissue types
   - GPU-accelerated (TensorFlow 2.x + CUDA)
   - Handles nuclear, cytoplasm, or combined segmentation

2. **Python environment (conda/venv):**
   - Python 3.8+
   - TensorFlow 2.10+
   - DeepCell package (`pip install deepcell`)
   - Scientific stack: numpy, scikit-image, tifffile, matplotlib

3. **GPU resources:**
   - NVIDIA GPU with CUDA support (required for practical runtime)
   - Typical memory: 8-16GB VRAM
   - GCP VM instances (n1-standard-8 with T4 GPU typical)

### Script Catalog Links

- [mesmer_segmentation.md](../scripts_catalog/segmentation/mesmer_segmentation.md) - Main segmentation script
- [tile_processor.md](../scripts_catalog/segmentation/tile_processor.md) - Tile-based processing for large images
- [qc_visualization.md](../scripts_catalog/segmentation/qc_visualization.md) - QC plot generation

## Manual Steps

### Typical Analyst Workflow

#### 1. Environment Setup and Verification

```bash
# Activate version-locked environment
conda activate deepcell-0.12

# Verify GPU availability
nvidia-smi
python -c "import tensorflow as tf; print(tf.config.list_physical_devices('GPU'))"

# Verify DeepCell installation
python -c "from deepcell.applications import Mesmer; print('Mesmer loaded successfully')"
```

#### 2. Load and Inspect Input Images

```python
import tifffile
import numpy as np

# Load OME-TIFF
img = tifffile.imread('raw/image.ome.tiff')
print(f"Image shape: {img.shape}")
print(f"Data type: {img.dtype}")
print(f"Value range: {img.min()} to {img.max()}")

# Extract nuclear and cytoplasm channels
nuclear = img[0, :, :, 0]  # Adjust indices based on channel order
cytoplasm = img[0, :, :, 1]

# Visual inspection
import matplotlib.pyplot as plt
fig, axes = plt.subplots(1, 2, figsize=(12, 6))
axes[0].imshow(nuclear, cmap='gray')
axes[0].set_title('Nuclear Channel')
axes[1].imshow(cytoplasm, cmap='gray')
axes[1].set_title('Cytoplasm Channel')
plt.show()
```

#### 3. Prepare Input for Mesmer

```python
# Stack channels: (batch, height, width, channels)
image = np.stack([nuclear, cytoplasm], axis=-1)
image = np.expand_dims(image, axis=0)

print(f"Input shape for Mesmer: {image.shape}")  # Should be (1, H, W, 2)
```

#### 4. Run Segmentation

```python
from deepcell.applications import Mesmer
import time

# Initialize Mesmer application
app = Mesmer()

# Set imaging parameters
image_mpp = 0.5  # microns per pixel (adjust based on microscope settings)

# Run prediction
start_time = time.time()
segmentation = app.predict(
    image,
    image_mpp=image_mpp,
    compartment='whole-cell'  # Options: 'nuclear', 'whole-cell', 'both'
)
end_time = time.time()

print(f"Segmentation shape: {segmentation.shape}")
print(f"Number of cells detected: {segmentation.max()}")
print(f"Processing time: {end_time - start_time:.2f} seconds")
```

**Key parameters:**
- `image_mpp`: Critical for scale-aware segmentation (typically 0.325-0.5µm)
- `compartment`: 'whole-cell' most common for multiplex imaging
- Tile-based processing used for images >4096×4096

#### 5. Quality Control (Mandatory)

```python
import matplotlib.pyplot as plt

# Extract mask (remove batch and channel dimensions)
mask = segmentation[0, :, :, 0]

# QC visualization
fig, axes = plt.subplots(1, 3, figsize=(15, 5))

axes[0].imshow(nuclear, cmap='gray')
axes[0].set_title('Nuclear Channel')

axes[1].imshow(cytoplasm, cmap='gray')
axes[1].set_title('Cytoplasm Channel')

axes[2].imshow(mask, cmap='nipy_spectral')
axes[2].set_title(f'Segmentation ({mask.max()} cells)')

plt.tight_layout()
plt.savefig('segmentation/qc/qc_<timestamp>.png', dpi=150)
plt.show()
```

**QC Criteria (failure if violated):**
- All cells individually segmented (no merged clusters >30µm)
- No significant over-segmentation (single cells split)
- No significant under-segmentation (multiple cells merged)
- Cell boundaries align with cytoplasm/membrane staining
- Nuclear masks contained within whole-cell masks
- Cell count biologically plausible (typically 500-5000 per FOV)

If any criteria fail → analyst documents in troubleshooting KB before escalating.

#### 6. Save Outputs

```python
import tifffile
import json
from datetime import datetime

# Save segmentation mask
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
mask_path = f'segmentation/masks/mask_{timestamp}.tiff'
tifffile.imwrite(mask_path, mask.astype(np.uint16))

# Save metadata
metadata = {
    "timestamp": timestamp,
    "mesmer_version": "0.12.0",
    "tensorflow_version": "2.10",
    "image_mpp": image_mpp,
    "compartment": "whole-cell",
    "channels_used": ["DAPI", "Membrane"],
    "num_cells_detected": int(mask.max()),
    "processing_time_sec": end_time - start_time,
    "qc_passed": True  # Updated after QC review
}

with open('segmentation/metadata.json', 'w') as f:
    json.dump(metadata, f, indent=2)

print(f"Saved mask to {mask_path}")
print(f"Detected {mask.max()} cells")
```

## Variations Between Projects

### By Tissue Type

**Lymph nodes:**
- High cell density (5000+ cells per FOV typical)
- Clear nuclear staining (DAPI)
- Membrane channel often CD45 (pan-immune marker)
- Mesmer `compartment='whole-cell'` standard

**Tumor samples:**
- Variable cell density (tumor regions dense, stroma sparse)
- Mix of epithelial (large, clustered) and immune (small, scattered) cells
- Pan-Cytokeratin for tumor membrane
- May require nuclear-only segmentation in tumor regions

**Bone marrow:**
- Very high cell density (densely packed)
- Small cell sizes
- May require parameter tuning or alternative segmentation methods

### By Platform

**QuPath integration:**
- Mesmer run externally (Python script)
- Masks imported into QuPath for visualization and feature extraction
- Groovy script for mask import (see phenotyping SOP)

**Python-only workflows:**
- Mesmer segmentation
- Feature extraction via scikit-image or custom functions
- Direct export to CSV for phenotyping

**Hybrid (most common):**
- Python/Mesmer for segmentation
- QuPath for QC, manual correction, and feature extraction
- Python for downstream spatial analysis

### By Image Size

**Small ROIs (<4096×4096):**
- Process full image in one pass
- Typical runtime: 10-30 seconds on GPU

**Large whole-slide images (>8192×8192):**
- Tile-based processing required
- Typical tile size: 2048×2048 with 128-pixel overlap
- Stitch tiles with overlap handling
- Typical runtime: 5-20 minutes depending on slide size

## Known Issues

### 1. GPU Memory Errors (OOM - Out of Memory)

**Problem:** Large images cause CUDA out-of-memory errors.

**Symptoms:**
```
tensorflow.python.framework.errors_impl.ResourceExhaustedError:
OOM when allocating tensor with shape [1,8192,8192,2]
```

**Current solution:**
- Tile-based processing (2048×2048 tiles standard)
- Reduce batch size
- Use smaller images for testing
- Monitor GPU memory with `nvidia-smi`

See [deepcell_mesmer_errors.md](../troubleshooting/deepcell_mesmer_errors.md) for detailed troubleshooting.

### 2. "Exploding Cells" Artifact

**Problem:** Mesmer occasionally produces massive segmentation regions (>100µm) that don't correspond to cells.

**Current detection:**
```python
# Check for oversized cells
cell_areas = np.bincount(mask.ravel())[1:]  # Exclude background (0)
large_cells = np.where(cell_areas > 10000)[0]  # Adjust threshold based on mpp
print(f"Found {len(large_cells)} cells with area >10000 pixels")
```

**Current handling:**
- Flag in QC
- Manually review and exclude if necessary
- Document in troubleshooting KB if recurring

### 3. Over-segmentation of Large Cells

**Problem:** Epithelial or tumor cells (large, irregular) split into multiple segments.

**Current mitigation:**
- Adjust `image_mpp` parameter (sometimes under-reporting mpp helps)
- Use nuclear-only segmentation + watershed expansion
- Post-processing to merge over-segmented cells (morphological operations)

### 4. Under-segmentation in Dense Regions

**Problem:** Tightly packed lymphocytes merge into single segments.

**Current approach:**
- Check nuclear channel quality (is staining sufficient?)
- Try nuclear-only segmentation first
- May require alternative segmentation methods (Cellpose, StarDist)

### 5. Channel Selection Errors

**Problem:** Wrong channels selected for nuclear/cytoplasm inputs.

**Symptoms:**
- Very low cell counts (<50 for typical FOV)
- Segmentation boundaries don't align with cell staining
- QC visualization shows mismatch

**Prevention:**
- Always visualize channels before segmentation
- Document channel order in metadata
- Use descriptive variable names in code

### 6. Inconsistent Segmentation Across Batches

**Problem:** Different Mesmer versions or parameters produce different results.

**Current enforcement:**
- Version-locked conda environment (deepcell-0.12)
- Metadata.json records all versions and parameters
- Analysts must not modify environment without team approval

### 7. Missing QC Documentation

**Problem:** Segmentation runs without QC visualization or review.

**Current requirement (non-negotiable):**
- QC plot generation is mandatory
- Analyst must review and document pass/fail
- If QC fails, troubleshooting KB entry required before escalating

## Success Metrics

From recent projects:

**Lymph node samples (Nguyen Lab):**
- **4 whole-slide images** processed
- **~100,000 cells** segmented total
- **QC pass rate:** 100% (no re-runs required)
- **Processing time:** ~15 minutes per slide (tile-based, GPU)
- **Cell density:** 3000-8000 cells per major region

**Tumor microenvironment:**
- **Variable cell density:** 500-5000 cells per ROI
- **QC considerations:** Manual review of tumor/stroma boundary regions
- **Typical processing:** 30-60 seconds per ROI (2048×2048)

## Next Steps / Improvements Needed

1. **Automate tile-based processing** with standardized overlap handling
2. **Implement post-processing filters** to remove artifacts automatically
3. **Develop tissue-specific parameter sets** (lymph node defaults, tumor defaults)
4. **Create segmentation QC dashboard** for batch QC review
5. **Benchmark alternative methods** (Cellpose, StarDist) for specific tissue types
6. **Build segmentation validation dataset** with manual annotations for accuracy metrics
