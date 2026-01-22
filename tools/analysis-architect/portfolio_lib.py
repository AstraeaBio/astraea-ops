"""
Portfolio Library - Shared Code for Multi-Project Analysis
============================================================

This module provides portfolio management functions used by both:
- project_tracker_ui.py (main UI with Portfolio tab)
- portfolio_dashboard.py (standalone dashboard)

Key Functions:
- load_portfolio() - Load portfolio manifest and all projects
- get_next_task() - Identify next actionable task per project
- detect_batch_candidates() - Find batchable tasks across projects
- calculate_analyst_workload() - Aggregate workload per analyst
- create_daily_snapshot() - Log portfolio state for historical tracking
"""

import sys
from pathlib import Path
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple
import json

# TOML imports - use built-in tomllib for Python 3.11+ reading
if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib
import tomli_w


# ============================================================================
# PORTFOLIO LOADING
# ============================================================================

def load_portfolio(portfolio_path: str) -> Dict:
    """
    Load portfolio manifest and all associated projects.

    Args:
        portfolio_path: Path to portfolio.toml file

    Returns:
        Dictionary with:
        - portfolio_config: Portfolio configuration
        - projects: List of loaded project data
        - load_errors: List of any projects that failed to load
    """
    portfolio_path = Path(portfolio_path)

    if not portfolio_path.exists():
        raise FileNotFoundError(f"Portfolio file not found: {portfolio_path}")

    # Load portfolio manifest
    with open(portfolio_path, 'rb') as f:
        portfolio_config = tomllib.load(f)

    # Load all project files
    projects = []
    load_errors = []

    for proj_entry in portfolio_config.get('projects', []):
        if not proj_entry.get('active', True):
            continue  # Skip inactive projects

        proj_path = proj_entry['path']

        # Resolve relative paths relative to portfolio file location
        if not Path(proj_path).is_absolute():
            proj_path = (portfolio_path.parent / proj_path).resolve()
        else:
            proj_path = Path(proj_path)

        try:
            with open(proj_path, 'rb') as f:
                project_data = tomllib.load(f)
                project_data['_filepath'] = str(proj_path)  # Store path for reference
                project_data['_portfolio_notes'] = proj_entry.get('notes', '')
                projects.append(project_data)
        except Exception as e:
            load_errors.append({
                'path': str(proj_path),
                'error': str(e)
            })

    return {
        'portfolio_config': portfolio_config,
        'projects': projects,
        'load_errors': load_errors
    }


# ============================================================================
# NEXT TASK IDENTIFICATION
# ============================================================================

def get_next_task(project_data: Dict) -> Optional[Dict]:
    """
    Identify the next actionable task for a project.

    Logic:
    - Find all 'not_started' components
    - Filter to those with no unfulfilled dependencies
    - Return the highest priority one, or first one if priorities equal

    Args:
        project_data: Loaded project dictionary

    Returns:
        Component dictionary, or None if no actionable tasks
    """
    components = project_data.get('components', [])

    # Build dependency map
    component_status = {c['component_id']: c['status'] for c in components}

    # Find not_started components with fulfilled dependencies
    actionable = []
    for comp in components:
        if comp['status'] != 'not_started':
            continue

        # Check if all dependencies are completed
        dependencies = comp.get('dependencies', [])
        if all(component_status.get(dep) == 'completed' for dep in dependencies):
            actionable.append(comp)

    if not actionable:
        return None

    # Sort by priority (high > medium > low), then by order in file
    priority_order = {'high': 0, 'medium': 1, 'low': 2}
    actionable.sort(key=lambda c: priority_order.get(c.get('priority', 'medium'), 1))

    return actionable[0]


# ============================================================================
# BATCH DETECTION
# ============================================================================

