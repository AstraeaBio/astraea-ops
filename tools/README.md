# Analysis Architect - Project Tracker v1.0

**Automate project planning and tracking for spatial biology image analysis projects**

---

## 🎯 What This Does

Analysis Architect helps your team:
- ✅ **Parse SOWs faster** - Use LLM to extract project structure from PDF SOWs
- ✅ **Track progress in real-time** - Simple web UI for analysts to update status
- ✅ **Flag delays early** - Traffic light system (🟢🟡🔴) alerts when projects drift
- ✅ **Generate client updates** - Auto-generate status summaries for client comms
- ✅ **Learn from history** - Canonical component library improves time estimates

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd analysis-architect
pip install -r requirements.txt
```

### 2. Start the Web UI

```bash
streamlit run project_tracker_ui.py
```

The UI will open in your browser at `http://localhost:8501`

### 3. Create Your First Project

**Option A: Parse an existing SOW**
1. Extract text from your SOW PDF
2. Open `sow_parser_prompt.md` and follow instructions
3. Paste SOW text into Claude/GPT-4
4. Save the generated TOML as `your_project/project.toml`
5. Open in the web UI and review/edit components

**Option B: Start from example template**
1. Copy `example_project.toml` to `your_project/project.toml`
2. Edit project details manually
3. Open in the web UI

---

## 📁 Project Structure

```
analysis-architect/
├── components_library.toml       # Canonical library of ~40 analysis components
├── project_tracker_ui.py         # Streamlit web UI for tracking
├── sow_parser_prompt.md          # LLM prompt for SOW parsing
├── example_project.toml          # Template for new projects
├── requirements.txt              # Python dependencies
├── LICENSE                       # MIT License
├── .gitignore                    # Git ignore rules
└── README.md                     # This file

your_projects/
├── mayo_liver/
│   ├── project.toml              # Project tracker file
│   ├── sow/
│   │   └── sow_v1.pdf            # Original SOW
│   └── scripts/
│       └── 1_preprocess.ipynb
└── 7hills_melanoma/
    └── project.toml
```

---

## 📋 Workflow

### **PM: Creating a New Project**

1. **Receive finalized SOW** from client
2. **Extract SOW text** (copy-paste from PDF or use OCR)
3. **Use LLM to parse**:
   - Open `sow_parser_prompt.md`
   - Follow instructions to paste SOW text into Claude/GPT-4
   - Copy generated TOML
4. **Save as** `projects/[client_name]/project.toml`
5. **Review with analyst**: Open in web UI, verify components and time estimates
6. **Approve and lock**: Set `status: "in_progress"` when data arrives

### **Analyst: Updating Progress**

1. **Open web UI**: `streamlit run project_tracker_ui.py`
2. **Select your project** from sidebar
3. **Go to "Update Components" tab**
4. **For each component you worked on**:
   - Update `Status` (not_started → in_progress → completed)
   - Update `Time Used (hours)`
   - Update `Progress (%)`
   - Add `Notes` about any blockers or decisions
5. **Click "Save Changes"**
6. **Check "Overview" tab** for traffic light status:
   - 🟢 Good: On track
   - 🟡 Caution: Time running high or progress slow
   - 🔴 Flag: Over budget or behind schedule

### **PM: Client Communications**

1. **Open web UI** and select project
2. **Go to "Client Summary" tab**
3. **Review generated markdown summary**
4. **Copy and paste into email/Slack** or download as file
5. **Client sees**:
   - Completed milestones ✅
   - In-progress components with % complete
   - Upcoming deliverables and dates
   - No internal details (hours, blockers stay private)

---

## 🎨 Components Library

The `components_library.toml` file contains ~40 canonical analysis components organized by phase:

1. **Data Ingestion & QC** (5 components)
2. **Segmentation** (6 components)
3. **Feature Extraction & Classification** (7 components)
4. **Analysis & Visualization** (10 components)
5. **Multimodal Integration** (3 components)
6. **Reporting** (3 components)
7. **Special/Custom** (2+ components)

Each component includes:
- Typical time ranges (method dev + compute hours)
- Software dependencies
- Input/output types
- Usage notes

**When creating a new project**, the LLM parser will:
1. Match SOW deliverables to library components
2. Suggest component IDs and names
3. Estimate hours based on typical ranges
4. Flag items that need custom components

**Over time**, add new components to the library as you develop new methods.

---

## 🚦 Traffic Light System

Components are automatically flagged based on:

- **🟢 Green (Good)**:
  - Time used < 70% of allocated
  - Progress > 50%

- **🟡 Yellow (Caution)**:
  - Time used ≈ 90% of allocated OR
  - Progress lagging behind time spent

- **🔴 Red (Flag)**:
  - Time used > allocated OR
  - Low progress with deadline approaching OR
  - Component marked as "blocked"

