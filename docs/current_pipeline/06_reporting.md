# Stage 6 — Reporting & Delivery

This document describes how this stage is **currently** performed across projects.

## Objectives

- Synthesize analysis results into client-facing deliverables
- Create publication-quality figures and visualizations
- Generate summary tables and statistical reports
- Document methods and parameters for reproducibility
- Package and deliver all outputs in organized format
- Ensure results are version-controlled and archived appropriately
- Communicate key findings and interpretations to clients

## Common Inputs

### Input File Types and Formats

1. **From phenotyping stage:**
   - `phenotype_results.csv` - Cell-level measurements with phenotype assignments
   - `phenotype_summary.txt` - Cell type counts and QC metrics
   - `phenotyping/metadata.json` - Thresholds and parameters used

2. **From spatial analysis stage:**
   - `adata_spatial.h5ad` - AnnData object with spatial results
   - `neighborhood_enrichment.csv` - Cell-cell interaction matrices
   - `spatial_analysis_results.csv` - Enriched cell table with clusters, distances
   - `spatial/figures/*.png` - Spatial visualizations
   - `spatial/metadata.json` - Analysis parameters (radius, resolution, methods)

3. **From all stages:**
   - QC reports and visualizations
   - Processing logs
   - Metadata files documenting versions, parameters, decisions

4. **Project documentation:**
   - Analysis plan or statement of work
   - Client communication history
   - Troubleshooting KB entries (if created)

## Current Scripts / Tools

### Primary Tools

1. **Jupyter Notebooks (most common):**
   - Narrative analysis combining code, visualizations, and interpretation
   - Export to HTML or PDF for client delivery
   - Advantage: Reproducible, shows methods alongside results

2. **Python visualization libraries:**
   - **matplotlib/seaborn:** Publication-quality static figures
   - **plotly:** Interactive visualizations
   - **scanpy plotting:** UMAP, heatmaps, dotplots for cell types

3. **Microsoft PowerPoint:**
   - Client-facing slide decks
   - High-level summaries for stakeholder presentations
   - Often created from notebook figures + additional annotations

4. **Google Docs/Sheets:**
   - Collaborative report writing
   - Summary tables shared with clients
   - Project tracking and communication logs

5. **ClickUp attachments:**
   - Deliver final reports via ClickUp task
   - Archive project outputs in ClickUp folders
   - Most common delivery mechanism currently

### Script Catalog Links

- [generate_summary_report.md](../scripts_catalog/reporting/generate_summary_report.md) - Automated report generation
- [create_figure_panels.md](../scripts_catalog/reporting/create_figure_panels.md) - Multi-panel figure creation
- [export_results_tables.md](../scripts_catalog/reporting/export_results_tables.md) - Formatted Excel/CSV exports

## Manual Steps

### Typical Analyst Workflow

#### 1. Review Analysis Results and Identify Key Findings

**Questions to answer:**
- What are the major cell populations present?
- Are there significant differences between conditions (if applicable)?
- What spatial patterns or interactions were detected?
- Do results match biological expectations?
- What unexpected findings emerged?

**Example from Nguyen Lab lymph node project:**
- Key finding: Dendritic cell neighborhoods showed significant enrichment for T cells and macrophages post-reperfusion
- Supporting evidence: DC-T cell distances decreased (85µm → 68µm, p < 0.01)
- Biological interpretation: Enhanced immune surveillance after organ transplant

#### 2. Create Summary Figures

**Standard figure panels:**

**A. Phenotype Distribution**
```python
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load phenotyped cells
cells = pd.read_csv('phenotyping/exports/phenotype_results.csv')

# Phenotype counts
phenotype_counts = cells['Level_4'].value_counts()

# Barplot
fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(x=phenotype_counts.values, y=phenotype_counts.index, ax=ax)
ax.set_xlabel('Cell Count')
ax.set_ylabel('Phenotype')
ax.set_title('Cell Type Distribution')
plt.tight_layout()
plt.savefig('reports/figures/phenotype_distribution.png', dpi=300)
```

**B. Spatial Distribution Map**
```python
# Spatial scatter colored by phenotype
fig, ax = plt.subplots(figsize=(12, 10))
for pheno in cells['Level_4'].unique():
    subset = cells[cells['Level_4'] == pheno]
    ax.scatter(subset['Centroid X µm'], subset['Centroid Y µm'],
               label=pheno, s=5, alpha=0.7)
ax.legend(bbox_to_anchor=(1.05, 1), fontsize=8)
ax.set_xlabel('X (µm)')
ax.set_ylabel('Y (µm)')
ax.set_title('Spatial Distribution of Cell Types')
plt.tight_layout()
plt.savefig('reports/figures/spatial_map.png', dpi=300)
```

