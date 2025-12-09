# Stage 5 — Spatial Analysis

This document describes how this stage is **currently** performed across projects.

## Objectives

- Compute spatial statistics and neighborhood relationships.
- Quantify interactions between cell types or regions.
- Measure distances between cell populations.
- Identify spatial microenvironments and cellular communities.
- Compare spatial organization across conditions (e.g., pre/post treatment, disease vs control).

## Common Inputs

### Input File Types and Formats

1. **Phenotyped cell tables (CSV/TSV):**
   - Required columns:
     - Cell ID
     - X and Y coordinates in microns (`Centroid X µm`, `Centroid Y µm`)
     - Phenotype labels (`Level_4`, `phenotype`, etc.)
     - Sample/slide identifiers
     - Optional: Region annotations, marker intensities
   - Example from Nguyen Lab: `df_ss2_cleaned_phenotyped_levels_data.csv` with 36 phenotypes

2. **AnnData H5AD files:**
   - `.X`: Marker expression matrix (optional for pure spatial analysis)
   - `.obs`: Cell metadata including phenotypes, coordinates, condition labels
   - `.obsm['spatial']`: XY coordinate array (N cells × 2)
   - `.uns`: Storage for spatial analysis results
   - Example: `adata_countingregions_phenotyped_combined.h5ad`

3. **Region/ROI definitions:**
   - CSV or JSON defining anatomical regions
   - Boundary coordinates or annotation masks
   - Example regions: Germinal Center, T-B Transition Zone, Subcapsular Sinus, Cortex, Follicle

4. **Metadata files:**
   - Sample-level metadata (condition, batch, patient ID)
   - Analysis parameters (radius thresholds, distance cutoffs)
   - Example: `metadata.json` with spatial parameters documented

## Current Scripts / Tools

### Primary Tools

1. **SCIMAP (Primary spatial analysis framework)** - See [spatial_analysis.md](../sops/spatial_analysis.md)
   - Spatial interaction analysis (permutation-based)
   - Neighborhood enrichment
   - Distance calculations
   - Spatial clustering
   - Well-documented and maintained

2. **Squidpy (Alternative/complementary):**
   - Neighborhood enrichment analysis
   - Co-occurrence analysis
   - Spatial autocorrelation
   - Integration with scanpy ecosystem

3. **Custom spatial functions:**
   - Delaunay triangulation for spatial networks
   - Distance-based edge filtering
   - Neighborhood composition analysis
   - Voronoi tessellation visualization

4. **Scipy spatial utilities:**
   - `scipy.spatial.distance.cdist` for pairwise distances
   - `scipy.spatial.Delaunay` for triangulation
   - `scipy.stats.mannwhitneyu` for statistical testing

### Script Catalog Links

- [compute_neighbors.md](../scripts_catalog/spatial_analysis/compute_neighbors.md) - Neighborhood graph construction
- [enrichment_analysis.md](../scripts_catalog/spatial_analysis/enrichment_analysis.md) - Spatial enrichment testing
- [vessel_distance.md](../scripts_catalog/spatial_analysis/vessel_distance.md) - Distance to anatomical features

## Manual Steps

### Typical Analyst Workflow

#### 1. Load and Prepare Data

```python
import pandas as pd
import numpy as np
import scimap as sm
import anndata as ad

# Load phenotyped cells
cells = pd.read_csv('phenotyping/exports/phenotyped_cells.csv')

# Create AnnData object
adata = sm.pp.create_adata(
    cells,
    x='Centroid X µm',
    y='Centroid Y µm',
    phenotype='Level_4'
)

print(f"Loaded {adata.n_obs} cells with {len(adata.obs['phenotype'].unique())} phenotypes")
```

#### 2. Define Regions of Interest (ROIs)

**Example from Nguyen Lab - defining T-B transition zone:**

```python
# T-B Transition Zone: Cortex cells within 60µm of Germinal Center/Follicle
gc_cells = cells[cells['Region_Name'].isin(['Germinal Center', 'Follicle'])]
cortex_cells = cells[cells['Region_Name'] == 'Cortex']

from scipy.spatial.distance import cdist

gc_coords = gc_cells[['Centroid X µm', 'Centroid Y µm']].values
cortex_coords = cortex_cells[['Centroid X µm', 'Centroid Y µm']].values

distances = cdist(cortex_coords, gc_coords)
min_distances = distances.min(axis=1)

# Cells within 60µm define T-B transition zone
transition_mask = min_distances <= 60
cells.loc[cortex_cells.index[transition_mask], 'Region_Name'] = 'T-B Transition Zone'
```

