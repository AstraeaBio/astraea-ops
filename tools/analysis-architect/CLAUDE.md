# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

Analysis Architect is a project tracking and planning tool for spatial biology image analysis projects. It helps project managers and analysts:

- Parse SOWs (Statements of Work) from client PDFs using LLMs
- Track progress on analysis components in real-time
- Generate client status updates automatically
- Maintain a canonical library of reusable analysis components

The system uses TOML files for project storage and a Streamlit web UI for interactive tracking.

## Quick Start Commands

### Starting the Web UI

```bash
streamlit run project_tracker_ui.py
```

The UI opens at `http://localhost:8501` and provides:
- Project overview dashboard with traffic light status indicators
- Component update interface for analysts
- Client summary generation for project managers
- **Report Builder** for comprehensive analysis reports (v1.2)
- Script inventory and output tracking (v1.2)
- Component library browser

### Installing Dependencies

```bash
pip install -r requirements.txt
```

Core dependencies:
- `streamlit>=1.28.0` - Web UI framework
- `tomli>=2.0.0` - TOML file reading (Python 3.11+ has built-in tomllib)
- `tomli-w>=1.0.0` - TOML file writing
- `pandas>=2.0.0` - Data manipulation

### Creating a New Project from SOW

⚠️ **IMPORTANT:** Before starting, ensure your project has required fields. See **PROJECT_SETUP_CHECKLIST.md** for validation requirements.

1. Extract text from SOW PDF
2. Open `sow_parser_prompt.md` in an editor (note CRITICAL REQUIREMENTS section)
3. Copy the prompt and paste SOW text where indicated
4. Send to Claude/GPT-4 to generate project TOML
5. **Verify output includes:**
   - `sow.total_cost_usd` (number, not string)
   - At least one `[[sow.milestones]]` entry
   - At least one `[[components]]` entry
   - `estimated_completion` date
6. Save output as `[project_folder]/project.toml`
7. Open in web UI to review and adjust
8. **Check sidebar validation** - fix any ❌ or ⚠️ issues before using

## Project Structure

### Root-Level Files

- **`project_tracker_ui.py`** - Main Streamlit application (500+ lines)
- **`components_library.toml`** - Canonical library of ~40 reusable analysis components organized by phase
- **`sow_parser_prompt.md`** - LLM prompt template for parsing SOW PDFs into structured TOML
- **`example_project.toml`** - Template showing complete project TOML structure
- **`project.toml`** - Example project in root directory
- **`requirements.txt`** - Python dependencies

### Project Subdirectories

The repository contains example projects as subdirectories:
- **`251119_7Hills/`** - 7Hills tumor-vessel analysis project
- **`251125_CellSighter/`** - CellSighter deep learning classifier project
- **`maitra_sow124/`** - Multimodal spatial biology project (Visium HD + COMET + MSI)

Each project subdirectory may contain:
- `project.toml` - Project tracking file
- Analysis scripts and notebooks
- Project-specific documentation

## Core Architecture

### TOML Schema

All projects use a consistent TOML structure defined in `example_project.toml`:

```toml
project_id = "SOW-XXX-YYY-NNN"
project_name = "Descriptive Title"
client = "Organization - Contact Name"
pm = "Project Manager"
analyst_primary = "Lead Analyst"
status = "draft"  # draft | in_progress | completed | on_hold

[sow]
version = 1
total_cost_usd = 16800

[[sow.milestones]]
# milestones defined here

[data]
platform = "Technology Platform"
n_samples = N
n_rois = N
markers = N

[[components]]
component_id = "unique-id"
name = "Component Name"
status = "not_started"  # not_started | in_progress | completed | blocked
assigned_to = "Analyst Name"
method_dev_hours = X.X
compute_hours = X.X
sow_allocated_hours = X.X
time_used_hours = X.X
progress_fraction = 0.0
priority = "low"  # low | medium | high
dependencies = ["component-id"]
notes = "..."

[[components.inputs]]
# input definitions

[[components.outputs]]
# output definitions

[timeline]
client_deadline = "YYYY-MM-DD"
internal_deadline = "YYYY-MM-DD"
buffer_days = N

[[timeline.flags]]
# flag definitions

[[change_orders]]
# change order definitions

[[code_repository]]
# repository definitions
```

### Traffic Light Status System

Components are automatically flagged in `calculate_status()` (project_tracker_ui.py:48):

- **🟢 Green (Good)**: `utilization < 0.7` AND `progress > 0.5`
- **🟡 Yellow (Caution)**: Everything else not red
- **🔴 Red (Flag)**: `utilization > 1.0` OR (`progress < 0.3` AND `utilization > 0.6`)