**C. Neighborhood Enrichment Heatmap**
```python
import anndata as ad

# Load spatial results
adata = ad.read_h5ad('spatial/exports/adata_spatial.h5ad')

# Plot neighborhood enrichment
interaction_matrix = adata.uns['spatial_interaction']
fig, ax = plt.subplots(figsize=(12, 10))
sns.heatmap(interaction_matrix, cmap='RdBu_r', center=0, ax=ax,
            cbar_kws={'label': 'Z-score'}, square=True)
ax.set_title('Spatial Interaction Enrichment')
plt.tight_layout()
plt.savefig('reports/figures/neighborhood_enrichment.png', dpi=300)
```

**D. Statistical Comparisons (if applicable)**
```python
# Example: Pre vs Post treatment comparison
import scipy.stats as stats

pre_cells = cells[cells['Condition'] == 'Pre']
post_cells = cells[cells['Condition'] == 'Post']

# Compare phenotype proportions
comparisons = []
for pheno in cells['Level_4'].unique():
    pre_prop = (pre_cells['Level_4'] == pheno).sum() / len(pre_cells) * 100
    post_prop = (post_cells['Level_4'] == pheno).sum() / len(post_cells) * 100

    # Chi-square test
    contingency = [[
        (pre_cells['Level_4'] == pheno).sum(),
        (pre_cells['Level_4'] != pheno).sum()
    ], [
        (post_cells['Level_4'] == pheno).sum(),
        (post_cells['Level_4'] != pheno).sum()
    ]]
    chi2, pval = stats.chi2_contingency(contingency)[:2]

    comparisons.append({
        'Phenotype': pheno,
        'Pre_%': pre_prop,
        'Post_%': post_prop,
        'Fold_Change': post_prop / pre_prop if pre_prop > 0 else None,
        'P_Value': pval
    })

comp_df = pd.DataFrame(comparisons)
comp_df.to_csv('reports/tables/phenotype_comparisons.csv', index=False)

# Volcano plot
fig, ax = plt.subplots(figsize=(8, 6))
ax.scatter(comp_df['Fold_Change'], -np.log10(comp_df['P_Value']))
ax.axhline(-np.log10(0.05), color='red', linestyle='--', label='p=0.05')
ax.set_xlabel('Fold Change (Post / Pre)')
ax.set_ylabel('-log10(P Value)')
ax.set_title('Phenotype Proportion Changes')
plt.tight_layout()
plt.savefig('reports/figures/volcano_plot.png', dpi=300)
```

#### 3. Generate Summary Tables

**Standard tables:**

**Table 1: Sample Overview**
```python
sample_summary = cells.groupby('Sample_ID').agg({
    'Cell_ID': 'count',
    'Level_4': lambda x: x.nunique()
}).rename(columns={'Cell_ID': 'Total_Cells', 'Level_4': 'Phenotypes_Detected'})

sample_summary.to_excel('reports/tables/sample_summary.xlsx')
```

**Table 2: Phenotype Proportions**
```python
# Proportions per sample
phenotype_props = cells.groupby(['Sample_ID', 'Level_4']).size().unstack(fill_value=0)
phenotype_props = phenotype_props.div(phenotype_props.sum(axis=1), axis=0) * 100
phenotype_props.to_excel('reports/tables/phenotype_proportions.xlsx')
```

**Table 3: Spatial Metrics Summary**
```python
spatial_summary = pd.read_csv('spatial/exports/spatial_analysis_results.csv')

# Example: Mean distances by phenotype pair
distance_summary = spatial_summary.groupby(['Phenotype_A', 'Phenotype_B']).agg({
    'Distance_um': ['mean', 'std', 'median']
})
distance_summary.to_excel('reports/tables/spatial_distances.xlsx')
```

#### 4. Write Methods Section

**Template:**

