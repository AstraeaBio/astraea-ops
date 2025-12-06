# Squidpy Common Errors & Troubleshooting

Standardized troubleshooting guide for Squidpy-based spatial analysis (graph construction, neighborhood enrichment, spatial statistics).

---

## 1. Installation / Import Errors

### PROBLEM
```text
ModuleNotFoundError: No module named 'squidpy'
```

### DIAGNOSIS
- Squidpy not installed in the active Python environment.
- Jupyter kernel not bound to the `spatial` environment.

### FIX
1. Activate the spatial environment:
   ```bash
   conda activate spatial
   ```
2. Install Squidpy:
   ```bash
   pip install squidpy
   ```
3. Verify:
   ```python
   import squidpy as sq
   print(sq.__version__)
   ```

---

## 2. spatial_neighbors Errors

### PROBLEM
```text
KeyError: 'spatial'
```
or
```text
ValueError: coordinates not found
```

### DIAGNOSIS
- `adata.obsm['spatial']` is missing or named differently.
- Coordinates not stored in the expected location.

### FIX
1. Inspect `obsm`:
   ```python
   adata.obsm.keys()
   ```
2. If coordinates are in `obs`:
   ```python
   import numpy as np
   adata.obsm['spatial'] = adata.obs[['X','Y']].to_numpy()
   ```
3. Retry:
   ```python
   import squidpy as sq
   sq.gr.spatial_neighbors(adata, coord_type='generic', n_neighs=15)
   ```

---

## 3. nhood_enrichment Fails

### PROBLEM
```text
KeyError: 'phenotype'
```
or
```text
ValueError: cluster_key not found in .obs
```

### DIAGNOSIS
- `cluster_key` not present in `adata.obs`.
- Using the wrong column name for phenotypes or clusters.

### FIX
1. Check available keys:
   ```python
   adata.obs.head()
   ```
2. Ensure the phenotype column exists:
   ```python
   adata.obs['phenotype']  # should not error
   ```
3. Run:
   ```python
   sq.gr.nhood_enrichment(adata, cluster_key='phenotype')
   ```

---

## 4. nhood_enrichment Plot Looks Flat or Nonsense

### PROBLEM
- Enrichment heatmap shows no structure or biologically implausible patterns.

### DIAGNOSIS
- Wrong `cluster_key` (e.g. using numeric cluster IDs with no biological meaning).
- Very imbalanced classes (tiny populations).
- Neighborhood graph too sparse or too dense.

### FIX
1. Inspect class sizes:
   ```python
   adata.obs['phenotype'].value_counts()
   ```
2. Drop extremely rare phenotypes:
   ```python
   counts = adata.obs['phenotype'].value_counts()
   keep = counts[counts > 20].index
   adata = adata[adata.obs['phenotype'].isin(keep)].copy()
   ```
3. Adjust neighbors:
   ```python
   sq.gr.spatial_neighbors(adata, coord_type='generic', n_neighs=8)
   sq.gr.nhood_enrichment(adata, cluster_key='phenotype')
   ```

---

## 5. Plotting Errors (nhood_enrichment, spatial_scatter)

### PROBLEM
```text
ValueError: Axes limits are NaN or Inf
```
or
```text
TypeError: Invalid RGBA argument
```

### DIAGNOSIS
- NaNs or infinities in coordinates.
- Invalid or non-numeric values in the data being plotted.

### FIX
1. Check coordinate sanity:
   ```python
   adata.obsm['spatial'].min(axis=0), adata.obsm['spatial'].max(axis=0)
   ```
2. Drop NaN rows:
   ```python
   import numpy as np
   mask = np.isfinite(adata.obsm['spatial']).all(axis=1)
   adata = adata[mask].copy()
   ```
3. Retry plotting.

---

## 6. Memory / Performance Issues

### PROBLEM
- Kernel dies when building graphs or computing neighborhood stats.
- Very slow execution on large datasets.

### DIAGNOSIS
- Dataset too large for full-resolution spatial graph.
- Too many neighbors (`n_neighs` too high).
- Running analyses on whole tissue when ROI-level would suffice.

### FIX
1. Subsample cells:
   ```python
   adata_sub = adata[::5, :].copy()
   sq.gr.spatial_neighbors(adata_sub, coord_type='generic', n_neighs=10)
   ```
2. Restrict to ROI or phenotype of interest.
3. Lower `n_neighs` and focus analyses.

---

## 7. Inconsistent Results Between Runs

### PROBLEM
- Re-running the same notebook yields slightly different results (clusters, enrichment).

### DIAGNOSIS
- Random initialization, no fixed seed.
- Non-deterministic algorithms.

### FIX
1. Set random seeds globally at top of notebook:
   ```python
   import numpy as np
   import random
   import scanpy as sc

   seed = 1234
   np.random.seed(seed)
   random.seed(seed)
   sc.settings.seed = seed
   ```
2. Document the seed used in `spatial/metadata.json`.

---

## Logging & Documentation Requirements

For any Squidpy-related error:

- Record:
  - Exact error text
  - Dataset size (#cells)
  - `n_neighs` and any relevant parameters
  - Squidpy and Scanpy versions
- Add or update a section in this file with:
  - PROBLEM
  - DIAGNOSIS
  - FIX
- Link this page from the relevant ClickUp task.