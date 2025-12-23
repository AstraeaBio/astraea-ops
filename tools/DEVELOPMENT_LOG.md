# Analysis Architect Development Log

This file tracks key decisions, actions, and progress on the Analysis Architect project to maintain continuity across sessions.

---

## Session: "Identify key questions for Analysis Architect v1" (Dec 2025)

### Context
Review session to identify key questions and considerations for v1 of Analysis Architect before expanding the system.

### Key Questions Identified

#### 1. Core Functionality & User Experience
- **Is the traffic light system working as intended?** Need to validate the threshold logic (utilization/progress ratios) matches real-world needs
- **Is the component library comprehensive enough?** Review whether the ~40 components cover typical spatial biology workflows
- **Are SOW parsing prompts generating accurate YAMLs?** Test with recent SOWs to validate quality
- **Is the web UI intuitive for analysts and PMs?** Need user feedback on the Streamlit interface

#### 2. Data Model & Schema
- **Should we track more granular time logging?** Currently using simple `time_used_hours` - consider date-stamped time entries
- **Are dependency relationships being used effectively?** Confirm if analysts benefit from the dependency tracking
- **Do we need version control for project.yaml files?** Currently relying on git, but no in-app history
- **Should milestones be more structured?** Current SOW milestones may need better linking to components

#### 3. Workflow & Integration
- **How are analysts actually updating progress?** Need to observe if weekly updates via UI is realistic
- **Should client summaries be more automated?** Consider templating or more sophisticated generation
- **Do we need integration with external tools?** Slack notifications, calendar integration, etc.
- **How should change orders be tracked?** Current schema exists but workflow is unclear

#### 4. Technical Debt & Architecture
- **Should we migrate from YAML to database?** Consider scalability, concurrent edits, query performance
- **Is Streamlit the right framework long-term?** Evaluate vs FastAPI + React, Dash, etc.
- **How do we handle concurrent edits?** Multiple users could overwrite each other's changes
- **Should we add authentication/authorization?** Currently assumes single-user or file-system access control

#### 5. Component Library Management
- **How do we keep the library updated?** Process for adding new components discovered in projects
- **Should components have versions?** Track evolution of standard components over time
- **How do we handle project-specific custom components?** Promote them to library vs keep isolated
- **Are the time estimates (`typical_method_dev_hours`) accurate?** Need feedback loop from actual projects

#### 6. Reporting & Analytics
- **What aggregate metrics would be valuable?** Cross-project analysis, analyst utilization, accuracy of estimates
- **Should we track estimate vs actual for learning?** Improve future SOW scoping
- **Do we need alerting for at-risk projects?** Proactive notifications when components go red
- **How should we visualize portfolio status?** Multi-project dashboard for leadership

### Decisions Made

#### Architecture Decisions
- **Keep YAML-based storage for v1**: Simplicity and git-friendliness outweigh database benefits at current scale
- **Retain Streamlit for UI**: Rapid development and sufficient for current user base
- **No authentication in v1**: File system permissions sufficient for current deployment model

#### Schema Decisions
- **Preserve current time tracking model**: Simple `time_used_hours` is working; defer granular logging to v2
- **Keep traffic light thresholds as-is**: No evidence yet that they need adjustment
- **Maintain component library structure**: 7-phase organization is clear and comprehensive

#### Workflow Decisions
- **Manual SOW parsing acceptable for v1**: LLM-assisted via prompt template is working
- **Keep client summary generation simple**: Current markdown generation is sufficient
- **No automatic notifications in v1**: Users check UI when needed

#### Timeline & Milestone Decisions (Critical)
- **Use "time from today" for realistic timelines**: SOW timelines are often out of date; calculate deadlines relative to current date
- **Convert hours to days using 3:1 ratio**: Use 3 hours of work per day as conservative estimate to account for:
  - Inefficiencies and context switching
  - Part-time analyst availability
  - Other project demands
  - Realistic productivity expectations
- **Separate major phases into distinct milestones**: Avoid bunched milestones; each major phase should be its own milestone:
  - Image Receipt (data ingestion)
  - Segmentation (cell/structure segmentation)
  - Classification (phenotyping, cell typing)
  - Spatial Analysis (neighborhood, distance, clustering analyses)
  - Additional phases as needed per project

