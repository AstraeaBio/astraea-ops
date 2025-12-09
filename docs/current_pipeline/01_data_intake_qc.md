# Stage 1 — Data Intake & QC

This document describes how this stage is **currently** performed across projects.

## Objectives

- Receive and organize raw multiplex imaging data from clients
- Verify data completeness (all expected files, channels, samples present)
- Check file integrity (no corruption, correct formats)
- Validate metadata (channel names, physical units, sample identifiers)
- Perform basic image quality checks (focus, brightness, artifacts)
- Establish standardized project folder structure
- Document all findings and communicate with client if issues detected

## Common Inputs

### Input File Types and Formats

1. **Multiplex imaging data:**
   - **OME-TIFF** (most common, preferred)
     - Multi-channel TIFF with embedded metadata
     - Channel names, physical units (µm/pixel), Z-stack info
     - File sizes: 500MB - 5GB per slide/ROI typical
   - **QPTIFF** (Aperio/Leica format)
     - Pyramidal TIFF for whole-slide imaging
     - Requires conversion or import into QuPath
   - **CZI** (Zeiss format)
     - Proprietary format, requires conversion to OME-TIFF
   - **Raw TIFF stacks**
     - Separate TIFF per channel (less common)
     - Requires manual channel assignment

2. **Metadata files:**
   - **Marker panel definition**
     - CSV or Excel listing markers, channels, expected expression patterns
     - Example columns: `Channel`, `Marker_Name`, `Conjugate`, `Target_Cell_Type`
   - **Sample manifest**
     - CSV listing all samples/slides with identifiers, conditions, batches
     - Example columns: `Sample_ID`, `Slide_ID`, `Condition`, `Batch`, `Date_Acquired`
   - **Imaging parameters**
     - Microscope settings (exposure time, laser power, objective, binning)
     - Physical calibration (µm/pixel, Z-step size if applicable)

3. **Client documentation (if available):**
   - Study design overview
   - Tissue type and preparation method
   - Expected cell populations
   - Analysis goals/questions

## Current Scripts / Tools

### Primary Tools

1. **Manual inspection (QuPath, Fiji/ImageJ):**
   - Load images and check channel visualization
   - Verify channel names match panel definition
   - Inspect for imaging artifacts (out of focus, uneven illumination, edge effects)
   - Most common first step

2. **Python scripts for metadata extraction:**
   - `tifffile` or `bioformats` to read OME-TIFF metadata
   - Extract channel names, physical units, dimensions
   - Example: `python check_metadata.py --input raw/`

3. **File integrity checks:**
   - MD5 checksums (if provided by client)
   - Verify file sizes reasonable
   - Check for file corruption (can image be opened?)

4. **Folder structure setup:**
   - Manual creation or script-based
   - Standard structure: `raw/`, `segmentation/`, `phenotyping/`, `spatial/`, `notebooks/`

### Script Catalog Links

- [check_ome_metadata.md](../scripts_catalog/data_intake/check_ome_metadata.md) - Extract and validate OME-TIFF metadata
- [setup_project_structure.md](../scripts_catalog/data_intake/setup_project_structure.md) - Create standard folders
- [validate_channel_names.md](../scripts_catalog/data_intake/validate_channel_names.md) - Compare channel names to panel definition

## Manual Steps

### Typical Analyst Workflow

#### 1. Receive Data from Client

**Common delivery methods:**
- Google Drive link (most common)
- Cloud storage (AWS S3, GCP bucket)
- External hard drive (for very large datasets)
- Direct upload to GCP VM

**Initial actions:**
- Download to appropriate location (GCP VM or local workstation)
- Document download date, source, contact person
- Check total data size matches client expectations

#### 2. Organize Files into Project Structure

```bash
# Create standard project folders
mkdir -p project_name/{raw,segmentation/{logs,qc,masks},phenotyping/{logs,qc,exports},spatial/{logs,qc,exports,figures},notebooks}

# Move raw data
mv /path/to/client_data/*.ome.tiff project_name/raw/

# Copy metadata files
cp /path/to/panel_definition.csv project_name/raw/
cp /path/to/sample_manifest.csv project_name/raw/
```

#### 3. Extract and Validate Metadata

**Using Python:**

