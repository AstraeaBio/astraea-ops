# TIFF Inspector

Memory-efficient tools for inspecting, diagnosing, and extracting data from large TIFF files that may fail to open in standard image viewers like QuPath.

**Part of the Astraea Bio Operations Toolkit**

## Problem Statement

Large microscopy TIFF files (50GB+) frequently fail to open in QuPath or other viewers due to:
- Corrupted or missing frames
- OME metadata mismatches
- Invalid page offsets
- Insufficient memory
- Incompatible compression formats

This toolkit provides command-line tools to:
1. Inspect files without loading into memory
2. Diagnose multi-channel structure issues
3. Extract valid channels from problematic files
4. Create cleaned versions compatible with standard viewers

## Installation

```bash
# From the tiff-inspector directory
pip install -r requirements.txt
```

### Requirements
- Python 3.7+
- numpy
- tifffile
- imagecodecs

## Tools

### 1. `inspect_tiff.py` - General TIFF File Inspector

Inspects TIFF file metadata and extracts test regions without loading full image into memory.

**Features:**
- Check for file corruption
- Extract metadata (dimensions, data type, compression, etc.)
- Read small test regions
- Create downsampled thumbnails
- Extract OME-XML metadata

**Usage:**
```bash
# Basic inspection
python inspect_tiff.py image.tiff

# Inspect multiple files
python inspect_tiff.py file1.tiff file2.tiff

# Save test region and downsampled version
python inspect_tiff.py image.tiff --output-dir ./output

# Custom region size and downsample factor
python inspect_tiff.py image.tiff --region-size 2000 --downsample 200

# Metadata only (skip data extraction)
python inspect_tiff.py image.tiff --metadata-only

# Extract and save OME metadata
python inspect_tiff.py image.tiff --save-ome --output-dir ./output
```

**Output:**
- Console: File metadata, warnings, statistics
- `*_region_*.npy`: Test region data (if `--output-dir` specified)
- `*_downsampled_*.npy`: Downsampled image data
- `*_ome_metadata.xml`: OME-XML metadata (if `--save-ome`)

### 2. `diagnose_channels.py` - Multi-Channel TIFF Diagnostic

Diagnoses multi-channel TIFF files to identify which channels contain actual data vs empty/corrupted channels.

**Features:**
- Check all channels for data presence
- Calculate statistics per channel
- Sample data from each channel
- Extract OME metadata
- Identify missing or corrupted frames

**Usage:**
```bash
# Basic diagnosis
python diagnose_channels.py image.tiff

# Save channel samples and metadata
python diagnose_channels.py image.tiff --output-dir ./diagnosis

# Check specific channels with detailed distribution
python diagnose_channels.py image.tiff --check-distribution 0 3 5

# Limit number of channels to check (for speed)
python diagnose_channels.py image.tiff --max-channels 10
```

**Output:**
- Console: Per-channel statistics and data presence
- `channel_NNN_sample.npy`: Sample data from channels with content
- `*_ome_metadata.xml`: OME-XML metadata
- `*_channel_stats.txt`: Summary of all channel statistics

### 3. `extract_channels.py` - Channel Extraction Tool

Identifies valid channels and exports them as individual files or creates a cleaned multi-page TIFF.

**Features:**
- Automatically identify channels with data
- Export channels individually
- Create cleaned multi-page TIFF with only valid channels
- Configurable validation threshold
- Compression options

**Usage:**
```bash
# Find valid channels (summary only)
python extract_channels.py image.tiff

# Export valid channels as individual files
python extract_channels.py image.tiff --export-individual --output-dir ./channels

# Create cleaned multi-page TIFF with only valid channels
python extract_channels.py image.tiff --create-cleaned --output cleaned.tiff

# Both individual export and cleaned multi-page
python extract_channels.py image.tiff --export-individual --create-cleaned

# Adjust threshold for what counts as "valid" (% non-zero pixels)
python extract_channels.py image.tiff --threshold 5.0 --create-cleaned

# Export without compression (faster, larger files)
python extract_channels.py image.tiff --create-cleaned --compression none
```

**Output:**
- `valid_channels_summary.txt`: List of valid channels with statistics
- Individual channel TIFFs (if `--export-individual`)
- Cleaned multi-page TIFF (if `--create-cleaned`)

## Common Workflows

### Workflow 1: QuPath Won't Open My TIFF File

