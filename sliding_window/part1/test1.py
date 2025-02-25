from multiprocessing import Process
from sliding_window.part1.Receiver1 import receiver1
from sliding_window.part1.Sender1 import sender1


def run_receiver():
    receiver1(8080, "received.jpg")


def run_sender():
    sender1("localhost", 8080, "../assets/test.jpg")


if __name__ == "__main__":
    receiver_process = Process(target=run_receiver)
    sender_process = Process(target=run_sender)

    receiver_process.start()
    sender_process.start()

    receiver_process.join()
    sender_process.join()