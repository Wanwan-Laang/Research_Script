import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# ========================
# 1. User Configuration
# ========================
step_ranges = [
    (5000, 8000),
    (22000, 25000),
    (70000, 72500),
]

rdf_file              = "rdf_out.txt"
nbins                 = 100
expected_column_count = 14
g_indices             = [2, 4, 6, 8, 10, 12]
rdf_labels            = ['F-F', 'F-Be', 'F-Li', 'Be-Be', 'Li-Be', 'Li-Li']
plot_labels           = ['F-F', 'F-Be', 'Li-Li']
colors                = ['red', 'green', 'blue', 'purple', 'orange', 'cyan']
line_styles           = ['-', '--', ':', '-.']
alphas                = np.linspace(1.0, 0.5, len(step_ranges))

# ========================
# 2. Read RDF Blocks
# ========================
with open(rdf_file, "r") as f:
    lines = f.readlines()[3:]  # Skip LAMMPS header

all_blocks = []
current_block = []
current_step = None

for line in lines:
    parts = line.strip().split()
    if len(parts) == 2:
        if current_block and current_step is not None:
            all_blocks.append((current_step, np.array(current_block, dtype=float)))
        current_step = int(parts[0])
        current_block = []
    elif len(parts) == expected_column_count:
        current_block.append(parts)

if current_block and current_step is not None:
    all_blocks.append((current_step, np.array(current_block, dtype=float)))

# ========================
# 3. Plot Setup
# ========================
plt.rcParams.update({
    'font.family': 'Times New Roman',
    'font.weight': 'bold',
    'axes.labelweight': 'bold',
    'axes.linewidth': 2,
    'axes.titlesize': 15,
    'axes.labelsize': 15,
    'legend.fontsize': 15,
    'xtick.labelsize': 13,
    'ytick.labelsize': 13
})
plt.tick_params(axis='both', direction='in')

# Used to only add label for each atom pair once
labeled_pairs = set()

# Peak data
peak_data = []

# ========================
# 4. Loop Over Ranges
# ========================
for idx, (step_start, step_end) in enumerate(step_ranges):
    blocks = [
        data for step, data in all_blocks
        if step_start <= step <= step_end
    ]

    if not blocks:
        print(f"[!] No RDF data found in step range {step_start}–{step_end}")
        continue

    rdf_array = np.stack(blocks)
    avg_rdf = np.mean(rdf_array[:, :, g_indices], axis=0)
    r_vals = rdf_array[0, :, 1].reshape(-1, 1)
    final_rdf = np.hstack([r_vals, avg_rdf])

    output_file = f"averaged_rdf_{step_start}_{step_end}.txt"
    np.savetxt(output_file, final_rdf,
               header="r g(F-F) g(F-Be) g(F-Li) g(Be-Be) g(Li-Be) g(Li-Li)",
               fmt="%.6f", comments='')
    print(f"[✓] Saved: {output_file:<35} Frames Averaged: {len(blocks):<4}")

    # Plot each atom pair
    for i, (label, color) in enumerate(zip(rdf_labels, colors)):
        if label not in plot_labels:
            continue

        r = final_rdf[:, 0]
        g = final_rdf[:, i + 1] / 1.875

        # Detect first peak after r > 0.5
        valid_indices = np.where(r > 0.5)[0]
        peak_idx = valid_indices[np.argmax(g[valid_indices])]
        r_peak, g_peak = r[peak_idx], g[peak_idx]

        peak_data.append({
            'Range': f"{step_start}-{step_end}",
            'Pair': label,
            'r_peak': round(r_peak, 4),
            'g_peak': round(g_peak, 4)
        })

        # Only label the atom pair once in legend
        legend_label = label if label not in labeled_pairs else None
        labeled_pairs.add(label)

        plt.plot(r, g,
                 label=legend_label,
                 color=color,
                 linestyle=line_styles[idx % len(line_styles)],
                 alpha=alphas[idx],
                 linewidth=2.5,
                 #marker='o',
                 markersize=4,
                 markevery=max(1, len(r) // 25))

# ========================
# 5. Finalize Plot
# ========================
plt.xlim(0, 6)
plt.ylim(0, 11)
plt.xlabel("r (Å)")
plt.ylabel("g(r)")
plt.legend()
plt.tight_layout()
plt.savefig("figure-rdf_overlay_clean.pdf", dpi=1200, transparent=True)
plt.show()

# ========================
# 6. Peak Summary Output
# ========================
df_peak = pd.DataFrame(peak_data)
df_peak = df_peak[['Range', 'Pair', 'r_peak', 'g_peak']]
df_peak.to_csv("rdf_peaks.csv", index=False)
print("\n[✓] Peak summary saved to: rdf_peaks.csv")

# Console pretty table
print("\n┌──────────────┬────────┬──────────┬──────────┐")
print("│ Step Range   │ Pair   │ r_peak   │ g_peak   │")
print("├──────────────┼────────┼──────────┼──────────┤")
for row in df_peak.itertuples(index=False):
    print(f"│ {row.Range:<12} │ {row.Pair:<6} │ {row.r_peak:<8.4f} │ {row.g_peak:<8.4f} │")
print("└──────────────┴────────┴──────────┴──────────┘")

# ========================
# 7. Print Range → Style Mapping
# ========================
print("\n[Legend Range Info] (linestyle + alpha):")
for idx, (step_start, step_end) in enumerate(step_ranges):
    ls = line_styles[idx % len(line_styles)]
    alpha = alphas[idx]
    print(f"  range {step_start}-{step_end:<9} → linestyle='{ls}', alpha={alpha:.2f}")