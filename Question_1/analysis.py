import pandas as pd
import argparse

def compute_metrics(csv_file):
    # Read CSV data
    df = pd.read_csv(csv_file)

    # Ensure required columns exist
    if 'Time' not in df.columns or 'Length' not in df.columns:
        print("CSV must contain 'Time' and 'Length' columns.")
        return

    # Convert Time and Length to numeric values
    df['Time'] = pd.to_numeric(df['Time'], errors='coerce')
    df['Length'] = pd.to_numeric(df['Length'], errors='coerce').fillna(0)

    # Compute capture duration
    duration = df['Time'].max() - df['Time'].min()
    if duration <= 0:
        print("Invalid capture duration. Check the 'Time' column in the CSV.")
        return

    # Compute Goodput (in bits per second)
    total_payload = df['Length'].sum()
    goodput_bps = (total_payload * 8) / duration

    # Packet Loss Rate Estimation
    if 'Info' in df.columns:
        duplicate_packets = df['Info'].duplicated().sum()  # Approximation for retransmissions
    else:
        duplicate_packets = 0  # No Info field, cannot estimate loss effectively

    total_packets = len(df)
    packet_loss_rate = (duplicate_packets / total_packets * 100) if total_packets > 0 else 0

    # Print results
    print("Capture Duration: {:.2f} seconds".format(duration))
    print("Total Payload (from Length column): {} bytes".format(total_payload))
    print("Goodput: {:.2f} bits per second".format(goodput_bps))
    print("Total Packets: {}".format(total_packets))
    print("Estimated Duplicate Packets (approx. retransmissions): {}".format(duplicate_packets))
    print("Estimated Packet Loss Rate: {:.2f}%".format(packet_loss_rate))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Calculate Goodput and Approximate Packet Loss Rate from CSV"
    )
    parser.add_argument("csv_file", help="Path to the CSV file (e.g., h1_parta.csv)")
    args = parser.parse_args()
    compute_metrics(args.csv_file)
