import time


def throughput(func, file_size, params):

    # Start time
    start_time = time.time_ns()

    # Call the function
    func(*params)

    # Time elapsed
    elapsed_time = time.time_ns() - start_time

    # Output the throughput in KB/s
    throughput = (file_size / 1024.0) / (elapsed_time / 1e9)  # KB/s

    print(throughput)
