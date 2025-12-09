# Known Pain Points

A running list of issues and friction points in the current pipeline. This drives prioritization for future improvements.

## Technical

### Segmentation Issues

1. **GPU Memory Errors (OOM)**
   - Large images (>8192×8192) cause CUDA out-of-memory errors
   - Requires manual tile-based processing with overlap handling
   - No automated tile stitching currently
   - See: [deepcell_mesmer_errors.md](../troubleshooting/deepcell_mesmer_errors.md)

2. **"Exploding Cells" Artifact**
   - Mesmer occasionally produces massive segmentation regions (>100µm)
   - Requires manual QC review and filtering
   - No automated detection/removal currently

3. **Over-segmentation of Large Cells**
   - Epithelial/tumor cells split into multiple segments
   - Requires manual parameter tuning per tissue type
   - No standard tissue-specific parameter sets

4. **Inconsistent Segmentation Across Batches**
   - Environment drift between analysts
   - Different Mesmer versions produce different results
   - Mitigation: version-locked environments, but still requires enforcement

### Phenotyping Issues

5. **Threshold Sensitivity**
   - Small changes in threshold values dramatically change phenotype assignments
   - No automated threshold selection method
   - Relies on manual positive control validation
   - **Example:** CD45 threshold shifts can change immune cell fraction from 80% to 90%

6. **Memory Issues with Large Datasets**
   - 100,000+ cells with 36+ markers causes memory errors
   - Requires chunked processing (5000 cells per chunk)
   - Manual concatenation of chunks
   - Parquet format helps but not standardized

7. **Conflicting Marker Combinations**
   - Cells positive for mutually exclusive markers (e.g., CD4+ CD8+)
   - Current tie-breaking: use intensity-based rules
   - No standard handling across projects

8. **Batch Effects in Phenotyping**
   - Different staining batches show shifted intensity distributions
   - Requires batch-specific threshold calibration (not ideal)
   - Harmony/Combat batch correction helps but not always sufficient

9. **Missing or Corrupted Intensity Values**
   - NaN or zero values in marker intensity columns
   - Current handling: exclude cells with >3 missing markers
   - Requires investigation of upstream segmentation issues

10. **Inconsistent Marker Naming**
    - Different projects use different naming conventions (spaces, underscores, capitalization)
    - Example: `CD8 Mean` vs `CD8_mean` vs `cd8_Mean`
    - Requires manual rename mapping at data loading

### Spatial Analysis Issues

11. **Coordinate System Inconsistencies**
    - X/Y coordinates may be in different units (pixels vs microns)
    - Axes may be flipped or rotated without documentation
    - Requires manual verification and correction per project

12. **Edge Effects in Spatial Analysis**
    - Cells near tissue boundaries have incomplete neighborhoods
    - Current mitigation: exclude edge cells (e.g., within 50µm of boundary)
    - Loses data, especially in small ROIs

13. **Rare Cell Type Analysis**
    - Insufficient cells of rare phenotypes for meaningful spatial statistics
    - No standard minimum cell count threshold enforced
    - Example: NK cells in some lymph node regions (<20 cells)

14. **Radius Selection for Neighborhood Analysis**
    - No universal "correct" radius
    - Results sensitive to choice (30µm vs 100µm gives different conclusions)
    - Current practice: test multiple radii, but time-consuming

15. **Multiple Testing Correction**
    - Testing many cell type pairs inflates false positives
    - FDR correction helps but conservative
    - Example: 36 phenotypes = 1,260 pairwise tests

16. **Computational Performance with Large Datasets**
    - 100,000+ cells causes slow spatial analysis (hours)
    - KD-tree indexing helps but not always used
    - Parallel processing across regions not standardized

17. **SCIMAP vs Squidpy Differences**
    - Different tools give slightly different results
    - SCIMAP: radius-based, z-score permutation testing
    - Squidpy: k-NN based, different enrichment calculation
    - No clear decision rules on which to use when

### Infrastructure & Environment Issues

18. **Environment Drift Between Analysts**
    - Despite version-locked environments, analysts sometimes install additional packages
    - Breaks reproducibility
    - Requires periodic environment audits

19. **GCP VM Access Issues**
    - SSH connection failures
    - IAP tunneling complexity
    - Frequent authentication re-requirements
    - See: [gcp_ssh_issues.md](../troubleshooting/gcp_ssh_issues.md), [ssh_issues.md](../troubleshooting/ssh_issues.md)

20. **Git Branching Confusion**
    - Analysts unclear on when to branch vs commit to main
    - Merge conflicts in notebook outputs
    - See: [git_branching_issues.md](../troubleshooting/git_branching_issues.md)

