import os
import socket
import sys
import time

from sliding_window.lib.packets import build_packet

# Size of the data chunk
CHUNK_SIZE = 1024


def stream_file(filename):
    """Generator that reads a file in chunks and signals end of file."""
    with open(filename, "rb") as f:
        while True:
            chunk = f.read(CHUNK_SIZE)
            if not chunk:
                break
            yield chunk


def send_file(remote_host, port, filename):
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

    # Read and send the file in chunks using stream_file generator
    for chunk in stream_file(filename):

        # Build the packet: header + data
        packet = build_packet(seq_number, eof_flag, chunk)

        time.sleep(5 / 1000.0)

        # Send the packet
        sock.sendto(packet, (remote_host, port))

        # Increment sequence number (wrap around if needed)
        seq_number = (seq_number + 1) % 65536  # Max 2 bytes


    # Send an empty packet to indicate the end of the file
    eof_flag = 1
    empty_chunk = b'\x00' * CHUNK_SIZE
    packet = build_packet(seq_number, eof_flag, empty_chunk)
    sock.sendto(packet, (remote_host, port))
    print("End of file packet sent.")
    print("File transmission complete.")
    sock.close()


if __name__ == "__main__":
    try:
        remote_host = sys.argv[1]
        port = int(sys.argv[2])
        filename = sys.argv[3]
    except IndexError:
        print("Usage: python3 Sender1.py <RemoteHost> <Port> <Filename>")
        sys.exit(1)

    send_file(remote_host, port, filename)