Where `utilization = time_used_hours / sow_allocated_hours`

### Component Library Structure

The `components_library.toml` file organizes components into phases:

1. **phase_1_data_ingestion_qc** (5 components)
2. **phase_2_segmentation** (6 components)
3. **phase_3_feature_extraction_classification** (7 components)
4. **phase_4_analysis_visualization** (10 components)
5. **phase_5_multimodal_integration** (3 components)
6. **phase_6_reporting** (3 components)
7. **phase_7_special_custom** (custom components)

Each component includes:
- `component_id` - Unique identifier (e.g., "data-receipt-cloud-storage")
- `name` - Display name
- `description` - What the component does
- `typical_method_dev_hours` - [min, max] ranges
- `typical_compute_hours` - [min, max] ranges
- `software_dependencies` - Required tools
- `inputs`/`outputs` - Data types
- `notes` - Special considerations

## Key Workflows

### For Analysts: Updating Progress

1. Start web UI: `streamlit run project_tracker_ui.py`
2. Select project from sidebar dropdown
3. Navigate to "Update Components" tab
4. Select component to update
5. Update fields:
   - Status dropdown (not_started → in_progress → completed)
   - Progress slider (0-100%)
   - Time Used (hours)
   - Notes (blockers, decisions, etc.)
6. Click "Save Changes"
7. Check "Overview" tab for traffic light warnings

### For PMs: Creating New Projects

1. Extract SOW text from PDF
2. Follow `sow_parser_prompt.md` instructions to generate YAML via LLM
3. Save to `[project_name]/project.yaml`
4. Open in web UI to review:
   - Component breakdown matches SOW
   - Time estimates are reasonable
   - Dependencies are correct
5. Adjust components using "Add Component" tab if needed
6. Set `status: "in_progress"` when data arrives

### For PMs: Generating Client Updates

1. Select project in web UI
2. Navigate to "Client Summary" tab
3. Review auto-generated markdown:
   - Completed milestones ✅
   - In-progress components with % complete
   - Blocked items with blocker descriptions
4. Click "Download as Markdown" or copy-paste to email

### For Analysts/PMs: Generating Analysis Reports (v1.2)

1. Start web UI and select completed (or near-complete) project
2. Navigate to "Report Builder" tab
3. Configure report options:
   - Toggle "Include Script Inventory" (default: on)
   - Toggle "Include Component Deliverables" (default: on)
   - Optionally filter to specific components
4. Click "Generate Report"
5. Review preview in expander
6. Click "Download as Markdown (.md)"
7. Open downloaded file in editor (VS Code, Typora, etc.)
8. Fill in placeholder sections:
   - `[TO BE FILLED:]` sections with actual content
   - Replace `[INSERT FIGURE X HERE]` with figure paths
   - Update result tables with real data and p-values
   - Complete executive summary and conclusions
9. Convert to Word/PDF:
   ```bash
   pandoc report.md -o report.docx --toc --toc-depth=2
   ```
10. Share with client or internal team

**Report Structure** (based on ANALYSIS_REPORT_PROMPT_TEMPLATE.md):
- Executive Summary & Key Findings
- Study Design (data characteristics, methodology)
- Results sections with tables and figure placeholders
- Component Deliverables (completed work)
- Analysis Scripts & Pipeline (script inventory)
- Conclusions, Limitations, Future Directions
- Appendices (data locations, methods)

**Tip:** Generate report early to identify missing deliverables and guide remaining work.

## File Reading Patterns

The codebase uses TOML extensively. Key helper functions in `project_tracker_ui.py`:

```python
load_project_toml(filepath)  # Returns dict from TOML file
save_project_toml(filepath, data)  # Writes dict to TOML file
load_components_library()  # Returns flat list of all components
```

Projects are discovered via:
```python
project_files = list(Path(projects_dir).glob("**/project.toml"))
```

## Customization Points

### Adding New Components to Library

Edit `components_library.toml` under appropriate phase:

```toml
[[phase_X_your_phase]]
component_id = "new-component-id"
name = "New Component Name"
description = "What it does"
typical_method_dev_hours = [2.0, 4.0]
typical_compute_hours = [3.0, 6.0]
software_dependencies = ["tool1", "tool2"]
notes = "Special considerations"
```

### Modifying Traffic Light Thresholds

Edit `project_tracker_ui.py:48` in `calculate_status()` function to adjust warning thresholds.

### Extending Project TOML Schema

