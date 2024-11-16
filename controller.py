# controller.py

import subprocess

# Define the text you want to display
text = "hello"  # Change this text as needed

# Check if the text is "boat", then call display_image.py with sudo
if text.lower() == "boat":
    subprocess.run(["sudo", "python", "display_image.py"])
else:
    # Otherwise, call scroll.py with sudo and the text as an argument
    subprocess.run(["sudo", "python", "scroll.py", "--text", text])
