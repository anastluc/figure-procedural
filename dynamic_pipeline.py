#!/usr/bin/env python3
"""
Dynamic Pipeline: Generate collages by creating images on-demand with random parameters.

Instead of pre-generating all possible combinations, this script generates each
collage image dynamically by randomly selecting parameter values from specified ranges.
"""

import os
import sys
import argparse
import random
import re
from tqdm import tqdm
from PIL import Image

def parse_parameter(param_str, is_color=False):
    """
    Parse parameter string into either a range or a list of choices.

    Formats:
    - Range: "[100,150]" -> returns ('range', 100, 150)
    - List: "10,20,30" -> returns ('list', [10, 20, 30])
    - Single value: "100" -> returns ('single', 100)

    Parameters:
    - is_color: If True, keep values as strings instead of converting to int

    Returns:
    - tuple: (type, value(s))
    """
    if not param_str:
        return None

    param_str = param_str.strip()

    # Check if it's a range [min,max] (only for non-color params)
    if not is_color:
        range_match = re.match(r'\[(\d+),(\d+)\]', param_str)
        if range_match:
            min_val = int(range_match.group(1))
            max_val = int(range_match.group(2))
            return ('range', min_val, max_val)

    # Otherwise it's a comma-separated list
    values = [v.strip() for v in param_str.split(',')]

    # For colors, always keep as strings
    if is_color:
        if len(values) == 1:
            return ('single', values[0])
        return ('list', values)

    # Try to convert to integers
    try:
        int_values = [int(v) for v in values]
        if len(int_values) == 1:
            return ('single', int_values[0])
        return ('list', int_values)
    except ValueError:
        # Not integers, keep as strings
        if len(values) == 1:
            return ('single', values[0])
        return ('list', values)

def select_random_value(param_config):
    """
    Select a random value based on parameter configuration.

    Parameters:
    - param_config: tuple from parse_parameter()

    Returns:
    - Random value based on the parameter type
    """
    if param_config is None:
        return None

    param_type = param_config[0]

    if param_type == 'range':
        min_val, max_val = param_config[1], param_config[2]
        return random.randint(min_val, max_val)
    elif param_type == 'list':
        return random.choice(param_config[1])
    elif param_type == 'single':
        return param_config[1]

    return None

