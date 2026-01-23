# OME-TIFF Export Guide

## Overview

The `extract_channels_ome.py` script creates **proper OME-TIFF files** that are fully compatible with QuPath and other Bio-Formats based viewers. This is the **recommended approach** for creating cleaned TIFF files.

## Why Use OME-TIFF Format?

### Problem with Standard Multi-Page TIFF
The original `extract_channels.py` writes each channel as a separate page, which causes viewers like QuPath to see them as **separate images** rather than channels of a single multi-channel image.

### OME-TIFF Solution
- All channels stored as a single **multi-channel image** (CYX format)
- Proper OME-XML metadata embedded in the file
- Channel names preserved from original file
- Standards-compliant format recognized by Bio-Formats
- QuPath loads all channels correctly

## Key Differences

| Feature | extract_channels.py | extract_channels_ome.py |
|---------|-------------------|------------------------|
| Output Format | Multi-page TIFF | OME-TIFF |
| QuPath Compatibility | ⚠️ Shows as separate images | ✅ Shows as multi-channel |
| Channel Names | ❌ Not preserved | ✅ Preserved from original |
| OME-XML Metadata | ❌ Missing/incomplete | ✅ Standards-compliant |
| Data Organization | Separate pages | Stacked CYX array |
| Recommended | For individual channel export | **For QuPath import** |

## Usage

### Basic Command (Recommended)

```bash
python extract_channels_ome.py problematic.tiff --create-ome-tiff --output fixed.ome.tiff
```

This will:
1. Scan all channels for data
2. Extract channel names from OME metadata
3. Create a proper OME-TIFF with only valid channels
4. Preserve channel names in the output

### With Your Specific File

```bash
cd T:/0_Organizational/astraea-ops/tools/tiff-inspector

python extract_channels_ome.py \
    "T:/Data/128_Hesham_Amin/Human_Post_Treatment/20251212_192423_1_bopYhG_20251212_Mahesh_full panel 30plex_71054 57034-8ET1.tiff" \
    --create-ome-tiff \
    --output "T:/Data/128_Hesham_Amin/fixed_sample.ome.tiff"
```

Expected output:
- File: `fixed_sample.ome.tiff` (~20-30GB with LZW compression)
- Contains: 21 valid channels (not the 12 missing ones)
- Channel names: DAPI, TRITC, Cy5, CD31, CD4, etc.
- Format: Proper OME-TIFF with embedded metadata

### Opening in QuPath

1. Launch QuPath
2. File → Open → Select `fixed_sample.ome.tiff`
3. QuPath should now show **all 21 channels** in the channel viewer
4. You can toggle channels on/off, adjust brightness/contrast per channel

## Options

### Export Both OME-TIFF and Individual Channels

```bash
python extract_channels_ome.py file.tiff \
    --create-ome-tiff \
    --export-individual \
    --output-dir ./channels
```

Individual channel files will include channel names in filenames:
- `filename_000_DAPI.tiff`
- `filename_001_TRITC.tiff`
- `filename_003_CD31.tiff`
- etc.

### Adjust Validation Threshold

```bash
# Only include channels with >5% non-zero pixels
python extract_channels_ome.py file.tiff \
    --create-ome-tiff \
    --threshold 5.0
```

### No Compression (Faster but Larger)

```bash
python extract_channels_ome.py file.tiff \
    --create-ome-tiff \
    --compression none
```

Note: This will create much larger files but may be faster to write and read.

## Technical Details

### OME-XML Structure

The tool creates standards-compliant OME-XML following the OME 2016-06 schema:

```xml
<OME xmlns="http://www.openmicroscopy.org/Schemas/OME/2016-06">
  <Image ID="Image:0" Name="Extracted Channels">
    <Pixels Type="uint16"
            DimensionOrder="XYZCT"
            SizeX="44643"
            SizeY="44643"
            SizeZ="1"
            SizeC="21"
            SizeT="1"
            PhysicalSizeX="1.0"
            PhysicalSizeY="1.0"
            Interleaved="false">
      <Channel ID="Channel:0:0" Name="DAPI" />
      <Channel ID="Channel:0:1" Name="TRITC" />
      <Channel ID="Channel:0:2" Name="Cy5" />
      ...
    </Pixels>
  </Image>
</OME>
```

