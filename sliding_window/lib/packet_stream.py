import socket
import struct
import time
from threading import Thread, Event
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

        # Wait for the ack
        acks = self.wait_for_acks([seq_number], timeout)

        return acks.get(seq_number, False)

    def wait_for_acks(self, indices, timeout, multi_thread=False):
        cancel_event = Event()
        ack_results = {}

        def wait_ack(seq_number):
            if cancel_event.is_set():
                ack_results[seq_number] = False
                return
            try:
                self.sock.settimeout(timeout / 1000)
                ack, self.addr = self.sock.recvfrom(ACK_SIZE)
                result = struct.unpack("!H", ack)[0] == seq_number
                ack_results[seq_number] = result
                if not result:
                    cancel_event.set()
            except socket.timeout:
                ack_results[seq_number] = False
                cancel_event.set()

        if multi_thread:
            threads = []
            for seq_number in indices:
                thread = Thread(target=wait_ack, args=(seq_number,))
                thread.start()
                threads.append(thread)

            for t in threads:
                t.join()
        else:
            for seq_number in indices:
                wait_ack(seq_number)
                if cancel_event.is_set():
                    break

        return ack_results

    def send_ack(self, seq):

        # Send an acknowledgment for the received packet
        ack = struct.pack("!H", seq)
        ack += b'\x00'
        self.sock.sendto(ack, self.addr)

    def send_nack(self, seq):
        nack = struct.pack("!H", seq)
        nack += b'\x01'
        self.sock.sendto(nack, self.addr)

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

