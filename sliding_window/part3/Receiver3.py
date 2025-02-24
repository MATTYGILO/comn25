import socket
import sys
import struct

# Constants
CHUNK_SIZE = 1024
SEQ_SIZE = 2
EOF_SIZE = 1
HEADER_SIZE = SEQ_SIZE + EOF_SIZE
PACKET_SIZE = CHUNK_SIZE + HEADER_SIZE
ACK_SIZE = SEQ_SIZE

def extract_packet(packet):
    """
    Extract the header and data from the packet.
    Header format: !H? => (seq_number, eof_flag)
    """
    header = packet[:HEADER_SIZE]
    data = packet[HEADER_SIZE:]
    seq_number, eof_flag = struct.unpack("!H?", header)
    return seq_number, eof_flag, data

def send_ack(sock, ack_seq_num, addr):
    """
    Send an acknowledgment for the cumulative highest
    in-order sequence number we have received so far.
    """
    # We store just the seq_number in 2 bytes (unsigned short, big-endian)
    ack_data = struct.pack("!H", ack_seq_num)
    # Ensure we always send exactly ACK_SIZE bytes
    if len(ack_data) < ACK_SIZE:
        ack_data += b'\x00' * (ACK_SIZE - len(ack_data))
    elif len(ack_data) > ACK_SIZE:
        ack_data = ack_data[:ACK_SIZE]

    sock.sendto(ack_data, addr)

def receive_file(port, output_filename):
    """
    Receive a file over UDP and save it to output_filename using
    a basic Go-Back-N approach:
      - expectedSeqNum tracks the next in-order sequence number.
      - Out-of-order packets are discarded.
      - We send cumulative ACKs for the highest contiguous seq received.
      - Stop on an in-order packet that carries eof_flag=1.
    """

    # Create a UDP socket and bind to the given port
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("", port))

    # This dictionary will hold the data for each in-order packet we accept
    # Key: seq_number, Value: raw chunk data
    received_data = {}

    # The next sequence number we want to see
    expectedSeqNum = 0

    print(f"Receiver listening on port {port} ...")

    while True:
        # Block until we receive up to PACKET_SIZE bytes
        packet, addr = sock.recvfrom(PACKET_SIZE + 100)  # a bit extra is OK

        # Ignore any weird short packets
        if len(packet) < HEADER_SIZE:
            continue

        seq_number, eof_flag, data = extract_packet(packet)

        # If this is exactly the packet we expect:
        if seq_number == expectedSeqNum:
            # Store the data
            received_data[seq_number] = data
            # Increment expectedSeqNum
            expectedSeqNum += 1

            # Send an ACK for the newly received packet
            # (which means we have now cumulatively received up to seq_number)
            send_ack(sock, seq_number, addr)

            # If it's the last packet (EOF set), we can stop
            if eof_flag:
                break

        else:
            # Out of order or duplicate
            # GBN discards out-of-order packets
            # We still send an ACK for the highest in-order packet we have
            # That is expectedSeqNum - 1
            # (If we've never received anything in-order, that's -1, but
            # typically the sender won't rely on negative ACK in practice)
            ack_seq_num = expectedSeqNum - 1
            if ack_seq_num < 0:
                ack_seq_num = 0
            send_ack(sock, ack_seq_num, addr)

    # Once we exit the loop, we have all in-order packets [0 .. expectedSeqNum-1]
    # Write them to disk in ascending order
    with open(output_filename, "wb") as f:
        for seq in range(expectedSeqNum):
            # In pure GBN, we always had them in order. But just in case:
            f.write(received_data[seq])

    sock.close()
    print(f"File received successfully as {output_filename}")

if __name__ == "__main__":
    # Usage: python3 Receiver3.py <Port> <Filename>
    try:
        port = int(sys.argv[1])
        out_filename = sys.argv[2]
    except (IndexError, ValueError):
        print("Usage: python3 Receiver3.py <Port> <Filename>")
        sys.exit(1)

    receive_file(port, out_filename)
