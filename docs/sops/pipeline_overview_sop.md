# TOP-LEVEL PIPELINE SOP
### Segmentation → Phenotyping → Spatial Analysis  
### Astraea Bio — End-to-End Processing Workflow

## 0. Purpose
This document defines the complete, standardized, reproducible workflow for all Astraea Bio image-derived cell analysis. It describes required inputs/outputs, folder structure, QC checkpoints, handoff rules, and Definition of Done for each stage.

## 1. Global Folder Structure (MANDATORY)
```
project_root/
  raw/
    image.ome.tiff
    metadata.json
  segmentation/
    masks/
    logs/
    qc/
  phenotyping/
    exports/
    logs/
    qc/
    metadata.json
  spatial/
    exports/
    logs/
    qc/
    figures/
    metadata.json
  reports/
    summary/
    figures/
```

## 2. Upstream Requirements for All Stages
### 2.1 Required Files
- metadata.json  
- logs/run_<date>.txt  
- QC images  

### 2.2 Documentation
Record:  
- Analyst name  
- Software versions  
- Parameter values  
- Deviations from SOP  
- Troubleshooting links  

### 2.3 Communication
Each stage must update ClickUp with:  
- Summary  
- File paths  
- QC results  
- Troubleshooting links  

---

# 3. Stage 1 — Segmentation

## Goal
Generate high-quality nuclear + whole-cell masks.

## Inputs
- OME-TIFF  
- Nuclear & cytoplasm channels  
- MPP (microns per pixel)  
- raw/metadata.json  

## Process
Analyst follows **segmentation_pipeline.md**.

## Required Outputs
```
segmentation/masks/mask_<date>.tiff
segmentation/qc/*.png
segmentation/logs/run_<date>.txt
segmentation/metadata.json
```

## QC Criteria
- Minimal over-/under-segmentation  
- DAPI containment validated  
- Correct alignment with membrane channels  

## Definition of Done
- [ ] Mask saved  
- [ ] QC plots saved  
- [ ] Log file created  
- [ ] Metadata updated  
- [ ] ClickUp task updated  
- [ ] Troubleshooting entry added (if any error occurred)

## Handoff to Phenotyping
Provide mask path, QC, log, metadata.

---

# 4. Stage 2 — Phenotyping

## Goal
Assign biologically meaningful cell types.

## Inputs
- Segmentation masks  
- Channel names + panel definition  
- Thresholds or ML classifier  

## Process
Analyst follows **phenotyping_pipeline.md**.

## Required Outputs
```
phenotyping/exports/phenotype_results.csv
phenotyping/qc/*.png
phenotyping/logs/run_<date>.txt
phenotyping/metadata.json
```

## QC Criteria
- <5% unclassified cells (unless justified)  
- Thresholds validated against controls  
- Marker naming consistent  

## Definition of Done
- [ ] phenotype_results.csv exported  
- [ ] QC images saved  
- [ ] Log saved  
- [ ] Thresholds in metadata  
- [ ] GitHub Project task updated  
- [ ] Troubleshooting entry added  

## Handoff to Spatial Analysis
Provide phenotype_results.csv, QC, logs, metadata.

---

# 5. Stage 3 — Spatial Analysis

## Goal
Quantify tissue architecture, spatial organization, and cell interactions.

## Inputs
- phenotype_results.csv  
- Coordinates + phenotypes  
- Marker intensities (optional)  

## Process
Analyst follows **spatial_analysis_sop.md**.

## Required Outputs
```
spatial/exports/adata_spatial.h5ad
spatial/exports/neighborhood_enrichment.csv
spatial/exports/spatial_analysis_results.csv
spatial/figures/*.png
spatial/logs/run_<date>.txt
spatial/metadata.json
```

## QC Criteria
- Graph construction validated  
- Neighborhood enrichment plausible  
- Clusters coherent  
- Distances biologically plausible  

## Definition of Done
- [ ] AnnData saved  
- [ ] CSV exports written  
- [ ] ≥3 figures saved  
- [ ] QC + parameters logged  
- [ ] ClickUp updated  
- [ ] Troubleshooting entry added  

## Handoff to Reporting
Provide exports, figures, and spatial summary.

---

# 6. Cross-Stage Handoff Rules
1. **Nothing moves downstream unless ALL Definition of Done criteria are met.**  
2. **Downstream analysts return incomplete or incorrect work upstream.**  
3. **Each stage must produce reproducible metadata + logs.**  
4. **Analysts do NOT fix upstream errors; they escalate back.**

---

# 7. Troubleshooting Requirements
If ANY error occurs:
1. Capture full error text  
2. Attempt at least two fixes  
3. Document in the KB:  
   - deepcell_mesmer_errors.md  
   - qupath_common_errors.md  
   - scimap_common_errors.md  
   - squidpy_common_errors.md  
4. Link troubleshooting entry in ClickUp  
5. Only then escalate  

---

# 8. Full Pipeline Diagram
```
RAW IMAGE
   ↓
SEGMENTATION
   → mask, QC, logs
   ↓
PHENOTYPING
   → phenotype CSV, QC, logs
   ↓
SPATIAL ANALYSIS
   → AnnData, enrichment, clusters, distances
   ↓
REPORTING
```

---

# 9. Version History
| Version | Date | Author | Changes |
|---------|--------|--------|---------|
| 1.0 | 2025-12-05 | McKee | Initial full pipeline SOP |
