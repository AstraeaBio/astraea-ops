"""
Analysis Architect - Project Tracker UI
========================================
Simple Streamlit web interface for analysts to update project.toml files

Usage:
    streamlit run project_tracker_ui.py

Requirements:
    pip install streamlit tomli tomli-w pandas

Author: Analysis Architect Team
Version: 1.1 (TOML migration)
"""

import streamlit as st
import sys
import pandas as pd
from pathlib import Path
from datetime import datetime, date
import os

# TOML imports - use built-in tomllib for Python 3.11+ reading
if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib
import tomli_w

# ============================================================================
# CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Analysis Architect - Project Tracker",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def load_project_toml(filepath):
    """Load project TOML file"""
    with open(filepath, 'rb') as f:
        return tomllib.load(f)

def save_project_toml(filepath, data):
    """Save project TOML file"""
    with open(filepath, 'wb') as f:
        tomli_w.dump(data, f)

def calculate_status(time_used, sow_allocated, progress_fraction):
    """Calculate traffic light status"""
    if time_used is None or sow_allocated is None or progress_fraction is None:
        return "⚪ Unknown"

    utilization = time_used / sow_allocated if sow_allocated > 0 else 0

    # Green: low utilization and good progress
    if utilization < 0.7 and progress_fraction > 0.5:
        return "🟢 Good"
    # Red: over-allocated OR low progress near deadline
    elif utilization > 1.0 or (progress_fraction < 0.3 and utilization > 0.6):
        return "🔴 Flag"
    # Yellow: everything else
    else:
        return "🟡 Caution"

def load_components_library():
    """Load the canonical components library"""
    library_path = Path(__file__).parent / "components_library.toml"
    if library_path.exists():
        with open(library_path, 'rb') as f:
            lib = tomllib.load(f)
            # Extract all components into a flat list
            components = []
            for phase_key, phase_components in lib.items():
                if phase_key.startswith('phase_') and isinstance(phase_components, list):
                    components.extend(phase_components)
            return components
    return []

def generate_client_summary(project_data):
    """Generate markdown summary for client"""
    summary = f"""## Project Status: {project_data['project_name']}
**Client**: {project_data['client']}
**Estimated Completion**: {project_data['estimated_completion']}
**Status**: {project_data['status'].upper()}

---

### Milestones

"""
    for milestone in project_data['sow']['milestones']:
        status_icon = "✅" if milestone['status'] == 'completed' else "⏳"
        # Don't show cost in client summary
        summary += f"{status_icon} **{milestone['name']}**\n"
        if milestone['status'] == 'completed':
            summary += f"   - Completed: {milestone.get('completed_date', 'N/A')}\n"
        else:
            summary += f"   - Estimated completion: {milestone.get('estimated_completion', 'TBD')}\n"
        summary += "\n"

    summary += "### Component Status\n\n"

    status_groups = {'completed': [], 'in_progress': [], 'not_started': [], 'blocked': []}

    for comp in project_data['components']:
        status_groups[comp['status']].append(comp)

    if status_groups['in_progress']:
        summary += "**🔄 In Progress:**\n"
        for comp in status_groups['in_progress']:
            progress = comp.get('progress_fraction', 0) * 100
            summary += f"- {comp['name']} ({progress:.0f}% complete)\n"
        summary += "\n"

    if status_groups['blocked']:
        summary += "**🚫 Blocked:**\n"
        for comp in status_groups['blocked']:
            blocker = comp.get('blockers', [{}])[0]
            summary += f"- {comp['name']}: {blocker.get('issue', 'Unknown issue')}\n"
        summary += "\n"

    if status_groups['not_started']:
        summary += f"**⏳ Upcoming:** {len(status_groups['not_started'])} components\n\n"

    if status_groups['completed']:
        summary += f"**✅ Completed:** {len(status_groups['completed'])} components\n\n"

    return summary

# ============================================================================
# SIDEBAR - PROJECT SELECTION
# ============================================================================

st.sidebar.title("🔬 Analysis Architect")
st.sidebar.markdown("### Project Tracker")

