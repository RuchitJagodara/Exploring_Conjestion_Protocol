#!/usr/bin/env python3
import socket
import argparse
import time
import os

def main():
    parser = argparse.ArgumentParser(
        description="TCP Client for Nagle & Delayed-ACK Experiment"
    )
    parser.add_argument("--server", default="127.0.0.1", help="Server IP address (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=5001, help="Server port (default: 5001)")
    parser.add_argument(
        "--nagle",
        choices=["enabled", "disabled"],
        default="enabled",
        help="Nagle's algorithm (enabled or disabled, default: enabled)",
    )
    parser.add_argument(
        "--delayed_ack",
        choices=["enabled", "disabled"],
        default="enabled",
        help="Delayed ACK (enabled or disabled, default: enabled)",
    )
    parser.add_argument(
        "--file",
        default="data_4KB.bin",
        help="Path to 4 KB file to send (default: data_4KB.bin)",
    )
    args = parser.parse_args()

    # Ensure the 4KB file exists; if not, generate a simple 4KB file.
    if not os.path.exists(args.file):
        print(f"File '{args.file}' not found. Generating a 4 KB file.")
        with open(args.file, "wb") as f:
            f.write(b"A" * 4096)

    with open(args.file, "rb") as f:
        file_data = f.read()

    # Create a TCP client socket and connect to the server.
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_sock.connect((args.server, args.port))
    print(f"Connected to server {args.server}:{args.port}")

    # --- Set socket options as per configuration ---
    # Disable Nagle if required.
    if args.nagle == "disabled":
        client_sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        print("Nagle's algorithm disabled on client socket.")
    else:
        print("Nagle's algorithm enabled on client socket.")

    # Disable delayed ACK if requested (using TCP_QUICKACK, if available).
    if args.delayed_ack == "disabled":
        try:
            client_sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_QUICKACK, 1)
            print("Delayed ACK disabled on client socket (TCP_QUICKACK enabled).")
        except Exception as e:
            print("TCP_QUICKACK not supported on this platform. (Delayed ACK setting unchanged)")
    else:
        print("Delayed ACK enabled on client socket.")
    # ---------------------------------------------------

    # Send the file slowly at 40 bytes per second.
    chunk_size = 40
    total_bytes = 0
    start_time = time.time()

    print("\n--- Starting File Transfer ---")
    for i in range(0, len(file_data), chunk_size):
        chunk = file_data[i : i + chunk_size]
        bytes_sent = client_sock.send(chunk)
        total_bytes += bytes_sent
        print(f"Sent {bytes_sent} bytes (Total sent: {total_bytes} bytes)")
        # Sleep for 1 second to maintain a rate of 40 bytes/second.
        time.sleep(1)

    end_time = time.time()
    duration = end_time - start_time

    print("\n--- Transfer Summary ---")
    print(f"Total bytes sent: {total_bytes}")
    print(f"Duration: {duration:.2f} seconds")
    throughput = total_bytes / duration
    print(f"Throughput: {throughput:.2f} bytes/second")
    print(f"Goodput: {throughput:.2f} bytes/second")
    print("Packet loss rate: N/A (use a packet analyzer for detailed measurement)")
    print("Maximum packet size achieved: N/A (analyze with a packet capture tool)")

    client_sock.close()

if __name__ == "__main__":
    main()
