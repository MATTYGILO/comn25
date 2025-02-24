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

def main():
    pass

if __name__ == "__main__":
    pass