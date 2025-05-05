import pandas as pd
import matplotlib.pyplot as plt
plt.rcParams.update({
    'font.weight': '400',
    'axes.labelweight': '400',
    'axes.linewidth': 2,
    'axes.titlesize': 12,
    'axes.labelsize': 12,
    'legend.fontsize': 13,
    'xtick.labelsize': 13,
    'ytick.labelsize': 13
})
tick_params = {'direction': 'in', 'width': 2, 'length': 6}

df = pd.read_csv("cluster_stable_F2_100.csv")

end_frame_counts = df["end_frame"].value_counts().sort_index()

plt.figure(figsize=(4,3))
plt.scatter(end_frame_counts.index, end_frame_counts.values, alpha=0.9, color="blue", edgecolors="black", s=80)
plt.xlabel("Frame")
plt.ylabel("Molecules Number")
plt.title("Stable F2 Molecules Number")
#plt.xticks(rotation=45)
plt.tight_layout()
#plt.legend()
plt.tick_params(**tick_params)
plt.savefig("fig_stable_F2_molecules_number_100.pdf", dpi=900,transparent=True, bbox_inches='tight')

output_df = pd.DataFrame({"end_frame": end_frame_counts.index, "count": end_frame_counts.values})
output_df.to_csv("collect_end_frame_counts_100.csv", index=False)

# Print each end_frame and its corresponding count
#for end_frame, count in end_frame_counts.items():
#    print(end_frame, count)

