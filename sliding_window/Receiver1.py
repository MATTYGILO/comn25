import socket
import sys
import struct

# Constants
CHUNK_SIZE = 1024
SEQ_SIZE = 2
EOF_SIZE = 1
HEADER_SIZE = SEQ_SIZE + EOF_SIZE
PACKET_SIZE = CHUNK_SIZE + HEADER_SIZE

# The


def extract_packet(packet):
    """Extracts header and data from the packet."""
    header = packet[:HEADER_SIZE]
    data = packet[HEADER_SIZE:]
    seq_number, eof_flag = struct.unpack("!H?", header)
    return seq_number, eof_flag, data


def stream_packets(sock):
    """Generator that streams packets from the socket."""
    while True:
        packet, addr = sock.recvfrom(PACKET_SIZE)
        if len(packet) < HEADER_SIZE:
            continue
        seq_number, eof_flag, data = extract_packet(packet)
        yield seq_number, eof_flag, data, addr


def write_to_file(received_data, output_filename):
    """Writes received data to the output file in order of sequence number."""
    with open(output_filename, "wb") as f:
        for seq in sorted(received_data.keys()):
            f.write(received_data[seq])


def receive_file(port, output_filename):
    """Receive a file over UDP and save it to output_filename."""

    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("", port))

    # Store received data
    received_data = {}

    # Stream packets and process
    for seq_number, eof_flag, data, addr in stream_packets(sock):
        # Check for duplicate packets
        if seq_number in received_data:
            print(f"Duplicate packet {seq_number} received. Ignoring.")
            continue

        # Store the data in order of sequence number
        received_data[seq_number] = data

        # Check if it's the last packet
        if eof_flag:
            break

    # Write received data to file
    write_to_file(received_data, output_filename)
    sock.close()


if __name__ == "__main__":
    try:
        port = int(sys.argv[1])
        output_filename = sys.argv[2]
    except IndexError:
        print("Usage: python3 Receiver1.py <Port> <Filename>")
        sys.exit(1)

    receive_file(port, output_filename)
