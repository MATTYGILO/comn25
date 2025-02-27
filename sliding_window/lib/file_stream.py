import os

from sliding_window.lib.const import CHUNK_SIZE
from sliding_window.lib.packet import Packet


class FileStream:

    def __init__(self, file_path, debug=True):

        # The dictionary we are building for the data
        self.file_dic = {}
        self.file_path = file_path

        self.debug = debug

    def file_size(self):
        return os.path.getsize(self.file_path)

    def n_packets(self):
        return len(self.file_dic)

    def write(self):

        if self.debug:
            print(f"Writing file to {self.file_path}")

        with open(self.file_path, "wb") as f:
            for seq in sorted(self.file_dic.keys()):
                f.write(self.file_dic[seq])

    def read(self):

        print(f"Reading file from {self.file_path}")

        # Check if file exists
        if not os.path.exists(self.file_path):
            print(f"File {self.file_path} not found.")
            raise FileNotFoundError

        with open(self.file_path, "rb") as f:
            for seq_number, chunk in enumerate(iter(lambda: f.read(CHUNK_SIZE), b'')):
                self.file_dic[seq_number] = chunk

    # The total number of packets
    def __len__(self):
        return len(self.file_dic)

    def to_packets(self):

        # If the file dictionary is empty
        if len(self.file_dic) == 0:
            self.read()

        # If the file dictionary is still empty
        if not self.file_dic:
            raise ValueError("No data to send")

        # The sorted file dic keys
        file_dic_keys = sorted(self.file_dic.keys())

        for seq in file_dic_keys:
            yield self.get_packet(seq)

    def get_packet(self, seq_number):

        # If the file dictionary is empty
        if len(self.file_dic) == 0:
            raise ValueError("No data to send")

        if seq_number not in self.file_dic:
            return None

        # Get the data
        data = self.file_dic[seq_number]

        # Whether the end of the file
        eof_flag = seq_number == len(self.file_dic) - 1

        return Packet(seq_number, eof_flag, data)

    def from_packet(self, packet):

        # Add the packet to the dictionary
        self.file_dic[packet.seq_number] = packet.data

    def from_packets(self, packets):

        # Process the packet
        for packet in packets:

            if self.debug:
                print(f"Received packet {packet.seq_number}")

            # Add the packet to the dictionary
            self.from_packet(packet)

            # If the packet is the last packet
            if packet.eof_flag:
                break

        print("Finished waiting for packets")
