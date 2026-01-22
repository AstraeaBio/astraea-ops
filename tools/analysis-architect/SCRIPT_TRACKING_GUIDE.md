# Script Tracking & Output Management Guide

## Overview

Analysis Architect v1.2 now includes **Script Inventory** and **Output Tracking** features to help you:

1. **Discover and catalog** analysis scripts automatically
2. **Link scripts to components** to track which code addresses which SOW deliverable
3. **Monitor output completion** by checking if expected files exist
4. **Generate working reports** that combine progress tracking with analysis outputs

These features bridge the gap between project planning (components in `project.toml`) and actual implementation (scripts and outputs).

---

## Quick Start

### 1. Start the UI

```bash
streamlit run project_tracker_ui.py
```

Navigate to the **📜 Script Inventory** tab.

### 2. Scan for Scripts

1. Enter the directory containing your analysis scripts (defaults to project directory)
2. Click **🔄 Scan Scripts**
3. The scanner will discover all `.py`, `.ipynb`, `.R`, `.groovy`, `.sh`, and `.m` files

### 3. Review Discovered Scripts

The scanner automatically:
- Detects **version status** (latest/development/deprecated) based on filename patterns
- Identifies **language** from file extension
- Shows **last modified date** and file size

Filter results by:
- Version Status: latest, development, deprecated
- Language: python, R, groovy, etc.

### 4. Add Scripts to Inventory

For each discovered script:
1. Expand the script entry
2. Select which **components** it relates to (multi-select)
3. Click **➕ Add to Inventory**

The script is now tracked in `project.toml` under `[[code_repository]]`.

### 5. Check Output Completion

Navigate to the **📊 Output Tracking** tab to:
- See which expected outputs exist
- Identify missing outputs (analyses not yet run)
- Get completion percentages per component

---

## Script Version Detection

The scanner automatically classifies scripts based on naming patterns:

### ✅ Latest (Production)
- `analysis_script.py`
- `Script_01_rev3.groovy` (highest revision)
- `final_analysis.ipynb`

### 🔧 Development (Work in Progress)
- `test_analysis_dev.py`
- `experimental_model.ipynb`
- `draft_figures.R`

### ❌ Deprecated (Superseded)
- `analysis.old`
- `script_backup.py`
- `analysis_old2.ipynb`

**Patterns recognized:**
| Pattern | Status | Examples |
|---------|--------|----------|
| `.old`, `_old`, `_backup` | deprecated | `data.old`, `script_old.py` |
| `_dev`, `_test`, `_experimental` | development | `model_dev.py`, `test_pipeline.R` |
| `_revN`, `_final`, clean names | latest | `Script_rev3.groovy`, `analysis.ipynb` |

---

## Schema: `code_repository`

Scripts added via the UI are stored in `project.toml` as:

```toml
[[code_repository]]
script = "analysis_pipeline.py"
location = "scripts/analysis_pipeline.py"
component_ids = ["seg-001", "spatial-001"]
last_modified = "2025-01-21"
language = "python"
version_status = "latest"
```

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `script` | string | Script filename |
| `location` | string | Relative or absolute path |
| `component_ids` | list | Components this script addresses |
| `last_modified` | date | Last modification date (YYYY-MM-DD) |
| `language` | string | python, R, groovy, bash, matlab, other |
| `version_status` | string | latest, development, deprecated |

---

## Output Tracking Features

### Component Output Verification

The **Output Tracking** tab checks if expected outputs exist:

1. **Select a component** from the dropdown
2. View all expected outputs defined in `[[components.outputs]]`
3. See which files exist (✅) vs. missing (❌)
4. Get overall completion percentage

### Output Status Icons

- ✅ **Green check**: File exists locally
- ❌ **Red X**: File expected but not found
- ☁️ **Cloud**: Cloud storage path (cannot verify locally)

### Bulk Output Check

Click **🔄 Check All Component Outputs** to see completion across all components in a table.

