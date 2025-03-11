#!/usr/bin/env python3
import pandas as pd
import argparse

def analyze_csv(csv_file):
    # Load CSV file into DataFrame.
    df = pd.read_csv(csv_file)
    
    # Remove any leading/trailing whitespace from column names.
    df.columns = df.columns.str.strip()
    
    # Uncomment the following line to debug and view the DataFrame's head.
    # print(df.head())
    
    # Expected columns based on the tshark output:
    required_fields = ['frame.time_epoch', 'frame.len', 'ip.src', 'ip.dst',
                       'tcp.srcport', 'tcp.dstport', 'tcp.len', '_ws.col.info']
    for field in required_fields:
        if field not in df.columns:
            print(f"Field '{field}' is missing in the CSV. Check your tshark capture command.")
            return

    # Convert timestamp and length fields to numeric values.
    df['frame.time_epoch'] = pd.to_numeric(df['frame.time_epoch'], errors='coerce')
    df['frame.len'] = pd.to_numeric(df['frame.len'], errors='coerce')
    df['tcp.len'] = pd.to_numeric(df['tcp.len'], errors='coerce')
    
    # Remove any rows where conversion failed.
    df = df.dropna(subset=['frame.time_epoch', 'frame.len', 'tcp.len'])
    
    # Sort packets by timestamp.
    df.sort_values(by='frame.time_epoch', inplace=True)
    
    # Calculate the capture duration.
    start_time = df['frame.time_epoch'].iloc[0]
    end_time = df['frame.time_epoch'].iloc[-1]
    duration = end_time - start_time
    
    # --- Metric 1: Throughput ---
    # Throughput: Total frame bytes per second.
    total_bytes = df['frame.len'].sum()
    throughput = total_bytes / duration if duration > 0 else 0
    
    # --- Metric 2: Goodput ---
    # Goodput: Sum of TCP payload (tcp.len) per second.
    total_payload = df['tcp.len'].sum()
    goodput = total_payload / duration if duration > 0 else 0
    
    # --- Metric 3: Packet Loss Rate (approximate) ---
    # Approximate loss by counting segments marked as "Retransmission" in the info field.
    retransmissions = df['_ws.col.info'].str.contains("Retransmission", case=False, na=False).sum()
    data_packets = (df['tcp.len'] > 0).sum()
    packet_loss_rate = (retransmissions / data_packets) * 100 if data_packets > 0 else 0
    
    # --- Metric 4: Maximum Packet Size ---
    max_packet_size = df['frame.len'].max()
    
    # Print out the metrics.
    print(f"Capture Duration: {duration:.2f} seconds")
    print(f"Throughput: {throughput:.2f} bytes/sec (Total bytes: {total_bytes})")
    print(f"Goodput: {goodput:.2f} bytes/sec (Total payload: {total_payload})")
    print(f"Packet Loss Rate (approx.): {packet_loss_rate:.2f}%")
    print(f"Maximum Packet Size: {max_packet_size} bytes")
    
def main():
    parser = argparse.ArgumentParser(description="Analyze tshark CSV capture for TCP metrics")
    parser.add_argument("csv_file", help="Path to CSV file (e.g. /tmp/ns1_veth.csv)")
    args = parser.parse_args()
    analyze_csv(args.csv_file)

if __name__ == '__main__':
    main()
