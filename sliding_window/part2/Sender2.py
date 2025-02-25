import os
import random
import socket
import sys
import time

from sliding_window.lib.coms import wait_for_ack
from sliding_window.lib.const import PACKET_LOSS_RATE, CHUNK_SIZE, ACK_SIZE
from sliding_window.lib.file_stream import FileStream


def stream_file(filename):
    """Generator that reads a file in chunks and signals end of file."""
    with open(filename, "rb") as f:
        while True:
            chunk = f.read(CHUNK_SIZE)
            if not chunk:
                break
            yield chunk


def send_file(remote_host, port, filename, timeout):
    """Send a file over UDP in chunks with sequence numbers and EOF flag."""

    # Check if file exists
    if not os.path.exists(filename):
        print(f"File {filename} not found.")
        return

    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Initialize sequence number and EOF flag
    seq_number = 0
    eof_flag = 0

    # The number of retransmissions
    n_retrans = 0

    start_time = time.time_ns()

    # The file stream
    file_stream = FileStream(filename)

    print("file_stream", file_stream)

    # Create a file stream
    for packet in file_stream.to_packets():

        time.sleep(5 / 1000.0)

        # Send the packet with simulated packet loss
        if random.random() > PACKET_LOSS_RATE:
            sock.sendto(packet.to_bytes(), (remote_host, port))

        # Wait for acknowledgment
        success = wait_for_ack(sock, seq_number, timeout)

        # Retransmit if not successful
        if success is not True:
            n_retrans += 1
            continue

        # # Increment sequence number (wrap around if needed)
        # seq_number = (seq_number + 1) % 65536  # Max 2 bytes

    # # Send an empty packet to indicate the end of the file
    # eof_flag = 1
    # empty_chunk = b'\x00' * CHUNK_SIZE
    # packet = build_packet(seq_number, eof_flag, empty_chunk)
    # sock.sendto(packet, (remote_host, port))
    # sock.close()

    # The time taken to send the file in seconds
    time_taken = (time.time_ns() - start_time) / 1e9

    # Divide the file size by the time taken to get the throughput
    file_size = os.path.getsize(filename)
    throughput = file_size / time_taken

    # Convert to KBytes/s
    throughput /= 1024

    print("{} {}".format(n_retrans, throughput))


if __name__ == "__main__":
    try:
        remote_host = sys.argv[1]
        port = int(sys.argv[2])
        filename = sys.argv[3]
        timeout = int(sys.argv[4])
    except IndexError:
        print("Usage: python3 Sender3.py <RemoteHost> <Port> <Filename> <Timeout>")
        sys.exit(1)

    send_file(remote_host, port, filename, timeout)
