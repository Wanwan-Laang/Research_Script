import pandas as pd
import matplotlib.pyplot as plt

plt.rcParams.update({
    #'font.family': 'Times New Roman',
    'font.weight': 'bold',
    'axes.labelweight': 'bold',
    'axes.linewidth': 2,
    'axes.titlesize': 15,
    'axes.labelsize': 15,
    'legend.fontsize': 15,
    'xtick.labelsize': 13,
    'ytick.labelsize': 13
})

# 各吸附位置的數據
bridge_data = [1.88, 1.51, 1.15, 1.19, 1.60, 1.06, 1.73, 1.52, 1.09, 1.65, 1.34, 1.88, 1.66, 1.09, 1.66, 1.65, 1.51, 1.09, 1.51, 1.19, 1.78, 1.63, 1.06, 1.86, 1.34, 2.04, 1.66, 1.53, 1.21, 1.06, 1.60, 1.83, 1.73, 1.66, 1.34, 1.21, 1.21, 1.66, 1.34, 1.34, 1.34, 1.73, 1.73, 1.16, 1.21, 1.06, 1.06, 1.09, 1.34, 1.19, 1.21, 1.69, 1.70, 1.60, 1.66, 1.10, 1.78, 1.86, 1.10, 1.10, 1.06, 1.83, 1.61, 1.65, 1.60, 1.58, 1.60, 1.73, 1.89, 1.34, 1.95, 1.53, 1.21, 1.95, 1.96, 1.90, 1.53, 1.86, 1.78, 1.51]

hollow_data = [1.088, 1.509, 1.415, 1.703, 1.509, 1.531, 1.693, 1.765, 1.207, 1.890, 1.282, 1.101, 1.859, 1.662, 1.088, 2.030, 1.064, 0.940, 1.137, 1.702, 1.877, 1.706, 1.690, 1.207]

ontop_data =  [1.09, 1.34, 1.61, 1.06, 1.10, 1.66, 1.66, 1.06, 1.09, 1.89, 1.15, 1.75, 1.60, 1.21, 1.66, 1.51, 1.10, 5.92, 1.10, 1.10, 1.86, 1.15, 1.77, 1.07, 1.71, 1.90, 1.73, 1.19, 1.60, 1.35, 1.75, 1.21, 1.87, 1.09, 1.51, 1.10, 1.78, 1.66, 1.61, 1.83]

bridge_index = list(range(1, len(bridge_data) + 1))
hollow_index = list(range(1, len(hollow_data) + 1))
ontop_index  = list(range(1, len(ontop_data) + 1))

# 合併所有數據
adsorption = bridge_data + hollow_data + ontop_data
site_labels = ['bridge'] * len(bridge_data) + ['hollow'] * len(hollow_data) + ['ontop'] * len(ontop_data)
site_local_idx = bridge_index + hollow_index + ontop_index

# 建立主 DataFrame
df = pd.DataFrame({
    "POSCAR_Index": site_local_idx,
    "Eadsorption": adsorption,
    "Site": site_labels
})

# 以 Eadsorption 升序排序，添加 MergedIndex
df_sorted = df.sort_values(by="Eadsorption", ascending=True).reset_index(drop=True)
df_sorted.insert(0, "MergedIndex", df_sorted.index + 1)


plt.figure()
colors = {'bridge': 'green', 'hollow': 'purple', 'ontop': 'blue'}
for site in df_sorted['Site'].unique():
    subset = df_sorted[df_sorted['Site'] == site]
    plt.scatter(subset['MergedIndex'], subset['Eadsorption'], label=site, color=colors[site], marker='o', s=100)

zrc_energy = 0.65733667
plt.axhline(y=zrc_energy, color='red', linestyle='--', linewidth=2, label=f'ZrC: {zrc_energy:.3f}')

plt.xlabel("Merged Index (Global Ranking)")
plt.ylabel("Eadsorption")
plt.title("High Entropy Carbide Adsorption Energy (Sorted)")
plt.legend()
plt.tight_layout()
plt.tick_params(axis='both', direction='in')
plt.savefig("adsorption_energy.pdf", dpi=900, bbox_inches='tight', transparent=True)

# === 儲存總表 ===
df_sorted.to_csv("adsorption_data_full.csv", index=False)

# === 各 site group 個別排序與導出 ===
for site in ['bridge', 'hollow', 'ontop']:
    df_site = df_sorted[df_sorted['Site'] == site].copy()
    # 仍用全域排序的 MergedIndex，不重新編號
    df_site.to_csv(f"adsorption_sorted_{site}.csv", index=False)

print("✅ 圖形已輸出 adsorption_energy.pdf，數據已輸出 adsorption_data_full.csv, adsorption_sorted_bridge.csv, adsorption_sorted_hollow.csv, adsorption_sorted_ontop.csv")

# === Summary Log 輸出 ===
with open("adsorption_summary.log", "w") as f:
    total_count = len(df_sorted)
    f.write(f"📦 Total number of adsorption configurations: {total_count}\n\n")

    # 每種 site 構型數
    site_counts = df_sorted['Site'].value_counts().reindex(['bridge', 'hollow', 'ontop'])
    f.write("🔹 Number of configurations by site type:\n")
    for site, count in site_counts.items():
        f.write(f"  {site:>6}: {count} configurations\n")
    
    # 全體最穩定構型
    min_row = df_sorted.iloc[0]
    f.write("\n💎 Most stable adsorption configuration (all sites):\n")
    f.write(f"  MergedIndex: {min_row['MergedIndex']}\n")
    f.write(f"  POSCAR_Index: {min_row['POSCAR_Index']}\n")
    f.write(f"  Site: {min_row['Site']}\n")
    f.write(f"  Adsorption energy: {min_row['Eadsorption']:.3f} eV\n")

    # 各 site 類型的最穩定構型
    f.write("\n📉 Lowest adsorption energy for each site type:\n")
    for site in ['bridge', 'hollow', 'ontop']:
        min_site = df_sorted[df_sorted['Site'] == site].iloc[0]
        merged_idx = int(min_site['MergedIndex'])
        poscar_idx = int(min_site['POSCAR_Index'])
        eads = float(min_site['Eadsorption'])
        f.write(f"  {site:>6}: Merged #{merged_idx:>2}, POSCAR #{poscar_idx:>2}, Energy = {eads:.3f} eV\n")

    # 各 site 類型的平均值和標準差
    f.write("\n📊 Adsorption energy statistics by site type:\n")
    for site in ['bridge', 'hollow', 'ontop']:
        mean_val = df_sorted[df_sorted['Site'] == site]['Eadsorption'].mean()
        std_val  = df_sorted[df_sorted['Site'] == site]['Eadsorption'].std()
        f.write(f"  {site:>6}: Mean = {mean_val:.3f} eV, Std. Dev. = {std_val:.3f} eV\n")

print("✅ 統計摘要已儲存為 'adsorption_summary.log'")