def main():
    parser = argparse.ArgumentParser(
        description='Dynamic Pipeline: Generate collages with on-demand random figure generation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate 10x10 collage with dynamic random parameters
  %(prog)s --a=[100,150] --b=[50,60] --stroke_color=000000,444444 \\
           --grid_size 10x10 --output_collage_file ./my_collage.png

  # With flipping and specific parameter ranges
  %(prog)s --a=[100,150] --b=[50,60] --c=[40,40] --d=[50,60] --e=[10,30] \\
           --f=[10,30] --g=40,50 --stroke_width=10 \\
           --stroke_color=000000,000088,008800,880000,888800,880088,008888,8800ff,8888ff,ff0000,00ff00,0000ff,ff00ff,00ffff \\
           --output_folder ./my_figures_3 --grid_size 10x10 --flip 0.5

Parameter Formats:
  - Range: --a=[100,150]  (randomly select integer between 100-150)
  - List: --g=40,50       (randomly select from: 40 or 50)
  - Single: --stroke_width=10  (always use value 10)
        """
    )

    # Figure generation parameters
    gen_group = parser.add_argument_group('Figure Generation Parameters')
    gen_group.add_argument('--a', type=str, help='Parameter a: range [min,max] or list of values')
    gen_group.add_argument('--b', type=str, help='Parameter b: range [min,max] or list of values')
    gen_group.add_argument('--c', type=str, help='Parameter c: range [min,max] or list of values')
    gen_group.add_argument('--d', type=str, help='Parameter d: range [min,max] or list of values')
    gen_group.add_argument('--e', type=str, help='Parameter e: range [min,max] or list of values')
    gen_group.add_argument('--f', type=str, help='Parameter f: range [min,max] or list of values')
    gen_group.add_argument('--g', type=str, help='Parameter g: range [min,max] or list of values')
    gen_group.add_argument('--stroke_width', type=str, help='Stroke width: range [min,max] or list of values')
    gen_group.add_argument('--stroke_color', type=str, help='Stroke colors without # (comma-separated, e.g., "000000,444444")')

    # Output parameters
    parser.add_argument(
        '--output_folder', '-o',
        type=str,
        help='Output folder to save individual generated figures (optional)'
    )
    parser.add_argument(
        '--output_collage_file',
        type=str,
        required=True,
        help='Output file path for the final collage (e.g., ./my_collage.png)'
    )

    # Collage parameters
    collage_group = parser.add_argument_group('Collage Parameters')
    collage_group.add_argument(
        '--grid_size', '-g',
        type=str,
        required=True,
        help='Grid size for collage in format COLSxROWS (e.g., 10x10)'
    )
    collage_group.add_argument(
        '--flip',
        type=float,
        default=0.0,
        help='Probability (0.0-1.0) that each image will be flipped horizontally (default: 0.0)'
    )

    args = parser.parse_args()

    # Parse grid size
    try:
        cols, rows = map(int, args.grid_size.lower().split('x'))
    except ValueError:
        print(f"Error: Invalid grid_size format '{args.grid_size}'. Use format like '10x10'")
        sys.exit(1)

    total_images = cols * rows

    print("=" * 60)
    print("DYNAMIC PIPELINE: On-Demand Figure Generation")
    print("=" * 60)

    # Parse all parameter configurations
    param_configs = {
        'a': parse_parameter(args.a),
        'b': parse_parameter(args.b),
        'c': parse_parameter(args.c),
        'd': parse_parameter(args.d),
        'e': parse_parameter(args.e),
        'f': parse_parameter(args.f),
        'g': parse_parameter(args.g),
        'stroke_width': parse_parameter(args.stroke_width),
        'stroke_color': parse_parameter(args.stroke_color, is_color=True),
    }

    # Set defaults for unspecified parameters
    defaults = {
        'a': ('single', 100),
        'b': ('single', 50),
        'c': ('single', 50),
        'd': ('single', 20),
        'e': ('single', 20),
        'f': ('single', 20),
        'g': ('single', 15),
        'stroke_width': ('single', 3),
        'stroke_color': ('single', '000000'),
    }

    for key, value in defaults.items():
        if param_configs[key] is None:
            param_configs[key] = value

    # Display parameter configurations
    print(f"\nGenerating {total_images} images ({cols}x{rows} grid) with random parameters:")
    for key, config in param_configs.items():
        if config[0] == 'range':
            print(f"  {key}: random from range [{config[1]}, {config[2]}]")
        elif config[0] == 'list':
            print(f"  {key}: random from {config[1]}")
        elif config[0] == 'single':
            print(f"  {key}: fixed value {config[1]}")

    if args.flip > 0:
        print(f"  flip: {args.flip*100:.0f}% chance per image")

    # Import generation function
    try:
        from generate_figures_simple import generate_figure
    except ImportError as e:
        print(f"Error importing generate_figures_simple: {e}")
        sys.exit(1)

    # Create output folder if specified
    if args.output_folder:
        os.makedirs(args.output_folder, exist_ok=True)
        print(f"\nSaving individual figures to: {args.output_folder}/")

    # Create output directory for collage
    collage_dir = os.path.dirname(args.output_collage_file)
    if collage_dir and not os.path.exists(collage_dir):
        os.makedirs(collage_dir, exist_ok=True)

    print(f"\nGenerating collage...")

    # Generate images and build collage
    images = []
    flip_count = 0

    for i in tqdm(range(total_images), desc="Generating images", unit="img"):
        # Randomly select parameter values
        a = select_random_value(param_configs['a'])
        b = select_random_value(param_configs['b'])
        c = select_random_value(param_configs['c'])
        d = select_random_value(param_configs['d'])
        e = select_random_value(param_configs['e'])
        f = select_random_value(param_configs['f'])
        g = select_random_value(param_configs['g'])
        stroke_width = select_random_value(param_configs['stroke_width'])
        stroke_color_code = select_random_value(param_configs['stroke_color'])

        # Add # prefix to color
        stroke_color = f'#{stroke_color_code}'

        # Generate the figure
        img = generate_figure(a, b, c, d, e, f, g, stroke_width, stroke_color)

        # Apply horizontal flip if needed
        if random.random() < args.flip:
            img = img.transpose(Image.FLIP_LEFT_RIGHT)
            flip_count += 1

        # Save individual image if output folder specified
        if args.output_folder:
            filename = f"fig_a{a}_b{b}_c{c}_d{d}_e{e}_f{f}_g{g}_w{stroke_width}_col{stroke_color_code}.png"
            filepath = os.path.join(args.output_folder, filename)
            img.save(filepath, 'PNG')

        images.append(img)

    # Get dimensions from first image
    img_width, img_height = images[0].size

    # Create collage canvas
    collage_width = cols * img_width
    collage_height = rows * img_height
    collage = Image.new('RGB', (collage_width, collage_height), 'white')

    # Place images in grid
    print("\nAssembling collage...")
    for idx, img in enumerate(images):
        row = idx // cols
        col = idx % cols
        x = col * img_width
        y = row * img_height
        collage.paste(img, (x, y))

    # Save collage
    collage.save(args.output_collage_file, 'PNG')

    # Calculate file size
    file_size_mb = os.path.getsize(args.output_collage_file) / (1024 * 1024)

    print("\n" + "=" * 60)
    print("PIPELINE COMPLETE!")
    print("=" * 60)
    print(f"Generated {total_images} unique images")
    if args.flip > 0:
        print(f"Flipped {flip_count}/{total_images} images ({flip_count/total_images*100:.1f}%)")
    print(f"\nCollage saved: {args.output_collage_file}")
    print(f"  Size: {collage_width}x{collage_height}px ({file_size_mb:.2f} MB)")
    if args.output_folder:
        print(f"\nIndividual figures saved to: {args.output_folder}/")

if __name__ == '__main__':
    main()
