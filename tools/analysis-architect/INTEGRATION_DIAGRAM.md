# Analysis Architect Integration Diagram

## Phase 1: Script Tracking & Output Management

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         ANALYSIS ARCHITECT v1.2                         │
│                    Project Tracking & Script Management                 │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                           INPUT: Statement of Work (SOW)                │
│                         (PDF document from client)                      │
└─────────────┬───────────────────────────────────────────────────────────┘
              │
              │ 1. Parse SOW using LLM
              │    (sow_parser_prompt.md)
              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         project.toml GENERATED                          │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │ [project]                                                       │    │
│  │ project_name = "Client Analysis Project"                       │    │
│  │                                                                 │    │
│  │ [[components]]                                                  │    │
│  │ component_id = "seg-001"                                        │    │
│  │ name = "Cell Segmentation"                                      │    │
│  │ status = "not_started" ◄──── Manual updates via UI             │    │
│  │ sow_allocated_hours = 10.0                                      │    │
│  │ [[components.outputs]]                                          │    │
│  │   type = "csv"                                                  │    │
│  │   location = "outputs/cells.csv" ◄──── Phase 1 verifies exist  │    │
│  │                                                                 │    │
│  │ [[code_repository]]  ◄──── NEW in Phase 1                       │    │
│  │ script = "segmentation.py"                                      │    │
│  │ component_ids = ["seg-001"]  ◄──── Links script to component   │    │
│  │ version_status = "latest"                                       │    │
│  └────────────────────────────────────────────────────────────────┘    │
└─────────────┬───────────────────────────────────────────────────────────┘
              │
              │ 2. Analyst works on project
              │
              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    ANALYST WORKSPACE (Scripts & Outputs)                │
│                                                                          │
│  Project Directory:                                                     │
│  ├── project.toml                                                       │
│  ├── scripts/                                                           │
│  │   ├── 01_preprocessing.py        ◄──┐                               │
│  │   ├── 02_segmentation.py          ◄─┤ Phase 1: Auto-discover       │
│  │   ├── 03_analysis.ipynb           ◄─┤ via Script Inventory tab     │
│  │   ├── 04_figures.R                 ◄─┤                              │
│  │   └── old_script.py.old (ignored)  ◄─┘ (filtered as deprecated)    │
│  │                                                                      │
│  └── outputs/                                                           │
│      ├── cells.csv                    ◄──┐                              │
│      ├── features.parquet              ◄─┤ Phase 1: Verify existence   │
│      └── figures/                       ◄─┤ via Output Tracking tab    │
│          ├── Figure_1.png              ◄─┘                              │
│          └── Figure_2.png                                               │
└─────────────┬───────────────────────────────────────────────────────────┘
              │
              │ 3. Use Analysis Architect UI
              │
              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       STREAMLIT WEB UI (6 Tabs)                         │
