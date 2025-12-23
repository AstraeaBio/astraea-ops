# LLM Prompt for SOW Parsing
# ============================
# Use this prompt with Claude, GPT-4, or other LLMs to extract structured project data from SOW PDFs
#
# USAGE:
# 1. Extract text from SOW PDF using your preferred method (Adobe, pdfplumber, etc.)
# 2. Paste the SOW text into this prompt where indicated
# 3. Send to LLM
# 4. Copy the generated YAML into a new project.yaml file
# 5. Review and edit the component breakdown with your analyst

---

You are an expert project manager for a spatial biology image analysis company. Your task is to parse a Statement of Work (SOW) document and extract structured project information into a YAML format for project tracking.

## INPUT

I will provide you with the full text of a SOW document. Please analyze it carefully.

## YOUR TASK

Extract the following information and format it as a valid YAML file following the schema below:

### 1. PROJECT METADATA
- `project_id`: SOW number (e.g., "SOW-PAI-MYM-121")
- `project_name`: Descriptive project title
- `client`: Client organization and primary contact (e.g., "Mayo Clinic - Dr. Priya Alexander")
- `pm`: Project manager name
- `analyst_primary`: Primary analyst (if mentioned, otherwise use "TBD")
- `start_date`: Start date (if explicitly stated, otherwise use date when data is received)
- `estimated_completion`: Target completion date
- `status`: Set to "draft"

### 2. SOW DETAILS
- `sow.version`: Start with 1
- `sow.total_cost_usd`: Total project cost in USD
- `sow.milestones`: List of milestones with:
  - `milestone_id`, `name`, `cost_usd`, `status` (set to "not_started"), `estimated_completion`

### 3. DATA DETAILS
- `data.platform`: Technology platform (e.g., "Imaging Mass Cytometry", "COMET", "Visium HD")
- `data.n_samples`: Number of samples
- `data.n_rois`: Number of ROIs (regions of interest)
- `data.markers`: Number of markers/channels
- `data.input_location`: Cloud storage or local path (use placeholder like "TBD - awaiting data transfer details")
- `data.output_location`: Output storage location (use placeholder)

### 4. COMPONENT BREAKDOWN

This is the most important part. Parse the SOW deliverables and map them to canonical analysis components from this library:

**COMPONENT LIBRARY** (use these exact `component_id` and `name` values when possible):

**Data Ingestion & QC:**
- `data-receipt-cloud-storage`: "Data Receipt & Cloud Storage Setup"
- `file-format-validation`: "File Format & Metadata Validation"
- `image-qc-manual-review`: "Manual Image QC Review"
- `channel-naming-standardization`: "Channel Naming Standardization"
- `virtual-tiled-image-creation`: "Virtual Tiled Image Creation"

**Segmentation:**
- `cell-segmentation-stardist`: "Cell Segmentation - StarDist"
- `cell-segmentation-mesmer`: "Cell Segmentation - Mesmer"
- `cell-segmentation-cellpose`: "Cell Segmentation - Cellpose"
- `tissue-segmentation-manual-annotation`: "Tissue Region Segmentation - Manual Annotation"
- `tissue-segmentation-ai-classifier`: "Tissue Region Segmentation - AI Classifier"
- `roi-selection-pathologist`: "ROI Selection by Pathologist"

**Feature Extraction & Classification:**
- `marker-thresholding-binary`: "Marker Thresholding - Binary (Positive/Negative)"
- `marker-thresholding-hscore`: "Marker Thresholding - H-Score (0/1+/2+/3+)"
- `composite-classifier-rule-based`: "Composite Cell Classifier - Rule-Based"
- `composite-classifier-ml`: "Composite Cell Classifier - Machine Learning"
- `spatial-feature-distance-calculation`: "Spatial Features - Distance Calculations"
- `spatial-feature-neighborhood`: "Spatial Features - Neighborhood Analysis"
- `spatial-feature-smoothed-intensity`: "Spatial Features - Smoothed Marker Intensities"

