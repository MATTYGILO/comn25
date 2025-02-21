import subprocess

# Runs the different python files at the same time
if __name__ == "__main__":
    # Start the receiver
    receiver = subprocess.Popen(["python3", "Receiver1.py", "12345", "received.jpg"])

    # Start the sender
    sender = subprocess.Popen(["python3", "Sender1.py", "localhost", "12345", "test.jpg"])

    # Wait for both processes to complete
    receiver.wait()
    sender.wait()

    print("File transfer complete.")