#### 3. Spatial Interaction Analysis

**Using SCIMAP (preferred):**

```python
# Run spatial interaction for each region separately
regions = ['Germinal Center', 'Follicle', 'Cortex', 'T-B Transition Zone', 'Subcapsular Sinus']

for region in regions:
    # Subset to region
    adata_subset = adata[adata.obs['Region_Name'] == region].copy()

    # Calculate spatial interactions (radius-based)
    sm.tl.spatial_interaction(
        adata_subset,
        method='radius',
        radius=50,  # microns
        phenotype='phenotype',
        pval_method='zscore',
        permutations=1000
    )

    # Visualize as heatmap
    sm.pl.spatial_interaction(
        adata_subset,
        summarize_plot=True,
        row_cluster=True,
        col_cluster=True
    )

    # Visualize as network (only significant interactions, p<0.05)
    sm.pl.spatialInteractionNetwork(
        adata_subset,
        p_val=0.05
    )

    # Save results
    interaction_matrix = adata_subset.uns['spatial_interaction']
    interaction_matrix.to_csv(f'spatial/exports/spatial_interaction_{region}.csv')
```

**Key parameters:**
- **Radius:** 30-100µm typical (tissue-dependent)
- **Permutations:** 1000 (minimum for robust p-values)
- **Method:** 'radius' (distance-based) or 'knn' (k-nearest neighbors)

#### 4. Neighborhood Composition Analysis

**60µm radius neighborhoods around specific cell types:**

```python
def neighborhood_analysis(adata, center_phenotype, radius=60):
    """
    Analyze cell composition within radius of center_phenotype cells
    """
    from scipy.spatial.distance import cdist

    # Get coordinates
    all_coords = adata.obsm['spatial']
    phenotypes = adata.obs['phenotype'].values

    # Center cells
    center_mask = phenotypes == center_phenotype
    center_coords = all_coords[center_mask]

    neighborhoods = []

    for center_coord in center_coords:
        # Calculate distances to all cells
        distances = np.linalg.norm(all_coords - center_coord, axis=1)

        # Get cells within radius
        neighbor_mask = distances <= radius
        neighbor_phenotypes = phenotypes[neighbor_mask]

        # Count phenotypes
        unique, counts = np.unique(neighbor_phenotypes, return_counts=True)
        neighborhood = dict(zip(unique, counts / counts.sum() * 100))  # as percentages
        neighborhoods.append(neighborhood)

    # Convert to DataFrame
    neighborhood_df = pd.DataFrame(neighborhoods).fillna(0)

    return neighborhood_df

# Example: Dendritic cell neighborhoods
dc_neighborhoods = neighborhood_analysis(adata, 'Dendritic', radius=60)

# Statistics by condition
pre_dc = dc_neighborhoods[adata.obs[adata.obs['phenotype'] == 'Dendritic']['Pre_Post'] == 'Pre']
post_dc = dc_neighborhoods[adata.obs[adata.obs['phenotype'] == 'Dendritic']['Pre_Post'] == 'Post']

from scipy.stats import mannwhitneyu

results = []
for phenotype in dc_neighborhoods.columns:
    stat, pval = mannwhitneyu(pre_dc[phenotype], post_dc[phenotype])
    fold_change = post_dc[phenotype].mean() / pre_dc[phenotype].mean()
    results.append({
        'Phenotype': phenotype,
        'Mean_Pre': pre_dc[phenotype].mean(),
        'Mean_Post': post_dc[phenotype].mean(),
        'Fold_Change': fold_change,
        'P_Value': pval
    })

results_df = pd.DataFrame(results)
results_df.to_csv('spatial/exports/Dendritic_neighborhood_analysis.csv', index=False)
```

**Example results from Nguyen Lab (Follicle region, Dendritic neighborhoods):**
- Macrophage: +143% post-reperfusion (p < 0.0001)
- Cyt T: +116% (p < 0.0001)
- Helper T: +62% (p < 0.0001)
- NK Cell: -23% (p < 0.0001)

#### 5. Distance Analysis Between Cell Types