def detect_batch_candidates(
    portfolio_data: Dict,
    min_batch_size: int = 2,
    same_platform: bool = True,
    same_component_type: bool = True,
    same_status: bool = True,
    batchable_components: Optional[List[str]] = None
) -> List[Dict]:
    """
    Detect tasks across projects that can be batched together.

    Args:
        portfolio_data: Portfolio data from load_portfolio()
        min_batch_size: Minimum number of tasks to suggest batching
        same_platform: Require tasks to be on same platform (IMC, CyCIF, etc.)
        same_component_type: Require tasks to be same component type
        same_status: Require tasks to have same status
        batchable_components: List of component IDs that are batchable

    Returns:
        List of batch candidate groups, each containing:
        - batch_key: Description of batch
        - tasks: List of tasks in batch
        - count: Number of tasks
    """
    projects = portfolio_data['projects']

    # Group tasks by batch key
    batch_groups = {}

    for project in projects:
        platform = project.get('data', {}).get('platform', 'unknown')

        for comp in project.get('components', []):
            # Filter to batchable components
            if batchable_components and comp['component_id'] not in batchable_components:
                continue

            # Build batch key based on grouping criteria
            key_parts = []

            if same_component_type:
                # Use component name or ID as proxy for type
                comp_type = comp.get('name', comp['component_id'])
                key_parts.append(comp_type)

            if same_platform:
                key_parts.append(platform)

            if same_status:
                key_parts.append(comp['status'])

            batch_key = " | ".join(key_parts)

            # Add to batch group
            if batch_key not in batch_groups:
                batch_groups[batch_key] = []

            batch_groups[batch_key].append({
                'project_id': project['project_id'],
                'project_name': project['project_name'],
                'component': comp,
                'platform': platform
            })

    # Filter to groups meeting min_batch_size
    batches = []
    for key, tasks in batch_groups.items():
        if len(tasks) >= min_batch_size:
            batches.append({
                'batch_key': key,
                'tasks': tasks,
                'count': len(tasks)
            })

    # Sort by count descending
    batches.sort(key=lambda b: b['count'], reverse=True)

    return batches


# ============================================================================
# ANALYST WORKLOAD
# ============================================================================

def calculate_analyst_workload(
    portfolio_data: Dict,
    analyst_capacity: Optional[Dict[str, float]] = None
) -> Dict[str, Dict]:
    """
    Calculate workload aggregated by analyst.

    Args:
        portfolio_data: Portfolio data from load_portfolio()
        analyst_capacity: Dict mapping analyst name to hours/day capacity

    Returns:
        Dictionary mapping analyst name to:
        - hours_allocated: Total hours allocated across all projects
        - hours_used: Total hours used
        - utilization: hours_used / hours_allocated
        - capacity_utilization: hours_allocated / (capacity * workdays remaining)
        - tasks: List of assigned tasks
        - projects: Set of project names
    """
    if analyst_capacity is None:
        analyst_capacity = portfolio_data['portfolio_config'].get('analyst_capacity', {})

    analysts = {}

    for project in portfolio_data['projects']:
        for comp in project.get('components', []):
            analyst = comp.get('assigned_to')
            if not analyst:
                continue

            if analyst not in analysts:
                analysts[analyst] = {
                    'hours_allocated': 0,
                    'hours_used': 0,
                    'tasks': [],
                    'projects': set()
                }

            analysts[analyst]['hours_allocated'] += comp.get('sow_allocated_hours', 0)
            analysts[analyst]['hours_used'] += comp.get('time_used_hours', 0)
            analysts[analyst]['tasks'].append({
                'project_id': project['project_id'],
                'project_name': project['project_name'],
                'component_id': comp['component_id'],
                'component_name': comp['name'],
                'status': comp['status'],
                'hours_allocated': comp.get('sow_allocated_hours', 0),
                'hours_used': comp.get('time_used_hours', 0),
                'progress': comp.get('progress_fraction', 0)
            })
            analysts[analyst]['projects'].add(project['project_name'])

    # Calculate utilization
    for analyst, data in analysts.items():
        if data['hours_allocated'] > 0:
            data['utilization'] = data['hours_used'] / data['hours_allocated']
        else:
            data['utilization'] = 0

        # Convert projects set to count
        data['project_count'] = len(data['projects'])
        data['projects'] = list(data['projects'])  # Convert set to list for JSON serialization

        # Add capacity info if available
        if analyst in analyst_capacity:
            data['capacity_hours_per_day'] = analyst_capacity[analyst]

    return analysts


# ============================================================================
# DAILY SNAPSHOT LOGGING
# ============================================================================