│                                                                          │
│  ┌──────────────┬──────────────┬──────────────┬──────────────┐         │
│  │ 📊 Overview  │ ✏️ Update    │ 📜 SCRIPT    │ 📊 OUTPUT    │         │
│  │              │  Components  │  INVENTORY   │  TRACKING    │         │
│  │              │              │   [NEW]      │   [NEW]      │         │
│  └──────────────┴──────────────┴──────────────┴──────────────┘         │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ 📜 SCRIPT INVENTORY TAB (Phase 1)                               │   │
│  ├─────────────────────────────────────────────────────────────────┤   │
│  │ 1. Enter scripts directory: /project/scripts                    │   │
│  │ 2. Click "Scan Scripts" ────────┐                               │   │
│  │                                  │                               │   │
│  │ Discovered Scripts (4 found):    │                               │   │
│  │  ✅ 01_preprocessing.py    ──────┼─> Language: python           │   │
│  │     Version: latest              │   Last Modified: 2025-01-20  │   │
│  │     Link to: [seg-001] ◄─────────┼─> Multi-select components    │   │
│  │     [➕ Add to Inventory]        │                               │   │
│  │                                  │                               │   │
│  │  ✅ 02_segmentation.py           │                               │   │
│  │  ✅ 03_analysis.ipynb            └─> Auto-detect version status │   │
│  │  ✅ 04_figures.R                                                 │   │
│  │  ❌ old_script.py.old (deprecated - filtered out)               │   │
│  │                                                                  │   │
│  │ Current Inventory (saved to project.toml):                      │   │
│  │  • 01_preprocessing.py → [seg-001]                              │   │
│  │  • 02_segmentation.py → [seg-001, spatial-001]                  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ 📊 OUTPUT TRACKING TAB (Phase 1)                                │   │
│  ├─────────────────────────────────────────────────────────────────┤   │
│  │ Select Component: [Cell Segmentation (seg-001)]                 │   │
│  │                                                                  │   │
│  │ Output Summary:                                                 │   │
│  │  Total: 3  |  Completed: 2  |  Completion: 67%                 │   │
│  │                                                                  │   │
│  │ Output Files:                                                   │   │
│  │  ✅ outputs/cells.csv          (exists)                         │   │
│  │  ✅ outputs/features.parquet   (exists)                         │   │
│  │  ❌ outputs/summary.xlsx       (missing) ◄── Needs attention!   │   │
│  │                                                                  │   │
│  │ [🔄 Check All Component Outputs] ────────────┐                  │   │
│  │                                               │                  │   │
│  │ All Components Status:                        │                  │   │
│  │  Component          Status      Completion    │                  │   │
│  │  Cell Segmentation  in_progress 67%           │                  │   │
│  │  Spatial Analysis   not_started 0%            │                  │   │
│  │  Visualization      completed   100%          │                  │   │
│  └──────────────────────────────────────────────┴──────────────────┘   │
└─────────────┬───────────────────────────────────────────────────────────┘
              │
              │ 4. Update component status manually
              │
              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    project.toml UPDATED (saved automatically)           │
│                                                                          │
│  [[components]]                                                         │
│  component_id = "seg-001"                                               │
│  status = "completed" ◄────── Updated after outputs verified           │
│  progress_fraction = 1.0                                                │
│                                                                          │
│  [[code_repository]]                                                    │
│  script = "02_segmentation.py"                                          │
│  component_ids = ["seg-001"] ◄────── Traceability: component → script  │
│  version_status = "latest"                                              │
└─────────────┬───────────────────────────────────────────────────────────┘
              │
              │ 5. Generate client reports
              │    (Phase 2: Auto-generation)
              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        CLIENT DELIVERABLES                              │
│                                                                          │
│  📝 Status Report (generated from project.toml):                       │
│     - Completed: Cell Segmentation (100%)                              │
│     - In Progress: Spatial Analysis (67%)                              │
│     - Outputs delivered: cells.csv, features.parquet                   │
│                                                                          │
│  📊 Analysis Report (Phase 2 - future):                                │
│     - Combines script inventory + outputs                              │
│     - Uses ANALYSIS_REPORT_PROMPT_TEMPLATE.md                          │
│     - Generated markdown → Word document                               │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Data Flow Summary

### Phase 1 (Current Implementation)

```
SOW PDF
  ↓ (parse via LLM)
project.toml created
  ↓
Analyst writes scripts → Scripts saved in directory
  ↓
UI: Script Inventory tab
  ↓
  1. Scan directory → Discover scripts
  2. Link to components → Update code_repository section
  3. Save to project.toml
  ↓
Analyst runs scripts → Outputs generated
  ↓
UI: Output Tracking tab
  ↓
  1. Check if expected outputs exist
  2. Calculate completion %
  3. Identify missing outputs
  ↓
UI: Update Components tab
  ↓
  1. Manually update progress_fraction
  2. Change status to "completed"
  3. Save to project.toml
  ↓
UI: Client Summary tab
  ↓
  Generate markdown report for client
```

