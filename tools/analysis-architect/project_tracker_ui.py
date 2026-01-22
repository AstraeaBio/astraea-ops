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
from datetime import datetime, date, timedelta
import os

# TOML imports - use built-in tomllib for Python 3.11+ reading
if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib
import tomli_w

# Portfolio library
import portfolio_lib

# ============================================================================
# SCRIPT SCANNING & OUTPUT TRACKING
# ============================================================================

def scan_scripts_directory(directory_path, extensions=None):
    """
    Scan directory for analysis scripts and return structured inventory.

    Args:
        directory_path: Path to directory containing scripts
        extensions: List of file extensions to scan (default: ['.py', '.ipynb', '.R', '.groovy', '.sh'])

    Returns:
        List of dicts with script metadata
    """
    if extensions is None:
        extensions = ['.py', '.ipynb', '.R', '.groovy', '.sh', '.m']

    script_dir = Path(directory_path)
    if not script_dir.exists():
        return []

    discovered_scripts = []

    for script_file in script_dir.rglob('*'):
        if script_file.is_file() and script_file.suffix in extensions:
            # Skip hidden files and common non-script patterns
            if script_file.name.startswith('.') or '__pycache__' in str(script_file):
                continue

            # Detect version patterns
            version_status = detect_version_status(script_file.name)

            # Calculate relative path from project directory
            try:
                rel_path = script_file.relative_to(script_dir.parent)
            except ValueError:
                rel_path = script_file

            discovered_scripts.append({
                'path': str(rel_path),
                'filename': script_file.name,
                'language': detect_language(script_file.suffix),
                'last_modified': datetime.fromtimestamp(script_file.stat().st_mtime).strftime('%Y-%m-%d'),
                'version_status': version_status,
                'size_kb': script_file.stat().st_size / 1024
            })

    # Sort by modification date (newest first)
    discovered_scripts.sort(key=lambda x: x['last_modified'], reverse=True)

    return discovered_scripts

def detect_language(extension):
    """Map file extension to language"""
    lang_map = {
        '.py': 'python',
        '.ipynb': 'python',
        '.R': 'R',
        '.groovy': 'groovy',
        '.sh': 'bash',
        '.m': 'matlab'
    }
    return lang_map.get(extension, 'unknown')

def detect_version_status(filename):
    """
    Detect if a script is latest, deprecated, or development based on naming patterns.

    Patterns:
    - .old, .old2, _old, _backup: deprecated
    - _dev, _test, _experimental, _draft: development
    - _revN, _final, or no pattern: latest
    """
    filename_lower = filename.lower()

    # Check for deprecated patterns
    deprecated_patterns = ['.old', '_old', '_backup', '_archive']
    if any(pattern in filename_lower for pattern in deprecated_patterns):
        return 'deprecated'

    # Check for development patterns
    dev_patterns = ['_dev', '_test', '_experimental', '_draft', '_wip']
    if any(pattern in filename_lower for pattern in dev_patterns):
        return 'development'

    # Default to latest
    return 'latest'

def check_component_outputs(component, project_dir):
    """
    Check if expected outputs exist for a component.

    Args:
        component: Component dict with 'outputs' list
        project_dir: Path to project directory

    Returns:
        Dict with output status information
    """
    outputs_status = []

    for output in component.get('outputs', []):
        location = output.get('location', '')

        # Handle cloud storage paths (gs://, s3://, etc.)
        if location.startswith(('gs://', 's3://', 'http://', 'https://')):
            outputs_status.append({
                'location': location,
                'exists': None,  # Cannot check cloud storage from local
                'type': 'cloud'
            })
            continue

        # Check local paths
        output_path = Path(location)
        if not output_path.is_absolute():
            output_path = Path(project_dir) / location

        exists = output_path.exists()
        outputs_status.append({
            'location': location,
            'exists': exists,
            'type': output.get('type', 'unknown'),
            'created_date': output.get('created_date', 'N/A')
        })

    # Calculate summary
    local_outputs = [o for o in outputs_status if o['type'] != 'cloud']
    if not local_outputs:
        completion_pct = None
    else:
        completed = sum(1 for o in local_outputs if o['exists'])
        completion_pct = (completed / len(local_outputs)) * 100

    return {
        'outputs': outputs_status,
        'completion_percentage': completion_pct,
        'total': len(outputs_status),
        'completed': sum(1 for o in outputs_status if o['exists'])
    }

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

