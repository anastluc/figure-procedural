#!/usr/bin/env python3
"""
Create collages from generated figure images in various grid arrangements.

Usage:
    python create_collages.py --grid_size 5x5 --images_folder ./data
    python create_collages.py --grid_size 10x10 --images_folder ./data_simple --output_folder ./my_collages
"""

import os
import sys
import random
import argparse
from PIL import Image

# Canvas dimensions from original script
CANVAS_WIDTH = 300
CANVAS_HEIGHT = 500

def create_collage(image_paths, cols, rows, output_path, flip_hor=0.0, flip_ver=0.0):
    """
    Create a collage from a list of image paths.

    Parameters:
    - image_paths: list of paths to images
    - cols: number of columns in grid
    - rows: number of rows in grid
    - output_path: path to save the collage
    - flip_hor: probability (0.0-1.0) that an image will be flipped horizontally
    - flip_ver: probability (0.0-1.0) that an image will be flipped vertically
    """
    num_images = cols * rows

    # Randomly select images for this collage (with replacement to allow duplicates)
    # This allows creating large grids even with a small sample of images
    selected_images = random.choices(image_paths, k=num_images)

    # Create blank canvas for collage
    collage_width = CANVAS_WIDTH * cols
    collage_height = CANVAS_HEIGHT * rows
    collage = Image.new('RGB', (collage_width, collage_height), 'white')

    # Track flips for statistics
    flipped_hor_count = 0
    flipped_ver_count = 0

    # Place images in grid
    for idx, img_path in enumerate(selected_images):
        row = idx // cols
        col = idx % cols

        # Calculate position
        x = col * CANVAS_WIDTH
        y = row * CANVAS_HEIGHT

        # Load and paste image
        try:
            img = Image.open(img_path)

            # Randomly flip image horizontally based on flip_hor
            if random.random() < flip_hor:
                img = img.transpose(Image.FLIP_LEFT_RIGHT)
                flipped_hor_count += 1

            # Randomly flip image vertically based on flip_ver
            if random.random() < flip_ver:
                img = img.transpose(Image.FLIP_TOP_BOTTOM)
                flipped_ver_count += 1

            collage.paste(img, (x, y))
        except Exception as e:
            print(f"Error loading {img_path}: {e}")
            continue

        # Progress indicator
        if (idx + 1) % 20 == 0:
            print(f"  Placed {idx + 1}/{num_images} images...")

    # Save collage
    collage.save(output_path, 'PNG')

    if flip_hor > 0:
        print(f"Flipped horizontally {flipped_hor_count}/{num_images} images ({100*flipped_hor_count/num_images:.1f}%)")
    if flip_ver > 0:
        print(f"Flipped vertically {flipped_ver_count}/{num_images} images ({100*flipped_ver_count/num_images:.1f}%)")

    print(f"Saved collage: {output_path}")
    return True

def filter_images_by_params(image_paths, filter_params):
    """
    Filter images based on parameter specifications from filenames.

    Parameters:
    - image_paths: list of image file paths
    - filter_params: comma-separated string like 'a100,b50,col444444'

    Returns:
    - filtered list of image paths
    """
    if not filter_params:
        return image_paths

    # Parse filter parameters
    filters = [f.strip() for f in filter_params.split(',')]

    filtered_images = []
    for img_path in image_paths:
        filename = os.path.basename(img_path)

        # Check if all filter criteria match in filename
        match = True
        for filter_str in filters:
            # Convert filter to pattern that appears in filename
            # e.g., 'a100' should match '_a100_' or '_a100.'
            # e.g., 'col444444' should match '_col444444_' or '_col444444.'
            pattern = f"_{filter_str}_"
            pattern_end = f"_{filter_str}."

            if pattern not in filename and pattern_end not in filename:
                match = False
                break

        if match:
            filtered_images.append(img_path)

    return filtered_images

def parse_grid_size(grid_str):
    """
    Parse grid size string like '5x5' into (cols, rows) tuple.

    Parameters:
    - grid_str: string in format 'COLSxROWS' (e.g., '5x5', '10x16')

    Returns:
    - tuple of (cols, rows)
    """
    try:
        parts = grid_str.lower().split('x')
        if len(parts) != 2:
            raise ValueError("Grid size must be in format 'COLSxROWS' (e.g., '5x5')")

        cols = int(parts[0])
        rows = int(parts[1])

        if cols <= 0 or rows <= 0:
            raise ValueError("Grid dimensions must be positive integers")

        return (cols, rows)
    except ValueError as e:
        raise ValueError(f"Invalid grid size '{grid_str}': {e}")