```python
def pairwise_distances(adata, phenotype_pairs):
    """Calculate pairwise distances between cell type pairs"""
    coords = adata.obsm['spatial']
    phenotypes = adata.obs['phenotype'].values

    results = {}

    for pheno1, pheno2 in phenotype_pairs:
        coords1 = coords[phenotypes == pheno1]
        coords2 = coords[phenotypes == pheno2]

        if len(coords1) > 0 and len(coords2) > 0:
            distances = cdist(coords1, coords2)
            min_distances = distances.min(axis=1)  # nearest neighbor distance
            results[(pheno1, pheno2)] = min_distances

    return results

# Example: DC to T cell distances
pairs = [
    ('Dendritic', 'Cyt T'),
    ('Dendritic', 'Helper T'),
    ('Macrophage', 'B Cell'),
    ('NK Cell', 'Dendritic')
]

distances = pairwise_distances(adata, pairs)

# Plot distributions
import matplotlib.pyplot as plt

fig, axes = plt.subplots(2, 2, figsize=(12, 10))
axes = axes.ravel()

for i, (pair, dists) in enumerate(distances.items()):
    axes[i].hist(dists, bins=50, alpha=0.7)
    axes[i].set_xlabel('Distance (µm)')
    axes[i].set_ylabel('Count')
    axes[i].set_title(f'{pair[0]} → {pair[1]}')
    axes[i].axvline(dists.median(), color='red', linestyle='--',
                   label=f'Median: {dists.median():.1f}µm')
    axes[i].legend()

plt.tight_layout()
plt.savefig('spatial/figures/pairwise_distances.png', dpi=150)
```

#### 6. Spatial Network Construction (Delaunay Triangulation)

**From Nguyen Lab custom functions:**

```python
from scipy.spatial import Delaunay

def build_spatial_network(coords, phenotypes, distance_cutoff, phenotypes_of_interest):
    """
    Build spatial network using Delaunay triangulation with distance filtering
    """
    # Delaunay triangulation
    tri = Delaunay(coords)

    # Extract edges from triangulation
    edges = set()
    for simplex in tri.simplices:
        for i in range(3):
            edge = tuple(sorted([simplex[i], simplex[(i + 1) % 3]]))
            edges.add(edge)

    # Filter by distance and phenotype
    filtered_edges = []
    for edge in edges:
        # Check if both cells are phenotypes of interest
        if phenotypes[edge[0]] in phenotypes_of_interest and \
           phenotypes[edge[1]] in phenotypes_of_interest:
            # Check distance
            dist = np.linalg.norm(coords[edge[0]] - coords[edge[1]])
            if dist <= distance_cutoff:
                filtered_edges.append(edge)

    return filtered_edges

# Example usage
phenotypes_oi = ['Cyt T', 'Helper T', 'Dendritic', 'Macrophage', 'B Cell']
edges = build_spatial_network(
    adata.obsm['spatial'],
    adata.obs['phenotype'].values,
    distance_cutoff=50,  # µm
    phenotypes_of_interest=phenotypes_oi
)

print(f"Network: {len(edges)} edges connecting {len(phenotypes_oi)} phenotypes")
```

#### 7. Generate Spatial Visualizations

```python
import matplotlib.pyplot as plt
import seaborn as sns

fig, axes = plt.subplots(1, 3, figsize=(18, 6))

# 1. Phenotype spatial map
for pheno in adata.obs['phenotype'].unique():
    mask = adata.obs['phenotype'] == pheno
    coords = adata.obsm['spatial'][mask]
    axes[0].scatter(coords[:, 0], coords[:, 1], label=pheno, s=3, alpha=0.6)
axes[0].set_title('Spatial Distribution by Phenotype')
axes[0].set_xlabel('X (µm)')
axes[0].set_ylabel('Y (µm)')
axes[0].legend(bbox_to_anchor=(1.05, 1), fontsize=7)

# 2. Interaction heatmap
interaction_matrix = adata.uns['spatial_interaction']
sns.heatmap(interaction_matrix, cmap='RdBu_r', center=0, ax=axes[1],
            cbar_kws={'label': 'Z-score'})
axes[1].set_title('Spatial Interaction Enrichment')

# 3. Distance distribution
example_distances = distances[('Dendritic', 'Cyt T')]
axes[2].hist(example_distances, bins=50, alpha=0.7, edgecolor='black')
axes[2].axvline(example_distances.median(), color='red', linestyle='--',
               label=f'Median: {example_distances.median():.1f}µm')
axes[2].set_xlabel('Distance (µm)')
axes[2].set_ylabel('Count')
axes[2].set_title('Dendritic → Cyt T Distance')
axes[2].legend()

plt.tight_layout()
plt.savefig('spatial/figures/spatial_analysis_summary.png', dpi=150)
```