def validate_project_structure(project_data):
    """
    Validate that project has all required fields for UI to function.
    Returns: (is_valid: bool, issues: list of strings)
    """
    issues = []

    # Check SOW section
    if 'sow' not in project_data:
        issues.append("❌ Missing [sow] section")
    else:
        # Check total_cost_usd
        if 'total_cost_usd' not in project_data['sow'] or not project_data['sow']['total_cost_usd']:
            issues.append("⚠️ Missing sow.total_cost_usd (required for hours calculation)")

        # Check milestones
        if 'milestones' not in project_data['sow'] or not project_data['sow']['milestones']:
            issues.append("⚠️ Missing sow.milestones (required for client summary)")

    # Check components
    if 'components' not in project_data or not project_data['components']:
        issues.append("❌ Missing components array (at least one component required)")

    # Check dates
    if 'estimated_completion' not in project_data:
        issues.append("⚠️ Missing estimated_completion date")

    # Check basic metadata
    required_fields = ['project_id', 'project_name', 'client', 'status']
    for field in required_fields:
        if field not in project_data:
            issues.append(f"❌ Missing required field: {field}")

    is_valid = len(issues) == 0
    return is_valid, issues

def generate_client_summary(project_data):
    """Generate markdown summary for client"""
    summary = f"""## Project Status: {project_data['project_name']}
**Client**: {project_data['client']}
**Estimated Completion**: {project_data.get('estimated_completion', 'TBD')}
**Status**: {project_data['status'].upper()}

---

"""

    # Only include milestones section if they exist
    if 'milestones' in project_data.get('sow', {}) and project_data['sow']['milestones']:
        summary += "### Milestones\n\n"
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

