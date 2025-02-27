import sys
import os
import time

from sliding_window.lib.file_stream import FileStream
from sliding_window.lib.packet_stream import PacketStream
from sliding_window.lib.utils import throughput


def send_window(packet_stream, file_stream, start_index, windowSize, retryTimeout):

    # The indices we are waiting for
    indices = range(start_index, min(start_index + windowSize, len(file_stream)))

    while len(indices) > 0:

        # Create the packets
        packets = [file_stream.get_packet(i) for i in indices]

        # Send the packets
        packet_stream.send_packets(packets)

        # Wait for the acks
        acks = packet_stream.wait_for_acks(indices, retryTimeout, multi_thread=True)

        # Remove any indices that were acknowledged
        indices = [i for i in indices if acks.get(i, False) is False]

    # The index we got to
    return start_index + windowSize

def sender4(remoteHost, port, filename, retryTimeout, windowSize):
    """
    Go-Back-N Sender using n_acked and n_sent:
    - remoteHost (str): IP or hostname of the receiver.
    - port (int): UDP port of the receiver.
    - filename (str): File to send.
    - retryTimeout (int): Retransmission timeout in milliseconds.
    - windowSize (int): GBN window size.
    """

    # 1. Create and open the PacketStream (UDP) socket.
    packet_stream = PacketStream(remoteHost, port)

    # 2. Create the FileStream from your library to read the file.
    file_stream = FileStream(filename)
    file_stream.read()

    # 3. Initialize GBN window variables using n_acked and n_sent.
    n_acked = 0

    # 4. For measuring throughput.
    start_time = time.time()

    # 5. Main sending loop: keep sending until we've sent all packets.
    while n_acked < len(file_stream):

        # Send the window
        n_acked = send_window(packet_stream, file_stream, n_acked, windowSize, retryTimeout)

    # 9. Done sending the file; calculate throughput and close.
    elapsed_time = time.time() - start_time
    throughput_kbps = (file_stream.file_size() / 1024.0) / elapsed_time  # KB/s
    print(f"{throughput_kbps:.2f}")

    packet_stream.close()
    print("Finished sending file via Go-Back-N.")


if __name__ == "__main__":
    """
    Usage: python3 Sender3.py <RemoteHost> <Port> <Filename> <retryTimeout> <WindowSize>
    Example: python3 Sender3.py 127.0.0.1 54321 test.bin 100 5
    """
    if len(sys.argv) != 6:
        print("Usage: python3 Sender3.py <RemoteHost> <Port> <Filename> <retryTimeout> <WindowSize>")
        sys.exit(1)

    remoteHost = sys.argv[1]
    port = int(sys.argv[2])
    filename = sys.argv[3]
    retryTimeout = int(sys.argv[4])
    windowSize = int(sys.argv[5])

    # Create the file stream and packet stream
    file_stream = FileStream(filename)
    packet_stream = PacketStream(remoteHost, port)

    # Get the throughput
    throughput(sender4, file_stream.file_size,(file_stream, packet_stream, retryTimeout, windowSize))