Add custom fields to `project.toml` files as needed. The UI will preserve unknown fields when saving. Update UI forms in `project_tracker_ui.py` tabs to display/edit new fields.

## Data Flows

### SOW → Project TOML

1. PM extracts SOW text from PDF
2. LLM parses using `sow_parser_prompt.md` instructions
3. LLM matches deliverables to component library IDs
4. LLM generates TOML with estimated hours
5. PM reviews and adjusts in web UI

### Analyst Updates → Project TOML

1. Analyst updates component in web UI
2. `save_project_toml()` writes to disk immediately
3. UI reloads to show updated traffic light status
4. No database - TOML files are source of truth

### Project TOML → Client Summary

1. `generate_client_summary()` reads project data
2. Filters out internal details (hours, blockers)
3. Generates markdown with public-facing status
4. PM copies to client communication

### Project TOML → Analysis Report (v1.2)

1. PM or analyst navigates to "Report Builder" tab
2. Selects report configuration (components, scripts, outputs)
3. Clicks "Generate Report"
4. `generate_analysis_report()` creates comprehensive markdown report
5. Downloads markdown file for editing
6. Fills in placeholder sections with actual results
7. Converts to Word/PDF using pandoc

## Important Conventions

### Component IDs

Use kebab-case with phase prefix:
- `data-receipt-cloud-storage`
- `seg-001` (numbered for custom components)
- `spatial-feature-distance-calculation`

### File Paths

- All paths in `project.toml` should be absolute or relative to project directory
- Cloud storage paths use `gs://` prefix for Google Cloud Storage
- Local paths use platform-appropriate separators

### Time Tracking

- All time values in **hours** (not days)
- `sow_allocated_hours` = `method_dev_hours` + `compute_hours` (typically)
- Cost calculation: `total_cost_usd / 250` = total hours at $250/hr

### Status Values

Controlled vocabularies (do not use other values):
- Project status: `draft`, `in_progress`, `completed`, `on_hold`
- Component status: `not_started`, `in_progress`, `completed`, `blocked`
- Priority: `low`, `medium`, `high`
- Blocker severity: `low`, `medium`, `high`

## Common Development Tasks

### Adding a New Tab to Web UI

1. Add tab in `st.tabs()` call (project_tracker_ui.py:172)
2. Create corresponding `with tabN:` block
3. Use `project_data` dict which contains current project
4. Call `save_project_toml()` if making edits
5. Call `st.rerun()` after saving to refresh UI

### Adding a New Field to Components

1. Update `example_project.toml` with example
2. Add input widget in "Update Components" tab (project_tracker_ui.py:255+)
3. Add save logic in button handler (project_tracker_ui.py:360+)
4. Update display in "Overview" tab if needed (project_tracker_ui.py:178+)

### Modifying SOW Parser Prompt

Edit `sow_parser_prompt.md`:
- Component library definitions (lines 52-103)
- Output schema instructions (lines 104-131)
- Important guidelines (lines 143-151)

Test with actual SOW text to verify output quality.

## Project-Specific Notes

### 7Hills Project (251119_7Hills/)

Completed tumor-vessel spatial analysis using QuPath + Python notebooks. See project README.md for workflow details. Has `project.toml` with full close-out documentation including script inventory, reusability assessments, and pipeline candidates. Use as reference for close-out process.

### CellSighter Project (251125_CellSighter/)

Deep learning cell classifier project. Has extensive documentation in `.github/copilot-instructions.md` covering the full training/inference pipeline. Not using Analysis Architect tracker.

### Maitra SOW124 (maitra_sow124/)

Multimodal spatial biology project with comprehensive CLAUDE.md. Uses conda environment with complex dependencies. Has example of well-structured project documentation.

## Portfolio Management (v1.1)

### Overview

Portfolio management enables tracking multiple projects simultaneously for resource allocation, workload balancing, and batch processing.

### Key Files

- **`portfolio_lib.py`** - Shared library with portfolio functions
- **`portfolio.toml`** - Portfolio manifest listing active projects
- **`example_portfolio.toml`** - Template for creating portfolios
- **`logs/portfolio_YYYY-MM-DD.json`** - Daily snapshots

### Core Functions

```python
# Load portfolio and all projects
portfolio_data = portfolio_lib.load_portfolio('portfolio.toml')

# Get next actionable task (dependency-based)
next_task = portfolio_lib.get_next_task(project_data)

# Detect batchable tasks across projects
batches = portfolio_lib.detect_batch_candidates(portfolio_data)

# Calculate analyst workload aggregation
workload = portfolio_lib.calculate_analyst_workload(portfolio_data)

# Get immediate attention items (Tuesday morning view)
attention = portfolio_lib.get_immediate_attention_items(portfolio_data)

# Create daily snapshot for historical tracking
snapshot = portfolio_lib.create_daily_snapshot(portfolio_data)
```