def generate_analysis_report(project_data, selected_components=None, include_scripts=True, include_outputs=True):
    """
    Generate comprehensive analysis report using ANALYSIS_REPORT_PROMPT_TEMPLATE structure.

    Args:
        project_data: Project dict from project.toml
        selected_components: List of component_ids to include (None = all)
        include_scripts: Include script inventory section
        include_outputs: Include outputs/deliverables section

    Returns:
        Markdown string with complete report
    """
    # Filter components if specified
    if selected_components:
        components = [c for c in project_data['components'] if c['component_id'] in selected_components]
    else:
        components = project_data['components']

    # Start report
    report = f"""# {project_data['project_name']} - Analysis Report

**Project ID:** {project_data['project_id']}
**Client:** {project_data['client']}
**Project Manager:** {project_data.get('pm', 'N/A')}
**Primary Analyst:** {project_data.get('analyst_primary', 'N/A')}
**Report Generated:** {datetime.now().strftime('%Y-%m-%d')}

---

## Executive Summary

[TO BE FILLED: 1-2 paragraph summary of key findings and outcomes]

### Key Findings

[TO BE FILLED: 3-5 numbered bullet points with primary discoveries]

1. Finding 1
2. Finding 2
3. Finding 3

---

## 1. Study Design

### 1.1 Project Overview

"""

    # Add project description from notes or data section
    if 'description' in project_data:
        report += f"{project_data['description']}\n\n"
    else:
        report += "[TO BE FILLED: Brief description of project objectives and scope]\n\n"

    # Data characteristics
    if 'data' in project_data:
        data_section = project_data['data']
        report += f"""### 1.2 Data Characteristics

**Platform:** {data_section.get('platform', 'N/A')}
**Samples:** {data_section.get('n_samples', 'N/A')}
**ROIs:** {data_section.get('n_rois', 'N/A')}
**Markers/Channels:** {data_section.get('markers', 'N/A')}

"""

    # Methodology overview from components
    report += """### 1.3 Methodology Overview

The analysis pipeline consisted of the following major phases:

"""

    # Group components by phase (infer from component names/ids)
    phase_map = {
        'data': [], 'qc': [], 'seg': [], 'feature': [],
        'spatial': [], 'analysis': [], 'visualization': [], 'report': []
    }

    for comp in components:
        comp_id = comp['component_id'].lower()
        if any(x in comp_id for x in ['data', 'receipt', 'ingest']):
            phase_map['data'].append(comp)
        elif any(x in comp_id for x in ['qc', 'validation', 'quality']):
            phase_map['qc'].append(comp)
        elif any(x in comp_id for x in ['seg', 'segmentation', 'mask']):
            phase_map['seg'].append(comp)
        elif any(x in comp_id for x in ['feature', 'threshold', 'classifier', 'phenotype']):
            phase_map['feature'].append(comp)
        elif any(x in comp_id for x in ['spatial', 'distance', 'proximity', 'neighborhood']):
            phase_map['spatial'].append(comp)
        elif any(x in comp_id for x in ['cluster', 'statistical', 'correlation']):
            phase_map['analysis'].append(comp)
        elif any(x in comp_id for x in ['visual', 'plot', 'figure']):
            phase_map['visualization'].append(comp)
        elif any(x in comp_id for x in ['report', 'writeup', 'methods']):
            phase_map['report'].append(comp)
        else:
            phase_map['analysis'].append(comp)  # Default

    phase_names = {
        'data': 'Data Ingestion & QC',
        'qc': 'Quality Control',
        'seg': 'Segmentation',
        'feature': 'Feature Extraction & Classification',
        'spatial': 'Spatial Analysis',
        'analysis': 'Statistical Analysis',
        'visualization': 'Visualization',
        'report': 'Reporting'
    }

    for phase_key, phase_name in phase_names.items():
        if phase_map[phase_key]:
            report += f"**{phase_name}:**\n"
            for comp in phase_map[phase_key]:
                report += f"- {comp['name']}\n"
            report += "\n"

    # Results sections (placeholder structure)
    report += """---

## 2. Results

### 2.1 [Primary Analysis Type]

[TO BE FILLED: Description of analysis approach and rationale]

"""

    # Add placeholder for results table
    report += """**Table 1: [Analysis Results Summary]**

| Metric | Value | p-value | n | Significant? |
|--------|-------|---------|---|--------------|
| [Metric 1] | [Value] | [p-value] | [n] | [Yes/No] |
| [Metric 2] | [Value] | [p-value] | [n] | [Yes/No] |

[TO BE FILLED: Interpretation of results]

---

**[INSERT FIGURE 1 HERE]**

**Figure 1: [Title].** [TO BE FILLED: Detailed figure legend with sample sizes, statistical tests, and significance levels]

---

"""

    # Component deliverables section
    if include_outputs:
        report += """## 3. Component Deliverables

The following analysis components were completed and delivered:

"""
        completed_comps = [c for c in components if c['status'] == 'completed']

        for i, comp in enumerate(completed_comps, 1):
            report += f"""### 3.{i} {comp['name']}

**Status:** ✅ Completed
**Assigned to:** {comp.get('assigned_to', 'N/A')}
**Time allocated:** {comp.get('sow_allocated_hours', 0):.1f} hours
**Time used:** {comp.get('time_used_hours', 0):.1f} hours

"""
            if 'outputs' in comp and comp['outputs']:
                report += "**Outputs:**\n"
                for output in comp['outputs']:
                    output_type = output.get('type', 'File')
                    output_desc = output.get('description', 'N/A')
                    report += f"- {output_type}: {output_desc}\n"
                report += "\n"

            if comp.get('notes'):
                report += f"**Notes:** {comp['notes']}\n\n"

    # Script inventory section
    if include_scripts:
        # Get scripts from code_repository or closeout.scripts
        scripts = []
        if 'code_repository' in project_data:
            scripts.extend(project_data['code_repository'])
        if 'closeout' in project_data and 'scripts' in project_data['closeout']:
            # Filter to latest versions only
            closeout_scripts = [s for s in project_data['closeout']['scripts']
                              if s.get('version_status') == 'latest']
            scripts.extend(closeout_scripts)

        if scripts:
            report += """---

## 4. Analysis Scripts & Pipeline

### 4.1 Script Inventory

The following scripts were developed and used in this analysis:

"""
            for i, script in enumerate(scripts, 1):
                script_path = script.get('path', script.get('script', 'N/A'))
                script_lang = script.get('language', 'unknown')
                script_purpose = script.get('purpose', 'N/A')

                report += f"""#### 4.1.{i} `{script_path}`

**Language:** {script_lang}
**Purpose:** {script_purpose}
"""

                if 'reusability' in script:
                    report += f"**Reusability:** {script['reusability']}\n"

                if 'dependencies' in script and script['dependencies']:
                    deps = ', '.join(script['dependencies'])
                    report += f"**Dependencies:** {deps}\n"

                report += "\n"

    # Conclusions section
    report += """---

## 5. Conclusions

### 5.1 Primary Conclusions

[TO BE FILLED: Summary of main findings and their implications]

1. Conclusion 1
2. Conclusion 2
3. Conclusion 3

### 5.2 Limitations

[TO BE FILLED: Key caveats and limitations of the analysis]

- Limitation 1
- Limitation 2

### 5.3 Future Directions

[TO BE FILLED: Suggested follow-up analyses or studies]

- Direction 1
- Direction 2

---

## 6. Methods Summary

[TO BE FILLED: Brief methods description suitable for publication]

---

## Appendix A: Data Locations

"""

    # Add data locations
    if 'data' in project_data:
        data_section = project_data['data']
        if 'input_location' in data_section:
            report += f"**Raw Data:** `{data_section['input_location']}`\n"
        if 'output_location' in data_section:
            report += f"**Processed Data:** `{data_section['output_location']}`\n"

    if 'closeout' in project_data and 'data_locations' in project_data['closeout']:
        data_locs = project_data['closeout']['data_locations']
        for key, path in data_locs.items():
            if path:
                report += f"**{key.replace('_', ' ').title()}:** `{path}`\n"

    report += "\n---\n\n*Report generated by Analysis Architect v1.2*\n"

    return report

