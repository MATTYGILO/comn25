import struct

from sliding_window.lib.const import HEADER_SIZE, CHUNK_SIZE


class Packet:

    def __init__(self, seq_number, eof_flag, data):
        self.seq_number = seq_number
        self.eof_flag = eof_flag
        self.data = data

    @classmethod
    def from_bytes(cls, packet):
        """
        Extract the header and data from the packet.
        Header format: !H? => (seq_number, eof_flag)
        """

        if len(packet) < HEADER_SIZE:
            raise ValueError("Packet is too small")

        header = packet[:HEADER_SIZE]
        data = packet[HEADER_SIZE:]
        seq_number, eof_flag = struct.unpack("!H?", header)
        return cls(seq_number, eof_flag, data)

    def to_bytes(self):
        """
        Build a packet with:
        - 2-byte sequence number (big-endian)
        - 1-byte EOF flag (True/False)
        - chunk data (padded to CHUNK_SIZE)
        """
        header = struct.pack("!H?", self.seq_number, self.eof_flag)

        # Pad the chunk if it's smaller than CHUNK_SIZE
        if len(self.data) < CHUNK_SIZE:
            self.data += b'\x00' * (CHUNK_SIZE - len(self.data))

        return header + self.data
