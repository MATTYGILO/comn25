import socket
import struct
import time

from sliding_window.lib.const import PACKET_SIZE, ACK_SIZE
from sliding_window.lib.packet import Packet


class PacketStream:

    def __init__(self, remote_host, port, packets=None, debug=True, buffer_size=None):

        # The packet stream port
        self.remote_host = remote_host
        self.port = port

        # Create a UDP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # The packets provided
        self.packets = packets
        self.addr = None

        # Debug mode
        self.debug = debug

        # Set the buffer size
        self.buffer_size = buffer_size
        self.buffer = [] if buffer_size else None

    def wait_for_ack(self, seq_number, timeout):
        try:
            self.sock.settimeout(timeout / 1000)
            ack, self.addr = self.sock.recvfrom(ACK_SIZE)
            ack_seq_number = struct.unpack("!H", ack)[0]
            return ack_seq_number == seq_number
        except socket.timeout:
            return False

    def send_ack(self, seq_number):

        # Send an acknowledgment for the received packet
        ack = struct.pack("!H", seq_number)

        # Make it the ack size
        if len(ack) < ACK_SIZE:
            ack += b'\x00' * (ACK_SIZE - len(ack))
        else:
            ack = ack[:ACK_SIZE]

        print("Sending ack {}".format(seq_number))

        self.sock.sendto(ack, self.addr)

    def listen(self):

        # Bind the socket
        self.sock.bind((self.remote_host, self.port))

        if self.debug:
            print(f"Listening on port {self.port}...")

        while True:

            # Receive a packet
            packet_bytes, self.addr = self.sock.recvfrom(PACKET_SIZE)

            # Get the packet
            packet = Packet.from_bytes(packet_bytes)

            yield packet

            # If the packet is the last one
            if packet.eof_flag:
                break

    def close(self):
        self.sock.close()