```python
import tifffile
import pandas as pd
from pathlib import Path

# List all OME-TIFF files
raw_dir = Path('project_name/raw')
ome_files = list(raw_dir.glob('*.ome.tiff'))

print(f"Found {len(ome_files)} OME-TIFF files")

# Extract metadata from each file
metadata_list = []

for ome_file in ome_files:
    with tifffile.TiffFile(ome_file) as tif:
        # Get OME-XML metadata
        ome_metadata = tif.ome_metadata

        # Get image dimensions
        page = tif.pages[0]
        shape = page.shape

        # Extract physical pixel size if available
        try:
            tags = page.tags
            x_res = tags['XResolution'].value
            y_res = tags['YResolution'].value
            unit = tags.get('ResolutionUnit', {}).value

            # Convert to µm/pixel
            if unit == 3:  # Centimeters
                mpp_x = 10000 / x_res[0]  # Convert cm to µm
                mpp_y = 10000 / y_res[0]
            else:
                mpp_x = mpp_y = None
        except:
            mpp_x = mpp_y = None

        metadata_list.append({
            'File': ome_file.name,
            'Width': shape[1],
            'Height': shape[0],
            'Channels': tif.series[0].shape[2] if len(tif.series[0].shape) > 2 else 1,
            'MPP_X': mpp_x,
            'MPP_Y': mpp_y
        })

# Create summary DataFrame
metadata_df = pd.DataFrame(metadata_list)
metadata_df.to_csv('project_name/raw/file_metadata_summary.csv', index=False)
print(metadata_df)

# Check for inconsistencies
if metadata_df['MPP_X'].isna().any():
    print("WARNING: Some files missing physical pixel size (mpp)")

if metadata_df['Channels'].nunique() > 1:
    print("WARNING: Files have different number of channels")
    print(metadata_df.groupby('Channels')['File'].apply(list))
```

#### 4. Visual QC of Images

**Using QuPath:**

1. Open QuPath
2. `File → Open → Select OME-TIFF`
3. Check each channel:
   - Navigate through channels using brightness/contrast panel
   - Look for:
     - **Out of focus:** Blurry nuclei, indistinct cell boundaries
     - **Uneven illumination:** Brightness gradient across image
     - **Saturation:** Pixels at max value (clipped signal)
     - **Autofluorescence:** Background signal patterns
     - **Edge artifacts:** Vignetting, black borders
     - **Stitching artifacts:** Visible tile boundaries (if whole-slide)

4. Document findings in QC log

**QC Checklist:**
- [ ] All expected channels present
- [ ] Channel names match panel definition
- [ ] Nuclear channel (DAPI/Hoechst) clear and in focus
- [ ] Membrane/cytoplasm channels show cell boundaries
- [ ] No major imaging artifacts
- [ ] Consistent brightness across samples/slides
- [ ] Physical calibration (mpp) present and reasonable

#### 5. Validate Against Sample Manifest

```python
import pandas as pd

# Load sample manifest
manifest = pd.read_csv('project_name/raw/sample_manifest.csv')

# List actual files
import os
actual_files = [f for f in os.listdir('project_name/raw') if f.endswith('.ome.tiff')]

# Extract sample IDs from filenames (project-specific logic)
actual_sample_ids = [f.replace('.ome.tiff', '').split('_')[0] for f in actual_files]

# Compare
expected_sample_ids = manifest['Sample_ID'].tolist()

missing = set(expected_sample_ids) - set(actual_sample_ids)
extra = set(actual_sample_ids) - set(expected_sample_ids)

if missing:
    print(f"WARNING: Missing expected samples: {missing}")

if extra:
    print(f"INFO: Extra files not in manifest: {extra}")

if not missing and not extra:
    print(f"SUCCESS: All {len(expected_sample_ids)} expected samples present")
```

#### 6. Document Findings and Communicate

**Create intake QC report:**

```markdown
# Data Intake QC Report

**Project:** [Project Name]
**Client:** [Client Name]
**Analyst:** [Your Name]
**Date:** [Date]

## Data Received

- **Number of files:** X OME-TIFF files
- **Total data size:** XX GB
- **Delivery method:** Google Drive
- **Download date:** YYYY-MM-DD

## Metadata Validation

- [x] All expected samples present (N samples)
- [x] Channel names match panel definition (36 channels)
- [x] Physical calibration present (0.325 µm/pixel)
- [ ] Issue: Sample ABC123 missing from delivery → contacted client

## Image Quality Checks

- [x] Nuclear channel clear and in focus (spot-checked 10%)
- [x] No major artifacts detected
- [ ] Issue: Sample XYZ456 shows uneven illumination in Slide 2 → flagged for QC

## Folder Structure

- [x] Standard folders created
- [x] Raw data organized in `raw/`
- [x] Metadata files documented

## Issues / Actions

1. **Missing sample:** Contacted client on YYYY-MM-DD, awaiting response
2. **Uneven illumination:** Proceeding with analysis, will monitor in segmentation QC

## Ready for Segmentation?

- [ ] **HOLD** - waiting for missing sample
- [x] **GO** - proceeding with available data
```

## Variations Between Projects

### By Imaging Platform

**CODEX (Akoya):**
- OME-TIFF with 30-60 channels typical
- High resolution (0.3-0.4 µm/pixel)
- Channel names standardized (usually)
- May include Z-stacks

**PhenoCycler/CODEX+ (Akoya):**
- Similar to CODEX
- Larger tile sets (whole-slide imaging)
- Requires stitching QC

