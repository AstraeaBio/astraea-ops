# TIFF Inspector Integration Notes

## Overview

This document describes the integration of TIFF Inspector tools into the astraea-ops knowledge base.

## Date Integrated

2026-01-12

## Files Added

### Tools (`tools/tiff-inspector/`)
- `inspect_tiff.py` - General TIFF file inspector
- `diagnose_channels.py` - Multi-channel TIFF diagnostic tool
- `extract_channels.py` - Channel extraction and cleaning tool
- `requirements.txt` - Python dependencies
- `README.md` - Complete tool documentation
- `examples/` - Example usage directory (empty, for future)
- `docs/` - Additional documentation directory (empty, for future)

### Documentation (`docs/troubleshooting/`)
- `tiff_file_issues.md` - Comprehensive TIFF troubleshooting guide

### Updates to Existing Files
- `docs/troubleshooting/qupath_common_errors.md` - Added reference to TIFF Inspector tools
- `README.md` - Ready to add TIFF Inspector section (see `tiff_inspector_section.txt`)

## Integration Steps Completed

1. ✓ Created `tools/tiff-inspector/` directory structure
2. ✓ Refactored scripts from original implementation to be generic:
   - Removed hard-coded file paths
   - Added comprehensive CLI arguments
   - Added proper error handling
   - Made output directories configurable
3. ✓ Created comprehensive tool documentation (README.md)
4. ✓ Created Python requirements.txt
5. ✓ Created TIFF File Issues troubleshooting guide
6. ✓ Updated QuPath errors doc to reference TIFF tools
7. ⚠️ Main README update prepared (manual insertion needed)

## Manual Steps Remaining

### 1. Update Main README

Insert the content from `tiff_inspector_section.txt` into the main `README.md` after the "Analysis Architect" section and before "Future Tools".

```bash
# Location: T:/0_Organizational/astraea-ops/README.md
# Insert after line 49 (after Analysis Architect documentation links)
# Content is in: T:/0_Organizational/astraea-ops/tiff_inspector_section.txt
```

### 2. Update Repository Structure Diagram

Update the repository structure in main README to include:

```
astraea-ops/
├── docs/
│   └── troubleshooting/
│       ├── qupath_common_errors.md
│       └── tiff_file_issues.md       # NEW
├── tools/
│   ├── analysis-architect/
│   └── tiff-inspector/                # NEW
├── projects/
├── requirements.txt
└── README.md
```

### 3. Test Installation

```bash
cd tools/tiff-inspector
pip install -r requirements.txt

# Test with example file
python inspect_tiff.py <path-to-tiff> --metadata-only
```

### 4. Update Global Requirements (Optional)

If desired, add tifffile dependencies to root `requirements.txt`:

```txt
# Add to root requirements.txt
numpy>=1.20.0
tifffile>=2021.0.0
imagecodecs>=2021.0.0
```

## Usage Examples for KB

### Case Study 1: 30-plex Missing Frames

**Problem:** 107GB OME-TIFF won't open in QuPath, error says "missing 12 frames"

**Solution:**
```bash
cd tools/tiff-inspector

# Step 1: Diagnose
python diagnose_channels.py sample.tiff --output-dir ./diagnosis

# Step 2: Extract valid channels
python extract_channels.py sample.tiff \
    --create-cleaned \
    --output sample_fixed.tiff

# Step 3: Open sample_fixed.tiff in QuPath
```

**KB Entry:** See `docs/troubleshooting/tiff_file_issues.md` - Real-World Example section

### Case Study 2: Verify File After Transfer

**Problem:** Need to verify 150GB file transferred correctly

**Solution:**
```bash
python tools/tiff-inspector/inspect_tiff.py transferred_file.tiff \
    --metadata-only \
    --save-ome \
    --output-dir ./validation
```

## Git Commit Message

```
feat: Add TIFF Inspector toolkit to astraea-ops

Add comprehensive TIFF file diagnostic and repair tools to operations toolkit:

Tools added:
- inspect_tiff.py: Memory-efficient TIFF inspection
- diagnose_channels.py: Multi-channel structure diagnostic
- extract_channels.py: Channel extraction and file repair

Documentation added:
- tools/tiff-inspector/README.md: Complete tool documentation
- docs/troubleshooting/tiff_file_issues.md: TIFF troubleshooting guide

Updates:
- docs/troubleshooting/qupath_common_errors.md: Reference to new TIFF tools

These tools address common issues with large (50GB+) microscopy TIFF files
that fail to open in QuPath due to corruption, missing frames, or metadata
mismatches.

Related KB entry: docs/troubleshooting/tiff_file_issues.md
```

## Testing Checklist

Before committing to repository:

- [ ] Test `inspect_tiff.py` with valid TIFF file
- [ ] Test `diagnose_channels.py` with multi-channel file
- [ ] Test `extract_channels.py` channel extraction
- [ ] Verify all documentation links work
- [ ] Check Python imports work correctly
- [ ] Test on both Windows and Linux (if applicable)
- [ ] Verify output files are created correctly
- [ ] Test with corrupted/incomplete file

## Future Enhancements

Potential additions to the toolkit:

1. **Format conversion tool**: Convert between TIFF formats (OME-TIFF, pyramidal, etc.)
2. **Batch processing**: Process multiple files in parallel
3. **Web interface**: Upload and diagnose files via browser
4. **Integration with GCP**: Direct processing of files in cloud storage
5. **Automated repair**: Attempt to fix common issues automatically
6. **Comparison tool**: Compare two TIFF files for differences

## Contact

Questions or issues with TIFF Inspector tools:
- See: `docs/troubleshooting/tiff_file_issues.md`
- Update KB with new cases encountered
- Follow the astraea-ops KB update rules

## Original Implementation Source

These tools were developed to address issues with:
- File: `20251212_192423_1_bopYhG_20251212_Mahesh_full panel 30plex_71054 57034-8ET1.tiff`
- Problem: 107GB OME-TIFF with 12 missing frames, wouldn't open in QuPath
- Original scripts location: `T:/Data/128_Hesham_Amin/`

The original implementation has been refactored for general use and integrated into the astraea-ops knowledge base per KB update rules.
