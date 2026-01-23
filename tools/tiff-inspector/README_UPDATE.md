# README Update - Add this section after tool #2

### 3. `extract_channels_ome.py` - OME-TIFF Channel Extraction (⭐ RECOMMENDED for QuPath)

**⭐ Use this version for QuPath compatibility!**

Creates proper OME-TIFF files that QuPath recognizes as multi-channel images. This is the **recommended tool** for creating cleaned files that need to open in QuPath or other Bio-Formats viewers.

**Features:**
- Creates standards-compliant OME-TIFF format
- Preserves channel names from original file
- QuPath opens as proper multi-channel image
- Individual channel export with channel names in filenames
- Based on best practices from imc-converter

**Usage:**
```bash
# Create OME-TIFF for QuPath (RECOMMENDED)
python extract_channels_ome.py image.tiff --create-ome-tiff --output fixed.ome.tiff

# Export individual channels with names
python extract_channels_ome.py image.tiff \
    --export-individual \
    --output-dir ./channels

# Both OME-TIFF and individual files
python extract_channels_ome.py image.tiff \
    --create-ome-tiff \
    --export-individual

# Adjust validation threshold
python extract_channels_ome.py image.tiff \
    --create-ome-tiff \
    --threshold 5.0
```

**Output:**
- Proper OME-TIFF with all valid channels in single multi-channel image
- Channel names preserved from original file (e.g., DAPI, CD31, Ki67)
- Embedded OME-XML metadata
- QuPath-compatible format

**See also:** [OME_TIFF_GUIDE.md](OME_TIFF_GUIDE.md) for detailed documentation

---

### 4. `extract_channels.py` - Basic Channel Extraction

Creates multi-page TIFF files (each channel as separate page).

**⚠️ Note:** QuPath may show channels as separate images instead of a multi-channel image. Use `extract_channels_ome.py` instead for QuPath compatibility.

**Use this version for:**
- Exporting individual channels only
- Non-QuPath workflows
- Simple channel splitting

**Usage:**
```bash
# Find valid channels (summary only)
python extract_channels.py image.tiff

# Export as multi-page TIFF
python extract_channels.py image.tiff --create-cleaned --output cleaned.tiff

# Export individual channels
python extract_channels.py image.tiff --export-individual
```

---

## Which Tool Should I Use?

| Your Goal | Recommended Tool |
|-----------|------------------|
| **Open in QuPath** | `extract_channels_ome.py --create-ome-tiff` ⭐ |
| Check file integrity | `inspect_tiff.py --metadata-only` |
| See which channels have data | `diagnose_channels.py` |
| Export individual channels | `extract_channels_ome.py --export-individual` |
| Quick file inspection | `inspect_tiff.py` |

