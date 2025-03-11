import sys
import os

from sliding_window.lib.file_stream import FileStream
from sliding_window.lib.packet_stream import PacketStream
from sliding_window.lib.utils import throughput


def send_window(packet_stream, file_stream, start_index, windowSize, retryTimeout):

    # The indices we are waiting for
    indices = range(start_index, min(start_index + windowSize, len(file_stream)))

    # Create the packets
    packets = [file_stream.get_packet(i) for i in indices]

    # Send the packets
    packet_stream.send_packets(packets)

    # Wait for the acks
    acks = packet_stream.wait_for_acks(indices, retryTimeout, multi_thread=False)

    # Check ACK results
    for i in indices:
        if not acks.get(i, False):
            return i

    # The index we got to
    return start_index + windowSize


def sender3(file_stream, packet_stream, retryTimeout, windowSize):

    # The number of acknowledgments we have received
    n_acked = 0

    while n_acked < len(file_stream):

        # Send the window
        n_acked = send_window(packet_stream, file_stream, n_acked, windowSize, retryTimeout)

    packet_stream.close()


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
    throughput(sender3, file_stream.file_size,(file_stream, packet_stream, retryTimeout, windowSize))
