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

## Session: "Portfolio Dashboard Implementation" (Dec 22-23, 2025)

### Context
Built multi-project portfolio dashboard to enable task-based workflow, resource allocation, and batch processing across multiple concurrent projects.

### Requirements Captured

#### Vision Statement
Move from analyst-per-project model to modular task-based workflow where:
- Analysts can easily switch between well-defined tasks across projects
- Tasks have explicit inputs/outputs for hand-off to analysts or automated agents
- PMs can quickly identify blockers and critical path items
- Portfolio health is visible at a glance

#### Primary Use Case: Tuesday Morning Standup
PM wants to see in <5 minutes:
- All outstanding projects
- What's being worked on now
- What's due soon / overdue
- What's behind schedule
- What can be done to unblock analysts TODAY

### Decisions Made

#### Architecture
- **Portfolio manifest location**: User-configurable (`portfolio.toml` can be anywhere)
- **Logging location**: Separate `logs/` directory at repo root
- **Implementation approach**: Shared library (`portfolio_lib.py`) used by:
  - Extended `project_tracker_ui.py` (Portfolio Overview tab)
  - Future standalone `portfolio_dashboard.py`

#### Batch Actions
- Mark tasks as assigned
- Log batch operations to file
- Manual external triggering for v1.1
- Full batch assignment actions planned for v1.2

#### Next Task Logic
- **Dependency-based**: Find `not_started` components with fulfilled dependencies
- **Priority sorting**: High > medium > low
- Enables non-sequential, flexible workflow

### Implementation Completed

#### Files Created
- `portfolio_lib.py` - Shared portfolio management library
- `portfolio.toml` - Portfolio manifest example
- `example_portfolio.toml` - Template
- `PORTFOLIO_REQUIREMENTS.md` - Detailed specifications
- `PORTFOLIO_QUICKSTART.md` - User guide

#### Files Updated
- `project_tracker_ui.py` - Added Portfolio Overview tab
- `README.md` - Added portfolio features section
- `CLAUDE.md` - Added portfolio architecture documentation
- `DEVELOPMENT_LOG.md` - This session

#### Core Functions Implemented

**`portfolio_lib.py`:**
- `load_portfolio()` - Load manifest and all projects
- `get_next_task()` - Identify next actionable task (dependency-based)
- `detect_batch_candidates()` - Find batchable tasks across projects
- `calculate_analyst_workload()` - Aggregate workload by analyst
- `create_daily_snapshot()` - Historical logging to JSON
- `get_immediate_attention_items()` - Tuesday morning view
- `get_overdue_tasks()` - Helper for deadline tracking

### Features Delivered

#### Portfolio Overview Tab (in `project_tracker_ui.py`)
1. **Portfolio Health Metrics**
   - Active projects count
   - Total tasks across portfolio
   - Completion percentage
   - Blocked items count

2. **Immediate Attention Section**
   - Blocked tasks (waiting on dependencies)
   - High utilization tasks (>85% hours used)
   - Overdue items (past deadline)
   - Expandable cards with urgency indicators (🔴🟡🟢)

3. **Analyst Workload**
   - Hours used vs. allocated across ALL projects
   - Utilization percentage with progress bars
   - Project count per analyst
   - Capacity indicators (➕ Capacity / ✓ Good / ⚠️ High)

4. **Batch Opportunities**
   - Auto-detect similar tasks across projects
   - Group by component type + platform + status
   - Configurable in `portfolio.toml`
   - Placeholder batch actions (full implementation in v1.2)

5. **Timeline Overview**
   - Projects grouped by deadline: Overdue / This Week / Next Week / 2+ Weeks
   - Quick visual scan of upcoming deliverables

### Configuration Schema

**Portfolio Manifest (`portfolio.toml`):**
```toml
portfolio_name = "Astraea Active Projects"
portfolio_id = "main"

[[projects]]
path = "path/to/project.toml"
active = true

[analyst_capacity]
Sharon = 6.0  # hours/day

[time_settings]
hours_per_day = 3.0

[batching]
enabled = true
min_batch_size = 2
batchable_components = [...]
```

**Daily Snapshot Log (`logs/portfolio_YYYY-MM-DD.json`):**
- Portfolio summary (project counts, component status)
- Analyst utilization (hours used/allocated per analyst)
- Project details (progress, deadlines, next tasks)