# Project directory selector
projects_dir = st.sidebar.text_input(
    "Projects Directory",
    value=str(Path(__file__).parent),
    help="Directory containing project.toml files",
    key="projects_dir_input"
)

# Find all project.toml files
project_files = list(Path(projects_dir).glob("**/project.toml"))

if not project_files:
    st.sidebar.warning("No project.toml files found in directory")
    st.stop()

# Project selector
selected_project_path = st.sidebar.selectbox(
    "Select Project",
    options=project_files,
    format_func=lambda x: x.parent.name
)

# Load selected project
if selected_project_path:
    project_data = load_project_toml(selected_project_path)

    st.sidebar.success(f"Loaded: {project_data['project_name']}")
    st.sidebar.markdown(f"**PM:** {project_data['pm']}")
    st.sidebar.markdown(f"**Analyst:** {project_data['analyst_primary']}")
    st.sidebar.markdown(f"**Status:** {project_data['status']}")

# ============================================================================
# MAIN CONTENT - TABS
# ============================================================================

tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "✏️ Update Components", "📝 Client Summary", "➕ Add Component"])

# ============================================================================
# TAB 1: OVERVIEW
# ============================================================================

with tab1:
    st.title(project_data['project_name'])

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Client", project_data['client'])
    with col2:
        # Calculate total hours from cost at $250/hr
        total_hours = project_data['sow']['total_cost_usd'] / 250
        st.metric("Total Hours", f"{total_hours:.1f} hrs")
    with col3:
        st.metric("Completion Date", project_data['estimated_completion'])
    with col4:
        status_color = {"draft": "🔵", "in_progress": "🟠", "completed": "🟢", "on_hold": "🔴"}
        st.metric("Status", f"{status_color.get(project_data['status'], '')} {project_data['status']}")

    st.markdown("---")

    # Milestones
    st.subheader("📌 Milestones")
    milestones_display = []
    for milestone in project_data['sow']['milestones']:
        milestone_hours = milestone['cost_usd'] / 250
        milestones_display.append({
            'Name': milestone['name'],
            'Hours': f"{milestone_hours:.1f}",
            'Status': milestone['status'],
            'Completion': milestone.get('estimated_completion', milestone.get('completed_date', 'TBD'))
        })
    milestone_df = pd.DataFrame(milestones_display)
    st.dataframe(milestone_df, use_container_width=True, hide_index=True)

    st.markdown("---")

    # Components overview
    st.subheader("🔧 Components Overview")

    # Calculate statistics
    components = project_data['components']
    total_components = len(components)
    completed = sum(1 for c in components if c['status'] == 'completed')
    in_progress = sum(1 for c in components if c['status'] == 'in_progress')
    not_started = sum(1 for c in components if c['status'] == 'not_started')
    blocked = sum(1 for c in components if c['status'] == 'blocked')

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total", total_components)
    col2.metric("✅ Completed", completed)
    col3.metric("🔄 In Progress", in_progress)
    col4.metric("⏳ Not Started", not_started)
    col5.metric("🚫 Blocked", blocked)

    # Components table with status
    components_display = []
    for comp in components:
        time_used = comp.get('time_used_hours', 0)
        sow_allocated = comp.get('sow_allocated_hours', 0)
        progress = comp.get('progress_fraction', 0)

        components_display.append({
            'Component': comp['name'],
            'Assigned To': comp['assigned_to'],
            'Status': comp['status'],
            'Traffic Light': calculate_status(time_used, sow_allocated, progress),
            'Progress': f"{progress*100:.0f}%" if progress else "0%",
            'Hours Used': time_used,
            'Hours Allocated': sow_allocated,
            'Priority': comp.get('priority', 'medium')
        })

    df = pd.DataFrame(components_display)
    st.dataframe(df, use_container_width=True, hide_index=True)

# ============================================================================
# TAB 2: UPDATE COMPONENTS
# ============================================================================

