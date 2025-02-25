import os
import socket
import sys

from sliding_window.lib.file_stream import FileStream
from sliding_window.lib.packet_stream import PacketStream


def sender1(remote_host, port, filename):
    """Send a file over UDP in chunks with sequence numbers and EOF flag."""

    # Create the file streamer
    file_stream: FileStream = FileStream(filename)
    file_stream.read()
    packet_generator = file_stream.to_packets()

    # Create the packet stream
    packet_stream = PacketStream(remote_host, port)

    # Wait for someone to connect

    print("Streaming packets to receiver")
    packet_stream.stream(packet_generator)

    print("Finished sending file 1")

    packet_stream.close()
    print("Closing packet stream")


if __name__ == "__main__":
    try:
        remote_host = sys.argv[1]
        port = int(sys.argv[2])
        filename = sys.argv[3]
    except IndexError:
        print("Usage: python3 Sender1.py <RemoteHost> <Port> <Filename>")
        sys.exit(1)

    send_file(remote_host, port, filename)
