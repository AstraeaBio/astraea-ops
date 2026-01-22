# Analysis Report Generation Prompt Template

**Purpose:** Standardized prompt for generating comprehensive analysis reports and documentation across projects.

**Usage:** Copy the prompt below and customize the bracketed sections for your specific project.

---

## The Prompt

```
I need help creating a comprehensive analysis report and documentation package for a project. Please follow this standardized structure:

## Project Context

**Project Name:** [PROJECT_NAME]
**Analysis Type:** [e.g., multiplex immunofluorescence, RNA-seq, proteomics, clinical data analysis]
**Primary Question:** [Main research question or objective]
**Data Sources:** [List input data files and locations]
**Output Location:** [Where to save results]

## Key Variables

**Primary Markers/Features:** [List main variables being analyzed]
**Outcome Variables:** [What you're trying to predict or correlate with]
**Sample Groups:** [e.g., Hot/Cold, Responder/Non-responder, Treatment/Control]
**Sample Size:** [Number of samples, ROIs, patients, etc.]

## Deliverables Requested

Please create the following standardized documentation package:

### 1. Main Analysis Report (`[PROJECT]_Analysis_Report.md`)

Structure the report with:
- Executive Summary (key findings, 1-2 paragraphs)
- Key Findings (numbered list, 3-5 bullet points)
- Study Design (introduction, sample characteristics, methodology)
- Results sections (organized by analysis type)
- Integrated Analysis (if multiple analysis approaches)
- Conclusions (primary conclusions, clinical/practical implications, limitations)
- Future Directions

For each results section include:
- Clear section numbering (1, 1.1, 1.1.1)
- Tables with statistical results (include p-values and significance indicators)
- Figure placeholders in format: `**[INSERT FIGURE X HERE]**` followed by figure legend
- Explicit statements about what IS and IS NOT statistically significant

### 2. Figures and Outputs Appendix (`FIGURES_AND_OUTPUTS_APPENDIX.md`)

Include:
- Inventory of all generated figures with descriptions
- Data tables listing with contents
- Figure recommendations for publication (main vs supplementary)
- Key statistics summary table with significance column

### 3. Pipeline Documentation (`PIPELINE_DOCUMENTATION.md`)

For each analysis script, document:
- Purpose (1-2 sentences)
- Usage (command line example)
- Inputs (file paths, formats)
- Outputs (files generated, locations)
- Key parameters/configuration
- Critical code sections (if applicable)
- Reusability rating (High/Medium/Low) and adaptation notes

Include:
- Pipeline overview diagram (ASCII or description)
- Data flow from inputs to outputs
- Dependencies list
- Quick reference for running full pipeline

### 4. Development Notes (`DEVELOPMENT_NOTES.md`)

Track:
- Bug fixes with issue/resolution/impact
- Major analytical decisions with rationale
- Interpretation changes or corrections
- Figure development iterations
- Key reference values (correlations, p-values, etc.)
- Lessons learned
- Files modified during analysis

### 5. Project Context File (`CLAUDE.md`)

Create a quick-reference file with:
- Project overview (2-3 sentences)
- Key findings (bullet points)
- Data locations table
- Key files index
- Sample/group classifications
- Important notes (bugs fixed, threshold definitions, etc.)
- Common commands for running analysis
- Documentation index

### 6. Markdown Report Guide (`MARKDOWN_REPORT_GUIDE.md`)

If not already present in the project, create or link to standard guide for:
- Document structure template
- Markdown formatting reference
- Figure placeholder format
- Table formatting best practices
- Pandoc conversion commands
- Word template customization

## Formatting Standards

### Tables
- Always include header row with clear column names
- Right-align numeric values
- Include units in headers where applicable
- Bold significant results
- Add "Significant?" column for statistical tests

Example:
| Analysis | AUC/r | Direction | p-value | n | Significant? |
|----------|-------|-----------|---------|---|--------------|
| Primary analysis | **0.60** | Up in Group A | **<0.001** | 100 | **Yes** |
| Secondary analysis | 0.52 | ns | 0.34 | 100 | No |

### Figure Placeholders
```markdown
---

**[INSERT FIGURE X HERE]**