### Data Organization

- **Format**: CYX (channels, height, width)
- **Channel stacking**: All channels in a single 3D array
- **Tiling**: 512x512 tiles for efficient access
- **BigTIFF**: Automatically enabled for files >2GB
- **Compression**: LZW by default (good balance of size/speed)

### Channel Name Extraction

Channel names are extracted from the original file's OME-XML metadata:

1. Parse OME-XML from original TIFF
2. Find all `<Channel>` elements
3. Extract `Name` attribute from each
4. Match to corresponding page index
5. Preserve in output OME-TIFF

If no OME metadata exists, channels are named `Channel_0`, `Channel_1`, etc.

## Implementation Reference

This implementation follows best practices from:
- **imc-converter** (STTARR): OME-TIFF export for imaging mass cytometry data
- **OME-TIFF Specification**: Standards-compliant metadata structure
- **Bio-Formats**: Format requirements for proper viewer compatibility

Key pattern from imc-converter:
```python
# Stack channels into CYX format
stacked_data = np.stack([ch0, ch1, ch2, ...], axis=0)

# Create OME-XML with channel metadata
ome_xml = create_ome_xml(channel_names, stacked_data.shape, dtype)

# Write with embedded OME-XML
tifffile.imwrite(output, stacked_data, description=ome_xml, metadata={'axes': 'CYX'})
```

## Troubleshooting

### QuPath still shows only one channel

**Possible causes:**
1. File not saved with `.ome.tiff` extension
   - Solution: Use `--output file.ome.tiff`

2. OME-XML not properly embedded
   - Check: Open file in text editor, look for `<OME xmlns=` near beginning
   - If missing: Re-run with latest version of script

3. QuPath cached old file format
   - Solution: Restart QuPath, clear image cache

### "Out of memory" during export

For 100GB+ source files:
1. Close other applications
2. Use higher downsample factor: `--threshold 1.0` (more aggressive filtering)
3. Export individual channels first to verify, then combine
4. Consider processing channels in batches (future enhancement)

### Channel names not showing correctly

Check original file has OME metadata:
```bash
python inspect_tiff.py original.tiff --save-ome --output-dir ./metadata
```

If `*_ome_metadata.xml` is empty or doesn't contain `<Channel>` elements, the original file doesn't have channel name metadata.

### File size concerns

Expected sizes:
- Uncompressed: ~3.7GB per channel (for 44k x 44k uint16)
- LZW compressed: ~1-2GB per channel (depends on data sparsity)
- 21 channels: ~20-40GB total

If size is too large:
1. Use JPEG compression (lossy but smaller): `--compression jpeg`
2. Downsample data before export (future enhancement)
3. Export only essential channels

## Migration from extract_channels.py

If you previously used `extract_channels.py`:

**Old command:**
```bash
python extract_channels.py file.tiff --create-cleaned --output fixed.tiff
```

**New command:**
```bash
python extract_channels_ome.py file.tiff --create-ome-tiff --output fixed.ome.tiff
```

**Key changes:**
- `--create-cleaned` → `--create-ome-tiff`
- Output should have `.ome.tiff` extension
- Channel names now preserved automatically
- QuPath will correctly show as multi-channel

## References

- [imc-converter GitHub](https://github.com/STTARR/imc-converter) - Reference implementation
- [OME-TIFF Specification](https://docs.openmicroscopy.org/ome-model/latest/ome-tiff/)
- [tifffile Documentation](https://github.com/cgohlke/tifffile)
- [Bio-Formats](https://www.openmicroscopy.org/bio-formats/)

## Last Updated

2026-01-12
