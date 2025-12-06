# Spatial Analysis Pipeline SOP

## Purpose

Standard Operating Procedure for **reproducible, standardized spatial analysis** of segmented and phenotyped cell data using the **SCIMAP** and **Squidpy** Python packages.  
This SOP defines required inputs, folder structure, spatial graph construction, neighborhood analysis, clustering, distance metrics, visualization, QC, and Definition of Done so that all analysts follow the same workflow.

---

## 1. Prerequisites

- Completed segmentation (see [Segmentation Pipeline](segmentation_pipeline.md))
- Completed phenotyping (see [Phenotyping Pipeline](phenotyping_pipeline.md))
- Python 3.8+ (recommended 3.9+)
- Cell coordinates and phenotype assignments exported from phenotyping
- Access to project directory with standardized folder structure

---

## 2. Required Inputs

Analysts must have the following before beginning spatial analysis:

### 2.1 Folder Structure (MANDATORY)

```text
project_root/
  raw/
    image.ome.tiff
  segmentation/
    masks/
      mask_<date>.tiff
  phenotyping/
    exports/
      phenotype_results.csv
  spatial/
    logs/
    qc/
    exports/
    figures/
    metadata.json
```

### 2.2 Required Files

From the phenotyping pipeline:

- Cell-level CSV, e.g. `phenotype_results.csv`, containing at minimum:
  - Cell identifier
  - X and Y coordinates (in microns where possible)
  - Phenotype labels
- Optional but recommended:
  - Marker intensity columns
  - Region/ROI identifiers
  - Sample ID / slide ID
- Panel definition (JSON/CSV) and any tissue metadata, if applicable

**Standard column names (preferred):**

- `X_centroid`, `Y_centroid` (or `X`, `Y` if legacy; must be mapped)
- `phenotype` (string label)
- Optional: `sample_id`, `roi_id`, marker intensities like `CD8_mean`, `PDL1_mean`, etc.

---

## 3. Software Requirements

- Python scientific stack:
  - `pandas`, `numpy`, `matplotlib`, `seaborn`
- Spatial analysis packages:
  - **Primary:** `scimap`
  - **Additional / alternative:** `squidpy`, `scikit-learn`, `scipy`, `anndata`
- Jupyter Notebook or JupyterLab

### 3.1 Environment Setup

Create / activate an environment for spatial analysis:

```bash
conda create -n spatial python=3.9
conda activate spatial

pip install scimap squidpy anndata pandas numpy matplotlib seaborn scikit-learn scipy
```

Record environment name and key package versions in `spatial/metadata.json`.

---

## 4. Procedure

### Step 1 — Load Data

Load phenotyping results and verify required columns:

```python
import pandas as pd

cells = pd.read_csv('phenotyping/exports/phenotype_results.csv')

print(f"Loaded {len(cells)} cells")
print("Columns:", cells.columns.tolist())

# Standardize coordinate columns
if {'X_centroid', 'Y_centroid'}.issubset(cells.columns):
    cells['X'] = cells['X_centroid']
    cells['Y'] = cells['Y_centroid']

required = ['X', 'Y', 'phenotype']
missing = [c for c in required if c not in cells.columns]
assert not missing, f"Missing required columns: {missing}"

print("Phenotypes:", cells['phenotype'].unique())
```

If required columns are missing or incorrect → STOP and fix upstream or update the export logic.

---

### Step 2 — Create AnnData Object (SCIMAP / Squidpy Compatible)

Using SCIMAP helper (preferred):

```python
import scimap as sm

adata = sm.pp.create_adata(
    cells,
    x='X',
    y='Y',
    phenotype='phenotype'
)

adata
```

Or manually (Squidpy-style):

```python
import anndata as ad
import numpy as np

intensity_cols = [c for c in cells.columns if c not in ['X','Y','phenotype']]
X_mat = cells[intensity_cols].values if intensity_cols else np.empty((len(cells), 0))

adata = ad.AnnData(
    X=X_mat,
    obs=cells[['phenotype']].copy(),
    obsm={'spatial': cells[['X','Y']].values}
)
```

Log the shape of `adata` and the list of phenotypes to `spatial/logs/run_<date>.txt`.

---

### Step 3 — Build Spatial Graph

#### 3.1 Using SCIMAP (Primary)

```python
adata = sm.tl.spatial_neighbors(
    adata,
    radius=30  # microns; adjust based on tissue context
)
```

Record the radius in `metadata.json` and the log file.

#### 3.2 Using Squidpy (Alternative / Additional)

