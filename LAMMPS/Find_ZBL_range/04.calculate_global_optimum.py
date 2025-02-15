import numpy as np
from collections import defaultdict

# Configuration: List of RMSE result files
RMSE_FILES = [
    "rmse_results_Be-Be.txt",
    "rmse_results_Be-Li.txt",
    "rmse_results_F-Be.txt",
    "rmse_results_F-F.txt",
    "rmse_results_F-Li.txt",
    "rmse_results_Li-Li.txt"
]
OUTPUT_FILE = "rmse_best_d1d2_rmse_summary.txt"

def find_data_start(lines):
    """
    Locate the start of the numerical data in the RMSE files.
    The data typically starts after a line with "=====".
    """
    for i, line in enumerate(lines):
        if line.startswith("="):
            return i + 1  # The next line should contain the data
    return 0  # Default to the beginning if no separator is found

def process_rmse_file(filepath):
    """
    Read an RMSE result file and extract (d1, d2) pairs with their RMSE values.
    """
    try:
        with open(filepath) as f:
            lines = f.readlines()
            
        start_line = find_data_start(lines)
        data_lines = lines[start_line:]
        
        for line in data_lines:
            parts = line.strip().split()
            if len(parts) < 3:
                continue  # Skip malformed lines
            
            try:
                d1 = float(parts[0])
                d2 = float(parts[1])
                rmse = float(parts[2])
                yield (d1, d2), rmse
            except (ValueError, IndexError):
                continue  # Skip lines with incorrect format
                
    except FileNotFoundError:
        print(f"Skipping missing file: {filepath}")

def accumulate_rmse():
    """
    Accumulate RMSE values for each (d1, d2) combination across all RMSE files.
    The total RMSE for each pair is summed across different systems.
    """
    total_rmse = defaultdict(float)
    counts = defaultdict(int)
    
    for file in RMSE_FILES:
        for (d1, d2), rmse in process_rmse_file(file):
            total_rmse[(d1, d2)] += rmse
            counts[(d1, d2)] += 1
    
    # Verify data completeness
    zero_counts = [pair for pair, cnt in counts.items() if cnt == 0]
    if zero_counts:
        print("Warning: The following parameter combinations were never found:", zero_counts)
    
    return total_rmse

def find_optimal_parameters(rmse_data):
    """
    Find the (d1, d2) combination with the minimum total RMSE.
    """
    return min(rmse_data.items(), key=lambda x: x[1])

def save_results(best_pair, total_rmse):
    """
    Save the summarized RMSE results and the optimal (d1, d2) pair to a file.
    """
    with open(OUTPUT_FILE, "w") as f:
        # Write summarized RMSE data
        f.write("d1\t d2\t Total_RMSE\n")
        f.write("=" * 30 + "\n")
        for (d1, d2), value in sorted(total_rmse.items(), key=lambda x: x[1]):
            f.write(f"{d1:.2f}\t{d2:.2f}\t{value:.6f}\n")
        
        # Write the best parameter combination
        f.write("\nOptimal Parameter Combination:\n")
        f.write(f"d1 = {best_pair[0][0]:.2f}, d2 = {best_pair[0][1]:.2f}\n")
        f.write(f"Total RMSE: {best_pair[1]:.6f}\n")

def main():
    print("Processing RMSE data...")

    # Aggregate RMSE values
    total_rmse = accumulate_rmse()
    
    if not total_rmse:
        print("Error: No valid data found")
        return
    
    # Find the best (d1, d2) combination
    best_pair = find_optimal_parameters(total_rmse)
    
    print("\nOptimal Parameter Combination:")
    print(f"d1 = {best_pair[0][0]:.2f}, d2 = {best_pair[0][1]:.2f}")
    print(f"Total RMSE: {best_pair[1]:.6f}")
    
    save_results(best_pair, total_rmse)
    print(f"\nResults saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()