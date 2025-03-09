#!/bin/bash

# Modify Linux kernel parameters for SYN flood attack
echo "Setting Linux kernel parameters for SYN flood attack..."
sysctl -w net.ipv4.tcp_max_syn_backlog=4096
sysctl -w net.ipv4.tcp_syncookies=0
sysctl -w net.ipv4.tcp_synack_retries=2

# Start tcpdump to capture packets
echo "Starting tcpdump to capture packets..."
tcpdump -i eth0 -w /home/chirag/Computer_Networks/assignment_2/capture.pcap &

# Start legitimate traffic (replace with actual command)
echo "Starting legitimate traffic..."
# ...command to start legitimate traffic...

# Wait for 20 seconds
sleep 20

# Start SYN flood attack (replace with actual command)
echo "Starting SYN flood attack..."
# ...command to start SYN flood attack...

# Wait for 100 seconds
sleep 100

# Stop SYN flood attack (replace with actual command)
echo "Stopping SYN flood attack..."
# ...command to stop SYN flood attack...

# Wait for 20 seconds
sleep 20

# Stop legitimate traffic (replace with actual command)
echo "Stopping legitimate traffic..."
# ...command to stop legitimate traffic...

# Stop tcpdump
echo "Stopping tcpdump..."
pkill tcpdump

echo "SYN flood attack simulation completed."