# ============================================================================
# SIDEBAR - PROJECT SELECTION
# ============================================================================

st.sidebar.title("🔬 Analysis Architect")
st.sidebar.markdown("### Project Tracker")

# Portfolio selector (optional)
st.sidebar.markdown("---")
st.sidebar.markdown("#### 📊 Portfolio View")

portfolio_file = st.sidebar.text_input(
    "Portfolio File (optional)",
    value="",
    help="Path to portfolio.toml file for multi-project view",
    key="portfolio_file_input"
)

# Load portfolio if specified
portfolio_data = None
if portfolio_file and Path(portfolio_file).exists():
    try:
        portfolio_data = portfolio_lib.load_portfolio(portfolio_file)
        st.sidebar.success(f"✅ Portfolio: {portfolio_data['portfolio_config'].get('portfolio_name', 'Loaded')}")
        st.sidebar.markdown(f"**Projects:** {len(portfolio_data['projects'])}")
    except Exception as e:
        st.sidebar.error(f"Error loading portfolio: {e}")

st.sidebar.markdown("---")
st.sidebar.markdown("#### 📁 Single Project View")

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

    # Validate project structure
    st.sidebar.markdown("---")
    st.sidebar.markdown("#### ✅ Validation")
    is_valid, validation_issues = validate_project_structure(project_data)

    if is_valid:
        st.sidebar.success("All required fields present")
    else:
        st.sidebar.warning("⚠️ Issues found:")
        for issue in validation_issues:
            st.sidebar.markdown(f"- {issue}")
        st.sidebar.info("💡 See sow_parser_prompt.md for required field details")

# ============================================================================
# MAIN CONTENT - TABS
# ============================================================================

# Add Portfolio tab if portfolio is loaded
if portfolio_data:
    tabs_list = ["🌐 Portfolio Overview", "📊 Project Overview", "✏️ Update Components", "📜 Script Inventory", "📊 Output Tracking", "📝 Client Summary", "📄 Report Builder", "➕ Add Component"]
    tab0, tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(tabs_list)
else:
    tabs_list = ["📊 Overview", "✏️ Update Components", "📜 Script Inventory", "📊 Output Tracking", "📝 Client Summary", "📄 Report Builder", "➕ Add Component"]
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(tabs_list)

# ============================================================================
# TAB 0: PORTFOLIO OVERVIEW (if portfolio loaded)
# ============================================================================

