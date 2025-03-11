#!/usr/bin/env python3
import socket
import argparse
import time

def main():
    parser = argparse.ArgumentParser(
        description="TCP Server for Nagle & Delayed-ACK Experiment"
    )
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=5001, help="Port to bind (default: 5001)")
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
    args = parser.parse_args()

    # Create a TCP socket and bind to the host and port
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind((args.host, args.port))
    server_sock.listen(1)
    print(f"Server listening on {args.host}:{args.port}")

    # Accept a connection
    conn, addr = server_sock.accept()
    print(f"Accepted connection from {addr}")

    # --- Set socket options as per configuration ---
    # If Nagle's algorithm is disabled, set TCP_NODELAY (disables packet coalescing)
    if args.nagle == "disabled":
        conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        print("Nagle's algorithm disabled on server socket.")
    else:
        print("Nagle's algorithm enabled on server socket.")

    # If delayed ACK is disabled, attempt to set TCP_QUICKACK (if available)
    if args.delayed_ack == "disabled":
        try:
            conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_QUICKACK, 1)
            print("Delayed ACK disabled on server socket (TCP_QUICKACK enabled).")
        except Exception as e:
            print("TCP_QUICKACK not supported on this platform. (Delayed ACK setting unchanged)")
    else:
        print("Delayed ACK enabled on server socket.")
    # ---------------------------------------------------

    # Receive data (the 4 KB file is sent slowly over ~2 minutes)
    start_time = time.time()
    total_bytes = 0
    buffer_size = 1024

    while True:
        data = conn.recv(buffer_size)
        if not data:
            break
        total_bytes += len(data)
        print(f"Received {len(data)} bytes (Total: {total_bytes} bytes)")

    end_time = time.time()
    duration = end_time - start_time

    print("\n--- Transfer Summary ---")
    print(f"Total bytes received: {total_bytes}")
    print(f"Duration: {duration:.2f} seconds")
    throughput = total_bytes / duration
    print(f"Throughput: {throughput:.2f} bytes/second")
    # In this test, goodput equals throughput because only file data is transferred.
    print(f"Goodput: {throughput:.2f} bytes/second")
    # Packet loss rate and max packet size require external network capture/analysis.
    print("Packet loss rate: N/A (use a packet analyzer for detailed measurement)")
    print("Maximum packet size achieved: N/A (analyze with a packet capture tool)")

    conn.close()
    server_sock.close()

if __name__ == "__main__":
    main()
