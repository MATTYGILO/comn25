import subprocess


# Runs the different python files at the same time
if __name__ == "__main__":

    # Choose the task to run
    task = 2
    timeout = 10

    packet_loss = 0.05

    delays = [5, 10, 15, 20, 25, 30, 40, 50, 75, 100]
    retrans = []
    throughput = []


    for delay in delays:

        r = []
        t = []

        for _ in range(5):

            # Start the receiver
            receiver = subprocess.Popen(["python3", "Receiver{}.py".format(task), "12345", "received.jpg"])

            # Start the sender
            sender = subprocess.Popen(["python3", "Sender{}.py".format(task), "localhost", "12345", "test.jpg", str(delay)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # Get the sender response
            response = sender.communicate()

            # Split to get retrans and throughput
            r.append(int(response[0].split()[0]))
            t.append(float(response[0].split()[1]))

            # Wait for both processes to complete
            receiver.wait()
            sender.wait()

        # Append the mean of r and t
        retrans.append(sum(r) / len(r))
        throughput.append(sum(t) / len(t))

        print("Delay {}ms, Retransmissions: {}, Throughput: {}".format(delay, retrans[-1], throughput[-1]))

    print("delays: ", delays)
    print("retransmissions: ", retrans)
    print("throughput: ", throughput)



