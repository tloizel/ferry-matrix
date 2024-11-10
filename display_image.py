import sys
import os
import tempfile
sys.path.append(os.path.join(os.path.dirname(__file__), 'get-ferry'))

import time
import shutil
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from PIL import Image, ImageDraw, ImageFont
from ferry import get_combined_departures, download_gtfs_data

# Define the path to the image
image_path = '/home/tloizel/code/ferry-led/images/red.png'

try:
    # Open the image file
    img = Image.open(image_path)
    #img.show()  # Show the image using the default image viewer
    # Use the absolute path to the image file
    print(f"Trying to open: {image_path}")
    logo = Image.open(image_path)
    print(f"Image '{image_path}' opened successfully.")
except Exception as e:
    print(f"An error occurred: {e}")

# Set up a temporary directory
temp_dir = tempfile.mkdtemp(prefix='ferry_')
os.environ['FERRY_TEMP_DIR'] = temp_dir

# Configuration for the matrix
options = RGBMatrixOptions()
options.rows = 32
options.cols = 64
options.chain_length = 1
options.parallel = 1
options.hardware_mapping = 'adafruit-hat'
options.gpio_slowdown = 4
options.brightness = 50

# Create the matrix
matrix = RGBMatrix(options = options)

# Create a canvas
image = Image.new("RGB", (matrix.width, matrix.height))
draw = ImageDraw.Draw(image)

# Load a smaller font
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 8)

def draw_frame(departures):
    draw.rectangle((0, 0, matrix.width, matrix.height), fill=(0, 0, 0))

    for stop_id, stop_departures in departures.items():
        if stop_id == 4:
            # Top-right corner (next ferry at stop 4) - SWAPPED
            if stop_departures:
                text = str(stop_departures[0]['minutes_to_next_departure'])
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                draw.text((matrix.width - text_width - 1, 1), text, font=font, fill=(255, 255, 255))


            # Top-left corner (following ferry at stop 4) - SWAPPED
            if len(stop_departures) > 1:
                text = str(stop_departures[1]['minutes_to_next_departure'])
                draw.text((1, 1), text, font=font, fill=(255, 255, 255))



        elif stop_id == 90:
            # Bottom-right corner (next ferry at stop 90) - SWAPPED
            if stop_departures:
                text = str(stop_departures[0]['minutes_to_next_departure'])
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                draw.text((matrix.width - text_width - 1, matrix.height - text_height - 5), text, font=font, fill=(255, 255, 255))

            # Bottom-left corner (following ferry at stop 90) - SWAPPED
            if len(stop_departures) > 1:
                text = str(stop_departures[1]['minutes_to_next_departure'])
                bbox = draw.textbbox((0, 0), text, font=font)
                text_height = bbox[3] - bbox[1]
                draw.text((1, matrix.height - text_height - 5), text, font=font, fill=(255, 255, 255))

    try:
        # Resize if necessary (optional, but good practice)
        logo.thumbnail((matrix.width, matrix.height), Image.Resampling.LANCZOS)

        # Calculate center position
        x = (matrix.width - logo.width) // 2
        y = (matrix.height - logo.height) // 2

        # Paste the image onto the canvas, centered
        image.paste(logo, (x, y))

    except FileNotFoundError:
        print(f"Error: Image file not found at {image_path}")

    matrix.SetImage(image)

def cleanup():
    print("Cleaning up...")
    matrix.Clear()
    shutil.rmtree(temp_dir, ignore_errors=True)

try:
    print("Downloading initial GTFS data...")
    download_gtfs_data()

    last_update = 0
    last_gtfs_download = time.time()
    while True:
        current_time = time.time()
        if current_time - last_update >= 30:  # Update every 30 seconds
            departures = get_combined_departures([4, 90])
            draw_frame(departures)
            last_update = current_time

            # Download fresh GTFS data every 12 hours
            if current_time - last_gtfs_download >= 12 * 3600:
                print("Downloading fresh GTFS data...")
                download_gtfs_data()
                last_gtfs_download = current_time

        time.sleep(0.1)  # Small delay to reduce CPU usage

except KeyboardInterrupt:
    print("Interrupted by user. Exiting...")
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    cleanup()

print("Script ended.")
