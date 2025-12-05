# Phenotyping Pipeline SOP

## Purpose

Standard Operating Procedure for cell phenotyping analysis using QuPath and marker-based classification.

## Prerequisites

- QuPath 0.4.0 or later installed
- Segmentation masks from the segmentation pipeline
- Multi-channel immunofluorescence images
- Marker panel definition

## Equipment/Software

- QuPath application
- Required QuPath extensions (if applicable)
- Python for post-processing (optional)

## Procedure

### Step 1: Project Setup

Create a new QuPath project:

1. Open QuPath
2. File > Create project
3. Select a project directory
4. Add images to project via drag-and-drop or File > Add images

### Step 2: Import Segmentation Masks

Import pre-computed segmentation masks:

```groovy
// QuPath script to import segmentation mask
import qupath.lib.objects.PathObjects
import qupath.lib.roi.RoiTools
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
```

Or manually load masks:
1. Objects > Import objects
2. Select the segmentation mask file
3. Configure import settings

### Step 3: Measure Intensities

Calculate marker intensities per cell:

1. Analyze > Calculate features > Add intensity features
2. Select all marker channels
3. Choose measurement types (Mean, Median, etc.)
4. Click "Run"

Alternatively, use script:

```groovy
// Measure all intensity features
import qupath.lib.analysis.features.ObjectMeasurements

def measurements = ObjectMeasurements.Measurements.values()
def compartments = ObjectMeasurements.Compartments.values()

for (detection in getDetectionObjects()) {
    ObjectMeasurements.addIntensityMeasurements(
        getCurrentServer(),
        detection,
        1.0,  // downsample
        measurements,
        compartments
    )
}
```

### Step 4: Define Phenotypes

Create classifiers based on marker expression:

Manual thresholding:
1. Classify > Set cell intensity classifications
2. Select marker channel
3. Set positive/negative threshold
4. Apply to all cells

Or create composite classifier:

```groovy
// Example: Define CD8+ T cells
def cd8Threshold = 50.0
def cd3Threshold = 40.0

for (cell in getCellObjects()) {
    def cd8 = measurement(cell, "Cell: CD8 mean")
    def cd3 = measurement(cell, "Cell: CD3 mean")
    
    if (cd8 > cd8Threshold && cd3 > cd3Threshold) {
        cell.setPathClass(getPathClass("CD8+ T cell"))
    }
}
fireHierarchyUpdate()
```

### Step 5: Export Results

Export phenotyping results:

```groovy
// Export measurements to CSV
def path = buildFilePath(PROJECT_BASE_DIR, 'exports', 'phenotype_results.csv')
saveDetectionMeasurements(path)
print("Results exported to: " + path)
```

Or export via GUI:
1. Measure > Export measurements
2. Select output file and format
3. Choose measurements to include
4. Click "Export"

### Step 6: Quality Control

Validate phenotyping results:

```groovy
// Generate phenotype summary
def classCounts = [:]
for (cell in getCellObjects()) {
    def className = cell.getPathClass()?.toString() ?: "Unclassified"
    classCounts[className] = (classCounts[className] ?: 0) + 1
}

println "Phenotype Summary:"
classCounts.each { k, v -> 
    println "  ${k}: ${v} cells"
}
```

## Quality Criteria

- [ ] All cells have intensity measurements
- [ ] Threshold values are validated against positive controls
- [ ] Phenotype distributions match expected biology
- [ ] No unexpected cell populations
- [ ] Results are reproducible across technical replicates

## Troubleshooting

- For QuPath errors, see [QuPath Common Errors](../troubleshooting/qupath_common_errors.md)
- For classifier issues, verify threshold values on positive control samples

## References

- QuPath Documentation: https://qupath.readthedocs.io/
- QuPath Wiki: https://github.com/qupath/qupath/wiki

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-12-05 | Astraea Team | Initial version |
