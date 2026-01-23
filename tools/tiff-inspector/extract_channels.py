#!/usr/bin/env python3
"""
Channel Extraction Tool for Multi-Channel TIFF Files

Part of the Astraea Bio Operations Toolkit
Extracts valid channels from problematic TIFF files and saves them as individual files
or creates a new multi-page TIFF with only valid data.

Usage:
    python extract_channels.py <filepath> [options]
"""

import numpy as np
import tifffile
from pathlib import Path
import argparse
import sys


def find_valid_channels(filepath, min_nonzero_percent=1.0, sample_factor=100):
    """
    Scan all channels and identify which ones have actual data.

    Args:
        filepath: Path to TIFF file
        min_nonzero_percent: Minimum percentage of non-zero pixels to consider valid
        sample_factor: Downsample factor for checking (default: 100)

    Returns:
        List of (channel_index, stats_dict) for valid channels
    """
    print(f"Scanning {Path(filepath).name} for valid channels...")
    print(f"Minimum non-zero threshold: {min_nonzero_percent}%\n")

    valid_channels = []

    with tifffile.TiffFile(filepath) as tif:
        total_pages = len(tif.pages)
        print(f"Total pages to check: {total_pages}\n")

        for page_idx in range(total_pages):
            try:
                page = tif.pages[page_idx]

                # Sample the data
                print(f"Checking channel {page_idx}/{total_pages}...", end=" ")
                sample = page.asarray()[::sample_factor, ::sample_factor]

                # Calculate statistics
                nonzero_count = np.count_nonzero(sample)
                total_count = sample.size
                nonzero_percent = 100 * nonzero_count / total_count

                stats = {
                    'min': int(sample.min()),
                    'max': int(sample.max()),
                    'mean': float(sample.mean()),
                    'std': float(sample.std()),
                    'nonzero_percent': nonzero_percent,
                    'shape': page.shape,
                    'dtype': str(page.dtype)
                }

                # Check if channel is valid
                if nonzero_percent >= min_nonzero_percent:
                    print(f"✓ VALID (max={stats['max']}, {nonzero_percent:.2f}% non-zero)")
                    valid_channels.append((page_idx, stats))
                else:
                    print(f"✗ Empty (max={stats['max']}, {nonzero_percent:.2f}% non-zero)")

                del sample

            except Exception as e:
                print(f"✗ ERROR: {e}")

    print(f"\n{'='*80}")
    print(f"Summary: Found {len(valid_channels)} valid channels out of {total_pages} total")
    print(f"{'='*80}\n")

    return valid_channels


