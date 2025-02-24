import subprocess

# Runs the different python files at the same time
if __name__ == "__main__":

    # The task we are doing
    task = 1

    # Start the receiver
    receiver = subprocess.Popen(["python3", "Receiver{}.py".format(task), "12345", "received.jpg"])

    # Start the sender
    sender = subprocess.Popen(["python3", "Sender{}.py".format(task), "localhost", "12345", "../assets/test.jpg"],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    receiver.wait()
    sender.wait()

    # Stream their outputs
    print(sender.communicate())
    print(receiver.communicate())

