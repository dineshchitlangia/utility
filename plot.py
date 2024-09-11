import matplotlib.pyplot as plt
import pandas as pd
import sys
import re

def parse_memory_value(value):
    """Convert memory values with units (M, G) to MB."""
    if pd.isna(value):
        return 0
    value = str(value).strip().upper()
    match = re.match(r'([\d.]+)\s*([MG])', value)
    if match:
        num, unit = match.groups()
        num = float(num)
        if unit == 'G':
            return num * 1024  # Convert GB to MB
        elif unit == 'M':
            return num
    return 0

def read_dstat_file(file_path):
    """Read the dstat output file and extract usr CPU time, memory used, and total memory data."""
    try:
        # Read the dstat file with multiple delimiters (whitespace and |)
        data = pd.read_csv(file_path, delimiter=r'\s*\|\s*|\s+', engine='python', skiprows=1)

        # Check for required columns
        required_columns = ['usr', 'sys', 'used', 'total']
        for col in required_columns:
            if col not in data.columns:
                raise ValueError(f"Required column '{col}' not found in dstat data.")

        # Convert columns to numeric with unit handling
        for col in required_columns:
            if col != 'usr':
                data[col] = data[col].apply(parse_memory_value)
            else:
                data[col] = pd.to_numeric(data[col], errors='coerce').fillna(0)

        return data
    except Exception as e:
        print(f"Error reading dstat file: {e}")
        sys.exit(1)

def plot_cpu_usage(data, output_image):
    """Plot the usr CPU time from dstat data."""
    # Extract time and columns
    time = range(len(data))  # Assuming each row is a time step
    usr = data['usr']
    sys = data['sys']

    # Create the plot
    plt.figure(figsize=(12, 8))

    # Plot usr CPU time
    plt.plot(time, usr, marker='', linestyle='-', color='r', label='User CPU Util (%)')
    plt.plot(time, sys, marker='', linestyle='--', color='b', label='Sys CPU Util (%)')

    title = "CPU Utilization\n" + str(output_image)
    plt.xlabel('Time(seconds)')
    plt.ylabel('Utilization % ')
    plt.title(title)
    plt.legend()
    plt.grid(True)

    # Save the plot to a file
    plt.savefig("cpu_" + output_image.replace(" ","_") + ".png")
    plt.close()  # Close the plot to free memory

def plot_memory_usage(data, output_image):
    """Plot the memory used as percentage of total memory from dstat data."""
    # Extract time and columns
    time = range(len(data))  # Assuming each row is a time step
    used = data['used']
    total = data['total']

    # Calculate memory used as a percentage of total memory
    total_non_zero = total.replace(0, pd.NA)
    used_percentage = (used / total_non_zero) * 100

    # Create the plot
    plt.figure(figsize=(12, 8))

    # Plot memory used percentage
    plt.plot(time, used_percentage, marker='', linestyle='--', color='r', label='Memory Used (%)')

    plt.xlabel('Time(seconds)')
    plt.ylabel('Memory Used (%)')
    title = "Memory Used Percentage Over Time'\n" + str(output_image)
    plt.title(title)
    plt.legend()
    plt.grid(True)

    # Save the plot to a file
    plt.savefig("mem_" + output_image.replace(" ","_") + ".png")
    plt.close()  # Close the plot to free memory

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python plot.py <dstat_file> <label>")
        sys.exit(1)

    dstat_file = sys.argv[1]
    label = sys.argv[2]

    # Read dstat file
    data = read_dstat_file(dstat_file)

    # Plot CPU usage and memory used percentage
    plot_cpu_usage(data, label)
    plot_memory_usage(data, label)