with tab2:
    st.header("✏️ Update Component Status")

    # Component selector
    component_names = [c['name'] for c in project_data['components']]
    selected_component_name = st.selectbox("Select Component to Update", component_names, key="component_selector")

    # Find the component
    comp_index = next(i for i, c in enumerate(project_data['components']) if c['name'] == selected_component_name)
    component = project_data['components'][comp_index]

    st.markdown(f"### {component['name']}")
    st.markdown(f"**Component ID:** `{component['component_id']}`")

    # Two columns for editing
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Status & Assignment")

        new_status = st.selectbox(
            "Status",
            options=["not_started", "in_progress", "completed", "blocked"],
            index=["not_started", "in_progress", "completed", "blocked"].index(component['status']),
            key="update_status"
        )

        new_assigned_to = st.text_input("Assigned To", value=component['assigned_to'], key="update_assigned_to")

        new_priority = st.selectbox(
            "Priority",
            options=["low", "medium", "high"],
            index=["low", "medium", "high"].index(component.get('priority', 'medium')),
            key="update_priority"
        )

        new_progress = st.slider(
            "Progress (%)",
            min_value=0,
            max_value=100,
            value=int(component.get('progress_fraction', 0) * 100),
            step=5,
            key="update_progress"
        )

    with col2:
        st.subheader("Time Tracking")

        new_time_used = st.number_input(
            "Time Used (hours)",
            min_value=0.0,
            value=float(component.get('time_used_hours', 0)),
            step=0.5,
            key="update_time_used"
        )

        new_method_dev = st.number_input(
            "Method Dev Hours",
            min_value=0.0,
            value=float(component.get('method_dev_hours', 0)),
            step=0.5,
            key="update_method_dev"
        )

        new_compute = st.number_input(
            "Compute Hours",
            min_value=0.0,
            value=float(component.get('compute_hours', 0)),
            step=0.5,
            key="update_compute"
        )

        new_sow_allocated = st.number_input(
            "SOW Allocated Hours",
            min_value=0.0,
            value=float(component.get('sow_allocated_hours', 0)),
            step=0.5,
            key="update_sow_allocated"
        )

    # Traffic light preview
    traffic_light = calculate_status(new_time_used, new_sow_allocated, new_progress/100)
    st.info(f"**Current Status:** {traffic_light}")

    # Notes
    st.subheader("Notes & Blockers")
    new_notes = st.text_area("Notes", value=component.get('notes', ''), height=100, key="update_notes")

    # Blockers section
    if new_status == 'blocked':
        st.warning("⚠️ This component is blocked")
        blocker_issue = st.text_input(
            "Blocker Issue",
            value=component.get('blockers', [{}])[0].get('issue', '') if component.get('blockers') else '',
            key="blocker_issue_input"
        )
        blocker_severity = st.selectbox(
            "Severity",
            options=["low", "medium", "high"],
            index=1,
            key="blocker_severity_select"
        )

    # Save button
    st.markdown("---")
    if st.button("💾 Save Changes", type="primary", use_container_width=True):
        # Update component
        project_data['components'][comp_index]['status'] = new_status
        project_data['components'][comp_index]['assigned_to'] = new_assigned_to
        project_data['components'][comp_index]['priority'] = new_priority
        project_data['components'][comp_index]['progress_fraction'] = new_progress / 100
        project_data['components'][comp_index]['time_used_hours'] = new_time_used
        project_data['components'][comp_index]['method_dev_hours'] = new_method_dev
        project_data['components'][comp_index]['compute_hours'] = new_compute
        project_data['components'][comp_index]['sow_allocated_hours'] = new_sow_allocated
        project_data['components'][comp_index]['notes'] = new_notes

        if new_status == 'blocked':
            project_data['components'][comp_index]['blockers'] = [{
                'issue': blocker_issue,
                'raised_date': datetime.now().strftime('%Y-%m-%d'),
                'severity': blocker_severity
            }]
        elif 'blockers' in project_data['components'][comp_index]:
            del project_data['components'][comp_index]['blockers']

        # Save to file
        save_project_toml(selected_project_path, project_data)
        st.success(f"✅ Saved changes to {component['name']}")
        st.rerun()

# ============================================================================
# TAB 3: CLIENT SUMMARY
# ============================================================================