## Variations Between Projects

### By Tissue Type

**Lymph nodes (Nguyen Lab):**
- **Analysis focus:** 4-zone analysis (B cell zone, T cell zone, T-B transition, Subcapsular sinus)
- **Key interactions:** DC-T cell, DC-B cell, Macrophage-B cell
- **Neighborhood radius:** 60µm (based on Nolan sliding window technique)
- **Key findings:** Spatial reorganization post-transplant with T cell enrichment around DCs

**Tumor microenvironment:**
- **Analysis focus:** Tumor core vs invasive margin vs stroma
- **Key interactions:** Tumor-immune, immune-immune, immune-stroma
- **Neighborhood radius:** 50-100µm
- **Common metrics:** Tumor-immune distance, TLS (Tertiary Lymphoid Structure) identification

**Bone marrow:**
- **Analysis focus:** Vascular niche proximity, endosteal niche
- **Key interactions:** HSC-stromal, HSC-vascular
- **Distance metrics:** Distance to blood vessels, distance to bone surface
- **Neighborhood radius:** 20-50µm (smaller due to dense packing)

### By Analysis Goal

**Pre/Post treatment comparison (Nguyen Lab approach):**
1. Separate spatial analysis for each condition
2. Statistical comparison of:
   - Neighborhood compositions (Mann-Whitney U test)
   - Distance distributions (KS test or t-test)
   - Interaction matrices (differential enrichment)
