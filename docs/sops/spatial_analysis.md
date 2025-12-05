# Spatial Analysis SOP

## Purpose

Standard Operating Procedure for performing spatial analysis on segmented and phenotyped cell data.

## Prerequisites

- Completed segmentation (see [Segmentation Pipeline](segmentation_pipeline.md))
- Completed phenotyping (see [Phenotyping Pipeline](phenotyping_pipeline.md))
- Python 3.8+ with spatial analysis packages
- Cell coordinates and phenotype assignments

## Equipment/Software

- Python scientific stack
- Spatial analysis packages (squidpy, scikit-learn, scipy)
- Visualization libraries (matplotlib, seaborn)

## Procedure

### Step 1: Environment Setup

Install required packages:

```bash
pip install squidpy pandas numpy matplotlib seaborn scikit-learn scipy
```

Activate environment:

```bash
conda activate spatial
# or
source venv/bin/activate
```

### Step 2: Load Data

Import cell data with coordinates and phenotypes:

```python
import pandas as pd
import numpy as np

# Load phenotyping results
cells = pd.read_csv('phenotype_results.csv')

# Required columns: X, Y, phenotype
print(f"Loaded {len(cells)} cells")
print(f"Columns: {cells.columns.tolist()}")
print(f"Phenotypes: {cells['phenotype'].unique()}")
```

### Step 3: Build Spatial Graph

Construct neighborhood graph:

```python
import squidpy as sq
import anndata as ad

# Create AnnData object
adata = ad.AnnData(
    X=cells[['intensity_col1', 'intensity_col2']].values,
    obs=cells[['phenotype']],
    obsm={'spatial': cells[['X', 'Y']].values}
)

# Build spatial graph
sq.gr.spatial_neighbors(
    adata,
    coord_type='generic',
    n_neighs=15  # Number of neighbors
)

print(f"Spatial graph built with {adata.obsp['spatial_connectivities'].nnz} connections")
```

### Step 4: Neighborhood Analysis

Analyze cell type neighborhoods:

```python
# Compute neighborhood enrichment
sq.gr.nhood_enrichment(
    adata,
    cluster_key='phenotype'
)

# Visualize enrichment
sq.pl.nhood_enrichment(
    adata,
    cluster_key='phenotype',
    figsize=(8, 8)
)
plt.savefig('neighborhood_enrichment.png', dpi=150)
```

### Step 5: Spatial Clustering

Identify spatial communities:

```python
from sklearn.cluster import DBSCAN

# DBSCAN clustering
coords = cells[['X', 'Y']].values
clustering = DBSCAN(eps=50, min_samples=5).fit(coords)

cells['spatial_cluster'] = clustering.labels_
print(f"Found {cells['spatial_cluster'].nunique()} spatial clusters")
```

### Step 6: Distance Analysis

Compute cell-cell distances:

```python
from scipy.spatial.distance import cdist

# Calculate pairwise distances between phenotypes
phenotype_a = cells[cells['phenotype'] == 'CD8+ T cell'][['X', 'Y']].values
phenotype_b = cells[cells['phenotype'] == 'Tumor cell'][['X', 'Y']].values

distances = cdist(phenotype_a, phenotype_b)
min_distances = distances.min(axis=1)

print(f"Mean distance from CD8+ T cells to nearest Tumor cell: {min_distances.mean():.2f}")
```

### Step 7: Visualization

Create spatial plots:

```python
import matplotlib.pyplot as plt
import seaborn as sns

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Phenotype spatial map
for phenotype in cells['phenotype'].unique():
    subset = cells[cells['phenotype'] == phenotype]
    axes[0].scatter(
        subset['X'], subset['Y'],
        label=phenotype, alpha=0.5, s=10
    )
axes[0].legend(bbox_to_anchor=(1.05, 1))
axes[0].set_title('Spatial Distribution by Phenotype')
axes[0].set_xlabel('X (μm)')
axes[0].set_ylabel('Y (μm)')

# Spatial clusters
scatter = axes[1].scatter(
    cells['X'], cells['Y'],
    c=cells['spatial_cluster'], cmap='tab20', alpha=0.5, s=10
)
axes[1].set_title('Spatial Clusters')
axes[1].set_xlabel('X (μm)')
axes[1].set_ylabel('Y (μm)')
plt.colorbar(scatter, ax=axes[1], label='Cluster')

plt.tight_layout()
plt.savefig('spatial_analysis_results.png', dpi=150)
plt.show()
```

### Step 8: Export Results

Save analysis outputs:

```python
# Export enriched cell data
cells.to_csv('spatial_analysis_results.csv', index=False)

# Export summary statistics
summary = cells.groupby('phenotype').agg({
    'X': ['mean', 'std'],
    'Y': ['mean', 'std'],
    'spatial_cluster': 'nunique'
})
summary.to_csv('spatial_summary.csv')

print("Results exported successfully")
```

## Quality Criteria

- [ ] Spatial graph correctly captures local neighborhoods
- [ ] Neighborhood enrichment patterns are biologically meaningful
- [ ] Spatial clusters represent coherent tissue regions
- [ ] Distance metrics are computed correctly
- [ ] Visualizations accurately represent spatial relationships

## Troubleshooting

- For coordinate issues, verify units (pixels vs microns)
- For memory issues with large datasets, consider downsampling or chunking
- For unexpected enrichment patterns, validate phenotype assignments

## References

- Squidpy Documentation: https://squidpy.readthedocs.io/
- Spatial Analysis in Single-Cell: https://www.nature.com/articles/s41592-021-01358-2

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-12-05 | Astraea Team | Initial version |
