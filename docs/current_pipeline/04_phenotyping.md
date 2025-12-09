# Stage 4 — Phenotyping

This document describes how this stage is **currently** performed across projects.

## Objectives

- Assign cell types or states based on marker expression.
- Optionally train or apply supervised classifiers.
- Create hierarchical phenotyping schemes from broad categories to refined functional states.

## Common Inputs

### Input File Types and Formats

1. **CSV/TSV files from QuPath or segmentation pipeline:**
   - Cell-level measurements with marker intensities
   - Required columns: Cell ID, X/Y coordinates, marker mean/median/std intensities
   - Example: `phenotype_results.csv` with columns like `CD3e Mean`, `CD8 Mean`, `HLA-DR Mean`

2. **AnnData H5AD files:**
   - `.X` matrix: marker expression values (cells × markers)
   - `.obs`: cell metadata (coordinates, sample ID, region annotations)
   - `.var`: marker metadata
   - Used when integrating with scanpy/SCIMAP workflows

3. **Marker panel definitions:**
   - JSON or CSV defining marker names, expected positivity thresholds
   - Example: `channels.csv` listing all 36+ markers with biological roles

4. **Pre-existing classification rules:**
   - Decision trees or threshold definitions from prior projects
   - Documented in project-specific metadata files

## Current Scripts / Tools

### Primary Tools

1. **QuPath scripting (Groovy)** - See [phenotyping_pipeline.md](../sops/phenotyping_pipeline.md)
   - Threshold-based classification
   - Composite classifiers for multi-marker phenotypes

2. **Python-based hierarchical phenotyping:**
   - Custom decision trees using pandas
   - Chunked processing for large datasets (5000+ cells/chunk)
   - See example notebooks in existing pipelines

3. **Scanpy workflows:**
   - Leiden clustering on marker expression
   - Marker-based annotation of clusters
   - Integration with dimensional reduction (UMAP/PCA)

### Script Catalog Links

- [apply_thresholds.md](../scripts_catalog/phenotyping/apply_thresholds.md) - Threshold-based classification
- [ml_classifier_training.md](../scripts_catalog/phenotyping/ml_classifier_training.md) - Machine learning approaches
- [classifier_application.md](../scripts_catalog/phenotyping/classifier_application.md) - Applying trained classifiers

## Manual Steps

### Typical Analyst Workflow

1. **Load data and apply log transformation:**
   ```python
   import pandas as pd
   import numpy as np

   df = pd.read_csv('raw_measurements.csv')

   # Log transform all marker intensities
   marker_cols = [col for col in df.columns if 'Mean' in col]
   for col in marker_cols:
       df[f'{col}_log'] = np.log1p(df[col])
   ```

2. **Define hierarchical phenotyping scheme:**

   **Example from Nguyen Lab lymph node project:**

   **Level 1:** Immune vs Epithelial vs Other
   - Based on CD45 (immune) and Pan-Cytokeratin (epithelial)

   **Level 2:** Lymphoid vs Myeloid (within Immune)
   - Lymphoid: CD3e+ (T cells), CD20+/CD21+ (B cells)
   - Myeloid: CD68+ (macrophages), CD14+ (monocytes), CD11c+ (dendritic cells)

   **Level 3:** Major cell types (11 types)
   - Cyt T, Helper T, B Cell, Macrophage, Dendritic, Monocyte, NK Cell

   **Level 4:** Refined functional phenotypes (36 types)
   - Examples: Act Cyt T, PD-1+ Tc, Ex Tc, T reg, Th1 Helper T, Plasma B, Ant Pres Macrophage

3. **Apply decision tree logic:**
   ```python
   def classify_level_1(row):
       if row['CD45 Mean'] > threshold_cd45:
           return 'Immune'
       elif row['Pan-Cytokeratin Mean'] > threshold_panck:
           return 'Epithelial'
       else:
           return 'Other'

   df['Level_1'] = df.apply(classify_level_1, axis=1)
   ```

4. **Validate phenotypes using visualization:**
   - Plot UMAP colored by phenotype
   - Generate heatmaps of marker expression by phenotype
   - Check for biologically implausible combinations

5. **QC checks:**
   - Ensure <5% cells remain "Unclassified"
   - Verify marker expression patterns match known biology
   - Check phenotype proportions across samples for consistency

6. **Export results:**
   ```python
   df.to_csv('phenotyping/exports/phenotyped_cells.csv', index=False)

   # Summary statistics
   phenotype_counts = df['Level_4'].value_counts()
   phenotype_counts.to_csv('phenotyping/qc/phenotype_summary.csv')
   ```

## Variations Between Projects

### By Tissue Type

**Lymph nodes (Nguyen Lab):**
- 36 refined phenotypes with 4-level hierarchy
- Focus on T cell exhaustion states (PD-1+, TOX+, CD39+)
- Antigen presentation markers (HLA-DR, CD11c)
- Chunked processing due to 100,000+ cells per sample

