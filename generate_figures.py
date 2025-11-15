#!/usr/bin/env python3
"""
Generate procedural figures with different parameter combinations.
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
SCALE_FACTOR = 10  # Render at 4x resolution for anti-aliasing

# Parameter ranges (reduced for manageable image count)
PARAM_RANGES = {
    'a': [100 , 130, 150],
    'b': [50, 100, 125],
    'g': [20, 40, 60],
    'c': [50 , 60],
    'y': [290,305,320],
    'd': [20,40,60],
    'e': [20, 30],
    'f': [20, 40],
    'h': [15, 30],  # Using 'h' instead of 'g' to avoid conflict
    'stroke_width': [3,6]
}

def calculate_point_from_angle(start_x, start_y, angle_degrees, distance):
    """
    Calculate end point given start point, angle (from vertical), and distance.
    Angle is measured clockwise from vertical (downward).
    """
    # Convert angle to radians
    angle_rad = math.radians(angle_degrees)

    # Calculate end point (angle measured from vertical, clockwise)
    end_x = start_x + distance * math.sin(angle_rad)
    end_y = start_y + distance * math.cos(angle_rad)

    return end_x, end_y

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

def generate_figure(a, b, g, c, y, d, e, f, h, stroke_width):
    """
    Generate a single figure with the given parameters.

    Parameters:
    - a: vertical distance for first downstroke
    - b: vertical component of diagonal segment
    - g: angle (degrees) to turn left after first downstroke
    - c: vertical distance after returning to center
    - y: angle (degrees) to turn right before final diagonal
    - d: horizontal distance and length of angled segments
    - e: horizontal offset for additional strokes
    - f: horizontal length for additional stroke
    - h: vertical length for additional stroke
    - stroke_width: width of the stroke
    """
    # Create image at higher resolution for anti-aliasing
    img = Image.new('RGBA',
                    (CANVAS_WIDTH * SCALE_FACTOR, CANVAS_HEIGHT * SCALE_FACTOR),
                    (255, 255, 255, 255))
    draw = ImageDraw.Draw(img, 'RGBA')

    # Starting point for downstroke (scaled)
    x_center = 150 * SCALE_FACTOR

    # Build the path (scale all coordinates)
    points = []

    # Scale parameters
    a_scaled = a * SCALE_FACTOR
    b_scaled = b * SCALE_FACTOR
    c_scaled = c * SCALE_FACTOR
    d_scaled = d * SCALE_FACTOR
    e_scaled = e * SCALE_FACTOR
    f_scaled = f * SCALE_FACTOR
    h_scaled = h * SCALE_FACTOR
    stroke_scaled = stroke_width * SCALE_FACTOR

    # 1. Downstroke from (150, 0) to (150, a)
    points.append((x_center, 0))
    points.append((x_center, a_scaled))

    # 2. Turn left by g degrees and continue for q pixels until reaching (150+d, a+b)
    # We need to calculate q such that we reach (150+d, a+b)
    # From (150, a) turning left by g degrees
    # Target: (150+d, a+b)
    # Using trigonometry: horizontal = q * sin(g), vertical = q * cos(g)
    # d = q * sin(g) and b = q * cos(g)
    # Therefore: q = sqrt(d^2 + b^2)
    q = math.sqrt(d_scaled**2 + b_scaled**2)
    end_x, end_y = calculate_point_from_angle(x_center, a_scaled, g, q)
    points.append((end_x, end_y))

    # 3. Continue to point (150, a+b)
    # points.append((x_center, a + b))
    points.append((x_center, end_y))

    # 4. Continue downwards for c pixels to (150, a+b+c)
    points.append((x_center, a_scaled + b_scaled + c_scaled))

    # 5. Go to point (150-d, a+b+c)
    points.append((x_center - d_scaled, a_scaled + b_scaled + c_scaled))

    # 6. Turn right by y degrees and continue for d pixels
    # From (150-d, a+b+c), turning right by y degrees, going distance d
    # Right turn means negative angle
    end_x2, end_y2 = calculate_point_from_angle(x_center - d_scaled, a_scaled + b_scaled + c_scaled, -y, d_scaled)
    points.append((end_x2, end_y2))

    # 7. Continue downwards for the rest of the canvas
    points.append((end_x2, CANVAS_HEIGHT * SCALE_FACTOR))

    # Additional strokes as requested:
    # Stroke from (150-e, a) to (150-e-f, a)
    additional_points = []
    point_a = (x_center - e_scaled, a_scaled)
    point_b = (x_center - e_scaled - f_scaled, a_scaled)
    additional_points.append(point_a)
    additional_points.append(point_b)

    # Stroke from (150-e-f, a) to (150-e, a+h)
    point_c = (x_center - e_scaled, a_scaled + h_scaled)
    additional_points.append(point_c)

    # Draw the main lines using polygon method for better anti-aliasing
    for i in range(len(points) - 1):
        draw_antialiased_line(draw, points[i][0], points[i][1],
                            points[i+1][0], points[i+1][1],
                            stroke_scaled, 'black')

    # Draw the additional strokes
    # First stroke: (150-e, a) to (150-e-f, a)
    draw_antialiased_line(draw, point_a[0], point_a[1],
                        point_b[0], point_b[1],
                        stroke_scaled, 'black')

    # Second stroke: (150-e-f, a) to (150-e, a+h)
    draw_antialiased_line(draw, point_b[0], point_b[1],
                        point_c[0], point_c[1],
                        stroke_scaled, 'black')

    # Add circles at joints for smooth connections (main path)
    for point in points:
        left_up = (point[0] - stroke_scaled/2, point[1] - stroke_scaled/2)
        right_down = (point[0] + stroke_scaled/2, point[1] + stroke_scaled/2)
        draw.ellipse([left_up, right_down], fill='black')

    # Add circles at joints for additional strokes
    for point in additional_points:
        left_up = (point[0] - stroke_scaled/2, point[1] - stroke_scaled/2)
        right_down = (point[0] + stroke_scaled/2, point[1] + stroke_scaled/2)
        draw.ellipse([left_up, right_down], fill='black')

    # Downsample to original size with high-quality anti-aliasing
    img = img.resize((CANVAS_WIDTH, CANVAS_HEIGHT), Image.LANCZOS)

    # Convert back to RGB
    rgb_img = Image.new('RGB', (CANVAS_WIDTH, CANVAS_HEIGHT), 'white')
    rgb_img.paste(img, mask=img.split()[3] if img.mode == 'RGBA' else None)

    return rgb_img

def main():
    """Generate all combinations of figures."""
    # Create output directory
    output_dir = './data'
    os.makedirs(output_dir, exist_ok=True)

    # Calculate total combinations
    total = 1
    for param_range in PARAM_RANGES.values():
        total *= len(param_range)

    print(f"Generating {total:,} images...")
    print(f"Output directory: {output_dir}")

    # Generate all combinations
    count = 0
    param_names = ['a', 'b', 'g', 'c', 'y', 'd', 'e', 'f', 'h', 'stroke_width']
    param_values = [PARAM_RANGES[name] for name in param_names]

    for combination in product(*param_values):
        a, b, g, c, y, d, e, f, h, stroke_width = combination

        # Generate the figure
        img = generate_figure(a, b, g, c, y, d, e, f, h, stroke_width)

        # Create filename
        filename = f"fig_a{a}_b{b}_g{g}_c{c}_y{y}_d{d}_e{e}_f{f}_h{h}_w{stroke_width}.png"
        filepath = os.path.join(output_dir, filename)

        # Save the image
        img.save(filepath, 'PNG')

        count += 1

        # Progress update every 10000 images
        if count % 10000 == 0:
            print(f"Progress: {count:,}/{total:,} ({100*count/total:.1f}%)")

    print(f"\nCompleted! Generated {count:,} images in {output_dir}/")

if __name__ == '__main__':
    main()