3. Volcano plots (fold change vs p-value)
4. Effect size calculations (Cohen's d)

**Biomarker discovery:**
1. Spatial clustering to identify microenvironments
2. Association of microenvironments with outcome
3. Survival analysis stratified by spatial features
4. Spatial signature development

**Spatial heterogeneity assessment:**
1. Multiple ROIs per sample
2. Within-sample vs between-sample variation
3. Spatial entropy calculations
4. Regional diversity indices

### By Platform

**SCIMAP-based (most common):**
- Radius-based spatial graphs
- Permutation testing for interactions
- Integrated with AnnData ecosystem
- Good for hypothesis testing

**Squidpy-based:**
- k-NN spatial graphs
- Co-occurrence and spatial autocorrelation
- Integration with scanpy workflows
- Good for exploratory analysis

**Custom pipelines (when needed):**
- Delaunay triangulation for specific network analyses
- Distance-based metrics for targeted questions
- Combined with SCIMAP/Squidpy for validation

## Known Issues

### 1. Coordinate System Inconsistencies

**Problem:** X/Y coordinates may be in different units (pixels vs microns) or have flipped axes.

**Detection:**
```python
# Check coordinate ranges
print(f"X range: {cells['Centroid X µm'].min():.2f} to {cells['Centroid X µm'].max():.2f}")
print(f"Y range: {cells['Centroid Y µm'].min():.2f} to {cells['Centroid Y µm'].max():.2f}")

# Visualize to check orientation
plt.scatter(cells['Centroid X µm'], cells['Centroid Y µm'], s=1, alpha=0.3)
plt.title('Check for correct orientation')
plt.show()
```

**Current handling:**
- Verify units match physical tissue dimensions
- Document any axis flips in metadata
- Standardize to microns for all spatial analyses

### 2. Edge Effects in Spatial Analysis

**Problem:** Cells near tissue boundaries have incomplete neighborhoods.

**Current mitigation:**
- Exclude edge cells (e.g., cells within radius distance of boundary)
- Use ROI masks to define analysis regions
- Report percentage of excluded cells in QC

**Example:**
```python
# Define ROI mask (exclude 50µm from edges)
x_min, x_max = cells['Centroid X µm'].min() + 50, cells['Centroid X µm'].max() - 50
y_min, y_max = cells['Centroid Y µm'].min() + 50, cells['Centroid Y µm'].max() - 50

roi_mask = (
    (cells['Centroid X µm'] > x_min) &
    (cells['Centroid X µm'] < x_max) &
    (cells['Centroid Y µm'] > y_min) &
    (cells['Centroid Y µm'] < y_max)
)

print(f"Excluded {(~roi_mask).sum()} edge cells ({(~roi_mask).sum()/len(cells)*100:.1f}%)")
```

### 3. Rare Cell Type Analysis

**Problem:** Insufficient cells of rare phenotypes for meaningful spatial statistics.

**Current approach:**
- Set minimum cell count threshold (e.g., >20 cells per condition)
- Report cell counts in all outputs
- Combine related phenotypes if biologically justified
- Use exact permutation tests instead of asymptotic approximations

**Example from Nguyen Lab:**
- NK cells: low counts in some regions
- Reported but flagged as underpowered for statistical testing
- Combined "Prolif NK" with "NK Cell" for spatial analysis

### 4. Radius Selection for Neighborhood Analysis

**Problem:** No universal "correct" radius; results sensitive to choice.

**Current practice:**
- Use literature-based values when available (Nolan: 60µm for lymph nodes)
- Test multiple radii (30, 50, 75, 100µm) and report sensitivity
- Document biological rationale for chosen radius
- Visualize radius on tissue images for validation

**From Nguyen Lab:**
- 60µm radius chosen based on:
  - Nolan Lab sliding window technique
  - Approximate T cell zone size in lymph nodes
  - DC antigen presentation range (~50-100µm)

### 5. Multiple Testing Correction

**Problem:** Testing many cell type pairs inflates false positives.

**Current handling:**
- Apply Benjamini-Hochberg FDR correction
- Report both raw and corrected p-values
- Use adjusted p < 0.05 for significance claims

```python
from statsmodels.stats.multitest import multipletests

# After calculating p-values for all phenotype pairs
reject, pvals_corrected, _, _ = multipletests(pvals, method='fdr_bh', alpha=0.05)

results_df['P_Value_Adjusted'] = pvals_corrected
results_df['Significant'] = reject
```

### 6. Computational Performance with Large Datasets

**Problem:** 100,000+ cells causes slow spatial analysis.

**Current optimization:**
- Spatial indexing (KD-trees) for distance queries
- Parallel processing for independent regions
- Subsample for initial exploration, then run full analysis
- Use Dask for out-of-core computation if needed

**Example:**
```python
from sklearn.neighbors import KDTree

# Build spatial index (much faster for repeated queries)
tree = KDTree(coords)
neighbors = tree.query_radius(center_coords, r=60)  # radius query in O(log n)
```

### 7. SCIMAP vs Squidpy Differences

**Problem:** Different tools give slightly different results due to implementation differences.

**Current practice:**
- Choose one primary tool per project (usually SCIMAP)
- Use second tool for validation if discrepancies arise
- Document which tool was used in all outputs
- Report version numbers

**Key differences:**
- SCIMAP: radius-based, z-score permutation testing
- Squidpy: k-NN based, different enrichment calculation
- Both valid; choose based on biological question and precedent

## Success Metrics

From recent Nguyen Lab project:

**Scale:**
- **~100,000 cells** analyzed across 4 lymph nodes
- **5 anatomical regions** analyzed separately
- **36 phenotypes** included in spatial analysis

**Key findings:**
- **Dendritic cell neighborhoods** showed significant enrichment for T cells and macrophages post-reperfusion
- **Spatial interactions:** 15 significant cell pair interactions identified (p < 0.001)
- **Distance metrics:** DC-T cell distances decreased post-reperfusion (median: 85µm → 68µm, p < 0.01)

**Computational performance:**
- **Processing time:** ~2 hours for full spatial analysis suite (all regions, all metrics)
- **Memory:** <16GB RAM (using AnnData efficient storage)
- **Reproducibility:** 100% reproducible with fixed random seeds in permutation tests

**Outputs generated:**
- 10 spatial interaction matrices (CSV)
- 25+ spatial visualization figures (PNG, PDF)
- 5 neighborhood analysis summary tables
- 3 distance distribution datasets

## Next Steps / Improvements Needed

1. **Automate ROI definition** using image analysis (currently manual)
2. **Standardize radius selection** with tissue-specific defaults
3. **Implement spatial transcriptomics integration** (when marker panel + RNA data available)
4. **Build spatial signature library** from completed projects
5. **Create interactive spatial viewers** for exploration
6. **Develop spatial QC metrics** (automated detection of artifacts, edge effects)
7. **Add spatial statistical power calculations** (minimum cell counts, effect sizes)
8. **Build spatial analysis dashboard** for real-time results visualization
