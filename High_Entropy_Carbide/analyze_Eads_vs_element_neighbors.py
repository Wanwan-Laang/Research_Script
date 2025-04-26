"""
Plot adsorption energy vs. the number of neighboring target atoms.

This script reads a CSV file containing adsorption energies (Eads) and 
the number of neighboring atoms (e.g., Nb, Ti, Ta, Hf, Zr) around an adsorbed C atom. 
It generates a scatter plot with optional jitter for better visualization,
grouped by adsorption site types (bridge, hollow, ontop).

Author: [Your Name]
Date: [Today's Date]
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# === User Settings ===
target_element = "Ta"  # <<< Set the element to analyze, e.g., Nb, Ti, Ta, Hf, Zr
file_path = "C_env_cdist_withEadsortion.csv"  # <<< Path to input CSV file

# === Load and prepare data ===
df = pd.read_csv(file_path)
df.columns = df.columns.str.strip()  # Clean column names

required_columns = [target_element, "Eads", "Group"]
for col in required_columns:
    if col not in df.columns:
        raise ValueError(f"Missing required column: {col}")

# === Plotting style settings ===
plt.rcParams.update({
    "axes.labelweight": "bold",
    "axes.linewidth":   2,
    "axes.titlesize":   15,
    "axes.labelsize":   15,
    "legend.fontsize":  15,
    "xtick.labelsize":  13,
    "ytick.labelsize":  13,
})

# === Group color mapping ===
group_color_map = {
    "bridge": "tab:blue",
    "hollow": "tab:green",
    "ontop": "tab:red"
}

# === Create scatter plot ===
plt.figure(figsize=(8, 6))

for group, color in group_color_map.items():
    sub_df = df[df["Group"] == group]
    if sub_df.empty:
        continue
    jitter = np.random.uniform(-0.1, 0.1, size=len(sub_df))
    plt.scatter(
        sub_df["Eads"].to_numpy(),
        (sub_df[target_element] + jitter).to_numpy(),
        label=group, color=color, s=80, edgecolors='k'
    )

plt.xlabel("Adsorption Energy $E_{ads}$ (eV)")
plt.ylabel(f"Number of {target_element} atoms")
plt.title(f"Number of {target_element} neighbors vs $E_{{ads}}$")
plt.legend(title="Site Type")
plt.grid(True)
plt.tight_layout()
plt.show()
plt.close()

# === Save output CSV ===
output_df = df[["Eads", target_element, "Group"]]
output_df.to_csv(f"Eads_vs_{target_element}_output.csv", index=False)

print(f"✅ Saved: Eads_vs_{target_element}_output.csv")