def main():
    """Generate collages from generated figure images."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Create collages from generated figure images',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --grid_size 5x5 --images_folder ./data
  %(prog)s --grid_size 10x16 --images_folder ./data_simple --output_folder ./my_collages
  %(prog)s -g 8x10 -i ./data -o ./collages --flip 0.5
  %(prog)s -g 5x5 -i ./data -f 0.3
  %(prog)s -g 10x10 -i ./data_simple -s "a100,b50,col444444"
  %(prog)s -g 5x5 -i ./data_simple --select_only_from "w3,c50"
        """
    )

    parser.add_argument(
        '--grid_size', '-g',
        type=str,
        required=True,
        help='Grid size in format COLSxROWS (e.g., 5x5, 10x16)'
    )

    parser.add_argument(
        '--images_folder', '-i',
        type=str,
        required=True,
        help='Path to folder containing images'
    )

    parser.add_argument(
        '--output_folder', '-o',
        type=str,
        default='./collages',
        help='Path to output folder for collages (default: ./collages)'
    )

    parser.add_argument(
        '--flip_hor',
        type=float,
        default=0.0,
        help='Probability (0.0-1.0) that each image will be flipped horizontally (default: 0.0)'
    )

    parser.add_argument(
        '--flip_ver',
        type=float,
        default=0.0,
        help='Probability (0.0-1.0) that each image will be flipped vertically (default: 0.0)'
    )

    parser.add_argument(
        '--select_only_from', '-s',
        type=str,
        default=None,
        help='Filter images by parameters (e.g., "a100,b50,col444444" selects only images with a=100, b=50, color=444444)'
    )

    args = parser.parse_args()

    # Validate flip parameters
    if not 0.0 <= args.flip_hor <= 1.0:
        print(f"Error: flip_hor must be between 0.0 and 1.0, got {args.flip_hor}")
        sys.exit(1)
    if not 0.0 <= args.flip_ver <= 1.0:
        print(f"Error: flip_ver must be between 0.0 and 1.0, got {args.flip_ver}")
        sys.exit(1)

    # Parse grid size
    try:
        cols, rows = parse_grid_size(args.grid_size)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Validate input directory
    if not os.path.isdir(args.images_folder):
        print(f"Error: Images folder '{args.images_folder}' does not exist")
        sys.exit(1)

    # Create output directory
    output_dir = args.output_folder
    os.makedirs(output_dir, exist_ok=True)

    # Get all PNG files from images directory
    print(f"Scanning {args.images_folder} for images...")
    image_files = [
        os.path.join(args.images_folder, f)
        for f in os.listdir(args.images_folder)
        if f.endswith('.png')
    ]

    if not image_files:
        print(f"Error: No PNG images found in {args.images_folder}")
        sys.exit(1)

    print(f"Found {len(image_files)} images")

    # Filter images if select_only_from is specified
    if args.select_only_from:
        original_count = len(image_files)
        image_files = filter_images_by_params(image_files, args.select_only_from)

        if not image_files:
            print(f"Error: No images match the filter criteria '{args.select_only_from}'")
            sys.exit(1)

        print(f"Filtered to {len(image_files)} images matching '{args.select_only_from}' (from {original_count} total)")

    # Create collage
    num_images = cols * rows
    flip_info = ""
    if args.flip_hor > 0:
        flip_info += f" {args.flip_hor*100:.0f}% horizontal flip"
    if args.flip_ver > 0:
        if flip_info:
            flip_info += ","
        flip_info += f" {args.flip_ver*100:.0f}% vertical flip"
    if flip_info:
        flip_info = f" with{flip_info}"

    print(f"\nCreating {cols}x{rows} collage ({num_images} images){flip_info}...")

    # Include flip values in filename
    flip_str = ""
    if args.flip_hor > 0 or args.flip_ver > 0:
        flip_str = f"_fh{args.flip_hor:.2f}_fv{args.flip_ver:.2f}".replace('.', '_')
    output_filename = f"collage_{cols}x{rows}{flip_str}.png"
    output_path = os.path.join(output_dir, output_filename)

    success = create_collage(image_files, cols, rows, output_path, args.flip_hor, args.flip_ver)

    if success:
        # Calculate file size
        file_size = os.path.getsize(output_path) / (1024 * 1024)  # MB
        print(f"  Size: {CANVAS_WIDTH * cols}x{CANVAS_HEIGHT * rows}px ({file_size:.2f} MB)")
        print(f"\nCollage saved to {output_path}")
    else:
        print("\nFailed to create collage")
        sys.exit(1)

if __name__ == '__main__':
    main()
