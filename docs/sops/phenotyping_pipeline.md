# Phenotyping Pipeline SOP

## Purpose
Standard Operating Procedure for **reproducible, QC-driven, marker-based phenotyping** of segmented cells using QuPath. This SOP defines mandatory inputs, folder structure, intensity extraction steps, classification rules, QC checks, and Definition of Done to ensure consistency across all analysts and projects.

---

# 1. Required Inputs

Analysts must have the following before starting:

### **1.1 Folder Structure (MANDATORY)**

```
project_root/
  raw/
    image.ome.tiff
  segmentation/
    masks/
      mask_<date>.tiff
  phenotyping/
    logs/
    qc/
    exports/
    metadata.json
```

### **1.2 Required Files**
- OME-TIFF or TIFF multiplex image
- Segmentation masks from the segmentation pipeline  
- Marker panel definition JSON or CSV  
- Threshold definitions (if pre-defined for the project)  
- Tissue-specific QC expectations (if provided)

---

# 2. Software Requirements
- QuPath 0.4.0 or later  
- Recommended extensions (StarDist, Cellpose, etc.) if needed  
- Python (optional) for downstream analysis  

---

# 3. Procedure

## Step 1 — Project Setup

1. Open QuPath  
2. **File → Create Project**  
3. Select the project directory  
4. Add image(s):  
   - Drag-and-drop  
   - OR `File → Add Images`  

Verify correct channel names before proceeding.

---

## Step 2 — Import Segmentation Masks

### **Scripted import (preferred)**

```groovy
import qupath.lib.objects.PathObjects
import qupath.lib.images.servers.LabeledImageServer

def labelPath = '/path/to/segmentation_mask.tiff'
def labelServer = new LabeledImageServer.Builder(labelPath)
    .useLabelColors()
    .build()

def labels = labelServer.getLabels()

for (label in labels) {
    def roi = labelServer.getROI(label)
    def cell = PathObjects.createCellObject(roi, null, null)
    addObject(cell)
}

fireHierarchyUpdate()
println "Imported ${labels.size()} segmented cells."
```

### **Manual import (acceptable for testing)**
1. `Objects → Import Objects`  
2. Select segmentation mask  
3. Confirm mask layer alignment  

Analyst must record import method in the phenotyping log.

---

## Step 3 — Extract Marker Intensities (MANDATORY)

### **GUI Method**
1. `Analyze → Calculate features → Add Intensity features`  
2. Select all relevant channels  
3. Use: Mean, Median, Std
4. Click **Run**

### **Scripting Method (preferred for reproducibility)**

```groovy
import qupath.lib.analysis.features.ObjectMeasurements

def measurements = ObjectMeasurements.Measurements.values()
def compartments = ObjectMeasurements.Compartments.values()

for (cell in getDetectionObjects()) {
    ObjectMeasurements.addIntensityMeasurements(
        getCurrentServer(),
        cell,
        1.0, // downsample
        measurements,
        compartments
    )
}

fireHierarchyUpdate()
println "Intensity measurements added to ${getDetectionObjects().size()} cells."
```

### **Analyst must verify:**
- All expected measurement columns appear in the table  
- No missing values for major markers  
- Bright/dim channel distributions are reasonable  

If measurements look incorrect → STOP → update troubleshooting KB.

---

## Step 4 — Define Phenotypes

### **4.1 Standard Marker Naming Rules (CRITICAL)**

To avoid downstream chaos:

- Channel names must match panel definitions  
- No spaces: use `CD8_mean`, not `CD8 mean`  
- Nuclear markers must be prefixed with `Nuc_`  
- Membrane/cell markers with `Cell_`

Analysts must correct channel names in QuPath before classification. TODO Script for channel renaming to come...

---

## Step 5 — Apply Threshold-Based Classification

### **Manual Thresholding**
1. Utilize manual thresholding SOP - see  `sops/phenotyping_manual.md`
2. Validate threshold using positive-control ROIs  

### **Composite Classifiers (Recommended)**  
Example: CD8+ T cells

```groovy
def cd8Threshold = 50
def cd3Threshold = 40

for (cell in getCellObjects()) {
    def cd8 = measurement(cell, "Cell: CD8 mean")
    def cd3 = measurement(cell, "Cell: CD3 mean")

    if (cd8 > cd8Threshold && cd3 > cd3Threshold)
        cell.setPathClass(getPathClass("CD8+ T cell"))
    else
        cell.setPathClass(getPathClass("Other"))
}

fireHierarchyUpdate()
println "Phenotyping complete."
```

Analyst must document threshold values used in `phenotyping/metadata.json`.

---

## Step 6 — Export Results

### Scripted export (preferred)

```groovy
def exportPath = buildFilePath(PROJECT_BASE_DIR, 'phenotyping', 'exports', 'phenotype_results.csv')
saveDetectionMeasurements(exportPath)
println "Phenotype results exported to ${exportPath}"
```

### GUI export
1. `Measure → Export measurements`  
2. Save to `phenotyping/exports/`

### Required exports:
- Full measurement table  
- Phenotype summary counts  
- QC plots  

---

# 7. Quality Control (MANDATORY)

### **Analysts must generate a phenotype QC summary:**

```groovy
def counts = getCellObjects().groupBy { it.getPathClass()?.toString() ?: "Unclassified" }
counts.each { k, v -> println "${k}: ${v.size()} cells" }
```

### **QC Criteria**
- [ ] All cells have intensity measurements  
- [ ] Thresholds validated using positive-control regions  
- [ ] Major cell populations match expected biology  
- [ ] No unusual or biologically implausible populations  
- [ ] Phenotype distribution is consistent with segmentation masks  
- [ ] Less than 5% cells remain "Unclassified" unless justified  

If QC fails → analyst must create a troubleshooting entry.

---

# 8. Definition of Done (NON-NEGOTIABLE)

Phenotyping is **DONE** only when:

### **Outputs**
- [ ] Classified cells present in object hierarchy  
- [ ] CSV export saved to `phenotyping/exports/`  
- [ ] QC phenotype summary saved to `phenotyping/qc/`  
- [ ] Metadata JSON updated with thresholds, versions, date  

### **Reproducibility**
- [ ] Script or GUI steps used recorded in `phenotyping/logs/run_<date>.txt`  
- [ ] QuPath version and settings logged  

### **Communication**
- [ ] Analyst posts summary to ClickUp including:  
  - Thresholds used  
  - QC results  
  - File locations  
  - Link to troubleshooting entry (if applicable)

If ANY item above is missing → work is returned for completion.

---

# 9. Troubleshooting

If errors occur:

1. Reproduce the issue  
2. Document error message + screenshot  
3. Attempt two fixes  
4. Add/update entry in:  
   `../troubleshooting/qupath_common_errors.md`  
5. Only then escalate  

---

# 10. References
- QuPath Documentation: https://qupath.readthedocs.io/  
- Panel definitions and threshold library (internal)  
- Troubleshooting KB  

---

# 11. Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.1 | 2025-12-05 | McKee | Revised for QC, reproducibility, and operational rigor |
| 1.0 | 2025-12-05 | Astraea Team | Initial version |