if portfolio_data:
    with tab0:
        st.title("🌐 Portfolio Overview")
        st.markdown(f"**{portfolio_data['portfolio_config'].get('portfolio_name', 'Portfolio')}**")
        st.markdown(f"*Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*")

        # Portfolio Summary Metrics
        st.markdown("---")
        st.subheader("📈 Portfolio Health")

        projects = portfolio_data['projects']
        total_projects = len(projects)
        active_projects = len([p for p in projects if p.get('status') != 'completed'])

        # Component counts
        total_components = sum(len(p.get('components', [])) for p in projects)
        completed_comps = sum(len([c for c in p.get('components', []) if c.get('status') == 'completed']) for p in projects)
        in_progress_comps = sum(len([c for c in p.get('components', []) if c.get('status') == 'in_progress']) for p in projects)
        blocked_comps = sum(len([c for c in p.get('components', []) if c.get('status') == 'blocked']) for p in projects)

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Active Projects", active_projects, f"of {total_projects} total")
        with col2:
            st.metric("Total Tasks", total_components)
        with col3:
            completion_pct = (completed_comps / total_components * 100) if total_components > 0 else 0
            st.metric("Completed", f"{completion_pct:.0f}%", f"{completed_comps}/{total_components}")
        with col4:
            st.metric("Blocked", blocked_comps, delta=f"{blocked_comps} items" if blocked_comps > 0 else None, delta_color="inverse")

        # Immediate Attention Section
        st.markdown("---")
        st.subheader("🚨 Immediate Attention")

        attention_items = portfolio_lib.get_immediate_attention_items(portfolio_data)

        if attention_items:
            for item in attention_items[:5]:  # Show top 5
                urgency_color = {"high": "🔴", "medium": "🟡", "low": "🟢"}
                comp = item['component']

                with st.expander(f"{urgency_color.get(item.get('urgency', 'low'))} {item['project_name']} - {comp['name']}", expanded=(item.get('urgency') == 'high')):
                    st.markdown(f"**Type:** {item['type'].replace('_', ' ').title()}")
                    st.markdown(f"**Assigned to:** {comp.get('assigned_to', 'Unassigned')}")
                    st.markdown(f"**Status:** {comp['status']}")

                    if item['type'] == 'blocked':
                        blockers = comp.get('blockers', [])
                        if blockers:
                            st.markdown(f"**Blocker:** {blockers[0].get('issue', 'Unknown')}")

                    if item['type'] == 'high_utilization':
                        st.markdown(f"**Utilization:** {item.get('utilization', 0)*100:.0f}%")

                    if item.get('deadline'):
                        st.markdown(f"**Deadline:** {item['deadline']}")
        else:
            st.success("✅ No immediate attention items!")

        # Analyst Workload
        st.markdown("---")
        st.subheader("👥 Analyst Workload")

        analyst_workload = portfolio_lib.calculate_analyst_workload(portfolio_data)

        if analyst_workload:
            for analyst, data in analyst_workload.items():
                util_pct = data['utilization'] * 100

                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**{analyst}**")
                    st.progress(min(data['utilization'], 1.0))
                    st.caption(f"{util_pct:.0f}% - {data['hours_used']:.1f}h used / {data['hours_allocated']:.1f}h allocated across {data['project_count']} projects")
                with col2:
                    if util_pct > 85:
                        st.warning("⚠️ High")
                    elif util_pct < 50:
                        st.info("➕ Capacity")
                    else:
                        st.success("✓ Good")

        # Batch Opportunities
        st.markdown("---")
        st.subheader("⚡ Batch Opportunities")

        config = portfolio_data['portfolio_config']
        batching_config = config.get('batching', {})

        if batching_config.get('enabled', True):
            batches = portfolio_lib.detect_batch_candidates(
                portfolio_data,
                min_batch_size=batching_config.get('min_batch_size', 2),
                same_platform=batching_config.get('same_platform_required', True),
                same_component_type=batching_config.get('same_component_type_required', True),
                same_status=batching_config.get('same_status_required', True),
                batchable_components=batching_config.get('batchable_components')
            )

            if batches:
                for batch in batches[:3]:  # Show top 3 batches
                    with st.expander(f"⚡ {batch['batch_key']} ({batch['count']} tasks)", expanded=True):
                        for task in batch['tasks']:
                            st.markdown(f"- **{task['project_name']}** - {task['component']['name']} ({task['platform']})")
                            st.caption(f"   Assigned: {task['component'].get('assigned_to', 'Unassigned')} | Status: {task['component']['status']}")

                        if st.button(f"Mark all as In Progress", key=f"batch_{batch['batch_key']}"):
                            st.info("Batch action functionality coming soon!")
            else:
                st.info("No batch opportunities detected right now")
        else:
            st.info("Batch detection is disabled in portfolio config")

        # Timeline View
        st.markdown("---")
        st.subheader("📅 Timeline Overview")

        today = date.today()
        this_week = []
        next_week = []
        two_weeks = []
        overdue_items = []

        for project in projects:
            deadline_str = project.get('timeline', {}).get('client_deadline')
            if deadline_str:
                try:
                    deadline = datetime.strptime(deadline_str, '%Y-%m-%d').date()
                    days_until = (deadline - today).days

                    project_info = f"{project['project_name']} (Due: {deadline_str})"

                    if days_until < 0:
                        overdue_items.append(project_info)
                    elif days_until <= 7:
                        this_week.append(project_info)
                    elif days_until <= 14:
                        next_week.append(project_info)
                    elif days_until <= 30:
                        two_weeks.append(project_info)
                except:
                    pass

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Overdue", len(overdue_items))
            if overdue_items:
                for item in overdue_items:
                    st.caption(f"🔴 {item}")
        with col2:
            st.metric("This Week", len(this_week))
            if this_week:
                for item in this_week:
                    st.caption(f"🟡 {item}")
        with col3:
            st.metric("Next Week", len(next_week))
            if next_week:
                for item in next_week:
                    st.caption(f"🟢 {item}")
        with col4:
            st.metric("2+ Weeks", len(two_weeks))

# ============================================================================
# TAB 1: OVERVIEW (Project-specific)
# ============================================================================