```markdown
## Methods

### Image Acquisition
- **Platform:** [CODEX/PhenoCycler/mIF]
- **Tissue type:** [Lymph node/Tumor/etc.]
- **Samples:** N samples from [source]
- **Resolution:** X µm/pixel
- **Channels:** Y markers (see Supplementary Table)

### Cell Segmentation
- **Method:** DeepCell Mesmer v0.12.0
- **Compartment:** Whole-cell segmentation
- **Parameters:** image_mpp=X, tile_size=2048×2048
- **QC:** Manual review of segmentation quality; all samples passed QC
- **Cells detected:** [range] cells per sample

### Feature Extraction
- **Tool:** QuPath v0.4.0
- **Features:** Mean marker intensity per cell, morphological features (area, perimeter)
- **Channels extracted:** [list markers]

### Cell Phenotyping
- **Method:** Hierarchical threshold-based classification
- **Levels:** 4-level hierarchy (Immune vs Epithelial → Cell type → Functional state)
- **Thresholds:** Validated using positive control regions
- **Phenotypes:** 36 refined phenotypes identified
- **QC:** <1% cells unclassified

### Spatial Analysis
- **Tool:** SCIMAP v1.3.0
- **Spatial graph:** Radius-based (60 µm, based on [Nolan et al. reference])
- **Neighborhood enrichment:** Permutation testing (1000 permutations, z-score)
- **Statistical testing:** Mann-Whitney U test for continuous variables, Chi-square for proportions
- **Multiple testing correction:** Benjamini-Hochberg FDR, α=0.05

### Software and Code
- Python 3.9, scimap 1.3.0, squidpy 1.2.0, pandas 1.4.0, numpy 1.22.0
- Analysis code available upon request
```

#### 5. Assemble Final Report

**Report structure (typical):**

```
reports/
  final_report.html           # Main deliverable (Jupyter notebook export)
  figures/
    phenotype_distribution.png
    spatial_map.png
    neighborhood_enrichment.png
    volcano_plot.png
    [additional figures]
  tables/
    sample_summary.xlsx
    phenotype_proportions.xlsx
    spatial_distances.xlsx
    [additional tables]
  data_exports/
    phenotype_results.csv      # Full cell-level data
    adata_spatial.h5ad         # AnnData for further analysis
  methods.md                   # Detailed methods documentation
  README.txt                   # Guide to deliverable contents
```

**README.txt template:**
```
Project: [Project Name]
Client: [Client Name]
Analyst: [Your Name]
Date: [Delivery Date]

CONTENTS:

1. final_report.html
   - Main analysis report with figures, tables, and interpretation
   - Open in web browser

2. figures/
   - Publication-quality figures (300 dpi PNG)
   - Figure legends included in report

3. tables/
   - Summary tables in Excel format
   - Tab-separated CSV versions also provided

4. data_exports/
   - phenotype_results.csv: Full cell-level measurements with phenotypes
   - adata_spatial.h5ad: AnnData object with spatial analysis results (Python/scanpy)

5. methods.md
   - Detailed methods section for publication

ANALYSIS SUMMARY:

[Brief summary of key findings, 3-5 bullet points]

QUESTIONS:

Please contact [email] with any questions or requests for additional analyses.
```

#### 6. Quality Check Before Delivery

