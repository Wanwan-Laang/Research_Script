import numpy as np
import matplotlib.pyplot as plt

# 假設你有 numpy array
# energies_dft = np.array([...])
# energies_dp = np.array([...])

# 1. 計算每一點的絕對誤差，轉為 meV/atom
errors = np.abs(energies_dp - energies_dft) * 1000  # 1 eV = 1000 meV

# 2. 畫 error distribution histogram
plt.figure(figsize=(3, 2))  # 小圖尺寸
plt.hist(errors, bins=np.arange(0, 11, 1), color='orange', edgecolor='black')

plt.xlabel("Error (meV/atom)")
plt.ylabel("Distribution (%)")

# Optional: 改為百分比 y 軸
counts, _ = np.histogram(errors, bins=np.arange(0, 11, 1))
percent = counts / len(errors) * 100
plt.clf()  # 清空畫面
plt.bar(np.arange(0.5, 10.5, 1), percent, width=1.0, color='orange', edgecolor='black')
plt.xlabel("Error (meV/atom)")
plt.ylabel("Distribution (%)")
plt.xticks(np.arange(0, 11, 2))

plt.tight_layout()
plt.savefig("energy_error_histogram.png", dpi=600)
plt.show()
