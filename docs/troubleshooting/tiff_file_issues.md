# TIFF File Issues

## Overview

Comprehensive troubleshooting guide for TIFF file corruption, metadata issues, and viewer compatibility problems encountered in microscopy image analysis workflows.

## Symptoms

- QuPath or other viewers refuse to open TIFF files
- "Invalid page offset" errors
- "Cannot read file" or "Unsupported format" errors
- Files fail to load with no error message
- Only some channels visible in multi-channel images
- Extremely slow loading or viewer crashes
- File size doesn't match expected dimensions

## Common Causes

1. **Incomplete file transfer**: Download/export interrupted
2. **Metadata corruption**: OME-XML doesn't match actual file structure
3. **Missing frames**: Some channels never written or lost
4. **Invalid page offsets**: Internal file pointers corrupted
5. **Compression incompatibility**: Viewer doesn't support compression type
6. **Memory constraints**: File too large for available RAM
7. **BigTIFF mismatch**: File >4GB but not in BigTIFF format
8. **Path issues**: Special characters or very long file paths

## Diagnostic Tools

The `tiff-inspector` toolkit provides command-line tools for diagnosing and fixing TIFF issues.

Location: `tools/tiff-inspector/`

### Quick Diagnosis

```bash
# Check if file is corrupt and view metadata
python tools/tiff-inspector/inspect_tiff.py problematic.tiff --metadata-only

# For multi-channel files, check which channels have data
python tools/tiff-inspector/diagnose_channels.py problematic.tiff
```

Expected output will show:
- File size vs expected size
- Whether file opens successfully
- Number of pages/channels
- Which channels contain data vs empty/corrupted

## Solutions

### Solution 1: Verify File Integrity

**Symptoms:**
- File size suspiciously small (KB instead of GB)
- Error when trying to open file header

**Diagnosis:**
```bash
python tools/tiff-inspector/inspect_tiff.py file.tiff --metadata-only
```

Look for:
- "File is suspiciously small" warning
- "Could not open TIFF file" error
- File size <<1GB for expected large microscopy image

**Fix:**
- Re-download or re-export the file from source
- Verify file transfer completed (check MD5/SHA checksums if available)
- Check available disk space during transfer

### Solution 2: Fix Multi-Channel Files with Missing Frames

**Symptoms:**
- "OME series is missing X frames" warning
- "Invalid page offset" errors
- QuPath shows some but not all channels
- Expected 30-plex but only 21 channels visible

**Diagnosis:**
```bash
python tools/tiff-inspector/diagnose_channels.py file.tiff --output-dir ./diagnosis
```

This will:
- Check each channel for actual data
- Save samples from channels with content
- Extract OME metadata
- Report which channels are missing

**Fix:**
```bash
# Extract only valid channels and create cleaned file
python tools/tiff-inspector/extract_channels.py file.tiff \
    --create-cleaned \
    --output fixed.tiff

# Try opening fixed.tiff in QuPath
```

This creates a new TIFF with:
- Only channels that contain data
- Corrected metadata matching actual content
- Proper BigTIFF format and tiling
- LZW compression for smaller size

### Solution 3: Memory Issues with Large Files

**Symptoms:**
- QuPath crashes when opening file
- "Out of memory" errors
- Very slow loading or system freeze

**Diagnosis:**
```bash
# Check memory requirements
python tools/tiff-inspector/inspect_tiff.py file.tiff --metadata-only
```

Look for "Estimated memory to load full image" line.

**Fix A - QuPath Memory Allocation:**

Increase QuPath's memory allocation (see [QuPath Common Errors](qupath_common_errors.md#solution-1-increase-memory-allocation)).

**Fix B - Create Pyramidal TIFF:**

Convert to multi-resolution pyramid format:
```python
import tifffile
import numpy as np

# Read original
with tifffile.TiffFile('large.tiff') as tif:
    data = tif.pages[0].asarray()

# Save with subresolutions
tifffile.imwrite(
    'pyramidal.tiff',
    data,
    tile=(512, 512),
    compression='jpeg',
    subfiletype=0,
    photometric='rgb'
)
```

**Fix C - Create Downsampled Version:**

```bash
# Create heavily downsampled preview
python tools/tiff-inspector/inspect_tiff.py file.tiff \
    --downsample 500 \
    --output-dir ./preview
```

### Solution 4: Compression Incompatibility

**Symptoms:**
- File opens but shows corrupted/garbled image
- "Unsupported compression" error
- QuPath loads metadata but not pixel data

**Diagnosis:**
```bash
python tools/tiff-inspector/inspect_tiff.py file.tiff
```

Look for "Compression: X" in output. Problematic compressions:
- JPEG in scientific images (lossy)
- Uncommon codecs not supported by viewer
- Proprietary compression formats

