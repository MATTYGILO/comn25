import sys

from sliding_window.lib.file_stream import FileStream
from sliding_window.lib.packet_stream import PacketStream
from sliding_window.lib.utils import throughput


def sender1(file_stream, packet_stream):

    # Loop through the file stream
    for packet in file_stream.to_packets():

        # Send the packet
        packet_stream.sock.sendto(packet.to_bytes(), (remoteHost, port))

    # Close the socket
    packet_stream.close()


if __name__ == "__main__":

    if len(sys.argv) != 4:
        print("Usage: python3 Sender3.py <RemoteHost> <Port> <Filename>")
        sys.exit(1)

    remoteHost = sys.argv[1]
    port = int(sys.argv[2])
    filename = sys.argv[3]
        
    # Start the packet stream
    packet_stream = PacketStream(remoteHost, port)

    # Create the file stream
    file_stream = FileStream(filename)

    # Get the throughput
    throughput(sender1, file_stream.file_size, (file_stream, packet_stream))
