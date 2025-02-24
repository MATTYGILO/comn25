import os
import random
import socket
import sys
import struct
import time

# Size of the data chunk
CHUNK_SIZE = 1024

# Header sizes
SEQ_SIZE = 2     # Unsigned short for seq number
EOF_SIZE = 1     # Boolean (or 0/1)
HEADER_SIZE = SEQ_SIZE + EOF_SIZE

# Packet size
PACKET_SIZE = CHUNK_SIZE + HEADER_SIZE

# Size of the acknowledgment packet
ACK_SIZE = SEQ_SIZE


class StreamFile:
    """
    A small helper class that reads chunks from a file.
    It keeps a buffer of the most recent chunks so that we
    can 'rewind' if we need to resend them.
    """
    def __init__(self, filename, chunk_size=1024, buffer_size=3):
        self.filename = filename
        self.chunk_size = chunk_size
        self.buffer_size = buffer_size
        self.buffer = []  # To store the last few chunks
        self.index = 0    # Tracks the 'rewind' position in the buffer
        self.file = open(self.filename, "rb")

    def __iter__(self):
        return self

    def __next__(self):
        """
        Returns the next chunk from the buffer (if rewinding)
        or from the file (if reading forward).
        """
        # If we have a rewind index, return from buffer
        if self.index > 0:
            self.index -= 1
            return self.buffer[self.index]

        # Otherwise, read the next chunk from the file
        chunk = self.file.read(self.chunk_size)
        if not chunk:
            self.file.close()
            raise StopIteration

        # Add the chunk to the front of the buffer
        self.buffer.insert(0, chunk)
        # Enforce our max buffer size
        if len(self.buffer) > self.buffer_size:
            self.buffer.pop()

        return chunk

    def rewind(self, steps=1):
        """
        Moves our 'index' backwards so that future calls
        to __next__() will return older chunks from the buffer.
        """
        self.index = min(self.index + steps, len(self.buffer))




def send_packet(sock, packet, remote_host, port):
    """
    Send one packet over UDP after an artificial delay
    and with simulated loss.
    """
    sock.sendto(packet, (remote_host, port))


def wait_for_ack(sock, seq_number, timeout_ms):
    """
    Attempt to receive an ACK for the given seq_number
    within 'timeout_ms' milliseconds.
    Returns True if an ACK for that sequence was received,
    False if timeout occurred.
    """
    try:
        sock.settimeout(timeout_ms / 1000.0)
        ack_data, _ = sock.recvfrom(ACK_SIZE)
        ack_seq = struct.unpack("!H", ack_data)[0]
        return (ack_seq == seq_number)
    except socket.timeout:
        return False


def send_empty_packet(seq_number, sock, remote_host, port):
    """
    Send an empty packet with EOF flag = 1.
    Useful for signaling file transfer completion.
    """
    eof_flag = 1
    empty_chunk = b'\x00' * CHUNK_SIZE
    packet = build_packet(seq_number, eof_flag, empty_chunk)
    sock.sendto(packet, (remote_host, port))


def send_file(remote_host, port, filename, timeout_ms, window_size):
    """
    Send a file over UDP in chunks with a Go-Back-N mechanism.
    - remote_host: IP or hostname of the receiver
    - port: UDP port of the receiver
    - filename: file to send
    - timeout_ms: retransmission timeout (milliseconds)
    - window_size: maximum GBN window size
    - delay_ms: artificially added send delay (simulates propagation)
    """
    if not os.path.exists(filename):
        print(f"File {filename} not found.")
        return

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Initialize base (n_acked) and nextSeqNum (n_sent)
    n_acked = 0
    n_sent = 0

    start_time = time.time_ns()

    # Initialize the file stream
    # Make sure buffer_size >= window_size so we can rewind
    chunk_stream = StreamFile(filename, chunk_size=CHUNK_SIZE,
                              buffer_size=window_size)

    while True:
        try:
            # If the current window is not full, send the next chunk
            window_index = n_sent - n_acked
            if window_index < window_size:
                chunk = next(chunk_stream)
            else:
                # Window is "full"; skip reading a new chunk
                chunk = None
        except StopIteration:
            # No more chunks => send EOF packet and break
            # but we still need to wait for final acks below
            chunk = None

        # If we got a chunk, send it
        if chunk is None:

            # Send an empty EOF packet
            send_empty_packet(n_sent, sock, remote_host, port)

            break

        else:
            packet = build_packet(n_sent, False, chunk)
            send_packet(sock, packet, remote_host, port)
            n_sent += 1

        # Whenever we either send or skip (due to window full),
        # we check ACKs for everything up to n_sent-1
        # (i.e. the current window).
        # A “proper” GBN uses a single timer for the oldest
        # unacked packet. This example uses a simpler approach:
        # we block on each packet within the window. If any fail,
        # we rewind to n_acked and resend them all.

        if (n_sent - n_acked) == window_size or chunk is None:

            # Attempt to ACK everything in [n_acked, n_sent-1]
            for seq in range(n_acked, n_sent):
                if wait_for_ack(sock, seq, timeout_ms):
                    n_acked += 1
                else:
                    # Missing ACK => go-back-n
                    # We must rewind the chunk stream so the next
                    # time we read, we re-send from n_acked onward
                    # (which effectively re-sends from base).
                    # Example: if we had 5 unacked packets, we rewind them all
                    to_rewind = (n_sent - n_acked)
                    chunk_stream.rewind(to_rewind)
                    # Move n_sent pointer back to the base
                    n_sent = n_acked
                    break

    # Calculate throughput
    end_time = time.time_ns()
    elapsed_s = (end_time - start_time) / 1e9
    file_size_bytes = os.path.getsize(filename)
    throughput_kb_s = (file_size_bytes / 1024.0) / elapsed_s

    # Print throughput (KBytes/s) on a single line
    print(f"{throughput_kb_s:.2f}")

    sock.close()

    raise NotImplementedError("Implement me!")


if __name__ == "__main__":
    try:
        remote_host = sys.argv[1]
        port = int(sys.argv[2])
        filename = sys.argv[3]
        timeout = int(sys.argv[4])      # e.g. 100ms
        window_size = int(sys.argv[5])  # e.g. 5
    except IndexError:
        print("Usage: python3 Sender3.py <RemoteHost> <Port> <Filename> <Timeout_ms> <WindowSize>")
        sys.exit(1)

    send_file(remote_host, port, filename, timeout, window_size)
