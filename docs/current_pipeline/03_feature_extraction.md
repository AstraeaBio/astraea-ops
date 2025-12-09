# Stage 3 — Feature Extraction

This document describes how this stage is **currently** performed across projects.

## Objectives

- Extract per-cell marker intensities from raw multiplex images using segmentation masks
- Calculate morphological features (area, perimeter, shape metrics)
- Combine segmentation masks, channel intensities, and spatial coordinates into cell-level tables
- Prepare standardized cell measurement tables for downstream phenotyping and spatial analysis

## Common Inputs

### Input File Types and Formats

1. **Segmentation masks:**
   - TIFF format with labeled regions (each cell has unique integer ID)
   - Typically 16-bit or 32-bit to support >65,535 cells
   - Generated from Stage 2 (Segmentation)
   - Path: `segmentation/masks/mask_<timestamp>.tiff`

2. **Raw multiplex images:**
   - OME-TIFF or TIFF with all marker channels
   - Must have same dimensions as segmentation mask
   - Channel order documented in metadata
   - Path: `raw/image.ome.tiff`

3. **Marker panel definitions:**
   - CSV or JSON listing all markers and their channel indices
   - Example columns: `Channel`, `Marker_Name`, `Expected_Expression`
   - Used to name output columns correctly

4. **Segmentation metadata:**
   - `segmentation/metadata.json` with mpp, versions, parameters
   - Required for correct spatial coordinate calculation

## Current Scripts / Tools

### Primary Tools

1. **QuPath (v0.4.0+)** - Most common approach
   - Import segmentation masks as cell objects
   - Extract marker intensities (mean, median, std dev) for each cell
   - Calculate morphological features automatically
   - Export to CSV with all measurements
   - See [phenotyping_pipeline.md](../sops/phenotyping_pipeline.md) for QuPath-based extraction

2. **Python/scikit-image** - Alternative for automated workflows
   - `skimage.measure.regionprops` for morphological features
   - Custom intensity extraction from raw images
   - Direct export to pandas DataFrame/CSV
   - Faster for batch processing

3. **CellProfiler** - Used occasionally for specialized pipelines
   - GUI-based or batch mode
   - Extensive feature library
   - Less common in current workflows

### Script Catalog Links

- [qupath_intensity_extraction.md](../scripts_catalog/feature_extraction/qupath_intensity_extraction.md) - QuPath Groovy scripts
- [python_regionprops.md](../scripts_catalog/feature_extraction/python_regionprops.md) - Python-based extraction
- [batch_feature_extraction.md](../scripts_catalog/feature_extraction/batch_feature_extraction.md) - Multi-sample processing

## Manual Steps

### Typical Analyst Workflow (QuPath-based)

#### 1. Load Image and Import Segmentation Mask

```groovy
import qupath.lib.objects.PathObjects
import qupath.lib.images.servers.LabeledImageServer

// Path to segmentation mask
def labelPath = '/path/to/segmentation/masks/mask_20231215.tiff'

// Create labeled image server
def labelServer = new LabeledImageServer.Builder(labelPath)
    .useLabelColors()
    .build()

// Import all labels as cell objects
def labels = labelServer.getLabels()
for (label in labels) {
    def roi = labelServer.getROI(label)
    def cell = PathObjects.createCellObject(roi, null, null)
    addObject(cell)
}

fireHierarchyUpdate()
println "Imported ${labels.size()} segmented cells"
```

#### 2. Extract Marker Intensities

```groovy
import qupath.lib.analysis.features.ObjectMeasurements

// Get all measurement types
def measurements = ObjectMeasurements.Measurements.values()
def compartments = ObjectMeasurements.Compartments.values()

// Extract intensities for all cells
for (cell in getDetectionObjects()) {
    ObjectMeasurements.addIntensityMeasurements(
        getCurrentServer(),
        cell,
        1.0,  // downsample factor (1.0 = full resolution)
        measurements,
        compartments
    )
}

fireHierarchyUpdate()
println "Intensity measurements added to ${getDetectionObjects().size()} cells"
```

**Extracted features per marker:**
- `Cell: <Marker> mean` - Mean intensity within cell boundary
- `Cell: <Marker> median` - Median intensity
- `Cell: <Marker> std dev` - Standard deviation
- `Cell: <Marker> min` - Minimum intensity
- `Cell: <Marker> max` - Maximum intensity
- `Nucleus: <Marker> mean` - Nuclear compartment (if available)
- `Cytoplasm: <Marker> mean` - Cytoplasm compartment (if available)

