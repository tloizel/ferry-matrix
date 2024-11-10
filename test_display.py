import time
from rgbmatrix import RGBMatrix, RGBMatrixOptions

# Set up the options for the LED matrix
options = RGBMatrixOptions()
options.rows = 32
options.cols = 64
options.chain_length = 1
options.parallel = 1
options.hardware_mapping = 'adafruit-hat'  # Use 'adafruit-hat' if you're using the Adafruit Bonnet

# Create the LED matrix
matrix = RGBMatrix(options=options)

# Fill the matrix with red
matrix.Fill(255, 0, 0)
time.sleep(2)

# Fill the matrix with green
matrix.Fill(0, 255, 0)
time.sleep(2)

# Fill the matrix with blue
matrix.Fill(0, 0, 255)
time.sleep(2)

# Clear the matrix
matrix.Clear()
