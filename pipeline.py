#!/usr/bin/env python3
"""
Pipeline script to generate procedural figures and create collages in one command.

Combines figure generation and collage creation into a single workflow.
"""

import os
import sys
import argparse
import subprocess

def parse_range_param(param_str, as_int=True):
    """
    Parse parameter range string like '50,100,150' into a list.

    Parameters:
    - param_str: comma-separated values
    - as_int: whether to convert values to integers (True) or keep as strings (False)

    Returns:
    - list of values (as integers or strings depending on parameter type)
    """
    if not param_str:
        return None
    values = [p.strip() for p in param_str.split(',')]
    if as_int:
        return [int(v) for v in values]
    return values

def main():
    parser = argparse.ArgumentParser(
        description='Pipeline: Generate figures and create collages in one command',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate figures with custom parameters and create a 10x10 collage
  %(prog)s --a=100,130,150 --b=50,100 --output_folder ./my_figures --grid_size 10x10

  # Full pipeline with filtering and flipping
  %(prog)s --a=100,150 --stroke_color=000000,444444 --output_folder ./figures \\
           --grid_size 8x8 --flip 0.5 --select_only_from "a100,col000000"

  # Generate only (skip collage)
  %(prog)s --a=100,130 --b=50,100 --output_folder ./figures --skip_collage
        """
    )

    # Figure generation parameters
    gen_group = parser.add_argument_group('Figure Generation Parameters')
    gen_group.add_argument('--a', type=str, help='Values for parameter a (comma-separated, e.g., "100,130,150")')
    gen_group.add_argument('--b', type=str, help='Values for parameter b (comma-separated)')
    gen_group.add_argument('--c', type=str, help='Values for parameter c (comma-separated)')
    gen_group.add_argument('--d', type=str, help='Values for parameter d (comma-separated)')
    gen_group.add_argument('--e', type=str, help='Values for parameter e (comma-separated)')
    gen_group.add_argument('--f', type=str, help='Values for parameter f (comma-separated)')
    gen_group.add_argument('--g', type=str, help='Values for parameter g (comma-separated)')
    gen_group.add_argument('--stroke_width', type=str, help='Stroke width values (comma-separated)')
    gen_group.add_argument('--stroke_color', type=str, help='Stroke colors without # (comma-separated, e.g., "000000,444444")')

    # Output folder
    parser.add_argument(
        '--output_folder', '-o',
        type=str,
        required=True,
        help='Output folder for generated figures (will be input for collage)'
    )

    # Collage parameters
    collage_group = parser.add_argument_group('Collage Parameters')
    collage_group.add_argument(
        '--grid_size', '-g',
        type=str,
        help='Grid size for collage in format COLSxROWS (e.g., 10x10)'
    )
    collage_group.add_argument(
        '--flip',
        type=float,
        default=0.0,
        help='Probability (0.0-1.0) that each image will be flipped horizontally (default: 0.0)'
    )
    collage_group.add_argument(
        '--select_only_from', '-s',
        type=str,
        help='Filter images by parameters for collage (e.g., "a100,b50,col444444")'
    )
    collage_group.add_argument(
        '--collage_output',
        type=str,
        default='./collages',
        help='Output folder for collages (default: ./collages)'
    )

    # Pipeline control
    parser.add_argument(
        '--skip_collage',
        action='store_true',
        help='Skip collage creation, only generate figures'
    )
    parser.add_argument(
        '--skip_generation',
        action='store_true',
        help='Skip figure generation, only create collage from existing images'
    )

    args = parser.parse_args()

    # Validate that at least one operation is requested
    if args.skip_collage and args.skip_generation:
        print("Error: Cannot skip both generation and collage creation")
        sys.exit(1)

    # === STEP 1: Generate Figures ===
    if not args.skip_generation:
        print("=" * 60)
        print("STEP 1: Generating Figures")
        print("=" * 60)

        # Build parameter ranges dictionary
        param_ranges = {}

        if args.a:
            param_ranges['a'] = parse_range_param(args.a)
        if args.b:
            param_ranges['b'] = parse_range_param(args.b)
        if args.c:
            param_ranges['c'] = parse_range_param(args.c)
        if args.d:
            param_ranges['d'] = parse_range_param(args.d)
        if args.e:
            param_ranges['e'] = parse_range_param(args.e)
        if args.f:
            param_ranges['f'] = parse_range_param(args.f)
        if args.g:
            param_ranges['g'] = parse_range_param(args.g)
        if args.stroke_width:
            param_ranges['stroke_width'] = parse_range_param(args.stroke_width, as_int=True)
        if args.stroke_color:
            # Add # prefix to color codes
            param_ranges['stroke_color'] = [f'#{c}' for c in parse_range_param(args.stroke_color, as_int=False)]

        if not param_ranges:
            print("Warning: No generation parameters specified, using defaults from generate_figures_simple.py")
            print("You can specify parameters like: --a=100,130,150 --b=50,100")

        # Import generation functions
        try:
            from generate_figures_simple import generate_figure
            from itertools import product
        except ImportError as e:
            print(f"Error importing generate_figures_simple: {e}")
            sys.exit(1)

        # Build default parameter ranges
        default_param_ranges = {
            'a': [100, 130, 150],
            'b': [50, 100, 125],
            'c': [50, 60],
            'd': [20, 40, 60],
            'e': [20, 30],
            'f': [20, 40],
            'g': [15, 30],
            'stroke_width': [3, 6],
            'stroke_color': ['#000000', '#222222', '#444444', '#666666']
        }

        # Override with custom parameters if provided
        if param_ranges:
            for key, value in param_ranges.items():
                default_param_ranges[key] = value

        # Create output directory
        os.makedirs(args.output_folder, exist_ok=True)

        # Calculate total combinations
        total = 1
        for param_range in default_param_ranges.values():
            total *= len(param_range)

        print(f"Generating {total:,} images...")
        print(f"Output directory: {args.output_folder}")

        # Generate all combinations
        count = 0
        param_names = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'stroke_width', 'stroke_color']
        param_values = [default_param_ranges[name] for name in param_names]

        for combination in product(*param_values):
            a, b, c, d, e, f, g, stroke_width, stroke_color = combination

            # Generate the figure
            img = generate_figure(a, b, c, d, e, f, g, stroke_width, stroke_color)

            # Create filename (remove # from color for filename)
            color_code = stroke_color.replace('#', '')
            filename = f"fig_a{a}_b{b}_c{c}_d{d}_e{e}_f{f}_g{g}_w{stroke_width}_col{color_code}.png"
            filepath = os.path.join(args.output_folder, filename)

            # Save the image
            img.save(filepath, 'PNG')

            count += 1

            # Progress update every 100 images
            if count % 100 == 0:
                print(f"Progress: {count:,}/{total:,} ({100*count/total:.1f}%)")

        print(f"\nCompleted! Generated {count:,} images in {args.output_folder}/")

        print("\n✓ Figure generation complete")

    # === STEP 2: Create Collage ===
    if not args.skip_collage:
        if not args.grid_size:
            print("\nSkipping collage creation (--grid_size not specified)")
            print("To create a collage, add: --grid_size 10x10")
        else:
            print("\n" + "=" * 60)
            print("STEP 2: Creating Collage")
            print("=" * 60)

            # Check if output folder exists and has images
            if not os.path.isdir(args.output_folder):
                print(f"Error: Output folder '{args.output_folder}' does not exist")
                sys.exit(1)

            image_count = len([f for f in os.listdir(args.output_folder) if f.endswith('.png')])
            if image_count == 0:
                print(f"Error: No PNG images found in '{args.output_folder}'")
                sys.exit(1)

            print(f"Found {image_count} images in {args.output_folder}")

            # Build collage command
            collage_cmd = [
                'python3', 'create_collages.py',
                '--grid_size', args.grid_size,
                '--images_folder', args.output_folder,
                '--output_folder', args.collage_output,
                '--flip', str(args.flip)
            ]

            if args.select_only_from:
                collage_cmd.extend(['--select_only_from', args.select_only_from])

            # Execute collage creation
            print(f"\nRunning: {' '.join(collage_cmd)}\n")
            result = subprocess.run(collage_cmd)

            if result.returncode != 0:
                print("\n✗ Collage creation failed")
                sys.exit(1)

            print("\n✓ Collage creation complete")

    print("\n" + "=" * 60)
    print("PIPELINE COMPLETE!")
    print("=" * 60)
    if not args.skip_generation:
        print(f"Generated figures: {args.output_folder}/")
    if not args.skip_collage and args.grid_size:
        print(f"Collages saved to: {args.collage_output}/")

if __name__ == '__main__':
    main()