**Fix:**

Re-save with standard compression:
```bash
# Extract valid channels with LZW compression
python tools/tiff-inspector/extract_channels.py file.tiff \
    --create-cleaned \
    --compression lzw \
    --output recompressed.tiff
```

Or no compression (faster, larger):
```bash
python tools/tiff-inspector/extract_channels.py file.tiff \
    --create-cleaned \
    --compression none \
    --output uncompressed.tiff
```

### Solution 5: Extract Specific Channels

**Symptoms:**
- Only need certain channels for analysis
- File too large to work with
- Some channels corrupted but others OK

**Fix:**
```bash
# Step 1: Identify valid channels
python tools/tiff-inspector/diagnose_channels.py file.tiff

# Step 2: Export specific channels as individual files
python tools/tiff-inspector/extract_channels.py file.tiff \
    --export-individual \
    --output-dir ./channels

# Each channel saved as: filename_channel_NNN.tiff
```

Individual channel files can be opened independently in QuPath or other tools.

### Solution 6: OME Metadata Mismatch

**Symptoms:**
- OME-TIFF but viewer shows incorrect dimensions
- Expected multi-channel but shows single-channel
- Channel names missing or incorrect

**Diagnosis:**
```bash
# Extract OME metadata
python tools/tiff-inspector/inspect_tiff.py file.tiff \
    --save-ome \
    --output-dir ./metadata
```

Open the `*_ome_metadata.xml` file and check:
- `SizeC` value (expected number of channels)
- Channel names in `<Channel>` elements
- Dimensions match actual file structure

**Fix:**

Extract valid channels which will create corrected OME metadata:
```bash
python tools/tiff-inspector/extract_channels.py file.tiff --create-cleaned
```

The cleaned file will have OME metadata matching actual channel count and structure.

## Prevention

### During Image Acquisition
- Verify file size immediately after export
- Check first/last channels for data presence
- Save MD5 checksums for large files
- Test opening in viewer before analysis

### During File Transfer
- Use reliable transfer methods (rsync, validated copies)
- Verify file size after transfer
- Use checksums to verify integrity
- Monitor for interrupted transfers

### File Format Selection
- Use BigTIFF format for files >4GB
- Prefer OME-TIFF for multi-channel microscopy
- Use standard compression (LZW, deflate)
- Include proper metadata at acquisition time

### Storage Best Practices
- Maintain backups of raw acquired data
- Store metadata separately for critical experiments
- Use file systems that support large files (NTFS, ext4)
- Avoid special characters in file names and paths

## Real-World Example

**Case Study: 30-plex Human Tissue Sample**

**Problem:**
- 107GB OME-TIFF file won't open in QuPath
- Expected 33 channels, error says "missing 12 frames"
- File exported from Lunaphore imaging system

**Diagnosis:**
```bash
$ python diagnose_channels.py sample.tiff

Total pages: 21
Series: 1 (33, 44643, 44643), uint16
OME series is missing 12 frames. Missing data are zeroed

Channel 0: DAPI ✓ VALID (max=3743, 15.2% non-zero)
Channel 1: TRITC ✓ VALID (max=4095, 42.1% non-zero)
...
Channel 20: Hoechst ✓ VALID
Channels 21-32: MISSING

Summary: 21 accessible channels out of 33 expected
```

**Root Cause:**
- Export process failed to write last 12 channels
- OME metadata still declared 33 channels
- QuPath Bio-Formats refused to open due to mismatch

**Solution:**
```bash
$ python extract_channels.py sample.tiff \
    --create-cleaned \
    --output sample_fixed.tiff

Found 21 valid channels
Created cleaned TIFF: sample_fixed.tiff
```

**Result:**
- New file opens successfully in QuPath
- Contains 21 valid channels with proper metadata
- Lost channels (CD56, CD57, CD11c, etc.) documented in KB
- Contacted imaging facility about export issues

## Related Resources

- [TIFF Inspector Tools](../../tools/tiff-inspector/README.md) - Complete tool documentation
- [QuPath Common Errors](qupath_common_errors.md) - QuPath-specific issues
- [tifffile Python Library](https://github.com/cgohlke/tifffile) - Underlying library
- [OME-TIFF Specification](https://docs.openmicroscopy.org/ome-model/latest/ome-tiff/) - Format details
- [Bio-Formats](https://www.openmicroscopy.org/bio-formats/) - File format library used by QuPath

## KB Update History

| Date | Issue | Resolution | Tools Used |
|------|-------|------------|------------|
| 2026-01-12 | 30-plex missing 12 frames | Extracted 21 valid channels | diagnose_channels, extract_channels |
| (Add new cases here) | | | |

## Last Updated

2026-01-12
