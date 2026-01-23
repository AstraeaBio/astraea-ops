#!/usr/bin/env python3
"""
TIFF File Inspector - Memory-Efficient Tool for Large TIFF Files

Part of the Astraea Bio Operations Toolkit
Inspects TIFF files that may be too large to load into memory or fail in standard viewers.

Usage:
    python inspect_tiff.py <filepath> [options]
    python inspect_tiff.py file1.tiff file2.tiff --region-size 2000
"""

import os
import sys
import argparse
import numpy as np
from pathlib import Path

try:
    import tifffile
except ImportError:
    print("ERROR: tifffile not installed. Install with: pip install tifffile")
    sys.exit(1)


def get_file_size_gb(filepath):
    """Get file size in GB."""
    size_bytes = os.path.getsize(filepath)
    return size_bytes / (1024**3)


def check_file_corruption(filepath):
    """
    Basic check for file corruption by attempting to read headers and data.
    """
    print(f"\n{'='*80}")
    print(f"Checking for corruption: {os.path.basename(filepath)}")
    print(f"{'='*80}")

    # Check file size
    file_size = os.path.getsize(filepath)
    print(f"File size: {file_size} bytes ({file_size / (1024**3):.2f} GB)")

    if file_size < 1024:  # Less than 1KB is suspicious for a TIFF
        print("WARNING: File is suspiciously small. Likely incomplete or corrupted.")
        return False

    # Try to open with tifffile
    try:
        with tifffile.TiffFile(filepath) as tif:
            print(f"Successfully opened TIFF file")
            print(f"Format appears valid: {tif.is_bigtiff and 'BigTIFF' or 'Standard TIFF'}")

            # Try to access first page
            if len(tif.pages) > 0:
                print(f"First page accessible: {tif.pages[0].shape}")

                # Try to read a small region
                try:
                    test_read = tif.pages[0].asarray()[0:10, 0:10]
                    print(f"Successfully read test region: {test_read.shape}")
                    return True
                except Exception as e:
                    print(f"ERROR: Could not read data from first page: {e}")
                    return False
            else:
                print("ERROR: No pages found in TIFF file")
                return False

    except Exception as e:
        print(f"ERROR: Could not open TIFF file: {e}")
        import traceback
        traceback.print_exc()
        return False


def inspect_tiff_metadata(filepath):
    """
    Inspect TIFF file metadata without loading the full image into memory.
    """
    print(f"\n{'='*80}")
    print(f"Inspecting: {os.path.basename(filepath)}")
    print(f"{'='*80}")
    print(f"File size: {get_file_size_gb(filepath):.2f} GB")

    try:
        with tifffile.TiffFile(filepath) as tif:
            print(f"\nNumber of pages/series: {len(tif.pages)}")
            print(f"Is BigTIFF: {tif.is_bigtiff}")

            # Get first page info
            page = tif.pages[0]
            print(f"\nFirst page information:")
            print(f"  Shape: {page.shape}")
            print(f"  Dtype: {page.dtype}")
            print(f"  Bits per sample: {page.bitspersample}")
            print(f"  Samples per pixel: {page.samplesperpixel}")
            print(f"  Photometric: {page.photometric}")
            print(f"  Compression: {page.compression}")
            print(f"  Planar config: {page.planarconfig}")

            # Check if tiled
            if page.is_tiled:
                print(f"  Tiled: Yes")
                print(f"  Tile shape: {page.tilelength} x {page.tilewidth}")
            else:
                print(f"  Tiled: No (Striped)")
                if hasattr(page, 'rowsperstrip'):
                    print(f"  Rows per strip: {page.rowsperstrip}")

            # Check for pyramidal/multi-resolution
            if len(tif.series) > 0:
                print(f"\nSeries information:")
                for i, series in enumerate(tif.series):
                    print(f"  Series {i}: {series.shape}, {series.dtype}")

            # Memory estimate
            if len(page.shape) >= 2:
                pixels = np.prod(page.shape)
                bytes_per_pixel = page.dtype.itemsize
                memory_gb = (pixels * bytes_per_pixel) / (1024**3)
                print(f"\nEstimated memory to load full image: {memory_gb:.2f} GB")

            # Check for image description
            if hasattr(page, 'description') and page.description:
                print(f"\nImage Description (first 500 chars):")
                print(page.description[:500])

            # Check for tags
            print(f"\nAvailable tags: {len(page.tags)} tags")

            # Check for OME metadata
            if hasattr(tif, 'ome_metadata') and tif.ome_metadata:
                print(f"\nOME-TIFF detected: Yes")
                # Save OME metadata if requested
                return tif.ome_metadata

        return None

    except Exception as e:
        print(f"\nERROR inspecting file: {e}")
        import traceback
        traceback.print_exc()
        return None