### Phase 2 (Planned)

```
[Everything from Phase 1]
  ↓
UI: Report Builder tab (new)
  ↓
  1. Auto-generate working reports
  2. Parse script outputs (figures, tables)
  3. Combine with component status
  4. Use ANALYSIS_REPORT_PROMPT_TEMPLATE
  ↓
Export to .md and .docx
  ↓
Client receives comprehensive report
```

---

## Key Integration Points

### 1. SOW → Components (v1.0)
- **Input**: SOW PDF
- **Process**: LLM parsing via `sow_parser_prompt.md`
- **Output**: `project.toml` with components and expected outputs
- **Status**: ✅ Existing feature

### 2. Components → Scripts (v1.2 - Phase 1)
- **Input**: Scripts directory
- **Process**: Auto-scan via `scan_scripts_directory()`
- **Output**: `[[code_repository]]` entries in `project.toml`
- **Status**: ✅ **NEW in Phase 1**

### 3. Scripts → Outputs (v1.2 - Phase 1)
- **Input**: Component output definitions
- **Process**: File existence check via `check_component_outputs()`
- **Output**: Completion percentage and missing file list
- **Status**: ✅ **NEW in Phase 1**

### 4. Outputs → Reports (v1.2 - Phase 2)
- **Input**: Script inventory + output files + component status
- **Process**: Auto-generate markdown using template
- **Output**: Comprehensive analysis report
- **Status**: 🔜 **Planned for Phase 2**

---

## Architecture: Three-Layer System

```
┌─────────────────────────────────────────────────────────────────┐
│                      PRESENTATION LAYER                         │
│                  (Streamlit Web UI - 6 tabs)                    │
│                                                                  │
│  📊 Overview  |  ✏️ Update  |  📜 Scripts  |  📊 Outputs        │
│  📝 Summary   |  ➕ Add     |  [Portfolio] (optional)          │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                       BUSINESS LOGIC LAYER                      │
│                   (Python functions in UI)                      │
│                                                                  │
│  • scan_scripts_directory()      ◄── Phase 1 additions         │
│  • detect_version_status()                                      │
│  • check_component_outputs()                                    │
│  • calculate_status()             ◄── Existing (v1.0)          │
│  • generate_client_summary()                                    │
│  • portfolio_lib functions        ◄── Portfolio (v1.1)         │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                        DATA LAYER                               │
│                    (TOML files on disk)                         │
│                                                                  │
│  project.toml                                                   │
│  ├── [project] metadata                                         │
│  ├── [[components]] ◄── SOW deliverables                        │
│  │   └── [[outputs]] ◄── Expected files (Phase 1 checks)       │
│  ├── [[code_repository]] ◄── NEW in Phase 1                     │
│  └── [closeout] (optional) ◄── Project completion (v1.2)       │
│                                                                  │
│  components_library.toml  ◄── Canonical component definitions  │
│  portfolio.toml           ◄── Multi-project tracking (v1.1)    │
└─────────────────────────────────────────────────────────────────┘
```

---

## Version History & Feature Evolution

```
v1.0 (Initial Release)
├── Core project tracking (components, status, time)
├── Traffic light warnings (utilization monitoring)
├── Client summary generation
└── Component library integration

v1.1 (Portfolio Management)
├── Multi-project portfolio tracking
├── Analyst workload aggregation
├── Batch opportunity detection
├── Next task logic (dependency-based)
└── Daily snapshot logging

v1.2 Phase 1 (Script Tracking) ◄── CURRENT
├── Script discovery & scanning
├── Script-to-component linking
├── Output existence verification
├── Version status detection
└── Script inventory UI

v1.2 Phase 2 (Report Generation) ◄── PLANNED
├── Report builder tab
├── Script output parsing
├── Automatic progress inference
├── Batch script management
└── Execution tracking
```

---

*Diagram created: 2025-01-21*
*Analysis Architect v1.2 (Phase 1)*
