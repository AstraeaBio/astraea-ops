# SCIMAP Common Errors & Troubleshooting

Standardized troubleshooting guide for SCIMAP-based spatial analysis.  
For each issue, document **what happened**, **why**, and **how it was fixed**.

---

## 1. SCIMAP Import / Installation Errors

### PROBLEM
```text
ModuleNotFoundError: No module named 'scimap'
```

### DIAGNOSIS
- SCIMAP not installed in the active environment.
- Analyst using the wrong conda environment.
- Jupyter kernel not pointing to the `spatial` env.

### FIX
1. Confirm active environment:
   ```bash
   conda env list
   conda activate spatial
   ```
2. Install SCIMAP:
   ```bash
   pip install scimap
   ```
3. In Jupyter, ensure kernel uses `spatial` environment.

4. Verify:
   ```python
   import scimap as sm
   print(sm.__version__)
   ```

---

## 2. create_adata Fails or Produces Wrong Shape

### PROBLEM
```text
KeyError: 'X' (or 'Y' or 'phenotype')
```
or
```text
ValueError: cannot convert float NaN to integer
```

### DIAGNOSIS
- Required columns (`X`, `Y`, `phenotype`) missing or misnamed.
- NaNs present in coordinate or phenotype columns.
- Using legacy names (`X_centroid`, `Y_centroid`) without mapping.

### FIX
1. Inspect columns:
   ```python
   print(df.columns.tolist())
   df[['X','Y','phenotype']].head()
   ```
2. Map legacy columns:
   ```python
   df['X'] = df['X_centroid']
   df['Y'] = df['Y_centroid']
   ```
3. Drop NaNs in critical columns:
   ```python
   df = df.dropna(subset=['X','Y','phenotype'])
   ```
4. Retry:
   ```python
   adata = sm.pp.create_adata(df, x='X', y='Y', phenotype='phenotype')
   ```

---

## 3. spatial_neighbors Fails or Is Extremely Slow

### PROBLEM
- Code hangs or takes excessively long:
  ```python
  adata = sm.tl.spatial_neighbors(adata, radius=30)
  ```
- Memory spikes or kernel dies.

### DIAGNOSIS
- Radius too large for the tissue scale.
- Dataset too big (hundreds of thousands of cells) without subsampling.
- Units confusion (pixels vs microns) – radius not in same units as `X`,`Y`.

### FIX
1. Confirm units:
   - If coordinates are in pixels, either convert to microns or set radius in pixels consistently.
2. Try a smaller radius:
   ```python
   adata = sm.tl.spatial_neighbors(adata, radius=15)
   ```
3. Subsample for testing:
   ```python
   adata_sub = adata[::10, :].copy()
   sm.tl.spatial_neighbors(adata_sub, radius=30)
   ```
4. If still problematic → document cell counts, radius, run time, and escalate.

---

## 4. neighborhood_enrichment Output Looks Wrong

### PROBLEM
- Neighborhood enrichment matrix shows unexpected strong enrichment between obviously unrelated phenotypes.
- All phenotypes show similar enrichment patterns.

### DIAGNOSIS
- Phenotypes not properly assigned (e.g., default labels like `Cluster_1`, `Cluster_2`).
- Too few cells of some phenotypes – noisy statistics.
- Using wrong key for phenotype column.

### FIX
1. Validate phenotype column:
   ```python
   adata.obs['phenotype'].value_counts()
   ```
2. Use a curated phenotype column (e.g. `phenotype_clean`):
   ```python
   adata.obs['phenotype'] = adata.obs['phenotype_clean']
   ```
3. Remove ultra-rare phenotypes:
   ```python
   counts = adata.obs['phenotype'].value_counts()
   keep = counts[counts > 20].index
   adata = adata[adata.obs['phenotype'].isin(keep)].copy()
   ```
4. Rerun:
   ```python
   enrichment = sm.tl.neighborhood_enrichment(adata)
   ```

---

## 5. cluster (Leiden) Fails or Produces Only One Cluster

### PROBLEM
```text
ValueError: cannot find neighbors
```
or clustering yields only a single Leiden cluster.

### DIAGNOSIS
- spatial_neighbors not computed or failed.
- Graph too sparse (radius too small).
- Resolution parameter too low.

### FIX
1. Confirm neighbors exist:
   ```python
   'spatial_connectivities' in adata.obsp
   ```
2. Increase graph connectivity:
   - Increase radius (e.g. from 20 → 30 or 40).
3. Increase resolution:
   ```python
   adata = sm.tl.cluster(adata, method='leiden', resolution=0.8)
   ```
4. Plot to inspect:
   ```python
   sm.pl.spatial_scatter(adata, color='leiden')
   ```

---

## 6. Plotting Functions Fail (sm.pl.*)

### PROBLEM
```text
AttributeError: 'AnnData' object has no attribute 'obsm'
KeyError: 'spatial'
```

### DIAGNOSIS
- `obsm['spatial']` missing or incorrectly named.
- SCIMAP expects a `spatial` coordinate matrix.

### FIX
1. Check available obsm keys:
   ```python
   adata.obsm.keys()
   ```
2. Set / rename spatial coordinates:
   ```python
   import numpy as np
   adata.obsm['spatial'] = np.vstack([adata.obs['X'], adata.obs['Y']]).T
   ```
3. Retry plotting:
   ```python
   sm.pl.spatial_scatter(adata, color='phenotype')
   ```

---

## 7. AnnData Save/Load Problems

### PROBLEM
```text
OSError: Unable to create file (unable to open file: name = 'adata_spatial.h5ad', errno = 13)
```

### DIAGNOSIS
- Path does not exist (`spatial/exports/`).
- File permissions or locked file.
- Running in read-only environment.

### FIX
1. Ensure directory exists:
   ```python
   import os
   os.makedirs('spatial/exports', exist_ok=True)
   ```
2. Save with full path:
   ```python
   adata.write('spatial/exports/adata_spatial.h5ad')
   ```

---

## 8. Performance / Memory Issues

### PROBLEM
- Kernel dies when computing distance matrices or enrichment on very large datasets.

### DIAGNOSIS
- Data too large to process in-core with full pairwise distances.
- Running unnecessary heavy operations for exploratory analysis.

### FIX
1. Subsample:
   ```python
   adata_sub = adata[::5, :].copy()  # 20% of cells
   ```
2. Restrict to region or phenotype of interest.
3. Compute metrics on selected subsets and document this choice in the log.

---

## Logging & Documentation Requirements

For any SCIMAP-related error:

- Record:
  - Exact error message
  - Dataset size (#cells)
  - Radius or k-NN parameters
  - SCIMAP version
- Add an entry here **or update an existing one** with:
  - PROBLEM
  - DIAGNOSIS
  - FIX
- Link this page from the relevant ClickUp task.
