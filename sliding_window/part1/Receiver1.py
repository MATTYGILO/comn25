import sys

from sliding_window.lib.file_stream import FileStream
from sliding_window.lib.packet_stream import PacketStream


def receiver1(port, output_path):

    # The packet streamer
    packet_stream = PacketStream("0.0.0.0", port)

    # Listen for packets
    packet_generator = packet_stream.listen()

    # Convert it into a file
    file_stream = FileStream(output_path)
    file_stream.from_packets(packet_generator)

    # Wait for all the packets
    file_stream.write()

    # Write received data to file
    packet_stream.close()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 Receiver3.py <Port> <Filename>")
        sys.exit(1)

    port = int(sys.argv[1])
    filename = sys.argv[2]

    receiver1(port, filename)
