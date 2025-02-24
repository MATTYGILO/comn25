

def construct_file(file_packets: dict, output_filename: str):

    # Check there is an unbroken sequence of packets
    seq_numbers = list(file_packets.keys())
    seq_numbers.sort()

    # Check for missing packets
    if seq_numbers != list(range(len(seq_numbers))):
        raise ValueError("Missing packets")

    # Write the packets to the file
    with open(output_filename, "wb") as f:
        for seq_number in seq_numbers:
            f.write(file_packets[seq_number])
