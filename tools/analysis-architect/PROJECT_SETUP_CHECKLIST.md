# Project Setup Checklist

## Before Starting: Ensure These Required Fields Are Present

The Analysis Architect UI **requires** specific fields in `project.toml` files to function without errors. Use this checklist when creating new projects from SOWs.

---

## ✅ Required Fields Checklist

### 1. Project Metadata (Top-Level)
- [ ] `project_id` - Unique identifier (e.g., "SOW-XXX-YYY-NNN")
- [ ] `project_name` - Descriptive title
- [ ] `client` - Client organization and contact
- [ ] `pm` - Project manager name
- [ ] `analyst_primary` - Lead analyst name
- [ ] `status` - One of: "draft", "in_progress", "completed", "on_hold"
- [ ] `estimated_completion` - Date in YYYY-MM-DD format

### 2. SOW Section (`[sow]`)
- [ ] **`total_cost_usd`** - Total project cost as a number (CRITICAL)
  - ❌ Wrong: `total_cost_usd = "$30,000"` (string)
  - ✅ Right: `total_cost_usd = 30000` (number)
  - Used for: Hours calculation (cost / 250)
  - If missing: UI displays "N/A" but some calculations may fail

- [ ] **`milestones`** - Array of at least ONE milestone (CRITICAL)
  - Used for: Client summary generation, project status tracking
  - If missing: Client Summary tab will show KeyError

#### Milestone Template
```toml
[[sow.milestones]]
milestone_id = "m1"
name = "Milestone Name"
cost_usd = 15000
status = "not_started"  # or "in_progress", "completed"
estimated_completion = "2025-12-31"
completed_date = ""  # Fill when status = "completed"
```

**Default Milestone** (if SOW has no explicit milestones):
```toml
[[sow.milestones]]
milestone_id = "m1"
name = "Full Project Delivery"
cost_usd = 30000  # Same as sow.total_cost_usd
status = "not_started"
estimated_completion = "2025-12-31"  # Same as project estimated_completion
```

### 3. Components (`[[components]]`)
- [ ] At least ONE component defined
- [ ] Each component has:
  - `component_id` - Unique identifier
  - `name` - Display name
  - `status` - "not_started", "in_progress", "completed", or "blocked"
  - `assigned_to` - Analyst name
  - `sow_allocated_hours` - Total hours from SOW
  - `time_used_hours` - Hours spent (start at 0.0)
  - `progress_fraction` - 0.0 to 1.0

---

## 🚨 Common Errors and Fixes

### Error: `KeyError: 'total_cost_usd'`
**Cause:** Missing `sow.total_cost_usd` field

**Fix:**
```toml
[sow]
total_cost_usd = 30000  # Add this line
```

### Error: `KeyError: 'milestones'`
**Cause:** Missing `[[sow.milestones]]` array

**Fix:** Add at least one milestone using the template above.

### Error: `KeyError: 'estimated_completion'`
**Cause:** Missing top-level `estimated_completion` field

**Fix:**
```toml
estimated_completion = "2025-12-31"  # Add at top level
```

---

## 📋 Validation in UI

The UI includes automatic validation in the sidebar:

✅ **All required fields present** - Green checkmark, ready to use

⚠️ **Issues found** - Yellow warning with list of missing/invalid fields:
- ❌ Critical missing fields (project_id, components)
- ⚠️ Important missing fields (total_cost_usd, milestones)

**Tip:** See validation status immediately after loading a project in the sidebar.

---

## 🛠️ Workflow: Creating a New Project

### Step 1: Parse SOW with LLM
1. Extract SOW text from PDF
2. Open `sow_parser_prompt.md`
3. Copy prompt and paste SOW text
4. Send to Claude/GPT-4
5. Review output for required fields (see "CRITICAL REQUIREMENTS" section in prompt)

### Step 2: Save and Validate
1. Save LLM output as `[project_folder]/project.toml`
2. Open in Streamlit UI: `streamlit run project_tracker_ui.py`
3. Check **Validation** section in sidebar
4. Fix any missing fields

### Step 3: Review Components
1. Navigate to "Overview" tab
2. Verify components match SOW deliverables
3. Check time allocations are reasonable
4. Adjust priorities and dependencies as needed

### Step 4: Set Status
```toml
status = "draft"  # Initial state
# Change to "in_progress" when data arrives
# Change to "completed" when all components done
```

---

## 📝 Example: Minimal Valid Project

```toml
project_id = "TEST-001"
project_name = "Test Project"
client = "Test Client"
pm = "John Doe"
analyst_primary = "Jane Smith"
start_date = "2025-01-01"
estimated_completion = "2025-12-31"
status = "draft"

[sow]
version = 1
total_cost_usd = 15000

[[sow.milestones]]
milestone_id = "m1"
name = "Complete Analysis"
cost_usd = 15000
status = "not_started"
estimated_completion = "2025-12-31"

[data]
platform = "Imaging Mass Cytometry"
n_samples = 10
n_rois = 20
markers = 40

[[components]]
component_id = "seg-001"
name = "Cell Segmentation"
status = "not_started"
assigned_to = "Jane Smith"
method_dev_hours = 5.0
compute_hours = 10.0
sow_allocated_hours = 15.0
time_used_hours = 0.0
progress_fraction = 0.0
priority = "high"
dependencies = []
notes = ""

[timeline]
client_deadline = "2025-12-31"
internal_deadline = "2025-12-24"
buffer_days = 7
```

This minimal example includes all required fields and will load without errors.

---

## 🔗 Related Documentation

- **sow_parser_prompt.md** - LLM prompt with CRITICAL REQUIREMENTS section
- **example_project.toml** - Full schema example with all optional fields
- **CLAUDE.md** - Detailed architecture and customization guide
- **README.md** - User-facing quickstart and FAQ

---

**Version:** 1.2 (Updated with validation requirements)
