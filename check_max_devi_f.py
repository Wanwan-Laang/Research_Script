import os
import numpy as np
import matplotlib.pyplot as plt
import glob
from pathlib import Path

iterations = [8, 9]  # surface
# iterations = [0, 2, 4, 6]

plt.figure(figsize=(8, 6))  # 設定圖表大小
colors = ['blue', 'red', 'green', 'purple', 'orange']  
linestyles = ['-', '--', '-.', ':'] 

for idx, i in enumerate(iterations):
    max_devi_f_values = []
    directory_pattern = f"./iter.{i:06d}/01.model_devi/task.*"
    task_directories = glob.glob(directory_pattern)

    for task_directory in task_directories:
        file_path = Path(task_directory) / "model_devi.out"
        if file_path.exists():
            try:
                data = np.genfromtxt(file_path, skip_header=1, usecols=4)
                if data.size > 0:
                    max_devi_f_values.append(data)
            except Exception as e:
                print(f"Warning: Unable to read {file_path}. Error: {e}")

    if max_devi_f_values:
        max_devi_f_values = np.concatenate(max_devi_f_values)
    else:
        print(f"Warning: No valid data found for iter {i}")
        continue  # 跳過這次迭代

    hist, bin_edges = np.histogram(max_devi_f_values, range=(0, 0.25), bins=100)
    hist = hist / len(max_devi_f_values) * 100  

    # 設定繪圖參數
    plt.rcParams.update({
        'font.weight': 'bold',
        'axes.labelweight': 'bold',
        'axes.linewidth': 2,
        'axes.titlesize': 15,
        'axes.labelsize': 15,
        'legend.fontsize': 16,
        'xtick.labelsize': 16,
        'ytick.labelsize': 16
    })

    plt.tick_params(axis='both', direction='in')
    plt.plot(bin_edges[:-1], hist, label=f'iter {i:02d}', lw=3,
             color=colors[idx % len(colors)], linestyle=linestyles[idx % len(linestyles)])

    # 加入參考線
    plt.axvline(x=0.05, color='grey', linestyle='--', alpha=0.7, lw=1.5)
    plt.axvline(x=0.10, color='grey', linestyle='-.', alpha=0.7, lw=1.5)
    plt.axvline(x=0.15, color='grey', linestyle='--', alpha=0.7, lw=1.5)

    plt.xlim((min(bin_edges), max(bin_edges)))
    plt.ylim(0, max(hist) * 1.2)  # 讓 y 軸適應數據範圍
    plt.grid(True, linestyle=":", alpha=0.5)  
    plt.legend()
    plt.xlabel("max_devi_f (eV/Å)")
    plt.ylabel("Distribution (%)")

    output_file = f'./iter{i:02d}_dist-max-devi-f.csv'
    np.savetxt(output_file, np.column_stack((bin_edges[:-1], hist)), delimiter=",",
               header="bin_edges,hist", fmt="%.6f")
    print(f"Saved distribution data to {output_file}")

plt.savefig('./max-devi-f.png', dpi=1200, bbox_inches='tight')
