# import os
# import socket
# import sys
#
# from sliding_window.lib.file_stream import FileStream
# from sliding_window.lib.packet_stream import PacketStream
#
#
# def sender1(remote_host, port, filename):
#     """Send a file over UDP in chunks with sequence numbers and EOF flag."""
#
#     # Create the file streamer
#     file_stream: FileStream = FileStream(filename)
#     file_stream.read()
#     packet_generator = file_stream.to_packets()
#
#     # Create the packet stream
#     packet_stream = PacketStream(remote_host, port)
#
#     # Wait for someone to connect
#
#     print("Streaming packets to receiver")
#     packet_stream.stream(packet_generator)
#
#     print("Finished sending file 1")
#
#     packet_stream.close()
#     print("Closing packet stream")
#
#
# if __name__ == "__main__":
#     try:
#         remote_host = sys.argv[1]
#         port = int(sys.argv[2])
#         filename = sys.argv[3]
#     except IndexError:
#         print("Usage: python3 Sender3.py <RemoteHost> <Port> <Filename>")
#         sys.exit(1)
#
#     sender1(remote_host, port, filename)
import socket
import sys
import os
import time

from sliding_window.lib.file_stream import FileStream
from sliding_window.lib.packet_stream import PacketStream


def send_file(remote_host, port, filename):

    # Start the packet stream
    packet_stream = PacketStream(remote_host, port)

    # Create the file stream
    file_stream = FileStream(filename)

    # Loop through the file stream
    for packet in file_stream.to_packets():

        # Send the packet
        packet_stream.sock.sendto(packet.to_bytes(), (remote_host, port))

    # Close the socket
    packet_stream.close()
    print("File transfer complete.")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python3 Sender3.py <RemoteHost> <Port> <Filename>")
        sys.exit(1)

    remote_host = sys.argv[1]
    port = int(sys.argv[2])
    filename = sys.argv[3]

    if not os.path.exists(filename):
        print("File not found:", filename)
        sys.exit(1)

    send_file(remote_host, port, filename)
