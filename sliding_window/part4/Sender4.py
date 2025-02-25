import sys
import os
import time

# Import your new classes for file reading and packet handling.
from sliding_window.lib.file_stream import FileStream
from sliding_window.lib.packet_stream import PacketStream

def sender4(remote_host, port, filename, timeout_ms, window_size):
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
    packet_generator = file_stream.to_packets()

    # 3. Initialize GBN window variables using n_acked and n_sent.
    n_acked = 0  # Base of the window (oldest unacknowledged packet)
    n_sent = 0  # Next sequence number to send

    # 4. For measuring throughput.
    start_time = time.time()
    total_bytes_sent = 0

    print(f"Sender3 started for file: {filename}")
    print(f"File length (in packets): {len(file_stream)}")
    print(f"Using window size = {window_size}, timeout = {timeout_ms} ms")

    # 5. Main sending loop: keep sending until we've sent all packets.
    while n_acked < len(file_stream):

        # 6. Send as many packets as the window allows.
        while n_sent < n_acked + window_size and n_sent < len(file_stream):
            packet = next(packet_generator)  # Get the next packet
            packet_stream.sock.sendto(packet.to_bytes(), (remote_host, port))
            print(f"Sent packet {packet.seq_number}")

            n_sent += 1
            total_bytes_sent += len(packet.data)

        # 7. Check for ACKs for all packets in the window.
        if packet_stream.wait_for_ack(n_acked, timeout_ms):
            n_acked += 1
            continue

        # Resend all packets in the current window.
        for seq in range(n_acked, n_sent):
            packet = file_stream[seq]  # Get the packet from the file stream by index
            packet_stream.sock.sendto(packet.to_bytes(), (remote_host, port))
            print(f"Retransmitted packet {packet.seq_number}")

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

    remoteHost = sys.argv[1]
    port = int(sys.argv[2])
    filename = sys.argv[3]
    retryTimeout = int(sys.argv[4])
    windowSize = int(sys.argv[5])

    if not os.path.exists(filename):
        print(f"File not found: {filename}")
        sys.exit(1)

    # Send the data to 4
    sender4(remoteHost, port, filename, retryTimeout, windowSize)