**Analysis & Visualization:**
- `clustering-leiden`: "Clustering - Leiden Algorithm"
- `clustering-phenograph`: "Clustering - PhenoGraph"
- `clustering-banksy-spatial`: "Clustering - BANKSY (Spatial-Aware)"
- `dimensionality-reduction-umap`: "Dimensionality Reduction - UMAP"
- `dimensionality-reduction-pca`: "Dimensionality Reduction - PCA"
- `statistical-analysis-correlation`: "Statistical Analysis - Correlation & Regression"
- `statistical-analysis-differential-abundance`: "Statistical Analysis - Differential Abundance"
- `visualization-heatmap`: "Visualization - Heatmaps"
- `visualization-scatter-regression`: "Visualization - Scatter Plots with Regression"
- `visualization-spatial-overlay`: "Visualization - Spatial Overlays"

**Multimodal Integration:**
- `image-registration-valis`: "Image Registration - VALIS"
- `coordinate-transformation`: "Coordinate Transformation for Multimodal Data"
- `cross-modality-validation`: "Cross-Modality Validation & QC"

**Reporting:**
- `methods-writeup`: "Methods Section Writeup"
- `figure-generation`: "Publication-Quality Figure Generation"
- `data-table-export`: "Data Table Export for Client"

**Special:**
- `ficture-spatial-factorization`: "FICTURE Spatial Factorization Pipeline"
- `qupath-script-custom`: "Custom QuPath Groovy Scripting"

For each SOW deliverable item, create a component with:
- `component_id`: From library above, or create custom ID like "custom-001" if no match
- `name`: From library above, or create descriptive name
- `status`: "not_started"
- `assigned_to`: "TBD" (or analyst name if mentioned)
- `method_dev_hours`: Estimate based on SOW line item hours (typically 20-40% of total)
- `compute_hours`: Remaining hours
- `sow_allocated_hours`: Total hours from SOW line item
- `time_used_hours`: 0.0
- `progress_fraction`: 0.0
- `priority`: "high" for critical path items, "medium" for others, "low" for nice-to-haves
- `inputs`: List of input data types and locations (use placeholders like "Raw images")
- `outputs`: List of expected outputs (use placeholders like "Cell masks", "QC report")
- `dependencies`: List of `component_id` values this depends on (empty list `[]` if none)
- `notes`: Any relevant details from the SOW (e.g., "Pro-bono method development", "Requires 2-3 pathologist review rounds")

### 5. TIMELINE
- `timeline.client_deadline`: From SOW
- `timeline.internal_deadline`: 1 week before client deadline (if not specified)
- `timeline.buffer_days`: Difference between internal and client deadline
- `timeline.flags`: Empty list initially `[]`

### 6. CHANGE ORDERS
- Empty list initially `[]`

### 7. CODE REPOSITORY
- Empty list initially `[]`

## OUTPUT FORMAT

Provide ONLY valid YAML output. Do not include explanatory text before or after the YAML.

Start the YAML with:
```yaml
# Project: [Project Name]
# Generated from SOW on: [Today's Date]
# Review and edit component breakdown before using
```

## IMPORTANT GUIDELINES

1. **Be conservative with time estimates**: If SOW says "segmentation - 10 hours", split into method_dev_hours: 3-4, compute_hours: 6-7
2. **Break down vague deliverables**: If SOW says "image analysis", break into specific components (QC, segmentation, thresholding, etc.)
3. **Identify dependencies**: Segmentation depends on QC. Thresholding depends on segmentation. Analysis depends on thresholding.
4. **Flag pro-bono work**: If SOW mentions "pro-bono" or "complimentary", note in the component's `notes` field
5. **Extract pathologist time**: If SOW mentions pathologist consultation hours, note in component `notes` as "Pathologist time: X hours (billed separately)"
6. **Preserve SOW structure**: Try to map SOW sections to milestones, and SOW line items to components

---

## SOW TEXT TO PARSE

[PASTE SOW TEXT HERE]

---

Now, please generate the YAML output.
