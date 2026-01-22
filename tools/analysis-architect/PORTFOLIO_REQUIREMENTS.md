# Portfolio Dashboard Requirements

## Vision Statement

Move from analyst-per-project model to task-based workflow where:
- Analysts can easily switch between well-defined, modular tasks across projects
- Tasks are clearly defined with explicit inputs/outputs
- Work can be handed off to analysts OR automated agents
- PMs can quickly identify blockers and critical path items
- Portfolio health is visible at a glance

## Core Use Cases

### Use Case 1: Tuesday Morning Standup (Primary)
> "It's Tuesday morning. I want to see all outstanding projects, identify what's being worked on, what's due soon, what's behind, and what I can do to unblock analysts TODAY."

**Required Views:**
- All active projects with current status
- Next immediate task per project with deadline
- Behind-schedule items flagged clearly
- Analyst assignments and capacity

### Use Case 2: Resource Allocation
> "I have 3-5 concurrent analysts. Who's overloaded? Who has capacity? Can I reassign work?"

**Required Views:**
- Analyst workload (hours allocated vs. available)
- Utilization percentages
- Ability to see all work assigned to each analyst

### Use Case 3: Batch Processing Identification
> "GPU segmentation needs to happen across 3 projects for 4 clients. Let me identify and schedule batch runs."

**Required Views:**
- Component type grouping (all segmentation, all thresholding, etc.)
- Filter by platform/method to find batchable tasks
- Schedule/assign batch operations

### Use Case 4: Portfolio Health Monitoring
> "Are we on track across all projects? Where are the red flags?"

**Required Views:**
- Traffic light summary across portfolio
- Revenue at risk (over-budget projects)
- Deadline tracking

### Use Case 5: Historical Tracking & Forecasting
> "How are we doing over time? Are we getting faster? Are estimates improving?"

**Required Views:**
- Daily snapshot logs
- Velocity trends per analyst
- Estimate accuracy (allocated vs. actual hours)
- Completion forecasts

## Functional Requirements

### FR1: Multi-Project Loading
- Load multiple `project.toml` files dynamically
- Portfolio manifest (`portfolio.toml`) lists active projects
- Each project appears as a tab in UI
- "Portfolio Overview" tab aggregates across all loaded projects

### FR2: Task-Centric View
- Tasks = components with well-defined inputs/outputs
- Display component dependencies clearly
- Show critical path for each project
- Highlight next actionable task per project

### FR3: Filtering & Grouping
**Filter by:**
- PM (project manager)
- Analyst (assigned_to)
- Priority (high/medium/low)
- Deadline (overdue, this week, next week, future)
- Component type (segmentation, classification, alignment, spatial analysis, etc.)
- Status (not_started, in_progress, completed, blocked)
- Platform (IMC, CyCIF, CODEX, Visium, etc.)

**Group by:**
- Project
- Analyst
- Component type
- Timeline (this week, next week, etc.)

### FR4: Batch Identification
- Auto-detect batchable tasks based on:
  - Same component type
  - Same platform
  - Same status (e.g., all `not_started`)
  - Assigned to same analyst (optional)
- Display batch candidates with "⚡ Batchable" indicator
- Batch actions: assign all, schedule all, mark as in-progress

### FR5: Critical Path Analysis
- For each project, identify:
  - Next immediate task
  - Tasks blocking others (dependency analysis)
  - Tasks on critical path to client deadline
- Highlight these prominently

### FR6: Analyst Dashboard
- Show all work assigned to specific analyst
- Hours allocated vs. capacity
- Utilization percentage
- Traffic light status per assigned component

### FR7: Historical Logging
- Daily snapshot of portfolio state
- Log format: `logs/portfolio_YYYY-MM-DD.json`
- Capture:
  - Project statuses
  - Component progress
  - Analyst utilization
  - Traffic light counts
- Enable trend analysis over time

### FR8: Forecasting
- Estimate project completion dates based on:
  - Remaining hours
  - Analyst velocity (hours/day from historical data)
  - 3:1 hours-to-days conversion
- Flag projects at risk of missing deadlines

## Data Model Extensions

### portfolio.toml (New File)
```toml
# Portfolio Manifest
portfolio_name = "Astraea Active Projects"
last_updated = "2025-12-22"

# List of active projects to track
[[projects]]
path = "projects/mayo_liver/project.toml"
active = true

[[projects]]
path = "projects/cellsighter/project.toml"
active = true

[[projects]]
path = "projects/7hills/project.toml"
active = false  # Completed, keep for historical data

# Analyst capacity (hours per day available)
[analyst_capacity]
Sharon = 6.0
Tom = 4.0
Alex = 8.0

# Logging configuration
[logging]
enabled = true
daily_snapshot = true
log_directory = "logs/"
```

### project.toml Extensions (Optional)
Add to existing schema if needed:

```toml
# Add to existing project.toml
[portfolio_metadata]
portfolio_priority = "high"  # high | medium | low
revenue_at_risk_usd = 0  # Calculated if over budget
last_activity_date = "2025-12-22"
estimated_completion = "2025-01-15"  # Forecasted based on velocity
```