**Tumor microenvironment:**
- Typically 10-15 major phenotypes
- Focus on tumor vs immune vs stroma
- Activation/exhaustion markers critical
- Often includes spatial context (tumor core vs margin)

**Bone marrow:**
- Hematopoietic lineage markers
- Progenitor vs mature cell states
- Typically more markers (40-50 panel)

### By Platform

**QuPath-based:**
- Manual threshold definition in GUI
- Groovy scripting for batch classification
- Export to CSV for downstream Python analysis

**Python-only workflows:**
- Direct import of segmentation + intensity measurements
- Pandas-based decision trees
- Integration with scanpy for clustering-based phenotyping

**Hybrid approaches (most common):**
- QuPath for initial broad classification
- Python for refined hierarchical phenotyping
- Validation using both UMAP clustering and marker thresholds

### By Analysis Goal

**Exploratory (unsupervised):**
- Leiden clustering on all markers
- Manual annotation of clusters based on marker expression
- Iterative refinement

**Hypothesis-driven (supervised):**
- Pre-defined decision trees
- Fixed thresholds from literature or controls
- Consistent across batches/samples

## Known Issues

### 1. Threshold Sensitivity

**Problem:** Small changes in threshold values dramatically change phenotype assignments.

**Current workaround:**
- Use positive control regions to validate thresholds
- Document threshold values in metadata.json
- Apply same thresholds across all samples in a batch

**Example from Nguyen Lab:**
- CD45 threshold: validated using known lymphocyte-rich regions
- Resulted in ~85% cells classified as "Immune" (biologically expected)

### 2. Memory Issues with Large Datasets

**Problem:** 100,000+ cells with 36+ markers causes memory errors.

**Current solution:**
- Chunked processing (5000 cells per chunk)
- Save intermediate results to disk
- Use parquet format for compression

```python
chunk_size = 5000
for i in range(0, len(df), chunk_size):
    chunk = df.iloc[i:i+chunk_size]
    chunk_classified = apply_phenotyping(chunk)
    chunk_classified.to_csv(f'temp_chunk_{i}.csv', index=False)

# Concatenate all chunks
all_chunks = [pd.read_csv(f'temp_chunk_{i}.csv')
              for i in range(0, len(df), chunk_size)]
final_df = pd.concat(all_chunks, ignore_index=True)
```

### 3. Conflicting Marker Combinations

**Problem:** Cells positive for mutually exclusive markers (e.g., CD4+ CD8+).

**Current approach:**
- Use intensity-based tie-breaking: assign to higher-intensity marker
- Flag cells with conflicting markers for manual review
- Report percentage of conflicting cells in QC

**Example:**
```python
# If both CD4 and CD8 are above threshold, use intensity
if (row['CD4 Mean'] > threshold_cd4) and (row['CD8 Mean'] > threshold_cd8):
    if row['CD4 Mean'] > row['CD8 Mean']:
        return 'Helper T'
    else:
        return 'Cyt T'
```

### 4. Batch Effects in Phenotyping

**Problem:** Different staining batches show shifted intensity distributions.

**Current mitigation:**
- Batch-specific threshold calibration (not ideal)
- Harmony or Combat batch correction before phenotyping
- Quantile normalization across samples

**From Nguyen Lab pipeline:**
- Applied Harmony batch correction on PCA space before clustering
- Used slide-specific positive controls to validate thresholds

### 5. Missing or Corrupted Intensity Values

**Problem:** NaN or zero values in marker intensity columns.

**Detection:**
```python
# Check for missing values
missing_per_marker = df[marker_cols].isna().sum()
print(missing_per_marker[missing_per_marker > 0])

# Check for suspicious zeros
zero_counts = (df[marker_cols] == 0).sum()
print(zero_counts[zero_counts > len(df) * 0.1])  # >10% zeros is suspicious
```

**Current handling:**
- Exclude cells with >3 missing marker values
- Document exclusion criteria in QC report
- Investigate upstream segmentation if >5% cells affected

### 6. Inconsistent Marker Naming

**Problem:** Different projects use different naming conventions (spaces, underscores, capitalization).

**Current standardization:**
- Create `channels.csv` with canonical names
- Rename columns at data loading:
```python
rename_map = {
    'CD8 Mean': 'CD8_mean',
    'CD 8 Mean': 'CD8_mean',
    'cd8_Mean': 'CD8_mean'
}
df.rename(columns=rename_map, inplace=True)
```

## Success Metrics

From recent Nguyen Lab project:
- **36 phenotypes** defined with 4-level hierarchy
- **<1% cells** remained unclassified
- **Processing time:** ~30 minutes for 100,000 cells (chunked)
- **Validation:** Phenotypes matched expected lymph node biology
- **Reproducibility:** Same thresholds applied across 4 lymph nodes with consistent results

## Next Steps / Improvements Needed

1. Automate threshold selection using positive/negative control regions
2. Develop standard phenotyping templates for common tissue types
3. Create validation plots automatically (UMAP + marker heatmaps)
4. Implement unit tests for phenotyping functions
5. Build web interface for threshold selection and QC visualization
