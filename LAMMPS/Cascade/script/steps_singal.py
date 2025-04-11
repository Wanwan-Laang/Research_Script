import numpy as np
import matplotlib.pyplot as plt

# 讀取數據
data_file = "flibe_equil_2.txt"  # 替換成你的數據文件名稱
data = np.loadtxt(data_file, skiprows=1)  # 跳過標題行

# 提取數據列
simTime = data[:, 0]  # 模擬時間
temp = data[:, 4]      # 系統溫度
c_ex = data[:, 5]      # 外部溫度
c_in = data[:, 6]      # 內部溫度
c_PKAin = data[:, 7]   # PKA 內部溫度
potEng = data[:, 8]    # 勢能
totEng = data[:, 9]    # 總能量

# 繪製溫度變化圖
plt.figure(figsize=(8, 6))
plt.plot(simTime, temp, label="Temp (System)", color="red", linewidth=2)
plt.plot(simTime, c_ex, label="c_ex (External)", color="blue", linestyle="--")
plt.plot(simTime, c_in, label="c_in (Internal)", color="green", linestyle="-.")
plt.plot(simTime, c_PKAin, label="c_PKAin (PKA Internal)", color="purple", linestyle=":")
plt.xlabel("Simulation Time (ps)")
plt.ylabel("Temperature (K)")
plt.title("FLiBe Equilibration: Temperature vs Time")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("flibe_equil_temperature_2.png", dpi=1200)

# 繪製能量變化圖
plt.figure(figsize=(8, 6))
plt.plot(simTime, potEng, label="Potential Energy", color="brown", linewidth=2)
plt.plot(simTime, totEng, label="Total Energy", color="black", linestyle="--")
plt.xlabel("Simulation Time (ps)")
plt.ylabel("Energy (eV)")
plt.title("FLiBe Equilibration: Energy vs Time")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("flibe_equil_energy_2.png", dpi=1200)