```python
import squidpy as sq

sq.gr.spatial_neighbors(
    adata,
    coord_type='generic',
    n_neighs=15  # number of neighbors
)

print("Spatial graph connections:",
      adata.obsp['spatial_connectivities'].nnz)
```

**Analyst must choose and document** whether a radius-based (SCIMAP) or k-NN (Squidpy) model is used.

---

### Step 4 — Neighborhood Analysis

#### 4.1 Neighborhood Enrichment (SCIMAP)

```python
enrichment = sm.tl.neighborhood_enrichment(adata)
enrichment.to_csv('spatial/exports/neighborhood_enrichment_scimap.csv')
```

#### 4.2 Neighborhood Enrichment (Squidpy)

```python
sq.gr.nhood_enrichment(adata, cluster_key='phenotype')

import matplotlib.pyplot as plt
sq.pl.nhood_enrichment(
    adata,
    cluster_key='phenotype',
    figsize=(8, 8)
)
plt.tight_layout()
plt.savefig('spatial/figures/neighborhood_enrichment_squidpy.png', dpi=150)
```

Analyst must save at least one enrichment matrix and one visualization.

---

### Step 5 — Spatial Clustering (Microenvironment Communities)

#### 5.1 SCIMAP Leiden Clustering

```python
adata = sm.tl.cluster(
    adata,
    method='leiden',
    resolution=0.5
)
```

Visualization:

```python
sm.pl.spatial_scatter(adata, color='leiden')
```

Save figure to `spatial/figures/leiden_clusters.png`.

#### 5.2 DBSCAN (Alternative Spatial Clusterer)

```python
from sklearn.cluster import DBSCAN

coords = cells[['X','Y']].values
clustering = DBSCAN(eps=50, min_samples=5).fit(coords)

cells['spatial_cluster'] = clustering.labels_
cells['spatial_cluster'].to_csv('spatial/exports/spatial_clusters_dbscan.csv', index=False)

print("DBSCAN clusters:", cells['spatial_cluster'].nunique())
```

Plot:

```python
import matplotlib.pyplot as plt

plt.figure(figsize=(6,6))
scatter = plt.scatter(
    cells['X'], cells['Y'],
    c=cells['spatial_cluster'],
    cmap='tab20', s=5, alpha=0.6
)
plt.colorbar(scatter, label='DBSCAN cluster')
plt.title('Spatial Clusters (DBSCAN)')
plt.xlabel('X (μm)')
plt.ylabel('Y (μm)')
plt.tight_layout()
plt.savefig('spatial/figures/spatial_clusters_dbscan.png', dpi=150)
```

---

### Step 6 — Distance-Based Metrics

Example: distance from CD8+ T cells to tumor cells.

```python
from scipy.spatial.distance import cdist
import numpy as np

cd8 = cells[cells['phenotype'] == 'CD8+ T cell'][['X','Y']].values
tumor = cells[cells['phenotype'] == 'Tumor cell'][['X','Y']].values

if len(cd8) > 0 and len(tumor) > 0:
    distances = cdist(cd8, tumor)
    min_distances = distances.min(axis=1)
    print(f"Mean distance CD8 → tumor: {min_distances.mean():.2f} μm")
else:
    print("Insufficient CD8 or Tumor cells for distance analysis.")
```

Save distribution:

```python
import matplotlib.pyplot as plt

plt.figure(figsize=(5,4))
plt.hist(min_distances, bins=30)
plt.xlabel('Distance to nearest tumor cell (μm)')
plt.ylabel('CD8+ T cell count')
plt.tight_layout()
plt.savefig('spatial/figures/cd8_to_tumor_distance_hist.png', dpi=150)
```

Export summary:

```python
import pandas as pd

pd.Series(min_distances, name='cd8_to_tumor_distance_um').to_csv(
    'spatial/exports/cd8_to_tumor_distance.csv',
    index=False
)
```

---

### Step 7 — Spatial Visualization (MANDATORY)

Analysts must produce at least:

1. **Phenotype spatial map**
2. **Cluster map (Leiden or DBSCAN)**
3. **Neighborhood enrichment heatmap**

Example combined plot:

