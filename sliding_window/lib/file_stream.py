import os

from sliding_window.lib.const import CHUNK_SIZE
from sliding_window.lib.packet import Packet


class FileStream:

    def __init__(self, file_path, debug=True):

        # The dictionary we are building for the data
        self.file_dic = {}
        self.file_path = file_path

        self.debug = debug

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

        # The last sequence number
        last_seq = file_dic_keys[-1]

        for seq in file_dic_keys:

            # Whether end of file
            eof_flag = last_seq == seq

            # Create the packet
            packet = Packet(seq, eof_flag, self.file_dic[seq])

            yield packet

    def from_packets(self, packets):

        print("Waiting for packets")

        # Process the packet
        for packet in packets:

            if self.debug:
                print(f"Received packet {packet.seq_number}")

            # Add the packet to the dictionary
            self.file_dic[packet.seq_number] = packet.data

            # If the packet is the last packet
            if packet.eof_flag:
                break

        print("Finished waiting for packets")