def create_daily_snapshot(
    portfolio_data: Dict,
    output_dir: Optional[str] = None
) -> Dict:
    """
    Create a daily snapshot of portfolio state for historical tracking.

    Args:
        portfolio_data: Portfolio data from load_portfolio()
        output_dir: Directory to save log (defaults to portfolio config)

    Returns:
        Snapshot dictionary (also saves to file)
    """
    if output_dir is None:
        output_dir = portfolio_data['portfolio_config'].get('logging', {}).get('log_directory', 'logs/')

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create snapshot
    snapshot_date = date.today().isoformat()

    # Portfolio summary
    projects = portfolio_data['projects']
    total_components = sum(len(p.get('components', [])) for p in projects)

    status_counts = {'completed': 0, 'in_progress': 0, 'not_started': 0, 'blocked': 0}
    for p in projects:
        for c in p.get('components', []):
            status = c.get('status', 'not_started')
            status_counts[status] = status_counts.get(status, 0) + 1

    snapshot = {
        'date': snapshot_date,
        'portfolio_id': portfolio_data['portfolio_config'].get('portfolio_id', 'unknown'),
        'portfolio_name': portfolio_data['portfolio_config'].get('portfolio_name', 'Unknown Portfolio'),
        'portfolio_summary': {
            'total_projects': len(projects),
            'active_projects': len([p for p in projects if p.get('status') != 'completed']),
            'total_components': total_components,
            **status_counts
        },
        'analyst_utilization': {},
        'projects': []
    }

    # Analyst utilization
    analyst_workload = calculate_analyst_workload(portfolio_data)
    for analyst, data in analyst_workload.items():
        snapshot['analyst_utilization'][analyst] = {
            'hours_used': data['hours_used'],
            'hours_allocated': data['hours_allocated'],
            'utilization': data['utilization'],
            'project_count': data['project_count']
        }

    # Project details
    for project in projects:
        components = project.get('components', [])
        completed = sum(1 for c in components if c.get('status') == 'completed')
        total = len(components)
        progress = completed / total if total > 0 else 0

        # Calculate days until deadline
        deadline = project.get('timeline', {}).get('client_deadline')
        days_until_deadline = None
        if deadline:
            try:
                deadline_date = datetime.strptime(deadline, '%Y-%m-%d').date()
                days_until_deadline = (deadline_date - date.today()).days
            except:
                pass

        snapshot['projects'].append({
            'project_id': project['project_id'],
            'project_name': project['project_name'],
            'status': project.get('status', 'unknown'),
            'progress': progress,
            'components_completed': completed,
            'components_total': total,
            'days_until_deadline': days_until_deadline,
            'next_task': get_next_task(project)
        })

    # Save to file
    filename = f"portfolio_{snapshot_date}.json"
    filepath = output_dir / filename

    with open(filepath, 'w') as f:
        json.dump(snapshot, f, indent=2, default=str)

    return snapshot


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_overdue_tasks(portfolio_data: Dict) -> List[Dict]:
    """Get all tasks that are overdue or due today."""
    today = date.today()
    overdue = []

    for project in portfolio_data['projects']:
        deadline = project.get('timeline', {}).get('client_deadline')
        if not deadline:
            continue

        try:
            deadline_date = datetime.strptime(deadline, '%Y-%m-%d').date()
        except:
            continue

        for comp in project.get('components', []):
            if comp['status'] in ['completed', 'blocked']:
                continue

            # Task is overdue if project deadline has passed
            if deadline_date <= today:
                overdue.append({
                    'project_id': project['project_id'],
                    'project_name': project['project_name'],
                    'component': comp,
                    'deadline': deadline,
                    'days_overdue': (today - deadline_date).days
                })

    overdue.sort(key=lambda x: x['days_overdue'], reverse=True)
    return overdue


def get_immediate_attention_items(portfolio_data: Dict) -> List[Dict]:
    """
    Get items requiring immediate attention (overdue, due today, or blocked).
    """
    items = []
    today = date.today()

    for project in portfolio_data['projects']:
        deadline_str = project.get('timeline', {}).get('client_deadline')
        deadline = None
        if deadline_str:
            try:
                deadline = datetime.strptime(deadline_str, '%Y-%m-%d').date()
            except:
                pass

        for comp in project.get('components', []):
            # Skip completed
            if comp['status'] == 'completed':
                continue

            # Blocked items
            if comp['status'] == 'blocked':
                items.append({
                    'type': 'blocked',
                    'project_id': project['project_id'],
                    'project_name': project['project_name'],
                    'component': comp,
                    'deadline': deadline_str,
                    'urgency': 'high'
                })

            # High utilization items
            utilization = 0
            if comp.get('sow_allocated_hours', 0) > 0:
                utilization = comp.get('time_used_hours', 0) / comp['sow_allocated_hours']

            if utilization > 0.85 and comp['status'] == 'in_progress':
                items.append({
                    'type': 'high_utilization',
                    'project_id': project['project_id'],
                    'project_name': project['project_name'],
                    'component': comp,
                    'utilization': utilization,
                    'deadline': deadline_str,
                    'urgency': 'medium' if utilization < 1.0 else 'high'
                })

            # Overdue items
            if deadline and deadline <= today and comp['status'] != 'blocked':
                items.append({
                    'type': 'overdue',
                    'project_id': project['project_id'],
                    'project_name': project['project_name'],
                    'component': comp,
                    'deadline': deadline_str,
                    'days_overdue': (today - deadline).days,
                    'urgency': 'high'
                })

    # Sort by urgency
    urgency_order = {'high': 0, 'medium': 1, 'low': 2}
    items.sort(key=lambda x: urgency_order.get(x.get('urgency', 'low'), 2))

    return items
