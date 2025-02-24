import socket

from sliding_window.lib.const import PACKET_SIZE
from sliding_window.lib.packet import Packet


class PacketStream:

    def __init__(self, remote_host, port, packets=None):

        # The packet stream port
        self.remote_host = remote_host
        self.port = port

        # Create a UDP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # The packets provided
        self.packets = packets

    def listen(self):

        # Bind the socket
        self.sock.bind(("", self.port))

        while True:

            # Receive a packet
            packet_bytes, addr = self.sock.recvfrom(PACKET_SIZE)

            # Get the packet
            packet = Packet.from_bytes(packet_bytes)

            yield packet

    def stream(self, packet_generator):

        # Bind the socket
        self.sock.bind((self.remote_host, self.port))

        # Loop through the packets in the file stream
        for packet in packet_generator:

            # Send the data to the stream
            self.sock.sendto(packet.build(), (self.remote_host, self.port))

    def close(self):
        self.sock.close()

    @classmethod
    def from_packets(cls, port, packet_generator):
        """Create a PacketStream from a FileStream."""

        # Create the packet stream
        packet_stream = cls(port)

        # Stream the packets
        packet_stream.stream(packet_generator)

        return packet_stream

