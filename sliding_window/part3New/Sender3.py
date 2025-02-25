import socket
import sys
import os
import time
from collections import deque

from sliding_window.lib.file_stream import FileStream
from sliding_window.lib.packet_stream import PacketStream


def sender3(remote_host, port, filename, timeout, window_size):

    # Start the packet stream
    packet_stream = PacketStream(remote_host, port)

    # Create the file stream
    file_stream = FileStream(filename)

    # The packet generator
    packet_generator = file_stream.to_packets()

    # Window parameters
    base = 0
    next_seq_num = 0
    window = deque()  # Store packets in the current window

    # Performance tracking
    n_retrans = 0
    start_time = time.time()
    total_bytes_sent = 0

    # Main sending loop
    while base < file_stream.total_packets():

        # Send packets within window size
        while next_seq_num < base + window_size and next_seq_num < file_stream.total_packets():

            # Get the next packet
            packet = next(packet_generator)

            # Send the packet
            packet_stream.sock.sendto(packet.to_bytes(), (remote_host, port))
            print(f"Sent packet {packet.seq_number}")

            # Add packet to the window
            window.append(packet)
            next_seq_num += 1
            total_bytes_sent += len(packet.data)

        # Wait for acknowledgment using Go-Back-N
        try:
            ack = packet_stream.wait_for_ack(base, timeout)
            if ack is not None and ack >= base:
                print(f"Received ACK for packet {ack}")
                # Slide window to the new base
                while window and window[0].seq_number <= ack:
                    window.popleft()
                    base += 1

        except socket.timeout:
            # Timeout occurred, retransmit all packets in the window
            print(f"Timeout occurred. Retransmitting from packet {base}")
            n_retrans += 1
            for packet in window:
                packet_stream.sock.sendto(packet.to_bytes(), (remote_host, port))
                print(f"Retransmitted packet {packet.seq_number}")

    # Close the socket and calculate throughput
    packet_stream.close()
    end_time = time.time()
    elapsed_time = end_time - start_time
    throughput = (total_bytes_sent / 1024) / elapsed_time  # KBytes per second
    print(f"{throughput:.2f}")  # Throughput output as required


if __name__ == "__main__":

    if len(sys.argv) != 6:
        print("Usage: python3 Sender3.py <RemoteHost> <Port> <Filename> <Timeout> <WindowSize>")
        sys.exit(1)

    remote_host = sys.argv[1]
    port = int(sys.argv[2])
    filename = sys.argv[3]
    timeout = int(sys.argv[4])
    window_size = int(sys.argv[5])

    if not os.path.exists(filename):
        print("File not found:", filename)
        sys.exit(1)

    sender3(remote_host, port, filename, timeout, window_size)
