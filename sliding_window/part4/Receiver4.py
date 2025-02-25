import sys

from sliding_window.lib.file_stream import FileStream
from sliding_window.lib.packet_stream import PacketStream


def receiver4(port, output_path):

    print(f"Receiving file on port {port} and saving to {output_path}")

    # The packet streamer
    packet_stream = PacketStream("0.0.0.0", port)

    # Listen for packets
    packet_generator = packet_stream.listen()

    # Create the file stream to write packets to a file
    file_stream = FileStream(output_path)

    # Main receiving loop
    for packet in packet_generator:
        packet_stream.send_ack(packet.seq_number)
        file_stream.from_packet(packet)

    # Write received data to file
    file_stream.write()

    # Close the packet stream
    packet_stream.close()

    print("Finished receiving file")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 Receiver3.py <Port> <Filename>")
        sys.exit(1)

    port = int(sys.argv[1])
    filename = sys.argv[2]
    windowSize = int(sys.argv[3])

    # Receive
    receiver4(port, filename, windowSize)