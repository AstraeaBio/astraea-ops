# Portfolio Dashboard - Quick Start Guide

## What We've Built

You now have a **Portfolio Overview** feature integrated into Analysis Architect that enables:

1. **Multi-project visibility** - See all projects in one view
2. **Tuesday Morning Standup view** - Immediate attention items highlighted
3. **Analyst workload tracking** - Who's overloaded, who has capacity
4. **Batch opportunity detection** - Find similar tasks to batch together
5. **Timeline overview** - What's overdue, due this week, next week
6. **Historical logging** - Daily snapshots for trend analysis

## Quick Start

### Step 1: Create a Portfolio File

Create a `portfolio.toml` file that lists your active projects:

```toml
portfolio_name = "Astraea Active Projects"
portfolio_id = "main"

[[projects]]
path = "project.toml"  # Path to project file (relative or absolute)
active = true

[[projects]]
path = "../../projects/mayo_liver/project.toml"
active = true

[[projects]]
path = "../../projects/cellsighter/project.toml"
active = true

[analyst_capacity]
Sharon = 6.0
Tom = 4.0
Alex = 8.0

[batching]
enabled = true
min_batch_size = 2
batchable_components = [
    "cell-segmentation-stardist",
    "marker-thresholding"
]
```

See `example_portfolio.toml` for a complete template.

### Step 2: Launch the UI

```bash
streamlit run project_tracker_ui.py
```

### Step 3: Load Portfolio

In the sidebar:
1. Enter the path to your `portfolio.toml` file in **"Portfolio File"** field
2. The UI will load all projects and show "✅ Portfolio: [name]"
3. Click the **"🌐 Portfolio Overview"** tab

## Portfolio Overview Features

### 📈 Portfolio Health
- Active projects count
- Total tasks across all projects
- Completion percentage
- Blocked items count

### 🚨 Immediate Attention
Shows items needing action TODAY:
- **Blocked tasks** - Items waiting on external dependencies
- **High utilization** - Tasks using >85% of allocated hours
- **Overdue items** - Past their deadline

Perfect for your **Tuesday Morning Standup**!

### 👥 Analyst Workload
For each analyst:
- Hours used vs. allocated across ALL projects
- Utilization percentage with progress bar
- Number of projects they're working on
- Status indicator:
  - ➕ Capacity (< 50%)
  - ✓ Good (50-85%)
  - ⚠️ High (> 85%)

### ⚡ Batch Opportunities
Auto-detects tasks that can be batched:
- Groups by component type + platform + status
- Shows all matching tasks across projects
- Configurable in `portfolio.toml`

**Example:** "3 IMC segmentation tasks ready to run"

### 📅 Timeline Overview
Projects grouped by deadline:
- Overdue (🔴)
- This Week (🟡)
- Next Week (🟢)
- 2+ Weeks

## Daily Snapshot Logging

Create historical logs to track portfolio health over time:

```python
import portfolio_lib

# Load portfolio
portfolio_data = portfolio_lib.load_portfolio('portfolio.toml')

# Create daily snapshot (saves to logs/portfolio_YYYY-MM-DD.json)
snapshot = portfolio_lib.create_daily_snapshot(portfolio_data)
```

**Automated Option:** Add to cron/scheduled task:
```bash
# Run daily at 9 AM
0 9 * * * cd /path/to/analysis-architect && python -c "import portfolio_lib; portfolio_lib.create_daily_snapshot(portfolio_lib.load_portfolio('portfolio.toml'))"
```

## Advanced: Shared Portfolio Library

The `portfolio_lib.py` module provides reusable functions:

```python
import portfolio_lib

# Load portfolio
portfolio_data = portfolio_lib.load_portfolio('portfolio.toml')

# Get next actionable task per project
for project in portfolio_data['projects']:
    next_task = portfolio_lib.get_next_task(project)
    if next_task:
        print(f"{project['project_name']}: {next_task['name']}")

# Find batch candidates
batches = portfolio_lib.detect_batch_candidates(portfolio_data)
for batch in batches:
    print(f"Batch: {batch['batch_key']} ({batch['count']} tasks)")

# Calculate analyst workload
workload = portfolio_lib.calculate_analyst_workload(portfolio_data)
for analyst, data in workload.items():
    print(f"{analyst}: {data['utilization']*100:.0f}% utilized")

# Get immediate attention items
attention = portfolio_lib.get_immediate_attention_items(portfolio_data)
for item in attention:
    print(f"{item['urgency']}: {item['project_name']} - {item['component']['name']}")
```

## Configuration Options

### Portfolio Manifest (`portfolio.toml`)

**Required fields:**
- `portfolio_name` - Display name
- `[[projects]]` - List of projects with `path` and `active` fields

**Optional fields:**
- `[analyst_capacity]` - Hours per day for each analyst
- `[time_settings]` - Hours/day conversion (default: 3.0)
- `[logging]` - Snapshot logging configuration
- `[batching]` - Batch detection settings

### Batch Detection Settings

```toml
[batching]
enabled = true
min_batch_size = 2  # Minimum tasks to suggest batching
same_platform_required = true  # Must be same platform (IMC, CyCIF, etc.)
same_component_type_required = true  # Must be same type (segmentation, etc.)
same_status_required = true  # Must be same status (not_started, in_progress)

batchable_components = [
    "cell-segmentation-stardist",
    "cell-segmentation-mesmer",
    "marker-thresholding",
    "spatial-feature-distance"
]
```

## Workflow Example: Tuesday Morning

1. **Launch UI** with your `portfolio.toml` loaded
2. **Go to Portfolio Overview tab**
3. **Check "Immediate Attention"** section:
   - Any blocked items? → Unblock them
   - Any overdue items? → Prioritize today
   - Any high utilization items? → Add hours or reassign
4. **Review Analyst Workload**:
   - Anyone over 85%? → Reallocate or extend deadline
   - Anyone under 50%? → Assign new work
5. **Check Batch Opportunities**:
   - Schedule GPU segmentation runs
   - Schedule pathologist review sessions
6. **Review Timeline**:
   - Projects due this week → Ensure on track
   - Overdue projects → Create action plan

**Time: < 5 minutes to get full portfolio visibility!**

## Next Steps

### Standalone Dashboard (Coming Soon)
A separate `portfolio_dashboard.py` for portfolio-only view without individual project tabs.

### Filtering & Search
Add filters by analyst, priority, component type, platform.

### Batch Actions
Implement actual batch assignment (currently shows "Coming soon" placeholder).

### Historical Trends
Visualize velocity, estimate accuracy, completion forecasts from daily logs.

## Troubleshooting

**"No portfolio found"**
- Check the path to `portfolio.toml` is correct
- Ensure file exists and has correct TOML syntax

**"Error loading portfolio"**
- Check that all project paths in `portfolio.toml` are valid
- Ensure all `project.toml` files have correct TOML syntax
- Use absolute paths if relative paths aren't resolving

**"No projects showing"**
- Check that projects have `active = true` in portfolio manifest
- Verify project files actually exist at specified paths

**Portfolio tab not appearing**
- Make sure you've entered a valid portfolio file path in sidebar
- The tab only appears when a portfolio is successfully loaded

## Files Reference

- `portfolio.toml` - Your portfolio configuration
- `example_portfolio.toml` - Template for creating portfolios
- `portfolio_lib.py` - Shared library functions
- `project_tracker_ui.py` - Main UI (now with Portfolio tab)
- `logs/portfolio_YYYY-MM-DD.json` - Daily snapshots

---

**Questions? See PORTFOLIO_REQUIREMENTS.md for detailed specifications.**
