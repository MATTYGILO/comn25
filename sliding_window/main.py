import subprocess

# Runs the different python files at the same time
if __name__ == "__main__":

    # Choose the task to run
    task = 2

    # Start the receiver
    receiver = subprocess.Popen(["python3", "Receiver{}.py".format(task), "12345", "received.jpg"])

    # Start the sender
    sender = subprocess.Popen(["python3", "Sender{}.py".format(task), "localhost", "12345", "test.jpg"])

    # Wait for both processes to complete
    receiver.wait()
    sender.wait()

    print("File transfer complete.")
