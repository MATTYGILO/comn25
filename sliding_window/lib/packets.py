import struct

from sliding_window.lib.const import HEADER_SIZE, CHUNK_SIZE


def extract_packet(packet):
    """
    Extract the header and data from the packet.
    Header format: !H? => (seq_number, eof_flag)
    """
    header = packet[:HEADER_SIZE]
    data = packet[HEADER_SIZE:]
    seq_number, eof_flag = struct.unpack("!H?", header)
    return seq_number, eof_flag, data


def build_packet(seq_number, eof_flag, chunk):
    """
    Build a packet with:
    - 2-byte sequence number (big-endian)
    - 1-byte EOF flag (True/False)
    - chunk data (padded to CHUNK_SIZE)
    """
    header = struct.pack("!H?", seq_number, eof_flag)
    # Pad the chunk if it's smaller than CHUNK_SIZE
    if len(chunk) < CHUNK_SIZE:
        chunk += b'\x00' * (CHUNK_SIZE - len(chunk))

    return header + chunk