with tab3:
    st.header("📝 Client Status Summary")

    st.markdown("Copy this summary for client communications:")

    summary_text = generate_client_summary(project_data)

    st.markdown(summary_text)

    st.download_button(
        label="📥 Download as Markdown",
        data=summary_text,
        file_name=f"{project_data['project_id']}_status_{datetime.now().strftime('%Y%m%d')}.md",
        mime="text/markdown"
    )

# ============================================================================
# TAB 4: ADD NEW COMPONENT
# ============================================================================

with tab4:
    st.header("➕ Add New Component")

    st.info("💡 Select from component library or create custom component")

    # Load component library
    components_library = load_components_library()

    use_library = st.checkbox("Select from Component Library", value=True, key="use_library_checkbox")

    if use_library and components_library:
        library_names = [c['name'] for c in components_library]
        selected_library_comp = st.selectbox("Select Component Template", library_names, key="library_component_select")

        # Find the component in library
        library_comp = next(c for c in components_library if c['name'] == selected_library_comp)

        st.markdown(f"**Description:** {library_comp.get('description', 'N/A')}")
        st.markdown(f"**Typical Method Dev Hours:** {library_comp.get('typical_method_dev_hours', [0,0])}")
        st.markdown(f"**Typical Compute Hours:** {library_comp.get('typical_compute_hours', [0,0])}")

        # Pre-fill from library
        default_name = library_comp['name']
        default_id = library_comp['component_id']
        default_method_dev = library_comp.get('typical_method_dev_hours', [2.0])[0]
        default_compute = library_comp.get('typical_compute_hours', [3.0])[0]
    else:
        default_name = ""
        default_id = f"custom-{len(project_data['components'])+1:03d}"
        default_method_dev = 2.0
        default_compute = 3.0

    col1, col2 = st.columns(2)

    with col1:
        new_comp_id = st.text_input("Component ID", value=default_id, key="new_comp_id")
        new_comp_name = st.text_input("Component Name", value=default_name, key="new_comp_name")
        new_comp_assigned = st.text_input("Assigned To", value=project_data['analyst_primary'], key="new_comp_assigned")
        new_comp_priority = st.selectbox("Priority", options=["low", "medium", "high"], index=1, key="new_comp_priority")

    with col2:
        new_comp_method_dev = st.number_input("Method Dev Hours", min_value=0.0, value=default_method_dev, step=0.5, key="new_comp_method_dev")
        new_comp_compute = st.number_input("Compute Hours", min_value=0.0, value=default_compute, step=0.5, key="new_comp_compute")
        new_comp_sow_allocated = st.number_input("SOW Allocated Hours", min_value=0.0, value=default_method_dev+default_compute, step=0.5, key="new_comp_sow_allocated")

    new_comp_notes = st.text_area("Notes", height=100, key="new_comp_notes")

    if st.button("➕ Add Component to Project", type="primary"):
        new_component = {
            'component_id': new_comp_id,
            'name': new_comp_name,
            'status': 'not_started',
            'assigned_to': new_comp_assigned,
            'method_dev_hours': new_comp_method_dev,
            'compute_hours': new_comp_compute,
            'sow_allocated_hours': new_comp_sow_allocated,
            'time_used_hours': 0.0,
            'priority': new_comp_priority,
            'inputs': [],
            'outputs': [],
            'dependencies': [],
            'notes': new_comp_notes
        }

        project_data['components'].append(new_component)
        save_project_toml(selected_project_path, project_data)
        st.success(f"✅ Added new component: {new_comp_name}")
        st.rerun()

# ============================================================================
# FOOTER
# ============================================================================

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔧 Tools")

if st.sidebar.button("🔄 Refresh Project Data"):
    st.rerun()

if st.sidebar.button("📊 Export to CSV"):
    df_export = pd.DataFrame(project_data['components'])
    csv = df_export.to_csv(index=False)
    st.sidebar.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name=f"{project_data['project_id']}_components.csv",
        mime="text/csv"
    )

st.sidebar.markdown("---")
st.sidebar.caption("Analysis Architect v1.0")
st.sidebar.caption(f"Project file: `{selected_project_path.name}`")
