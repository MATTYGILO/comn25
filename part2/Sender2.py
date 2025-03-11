import sys
import os

from sliding_window.lib.file_stream import FileStream
from sliding_window.lib.packet_stream import PacketStream
from sliding_window.lib.utils import throughput


def sender2(file_stream, packet_stream, timeout):

    # The packet generator
    packet_generator = file_stream.to_packets()

    # The number of retransmissions
    n_retrans = 0

    for packet in packet_generator:

        # Wait for acknowledgment
        received_ack = False

        while not received_ack:

            # Send the packet
            packet_stream.sock.sendto(packet.to_bytes(), (remoteHost, port))

            # Wait for acknowledgment
            ack_seq = packet_stream.wait_for_ack(packet.seq_number, timeout)

            if ack_seq != packet.seq_number:
                print(f"Retransmitting packet {packet.seq_number}")
                n_retrans += 1
            else:
                received_ack = True

    # Close the socket
    packet_stream.close()
    print("File transfer complete.")


if __name__ == "__main__":

    if len(sys.argv) != 5:
        print("Usage: python3 Sender3.py <RemoteHost> <Port> <Filename> <Timeout>")
        sys.exit(1)

    remoteHost = sys.argv[1]
    port = int(sys.argv[2])
    filename = sys.argv[3]
    retryTimeout = int(sys.argv[4])

    # Start the packet stream
    packet_stream = PacketStream(remoteHost, port)

    # Create the file stream
    file_stream = FileStream(filename)

    # Get the throughput
    throughput(sender2, file_stream.file_size,(file_stream, packet_stream, retryTimeout))

