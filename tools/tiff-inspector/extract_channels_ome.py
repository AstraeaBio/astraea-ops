#!/usr/bin/env python3
"""
Channel Extraction Tool for Multi-Channel TIFF Files (OME-TIFF Version)

Part of the Astraea Bio Operations Toolkit
Extracts valid channels from problematic TIFF files and creates proper OME-TIFF
format compatible with QuPath and other Bio-Formats viewers.

This version creates standards-compliant OME-TIFF files with proper multi-channel
structure and channel metadata, based on best practices from imc-converter.

Usage:
    python extract_channels_ome.py <filepath> [options]
"""

import numpy as np
import tifffile
from pathlib import Path
import argparse
import sys
import xml.etree.ElementTree as ET


def extract_channel_names(filepath):
    """
    Extract channel names from OME metadata in the TIFF file.

    Args:
        filepath: Path to TIFF file

    Returns:
        List of channel names, or None if no OME metadata
    """
    try:
        with tifffile.TiffFile(filepath) as tif:
            if not hasattr(tif, 'ome_metadata') or not tif.ome_metadata:
                return None

            # Parse OME-XML
            root = ET.fromstring(tif.ome_metadata)
            ns = {'ome': 'http://www.openmicroscopy.org/Schemas/OME/2016-06'}

            # Find all channel elements
            channels = root.findall('.//ome:Channel', ns)
            channel_names = []

            for i, channel in enumerate(channels):
                name = channel.get('Name', f'Channel_{i}')
                channel_names.append(name)

            return channel_names if channel_names else None

    except Exception as e:
        print(f"Warning: Could not extract channel names: {e}")
        return None


