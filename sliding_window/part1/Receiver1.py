import sys

from sliding_window.lib.file_stream import FileStream
from sliding_window.lib.packet_stream import PacketStream


def receiver1(port, output_path):

    print(f"Receiving file on port {port} and saving to {output_path}")

    # The packet streamer
    packet_stream = PacketStream("", port)

    # Listen for packets
    packet_generator = packet_stream.listen()

    print("Packet generator created")

    for packet in packet_generator:
        print(packet)

    print("Packet generator finished")

    # Convert it into a file
    file_stream = FileStream(output_path)
    file_stream.from_packets(packet_generator)

    # Wait for all the packets
    file_stream.write()

    # Write received data to file
    packet_stream.close()

    print("Finished receiving file 1")


if __name__ == "__main__":
    try:
        port = int(sys.argv[1])
        output_filename = sys.argv[2]
    except IndexError:
        print("Usage: python3 Receiver1.py <Port> <Filename>")
        sys.exit(1)

    receiver1(port, output_filename)
