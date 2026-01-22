# Section to Add to astraea-ops Root README.md

Add this section after your existing content:

---

## 🛠️ Tools

Operational software tools for Astraea Bio team:

### Analysis Architect

Project tracking and planning tool for spatial biology image analysis projects.

**Features:**
- Parse SOWs (Statements of Work) using LLMs to extract project structure
- Track progress on analysis components in real-time via web UI
- Automatic traffic light alerts (🟢🟡🔴) when projects drift off track
- Generate client status summaries automatically
- Maintain canonical library of reusable analysis components

**Quick start:**
```bash
# Install dependencies (from repo root)
pip install -r requirements.txt

# Start the web UI
cd tools/analysis-architect
streamlit run project_tracker_ui.py
```

**Documentation:**
- [Analysis Architect README](tools/analysis-architect/README.md) - Full usage guide
- [Developer Guide](tools/analysis-architect/CLAUDE.md) - Technical documentation
- [Component Library](tools/analysis-architect/components_library.toml) - ~40 standard components

### Future Tools

Planned additions to the tools ecosystem:
- **Portfolio Dashboard** - Cross-project analytics and resource planning
- **SOW Parser API** - Automated SOW text extraction and parsing
- **Timeline Calculator** - Realistic deadline estimation with 3:1 hours-to-days conversion

---

## 📁 Repository Structure

```
astraea-ops/
├── docs/                    # SOPs, KB articles, operational documentation
├── tools/                   # Software tools for operations
│   └── analysis-architect/  # Project tracking tool
├── projects/                # Active project tracking data
├── requirements.txt         # Universal Python dependencies
└── README.md               # This file
```