### Daily Snapshot Log Format
```json
{
  "date": "2025-12-22",
  "portfolio_summary": {
    "total_projects": 8,
    "active_projects": 6,
    "projects_on_track": 4,
    "projects_caution": 1,
    "projects_flagged": 1,
    "total_components": 45,
    "completed": 12,
    "in_progress": 18,
    "not_started": 13,
    "blocked": 2
  },
  "analyst_utilization": {
    "Sharon": {"hours_used": 33, "hours_allocated": 53, "utilization": 0.62},
    "Tom": {"hours_used": 18, "hours_allocated": 24, "utilization": 0.75}
  },
  "projects": [
    {
      "project_id": "SOW-PAI-MYM-121",
      "status": "in_progress",
      "progress": 0.45,
      "utilization": 0.62,
      "traffic_light": "yellow",
      "next_task": "thresh-001",
      "days_until_deadline": 12
    }
  ]
}
```

## UI Layout Proposal

### Main UI Structure
```
┌─────────────────────────────────────────────────────────────┐
│ 🔬 Analysis Architect - Portfolio View                      │
├─────────────────────────────────────────────────────────────┤
│ Sidebar:                                                     │
│   📂 Portfolio: Astraea Active Projects                     │
│   ─────────────────────────────────                         │
│   Tabs:                                                      │
│   • 📊 Portfolio Overview ← NEW                             │
│   • 📋 Mayo Liver                                           │
│   • 📋 CellSighter                                          │
│   • 📋 7Hills Melanoma                                      │
│   • 📋 Duke Kidney                                          │
│   • 📋 Stanford Brain                                       │
│   • ➕ Load Project                                         │
│                                                              │
│   Filters: (Apply to Portfolio Overview)                    │
│   ☐ Sharon  ☐ Tom  ☐ Alex                                  │
│   ☐ High Priority  ☐ Overdue                               │
│   ☐ Segmentation  ☐ Thresholding                           │
└─────────────────────────────────────────────────────────────┘

Main Content Area (Portfolio Overview Tab):
┌─────────────────────────────────────────────────────────────┐
│ 📊 Portfolio Overview - 6 Active Projects                   │
│ Last Updated: 2025-12-22 08:30 AM                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ 🚨 Immediate Attention (Overdue or Due Today)               │
│ ───────────────────────────────────────────────────────────│
│ 🔴 Mayo Liver - Thresholding (thresh-001)                  │
│    Assigned: Sharon | Due: TODAY | Blocker: Pathologist    │
│    [View Details] [Reassign] [Update]                       │
│                                                              │
│ 🟡 Duke Kidney - Segmentation (seg-001)                    │
│    Assigned: Tom | Due: Tomorrow | 85% time used           │
│    [View Details] [Add Hours]                               │
│                                                              │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                              │
│ 📈 Portfolio Health                                         │
│ ───────────────────────────────────────────────────────────│
│ Projects:  🟢 4  🟡 1  🔴 1                                 │
│ Tasks:     ████████████████░░░░  67% complete (30/45)      │
│ Budget:    $42,000 / $50,000 (84% used)                    │
│                                                              │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                              │
│ 👥 Analyst Workload                                         │
│ ───────────────────────────────────────────────────────────│
│ Sharon    ████████████░░░░  62%  (33h / 53h)  3 projects   │
│ Tom       █████████░░░░░░░  75%  (18h / 24h)  2 projects   │
│ Alex      ████░░░░░░░░░░░░  30%  (12h / 40h)  1 project    │
│           [Rebalance] [Assign Work]                          │
│                                                              │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                              │
│ ⚡ Batch Opportunities                                       │
│ ───────────────────────────────────────────────────────────│
│ Cell Segmentation (IMC) - 3 projects ready                  │
│   • Mayo Liver (47 samples)                                 │
│   • 7Hills Melanoma (30 samples)                            │
│   • Duke Kidney (24 samples)                                │
│   [Schedule Batch Run] [Assign All to Sharon]               │
│                                                              │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                              │
│ 📅 Timeline View                                            │
│ ───────────────────────────────────────────────────────────│
│ Overdue    | This Week  | Next Week  | 2+ Weeks            │
│ 2 tasks 🔴 | 7 tasks    | 4 tasks    | 15 tasks            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Implementation Plan

### Phase 1: Core Portfolio View
1. Create `portfolio.toml` schema and parser
2. Add "Portfolio Overview" tab to existing UI
3. Implement multi-project loading
4. Build basic aggregation views:
   - Project health summary
   - Analyst workload
   - Immediate attention list

### Phase 2: Filtering & Batching
5. Add filter controls (analyst, priority, deadline, type)
6. Implement batch detection logic
7. Create batch action UI

### Phase 3: Historical & Forecasting
8. Implement daily snapshot logging
9. Build historical trend views
10. Add completion forecasting
11. Velocity tracking per analyst

### Phase 4: Advanced Features
12. Critical path analysis
13. Interactive Gantt chart (optional)
14. Slack/email alerts (future)

## Success Metrics

How we'll know this is working:
- **Time to identify blockers**: < 30 seconds on Tuesday morning
- **Analyst utilization visibility**: Real-time view of who's overloaded
- **Batch efficiency**: Identify 3+ batchable tasks per week
- **Forecast accuracy**: Within 20% of actual completion dates after 2 months of data

## Technical Notes

- Use existing `load_project_toml()` function, iterate over multiple files
- Leverage pandas DataFrames for aggregation/filtering
- Cache loaded projects in Streamlit session state
- Incremental rendering: load projects on-demand vs. all at once
