# Project Close-Out Template

This document describes the workflow and schema for closing out completed Analysis Architect projects.

## Close-Out Goals

1. **Script Inventory** - Catalog all scripts, identify latest versions, deprecate old ones
2. **Reusability Assessment** - Flag scripts with potential for general pipelines
3. **Output Documentation** - Document final data locations and deliverables
4. **Archive State** - Mark project as completed with close-out metadata

---

## Close-Out Schema (TOML)

Add this section to `project.toml` when closing a project:

```toml
# ============================================================
# PROJECT CLOSE-OUT SECTION
# Add this when project is completed
# ============================================================

[closeout]
completed_date = "2025-09-25"
closed_by = "Trevor McKee"
final_delivery_date = "2025-09-20"
client_signoff = true
lessons_learned = """
- CSV-driven threshold workflow proved highly reproducible
- Sample-specific scripts were necessary due to variation in image quality
- Vessel proximity analysis became key deliverable
"""

# Final data locations
[closeout.data_locations]
raw_data = "T:\\7Hills\\RawImages\\"
processed_data = "T:\\7Hills\\Outputs\\processed\\"
final_deliverables = "T:\\7Hills\\Deliverables\\"
qupath_project = "T:\\7Hills\\QuPath\\7Hills.qpproj"
archive_location = ""  # Optional: if archived to cold storage

# ============================================================
# SCRIPT INVENTORY
# List all scripts with version status and reusability rating
# ============================================================

[[closeout.scripts]]
path = "Newer_Scripts/scripts/Script_01_rev3_ThresholdAdjustment.groovy"
language = "groovy"
purpose = "Interactive CSV-driven threshold adjustment with selective marker refinement"
version_status = "latest"  # latest | deprecated | development
related_components = ["thresh-001"]
reusability = "high"  # none | low | medium | high | very_high
reusability_notes = "Could be generalized into phenotyping-pipeline core. Remove hardcoded paths."
dependencies = ["QuPath 0.6.x"]

[[closeout.scripts]]
path = "Newer_Scripts/scripts/Script_02_rev5b_TumorArea_Exports_nomput.groovy"
language = "groovy"
purpose = "Batch cell phenotyping export with multi-level classification (1+/2+/3+)"
version_status = "latest"
related_components = ["thresh-001", "export-001"]
reusability = "high"
reusability_notes = "Export logic is generalizable. Sample-specific variants should be merged into parameterized version."
dependencies = ["QuPath 0.6.x"]

[[closeout.scripts]]
path = "scripts/Script_01_rev2_Threshold_Adjustment.groovy"
language = "groovy"
purpose = "Previous version of threshold adjustment"
version_status = "deprecated"
superseded_by = "Newer_Scripts/scripts/Script_01_rev3_ThresholdAdjustment.groovy"
reusability = "none"

[[closeout.scripts]]
path = "250801_7Hills_Gemini_vessel-surroundingtumor.ipynb"
language = "python"
purpose = "Distance-based stratification of cell phenotypes relative to vascular structures"
version_status = "latest"
related_components = ["spatial-001"]
reusability = "very_high"
reusability_notes = "Common spatial analysis pattern. Should be extracted into standalone module for Spatial Analysis SOP."
dependencies = ["pandas", "numpy", "scipy.spatial"]

[[closeout.scripts]]
path = "250412_7Hills_Statistical_Analysis_15Samples_FromCleanedData.ipynb"
language = "python"
purpose = "Multi-sample statistical aggregation and comparison"
version_status = "latest"
related_components = ["stats-001"]
reusability = "medium"
reusability_notes = "Statistical approach is generalizable but hardcoded for 15 samples."
dependencies = ["pandas", "scipy.stats", "seaborn"]

[[closeout.scripts]]
path = "250412_7Hills_Statistical_Analysis_15Samples.ipynb"
language = "python"
purpose = "Earlier version before data cleaning"
version_status = "deprecated"
superseded_by = "250412_7Hills_Statistical_Analysis_15Samples_FromCleanedData.ipynb"
reusability = "none"

# ============================================================
# DELIVERABLES
# What was delivered to the client
# ============================================================

[[closeout.deliverables]]
name = "Cell phenotype tables"
format = "csv"
location = "T:\\7Hills\\Deliverables\\phenotype_tables\\"
description = "Per-sample CSV files with cell X/Y coordinates, marker classifications (1+/2+/3+), and tumor area annotations"
delivered_date = "2025-09-15"

[[closeout.deliverables]]
name = "Vessel proximity analysis"
format = "csv"
location = "T:\\7Hills\\Deliverables\\vessel_proximity\\"
description = "Distance matrices showing cell-to-vessel distances with phenotype distribution by distance bins"
delivered_date = "2025-09-18"

[[closeout.deliverables]]
name = "Statistical summary"
format = "xlsx"
location = "T:\\7Hills\\Deliverables\\statistics\\7Hills_CrossSample_Statistics.xlsx"
description = "Cross-sample correlation matrices and statistical test results"
delivered_date = "2025-09-20"

[[closeout.deliverables]]
name = "Visualization package"
format = "png/pdf"
location = "T:\\7Hills\\Deliverables\\figures\\"
description = "Spatial plots, distance histograms, correlation heatmaps"
delivered_date = "2025-09-20"

# ============================================================
# PIPELINE CANDIDATES
# Scripts recommended for extraction into general pipelines
# ============================================================

[[closeout.pipeline_candidates]]
source_script = "250801_7Hills_Gemini_vessel-surroundingtumor.ipynb"
proposed_pipeline = "spatial-distance-stratification"
target_repo = "astraea-pipelines"
priority = "high"
effort_estimate_hours = 8.0
description = """
Extract vessel proximity analysis into standalone module:
- Parameterize structure type (vessels, ducts, etc.)
- Parameterize distance bins
- Add CLI interface
- Write tests
"""

[[closeout.pipeline_candidates]]
source_script = "Newer_Scripts/scripts/Script_01_rev3_ThresholdAdjustment.groovy"
proposed_pipeline = "qupath-csv-thresholding"
target_repo = "phenotyping-pipeline"
priority = "medium"
effort_estimate_hours = 12.0
description = """
Generalize CSV-driven threshold workflow:
- Remove project-specific paths
- Add configuration file support
- Document threshold CSV schema
- Create template CSV generator
"""
```