with tab1:
    st.title(project_data['project_name'])

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Client", project_data['client'])
    with col2:
        # Calculate total hours from cost at $250/hr (if available)
        if 'total_cost_usd' in project_data['sow'] and project_data['sow']['total_cost_usd']:
            total_hours = project_data['sow']['total_cost_usd'] / 250
            st.metric("Total Hours", f"{total_hours:.1f} hrs")
        else:
            st.metric("Total Hours", "N/A")
    with col3:
        st.metric("Completion Date", project_data.get('estimated_completion', 'TBD'))
    with col4:
        status_color = {"draft": "🔵", "in_progress": "🟠", "completed": "🟢", "on_hold": "🔴"}
        st.metric("Status", f"{status_color.get(project_data['status'], '')} {project_data['status']}")

    st.markdown("---")

    # Milestones
    st.subheader("📌 Milestones")
    if 'milestones' in project_data['sow'] and project_data['sow']['milestones']:
        milestones_display = []
        for milestone in project_data['sow']['milestones']:
            milestone_hours = milestone.get('cost_usd', 0) / 250 if milestone.get('cost_usd') else 0
            milestones_display.append({
                'Name': milestone['name'],
                'Hours': f"{milestone_hours:.1f}" if milestone_hours else "N/A",
                'Status': milestone['status'],
                'Completion': milestone.get('estimated_completion', milestone.get('completed_date', 'TBD'))
            })
        milestone_df = pd.DataFrame(milestones_display)
        st.dataframe(milestone_df, use_container_width=True, hide_index=True)
    else:
        st.info("No milestones defined for this project")

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
# TAB 3: SCRIPT INVENTORY
# ============================================================================

with tab3:
    st.header("📜 Script Inventory & Management")

    # Get project directory
    project_dir = selected_project_path.parent

    # Script directory input
    st.subheader("🔍 Script Discovery")

    col1, col2 = st.columns([3, 1])
    with col1:
        scripts_dir_input = st.text_input(
            "Scripts Directory",
            value=str(project_dir),
            help="Directory to scan for analysis scripts",
            key="scripts_dir_input"
        )
    with col2:
        scan_button = st.button("🔄 Scan Scripts", type="primary", use_container_width=True)

    # Scan scripts on button click
    discovered_scripts = []
    if scan_button and scripts_dir_input:
        with st.spinner("Scanning for scripts..."):
            discovered_scripts = scan_scripts_directory(scripts_dir_input)
            if discovered_scripts:
                st.success(f"✅ Found {len(discovered_scripts)} scripts")
            else:
                st.warning("No scripts found in directory")

    # Display existing code_repository entries
    st.markdown("---")
    st.subheader("📚 Current Script Inventory")

    # Initialize code_repository if it doesn't exist
    if 'code_repository' not in project_data:
        project_data['code_repository'] = []

    # Also check for closeout.scripts (for completed projects)
    closeout_scripts = []
    if 'closeout' in project_data and 'scripts' in project_data['closeout']:
        closeout_scripts = project_data['closeout']['scripts']

    # Combine both sources
    all_scripts = project_data['code_repository'] + [
        {'script': s.get('path', ''), 'component_ids': s.get('related_components', []),
         'location': s.get('path', ''), 'last_modified': s.get('last_modified', 'N/A'),
         'source': 'closeout'}
        for s in closeout_scripts
    ]

    if all_scripts:
        # Display as table
        scripts_display = []
        for idx, script_entry in enumerate(all_scripts):
            script_name = script_entry.get('script', script_entry.get('location', 'Unknown'))
            component_ids = script_entry.get('component_ids', [])
            source = script_entry.get('source', 'code_repository')

            scripts_display.append({
                'Script': script_name,
                'Components': ', '.join(component_ids) if component_ids else 'None',
                'Last Modified': script_entry.get('last_modified', 'N/A'),
                'Source': source
            })

        df_scripts = pd.DataFrame(scripts_display)
        st.dataframe(df_scripts, use_container_width=True, hide_index=True)
    else:
        st.info("No scripts registered yet. Scan for scripts or add manually below.")

    # Show discovered scripts (if scan was run)
    if discovered_scripts:
        st.markdown("---")
        st.subheader("🆕 Discovered Scripts")

        # Filter options
        col1, col2, col3 = st.columns(3)
        with col1:
            filter_status = st.multiselect(
                "Filter by Version Status",
                options=['latest', 'development', 'deprecated'],
                default=['latest', 'development'],
                key="filter_status"
            )
        with col2:
            filter_language = st.multiselect(
                "Filter by Language",
                options=list(set(s['language'] for s in discovered_scripts)),
                default=list(set(s['language'] for s in discovered_scripts)),
                key="filter_language"
            )

        # Apply filters
        filtered_scripts = [
            s for s in discovered_scripts
            if s['version_status'] in filter_status and s['language'] in filter_language
        ]

        # Display discovered scripts with "Add to Inventory" buttons
        st.markdown(f"**Showing {len(filtered_scripts)} of {len(discovered_scripts)} scripts**")

        for idx, script in enumerate(filtered_scripts[:20]):  # Limit to 20 for performance
            with st.expander(f"📄 {script['filename']} ({script['language']}) - {script['version_status']}", expanded=False):
                col1, col2 = st.columns([2, 1])

                with col1:
                    st.markdown(f"**Path:** `{script['path']}`")
                    st.markdown(f"**Last Modified:** {script['last_modified']}")
                    st.markdown(f"**Size:** {script['size_kb']:.1f} KB")

                with col2:
                    # Component selector for linking
                    component_options = ['None'] + [c['component_id'] for c in project_data['components']]
                    selected_components = st.multiselect(
                        "Link to Components",
                        options=component_options[1:],  # Exclude 'None'
                        key=f"link_comp_{idx}"
                    )

                    if st.button(f"➕ Add to Inventory", key=f"add_script_{idx}"):
                        # Add to code_repository
                        new_entry = {
                            'script': script['filename'],
                            'location': script['path'],
                            'component_ids': selected_components,
                            'last_modified': script['last_modified'],
                            'language': script['language'],
                            'version_status': script['version_status']
                        }

                        project_data['code_repository'].append(new_entry)
                        save_project_toml(selected_project_path, project_data)
                        st.success(f"✅ Added {script['filename']} to inventory")
                        st.rerun()

    # Manual script addition
    st.markdown("---")
    st.subheader("➕ Add Script Manually")

    with st.form("add_script_form"):
        col1, col2 = st.columns(2)

        with col1:
            manual_script_name = st.text_input("Script Name", key="manual_script_name")
            manual_script_location = st.text_input("Script Location/Path", key="manual_script_location")

        with col2:
            manual_script_language = st.selectbox(
                "Language",
                options=['python', 'R', 'groovy', 'bash', 'matlab', 'other'],
                key="manual_script_language"
            )
            manual_components = st.multiselect(
                "Link to Components",
                options=[c['component_id'] for c in project_data['components']],
                key="manual_components"
            )

        manual_submit = st.form_submit_button("➕ Add Script", type="primary")

        if manual_submit and manual_script_name:
            new_entry = {
                'script': manual_script_name,
                'location': manual_script_location,
                'component_ids': manual_components,
                'last_modified': datetime.now().strftime('%Y-%m-%d'),
                'language': manual_script_language
            }

            project_data['code_repository'].append(new_entry)
            save_project_toml(selected_project_path, project_data)
            st.success(f"✅ Added {manual_script_name} to inventory")
            st.rerun()