def find_valid_channels(filepath, min_nonzero_percent=1.0, sample_factor=100):
    """
    Scan all channels and identify which ones have actual data.

    Args:
        filepath: Path to TIFF file
        min_nonzero_percent: Minimum percentage of non-zero pixels to consider valid
        sample_factor: Downsample factor for checking (default: 100)

    Returns:
        Tuple of (valid_channels, channel_names)
        - valid_channels: List of (channel_index, stats_dict) for valid channels
        - channel_names: List of all channel names from metadata
    """
    print(f"Scanning {Path(filepath).name} for valid channels...")
    print(f"Minimum non-zero threshold: {min_nonzero_percent}%\n")

    # Extract channel names first
    channel_names = extract_channel_names(filepath)
    if channel_names:
        print(f"Found {len(channel_names)} channel names in OME metadata\n")

    valid_channels = []

    with tifffile.TiffFile(filepath) as tif:
        total_pages = len(tif.pages)
        print(f"Total pages to check: {total_pages}\n")

        for page_idx in range(total_pages):
            try:
                page = tif.pages[page_idx]

                # Get channel name if available
                ch_name = channel_names[page_idx] if channel_names and page_idx < len(channel_names) else f"Channel_{page_idx}"

                # Sample the data
                print(f"Checking channel {page_idx} ({ch_name})...", end=" ")
                sample = page.asarray()[::sample_factor, ::sample_factor]

                # Calculate statistics
                nonzero_count = np.count_nonzero(sample)
                total_count = sample.size
                nonzero_percent = 100 * nonzero_count / total_count

                stats = {
                    'name': ch_name,
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

    return valid_channels, channel_names


def create_ome_xml(channel_names, shape, dtype='uint16', physical_size_x=1.0, physical_size_y=1.0):
    """
    Create OME-XML metadata for multi-channel TIFF.

    Args:
        channel_names: List of channel names
        shape: Image shape (C, Y, X)
        dtype: Data type ('uint16', 'float', etc.)
        physical_size_x: Physical pixel size in X (microns)
        physical_size_y: Physical pixel size in Y (microns)

    Returns:
        OME-XML string
    """
    Nc, Ny, Nx = shape

    # Create channel XML elements
    channels_xml = '\n'.join([
        f'    <Channel ID="Channel:0:{i}" Name="{name}" SamplesPerPixel="1" />'
        for i, name in enumerate(channel_names)
    ])

    # Complete OME-XML following OME-TIFF specification
    ome_xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<OME xmlns="http://www.openmicroscopy.org/Schemas/OME/2016-06"
     xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
     xsi:schemaLocation="http://www.openmicroscopy.org/Schemas/OME/2016-06 http://www.openmicroscopy.org/Schemas/OME/2016-06/ome.xsd">
  <Image ID="Image:0" Name="Extracted Channels">
    <Pixels ID="Pixels:0"
            Type="{dtype}"
            DimensionOrder="XYZCT"
            SizeX="{Nx}"
            SizeY="{Ny}"
            SizeZ="1"
            SizeC="{Nc}"
            SizeT="1"
            PhysicalSizeX="{physical_size_x}"
            PhysicalSizeY="{physical_size_y}"
            PhysicalSizeXUnit="µm"
            PhysicalSizeYUnit="µm"
            Interleaved="false"
            BigEndian="false">
{channels_xml}
      <TiffData />
    </Pixels>
  </Image>
</OME>'''

    return ome_xml


def create_cleaned_ometiff(filepath, valid_channels, output_file=None, compression='lzw', channel_names_list=None):
    """
    Create a proper OME-TIFF file with only valid channels.

    This creates a standards-compliant OME-TIFF that QuPath can open properly,
    with all channels in a single multi-channel image (not separate pages).

    Args:
        filepath: Path to source TIFF
        valid_channels: List of (channel_idx, stats) tuples
        output_file: Output filename
        compression: Compression type ('lzw', 'none', 'jpeg', 'deflate')
        channel_names_list: Full list of channel names from original file

    Returns:
        Path to created file
    """
    if output_file is None:
        output_file = Path(filepath).parent / f"{Path(filepath).stem}_cleaned.ome.tiff"
    else:
        output_file = Path(output_file)

    print(f"\nCreating OME-TIFF with {len(valid_channels)} channels...")
    print(f"Output: {output_file}")

    try:
        with tifffile.TiffFile(filepath) as tif:
            # Read all valid channel data
            print("\nReading channel data...")
            channel_data = []
            channel_names = []

            for idx, (channel_idx, stats) in enumerate(valid_channels):
                print(f"  Reading channel {channel_idx} ({stats['name']}) ({idx+1}/{len(valid_channels)})...", end=" ")

                page = tif.pages[channel_idx]
                data = page.asarray()

                channel_data.append(data)
                channel_names.append(stats['name'])

                print("✓")

            # Stack into CYX format (channels, height, width)
            print("\nStacking channels...")
            stacked_data = np.stack(channel_data, axis=0)
            print(f"  Final shape: {stacked_data.shape} (C, Y, X)")
            print(f"  Data type: {stacked_data.dtype}")

            # Create OME-XML metadata
            print("\nCreating OME-XML metadata...")
            ome_xml = create_ome_xml(
                channel_names=channel_names,
                shape=stacked_data.shape,
                dtype=str(stacked_data.dtype),
                physical_size_x=1.0,  # Default 1 micron/pixel
                physical_size_y=1.0
            )

            # Determine compression
            comp = None if compression == 'none' else compression

            # Write OME-TIFF
            print(f"\nWriting OME-TIFF (compression: {compression})...")
            tifffile.imwrite(
                output_file,
                stacked_data,
                description=ome_xml,
                metadata={'axes': 'CYX'},  # Channel, Y, X
                compression=comp,
                tile=(512, 512),
                bigtiff=True
            )

            print(f"\n✓ Created OME-TIFF: {output_file}")
            print(f"  File size: {output_file.stat().st_size / (1024**3):.2f} GB")
            print(f"  Channels: {len(channel_names)}")
            print(f"  Channel names: {', '.join(channel_names[:5])}" +
                  (f"... and {len(channel_names)-5} more" if len(channel_names) > 5 else ""))

            return str(output_file)

    except Exception as e:
        print(f"\n✗ ERROR creating OME-TIFF: {e}")
        import traceback
        traceback.print_exc()
        return None


def export_channel(filepath, channel_idx, output_dir="extracted_channels",
                  compression='lzw', channel_name=None):
    """
    Export a single channel to a separate TIFF file.

    Args:
        filepath: Path to source TIFF
        channel_idx: Index of channel to export
        output_dir: Directory to save exported channel
        compression: Compression type ('lzw', 'none', 'jpeg', etc.)
        channel_name: Optional channel name for filename

    Returns:
        Path to exported file
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    filename = Path(filepath).stem

    if channel_name:
        # Sanitize channel name for filename
        safe_name = "".join(c if c.isalnum() or c in ('-', '_') else '_' for c in channel_name)
        output_file = output_path / f"{filename}_{channel_idx:03d}_{safe_name}.tiff"
    else:
        output_file = output_path / f"{filename}_channel_{channel_idx:03d}.tiff"

    print(f"Exporting channel {channel_idx}" +
          (f" ({channel_name})" if channel_name else "") +
          f" to {output_file.name}...", end=" ")

    try:
        with tifffile.TiffFile(filepath) as tif:
            page = tif.pages[channel_idx]
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


def main():
    parser = argparse.ArgumentParser(
        description="Extract valid channels and create proper OME-TIFF files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Find valid channels and show summary
  python extract_channels_ome.py image.tiff

  # Create cleaned OME-TIFF with only valid channels (RECOMMENDED)
  python extract_channels_ome.py image.tiff --create-ome-tiff --output cleaned.ome.tiff

  # Export valid channels as individual files
  python extract_channels_ome.py image.tiff --export-individual --output-dir ./channels

  # Both OME-TIFF and individual files
  python extract_channels_ome.py image.tiff --create-ome-tiff --export-individual

  # Adjust threshold for what counts as "valid"
  python extract_channels_ome.py image.tiff --threshold 5.0 --create-ome-tiff
        """
    )

    parser.add_argument('file', help='TIFF file to process')
    parser.add_argument('--threshold', '-t', type=float, default=0.1,
                       help='Minimum non-zero percentage to consider valid (default: 0.1%%)')
    parser.add_argument('--export-individual', '-e', action='store_true',
                       help='Export each valid channel as separate TIFF file')
    parser.add_argument('--create-ome-tiff', '-c', action='store_true',
                       help='Create OME-TIFF with only valid channels (RECOMMENDED for QuPath)')
    parser.add_argument('--output-dir', '-o', default='extracted_channels',
                       help='Output directory for individual channels (default: extracted_channels)')
    parser.add_argument('--output', '-O',
                       help='Output filename for OME-TIFF')
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
    print("Channel Extraction Tool (OME-TIFF Version) - Astraea Bio Operations Toolkit")
    print("="*80 + "\n")

    # Step 1: Find valid channels
    print("STEP 1: Identifying Valid Channels")
    print("="*80 + "\n")

    valid_channels, channel_names = find_valid_channels(filepath, min_nonzero_percent=args.threshold)

    if not valid_channels:
        print("\nNo valid channels found!")
        sys.exit(1)

    # Print summary
    print("\nValid Channels Summary:")
    print("-" * 80)
    print(f"{'Channel':<10} {'Name':<20} {'Max Value':<12} {'Non-zero %':<12}")
    print("-" * 80)

    for channel_idx, stats in valid_channels:
        print(f"{channel_idx:<10} {stats['name']:<20} {stats['max']:<12} "
              f"{stats['nonzero_percent']:<12.2f}")

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
            f.write(f"Channel {channel_idx}: {stats['name']}\n")
            for key, value in stats.items():
                if key != 'name':
                    f.write(f"  {key}: {value}\n")
            f.write("\n")

    print(f"\nSaved detailed summary to: {summary_file}")

    # Step 2: Create OME-TIFF if requested
    if args.create_ome_tiff:
        print("\n" + "="*80)
        print("STEP 2: Creating OME-TIFF with Valid Channels")
        print("="*80 + "\n")

        create_cleaned_ometiff(filepath, valid_channels, args.output, args.compression, channel_names)

    # Step 3: Export individual channels if requested
    if args.export_individual:
        print("\n" + "="*80)
        print(f"STEP {'3' if args.create_ome_tiff else '2'}: Exporting Individual Channels")
        print("="*80 + "\n")

        num_to_export = min(len(valid_channels), args.max_export)
        if len(valid_channels) > args.max_export:
            print(f"Limiting export to first {args.max_export} channels (use --max-export to change)\n")

        for channel_idx, stats in valid_channels[:num_to_export]:
            export_channel(filepath, channel_idx, args.output_dir, args.compression, stats['name'])

    if not args.export_individual and not args.create_ome_tiff:
        print("\nNo export requested. Use --create-ome-tiff or --export-individual to export channels.")
        print("See --help for usage examples.")
        print("\nRECOMMENDED: Use --create-ome-tiff to create a QuPath-compatible file.")

    print("\n" + "="*80)
    print("Processing Complete!")
    print("="*80)


if __name__ == "__main__":
    main()