### Action Items from Session

#### High Priority
- [ ] **Validate traffic light logic with real projects**: Test with 3-5 actual projects to confirm thresholds
- [ ] **User testing with PMs and analysts**: Observe actual usage patterns and pain points
- [ ] **Document SOW parser best practices**: Create guide for PMs on getting good YAML output

#### Medium Priority
- [ ] **Add simple edit conflict detection**: Warn if file modified since load
- [ ] **Create PM onboarding guide**: Step-by-step for creating first project
- [ ] **Review component library completeness**: Check against last 10 SOWs for gaps

#### Low Priority / Future Versions
- [ ] **Explore database migration**: Proof-of-concept with SQLite or PostgreSQL
- [ ] **Investigate concurrent editing**: Evaluate operational transform or optimistic locking
- [ ] **Design portfolio dashboard**: Aggregate view across all projects

### Open Questions for Next Session
1. What analytics/reports would actually get used by leadership?
2. Should we build mobile-friendly views for analysts updating on-the-go?
3. How do we validate that time estimates in library are accurate over time?
4. Is there value in integrating with calendar/scheduling tools?
5. Should we support exporting to other formats (Excel, Jira, etc.)?

### Notes
- Current deployment is single-user or small team with file-system based access
- Main users: PMs (create/monitor projects) and analysts (update progress)
- Spatial biology domain has standardized enough workflows to benefit from component library approach
- Git integration provides implicit version control for project.yaml files

---

## Session: "YAML to TOML Migration" (Dec 22, 2025)

### Context
Migrated all project and configuration files from YAML to TOML format to eliminate indentation errors and improve human editability.

### Decisions Made

#### Format Migration Decision
- **Switch from YAML to TOML**: TOML provides clearer structure, no indentation errors, better for hand-editing
- **Benefits identified**:
  - No indentation errors (explicit key-value pairs with `[sections]`)
  - More readable for humans
  - Industry standard for configuration files
  - Less fragile when hand-editing
- **Acceptable tradeoff**: Slightly more verbose syntax, but worth it for reliability

### Actions Completed
- [x] Updated `requirements.txt` to use `tomli` and `tomli-w` instead of `pyyaml`
- [x] Updated all load/save functions in `project_tracker_ui.py` to use TOML
- [x] Converted `example_project.yaml` → `example_project.toml`
- [x] Converted `components_library.yaml` → `components_library.toml`
- [x] Converted `project.yaml` → `project.toml`
- [x] Updated all documentation (CLAUDE.md, DEVELOPMENT_LOG.md) to reference TOML
- [x] Created `convert_yaml_to_toml.py` utility script for future conversions

### TOML Format Notes
- Array of tables syntax: `[[components]]` instead of YAML `- component_id:`
- Nested sections: `[sow]` and `[[sow.milestones]]`
- More explicit, less prone to copy-paste errors
- Comments use `#` just like YAML

### Next Steps
- [ ] Test UI with converted TOML files
- [ ] Update SOW parser prompt to generate TOML instead of YAML
- [ ] Consider whether to keep old YAML files as backup or remove them

---

## Session History

### Session Template
```
## Session: [Title] ([Date])

### Context
[What was being worked on]

### Key Questions Identified
[Questions raised during session]

### Decisions Made
[Concrete decisions with rationale]

### Action Items from Session
[Tasks identified]

### Open Questions for Next Session
[Unresolved items]

### Notes
[Additional context]
```

---

## Quick Reference: Key Files

- `project_tracker_ui.py` - Main Streamlit app (500+ lines)
- `components_library.toml` - Canonical component library (~40 components)
- `example_project.toml` - Template for project structure
- `sow_parser_prompt.md` - LLM prompt for SOW parsing
- `CLAUDE.md` - Comprehensive developer guide
- `README.md` - User-facing documentation

## Quick Reference: Key Functions

- `load_project_toml(filepath)` - Load project from TOML
- `save_project_toml(filepath, data)` - Save project to TOML
- `calculate_status(component)` - Traffic light logic
- `generate_client_summary(project_data)` - Create client update markdown
- `load_components_library()` - Load component library as flat list
