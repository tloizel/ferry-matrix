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
image_path_green = '/home/tloizel/code/ferry-led/images/blue.png'
image_path_orange = '/home/tloizel/code/ferry-led/images/orange.png'
green_boat = Image.open(image_path_green)
orange_boat = Image.open(image_path_orange)

# Load the DejaVu Sans Mono font
#font = ImageFont.truetype("/home/tloizel/code/ferry-led/fonts/Square-Dot-Matrix.ttf", 8)
font = ImageFont.load_default()

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
options.brightness = 85

# Create the matrix
matrix = RGBMatrix(options = options)

# Create a canvas
image = Image.new("RGB", (matrix.width, matrix.height))
draw = ImageDraw.Draw(image)


def draw_frame(departures):
    draw.rectangle((0, 0, matrix.width, matrix.height), fill=(0, 0, 0))

    for stop_id, stop_departures in departures.items():
        if stop_id == 4:
            # Display departure times for stop 4
            if stop_departures:
                next_departure = stop_departures[0]['minutes_to_next_departure']
                text = str(next_departure)
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                draw.text((matrix.width - text_width - 1, 4), text, font=font, fill=(255, 255, 255))

                # Calculate the column position for the green boat based on departure time
                green_boat_column = min(14 + max(0, 30 - next_departure), matrix.width - green_boat.width)
            
            else:
                # Center the green boat if no departures are available
                green_boat_column = (matrix.width - green_boat.width) // 2
                
            if len(stop_departures) > 1:
                following_departure = stop_departures[1]['minutes_to_next_departure']
                draw.text((1, 4), str(following_departure), font=font, fill=(255, 255, 255))

        elif stop_id == 90:
            # Display departure times for stop 90
            if stop_departures:
                next_departure = stop_departures[0]['minutes_to_next_departure']
                text = str(next_departure)
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                draw.text((matrix.width - text_width - 1, matrix.height - text_height - 3), text, font=font, fill=(255, 255, 255))

                # Calculate the column position for the orange boat based on departure time
                orange_boat_column = min(14 + max(0, 30 - next_departure), matrix.width - orange_boat.width)
                
            else:
                # Center the orange boat if no departures are available
                orange_boat_column = (matrix.width - orange_boat.width) // 2
                
            if len(stop_departures) > 1:
                following_departure = stop_departures[1]['minutes_to_next_departure']
                bbox = draw.textbbox((0, 0), str(following_departure), font=font)
                text_height = bbox[3] - bbox[1]
                draw.text((1, matrix.height - text_height - 3), str(following_departure), font=font, fill=(255, 255, 255))

    # Position the green boat based on the calculated column
    green_boat_position = (green_boat_column, 3)
    image.paste(green_boat, green_boat_position)

    # Position the orange boat based on the calculated column
    orange_boat_position = (orange_boat_column, matrix.height - orange_boat.height - 3)
    image.paste(orange_boat, orange_boat_position)
    
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
