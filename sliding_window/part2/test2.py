from multiprocessing import Process

from sliding_window.part2.Receiver2 import receive_file
from sliding_window.part2.Sender2 import send_file


# def run_receiver():
#     receive_file(8001, "received.jpg")
#
#
# def run_sender():
#     send_file("localhost", 8001, "../assets/test.jpg", 10)
#


# Runs the different python files at the same time
if __name__ == "__main__":
    # receiver_process = Process(target=run_receiver)
    # sender_process = Process(target=run_sender)
    #
    # receiver_process.start()
    # sender_process.start()
    #
    # receiver_process.join()
    # sender_process.join()
    #
    # raise NotImplementedError("Please implement this part of the code")


    # Choose the task to run
    task = 2
    timeout = 10

    packet_loss = 0.05

    delays = [5, 10, 15, 20, 25, 30, 40, 50, 75, 100]
    retrans = []
    throughput = []

    port = 8001


    for delay in delays:

        r = []
        t = []

        for _ in range(5):

            # Start the receiver
            receiver = subprocess.Popen(["python3", "Receiver{}.py".format(task), str(port), "received.jpg"])

            # Start the sender
            sender = subprocess.Popen(["python3", "Sender{}.py".format(task), "localhost", str(port), "../assets/test.jpg", str(delay)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # Get the sender response
            response = sender.communicate()

            print("Response: ", response)

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