This helps PMs spot issues early and adjust:
- Reallocate analyst time
- Request change order from client
- Escalate blockers (e.g., pathologist review delays)

---

## 📝 SOW Parsing Tips

The LLM parser works best when you:

1. **Extract clean text** from SOW (not scanned images)
2. **Include the full SOW** (all sections: scope, deliverables, costs, timelines)
3. **Review and edit** the generated TOML:
   - LLM might misinterpret vague deliverables
   - Adjust time estimates based on your team's actual speed
   - Add dependencies between components
4. **Add analyst-specific notes** after parsing:
   - "Use StarDist model trained on kidney tissue"
   - "Client prefers heatmaps over scatter plots"
   - "Pathologist available Tuesdays only"

---

## 🔧 Customization

### Add New Components to Library

Edit `components_library.toml` and add under the appropriate phase:

```toml
[[phase_X_your_phase]]
component_id = "your-component-id"
name = "Your Component Name"
description = "What this component does"
typical_method_dev_hours = [2.0, 4.0]
typical_compute_hours = [3.0, 6.0]
software_dependencies = ["tool1", "tool2"]
notes = "Any special considerations"
```

### Modify Traffic Light Thresholds

Edit `project_tracker_ui.py`, function `calculate_status()`:

```python
def calculate_status(time_used, sow_allocated, progress_fraction):
    utilization = time_used / sow_allocated

    # Adjust these thresholds:
    if utilization < 0.7 and progress_fraction > 0.5:
        return "🟢 Good"
    elif utilization > 1.0 or (progress_fraction < 0.3 and utilization > 0.6):
        return "🔴 Flag"
    else:
        return "🟡 Caution"
```

### Add Custom Fields to Project TOML

You can extend the schema. For example, to track compute resources:

```toml
[[components]]
component_id = "seg-001"
name = "Cell Segmentation"
# ... existing fields ...

[components.compute_resources]
gpu_hours = 8.5
cpu_cores = 16
memory_gb = 64
```

Just add corresponding fields in the web UI (`project_tracker_ui.py`).

---

## ❓ FAQ

**Q: Do I need to use the web UI or can I edit TOML files directly?**

A: Both! The web UI is easier for non-technical analysts, but you can edit `project.toml` files directly in any text editor. TOML is more forgiving than YAML (no indentation errors!). The UI just reads/writes TOML.

---

**Q: Can I track multiple projects at once?**

A: Yes! The web UI sidebar shows all `project.toml` files in your projects directory. Switch between projects with the dropdown.

---

**Q: What if a component doesn't match the library?**

A: Create a custom component! In the web UI's "Add Component" tab, uncheck "Select from Component Library" and fill in custom details. Or ask the LLM to suggest a new component when parsing the SOW.

---

**Q: How do I handle change orders?**

A:
1. Update SOW PDF and save as `sow_v2.pdf`
2. Add entry to `project.toml` under `[[change_orders]]`
3. Add/edit components as needed
4. Update `sow.version` to 2

---

**Q: Can I export data for reporting?**

A: Yes! In the web UI sidebar, click "📊 Export to CSV" to download all components as a spreadsheet.

---

**Q: Does this integrate with Jira/Notion/etc?**

A: Not yet in v1. But since everything is TOML, you can write scripts to sync with other tools. Or just use this as your single source of truth.

---

## 🛠️ Troubleshooting

**Web UI won't start:**
```bash
# Check if streamlit is installed
streamlit --version

# Reinstall if needed
pip install --upgrade streamlit
```

**No projects showing in sidebar:**
- Make sure your `project.toml` files are in subdirectories (not root)
- Check TOML syntax with: `python -c "import tomli; tomli.load(open('project.toml', 'rb'))"`

**LLM parser producing bad output:**
- Check that SOW text is clean (no OCR artifacts)
- Try breaking SOW into sections and parsing separately
- Manually review and edit the generated TOML

---

## 📚 Next Steps

### For v1:
1. ✅ Parse your first 3 SOWs and create project.toml files
2. ✅ Train analysts to use the web UI for daily updates
3. ✅ Customize component library based on your specific workflows
4. ✅ Generate client summaries weekly

### For v2 (Future):
- [ ] Auto-parse SOW PDFs (OCR + LLM in one step)
- [ ] Slack/email notifications when components turn 🔴
- [ ] Historical time tracking (learn typical hours per tissue type)
- [ ] Integration with git commits (auto-update component status from pushes)
- [ ] Vector embeddings for smarter SOW→component matching

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

Copyright (c) 2025 Astraea

---

## 👥 Support

Questions? Contact:
- **Architecture**: Trevor McKee
- **PM Workflow**: Trang Vu
- **Analyst Feedback**: Sharon (CellSighter), team members

---

**Happy tracking! 🚀**