### Portfolio Schema

```toml
portfolio_name = "Astraea Active Projects"
portfolio_id = "main"

[[projects]]
path = "path/to/project.toml"
active = true

[analyst_capacity]
Sharon = 6.0  # hours/day

[time_settings]
hours_per_day = 3.0  # Conservative productivity estimate

[batching]
enabled = true
min_batch_size = 2
batchable_components = ["cell-segmentation-stardist", ...]
```

### UI Integration

Portfolio Overview tab appears when `portfolio.toml` is loaded via sidebar:
- **Portfolio Health**: Metrics across all projects
- **Immediate Attention**: Overdue, blocked, high utilization items
- **Analyst Workload**: Utilization by analyst across projects
- **Batch Opportunities**: Auto-detected batchable tasks
- **Timeline Overview**: Deadline tracking

### Next Task Logic

Identifies next actionable task per project:
1. Find all `not_started` components
2. Filter to those with fulfilled dependencies
3. Return highest priority component

This enables dependency-based workflow rather than sequential execution.

### Batch Detection

Groups tasks by:
- Component type (segmentation, thresholding, etc.)
- Platform (IMC, CyCIF, CODEX, etc.)
- Status (not_started, in_progress)
- Configurable minimum batch size

Use case: Schedule GPU runs for multiple projects, batch pathologist reviews.

### Daily Snapshot Logging

Automatically log portfolio state for trend analysis:
- Portfolio summary (project counts, component status)
- Analyst utilization (hours used/allocated)
- Project details (progress, deadlines, next tasks)

Enable via cron/scheduled task or manual calls to `create_daily_snapshot()`.

### Documentation

- **PORTFOLIO_QUICKSTART.md** - User guide for portfolio features
- **PORTFOLIO_REQUIREMENTS.md** - Detailed specifications and use cases

## Project Close-Out (v1.2)

### Overview

Project close-out is the process of documenting a completed project to capture scripts, identify reusable components, and archive final deliverables.

### Key Files

- **`PROJECT_CLOSEOUT_TEMPLATE.md`** - Full close-out workflow and schema documentation
- **`251119_7Hills/project.toml`** - Example of a closed-out project with full inventory

### Close-Out Schema

Add a `[closeout]` section to `project.toml` when completing a project:

```toml
[closeout]
completed_date = "YYYY-MM-DD"
closed_by = "Analyst Name"
final_delivery_date = "YYYY-MM-DD"
client_signoff = true
lessons_learned = """Multi-line notes about what worked and what didn't"""

[closeout.data_locations]
raw_data = "path/to/raw/"
processed_data = "path/to/processed/"
final_deliverables = "path/to/deliverables/"
archive_location = ""  # Optional

[[closeout.scripts]]
path = "path/to/script.py"
language = "python"
purpose = "What the script does"
version_status = "latest"  # latest | deprecated | development
related_components = ["component-id"]
reusability = "high"  # none | low | medium | high | very_high
reusability_notes = "How to generalize this script"
dependencies = ["pandas", "numpy"]
superseded_by = ""  # For deprecated scripts

[[closeout.deliverables]]
name = "Deliverable Name"
format = "csv"
location = "path/to/deliverable/"
description = "What was delivered"
delivered_date = "YYYY-MM-DD"

[[closeout.pipeline_candidates]]
source_script = "path/to/script.py"
proposed_pipeline = "pipeline-name"
target_repo = "repo-name"
priority = "high"
effort_estimate_hours = 8.0
description = """What needs to be done to extract into a reusable pipeline"""
```

### Close-Out Workflow

1. **Set project status to completed**: `status = "completed"`
2. **Inventory all scripts**: Find all `.py`, `.ipynb`, `.groovy`, `.R` files
3. **Identify latest versions**: Use versioning patterns (`_rev[N]`, `.old`, date prefixes)
4. **Assess reusability**: Rate each script's potential for general pipelines
5. **Document outputs**: Record final data locations and deliverables
6. **Add `[closeout]` section**: Populate the close-out schema
7. **Extract pipeline candidates**: Create tickets for high-priority extractions

### Version Status Values

- **latest**: Current production version, use this
- **deprecated**: Old version, replaced by another script
- **development**: Experimental/testing, not for production

### Reusability Ratings

