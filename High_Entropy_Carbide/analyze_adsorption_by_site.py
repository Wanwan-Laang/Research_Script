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

# 建立總資料與標籤
configurations = list(range(1, len(bridge_data) + len(hollow_data) + len(ontop_data) + 1))
adsorption = bridge_data + hollow_data + ontop_data
sites = (
    ['bridge'] * len(bridge_data) +
    ['hollow'] * len(hollow_data) +
    ['ontop'] * len(ontop_data)
)

# 建立 DataFrame
df = pd.DataFrame({
    "Configuration": configurations,
    "Eadsorption": adsorption,
    "Site": sites
})

# 繪圖
plt.figure()
colors = {'bridge': 'green', 'hollow': 'purple', 'ontop': 'blue'}

for site in df['Site'].unique():
    subset = df[df['Site'] == site]
    plt.scatter(subset['Configuration'], subset['Eadsorption'], label=site, color=colors[site],marker='o', s=60, edgecolors='k')
 # 圓形標記，可以改成 's', '^', 'D', '*', 'x' 等等

# 加入 ZrC 能量基準線
#zrc_energy = 0.67183667
zrc_energy = 0.65733667
plt.axhline(y=zrc_energy, color='red', linestyle='--', linewidth=2, label=f'ZrC: {zrc_energy:.3f}')

# 標籤與圖例
plt.xlabel("Configuration")
plt.ylabel("Eadsorption")
plt.title("High Entropy Carbide Adsorption Energy")
plt.legend()
plt.tight_layout()
plt.tick_params(axis='both', direction='in')
plt.savefig("fig-overview-adsorption_energy.pdf", dpi=900, bbox_inches='tight', transparent=True)

###############################################################

# 定義原始（各自類型內部）POSCAR 編號
bridge_index = list(range(1, len(bridge_data) + 1))     # 1–80
hollow_index = list(range(1, len(hollow_data) + 1))     # 1–24
ontop_index  = list(range(1, len(ontop_data) + 1))      # 1–40

# 建立主 DataFrame（包含合併後編號與各自原始編號）
df = pd.DataFrame({
    "Configuration": list(range(1, len(bridge_data + hollow_data + ontop_data) + 1)),
    "SiteLocalIndex": bridge_index + hollow_index + ontop_index,
    "Eadsorption": bridge_data + hollow_data + ontop_data,
    "Site": ['bridge'] * len(bridge_data) + ['hollow'] * len(hollow_data) + ['ontop'] * len(ontop_data)
})

# 🔁 排序資料（按能量從小到大）
df = df.sort_values(by=["Eadsorption", "Site", "SiteLocalIndex"], ascending=[True, True, True]).reset_index(drop=True)
df["Configuration"] = range(1, len(df) + 1)  # 重新編號 Configuration（圖上用）

# 📦 Summary: Total number of configurations and count per site type
total_count = len(df)
print(f"📦 Total number of adsorption configurations: {total_count}")

# display order of site types
site_counts = df['Site'].value_counts().reindex(['bridge', 'hollow', 'ontop'])
print("🔹 Number of configurations by site type:")
for site, count in site_counts.items():
    print(f"  {site:>6}: {count} configurations")


# 💎 Identify the most stable configuration (lowest adsorption energy)
min_row = df.loc[df['Eadsorption'].idxmin()]
print("\n💎 Most stable adsorption configuration:")
print(f"  Configuration index: {min_row['Configuration']}")
print(f"  Site type: {min_row['Site']}")
print(f"  Adsorption energy: {min_row['Eadsorption']:.3f} eV")


print("\n📉 Lowest adsorption energy for each site type:")
for site in df['Site'].unique():
    min_site = df[df['Site'] == site].nsmallest(1, 'Eadsorption')
    merged_idx = int(min_site['Configuration'].values[0])
    local_idx = int(min_site['SiteLocalIndex'].values[0])
    eads = float(min_site['Eadsorption'].values[0])
    print(f"  {site:>6}: Merged #{merged_idx:>2}, POSCAR #{local_idx:>2}, Energy = {eads:.3f} eV")

# 📊 Average and standard deviation of adsorption energies
print("\n📊 Adsorption energy statistics by site type:")
for site in df['Site'].unique():
    mean_val = df[df['Site'] == site]['Eadsorption'].mean()
    std_val = df[df['Site'] == site]['Eadsorption'].std()
    print(f"  {site:>6}: Mean = {mean_val:.3f} eV, Std. Dev. = {std_val:.3f} eV")

# === 儲存所有資料為 CSV ===
df.to_csv("adsorption_data_full.csv", index=False)
print("✅ 所有構型資料已儲存為 'adsorption_data_full.csv'")

# === 輸出統計摘要到 log ===
with open("adsorption_summary.log", "w") as f:
    f.write(f"📦 Total number of adsorption configurations: {total_count}\n\n")
    
    f.write("🔹 Number of configurations by site type:\n")
    for site, count in site_counts.items():
        f.write(f"  {site:>6}: {count} configurations\n")

    f.write("\n💎 Most stable adsorption configuration:\n")
    f.write(f"  Configuration index: {min_row['Configuration']}\n")
    f.write(f"  Site type: {min_row['Site']}\n")
    f.write(f"  Adsorption energy: {min_row['Eadsorption']:.3f} eV\n")

    f.write("\n📉 Lowest adsorption energy for each site type:\n")
    for site in df['Site'].unique():
        min_site = df[df['Site'] == site].nsmallest(1, 'Eadsorption')
        merged_idx = int(min_site['Configuration'].values[0])
        local_idx = int(min_site['SiteLocalIndex'].values[0])
        eads = float(min_site['Eadsorption'].values[0])
        f.write(f"  {site:>6}: Merged #{merged_idx:>2}, POSCAR #{local_idx:>2}, Energy = {eads:.3f} eV\n")

    f.write("\n📊 Adsorption energy statistics by site type:\n")
    for site in df['Site'].unique():
        mean_val = df[df['Site'] == site]['Eadsorption'].mean()
        std_val = df[df['Site'] == site]['Eadsorption'].std()
        f.write(f"  {site:>6}: Mean = {mean_val:.3f} eV, Std. Dev. = {std_val:.3f} eV\n")

print("✅ 統計摘要已儲存為 'adsorption_summary.log'")    

# === 額外輸出：各 site 類型分開排序後的 CSV ===
site_types = ["bridge", "hollow", "ontop"]

for site in site_types:
    df_site = df[df["Site"] == site].copy()
    df_site = df_site.sort_values(by=["Eadsorption", "SiteLocalIndex"], ascending=[True, True])

    output_name = f"adsorption_sorted_{site}.csv"
    df_site.to_csv(output_name, index=False)
    print(f"✅ 已儲存：{output_name}（按 Eadsorption 排序）")