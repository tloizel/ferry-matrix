import sys
import os
import time
import random
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from PIL import Image, ImageDraw, ImageFont

# Set up the RGB matrix options
options = RGBMatrixOptions()
options.rows = 32
options.cols = 64
options.chain_length = 1
options.parallel = 1
options.hardware_mapping = 'adafruit-hat'  # Use 'adafruit-hat' if you're using Adafruit HAT

# Initialize the matrix with the given options
matrix = RGBMatrix(options=options)

# Use the default font
font = ImageFont.load_default()

# Text to display
text = "Hello, World!   "  # Add spaces for smooth wrap-around

# Calculate text width and height for scrolling
text_width, text_height = font.getsize(text)
image_width = text_width * 2  # Double width to allow wrap-around
image_height = matrix.height

# Create the image and draw object
image = Image.new("RGB", (image_width, image_height))
draw = ImageDraw.Draw(image)

# Start the infinite scroll
offset_x = 0  # Initial horizontal offset

# List to store colors for each "Hello, World!" instance on screen
colors = [
    (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)),  # Initial color for the first instance
    (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))   # Initial color for the second instance
]

while True:
    # Clear the image
    draw.rectangle((0, 0, image_width, image_height), fill=(0, 0, 0))

    # Draw the text twice with fixed colors for each instance
    draw.text((offset_x, (matrix.height - text_height) // 2), text, font=font, fill=colors[0])
    draw.text((offset_x + text_width, (matrix.height - text_height) // 2), text, font=font, fill=colors[1])

    # Scroll the text by adjusting the offset
    offset_x -= 1  # Move left by 1 pixel

    # When the first instance scrolls out, reset offset and shift colors
    if offset_x < -text_width:
        offset_x = 0
        # Shift the colors: the second instance becomes the first, and a new color is generated for the next
        colors[0] = colors[1]
        colors[1] = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    # Crop and display the current part of the image
    cropped_image = image.crop((0, 0, matrix.width, matrix.height))
    matrix.SetImage(cropped_image)

    time.sleep(0.03)  # Control the scroll speed
