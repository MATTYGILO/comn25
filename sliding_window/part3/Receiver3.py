import sys
from collections import deque

from sliding_window.lib.file_stream import FileStream
from sliding_window.lib.packet_stream import PacketStream


def receiver3(port, output_path):

    print(f"Receiving file on port {port} and saving to {output_path}")

    # The packet streamer
    packet_stream = PacketStream("0.0.0.0", port)

    # Listen for packets
    packet_generator = packet_stream.listen()

    # Go-Back-N variables
    expected_seq_num = 0
    received_packets = deque()

    # Create the file stream to write packets to a file
    file_stream = FileStream(output_path)

    # Main receiving loop
    for packet in packet_generator:

        # Check if the packet sequence number is as expected
        if packet.seq_number == expected_seq_num:
            # Correct packet, add to buffer and send ACK
            received_packets.append(packet)
            print(f"Received expected packet {packet.seq_number}")
            packet_stream.send_ack(packet.seq_number)
            expected_seq_num += 1

            # Deliver packets in order
            while received_packets and received_packets[0].seq_number == expected_seq_num:
                received_packets.popleft()
                expected_seq_num += 1

        elif packet.seq_number < expected_seq_num:
            # Duplicate packet, resend ACK
            print(f"Duplicate packet {packet.seq_number}, resending ACK")
            packet_stream.send_ack(packet.seq_number)

        else:
            # Out-of-order packet, ignore it
            print(f"Out-of-order packet {packet.seq_number}, expected {expected_seq_num}")

    # Convert received packets into a file
    file_stream.from_packets(received_packets)

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

    receiver3(port, filename)
