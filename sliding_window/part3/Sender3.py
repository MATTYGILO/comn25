import sys
import os
import time
import random

# Import your new classes for file reading and packet handling.
from sliding_window.lib.file_stream import FileStream
from sliding_window.lib.packet_stream import PacketStream


def send_window(packet_stream, file_stream, start_index, window_size, timeout_ms):

    # The indices we are waiting for
    indices = range(start_index, min(start_index + window_size, len(file_stream)))

    # Send all packets in the window
    for i in indices:
        # Get the packet
        packet = file_stream.get_packet(i)

        if packet is None:
            break

        # Send the packet
        if random.random() > 0.0005:
            packet_stream.sock.sendto(packet.to_bytes(), (packet_stream.remote_host, packet_stream.port))

    # Wait for the acks
    acks = packet_stream.wait_for_acks(indices, timeout_ms)

    # Check ACK results
    for i in indices:
        if not acks.get(i, False):
            return i

    # The index we got to
    return start_index + window_size


def sender3(remote_host, port, filename, timeout_ms, window_size):
    """
    Go-Back-N Sender using n_acked and n_sent:
    - remote_host (str): IP or hostname of the receiver.
    - port (int): UDP port of the receiver.
    - filename (str): File to send.
    - timeout_ms (int): Retransmission timeout in milliseconds.
    - window_size (int): GBN window size.
    """

    # 1. Create and open the PacketStream (UDP) socket.
    packet_stream = PacketStream(remote_host, port)

    # 2. Create the FileStream from your library to read the file.
    file_stream = FileStream(filename)
    file_stream.read()  # Load file data into memory (if your library requires this).

    # 3. Initialize GBN window variables using n_acked and n_sent.
    n_acked = 0  # Base of the window (oldest unacknowledged packet)

    # 4. For measuring throughput.
    start_time = time.time()
    total_bytes_sent = 0

    print(f"Sender3 started for file: {filename}")
    print(f"File length (in packets): {len(file_stream)}")
    print(f"Using window size = {window_size}, timeout = {timeout_ms} ms")

    # 5. Main sending loop: keep sending until we've sent all packets.
    while n_acked < len(file_stream):

        # Send the window
        n_acked = send_window(packet_stream, file_stream, n_acked, window_size, timeout_ms)

    # 9. Done sending the file; calculate throughput and close.
    elapsed_time = time.time() - start_time
    throughput_kbps = (total_bytes_sent / 1024.0) / elapsed_time  # KB/s
    print(f"{throughput_kbps:.2f}")  # Print only throughput on one line as required.

    packet_stream.close()
    print("Finished sending file via Go-Back-N.")


if __name__ == "__main__":
    """
    Usage: python3 Sender3.py <RemoteHost> <Port> <Filename> <Timeout_ms> <WindowSize>
    Example: python3 Sender3.py 127.0.0.1 54321 test.bin 100 5
    """
    if len(sys.argv) != 6:
        print("Usage: python3 Sender3.py <RemoteHost> <Port> <Filename> <Timeout_ms> <WindowSize>")
        sys.exit(1)

    remote_host = sys.argv[1]
    port = int(sys.argv[2])
    filename = sys.argv[3]
    timeout_ms = int(sys.argv[4])
    window_size = int(sys.argv[5])

    if not os.path.exists(filename):
        print(f"File not found: {filename}")
        sys.exit(1)

    sender3(remote_host, port, filename, timeout_ms, window_size)
