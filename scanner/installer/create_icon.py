#!/usr/bin/env python3
"""
Create a simple app icon for the BLE Kafka Scanner.
This script is used as a fallback if other icon creation methods fail.
"""

import os
import sys
from PIL import Image, ImageDraw, ImageFont

def create_icon(output_path="app_icon.png", size=1024):
    """Create a simple app icon."""
    # Create a new image with a blue background
    img = Image.new('RGB', (size, size), color=(0, 0, 255))
    draw = ImageDraw.Draw(img)
    
    # Draw a white border
    border_width = int(size * 0.01)
    draw.rectangle(
        [(border_width, border_width), (size - border_width, size - border_width)],
        outline=(255, 255, 255),
        width=border_width
    )
    
    # Try to add text
    try:
        # Try to get a font
        font_size = int(size * 0.1)
        try:
            # Try to use a system font
            font = ImageFont.truetype("Arial", font_size)
        except:
            # Fall back to default font
            font = ImageFont.load_default()
        
        # Draw the text
        text = "BLE\nKafka\nScanner"
        draw.text(
            (size // 2, size // 2),
            text,
            fill=(255, 255, 255),
            font=font,
            anchor="mm",
            align="center"
        )
    except Exception as e:
        print(f"Error adding text to icon: {e}")
        # If text fails, draw a simple symbol
        center = size // 2
        radius = size // 4
        draw.ellipse(
            [(center - radius, center - radius), (center + radius, center + radius)],
            fill=(255, 255, 255)
        )
    
    # Save the image
    img.save(output_path)
    print(f"Icon created at {output_path}")
    return output_path

if __name__ == "__main__":
    output_path = "app_icon.png"
    if len(sys.argv) > 1:
        output_path = sys.argv[1]
    create_icon(output_path) 