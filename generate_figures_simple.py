#!/usr/bin/env python3
"""
Generate procedural figures with simplified straight-line logic (no angles).
Creates a series of geometric line drawings based on specified parameters.
"""

import os
import math
from PIL import Image, ImageDraw
from itertools import product

# Canvas dimensions
CANVAS_WIDTH = 300
CANVAS_HEIGHT = 500

# Anti-aliasing settings
SCALE_FACTOR = 10  # Render at 10x resolution for anti-aliasing

# Parameter ranges (simplified - no angle parameters)
PARAM_RANGES = {
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

def draw_antialiased_line(draw, x1, y1, x2, y2, width, color='black'):
    """Draw an anti-aliased line by creating a polygon for the line."""
    # Calculate perpendicular vector for line thickness
    dx = x2 - x1
    dy = y2 - y1
    length = math.sqrt(dx*dx + dy*dy)

    if length == 0:
        return

    # Normalize and get perpendicular
    dx /= length
    dy /= length
    px = -dy * width / 2
    py = dx * width / 2

    # Create polygon points for thick line
    points = [
        (x1 + px, y1 + py),
        (x1 - px, y1 - py),
        (x2 - px, y2 - py),
        (x2 + px, y2 + py)
    ]

    draw.polygon(points, fill=color)

def generate_figure(a, b, c, d, e, f, g, stroke_width, stroke_color):
    """
    Generate a single figure with the given parameters (simplified geometry).

    Parameters:
    - a: vertical distance for first downstroke
    - b: vertical component of diagonal segment
    - c: horizontal offset for diagonal
    - d: horizontal/vertical distance for segments
    - e: horizontal offset for additional strokes
    - f: horizontal length for additional stroke
    - g: vertical length for additional stroke
    - stroke_width: width of the stroke
    - stroke_color: color of the stroke (hex format)
    """
    # Create image at higher resolution for anti-aliasing
    img = Image.new('RGBA',
                    (CANVAS_WIDTH * SCALE_FACTOR, CANVAS_HEIGHT * SCALE_FACTOR),
                    (255, 255, 255, 255))
    draw = ImageDraw.Draw(img, 'RGBA')

    # Starting point for downstroke (scaled)
    x_center = 150 * SCALE_FACTOR

    # Scale parameters
    a_scaled = a * SCALE_FACTOR
    b_scaled = b * SCALE_FACTOR
    c_scaled = c * SCALE_FACTOR
    d_scaled = d * SCALE_FACTOR
    e_scaled = e * SCALE_FACTOR
    f_scaled = f * SCALE_FACTOR
    g_scaled = g * SCALE_FACTOR
    stroke_scaled = stroke_width * SCALE_FACTOR

    # Build the main path with simplified straight-line geometry
    points = []

    # 1. from (150,0) to (150,a)
    points.append((x_center, 0))
    points.append((x_center, a_scaled))

    # 2. from (150,a) to (150+c,a+b)
    points.append((x_center + c_scaled, a_scaled + b_scaled))

    # 3. from (150+c,a+b) to (150,a+b)
    points.append((x_center, a_scaled + b_scaled))

    # 4. from (150,a+b) to (150,a+b+c)
    points.append((x_center, a_scaled + b_scaled + c_scaled))

    # 5. from (150,a+b+c) to (150-d,a+b+c)
    points.append((x_center - d_scaled, a_scaled + b_scaled + c_scaled))

    # 6. from (150-d,a+b+c) to (150,a+b+c+d)
    points.append((x_center, a_scaled + b_scaled + c_scaled + d_scaled))

    # 7. from (150,a+b+c+d) to (150,500)
    points.append((x_center, CANVAS_HEIGHT * SCALE_FACTOR))

    # Additional strokes as separate elements:
    additional_points = []

    # 8. from (150-e,a) to (150-e-f,a)
    point_a = (x_center - e_scaled, a_scaled)
    point_b = (x_center - e_scaled - f_scaled, a_scaled)
    additional_points.append(point_a)
    additional_points.append(point_b)

    # 9. from (150-e-f,a) to (150-e,a+g)
    point_c = (x_center - e_scaled, a_scaled + g_scaled)
    additional_points.append(point_c)

    # Draw the main lines using polygon method for better anti-aliasing
    for i in range(len(points) - 1):
        draw_antialiased_line(draw, points[i][0], points[i][1],
                            points[i+1][0], points[i+1][1],
                            stroke_scaled, stroke_color)

    # Draw the additional strokes
    # Stroke 8: (150-e, a) to (150-e-f, a)
    draw_antialiased_line(draw, point_a[0], point_a[1],
                        point_b[0], point_b[1],
                        stroke_scaled, stroke_color)

    # Stroke 9: (150-e-f, a) to (150-e, a+g)
    draw_antialiased_line(draw, point_b[0], point_b[1],
                        point_c[0], point_c[1],
                        stroke_scaled, stroke_color)

    # Add circles at joints for smooth connections (main path)
    for point in points:
        left_up = (point[0] - stroke_scaled/2, point[1] - stroke_scaled/2)
        right_down = (point[0] + stroke_scaled/2, point[1] + stroke_scaled/2)
        draw.ellipse([left_up, right_down], fill=stroke_color)

    # Add circles at joints for additional strokes
    for point in additional_points:
        left_up = (point[0] - stroke_scaled/2, point[1] - stroke_scaled/2)
        right_down = (point[0] + stroke_scaled/2, point[1] + stroke_scaled/2)
        draw.ellipse([left_up, right_down], fill=stroke_color)

    # Downsample to original size with high-quality anti-aliasing
    img = img.resize((CANVAS_WIDTH, CANVAS_HEIGHT), Image.LANCZOS)

    # Convert back to RGB
    rgb_img = Image.new('RGB', (CANVAS_WIDTH, CANVAS_HEIGHT), 'white')
    rgb_img.paste(img, mask=img.split()[3] if img.mode == 'RGBA' else None)

    return rgb_img

def main():
    """Generate all combinations of figures."""
    # Create output directory
    output_dir = './data_simple'
    os.makedirs(output_dir, exist_ok=True)

    # Calculate total combinations
    total = 1
    for param_range in PARAM_RANGES.values():
        total *= len(param_range)

    print(f"Generating {total:,} images (simplified geometry)...")
    print(f"Output directory: {output_dir}")

    # Generate all combinations
    count = 0
    param_names = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'stroke_width', 'stroke_color']
    param_values = [PARAM_RANGES[name] for name in param_names]

    for combination in product(*param_values):
        a, b, c, d, e, f, g, stroke_width, stroke_color = combination

        # Generate the figure
        img = generate_figure(a, b, c, d, e, f, g, stroke_width, stroke_color)

        # Create filename (remove # from color for filename)
        color_code = stroke_color.replace('#', '')
        filename = f"fig_a{a}_b{b}_c{c}_d{d}_e{e}_f{f}_g{g}_w{stroke_width}_col{color_code}.png"
        filepath = os.path.join(output_dir, filename)

        # Save the image
        img.save(filepath, 'PNG')

        count += 1

        # Progress update every 1000 images
        if count % 1000 == 0:
            print(f"Progress: {count:,}/{total:,} ({100*count/total:.1f}%)")

    print(f"\nCompleted! Generated {count:,} images in {output_dir}/")

if __name__ == '__main__':
    main()
