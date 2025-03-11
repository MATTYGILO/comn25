import os

def qdisk(loss_rate=0.5, delay=10, rate=5):
    os.system(f"sudo tc qdisc add dev lo root netem loss {loss_rate}% delay {delay}ms rate {rate}mbit")
