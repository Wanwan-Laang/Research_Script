import numpy as np
import matplotlib.pyplot as plt
plt.rcParams.update({
    'font.weight': 'bold',
    'axes.labelweight': 'bold',
    'axes.linewidth': 2,
    'axes.titlesize': 12,
    'axes.labelsize': 12,
    'legend.fontsize': 13,
    'xtick.labelsize': 13,
    'ytick.labelsize': 13
})
tick_params = {'direction': 'in', 'width': 2, 'length': 6}

# 讀取數據
data_file = "log-3.txt"  # 替換成你的數據文件名稱
data = np.loadtxt(data_file, skiprows=1)  # 跳過標題行

# 提取數據列
simTime = data[:, 0]  # 模擬時間
temp = data[:, 4]      # 系統溫度
c_ex = data[:, 5]      # 外部溫度
c_in = data[:, 6]      # 內部溫度
c_PKAin = data[:, 7]   # PKA 內部溫度
potEng = data[:, 8]    # 勢能
totEng = data[:, 9]    # 總能量

x_min, x_max = simTime[0], simTime[-1]

# 繪製溫度變化圖
plt.figure(figsize=(6,4))
plt.plot(simTime, temp, label='System   Temp',   color="red",   linewidth=2.0)
#plt.plot(simTime, c_ex, label='External Temp', color="blue",  linewidth=2.0)
plt.plot(simTime, c_in, label='Internal Temp', color="green", linewidth=2.0)
#plt.plot(simTime, c_PKAin, label="PKA Temp", color="purple", linestyle=":")
plt.xlabel("Simulation Time (ps)")
plt.ylabel("Temperature (K)")
#plt.title("FLiBe Equilibration: Temperature vs Time")
plt.legend()
plt.xlim(x_min, x_max)  # 設置 x 軸範圍

#plt.ylim(968, 1020)
plt.tight_layout()
plt.savefig("fig_signal_stage.pdf",dpi=1200,transparent=True)
#plt.show()
# 繪製能量變化圖
##plt.figure(figsize=(8, 6))
##plt.plot(simTime, potEng, label="Potential Energy", color="brown", linewidth=2)
##plt.plot(simTime, totEng, label="Total Energy", color="black", linestyle="--")
##plt.xlabel("Simulation Time (ps)")
##plt.ylabel("Energy (eV)")
##plt.title("FLiBe Equilibration: Energy vs Time")
##plt.legend()
##plt.grid(True)
##plt.tight_layout()
##plt.savefig("flibe_equil_energy_2.png", dpi=1200)