#### 3. Calculate Morphological Features

QuPath automatically calculates:
- `Cell: Area` - Cell area in µm² (if mpp set correctly)
- `Cell: Perimeter` - Cell perimeter in µm
- `Cell: Circularity` - Shape metric (1.0 = perfect circle)
- `Cell: Max diameter` - Maximum cell dimension
- `Cell: Min diameter` - Minimum cell dimension
- `Centroid X µm`, `Centroid Y µm` - Cell center coordinates

#### 4. Export Cell Measurements

```groovy
// Export path
def exportPath = buildFilePath(PROJECT_BASE_DIR, 'phenotyping', 'exports', 'cell_measurements.csv')

// Export all measurements
saveDetectionMeasurements(exportPath)

println "Cell measurements exported to ${exportPath}"
```

**Output CSV structure:**
```
Cell_ID, Centroid X µm, Centroid Y µm, Cell: Area, Cell: CD3e mean, Cell: CD8 mean, ...
1, 1234.5, 567.8, 125.3, 45.2, 12.3, ...
2, 1250.1, 572.4, 98.7, 120.5, 95.4, ...
```

### Typical Analyst Workflow (Python-based)

```python
import numpy as np
import tifffile
from skimage.measure import regionprops_table
import pandas as pd

# Load segmentation mask
mask = tifffile.imread('segmentation/masks/mask_20231215.tiff')

# Load raw multiplex image
img = tifffile.imread('raw/image.ome.tiff')

# Extract morphological properties
props = regionprops_table(
    mask,
    intensity_image=img,
    properties=['label', 'area', 'centroid', 'perimeter', 'major_axis_length', 'minor_axis_length']
)

# Convert to DataFrame
df = pd.DataFrame(props)

# Extract marker intensities for each cell
marker_names = ['DAPI', 'CD3e', 'CD8', 'CD4', 'CD45', ...]  # From panel definition

for i, marker in enumerate(marker_names):
    channel_img = img[0, :, :, i]  # Adjust indexing based on image structure

    intensities_mean = []
    intensities_median = []

    for cell_id in range(1, mask.max() + 1):
        cell_pixels = channel_img[mask == cell_id]
        intensities_mean.append(cell_pixels.mean() if len(cell_pixels) > 0 else 0)
        intensities_median.append(np.median(cell_pixels) if len(cell_pixels) > 0 else 0)

    df[f'{marker}_mean'] = intensities_mean
    df[f'{marker}_median'] = intensities_median

# Convert pixel coordinates to microns
mpp = 0.5  # microns per pixel (from metadata)
df['X_centroid_um'] = df['centroid-1'] * mpp
df['Y_centroid_um'] = df['centroid-0'] * mpp

# Export
df.to_csv('phenotyping/exports/cell_measurements.csv', index=False)
print(f"Extracted features for {len(df)} cells")
```

## Variations Between Projects

### By Platform

**QuPath-based (most common):**
- Interactive GUI for visualization and QC
- Groovy scripting for automation
- Good for manual corrections/annotations
- Export to CSV for downstream Python analysis

**Python-only:**
- Fully automated batch processing
- Integration with Jupyter notebooks
- Direct connection to phenotyping and spatial analysis code
- Faster for large-scale projects

**Hybrid (common for complex projects):**
- QuPath for initial extraction and QC
- Python for additional feature engineering
- Example: QuPath extracts intensities, Python calculates custom spatial features

### By Feature Requirements

**Basic intensity only:**
- Mean marker intensity per cell
- Fast extraction
- Sufficient for simple phenotyping

**Comprehensive feature set:**
- Mean, median, std dev, min, max per marker
- Nuclear vs cytoplasm compartmentalization
- Morphological features (shape, size)
- Texture features (Haralick features if needed)
- Required for advanced phenotyping or ML classification

**Spatial context features:**
- Distance to tissue boundaries
- Local cell density
- Neighborhood composition
- Typically extracted in Stage 5 (Spatial Analysis), but sometimes done here

### By Tissue Type

**Lymph nodes:**
- High cell density (features may be less reliable in crowded regions)
- Clear nuclear staining (compartment separation works well)
- Typically 30-40 markers extracted

**Tumor microenvironment:**
- Variable cell sizes (epithelial cells much larger than immune cells)
- Morphological features more important for tumor vs immune distinction
- May include tumor nest annotations as additional features

