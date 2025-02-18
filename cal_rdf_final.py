# ------------------------------------------------------------
# FLiBe Radial Distribution Function (RDF) Analysis Script
# Date: 2025-02-17
# Description:
# This script processes RDF data output from LAMMPS, performs averaging, and visualizes the results.
# It includes data reading, averaging, saving, and plotting functionalities.
# ------------------------------------------------------------

import numpy as np
import matplotlib.pyplot as plt

# ============================================================
# 1. Parameter Settings
# ============================================================

rdf_file        = "flibe.rdf"               # RDF file output from LAMMPS
output_file     = "averaged_rdf.txt"        # File to save averaged RDF values

# RDF distribution parameters
nbins           = 100                       # Number of bins for RDF
expected_column_count = 14                  # Number of columns in RDF file (based on LAMMPS settings)
g_indices       = [2, 4, 6, 8, 10, 12]      # Column indices for RDF g(r) data

# Initialize RDF data storage matrix (first column for r values)
rdf_data = np.zeros((nbins, len(g_indices) + 1))
frame_count = 0                             # Count of RDF frames

# ============================================================
# 2. Read RDF Data
# ============================================================
print(f"Reading RDF file: {rdf_file}")
with open(rdf_file, "r") as f:
    lines = f.readlines()[3:]               # Skip the first 3 lines (header information)

line_idx = 0
while line_idx < len(lines):
    line = lines[line_idx].strip()
    if len(line.split()) == 2:              # Detect new frame marker
        frame_count += 1
        line_idx += 1
        for i in range(nbins):
            data_line = lines[line_idx].strip().split()
            if len(data_line) == expected_column_count:
                rdf_data[i, 0] += float(data_line[1])  # r value
                for col_idx, g_idx in enumerate(g_indices):
                    rdf_data[i, col_idx + 1] += float(data_line[g_idx])  # RDF value
            else:
                raise ValueError(f"Unexpected data format at line {line_idx + 1}: {lines[line_idx]}")
            line_idx += 1
    else:
        raise ValueError(f"Unexpected format in line {line_idx + 1}: {line}")

# ============================================================
# 3. Calculate RDF Averages
# ============================================================
if frame_count > 0:
    rdf_data /= frame_count                 # Divide by total frame count to get averages
    print(f"RDF data successfully averaged over {frame_count} frames.")
else:
    raise ValueError("No valid frames found in the file.")

# ============================================================
# 4. Save Averaged RDF Data
# ============================================================
np.savetxt(output_file, rdf_data, header="r g(1-1) g(1-2) g(1-3) g(2-2) g(2-3) g(3-3)", comments='')
print(f"Averaged RDF data saved to {output_file}")

# ============================================================
# 5. Set Matplotlib Parameters
# ============================================================
plt.rcParams.update({
    'font.family':       'Times New Roman',
    'font.weight':       'bold',
    'axes.labelweight':  'bold',
    'axes.linewidth':    2,
    'axes.titlesize':    15,
    'axes.labelsize':    15,
    'legend.fontsize':   16,
    'xtick.labelsize':   16,
    'ytick.labelsize':   16
})

# ============================================================
# 6. Plot RDF Graph
# ============================================================

# Define RDF types to plot
labels_to_plot  = ['F-F', 'F-Be', 'F-Li']
all_labels      = ['F-F', 'F-Be', 'F-Li', 'Be-Be', 'Li-Be', 'Li-Li']
colors          = ['red', 'green', 'blue', 'purple', 'orange', 'cyan']

plt.figure(figsize=(8, 6))
for i, (label, color) in enumerate(zip(all_labels, colors)):
    if label in labels_to_plot:
        plt.plot(
            rdf_data[:, 0], rdf_data[:, i + 1],
            label=label, color=color, linewidth=2.5,
            marker='*', markersize=10,
            markevery=max(1, len(rdf_data) // 35)
        )

plt.ylim(0, 11)
plt.xlim(0, 6)
plt.xlabel("r (Å)")
plt.ylabel("g(r)")
plt.legend()
plt.tight_layout()

# ============================================================
# 7. Save and Show Plot
# ============================================================
plt.savefig("rdf-atten.png", dpi=1200, bbox_inches='tight')
plt.show()
# ============================================================