---

## Integration with Project Close-Out

For completed projects, scripts can also be tracked in the `[closeout]` section:

```toml
[closeout]
completed_date = "2025-01-21"
closed_by = "Analyst Name"

[[closeout.scripts]]
path = "scripts/final_analysis.py"
language = "python"
purpose = "Primary analysis pipeline for vessel proximity"
version_status = "latest"
related_components = ["vessel-proximity"]
reusability = "high"
reusability_notes = "Generalizable to other spatial distance calculations"
dependencies = ["pandas", "numpy", "scipy"]
```

The **Script Inventory** tab automatically shows scripts from both `code_repository` and `closeout.scripts`.

---

## Workflow: From SOW to Scripts to Outputs

### 1. **SOW Parsing** → Components Created
Use `sow_parser_prompt.md` to generate initial `project.toml` with components and expected outputs.

### 2. **Script Development** → Track in Inventory
As you write analysis scripts:
- Store them in a consistent location (e.g., `scripts/` folder)
- Scan periodically via the UI
- Link scripts to components

### 3. **Analysis Execution** → Monitor Outputs
As analyses complete:
- Check Output Tracking tab to verify files exist
- Update component `progress_fraction` and `status`
- Mark components as `completed` when outputs exist

### 4. **Report Generation** → Use Script Inventory
When generating client reports:
- Reference the script inventory to document what was done
- Use output tracking to identify completed analyses
- Generate working reports that show progress + results

---

## Example: Tracking a QuPath Project

### Scenario
You have a QuPath-based image analysis project with multiple Groovy scripts.

### Step 1: Directory Structure
```
251119_7Hills/
├── project.toml
├── scripts/
│   ├── Script_01_rev3_ThresholdAdjustment.groovy
│   ├── Script_02_rev5b_TumorArea_Exports.groovy
│   ├── Script_01_rev2.groovy.old
│   └── test_script_dev.groovy
└── Outputs/
    ├── cell_exports/
    └── figures/
```

### Step 2: Scan Scripts
1. Open **Script Inventory** tab
2. Enter `T:\Analysis\251119_7Hills\scripts` as scripts directory
3. Click **Scan Scripts**

Results:
- `Script_01_rev3_ThresholdAdjustment.groovy` → **latest**
- `Script_02_rev5b_TumorArea_Exports.groovy` → **latest**
- `Script_01_rev2.groovy.old` → **deprecated**
- `test_script_dev.groovy` → **development**

### Step 3: Link to Components
- Script 01 → Link to `threshold-adjustment` component
- Script 02 → Link to `cell-export` component

### Step 4: Check Outputs
Navigate to **Output Tracking**, select `cell-export` component:
- Expected: `Outputs/cell_exports/sample_01_cells.csv`
- Status: ✅ Exists
- Completion: 100%

---

## Manual Script Addition

If you have scripts not in a scannable directory or want more control:

1. Scroll to **➕ Add Script Manually** section
2. Fill in:
   - **Script Name**: `custom_analysis.R`
   - **Script Location**: `external/custom_analysis.R`
   - **Language**: R
   - **Link to Components**: Select relevant component IDs
3. Click **➕ Add Script**

---

## Use Cases

### Use Case 1: New Project Setup
**Goal**: Track all scripts as you develop them.

1. Create project from SOW
2. Set up scripts directory
3. Scan weekly to add new scripts
4. Link scripts to components as you write them

### Use Case 2: Mid-Project Check-In
**Goal**: Verify which analyses are complete.

1. Open Output Tracking tab
2. Check outputs for in-progress components
3. Identify missing outputs (analyses to prioritize)
4. Update component status based on output existence

### Use Case 3: Project Close-Out
**Goal**: Document all scripts and outputs for future reference.

1. Final scan of scripts directory
2. Add all scripts to inventory
3. Add `[closeout]` section with detailed script metadata
4. Verify all outputs exist
5. Mark project as `completed`