**Pre-delivery checklist:**
- [ ] All figures have clear labels, legends, and titles
- [ ] Table columns are clearly named with units where appropriate
- [ ] Methods section accurately describes what was done
- [ ] Key findings are highlighted and interpreted
- [ ] File paths in report are relative (not absolute paths from analyst's machine)
- [ ] All referenced files are included in delivery package
- [ ] README explains contents and how to access data
- [ ] No sensitive internal information (file paths, internal project codes, etc.)
- [ ] Report is formatted consistently (fonts, colors, layout)
- [ ] Statistical tests are appropriate and properly reported (p-values, effect sizes)
- [ ] Figures are publication-quality (high resolution, clear fonts)

#### 7. Deliver via ClickUp

1. Create deliverable package (ZIP file)
2. Upload to ClickUp task
3. Update task status to "Ready for Client Review"
4. Notify client via email or ClickUp comment
5. Archive copy in project folder on GCP/local storage

## Variations Between Projects

### By Client Type

**Academic collaborators:**
- Prefer Jupyter notebooks (HTML export) - shows methods and code
- Want raw data exports for follow-up analyses
- Interested in statistical details
- May request specific figure formats for publication

**Pharma/biotech clients:**
- Prefer PowerPoint slide decks - executive summaries
- Focus on high-level findings and interpretation
- Less interest in methods details
- May have specific deliverable templates

**Internal projects:**
- Informal reports (can be shorter)
- Code/notebooks shared directly (don't need HTML export)
- Focus on actionable insights for next steps

### By Analysis Complexity

**Simple phenotyping projects:**
- Report focused on cell type distributions
- Figures: Barplots, pie charts, spatial maps
- Tables: Counts and proportions
- Can be delivered in 1-2 days after analysis complete

**Comprehensive spatial analysis projects:**
- Extensive report with multiple sections
- Figures: Heatmaps, networks, statistical comparisons, multi-panel figures
- Tables: Interaction matrices, distance metrics, statistical tests
- May take 1-2 weeks to prepare comprehensive report

**Exploratory analyses:**
- Iterative reporting as findings emerge
- Informal updates via ClickUp comments or emails
- Formal report at project conclusion

### By Deliverable Format

**Standard HTML report (most common):**
- Jupyter notebook exported to HTML
- Self-contained, can be viewed in browser
- Good for archiving and sharing

**PowerPoint deck:**
- Client-facing presentations
- High-level summaries with key figures
- Often created in parallel with HTML report

**Interactive dashboards (rare, but requested):**
- Plotly Dash or Streamlit apps
- Allow client to explore data interactively
- Requires hosting and maintenance

**Publication-ready figures:**
- Vector formats (PDF, SVG)
- Multiple panel layouts (Figure 1, Figure 2, etc.)
- Detailed figure legends in separate document

## Known Issues

### 1. Inconsistent Deliverable Formats

**Problem:** Different clients receive different report formats, making it hard to maintain quality standards.

**Current handling:**
- Use Jupyter notebooks as default
- Adapt to client preferences as needed
- No standard template enforced

**Improvement needed:**
- Develop standard report templates (academic, pharma, internal)
- Create style guide for figures and tables

### 2. Figure Quality Issues

**Problem:** Figures created during analysis may not be publication-quality (low resolution, poor fonts, cluttered legends).

**Current handling:**
- Regenerate figures at high resolution for final report
- Manual touch-up in Illustrator if needed

**Improvement needed:**
- Set figure defaults for high-quality output from start
- Create figure style templates

### 3. Methods Documentation Incomplete

**Problem:** Methods section often written hastily at end, may miss important parameters or decisions.

**Current handling:**
- Refer back to metadata.json files and logs
- May need to re-check code for exact parameters used

**Prevention:**
- Document methods as you go, not at the end
- Use metadata.json consistently throughout pipeline

### 4. Deliverable Package Disorganized

**Problem:** Files scattered across multiple directories, unclear naming, missing README.

**Current handling:**
- Manually assemble package at delivery time
- Can be error-prone (forgetting files, including wrong versions)

**Improvement needed:**
- Automated packaging script
- Standard folder structure enforced

### 5. Version Control of Reports

**Problem:** Multiple rounds of client feedback lead to many report versions (report_v1, report_v2_final, report_v2_FINAL_revised, etc.).

**Current handling:**
- Manual version numbering
- Track versions in ClickUp comments
- Can become confusing

**Improvement needed:**
- Git version control for report notebooks
- Clear version numbering scheme
- Change log documenting updates

### 6. Time to Prepare Reports

**Problem:** Report preparation takes longer than expected (1-2 weeks for complex projects).

**Current handling:**
- Rush at end of project
- May delay other projects

**Improvement needed:**
- Start report outline early in project
- Generate figures incrementally, not all at end
- Automated report generation templates

### 7. Client Requests for Additional Analyses After Delivery

**Problem:** Client reviews report and requests new analyses or additional figures.

**Current handling:**
- Re-run analyses, update report, re-deliver
- Can lead to multiple rounds of revisions

**Prevention:**
- Clear scope definition upfront
- Preliminary results review before final report
- Separate "additional analyses" as follow-up projects

## Success Metrics

From recent projects:

**Nguyen Lab lymph node project:**
- **Report format:** Jupyter notebook (HTML export)
- **Figures generated:** 15 (phenotype distributions, spatial maps, heatmaps, statistical comparisons)
- **Tables generated:** 5 (sample summary, phenotype proportions, spatial metrics)
- **Report length:** 25 pages (including figures and tables)
- **Time to prepare:** 1 week after spatial analysis complete
- **Client feedback:** Positive, no revisions requested
- **Follow-up:** 2 additional analyses requested (handled as separate tasks)

**Typical project:**
- **Report format:** HTML + PowerPoint deck
- **Figures:** 8-12
- **Tables:** 3-5
- **Time to prepare:** 3-5 days
- **Revisions:** 1-2 rounds typical

## Next Steps / Improvements Needed

1. **Develop standardized report templates** (academic, pharma, internal formats)
2. **Create figure style guide** with consistent colors, fonts, layouts
3. **Build automated packaging script** to assemble deliverable folders
4. **Implement version control for reports** (git-based workflow)
5. **Create report generation pipeline** (automated figure/table generation from analysis outputs)
6. **Develop interactive dashboard template** for exploratory data delivery
7. **Build deliverable QC checklist** (automated checks for missing files, broken links)
8. **Create client feedback tracker** to manage revision requests systematically
