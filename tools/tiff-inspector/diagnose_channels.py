#!/usr/bin/env python3
"""
Multi-Channel TIFF Diagnostic Tool

Part of the Astraea Bio Operations Toolkit
Diagnoses multi-channel TIFF files to identify which channels contain actual data
and extract OME metadata for troubleshooting.

Usage:
    python diagnose_channels.py <filepath> [options]
"""

import numpy as np
import tifffile
from pathlib import Path
import argparse
import sys


def diagnose_channels(filepath, sample_factor=100, max_channels=None, output_dir=None):
    """Check all channels/pages for data presence and statistics."""
    print(f"\n{'='*80}")
    print(f"Diagnosing: {Path(filepath).name}")
    print(f"{'='*80}")

    with tifffile.TiffFile(filepath) as tif:
        print(f"\nTotal pages: {len(tif.pages)}")
        print(f"Series: {len(tif.series)}")

        # Check series structure
        for i, series in enumerate(tif.series):
            print(f"\nSeries {i}:")
            print(f"  Shape: {series.shape}")
            print(f"  Dtype: {series.dtype}")
            print(f"  Axes: {series.axes}")

        # Check each page for data
        print(f"\n{'='*80}")
        print("Checking each page for data...")
        print(f"{'='*80}")

        num_channels_to_check = max_channels if max_channels else len(tif.pages)
        num_channels_to_check = min(num_channels_to_check, len(tif.pages))

        channel_stats = []

        for page_idx in range(num_channels_to_check):
            try:
                page = tif.pages[page_idx]

                # Read a downsampled version to check for data
                data_sample = page.asarray()[::sample_factor, ::sample_factor]

                has_data = data_sample.max() > 0
                nonzero_count = np.count_nonzero(data_sample)
                total_count = data_sample.size

                stats = {
                    'channel': page_idx,
                    'shape': page.shape,
                    'has_data': has_data,
                    'min': int(data_sample.min()),
                    'max': int(data_sample.max()),
                    'mean': float(data_sample.mean()),
                    'nonzero_percent': 100 * nonzero_count / total_count
                }

                channel_stats.append(stats)

                print(f"\nPage/Channel {page_idx}:")
                print(f"  Shape: {page.shape}")
                print(f"  Has data: {has_data}")
                print(f"  Sample stats: min={stats['min']}, max={stats['max']}, "
                      f"mean={stats['mean']:.2f}")
                print(f"  Non-zero pixels in sample: {nonzero_count}/{total_count} "
                      f"({stats['nonzero_percent']:.2f}%)")

                # If has data and output dir specified, save a sample
                if has_data and output_dir and page_idx < 10:  # Limit to first 10 channels
                    output_path = Path(output_dir)
                    output_path.mkdir(parents=True, exist_ok=True)
                    sample_region = page.asarray()[::50, ::50]  # More detailed sample
                    output_file = output_path / f"channel_{page_idx:03d}_sample.npy"
                    np.save(str(output_file), sample_region)
                    print(f"  Saved sample to: {output_file}")

            except Exception as e:
                print(f"\nPage {page_idx}: ERROR - {e}")
                channel_stats.append({
                    'channel': page_idx,
                    'error': str(e)
                })

        # Check for OME-XML metadata
        print(f"\n{'='*80}")
        print("Checking OME-XML metadata...")
        print(f"{'='*80}")

        ome_metadata = None
        if hasattr(tif, 'ome_metadata'):
            ome_xml = tif.ome_metadata
            if ome_xml:
                print("\nOME-XML found")
                print(f"Length: {len(ome_xml)} characters")

                # Save full OME-XML if output dir specified
                if output_dir:
                    output_path = Path(output_dir)
                    output_path.mkdir(parents=True, exist_ok=True)
                    output_file = output_path / f"{Path(filepath).stem}_ome_metadata.xml"
                    with open(output_file, 'w') as f:
                        f.write(ome_xml)
                    print(f"Saved full OME-XML to: {output_file}")

                ome_metadata = ome_xml

        # Save channel statistics summary
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            summary_file = output_path / f"{Path(filepath).stem}_channel_stats.txt"
            with open(summary_file, 'w') as f:
                f.write("Channel Statistics Summary\n")
                f.write("=" * 80 + "\n\n")
                for stats in channel_stats:
                    f.write(f"Channel {stats['channel']}:\n")
                    if 'error' in stats:
                        f.write(f"  ERROR: {stats['error']}\n")
                    else:
                        f.write(f"  Has data: {stats['has_data']}\n")
                        f.write(f"  Min: {stats['min']}\n")
                        f.write(f"  Max: {stats['max']}\n")
                        f.write(f"  Mean: {stats['mean']:.2f}\n")
                        f.write(f"  Non-zero: {stats['nonzero_percent']:.2f}%\n")
                    f.write("\n")
            print(f"\n\nSaved channel statistics to: {summary_file}")

        return channel_stats, ome_metadata


