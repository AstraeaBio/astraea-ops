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

1. Extract text from SOW PDF
2. Open `sow_parser_prompt.md` in an editor
3. Copy the prompt and paste SOW text where indicated
4. Send to Claude/GPT-4 to generate project TOML
5. Save output as `[project_folder]/project.toml`
6. Open in web UI to review and adjust

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

Completed tumor-vessel spatial analysis using QuPath + Python notebooks. See project README.md for workflow details. Not actively using Analysis Architect tracker.

### CellSighter Project (251125_CellSighter/)

Deep learning cell classifier project. Has extensive documentation in `.github/copilot-instructions.md` covering the full training/inference pipeline. Not using Analysis Architect tracker.

### Maitra SOW124 (maitra_sow124/)

Multimodal spatial biology project with comprehensive CLAUDE.md. Uses conda environment with complex dependencies. Has example of well-structured project documentation.

## Additional Resources

- **README.md** - User-facing documentation with workflow examples and FAQ
- **Analysis-Architect-project-plan.md** - Original project planning document
- Example projects contain domain-specific documentation for spatial biology workflows