**Hyperion (Fluidigm IMC):**
- MCD format (requires conversion to OME-TIFF)
- 30-40 metal channels
- Lower resolution (~1 µm/pixel)
- ROI-based (not whole-slide)

**mIF (Multiplex Immunofluorescence):**
- Typically 4-8 channels
- Higher resolution
- May have separate images per marker (requires stacking)

### By Client Sophistication

**Well-organized clients:**
- Provide OME-TIFF with correct metadata
- Include detailed sample manifest
- Channel names match panel definition
- Minimal QC issues

**Disorganized clients:**
- Mixed file formats (TIFF, CZI, proprietary)
- Missing or incorrect channel names
- No sample manifest or incomplete
- Physical calibration missing
- Requires significant back-and-forth communication

### By Data Volume

**Small projects (1-10 samples):**
- Manual download and organization sufficient
- Full visual QC of all samples feasible

**Large projects (50+ samples):**
- Automated metadata extraction essential
- Spot-check visual QC (10-20% of samples)
- Batch download scripts needed

## Known Issues

### 1. Missing or Incorrect Physical Calibration

**Problem:** OME-TIFF missing mpp (microns per pixel) metadata, or incorrect value.

**Symptoms:**
- No `PhysicalSizeX` tag in OME-XML
- mpp value doesn't match known microscope spec
- Example: 1.0 µm/pixel reported but should be 0.325 µm/pixel

**Current handling:**
- Check against microscope specifications (if known)
- Contact client for correct value
- Manually add to metadata.json for downstream use

**Prevention:**
- Request imaging parameters sheet from client upfront
- Validate during intake QC, not later in pipeline

### 2. Inconsistent Channel Naming

**Problem:** Channel names don't match panel definition or are generic (Channel_0, Channel_1, etc.).

**Current handling:**
- Create rename mapping CSV: `Original_Name → Correct_Name`
- Document in project notes
- Apply renaming during feature extraction

**Example mapping:**
```csv
Original,Correct
Channel_0,DAPI
Channel_1,CD3e
Channel_2,CD8
```

### 3. File Corruption

**Problem:** File cannot be opened or appears corrupted (e.g., truncated download).

**Detection:**
```python
import tifffile

try:
    img = tifffile.imread('file.ome.tiff')
    print("File OK")
except Exception as e:
    print(f"ERROR: {e}")
```

**Current handling:**
- Re-download if possible
- Request re-upload from client
- Document in QC report

### 4. Missing Samples

**Problem:** Sample manifest lists samples not present in delivery.

**Current handling:**
- Contact client immediately
- Document in QC report
- Decide: HOLD analysis or proceed with available data

### 5. Imaging Artifacts

**Common artifacts:**
- **Out of focus:** Notify client, may need re-imaging
- **Saturation:** Flag for segmentation QC (may affect intensity measurements)
- **Uneven illumination:** Proceed with caution, may require flat-field correction
- **Stitching errors:** Exclude affected regions or re-stitch

**Documentation:**
- Take screenshots of artifacts
- Note affected samples/regions in QC report
- Communicate with client if re-imaging needed

### 6. Mixed File Formats

**Problem:** Client provides multiple formats (OME-TIFF, CZI, QPTIFF).

**Current handling:**
- Convert all to OME-TIFF using Fiji or bioformats
- Document conversion in QC notes
- Validate channel order after conversion

**Conversion example (Fiji):**
```
File → Import → Bio-Formats → Select file
File → Export → OME-TIFF
```

### 7. Unclear Sample Identifiers

**Problem:** Filenames cryptic or don't match manifest.

**Examples:**
- `IMG_20231215_001.ome.tiff` (no sample ID)
- `Sample A.ome.tiff` (ambiguous)

**Current handling:**
- Request filename key from client
- Create filename mapping document
- Standardize filenames if necessary

## Success Metrics

From recent projects:

**Well-organized intake (Nguyen Lab lymph nodes):**
- **4 samples** received
- **All metadata correct** (mpp, channel names)
- **No missing files**
- **QC completed:** 1 hour
- **Issues:** None

**Problematic intake (example):**
- **50 samples** received
- **Missing mpp** for all files → required client follow-up (2 days delay)
- **10 channels** unnamed (Channel_0, Channel_1, etc.) → manual mapping required
- **3 samples** corrupted → re-download (1 day delay)
- **QC completed:** 1 week including client communication

## Next Steps / Improvements Needed

1. **Develop automated intake QC script** (check files, extract metadata, generate report)
2. **Create intake QC template** with standard checklist
3. **Build file format converter** for common proprietary formats (CZI, etc.)
4. **Establish client onboarding docs** (what to provide, how to name files)
5. **Implement automated file integrity checks** (checksums)
6. **Create data delivery SOP** for clients to follow
7. **Build intake QC dashboard** for rapid visual review
