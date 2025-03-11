#!/bin/bash
# run_experiment.sh
# This script sets up two namespaces (ns1 and ns2) connected via a veth pair,
# disables firewall rules, and then runs your TCP server and client to perform the experiment.

# Exit on error
set -e

# Create two network namespaces
sudo ip netns add ns1
sudo ip netns add ns2

# Create a virtual Ethernet pair
sudo ip link add veth-ns1 type veth peer name veth-ns2

# Attach each veth interface to a namespace
sudo ip link set veth-ns1 netns ns1
sudo ip link set veth-ns2 netns ns2

# Bring up the loopback interfaces in each namespace
sudo ip netns exec ns1 ip link set lo up
sudo ip netns exec ns2 ip link set lo up

# Assign IP addresses to the veth interfaces
sudo ip netns exec ns1 ip addr add 10.0.0.1/24 dev veth-ns1
sudo ip netns exec ns2 ip addr add 10.0.0.2/24 dev veth-ns2

# Bring up the veth interfaces
sudo ip netns exec ns1 ip link set veth-ns1 up
sudo ip netns exec ns2 ip link set veth-ns2 up

# Disable firewall rules inside ns1
echo "Disabling firewall in ns1..."
sudo ip netns exec ns1 iptables -F
sudo ip netns exec ns1 iptables -X
sudo ip netns exec ns1 iptables -t nat -F
sudo ip netns exec ns1 iptables -t nat -X
sudo ip netns exec ns1 iptables -P INPUT ACCEPT
sudo ip netns exec ns1 iptables -P OUTPUT ACCEPT
sudo ip netns exec ns1 iptables -P FORWARD ACCEPT

# Disable firewall rules inside ns2
echo "Disabling firewall in ns2..."
sudo ip netns exec ns2 iptables -F
sudo ip netns exec ns2 iptables -X
sudo ip netns exec ns2 iptables -t nat -F
sudo ip netns exec ns2 iptables -t nat -X
sudo ip netns exec ns2 iptables -P INPUT ACCEPT
sudo ip netns exec ns2 iptables -P OUTPUT ACCEPT
sudo ip netns exec ns2 iptables -P FORWARD ACCEPT




# (Optional) Start packet capture on ns1's interface
# Uncomment the next line to capture packets on veth-ns1 into a file.
# sudo ip netns exec ns1 tcpdump -i veth-ns1 -w /tmp/ns1_veth.pcap &

CSV_FILE="delayed_ACK_disabled.csv"

echo "Start the wireshark capture"
sleep 30

# Run the server in ns1 (adjust the path to server.py as needed)
echo "Starting server in ns1..."
sudo ip netns exec ns1 python3 server.py --host 0.0.0.0 --port 5001 --nagle enabled --delayed_ack disabled &
SERVER_PID=$!

# Wait a few seconds for the server to start
sleep 5

# Run the client in ns2 (adjust the path to client.py as needed)
echo "Starting client in ns2..."
sudo ip netns exec ns2 python3 client.py --server 10.0.0.1 --port 5001 --nagle enabled --delayed_ack disabled
CLIENT_PID=$!

echo "Cleaning up background processes..."
sudo kill $SERVER_PID $CLIENT_PID 2>/dev/null || true


# Clean up the namespaces and veth pair
echo "Cleaning up..."
sudo ip netns delete ns1
sudo ip netns delete ns2

echo "Experiment complete."