```bash
# Step 1: Check for corruption and basic metadata
python inspect_tiff.py problematic.tiff --metadata-only

# Step 2: If multi-channel, diagnose which channels have data
python diagnose_channels.py problematic.tiff --output-dir ./diagnosis

# Step 3: Review diagnosis output, then extract valid channels
python extract_channels.py problematic.tiff --create-cleaned --output fixed.tiff

# Step 4: Try opening fixed.tiff in QuPath
```

### Workflow 2: Verify File Integrity After Transfer

```bash
# Quick check for corruption
python inspect_tiff.py transferred_file.tiff --metadata-only

# If OK, extract a test region to verify data
python inspect_tiff.py transferred_file.tiff --output-dir ./validation
```

### Workflow 3: Extract Specific Channels for Analysis

```bash
# Identify which channels have data
python diagnose_channels.py multichannel.tiff

# Export specific channels
python extract_channels.py multichannel.tiff --export-individual --threshold 1.0
```

### Workflow 4: Create Downsampled Preview

```bash
# Create heavily downsampled version for quick viewing
python inspect_tiff.py large_image.tiff --downsample 500 --output-dir ./preview
```

## Memory-Efficient Strategies

All tools are designed to work with files larger than available RAM:

1. **Streaming Access**: Read data in chunks, not all at once
2. **Downsampling**: Sample every Nth pixel for quick checks
3. **Region-Based**: Process small regions at a time
4. **Lazy Loading**: Only load data when actually needed
5. **Immediate Cleanup**: Delete large arrays after use

## Troubleshooting

### "Out of memory" errors

- Use higher `--downsample` factors
- Use `--metadata-only` to skip data extraction
- Reduce `--region-size`
- Close other applications

### "Invalid page offset" errors

File is likely corrupted. Use `diagnose_channels.py` to see which pages are accessible.

### All channels show as empty

Check if file completed downloading/exporting. Files with only header data will be very small (<1MB for expected 100GB+ files).

### OME metadata doesn't match actual pages

Common in corrupted files. Use `extract_channels.py` to create cleaned version with correct metadata.

## Integration with QuPath

These tools complement QuPath troubleshooting:

1. **Before** trying to open in QuPath, use `inspect_tiff.py` to validate
2. If QuPath fails with "Cannot read file", use `diagnose_channels.py` to identify issues
3. Use `extract_channels.py` to create QuPath-compatible version
4. The cleaned TIFFs use:
   - BigTIFF format (required for >4GB files)
   - 512x512 tiling (optimal for QuPath)
   - LZW compression (good balance of speed/size)
   - Proper metadata structure

## Technical Details

### Supported Formats
- Standard TIFF
- BigTIFF (>4GB files)
- OME-TIFF
- Multi-page/multi-channel TIFF
- Tiled TIFF
- Various compressions (uncompressed, LZW, JPEG, etc.)

### Limitations
- Very large single-channel images (>50GB uncompressed) may still require significant RAM for some operations
- Heavily compressed formats require decompression before access (slower)
- Some proprietary TIFF variants may not be fully supported

## For Developers

### Adding New Diagnostic Tools

The toolkit uses `tifffile` for TIFF I/O. Key patterns:

```python
import tifffile

# Always use context manager
with tifffile.TiffFile(filepath) as tif:
    # Access metadata without loading data
    page = tif.pages[0]
    print(page.shape, page.dtype)

    # Load data only when needed
    # Use slicing for regions: data = page.asarray()[y:y+h, x:x+w]
    # Use downsampling: data = page.asarray()[::N, ::N]
```

### Testing

Test with files of various sizes and formats:
- Small test files (<1GB)
- Large multi-channel files (50GB+)
- Corrupted files (incomplete downloads)
- Different compression formats

## References

- [QuPath Common Errors](../../docs/troubleshooting/qupath_common_errors.md)
- [TIFF File Issues](../../docs/troubleshooting/tiff_file_issues.md)
- [tifffile documentation](https://github.com/cgohlke/tifffile)
- [OME-TIFF specification](https://docs.openmicroscopy.org/ome-model/latest/ome-tiff/)

## Contributing

When adding tools or documentation:
1. Follow the KB update rules (see main README)
2. Add command-line examples to this README
3. Update troubleshooting docs with new failure modes discovered
4. Add your findings to the knowledge base

## Last Updated

2026-01-12

## Authors

Astraea Bio Operations Team