### Use Case 4: Client Report Generation
**Goal**: Create a working report showing progress.

1. Use Script Inventory to list completed analyses
2. Use Output Tracking to verify deliverables exist
3. Reference ANALYSIS_REPORT_PROMPT_TEMPLATE.md
4. Generate report combining:
   - Component status (from Overview tab)
   - Script inventory (what was done)
   - Output verification (what was delivered)

---

## Tips & Best Practices

### Organizing Scripts

**✅ Recommended Structure:**
```
project/
├── project.toml
├── scripts/
│   ├── 01_preprocessing.py
│   ├── 02_segmentation.ipynb
│   ├── 03_analysis.py
│   └── 04_figures.R
└── Outputs/
    ├── processed_data/
    ├── figures/
    └── tables/
```

**❌ Avoid:**
- Multiple scattered script folders
- Mixed old/new versions in same directory without naming convention
- Scripts in root directory with data files

### Naming Conventions

Use clear version indicators:
- **Revisions**: `Script_01_rev3.groovy` (increment `rev` number)
- **Deprecation**: Add `.old` or move to `archive/` folder
- **Development**: Add `_dev`, `_test`, or `_wip` suffix

### Output Definitions

Define outputs in `project.toml` components:
```toml
[[components.outputs]]
type = "csv"
location = "Outputs/analysis/results.csv"
expected_date = "2025-01-30"

[[components.outputs]]
type = "png"
location = "Outputs/figures/Figure_1.png"
```

This enables automatic tracking via the UI.

### Cloud Storage

For cloud storage paths (GCS, S3), the UI will show ☁️ but cannot verify locally:
```toml
[[components.outputs]]
type = "parquet"
location = "gs://bucket-name/processed/data.parquet"
```

You'll need to verify these manually via cloud console.

---

## Troubleshooting

### Scripts Not Found During Scan

**Problem**: Clicked "Scan Scripts" but no results.

**Solutions:**
1. Check the directory path is correct
2. Verify scripts have recognized extensions (`.py`, `.ipynb`, `.R`, `.groovy`, `.sh`, `.m`)
3. Check for typos in path (use absolute paths if relative doesn't work)

### Cannot Add Script to Inventory

**Problem**: Click "Add to Inventory" but nothing happens.

**Solutions:**
1. Ensure you selected at least one component to link
2. Check browser console for errors
3. Verify `project.toml` is writable (not open in another program)

### Output Shows as Missing But File Exists

**Problem**: Output Tracking shows ❌ but file exists.

**Solutions:**
1. Check the `location` path in `project.toml` matches actual file path
2. Verify path is relative to project directory, not absolute
3. For cloud storage, accept that local verification isn't possible (☁️ shown)

### Version Detection Wrong

**Problem**: Scanner marks a latest script as "deprecated".

**Solutions:**
1. Rename the file to remove patterns like `.old`, `_backup`
2. Manually edit `version_status` in `project.toml` after adding
3. Use clear naming: `script_rev3.py` instead of ambiguous names

---

## Next Steps: Phase 2 Integration

Future enhancements (Phase 2) will include:

1. **Report Builder Tab**: Auto-generate working reports using ANALYSIS_REPORT_PROMPT_TEMPLATE
2. **Script Output Parsing**: Extract figures/tables from script outputs automatically
3. **Progress Inference**: Update component status based on output file existence
4. **Batch Script Linking**: Link multiple scripts to components at once
5. **Script Execution Tracking**: Log when scripts were run

---

## Related Documentation

- **CLAUDE.md** - Project instructions and repository overview
- **ANALYSIS_REPORT_PROMPT_TEMPLATE.md** - Standardized report generation
- **PROJECT_CLOSEOUT_TEMPLATE.md** - Close-out schema and workflow
- **README.md** - User-facing documentation

---

*Guide Version: 1.2 | Updated: 2025-01-21*
