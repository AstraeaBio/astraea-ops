# QuPath Common Errors

## Overview

Troubleshooting guide for common QuPath application errors and issues.

## Symptoms

- QuPath crashes on startup
- Unable to open image files
- Memory errors with large images
- Plugin loading failures
- Export/import errors

## Common Causes

1. **Insufficient memory allocation**: Default heap size too small
2. **Incompatible image formats**: Unsupported file types or corrupted files
3. **Java version conflicts**: Wrong Java version installed
4. **Plugin incompatibilities**: Plugins not matching QuPath version
5. **Path issues with special characters**: File paths containing problematic characters

## Solutions

### Solution 1: Increase Memory Allocation

Edit QuPath launcher to allocate more memory:

On Linux/Mac, edit the launcher script:
```bash
# Add or modify the -Xmx parameter
java -Xmx16g -jar qupath.jar
```

On Windows, edit `QuPath.cfg`:
```
[JVMOptions]
-Xmx16g
```

### Solution 2: Convert Image Format

Convert problematic images to a supported format:

```python
import tifffile

# Read and resave as OME-TIFF
image = tifffile.imread('problematic_image.tif')
tifffile.imwrite('converted_image.ome.tiff', image, ome=True)
```

Or use Bio-Formats tools:
```bash
bfconvert input.czi output.ome.tiff
```

### Solution 3: Verify Java Installation

Check Java version:
```bash
java -version
```

QuPath typically requires Java 11 or later. Install the correct version if needed.

### Solution 4: Reset QuPath Configuration

If QuPath won't start, reset configuration:

```bash
# Linux/Mac
rm -rf ~/.qupath

# Windows
# Delete: C:\Users\USERNAME\.qupath
```

### Solution 5: Update Plugins

Ensure plugins are compatible with your QuPath version:

1. Open QuPath
2. Go to Extensions > Installed Extensions
3. Check for updates
4. Remove incompatible plugins

## Prevention

- Allocate sufficient memory for expected image sizes
- Use supported image formats (OME-TIFF recommended)
- Keep QuPath and plugins updated
- Avoid special characters in file paths

## Related Resources

- [QuPath Documentation](https://qupath.readthedocs.io/)
- [Phenotyping Pipeline SOP](../sops/phenotyping_pipeline.md)

## Last Updated

2025-12-05
