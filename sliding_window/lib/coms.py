import socket
import struct

from sliding_window.lib.const import ACK_SIZE


def wait_for_ack(sock, seq_number, timeout):
    try:
        sock.settimeout(timeout / 1000)
        ack, addr = sock.recvfrom(ACK_SIZE)
        ack_seq_number = struct.unpack("!H", ack)[0]
        return ack_seq_number == seq_number
    except socket.timeout:
        return False