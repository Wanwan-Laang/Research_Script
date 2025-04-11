import numpy as np
import matplotlib.pyplot as plt
import glob
import re

# **排序函數，確保數據文件順序正確**
def natural_sort_key(text):
    return [int(num) if num.isdigit() else num for num in re.split(r'(\d+)', text)]

# **獲取所有數據文件並排序**
file_list = sorted(glob.glob("flibe_equil_*.txt"), key=natural_sort_key)

simTime, temp, c_ex, c_in, c_PKAin, potEng, totEng = [], [], [], [], [], [], []
change_points = []
time_offset = 0  # 累積時間偏移

# **讀取數據文件**
for idx, file in enumerate(file_list):
    data = np.loadtxt(file, skiprows=1)
    
    # **計算時間偏移，使時間連續**
    if idx > 0:
        time_offset += simTime[-1]
        change_points.append(time_offset)  # 記錄條件變化點
    
    simTime.extend(data[:, 0] + time_offset)
    temp.extend(data[:, 4])
    c_ex.extend(data[:, 5])
    c_in.extend(data[:, 6])
    c_PKAin.extend(data[:, 7])
    potEng.extend(data[:, 8])
    totEng.extend(data[:, 9])

# **轉換為 NumPy 陣列**
simTime, temp, c_ex, c_in, c_PKAin, potEng, totEng = map(np.array, [simTime, temp, c_ex, c_in, c_PKAin, potEng, totEng])

# **設置 x 軸範圍**
x_min, x_max = simTime[0], simTime[-1]

# **設置 Matplotlib 參數**
plt.rcParams.update({
    'font.weight': 'bold', 'axes.labelweight': 'bold', 'axes.linewidth': 2,
    'axes.titlesize': 12, 'axes.labelsize': 12, 'legend.fontsize': 13,
    'xtick.labelsize': 13, 'ytick.labelsize': 13
})

# **統一 `tick` 樣式**
tick_params = {'direction': 'in', 'width': 2, 'length': 6}

# **繪製溫度變化圖**
plt.figure(figsize=(8, 6))
plt.plot(simTime, temp, label="System Temp", color="red", linewidth=2)
plt.plot(simTime, c_ex, label="External Temp", color="blue", linestyle="--")
plt.plot(simTime, c_in, label="Internal Temp", color="green", linestyle="-.")
plt.plot(simTime, c_PKAin, label="PKA Internal Temp", color="purple", linestyle=":")

# **標記條件變化點**
for i, cp in enumerate(change_points):
    plt.axvline(x=cp, color="gray", linestyle="--", linewidth=2, label="Condition Change" if i == 0 else "")

plt.xlim(x_min, x_max)
plt.xlabel("Simulation Time (ps)")
plt.ylabel("Temperature (K)")
plt.legend()
plt.tick_params(**tick_params)  # ✅ 確保 tick 樣式應用
plt.tight_layout()
plt.savefig("flibe_equil_temperature_combined.png", dpi=1200)

# **繪製能量變化圖**
plt.figure(figsize=(8, 6))
plt.plot(simTime, potEng, label="Potential Energy", color="brown", linewidth=2)
plt.plot(simTime, totEng, label="Total Energy", color="black", linestyle="--")

# **標記條件變化點**
for i, cp in enumerate(change_points):
    plt.axvline(x=cp, color="gray", linestyle="--", linewidth=2, label="Condition Change" if i == 0 else "")

plt.xlim(x_min, x_max)
plt.xlabel("Simulation Time (ps)")
plt.ylabel("Energy (eV)")
plt.legend()
plt.tick_params(**tick_params)  # ✅ 確保 tick 樣式應用
plt.tight_layout()
plt.savefig("flibe_equil_energy_combined.png", dpi=1200)