# ============================================================================
# TAB 4: OUTPUT TRACKING
# ============================================================================

with tab4:
    st.header("📊 Output Tracking & Verification")

    st.markdown("""
    This tab shows the expected outputs for each component and verifies if they exist.
    Helps identify which analyses have been completed and which are pending.
    """)

    # Component selector
    component_to_check = st.selectbox(
        "Select Component to Check Outputs",
        options=[c['name'] for c in project_data['components']],
        key="output_check_component"
    )

    # Find the component
    comp_idx = next(i for i, c in enumerate(project_data['components']) if c['name'] == component_to_check)
    component = project_data['components'][comp_idx]

    st.markdown(f"### {component['name']}")
    st.markdown(f"**Status:** {component['status']} | **Progress:** {component.get('progress_fraction', 0)*100:.0f}%")

    # Check outputs
    project_dir_path = selected_project_path.parent
    output_status = check_component_outputs(component, project_dir_path)

    # Display summary
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Outputs", output_status['total'])
    with col2:
        st.metric("Completed", output_status['completed'])
    with col3:
        if output_status['completion_percentage'] is not None:
            st.metric("Completion", f"{output_status['completion_percentage']:.0f}%")
        else:
            st.metric("Completion", "N/A (cloud storage)")

    # Display individual outputs
    st.markdown("---")
    st.subheader("📁 Output Files")

    if output_status['outputs']:
        for idx, output in enumerate(output_status['outputs']):
            status_icon = "✅" if output['exists'] else "❌" if output['exists'] is False else "☁️"

            with st.expander(f"{status_icon} {output['location']}", expanded=(not output['exists'] and output['type'] != 'cloud')):
                st.markdown(f"**Type:** {output['type']}")
                st.markdown(f"**Location:** `{output['location']}`")

                if output['type'] == 'cloud':
                    st.info("☁️ Cloud storage - cannot verify from local environment")
                elif output['exists']:
                    st.success("✅ File exists")
                    st.markdown(f"**Expected creation date:** {output.get('created_date', 'N/A')}")
                else:
                    st.error("❌ File not found")
                    st.markdown("This output is expected but does not exist yet.")
    else:
        st.info("No outputs defined for this component")

    # Bulk output check across all components
    st.markdown("---")
    st.subheader("📊 All Components Output Summary")

    if st.button("🔄 Check All Component Outputs", type="primary"):
        all_component_status = []

        for comp in project_data['components']:
            output_check = check_component_outputs(comp, project_dir_path)

            all_component_status.append({
                'Component': comp['name'],
                'Status': comp['status'],
                'Total Outputs': output_check['total'],
                'Completed Outputs': output_check['completed'],
                'Completion %': f"{output_check['completion_percentage']:.0f}%" if output_check['completion_percentage'] is not None else 'N/A'
            })

        df_outputs = pd.DataFrame(all_component_status)
        st.dataframe(df_outputs, use_container_width=True, hide_index=True)

