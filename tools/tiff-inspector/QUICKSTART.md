# TIFF Inspector Quick Start Guide

## Installation

```bash
cd T:/0_Organizational/astraea-ops/tools/tiff-inspector
pip install -r requirements.txt
```

## Basic Usage

### 1. Check if a TIFF file is corrupt

```bash
python inspect_tiff.py "path/to/file.tiff" --metadata-only
```

**What to look for:**
- "File is suspiciously small" = file incomplete/corrupted
- "Successfully opened TIFF file" = file header OK
- "Successfully read test region" = data accessible

### 2. Diagnose multi-channel files

```bash
python diagnose_channels.py "path/to/file.tiff" --output-dir ./diagnosis
```

**What this does:**
- Checks each channel for actual data
- Reports which channels are empty vs populated
- Saves sample data from valid channels
- Extracts OME-XML metadata

### 3. Fix problematic files

```bash
python extract_channels.py "path/to/file.tiff" \
    --create-cleaned \
    --output fixed.tiff
```

**What this does:**
- Identifies channels with valid data
- Creates new TIFF with only valid channels
- Fixes OME metadata to match actual structure
- Optimizes for QuPath compatibility

## Real Example (Your Files)

### For your 107GB problematic TIFF:

```bash
cd T:/0_Organizational/astraea-ops/tools/tiff-inspector

# Step 1: Quick check
python inspect_tiff.py "T:/Data/128_Hesham_Amin/Human_Post_Treatment/20251212_192423_1_bopYhG_20251212_Mahesh_full panel 30plex_71054 57034-8ET1.tiff" --metadata-only

# Step 2: Detailed diagnosis (this may take several minutes)
python diagnose_channels.py "T:/Data/128_Hesham_Amin/Human_Post_Treatment/20251212_192423_1_bopYhG_20251212_Mahesh_full panel 30plex_71054 57034-8ET1.tiff" --output-dir ./output

# Step 3: Create fixed version
python extract_channels.py "T:/Data/128_Hesham_Amin/Human_Post_Treatment/20251212_192423_1_bopYhG_20251212_Mahesh_full panel 30plex_71054 57034-8ET1.tiff" --create-cleaned --output "T:/Data/128_Hesham_Amin/fixed_sample.tiff"

# Step 4: Try opening fixed_sample.tiff in QuPath
```

## Common Options

### Save output files

```bash
# All tools support --output-dir
python inspect_tiff.py file.tiff --output-dir ./results

# This saves:
# - Test regions as .npy files
# - Downsampled versions
# - OME metadata as .xml
# - Channel statistics
```

### Adjust region/sample sizes

```bash
# Larger test region
python inspect_tiff.py file.tiff --region-size 2000

# Less aggressive downsampling
python inspect_tiff.py file.tiff --downsample 50
```

### Export individual channels

```bash
# Export each valid channel as separate TIFF
python extract_channels.py file.tiff \
    --export-individual \
    --output-dir ./channels
```

## Troubleshooting

### "Out of memory" error
- The tools are designed to avoid this, but if it happens:
- Use higher `--downsample` factors (200, 500)
- Use `--metadata-only` for quick checks
- Process fewer channels at once

### Very slow processing
- Normal for 100GB+ files
- Each channel takes 1-2 minutes to check
- Use `--max-channels 10` to limit scope
- Run in background and check results later

### "Module not found" error
```bash
# Make sure you installed requirements
pip install -r requirements.txt

# Or install directly
pip install numpy tifffile imagecodecs
```

## What Files Get Created

| Tool | Output Files |
|------|-------------|
| `inspect_tiff.py` | `*_region_*.npy`, `*_downsampled_*.npy`, `*_ome_metadata.xml` |
| `diagnose_channels.py` | `channel_NNN_sample.npy`, `*_ome_metadata.xml`, `*_channel_stats.txt` |
| `extract_channels.py` | `valid_channels_summary.txt`, individual channel TIFFs, cleaned multi-page TIFF |

All `.npy` files can be loaded in Python:
```python
import numpy as np
data = np.load('channel_000_sample.npy')
```

## Help

All tools have built-in help:
```bash
python inspect_tiff.py --help
python diagnose_channels.py --help
python extract_channels.py --help
```

For more details:
- See [README.md](README.md) for complete documentation
- See [../../docs/troubleshooting/tiff_file_issues.md](../../docs/troubleshooting/tiff_file_issues.md) for troubleshooting guide