### Testing
- ✅ Tested with example project data
- ✅ UI compiles and runs successfully
- ✅ Portfolio tab appears when portfolio.toml loaded
- ✅ All core functions working as expected

### Next Steps (v1.2)

#### Planned Enhancements
- [ ] Filtering in Portfolio View (analyst, priority, component type, platform)
- [ ] Batch assignment actions (mark all as in progress, assign to analyst)
- [ ] Historical trend charts from daily snapshots
- [ ] Completion forecasting based on velocity data
- [ ] Standalone `portfolio_dashboard.py` for portfolio-only view

### Technical Notes

**Key Design Patterns:**
- Shared library pattern for code reuse
- User-configurable portfolios (multiple portfolios supported)
- Dependency-based task identification (not sequential)
- Traffic light status system extended to portfolio level
- JSON logs for historical tracking and trend analysis

**Performance Considerations:**
- Tested with 5-10 concurrent projects
- Load time acceptable for current scale
- Projects loaded on-demand, cached in session state
- Future optimization: pre-aggregate data for faster rendering

**Timeline Conversion:**
- 3:1 hours-to-days ratio (conservative productivity estimate)
- "Time from today" for realistic deadline calculation
- Separate milestones for major phases (Image Receipt, Segmentation, Classification, Spatial Analysis)

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

**Core Application:**
- `project_tracker_ui.py` - Main Streamlit app with Portfolio Overview tab
- `portfolio_lib.py` - Shared portfolio management library
- `components_library.toml` - Canonical component library (~40 components)

**Configuration:**
- `portfolio.toml` / `example_portfolio.toml` - Portfolio manifests
- `example_project.toml` - Project template
- `requirements.txt` - Universal dependencies (TOML libraries)

**Documentation:**
- `CLAUDE.md` - Developer guide with portfolio architecture
- `README.md` - User-facing documentation
- `PORTFOLIO_QUICKSTART.md` - Portfolio user guide
- `PORTFOLIO_REQUIREMENTS.md` - Portfolio specifications
- `DEVELOPMENT_LOG.md` - This file

## Quick Reference: Key Functions

**Project Functions:**
- `load_project_toml(filepath)` - Load project from TOML
- `save_project_toml(filepath, data)` - Save project to TOML
- `calculate_status(component)` - Traffic light logic
- `generate_client_summary(project_data)` - Create client update markdown
- `load_components_library()` - Load component library as flat list

**Portfolio Functions (portfolio_lib.py):**
- `load_portfolio(portfolio_path)` - Load manifest and all projects
- `get_next_task(project_data)` - Identify next actionable task (dependency-based)
- `detect_batch_candidates(portfolio_data)` - Find batchable tasks across projects
- `calculate_analyst_workload(portfolio_data)` - Aggregate workload by analyst
- `get_immediate_attention_items(portfolio_data)` - Tuesday morning standup view
- `create_daily_snapshot(portfolio_data)` - Historical logging to JSON

---

## Session Summary: Key Decisions

**v1.1 Release - Portfolio Dashboard (Dec 22-23, 2025)**

**Architecture:**
- User-configurable portfolio manifests (can track multiple portfolios)
- Shared library pattern (`portfolio_lib.py`) for code reuse
- Portfolio Overview tab integrated into main UI
- Separate `logs/` directory for daily snapshots

**Critical Decisions:**
- **Next task logic**: Dependency-based (not sequential) - enables flexible task assignment
- **Batch detection**: Configurable by component type + platform + status
- **Time conversion**: 3:1 hours-to-days ratio for realistic scheduling
- **Milestones**: Separate major phases (Image Receipt, Segmentation, Classification, Spatial Analysis)
- **Analyst capacity**: Tracked in portfolio.toml (hours/day per analyst)

**Implementation:**
- 5 new files created (portfolio_lib.py, manifests, documentation)
- 4 files updated (project_tracker_ui.py, README, CLAUDE.md, DEVELOPMENT_LOG)
- Tested and working with example data
- Ready for astraea-ops repository integration

**Use Case Delivered:**
PM can see full portfolio status in <5 minutes every Tuesday morning:
- What's blocked/overdue/high utilization across ALL projects
- Which analysts are overloaded vs. have capacity
- What tasks can be batched together (GPU runs, reviews)
- Timeline view of all upcoming deadlines