| Rating | Criteria |
|--------|----------|
| **very_high** | Core analysis pattern, minimal modifications needed |
| **high** | Useful pattern, needs parameterization |
| **medium** | Some reusable logic, significant refactoring required |
| **low** | Project-specific, limited reuse potential |
| **none** | Deprecated or superseded |

### Version Identification Patterns

Common patterns to identify latest vs old scripts:

| Pattern | Example | Interpretation |
|---------|---------|----------------|
| `_rev[N]` | `Script_01_rev3.groovy` | Higher = newer |
| `.old` / `.old2` | `data.old2.csv` | More suffixes = older |
| Date prefix | `250801_analysis.ipynb` | YYMMDD stamp |
| `_final` | `report_final.ipynb` | Intended final |
| Folder | `Newer_Scripts/` vs `scripts/` | Named folders indicate current |

## Script Tracking & Output Management (v1.2)

### Overview

Script tracking enables discovery, cataloging, and linking of analysis scripts to project components, bridging the gap between SOW planning and actual code implementation.

### Key Files

- **SCRIPT_TRACKING_GUIDE.md** - Comprehensive guide to script inventory and output tracking

### UI Tabs (New in v1.2)

#### 📜 Script Inventory Tab
- **Script Discovery**: Auto-scan directories for `.py`, `.ipynb`, `.R`, `.groovy`, `.sh`, `.m` files
- **Current Inventory**: View tracked scripts from `code_repository` and `closeout.scripts`
- **Linking**: Multi-select components to link scripts to deliverables
- **Version Detection**: Automatically classifies scripts as latest/development/deprecated
- **Manual Addition**: Add scripts not in scannable directories

#### 📊 Output Tracking Tab
- **Component Outputs**: Verify expected output files exist
- **Completion %**: Calculate progress based on file existence
- **Status Indicators**: ✅ exists, ❌ missing, ☁️ cloud storage
- **Bulk Check**: Check all components at once

### Core Functions

```python
# Scan directory for scripts
scan_scripts_directory(directory_path, extensions=None)

# Detect version status from filename patterns
detect_version_status(filename)  # latest | development | deprecated

# Check if component outputs exist
check_component_outputs(component, project_dir)
```

### Version Detection Patterns

| Pattern | Status | Examples |
|---------|--------|----------|
| `.old`, `_old`, `_backup` | deprecated | `script.old`, `analysis_backup.py` |
| `_dev`, `_test`, `_experimental` | development | `model_dev.ipynb`, `test_pipeline.R` |
| `_revN`, `_final`, clean names | latest | `Script_rev3.groovy`, `final_analysis.py` |

### Schema: `code_repository`

```toml
[[code_repository]]
script = "analysis_pipeline.py"
location = "scripts/analysis_pipeline.py"
component_ids = ["seg-001", "spatial-001"]
last_modified = "2025-01-21"
language = "python"
version_status = "latest"
```

### Workflow Integration

**SOW → Components → Scripts → Outputs → Reports:**

1. Parse SOW → Generate `project.toml` with components
2. Write scripts → Scan and add to inventory
3. Link scripts → Connect to component deliverables
4. Run analyses → Check output tracking
5. Update progress → Mark complete when outputs exist
6. Generate reports → Use inventory for documentation

### Example Usage

```python
# 1. Scan project scripts directory
# UI: Navigate to Script Inventory tab → Enter path → Click "Scan Scripts"

# 2. Link discovered scripts to components
# UI: Expand script → Select components → Click "Add to Inventory"

# 3. Check output completion
# UI: Navigate to Output Tracking tab → Select component → View status

# 4. Update component based on outputs
# If outputs exist → Update component status to "completed"
```

See **SCRIPT_TRACKING_GUIDE.md** for detailed workflows and examples.

## Additional Resources

- **PROJECT_SETUP_CHECKLIST.md** - ⚠️ Required fields and validation checklist for new projects
- **README.md** - User-facing documentation with workflow examples and FAQ
- **SCRIPT_TRACKING_GUIDE.md** - Script inventory and output tracking guide (v1.2)
- **ANALYSIS_REPORT_PROMPT_TEMPLATE.md** - Standardized report generation template
- **Analysis-Architect-project-plan.md** - Original project planning document
- **PORTFOLIO_QUICKSTART.md** - Portfolio management guide
- **PORTFOLIO_REQUIREMENTS.md** - Portfolio specifications
- **PROJECT_CLOSEOUT_TEMPLATE.md** - Project close-out workflow and schema
- Example projects contain domain-specific documentation for spatial biology workflows
