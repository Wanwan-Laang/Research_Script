import pandas as pd
import matplotlib.pyplot as plt

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

# 各吸附位置的數據
bridge_data = [
    1.982, -0.352, 0.884, 1.932, 1.5, 1.243, -0.353, 2.196, 1.93, 1.378, -0.353, 4.945, 0.837, 1.483, 0.442, 1.929,
    1.235, 0.882, 0.881, -0.682, 1.481, 1.428, 0.893, None, -0.493, 2.328, 0.439, 0.438, 1.375, 1.931, 1.705, None, None, 5.087, 1.501, None,
    4.334, 2.041, 0.892, 1.247, 1.176, -0.355, 1.429, 1.01, 0.884, 1.505, 2.327, 1.482, 0.882, -0.493, 1.931, 1.01,
    1.671, 1.958, 0.436, 1.964, 0.439, 1.376, -0.355, 1.014, 0.884, 1.225
]

hollow_data = [
    1.015, 1.010, 0.881, 1.245, 1.503, 2.102, -0.355, 1.505, 0.823, -0.351
]

ontop_data = [
    1.24, 0.44, -0.69, -0.69, 1.51, 1.23, -0.35, 0.43, 3.27, 1.23,
    -0.35, 1.49, 1.25, -0.68, 0.89, 1.23, 0.84, 1.38, 1.93, 0.88
]

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
    plt.scatter(subset['Configuration'], subset['Eadsorption'], label=site, color=colors[site],marker='o', s=100)
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
plt.savefig("adsorption_energy.pdf", dpi=900, bbox_inches='tight', transparent=True)

###############################################################

# 定義原始（各自類型內部）POSCAR 編號
bridge_index = list(range(1, len(bridge_data) + 1))     # 1–58
hollow_index = list(range(1, len(hollow_data) + 1))     # 1–10
ontop_index  = list(range(1, len(ontop_data) + 1))      # 1–20

# 建立主 DataFrame（包含合併後編號與各自原始編號）
df = pd.DataFrame({
    "Configuration": list(range(1, len(bridge_data + hollow_data + ontop_data) + 1)),
    "SiteLocalIndex": bridge_index + hollow_index + ontop_index,
    "Eadsorption": bridge_data + hollow_data + ontop_data,
    "Site": ['bridge'] * len(bridge_data) + ['hollow'] * len(hollow_data) + ['ontop'] * len(ontop_data)
})

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