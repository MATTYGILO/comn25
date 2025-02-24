# VirtualLink.py
import struct
import sys
import time
import socket
import threading
import queue
import random




class DelayedForwarder:
    """
    Spawns a background thread that delivers (packet, destination)
    after a configured delay. The user calls forward(...) to enqueue
    a packet to be sent after 'delay_ms' milliseconds.
    """
    def __init__(self, delay_ms=5, packet_drop_prob=0.0):
        self.delay_s = delay_ms / 1000.0
        self.packet_drop_prob = packet_drop_prob
        self.q = queue.Queue()
        self.alive = True
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()

    def run(self):
        while self.alive:
            try:
                send_time, sock, packet, dest = self.q.get(timeout=0.05)
            except queue.Empty:
                continue

            now = time.time()
            wait = send_time - now
            if wait > 0:
                time.sleep(wait)

            try:
                sock.sendto(packet, dest)
            except OSError:
                # Socket may have closed
                pass

    def forward(self, sock, packet, dest):

        # Get the id from the packet
        seq_number, eof_flag, data = extract_packet(packet)

        print("seq_number: ", seq_number)
        print("eof_flag: ", eof_flag)

        send_time = time.time() + self.delay_s
        if random.random() > self.packet_drop_prob:
            self.q.put((send_time, sock, packet, dest))

    def stop(self):
        self.alive = False
        self.thread.join()


def usage():
    print("Usage: python3 VirtualLink.py <sender_listen_port> <receiver_listen_port> "
          "<receiver_dest_port> <sender_dest_port> <delay_ms>")
    print("Example: python3 VirtualLink.py 9000 9001 12345 54321 5")
    sys.exit(1)

def main():
    # Parse CLI
    if len(sys.argv) != 6:
        usage()

    sender_listen_port = int(sys.argv[1])
    receiver_listen_port = int(sys.argv[2])
    receiver_dest_port = int(sys.argv[3])
    sender_dest_port = int(sys.argv[4])
    delay_ms = int(sys.argv[5])
    packet_drop_prob = 0.005

    # Create sockets for listening:
    # - sock_sender listens on <sender_listen_port>
    # - sock_receiver listens on <receiver_listen_port>
    sock_sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock_sender.bind(("127.0.0.1", sender_listen_port))

    sock_receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock_receiver.bind(("127.0.0.1", receiver_listen_port))

    forwarder = DelayedForwarder(delay_ms=delay_ms, packet_drop_prob=packet_drop_prob)

    print(f"VirtualLink started. Delaying each packet by {delay_ms} ms.")
    print(f"Listening for sender data on port {sender_listen_port} -> forwarding to port {receiver_dest_port}")
    print(f"Listening for receiver data on port {receiver_listen_port} -> forwarding to port {sender_dest_port}")

    try:
        while True:
            # Use select or just do a simple non-blocking check in a tight loop
            # We'll do a blocking check with small timeouts
            sock_sender.settimeout(0.1)
            sock_receiver.settimeout(0.1)
            try:
                data, addr = sock_sender.recvfrom(65535)
                # Forward to the real receiver on 127.0.0.1:receiver_dest_port
                forwarder.forward(sock_sender, data, ("127.0.0.1", receiver_dest_port))
            except socket.timeout:
                pass

            try:
                data, addr = sock_receiver.recvfrom(65535)
                # Forward to the real sender on 127.0.0.1:sender_dest_port
                forwarder.forward(sock_receiver, data, ("127.0.0.1", sender_dest_port))
            except socket.timeout:
                pass

    except KeyboardInterrupt:
        print("\nShutting down VirtualLink.")
    finally:
        forwarder.stop()
        sock_sender.close()
        sock_receiver.close()


if __name__ == "__main__":
    main()