def read_tiff_region(filepath, x=0, y=0, width=1000, height=1000, page=0, output_dir=None):
    """
    Read a specific region from a TIFF file.
    Useful for inspecting data without loading the entire image.
    """
    print(f"\nReading region: x={x}, y={y}, width={width}, height={height}, page={page}")

    try:
        with tifffile.TiffFile(filepath) as tif:
            if page >= len(tif.pages):
                print(f"ERROR: Page {page} doesn't exist. File has {len(tif.pages)} pages.")
                return None

            page_obj = tif.pages[page]

            # Adjust width/height if they exceed image bounds
            max_y, max_x = page_obj.shape[:2]
            actual_height = min(height, max_y - y)
            actual_width = min(width, max_x - x)

            print(f"Adjusted region: {actual_width}x{actual_height}")

            # Read the region
            region = page_obj.asarray()[y:y+actual_height, x:x+actual_width]

            print(f"Region shape: {region.shape}")
            print(f"Region dtype: {region.dtype}")
            print(f"Region min/max: {region.min()} / {region.max()}")
            print(f"Region mean: {region.mean():.2f}")

            # Save region if output directory specified
            if output_dir:
                output_path = Path(output_dir)
                output_path.mkdir(parents=True, exist_ok=True)
                filename = Path(filepath).stem
                output_file = output_path / f"{filename}_region_{x}_{y}_{actual_width}x{actual_height}.npy"
                np.save(str(output_file), region)
                print(f"Saved to: {output_file}")

            return region

    except Exception as e:
        print(f"\nERROR reading region: {e}")
        import traceback
        traceback.print_exc()
        return None


def read_tiff_downsampled(filepath, downsample_factor=10, page=0, output_dir=None):
    """
    Read a downsampled version of the TIFF file by reading every Nth pixel.
    """
    print(f"\nReading downsampled image (factor={downsample_factor}, page={page})")

    try:
        with tifffile.TiffFile(filepath) as tif:
            if page >= len(tif.pages):
                print(f"ERROR: Page {page} doesn't exist. File has {len(tif.pages)} pages.")
                return None

            page_obj = tif.pages[page]

            # Read every Nth row and column
            downsampled = page_obj.asarray()[::downsample_factor, ::downsample_factor]

            print(f"Original shape: {page_obj.shape}")
            print(f"Downsampled shape: {downsampled.shape}")
            print(f"Downsampled dtype: {downsampled.dtype}")
            print(f"Downsampled min/max: {downsampled.min()} / {downsampled.max()}")

            # Save downsampled if output directory specified
            if output_dir:
                output_path = Path(output_dir)
                output_path.mkdir(parents=True, exist_ok=True)
                filename = Path(filepath).stem
                output_file = output_path / f"{filename}_downsampled_{downsample_factor}x.npy"
                np.save(str(output_file), downsampled)
                print(f"Saved to: {output_file}")

            return downsampled

    except Exception as e:
        print(f"\nERROR reading downsampled image: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Main function to inspect TIFF files."""
    parser = argparse.ArgumentParser(
        description="Inspect large TIFF files with memory-efficient strategies",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Inspect a single file
  python inspect_tiff.py image.tiff

  # Inspect multiple files
  python inspect_tiff.py file1.tiff file2.tiff

  # Save test region and downsampled version
  python inspect_tiff.py image.tiff --output-dir ./output

  # Custom region size and downsample factor
  python inspect_tiff.py image.tiff --region-size 2000 --downsample 200

  # Skip region/downsample extraction (metadata only)
  python inspect_tiff.py image.tiff --metadata-only
        """
    )

    parser.add_argument('files', nargs='+', help='TIFF file(s) to inspect')
    parser.add_argument('--output-dir', '-o', help='Directory to save output files (regions, downsampled images)')
    parser.add_argument('--region-size', '-r', type=int, default=1000, help='Size of test region to extract (default: 1000)')
    parser.add_argument('--downsample', '-d', type=int, default=100, help='Downsample factor (default: 100)')
    parser.add_argument('--metadata-only', '-m', action='store_true', help='Only inspect metadata, skip data extraction')
    parser.add_argument('--save-ome', action='store_true', help='Save OME-XML metadata to file')

    args = parser.parse_args()

    print("="*80)
    print("TIFF File Inspector - Astraea Bio Operations Toolkit")
    print("="*80)

    for filepath in args.files:
        filepath = str(Path(filepath).resolve())

        if not os.path.exists(filepath):
            print(f"\nWARNING: File not found: {filepath}")
            continue

        # Check for corruption
        is_valid = check_file_corruption(filepath)

        if not is_valid:
            print(f"\nSkipping detailed inspection due to corruption/errors.")
            continue

        # Inspect metadata
        ome_metadata = inspect_tiff_metadata(filepath)

        # Save OME metadata if requested
        if args.save_ome and ome_metadata and args.output_dir:
            output_path = Path(args.output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            filename = Path(filepath).stem
            ome_file = output_path / f"{filename}_ome_metadata.xml"
            with open(ome_file, 'w') as f:
                f.write(ome_metadata)
            print(f"\nSaved OME metadata to: {ome_file}")

        if args.metadata_only:
            continue

        # Read a small region for testing
        print("\n" + "-"*80)
        print(f"Reading test region ({args.region_size}x{args.region_size} pixels from top-left)")
        print("-"*80)
        region = read_tiff_region(filepath, x=0, y=0,
                                  width=args.region_size, height=args.region_size,
                                  output_dir=args.output_dir)

        # Read downsampled version
        print("\n" + "-"*80)
        print(f"Reading downsampled version (every {args.downsample}th pixel)")
        print("-"*80)
        downsampled = read_tiff_downsampled(filepath,
                                            downsample_factor=args.downsample,
                                            output_dir=args.output_dir)

    print("\n" + "="*80)
    print("Inspection complete!")
    print("="*80)


if __name__ == "__main__":
    main()
