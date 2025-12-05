# Segmentation Pipeline SOP

## 1. Purpose

Provide analysts with a fully reproducible, QC-driven, version-locked procedure for running cell segmentation with DeepCell Mesmer. This SOP ensures consistent results, minimal rework, and traceable troubleshooting across teams and clients.

## 2. Scope
This SOP applies to:
- OME-TIFF or TIFF multiplex images
- Nuclear-only, membrane-only, or combined nuclear+cytoplasm segmentation
- GPU-enabled environments on GCP VMs or local GPU workstations

## 3. Prerequisites / Required Inputs
Analysts must prepare the following before running segmentation:
### 3.1. Folder Structure (MANDATORY)
```
project_root/
  raw/
    image.ome.tiff
  segmentation/
    logs/
    qc/
    masks/
    metadata.json
  notebooks/
```
If this structure does not exist → analyst must create it.

### 3.2. Required Files
- Nuclear channel TIFF or OME-TIFF
- Cytoplasm/membrane channel TIFF (if whole-cell segmentation)
- Metadata file describing:
 - channels used
 - mpp
 - version of Mesmer
   
## 4. Required Prerequisites on VM
- Python 3.8+ installed
- DeepCell package installed (`pip install deepcell`)
- GPU with CUDA support (recommended)
- Input images in supported format (TIFF, OME-TIFF
- TensorFlow 2.x
- Python scientific stack (numpy, scikit-image, tifffile)


### 4.1  Conda environment (version locked)
- Analysts must not modify this environment. Changes break reproducibility.
```bash
conda activate deepcell-0.12
```
If the environment is missing, recreate:
````bash
conda env create -f envs/deepcell_mesmer.yml
````
### 4.2. GPU verification (MANDATORY)
Before any run:
````bash
nvidia-smi
python -c "import tensorflow as tf; print(tf.config.list_physical_devices('GPU'))"
````
If GPU is not detected → STOP → update deepcell_mesmer_errors.md.

### 4.3. Verify installation:

```python
from deepcell.applications import Mesmer
app = Mesmer()
print("Mesmer loaded successfully")
```

## 5. Pipeline Procedure
### Step 0 - activate environment
```bash
conda activate deepcell-0.1.2
# or
source venv/bin/activate
```
### Step 1 — Load Image and Verify Channels
Analyst must confirm correct channel indices and shapes:
```python
import tifffile
img = tifffile.imread('raw/image.ome.tiff')
print(img.shape)
```

### Step 1.5 - Tiling and Nucleus / Cytoplasm Identification (TODO: fill out)
Use tile-based input, never full whole-slide arrays unless < 4k x 4k.


### Step 2: Prepare Input Images

Ensure images are in the correct format:

```python
import numpy as np
import tifffile

# Load nuclear and cytoplasm channels
nuclear = tifffile.imread('nuclear_channel.tiff')
cytoplasm = tifffile.imread('cytoplasm_channel.tiff')

# Stack into expected format: (batch, height, width, channels)
image = np.stack([nuclear, cytoplasm], axis=-1)
image = np.expand_dims(image, axis=0)

print(f"Image shape: {image.shape}")  # Should be (1, H, W, 2)
```
If tiling code is used, record tile size in logs.

### Step 3: Run Segmentation

Execute the Mesmer segmentation:

```python
from deepcell.applications import Mesmer

app = Mesmer()

# Set microns per pixel for your imaging system
image_mpp = 0.5  # Adjust based on your microscope settings

# Run prediction
segmentation = app.predict(
    image,
    image_mpp=image_mpp,
    compartment='whole-cell'  # Options: 'nuclear', 'whole-cell', 'both'
)

print(f"Segmentation shape: {segmentation.shape}")
print(f"Number of cells detected: {segmentation.max()}")
```
Log:
- Start time
- End time
- GPU memory usage
- Number of cells detected
If seg.max() < 50 for a typical ROI → flag as QC failure.

### Step 4: Save Outputs
Analyst must save:
```bash
segmentation/masks/mask_<timestamp>.tiff
segmentation/logs/run_<timestamp>.txt
segmentation/qc/qc_<timestamp>.png
```
Metadata file appended:
```json
{
  "mesmer_version": "0.12.0",
  "tensorflow_version": "2.10",
  "mpp": 0.5,
  "channels_used": ["DAPI", "Membrane"],
  "tile_size": 2048,
  "batch_time_sec": 12.3
}
```
Export segmentation masks:

```python
import tifffile

# Remove batch dimension
mask = segmentation[0, :, :, 0]

# Save as labeled TIFF
tifffile.imwrite('segmentation_mask.tiff', mask.astype(np.uint16))

print("Segmentation mask saved")
```

### Step 5: Quality Control (MANDATORY)

Review segmentation results:

```python
import matplotlib.pyplot as plt

fig, axes = plt.subplots(1, 3, figsize=(15, 5))

axes[0].imshow(nuclear, cmap='gray')
axes[0].set_title('Nuclear Channel')

axes[1].imshow(cytoplasm, cmap='gray')
axes[1].set_title('Cytoplasm Channel')

axes[2].imshow(mask, cmap='nipy_spectral')
axes[2].set_title(f'Segmentation ({mask.max()} cells)')

plt.tight_layout()
plt.savefig('qc_visualization.png', dpi=150)
plt.show()
```

Analyst must review three default QC plots:
## Quality Criteria (failure if violated):

- [ ] All cells are individually segmented
- [ ] No merged clusters > 30 µm diameter
- [ ] No significant over-segmentation (single cells split into multiple)
- [ ] No significant under-segmentation (multiple cells merged)
- [ ] No “exploding cells” (Mesmer artifact)
- [ ] Cell boundaries align with cytoplasm / membrane staining
- [ ] Nuclear masks are contained within whole-cell masks
- [ ] Cell count is biologically plausible (range specified per tissue type)

If any QC criteria fail →
Analyst must attempt remediation before escalating.

### Step 6: Definition of Done (NON-NEGOTIABLE)
Segmentation is DONE only when all boxes checked:
## Output Quality
- [ ] Mask TIFF saved in correct folder
- [ ] QC image saved
- [ ] Mesmer version recorded
- [ ] Log file completed with start/end times
- [ ] Metadata JSON updated
- [ ] Analyst has reviewed QC and it PASSED
- [ ] If QC failed → troubleshooting entry created
## Reproducibility
- [ ] Command(s) used are pasted into log
- [ ] Code version (branch or commit hash) recorded
## Communication
- [ ] Summary posted to ClickUp task with:
    - What was done
    - Where outputs are
    - Any QC concerns
    - Link to troubleshooting entry if applicable
Please ensure the above steps are complete before submitting the results for review.

### 7: Troubleshooting
- For segmentation errors, see [DeepCell Mesmer Errors](../troubleshooting/deepcell_mesmer_errors.md)
- For memory issues, try processing images in smaller tiles

Before escalating:
Analyst must complete:
1. Check GPU (nvidia-smi)
2. Check Mesmer version
3. Check input image shape
4. Check memory usage
5. Run segmentation on a single small tile
6. Log ALL ERRORS into a new entry under:[DeepCell Mesmer Errors](../troubleshooting/deepcell_mesmer_errors.md)

Escalation rules:
- Only escalate after attempting troubleshooting
- Escalation must include:
  - Logs
  - Screenshots
  - Input shapes
  - Exact code block used
  - Link to troubleshooting entry

### 8: Common Mistakes
- Running whole-slide at once (causes OOM and rework)
- Forgetting GPU check
- Using wrong Mesmer version
- Forgetting to record which channels were used
- Missing metadata.json
- QC images not included
- Not checking mask range (if max() < 20, usually bad segmentation)

## References

- DeepCell Documentation: https://deepcell.readthedocs.io/
- Mesmer Paper: https://doi.org/10.1038/s41587-021-01094-0
- Astraea Troubelshooting KB [DeepCell Mesmer Errors](../troubleshooting/deepcell_mesmer_errors.md)
- Example segmentation logs (to be added)

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.1 | 2025-12-05 | Trevor McKee | Rewritten for operational reproducibility and QC rigor |
| 1.0 | 2025-12-05 | Astraea Team | Initial version |
