import subprocess
import time
import os

# Configuration
REMOTE_HOST = "localhost"
PORT = 54321
INPUT_FILE = "../assets/test.jpg"
OUTPUT_FILE = "rfile.jpg"


def run_test():
    # Check if input file exists
    if not os.path.exists(INPUT_FILE):
        print(f"Input file '{INPUT_FILE}' not found.")
        return

    # Remove the output file if it exists from a previous run
    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)

    # Start Receiver3.py
    receiver_cmd = f"python3 Receiver2.py {PORT} {OUTPUT_FILE}"
    print(f"Starting Receiver: {receiver_cmd}")
    receiver_process = subprocess.Popen(receiver_cmd, shell=True)

    # Give receiver some time to start listening
    time.sleep(1)

    # Start Sender3.py
    sender_cmd = f"python3 Sender2.py {REMOTE_HOST} {PORT} {INPUT_FILE} {30}"
    print(f"Starting Sender: {sender_cmd}")
    sender_process = subprocess.Popen(sender_cmd, shell=True)

    # Wait for the sender to complete
    sender_process.wait()
    print("Sender finished.")

    # Give some time for receiver to write the file
    time.sleep(2)

    # Terminate the receiver
    receiver_process.terminate()
    print("Receiver terminated.")

    # Verify file integrity
    if os.path.exists(OUTPUT_FILE):
        result = subprocess.run(["diff", INPUT_FILE, OUTPUT_FILE], capture_output=True, text=True)
        if result.returncode == 0:
            print("Test passed: Files are identical.")
        else:
            print("Test failed: Files are different.")
            print(result.stdout)
    else:
        print("Test failed: Output file not found.")


if __name__ == "__main__":
    run_test()