**Figure X: Descriptive Title.** Detailed caption explaining the figure, including sample sizes (n=X), statistical tests used, and significance levels. Define abbreviations on first use.

---
```

### Statistical Reporting
- Always report exact p-values (not just < or >)
- Clearly distinguish significant findings from trends
- Include effect sizes where appropriate (r, AUC, fold change)
- Report sample sizes for all analyses

### Section Numbering
Use hierarchical numbering:
- # 1. Main Section
- ## 1.1 Subsection
- ### 1.1.1 Sub-subsection

## Quality Checks

Before finalizing, verify:
- [ ] All p-values reported with significance clearly stated
- [ ] No over-interpretation of non-significant trends
- [ ] Figure placeholders have complete legends
- [ ] All scripts documented with inputs/outputs
- [ ] Sample sizes stated for all analyses
- [ ] Limitations section addresses key caveats
- [ ] CLAUDE.md provides accurate quick reference
- [ ] Development notes capture key decisions

## Conversion

After markdown files are complete:
```bash
pandoc [PROJECT]_Analysis_Report.md -o [PROJECT]_Analysis_Report.docx --toc --toc-depth=2
```
```

---

## Customization Checklist

When using this prompt for a new project, customize:

- [ ] Project name and type
- [ ] Primary research question
- [ ] Data source locations
- [ ] Output directory
- [ ] Key markers/variables
- [ ] Outcome measures
- [ ] Sample groupings
- [ ] Sample sizes
- [ ] Any project-specific sections needed

---

## Example: Filled Template for Oncology IF Project

```
## Project Context

**Project Name:** TumorX PD-L1 Expression Analysis
**Analysis Type:** Multiplex immunofluorescence from QuPath
**Primary Question:** Does PD-L1 expression on tumor cells predict response to immunotherapy?
**Data Sources:**
- H-scores: `T:\Analysis\TumorX\HScores\`
- Cell counts: `T:\Analysis\TumorX\Exports\`
**Output Location:** `D:\TumorX\Exports\`

## Key Variables

**Primary Markers/Features:** PD-L1, CD8, CD68, FoxP3
**Outcome Variables:** Treatment response (Responder/Non-responder), PFS
**Sample Groups:** Responder (n=25), Non-responder (n=30)
**Sample Size:** 55 patients, ~500 ROIs total

[Continue with Deliverables Requested section...]
```

---

## File Naming Conventions

| File Type | Naming Pattern | Example |
|-----------|----------------|---------|
| Main report | `[PROJECT]_Analysis_Report.md` | `TumorX_Analysis_Report.md` |
| Appendix | `FIGURES_AND_OUTPUTS_APPENDIX.md` | (standard name) |
| Pipeline docs | `PIPELINE_DOCUMENTATION.md` | (standard name) |
| Dev notes | `DEVELOPMENT_NOTES.md` | (standard name) |
| Context | `CLAUDE.md` | (standard name) |
| Report guide | `MARKDOWN_REPORT_GUIDE.md` | (standard name) |
| Analysis scripts | `[analysis_type]_analysis.py` | `response_prediction_analysis.py` |
| Figure scripts | `create_[figure_type]_figure.py` | `create_survival_figure.py` |

---

## Output Directory Structure Template

```
project/
├── CLAUDE.md                          # Project context (quick reference)
├── DEVELOPMENT_NOTES.md               # Decision record
├── PIPELINE_DOCUMENTATION.md          # Script documentation
├── MARKDOWN_REPORT_GUIDE.md           # Report preparation guide
├── [PROJECT]_Analysis_Report.md       # Main report
├── FIGURES_AND_OUTPUTS_APPENDIX.md    # Figure/output inventory
│
├── scripts/                           # Analysis scripts (or in root)
│   ├── primary_analysis.py
│   ├── secondary_analysis.py
│   └── create_figures.py
│
└── Exports/                           # All outputs
    ├── primary_analysis/
    │   ├── figures/
    │   └── tables/
    ├── secondary_analysis/
    │   ├── figures/
    │   └── tables/
    └── Final_figures_for_report/
        ├── Figure_1.png
        ├── Figure_2.png
        └── FIGURE_LEGENDS.md
```

---

*Template version: 1.0 | Created: January 2026 | Based on 7Hills Melanoma ICAM/VCAM Analysis Project*
