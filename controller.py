import subprocess
import time
import requests

# GitHub raw URL for remote_controller.txt
url = "https://raw.githubusercontent.com/tloizel/ferry-matrix/refs/heads/master/remote_controller.txt"

# Initialize last known content
last_content = None
current_process = None  # Track the current subprocess

def stop_current_process():
    """Stop the current process if it exists."""
    global current_process
    if current_process:
        print("Terminating previous process...")
        current_process.terminate()  # Terminate the existing process
        current_process.wait()  # Wait for the process to fully terminate
        current_process = None  # Reset the current process tracker

while True:
    try:
        # Fetch the latest content from GitHub
        print("Fetching latest content...")
        response = requests.get(url)
        response.raise_for_status()  # Check for HTTP errors
        content = response.text.strip()

        # Debug: Print the retrieved content
        print(f"Content fetched: {content}")

        # Check if the content has changed
        if content != last_content:
            print("Content has changed.")
            last_content = content  # Update last known content

            # Stop the current process before starting a new one
            stop_current_process()

            # Check if the content is "boat"
            if content.lower() == "boat":
                print("Content is 'boat', running display_image.py...")
                # Start display_image.py in the background
                current_process = subprocess.Popen(["sudo", "python", "display_image.py"])
            else:
                print(f"Running scroll.py with text: {content}")
                # Start scroll.py with the new text in the background
                current_process = subprocess.Popen(["sudo", "python", "scroll.py", "--text", content])

    except requests.RequestException as e:
        print(f"Error fetching remote_controller.txt: {e}")
    
    # Wait for 60 seconds before checking again
    print("Waiting for next check...")
    time.sleep(60)
    print("Checked.")
