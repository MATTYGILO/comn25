import random
import socket
import struct
from concurrent.futures import ThreadPoolExecutor, as_completed
from sliding_window.lib.const import PACKET_SIZE, ACK_SIZE
from sliding_window.lib.packet import Packet


class PacketStream:

    def __init__(self, remoteHost, port, packets=None, debug=True, buffer_size=None):

        # The packet stream port
        self.remoteHost = remoteHost
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
            return struct.unpack("!H", ack)[0]
        except socket.timeout:
            print("{} timeout out".format(seq_number))
            return None

    def should_stop(self, ack_results, indices):
        # Check each index; if any value is still None, we can't decide yet.
        # If any value is False, we trigger early stop.
        for index in indices:
            if ack_results[index] is None:
                return False
            if ack_results[index] is False:
                return True
        return False

    def wait_for_acks(self, indices, timeout, multi_thread=False):

        # The results of the acks
        ack_results = {i: None for i in indices}

        with ThreadPoolExecutor(max_workers=len(indices) if multi_thread else 1) as executor:

            # Submit tasks and map each future to its corresponding index
            future_to_index = {executor.submit(self.wait_for_ack, i, timeout): i for i in indices}

            for future in as_completed(future_to_index):
                index = future_to_index[future]
                result = future.result()

                # Add the result to the ack_results
                ack_results[index] = result

                # Check if there is a True, ... , False
                if not multi_thread and self.should_stop(ack_results, indices):
                    break

        return ack_results

    def send_packets(self, packets):

        # Send all packets in the window
        for packet in packets:

            if packet is None:
                break

            # Send the packet
            if random.random() > 0.0005:
                self.sock.sendto(packet.to_bytes(), (self.remoteHost, self.port))

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
        self.sock.bind((self.remoteHost, self.port))

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