# ============================================================================
# TAB 5: CLIENT SUMMARY
# ============================================================================

with tab5:
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
# TAB 6: REPORT BUILDER
# ============================================================================

with tab6:
    st.header("📄 Analysis Report Builder")

    st.markdown("""
    Generate a comprehensive analysis report based on project components, scripts, and deliverables.
    This report follows the structure defined in `ANALYSIS_REPORT_PROMPT_TEMPLATE.md`.
    """)

    st.markdown("---")

    # Report configuration section
    st.subheader("📋 Report Configuration")

    col1, col2 = st.columns(2)

    with col1:
        include_scripts = st.checkbox("Include Script Inventory", value=True, key="report_include_scripts")
        include_outputs = st.checkbox("Include Component Deliverables", value=True, key="report_include_outputs")

    with col2:
        filter_components = st.checkbox("Select Specific Components", value=False, key="report_filter_components")

    # Component selection if filter is enabled
    selected_component_ids = None
    if filter_components:
        st.markdown("**Select Components to Include:**")

        # Group components by status for easier selection
        status_groups = {'completed': [], 'in_progress': [], 'not_started': [], 'blocked': []}
        for comp in project_data['components']:
            status_groups[comp['status']].append(comp)

        selected_component_ids = []

        # Completed components
        if status_groups['completed']:
            st.markdown("**✅ Completed Components:**")
            for comp in status_groups['completed']:
                if st.checkbox(f"{comp['name']}", value=True, key=f"report_comp_{comp['component_id']}"):
                    selected_component_ids.append(comp['component_id'])

        # In progress components
        if status_groups['in_progress']:
            st.markdown("**🔄 In Progress Components:**")
            for comp in status_groups['in_progress']:
                if st.checkbox(f"{comp['name']}", value=False, key=f"report_comp_{comp['component_id']}"):
                    selected_component_ids.append(comp['component_id'])

    st.markdown("---")

    # Generate report button
    if st.button("🔨 Generate Report", type="primary"):
        with st.spinner("Generating report..."):
            report_content = generate_analysis_report(
                project_data,
                selected_components=selected_component_ids,
                include_scripts=include_scripts,
                include_outputs=include_outputs
            )

            # Store in session state for preview
            st.session_state['generated_report'] = report_content
            st.success("✅ Report generated successfully!")

    # Display report preview if exists
    if 'generated_report' in st.session_state and st.session_state['generated_report']:
        st.markdown("---")
        st.subheader("📖 Report Preview")

        # Preview in expander
        with st.expander("View Full Report", expanded=False):
            st.markdown(st.session_state['generated_report'])

        # Download buttons
        col1, col2 = st.columns(2)

        with col1:
            st.download_button(
                label="📥 Download as Markdown (.md)",
                data=st.session_state['generated_report'],
                file_name=f"{project_data['project_id']}_Analysis_Report_{datetime.now().strftime('%Y%m%d')}.md",
                mime="text/markdown",
                key="download_report_md"
            )

        with col2:
            # Info about converting to Word
            st.info("💡 Convert to Word with: `pandoc report.md -o report.docx --toc --toc-depth=2`")

        # Clear report button
        if st.button("🗑️ Clear Report", key="clear_report"):
            del st.session_state['generated_report']
            st.rerun()

        st.markdown("---")

        # Report editing tips
        with st.expander("✏️ Report Editing Guide"):
            st.markdown("""
            ### Next Steps:

            1. **Download the markdown file** using the button above
            2. **Edit in your preferred editor** (VS Code, Typora, etc.)
            3. **Fill in placeholder sections** marked with `[TO BE FILLED:]`
            4. **Add figures** by replacing `[INSERT FIGURE X HERE]` with actual figure paths
            5. **Update results tables** with actual data from analysis outputs
            6. **Review and refine** executive summary and conclusions

            ### Placeholder Sections to Complete:

            - Executive Summary
            - Key Findings (3-5 bullet points)
            - Results sections with actual data and figures
            - Statistical test results in tables
            - Figure legends with sample sizes and p-values
            - Conclusions and limitations
            - Methods summary

            ### Converting to Word:

            ```bash
            pandoc report.md -o report.docx --toc --toc-depth=2 --reference-doc=template.docx
            ```

            ### Converting to PDF:

            ```bash
            pandoc report.md -o report.pdf --toc --toc-depth=2
            ```
            """)

# ============================================================================
# TAB 7: ADD NEW COMPONENT
# ============================================================================

with tab7:
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