def check_data_distribution(filepath, channel=0, num_regions=5):
    """
    Check data distribution across the image for a specific channel.
    Samples multiple regions to see if data exists anywhere.
    """
    print(f"\n{'='*80}")
    print(f"Checking data distribution for channel {channel}")
    print(f"{'='*80}")

    with tifffile.TiffFile(filepath) as tif:
        if channel >= len(tif.pages):
            print(f"ERROR: Channel {channel} doesn't exist (only {len(tif.pages)} pages)")
            return None

        page = tif.pages[channel]
        height, width = page.shape[:2]

        # Sample from different regions
        region_size = 2000
        regions = [
            ("Top-left", 0, 0),
            ("Top-right", 0, max(0, width - region_size)),
            ("Center", max(0, height // 2 - region_size // 2), max(0, width // 2 - region_size // 2)),
            ("Bottom-left", max(0, height - region_size), 0),
            ("Bottom-right", max(0, height - region_size), max(0, width - region_size)),
        ]

        print(f"Image size: {width} x {height}")
        print(f"Sampling {region_size}x{region_size} regions from different locations...\n")

        distribution_stats = []
        for name, y, x in regions[:num_regions]:
            # Make sure we don't go out of bounds
            y = max(0, min(y, height - region_size))
            x = max(0, min(x, width - region_size))
            actual_height = min(region_size, height - y)
            actual_width = min(region_size, width - x)

            region = page.asarray()[y:y+actual_height, x:x+actual_width]

            stats = {
                'location': name,
                'x': x,
                'y': y,
                'min': int(region.min()),
                'max': int(region.max()),
                'mean': float(region.mean()),
                'nonzero_percent': 100 * np.count_nonzero(region) / region.size
            }

            distribution_stats.append(stats)

            print(f"{name} ({x},{y}):")
            print(f"  min={stats['min']}, max={stats['max']}, mean={stats['mean']:.2f}")
            print(f"  Non-zero: {np.count_nonzero(region)}/{region.size} "
                  f"({stats['nonzero_percent']:.2f}%)")

            del region

        return distribution_stats


def main():
    parser = argparse.ArgumentParser(
        description="Diagnose multi-channel TIFF files to identify channels with data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic diagnosis
  python diagnose_channels.py image.tiff

  # Save samples and metadata
  python diagnose_channels.py image.tiff --output-dir ./diagnosis_output

  # Check specific channels with detailed distribution
  python diagnose_channels.py image.tiff --check-distribution 0 3 5

  # Limit number of channels to check
  python diagnose_channels.py image.tiff --max-channels 10
        """
    )

    parser.add_argument('file', help='TIFF file to diagnose')
    parser.add_argument('--output-dir', '-o', help='Directory to save diagnostic outputs')
    parser.add_argument('--sample-factor', '-s', type=int, default=100,
                       help='Downsample factor for quick checks (default: 100)')
    parser.add_argument('--max-channels', '-m', type=int,
                       help='Maximum number of channels to check (default: all)')
    parser.add_argument('--check-distribution', '-d', nargs='+', type=int,
                       help='Check data distribution for specific channel(s)')

    args = parser.parse_args()

    filepath = str(Path(args.file).resolve())

    if not Path(filepath).exists():
        print(f"ERROR: File not found: {filepath}")
        sys.exit(1)

    print("="*80)
    print("Multi-Channel TIFF Diagnostic Tool - Astraea Bio Operations Toolkit")
    print("="*80)

    # Run main diagnosis
    channel_stats, ome_metadata = diagnose_channels(
        filepath,
        sample_factor=args.sample_factor,
        max_channels=args.max_channels,
        output_dir=args.output_dir
    )

    # Check distribution for specific channels if requested
    if args.check_distribution:
        print("\n\n" + "="*80)
        print("DETAILED DATA DISTRIBUTION CHECK")
        print("="*80)

        for channel in args.check_distribution:
            check_data_distribution(filepath, channel)

    # Print summary
    print("\n\n" + "="*80)
    print("SUMMARY")
    print("="*80)

    channels_with_data = [s for s in channel_stats if s.get('has_data', False)]
    channels_empty = [s for s in channel_stats if not s.get('has_data', True)]
    channels_error = [s for s in channel_stats if 'error' in s]

    print(f"Total channels checked: {len(channel_stats)}")
    print(f"Channels with data: {len(channels_with_data)}")
    print(f"Empty channels: {len(channels_empty)}")
    print(f"Channels with errors: {len(channels_error)}")

    if channels_with_data:
        print(f"\nChannels with data: {[s['channel'] for s in channels_with_data]}")


if __name__ == "__main__":
    main()