**Bone marrow:**
- Very small cells (morphological features less discriminative)
- Focus on marker intensities
- May require higher resolution for accurate feature extraction

## Known Issues

### 1. Intensity Normalization Challenges

**Problem:** Raw intensity values vary dramatically between slides/batches due to staining and imaging differences.

**Current handling:**
- Extract raw intensities first, normalize during phenotyping stage
- Document imaging settings (exposure time, laser power) in metadata
- Use positive control regions for batch correction

### 2. Background Intensity Estimation

**Problem:** Need to determine what constitutes "positive" vs "negative" marker expression.

**Current approach:**
- Include background regions (no cells) in measurement
- Calculate per-marker background median/mean
- Subtract background during phenotyping, not during extraction
- Alternatively: use negative control cells if available

### 3. Compartment Misidentification

**Problem:** Nuclear vs cytoplasm segmentation errors lead to incorrect compartment assignments.

**Current mitigation:**
- Use whole-cell measurements as primary features
- Compartment-specific measurements as secondary/validation
- Visual QC of compartment boundaries in QuPath

### 4. Missing Cells in Extraction

**Problem:** Some cells in segmentation mask don't appear in exported CSV.

**Causes:**
- Cells touching image edges excluded automatically by some tools
- Very small cells (<10 pixels) filtered out
- Label ID conflicts (overlapping cells assigned same ID)

**Detection:**
```python
# Check cell count consistency
mask = tifffile.imread('mask.tiff')
expected_cells = mask.max()
csv_cells = len(pd.read_csv('cell_measurements.csv'))
print(f"Mask cells: {expected_cells}, CSV cells: {csv_cells}, Missing: {expected_cells - csv_cells}")
```

**Current handling:**
- Report discrepancy in QC
- Investigate if >5% cells missing
- Document exclusion criteria

### 5. Channel Mismatch Errors

**Problem:** Wrong channel extracted for a marker due to indexing errors.

**Symptoms:**
- Marker intensity distributions don't match expected biology
- All cells negative for known-positive marker

**Prevention:**
- Always visualize channels in QuPath before extraction
- Document channel order in panel definition CSV
- QC checks: plot intensity distributions, compare to positive controls

### 6. Slow Extraction for Large Images

**Problem:** Feature extraction on 100,000+ cells takes hours.

**Current optimization:**
- Python regionprops faster than QuPath for large datasets
- Parallel processing across multiple images
- Extract only required features (don't calculate everything if not needed)

### 7. Memory Errors with High-Resolution Images

**Problem:** Loading full whole-slide image into memory causes crashes.

**Current handling:**
- Tile-based extraction (process regions separately, concatenate results)
- Downsample raw image for feature extraction (if acceptable)
- Use QuPath (handles large images efficiently with pyramidal formats)

### 8. Inconsistent Column Naming

**Problem:** Different projects/tools produce different column names for same feature.

**Examples:**
- `Centroid X µm` vs `X_centroid` vs `X` vs `Centroid_X_um`
- `Cell: CD8 mean` vs `CD8_mean` vs `CD8_Mean_Intensity`

**Current handling:**
- Standardize names during phenotyping data loading
- Maintain rename mapping dictionary per project
- Slowly converging on standard schema (see pain points)

## Success Metrics

From recent projects:

**Lymph node samples (Nguyen Lab):**
- **~100,000 cells** extracted across 4 slides
- **36 markers** per cell (mean intensities)
- **Morphological features:** Area, perimeter, circularity
- **Processing time:** ~10 minutes per slide (QuPath with Groovy script)
- **Completeness:** 99.8% of cells from segmentation mask present in CSV

**Tumor microenvironment:**
- **Variable cell counts:** 500-5000 per ROI
- **30-40 markers** typical
- **Compartment separation:** Nuclear vs cytoplasm for key markers
- **QC:** Visual inspection of 10% of cells for accuracy

## Next Steps / Improvements Needed

1. **Standardize output CSV schema** across all projects (column naming, units, required fields)
2. **Automate background intensity estimation** per marker per slide
3. **Develop feature extraction QC dashboard** (intensity distributions, cell count checks, missing cells)
4. **Build feature extraction pipeline** with automated retry on failure
5. **Create marker panel library** with standard channel orders for common panels
6. **Implement parallel extraction** for multi-region/multi-sample projects
7. **Add feature validation tests** (e.g., marker colocalization checks, morphology sanity checks)
8. **Document QuPath project setup** with standard settings for reproducibility