```python
import matplotlib.pyplot as plt
import seaborn as sns

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Phenotype map
for pheno in cells['phenotype'].unique():
    subset = cells[cells['phenotype'] == pheno]
    axes[0].scatter(
        subset['X'], subset['Y'],
        label=pheno, alpha=0.5, s=8
    )
axes[0].legend(bbox_to_anchor=(1.05, 1), fontsize=8)
axes[0].set_title('Spatial Distribution by Phenotype')
axes[0].set_xlabel('X (μm)')
axes[0].set_ylabel('Y (μm)')

# Spatial clusters (if available)
if 'spatial_cluster' in cells.columns:
    scatter = axes[1].scatter(
        cells['X'], cells['Y'],
        c=cells['spatial_cluster'],
        cmap='tab20', alpha=0.5, s=8
    )
    plt.colorbar(scatter, ax=axes[1], label='Cluster')
    axes[1].set_title('Spatial Clusters')
else:
    axes[1].text(0.5, 0.5, 'No spatial_cluster column', ha='center')

axes[1].set_xlabel('X (μm)')
axes[1].set_ylabel('Y (μm)')

plt.tight_layout()
plt.savefig('spatial/figures/spatial_analysis_overview.png', dpi=150)
plt.show()
```

---

### Step 8 — Export Results (MANDATORY)

Analyst must export:

```python
# Enriched cell table (with clusters, distances if computed)
cells.to_csv('spatial/exports/spatial_analysis_results.csv', index=False)

# Example summary statistics
summary = cells.groupby('phenotype').agg({
    'X': ['mean', 'std'],
    'Y': ['mean', 'std'],
})
summary.to_csv('spatial/exports/spatial_summary_by_phenotype.csv')
```

From SCIMAP:

```python
# Save AnnData with spatial results
adata.write('spatial/exports/adata_spatial.h5ad')
```

From SCIMAP/Squidpy:

- Neighborhood enrichment matrix  
- Interaction or distance matrices, if computed  

---

## 9. Quality Control (MANDATORY)

### QC Criteria

- [ ] Coordinates are correctly oriented (no flipped or rotated axes without documentation)  
- [ ] Spatial graph (radius or k-NN) successfully constructed  
- [ ] Neighborhood enrichment patterns are biologically plausible  
- [ ] Spatial clusters represent coherent tissue regions (no obvious numeric artifacts only)  
- [ ] Distance metrics are computed on sufficient numbers of cells  
- [ ] No NaNs or infinities in exported matrices  
- [ ] Visualizations clearly represent spatial relationships  

If any QC criterion fails, analyst must document the issue and attempt remediation before escalating.

---

## 10. Definition of Done (NON-NEGOTIABLE)

Spatial analysis is considered **DONE** only when:

### Outputs
- [ ] `spatial/exports/adata_spatial.h5ad` saved (if SCIMAP used)  
- [ ] At least one neighborhood enrichment CSV exported  
- [ ] Any distance/interaction matrices used exported as CSV  
- [ ] `spatial/exports/spatial_analysis_results.csv` written  
- [ ] Minimum three figures saved to `spatial/figures/`:
  - Phenotype scatter
  - Cluster scatter (Leiden or DBSCAN)
  - Neighborhood enrichment heatmap  
- [ ] QC notes and any threshold/parameter choices written to `spatial/qc/` and/or `metadata.json`

### Reproducibility
- [ ] The notebook or script used is saved in version control  
- [ ] Package versions and key parameters (radius, n_neighs, DBSCAN eps/min_samples, clustering resolution) logged in `metadata.json` and `spatial/logs/run_<date>.txt`

### Communication
- [ ] Analyst posts summary to ClickUp, including:
  - Which analyses were run (SCIMAP, Squidpy, DBSCAN, distance metrics)  
  - Key biological findings  
  - QC outcomes  
  - File paths to exports and figures  
  - Link to any troubleshooting KB entries created  

If ANY item above is missing → work is returned to the analyst.

---

## 11. Troubleshooting

If issues arise:

1. Reproduce the error or suspicious result.  
2. Capture:
   - Error message
   - Stack trace
   - Screenshot (for plotting issues)  
3. Try at least **two** remedial steps (e.g., adjusting radius, checking coordinate units, subsampling).  
4. Document the issue and attempted fixes in:
   - `../troubleshooting/scimap_common_errors.md` for SCIMAP issues  
   - `../troubleshooting/squidpy_common_errors.md` for Squidpy issues  
5. Only then escalate to a senior analyst / lead.

---

## 12. References

- SCIMAP Documentation: https://scimap.readthedocs.io  
- Squidpy Documentation: https://squidpy.readthedocs.io  
- AnnData: https://anndata.readthedocs.io  
- Spatial omics review: https://www.nature.com/articles/s41592-021-01358-2  
- Internal Troubleshooting KB

---

## 13. Version History

| Version | Date       | Author | Changes                                              |
|---------|------------|--------|------------------------------------------------------|
| 1.1     | 2025-12-05 | McKee  | Merged SCIMAP-based SOP with Squidpy/DBSCAN workflow |
| 1.0     | 2025-12-05 | Astraea Team | Initial SCIMAP-only SOP                         |
