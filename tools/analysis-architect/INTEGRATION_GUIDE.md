# Integration Guide: Analysis Architect → astraea-ops

This guide explains how to integrate Analysis Architect into the astraea-ops repository.

## Recommended Structure

```
astraea-ops/
├── docs/                           # Existing SOPs and KB articles
├── tools/                          # Operational software tools
│   └── analysis-architect/         # This tool
│       ├── project_tracker_ui.py
│       ├── components_library.toml
│       ├── example_project.toml
│       ├── CLAUDE.md
│       ├── DEVELOPMENT_LOG.md
│       └── README.md               # Tool-specific readme
├── projects/                       # Live project tracking (optional)
│   ├── example_project/
│   │   └── project.toml
│   └── README.md
├── requirements.txt                # Universal Python dependencies
├── .gitignore                      # Root-level ignore rules
└── README.md                       # Main repo readme (update this)
```

## Files to Add/Update

### 1. Root `requirements.txt` (NEW)

Create at repository root:

```txt
# astraea-ops - Universal Python Requirements
# Install with: pip install -r requirements.txt

# Analysis Architect dependencies
streamlit>=1.28.0
tomli>=2.0.0  # TOML reading (Python 3.11+ has built-in tomllib)
tomli-w>=1.0.0  # TOML writing
pandas>=2.0.0

# Add other tool dependencies here as you build more tools
```

### 2. Root `.gitignore` (UPDATE)

Add to existing `.gitignore` or create if it doesn't exist:

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
*.egg-info/
.Python
build/
dist/
venv/
env/
.venv/
*.pyc

# Virtual environments (any location)
**/venv/
**/env/
**/.venv/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# Streamlit
.streamlit/
**/.streamlit/

# Claude Code
.claude/
**/.claude/

# OS-specific
.DS_Store
Thumbs.db
desktop.ini
*.lnk

# Logs
*.log

# Temporary files
*.tmp
*.bak

# Optional: Exclude project data if sensitive
# Uncomment if projects/ contains client data:
# projects/*/
# !projects/README.md
# !projects/example_project/
```

### 3. Root `README.md` (UPDATE)

Add this section to your existing README:

```markdown
## 🛠️ Tools

Operational software tools for Astraea Bio:

### Analysis Architect

Project tracking and planning tool for spatial biology image analysis projects.

**Quick start:**
```bash
# Install dependencies
pip install -r requirements.txt

# Start the UI
cd tools/analysis-architect
streamlit run project_tracker_ui.py
```

See [tools/analysis-architect/README.md](tools/analysis-architect/README.md) for full documentation.

### Future Tools
- Portfolio Dashboard (coming soon)
- SOW Parser API (coming soon)
```

### 4. `projects/README.md` (NEW)

Create this file to document the projects directory:

```markdown
# Active Projects

This directory contains live project tracking files for ongoing spatial biology analysis projects.

## Structure

Each project should have its own subdirectory:

```
projects/
├── mayo_liver_rejection/
│   ├── project.toml              # Project tracker file
│   ├── scripts/                  # Analysis code
│   │   ├── 1_preprocess.py
│   │   └── 2_segment.py
│   ├── sow/                      # Statement of Work documents
│   │   └── sow_v1.pdf
│   └── README.md                 # Project-specific notes
└── cellsighter_melanoma/
    └── project.toml
```

## Usage

Projects are managed via [Analysis Architect](../tools/analysis-architect/):

1. **Create project**: Parse SOW using the tool's prompt template
2. **Track progress**: Update component status via Streamlit UI
3. **Generate updates**: Create client summaries from tracked data

## Best Practices

- Use descriptive project folder names (e.g., `mayo_liver_rejection`, not `project1`)
- Keep `project.toml` files up to date weekly
- Store analysis scripts in `scripts/` subdirectory
- Archive completed projects to separate storage after delivery

## Template

Copy `example_project/` to start a new project:

```bash
cp -r example_project/ your_project_name/
cd your_project_name/
# Edit project.toml with your project details
```
```

### 5. `tools/analysis-architect/README.md` (UPDATE)

Update the Quick Start section to reflect the new location:

Change from:
```bash
cd analysis-architect
pip install -r requirements.txt
streamlit run project_tracker_ui.py
```

To:
```bash
# From astraea-ops repository root:
pip install -r requirements.txt

cd tools/analysis-architect
streamlit run project_tracker_ui.py
```

## Migration Checklist

- [ ] Move Analysis Architect to `tools/analysis-architect/`
- [ ] Create root `requirements.txt`
- [ ] Update root `.gitignore`
- [ ] Update root `README.md` to document tools
- [ ] Create `projects/` directory
- [ ] Create `projects/README.md`
- [ ] Update `tools/analysis-architect/README.md` paths
- [ ] Move example projects to `projects/` (or delete if not needed)
- [ ] Delete `tools/analysis-architect/requirements.txt` (using root one now)
- [ ] Test that UI launches from new location
- [ ] Commit and push changes

## Testing After Integration

```bash
# 1. Clone the repo
git clone https://github.com/AstraeaBio/astraea-ops.git
cd astraea-ops

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch Analysis Architect
cd tools/analysis-architect
streamlit run project_tracker_ui.py

# 4. Verify it can find projects in ../../projects/
```

## Notes

- The root `requirements.txt` is now the single source of truth for Python dependencies
- All tools in `tools/` should use this shared requirements file
- Project data in `projects/` can be tracked in git or excluded via `.gitignore` depending on sensitivity
- Each tool in `tools/` should have its own README.md for tool-specific documentation