def export_channel(filepath, channel_idx, output_dir="extracted_channels", compression='lzw'):
    """
    Export a single channel to a separate TIFF file.

    Args:
        filepath: Path to source TIFF
        channel_idx: Index of channel to export
        output_dir: Directory to save exported channel
        compression: Compression type ('lzw', 'none', 'jpeg', etc.)
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    filename = Path(filepath).stem
    output_file = output_path / f"{filename}_channel_{channel_idx:03d}.tiff"

    print(f"Exporting channel {channel_idx} to {output_file.name}...", end=" ")

    try:
        with tifffile.TiffFile(filepath) as tif:
            page = tif.pages[channel_idx]

            # For very large images, consider downsampling or chunking
            # Here we'll load directly - for 100GB+ files, implement chunking
            data = page.asarray()

            # Determine compression
            comp = None if compression == 'none' else compression

            tifffile.imwrite(
                output_file,
                data,
                tile=(512, 512),
                compression=comp,
                bigtiff=(data.nbytes > 2**31)  # Use BigTIFF if > 2GB
            )

            print(f"✓ Done")
            return str(output_file)

    except Exception as e:
        print(f"✗ ERROR: {e}")
        return None


def create_cleaned_multipage_tiff(filepath, valid_channels, output_file=None, compression='lzw'):
    """
    Create a new multi-page TIFF with only valid channels.

    Args:
        filepath: Path to source TIFF
        valid_channels: List of (channel_idx, stats) tuples
        output_file: Output filename
        compression: Compression type
    """
    if output_file is None:
        output_file = Path(filepath).parent / f"{Path(filepath).stem}_cleaned.tiff"
    else:
        output_file = Path(output_file)

    print(f"\nCreating cleaned multi-page TIFF with {len(valid_channels)} channels...")
    print(f"Output: {output_file}")

    try:
        with tifffile.TiffFile(filepath) as tif:
            with tifffile.TiffWriter(output_file, bigtiff=True) as writer:

                for idx, (channel_idx, stats) in enumerate(valid_channels):
                    print(f"  Copying channel {channel_idx} ({idx+1}/{len(valid_channels)})...", end=" ")

                    page = tif.pages[channel_idx]
                    data = page.asarray()

                    # Determine compression
                    comp = None if compression == 'none' else compression

                    writer.write(
                        data,
                        tile=(512, 512),
                        compression=comp,
                        metadata={'channel': channel_idx}
                    )

                    print("✓")
                    del data

        print(f"\n✓ Created cleaned TIFF: {output_file}")
        return str(output_file)

    except Exception as e:
        print(f"\n✗ ERROR creating cleaned TIFF: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    parser = argparse.ArgumentParser(
        description="Extract valid channels from multi-channel TIFF files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Find valid channels and show summary
  python extract_channels.py image.tiff

  # Export valid channels as individual files
  python extract_channels.py image.tiff --export-individual --output-dir ./channels

  # Create cleaned multi-page TIFF with only valid channels
  python extract_channels.py image.tiff --create-cleaned --output cleaned.tiff

  # Both individual export and cleaned multi-page
  python extract_channels.py image.tiff --export-individual --create-cleaned

  # Adjust threshold for what counts as "valid"
  python extract_channels.py image.tiff --threshold 5.0 --create-cleaned
        """
    )

    parser.add_argument('file', help='TIFF file to process')
    parser.add_argument('--threshold', '-t', type=float, default=0.1,
                       help='Minimum non-zero percentage to consider valid (default: 0.1%%)')
    parser.add_argument('--export-individual', '-e', action='store_true',
                       help='Export each valid channel as separate TIFF file')
    parser.add_argument('--create-cleaned', '-c', action='store_true',
                       help='Create cleaned multi-page TIFF with only valid channels')
    parser.add_argument('--output-dir', '-o', default='extracted_channels',
                       help='Output directory for individual channels (default: extracted_channels)')
    parser.add_argument('--output', '-O',
                       help='Output filename for cleaned multi-page TIFF')
    parser.add_argument('--compression', default='lzw',
                       choices=['none', 'lzw', 'jpeg', 'deflate'],
                       help='Compression type (default: lzw)')
    parser.add_argument('--max-export', type=int, default=50,
                       help='Maximum number of individual channels to export (default: 50)')

    args = parser.parse_args()

    filepath = str(Path(args.file).resolve())

    if not Path(filepath).exists():
        print(f"ERROR: File not found: {filepath}")
        sys.exit(1)

    print("="*80)
    print("Channel Extraction Tool - Astraea Bio Operations Toolkit")
    print("="*80 + "\n")

    # Step 1: Find valid channels
    print("STEP 1: Identifying Valid Channels")
    print("="*80 + "\n")

    valid_channels = find_valid_channels(filepath, min_nonzero_percent=args.threshold)

    if not valid_channels:
        print("\nNo valid channels found!")
        sys.exit(1)

    # Print summary
    print("\nValid Channels Summary:")
    print("-" * 80)
    print(f"{'Channel':<10} {'Max Value':<12} {'Non-zero %':<12} {'Mean':<12}")
    print("-" * 80)

    for channel_idx, stats in valid_channels:
        print(f"{channel_idx:<10} {stats['max']:<12} "
              f"{stats['nonzero_percent']:<12.2f} {stats['mean']:<12.2f}")

    # Save summary to file
    summary_file = Path(args.output_dir) / "valid_channels_summary.txt"
    summary_file.parent.mkdir(parents=True, exist_ok=True)
    with open(summary_file, 'w') as f:
        f.write("Valid Channels Summary\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Source file: {filepath}\n")
        f.write(f"Threshold: {args.threshold}%\n")
        f.write(f"Valid channels found: {len(valid_channels)}\n\n")
        for channel_idx, stats in valid_channels:
            f.write(f"Channel {channel_idx}:\n")
            for key, value in stats.items():
                f.write(f"  {key}: {value}\n")
            f.write("\n")

    print(f"\nSaved detailed summary to: {summary_file}")

    # Step 2: Export if requested
    if args.export_individual:
        print("\n" + "="*80)
        print("STEP 2: Exporting Individual Channels")
        print("="*80 + "\n")

        num_to_export = min(len(valid_channels), args.max_export)
        if len(valid_channels) > args.max_export:
            print(f"Limiting export to first {args.max_export} channels (use --max-export to change)\n")

        for channel_idx, stats in valid_channels[:num_to_export]:
            export_channel(filepath, channel_idx, args.output_dir, args.compression)

    # Step 3: Create cleaned multi-page TIFF if requested
    if args.create_cleaned:
        print("\n" + "="*80)
        print("STEP 3: Creating Cleaned Multi-page TIFF")
        print("="*80 + "\n")

        create_cleaned_multipage_tiff(filepath, valid_channels, args.output, args.compression)

    if not args.export_individual and not args.create_cleaned:
        print("\nNo export requested. Use --export-individual or --create-cleaned to export channels.")
        print("See --help for usage examples.")

    print("\n" + "="*80)
    print("Processing Complete!")
    print("="*80)


if __name__ == "__main__":
    main()
