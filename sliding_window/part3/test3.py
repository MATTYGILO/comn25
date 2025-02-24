import subprocess
import time
import matplotlib.pyplot as plt

def save_plot(window_sizes, throughput_5ms, throughput_25ms, throughput_100ms):
    plt.figure(figsize=(10, 6))
    plt.plot(window_sizes, throughput_5ms, marker='o', label='Delay (5ms)', color='blue')
    plt.plot(window_sizes, throughput_25ms, marker='s', label='Delay (25ms)', color='orange')
    plt.plot(window_sizes, throughput_100ms, marker='^', label='Delay (100ms)', color='grey')

    plt.xscale('log', basex=2)
    plt.xlabel('Window Size')
    plt.ylabel('Throughput (KBps)')
    plt.title('Throughput vs Window Size (Go-Back-N) with VirtualLink')
    plt.legend()
    plt.grid(True)
    plt.show()

def get_avg_throughput(window, delay):
    runs = 5
    results = []

    for _ in range(runs):
        # 1. Start VirtualLink proxy with the chosen one-way delay.
        #    Suppose we want the real receiver on 12345, the real sender on 54321,
        #    so we forward from SENDER_LISTEN_PORT=9000 -> 12345 (receiver),
        #    and from RECEIVER_LISTEN_PORT=9001 -> 54321 (sender).
        # link = subprocess.Popen([
        #     "python3", "VirtualLink.py",
        #     "54321",         # SENDER_LISTEN_PORT
        #     "12345",         # RECEIVER_LISTEN_PORT
        #     "12345",        # RECEIVER_DEST_PORT
        #     "54321",        # SENDER_DEST_PORT
        #     str(delay)      # delay_ms
        # ])
        #
        # time.sleep(1)

        # 2. Start the receiver on port 12345
        receiver = subprocess.Popen(
            ["python3", "Receiver3.py", "12345", "received.jpg"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

        time.sleep(1)  # Give the receiver a moment to bind

        # 3. Start the sender, pointing to the VirtualLink port 9000
        #    Also specifying the ack listen port 54321 in your Sender3 code
        #    if you have that capability. If not, you might rely on ephemeral ports.
        sender = subprocess.Popen(
            ["python3", "Sender3.py", "localhost", "54321", "test.jpg", "100", str(window)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

        # 4. Capture throughput
        sender_output, sender_error = sender.communicate()
        sender_returncode = sender.wait()

        # 5. Wait for receiver to finish
        receiver_returncode = receiver.wait()

        # 6. Stop the VirtualLink
        link.terminate()
        link.wait()

        # 7. Parse the sender's throughput
        try:
            throughput = float(sender_output.decode().strip())
            results.append(throughput)
        except ValueError:
            print("Error parsing throughput. Output was:", sender_output)

    return sum(results) / len(results) if results else 0.0

if __name__ == "__main__":
    window_sizes = [1, 2, 4, 8, 16, 32, 64, 128, 256]
    delays = [5, 25, 100]

    # Gather results
    throughput_5ms, throughput_25ms, throughput_100ms = [], [], []

    for delay in delays:
        print(f"\n--- Testing Delay = {delay} ms ---")
        for w in window_sizes:
            print(f"  Window Size = {w} ...")
            avg_t = get_avg_throughput(w, delay)
            print(f"    -> Average Throughput: {avg_t:.2f} KB/s")

            if delay == 5:
                throughput_5ms.append(avg_t)
            elif delay == 25:
                throughput_25ms.append(avg_t)
            elif delay == 100:
                throughput_100ms.append(avg_t)

    # Plot results
    save_plot(window_sizes, throughput_5ms, throughput_25ms, throughput_100ms)
