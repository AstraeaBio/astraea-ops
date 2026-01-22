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

## Project Lifecycle

1. **Draft** - SOW received, project structure created
2. **In Progress** - Data received, analysis underway
3. **Completed** - Deliverables sent to client
4. **On Hold** - Waiting for client input or resources
5. **Archived** - Moved to long-term storage (not in this directory)
