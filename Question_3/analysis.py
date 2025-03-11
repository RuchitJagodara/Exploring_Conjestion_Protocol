#!/usr/bin/env python3
import pandas as pd
import argparse
import re

def extract_ports_from_info(info):
    """
    Extracts source and destination ports from the Info field.
    Expected pattern: "src_port > dst_port" somewhere in the string.
    Returns a tuple (src_port, dst_port) or (None, None) if not found.
    """
    match = re.search(r"(\d+)\s*>\s*(\d+)", info)
    if match:
        return int(match.group(1)), int(match.group(2))
    return None, None

def analyze_csv(csv_file, ip_filter="127.0.0.1", tcp_port=5001, header_size=40):
    # Read CSV file.
    df = pd.read_csv(csv_file)
    print(f"Total packets in CSV: {len(df)}")
    
    # Filter based on IP and TCP protocol.
    # Use "Source" and "Destination" columns, and if available, port columns.
    if "Source Port" in df.columns and "Destination Port" in df.columns:
        filtered_df = df[
            (((df["Source"] == ip_filter) | (df["Destination"] == ip_filter)) &
             ((df["Source Port"] == tcp_port) | (df["Destination Port"] == tcp_port)) &
             (df["Protocol"].str.upper() == "TCP"))
        ]
    else:
        # Fall back to checking the Info column.
        filtered_df = df[
            (((df["Source"] == ip_filter) | (df["Destination"] == ip_filter)) &
             (df["Protocol"].str.upper() == "TCP") &
             (df["Info"].astype(str).str.contains(str(tcp_port))))
        ]
    
    print(f"Packets after filtering: {len(filtered_df)}")
    
    if filtered_df.empty:
        print("No matching records found for the given IP and port.")
        return

    # Convert Time to numeric and calculate capture duration.
    filtered_df["Time"] = pd.to_numeric(filtered_df["Time"], errors="coerce")
    start_time = filtered_df["Time"].min()
    end_time = filtered_df["Time"].max()
    duration = end_time - start_time if end_time > start_time else 1

    # Overall Throughput is based on all filtered packets.
    total_bytes = filtered_df["Length"].sum()
    throughput = total_bytes / duration

    # Maximum packet size in the filtered set.
    max_packet_size = filtered_df["Length"].max()

    # --- Goodput Calculation ---
    # We want to sum only the payload (i.e. actual file data) from client-to-server packets.
    # Client-to-server packets should have the server’s port as the destination.
    if "Destination Port" in filtered_df.columns:
        goodput_df = filtered_df[filtered_df["Destination Port"] == tcp_port]
    else:
        # If port columns are missing, extract destination port from the Info field.
        filtered_df["dst_port"] = filtered_df["Info"].apply(lambda x: extract_ports_from_info(str(x))[1])
        goodput_df = filtered_df[filtered_df["dst_port"] == tcp_port]
    
    # If Wireshark exported a tcp.len column, use that as the payload length.
    if "tcp.len" in filtered_df.columns:
        # Convert tcp.len to numeric.
        goodput_df["tcp.len"] = pd.to_numeric(goodput_df["tcp.len"], errors="coerce").fillna(0)
        total_payload = goodput_df["tcp.len"].sum()
    else:
        # Otherwise, assume payload = Length - header_size, but only if positive.
        goodput_df = goodput_df.copy()
        goodput_df["Payload"] = goodput_df["Length"].apply(lambda x: x - header_size if (x - header_size) > 0 else 0)
        total_payload = goodput_df["Payload"].sum()

    goodput = total_payload / duration

    # --- Packet Loss Rate ---
    # We estimate loss by counting packets whose Info field indicates "Retransmission"
    # among the client-to-server packets.
    if "Destination Port" in filtered_df.columns:
        retrans_df = filtered_df[filtered_df["Destination Port"] == tcp_port]
    else:
        retrans_df = filtered_df[filtered_df["dst_port"] == tcp_port]
    retransmissions = retrans_df["Info"].astype(str).str.contains("Retransmission", case=False, na=False).sum()
    # Count data packets (those with payload).
    if "tcp.len" in filtered_df.columns:
        data_packets = (retrans_df["tcp.len"].astype(float) > 0).sum()
    else:
        data_packets = (goodput_df["Payload"] > 0).sum()
    packet_loss_rate = retransmissions / data_packets if data_packets > 0 else 0

    print("\n---- Analysis Results ----")
    print(f"Capture Duration: {duration:.2f} seconds")
    print(f"Total Bytes Transferred: {total_bytes}")
    print(f"Throughput: {throughput:.2f} bytes/second")
    print(f"Total Goodput (Payload Bytes): {total_payload}")
    print(f"Goodput: {goodput:.2f} bytes/second")
    print(f"Maximum Packet Size: {max_packet_size} bytes")
    print(f"Retransmissions (indicative of packet loss events): {retransmissions}")
    print(f"Estimated Packet Loss Rate: {packet_loss_rate:.2%}")
    
    # --- Identify Extra Packets ---
    # Extra packets here are those that do not carry any TCP payload,
    # which likely include handshake (SYN, SYN-ACK), pure ACK, FIN packets, etc.
    if "tcp.len" in filtered_df.columns:
        extra_packets = filtered_df[filtered_df["tcp.len"].astype(float) == 0]
    else:
        extra_packets = filtered_df[filtered_df["Length"] <= header_size]
    
    print(f"\nExtra packets count (likely handshake, ACK, FIN, etc.): {len(extra_packets)}")
    print("Examples of extra packets from the Info field:")
    print(extra_packets["Info"].head(10).to_string(index=False))

def main():
    parser = argparse.ArgumentParser(
        description="Analyze Wireshark CSV file for TCP performance metrics with refined filtering."
    )
    parser.add_argument("csv_file", help="Path to the Wireshark CSV file")
    parser.add_argument("--ip", default="127.0.0.1", help="IP address to filter on (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=5001, help="TCP port to filter on (default: 5001)")
    args = parser.parse_args()
    
    analyze_csv(args.csv_file, ip_filter=args.ip, tcp_port=args.port)

if __name__ == "__main__":
    main()