### Data Format & Schema Issues

21. **Inconsistent Cell Table Schemas Across Projects**
    - Different column names for same information
    - Example: `Centroid X µm` vs `X_centroid` vs `X` vs `Centroid_X_um`
    - Requires project-specific code modifications

22. **OME-TIFF Metadata Parsing**
    - Channel names not always reliably extracted
    - Physical units (mpp) sometimes missing or incorrect
    - Requires manual inspection and documentation

23. **Segmentation Mask Format Variations**
    - Some masks are 8-bit, some 16-bit, some 32-bit
    - Label ID conflicts when merging multiple regions
    - QuPath import compatibility issues with certain formats

## Operational

### Workflow & Handoff Issues

24. **Unclear Handoff Between Segmentation and Analysis**
    - No standard "Definition of Done" for segmentation historically
    - Analysts unclear on what QC checks are required
    - Recent SOPs address this, but enforcement needed

25. **Results Stored in Multiple Locations**
    - Local machines, GCP VMs, Google Drive, ClickUp attachments
    - Difficult to find "ground truth" version of analysis
    - No centralized project data repository

26. **Lack of Standard QC Checkpoints**
    - QC historically performed inconsistently
    - No automated QC report generation
    - Recent SOPs define QC criteria, but manual enforcement

27. **No Automated Pipeline Execution**
    - All steps manual (segmentation → phenotyping → spatial analysis)
    - High risk of human error (wrong file paths, skipped steps)
    - No workflow orchestration (Snakemake, Nextflow, etc.)

### Documentation & Knowledge Management

28. **Troubleshooting Knowledge Not Centralized**
    - Historically: issues documented in Slack threads, email, or not at all
    - New KB structure addresses this, but requires discipline to update
    - Rule: "If you troubleshoot something non-trivial, you update the KB" - enforcement needed

29. **Parameter Choices Not Recorded**
    - Historically: segmentation parameters, thresholds, radii not consistently logged
    - Makes reproduction difficult months later
    - Recent emphasis on `metadata.json` helps, but adoption incomplete

30. **No Standard Project Folder Structure (Historical)**
    - Different projects organized differently
    - Difficult to find segmentation masks, QC plots, exports
    - Recent standardization (raw/, segmentation/, phenotyping/, spatial/) helps new projects

### Communication & Collaboration Issues

31. **Definition of Done Not Enforced**
    - Tickets marked "Done" without required outputs (logs, QC, KB entry)
    - Recent README.md rules address this, but cultural shift needed

32. **Weekly KB Review Not Happening Consistently**
    - Team syncs don't always include "What did we add to the KB this week?"
    - Indicates documentation discipline gaps

33. **Analyst-Specific Approaches**
    - Different analysts use different methods for same task
    - Example: Some use SCIMAP, some use Squidpy, some use custom code
    - Standardization difficult due to project-specific requirements

### Client & External Issues

34. **Inconsistent Data Delivery from Clients**
    - Some provide OME-TIFFs, some provide raw CZI/QPTIFF
    - Channel definitions sometimes missing or incorrect
    - Physical calibration (mpp) sometimes absent

35. **Changing Analysis Requirements Mid-Project**
    - Clients request additional phenotypes or spatial metrics after initial analysis
    - Requires re-running large portions of pipeline
    - No version control for analysis outputs

36. **No Standardized Deliverable Format**
    - Different clients receive different report formats
    - Some want CSVs, some want h5ad files, some want PowerPoint
    - No templated report generation

## High-Priority Improvements

Based on frequency and impact, these should be addressed first:

### Critical (Blocking work regularly)
1. **Automate tile-based segmentation** with overlap handling
2. **Standardize cell table schemas** across all projects
3. **Create tissue-specific parameter sets** (segmentation, phenotyping thresholds)
4. **Centralize project data repository** (structured storage)

### High (Significant time sink)
5. **Implement automated QC report generation** (segmentation, phenotyping, spatial)
6. **Develop threshold auto-selection** using positive/negative control regions
7. **Build spatial analysis dashboard** for exploration and result review
8. **Standardize deliverable formats** with templated reports

### Medium (Quality of life)
9. **Improve GCP VM access** (better documentation, IAP wrapper scripts)
10. **Create git workflow guide** for analysts (when to branch, how to merge notebooks)
11. **Develop environment audit tools** (check for package drift)
12. **Build validation datasets** (ground truth for segmentation accuracy)

> Add items here as they are discovered in day-to-day work.
> Cross-reference with troubleshooting KB entries for detailed solutions.