---

## Close-Out Checklist

### 1. Script Inventory (Manual Review)

Run this process to inventory scripts:

```bash
# Find all scripts in project directory
find /path/to/project -type f \( -name "*.py" -o -name "*.ipynb" -o -name "*.groovy" -o -name "*.R" \) | sort
```

For each script, determine:
- [ ] **Version status**: Is this the latest version or deprecated?
- [ ] **Superseded by**: If deprecated, what replaced it?
- [ ] **Purpose**: One-line description of what it does
- [ ] **Dependencies**: What tools/libraries does it require?

### 2. Version Identification Patterns

Look for these common versioning patterns:

| Pattern | Example | Interpretation |
|---------|---------|----------------|
| `_rev[N]` | `Script_01_rev3.groovy` | Revision 3 (higher = newer) |
| `_v[N]` | `analysis_v2.py` | Version 2 |
| `.old` / `.old2` | `thresholds.old2.csv` | Older version (more suffixes = older) |
| Date prefix | `250801_analysis.ipynb` | YYMMDD date stamp |
| `_final` | `report_final.ipynb` | Intended final version |
| `_Redos` | `Analysis_Redos.ipynb` | Rework iteration |
| `_updated` | `Processing_updated.ipynb` | Updated version |

**Priority for "latest"**:
1. Highest revision number (`rev5` > `rev3`)
2. Most recent date prefix
3. `_final` or `_updated` suffix
4. No `.old` suffix
5. Located in production folder (e.g., `Newer_Scripts/`)

### 3. Reusability Assessment

Rate each script's potential for general pipelines:

| Rating | Criteria |
|--------|----------|
| **very_high** | Core analysis pattern applicable to many projects; minimal modifications needed |
| **high** | Useful pattern; needs parameterization and path cleanup |
| **medium** | Some reusable logic; significant refactoring required |
| **low** | Project-specific logic; limited reuse potential |
| **none** | Deprecated or superseded; do not reuse |

**Red flags for reusability**:
- Hardcoded file paths
- Magic numbers without explanation
- No comments or documentation
- Tightly coupled to specific data structure
- Multiple responsibilities in single script

### 4. Output Documentation

Document all final outputs:

- [ ] **Raw data location**: Where original data is stored
- [ ] **Processed data location**: Intermediate processed files
- [ ] **Final deliverables**: What was sent to client
- [ ] **QuPath/analysis projects**: Project files for tools used
- [ ] **Archive location**: If data has been archived

### 5. Update Project Status

```toml
# Change project status to completed
status = "completed"

# Add closeout section (see schema above)
[closeout]
completed_date = "YYYY-MM-DD"
...
```

---

## Recommended Folder Cleanup

Before close-out, consider organizing:

```
project/
├── README.md                    # Project overview
├── project.toml                 # Project tracking (with closeout section)
├── environment.yml              # Dependencies
│
├── scripts/                     # Production scripts (latest versions only)
│   ├── groovy/
│   ├── python/
│   └── notebooks/
│
├── archive/                     # Deprecated/development scripts
│   ├── deprecated/              # Old versions (keep for reference)
│   └── development/             # Experimental scripts
│
├── config/                      # Configuration files (thresholds, etc.)
│
└── docs/                        # Project documentation
    └── closeout_summary.md      # Close-out notes
```

---

## After Close-Out

1. **Extract pipeline candidates** - Create tickets/issues for high-priority extractions
2. **Update component library** - If new reusable components were developed
3. **Archive if needed** - Move to cold storage if disk space is needed
4. **Portfolio update** - Mark project complete in `portfolio.toml`

