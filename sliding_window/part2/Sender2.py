import socket
import sys
import os
import time

from sliding_window.lib.file_stream import FileStream
from sliding_window.lib.packet_stream import PacketStream


def sender2(remote_host, port, filename, timeout):

    # Start the packet stream
    packet_stream = PacketStream(remote_host, port)

    # Create the file stream
    file_stream = FileStream(filename)

    # The packet generator
    packet_generator = file_stream.to_packets()

    # The number of retransmissions
    n_retrans = 0

    for packet in packet_generator:

        # Wait for acknowledgment
        received_ack = False

        while not received_ack:

            # Send the packet
            packet_stream.sock.sendto(packet.to_bytes(), (remote_host, port))

            # Wait for acknowledgment
            received_ack = packet_stream.wait_for_ack(packet.seq_number, timeout)

            if not received_ack:
                print(f"Retransmitting packet {packet.seq_number}")
                n_retrans += 1

    # Close the socket
    packet_stream.close()
    print("File transfer complete.")


if __name__ == "__main__":

    if len(sys.argv) != 5:
        print("Usage: python3 Sender3.py <RemoteHost> <Port> <Filename> <Timeout>")
        sys.exit(1)

    remote_host = sys.argv[1]
    port = int(sys.argv[2])
    filename = sys.argv[3]
    timeout = int(sys.argv[4])

    if not os.path.exists(filename):
        print("File not found:", filename)
        sys.exit(1)

    sender2(remote_host, port, filename, timeout)
