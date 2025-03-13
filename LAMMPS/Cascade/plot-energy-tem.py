import numpy as np
import matplotlib.pyplot as plt
import glob
import os
import re

plt.style.use("seaborn-v0_8-paper")
plt.rcParams.update({
    'font.weight': 'bold', 'axes.labelweight': 'bold', 'axes.linewidth': 2,
    'axes.titlesize': 14, 'axes.labelsize': 14, 'legend.fontsize': 14,
    'xtick.labelsize': 12, 'ytick.labelsize': 12
})
tick_params = {'direction': 'in', 'width': 2, 'length': 6, 'top': True, 'right': True}

def sort_key(filename):
    match = re.search(r'\d+', filename)
    return int(match.group()) if match else 0

data_files = sorted(glob.glob("stage_0*"), key=sort_key)

# 遍历文件并绘制图表
for data_file in data_files:
    try:
        data = np.loadtxt(data_file, skiprows=1)  # 跳过标题行

        if data.shape[0] == 0:
            print(f"警告：{data_file} 为空，跳过处理。")
            continue

        # 提取数据列
        simTime = data[:, 0]   
        temp = data[:, 4]      
        c_ex = data[:, 5]      
        c_in = data[:, 6]      
        c_PKAin = data[:, 7]   
        potEng = data[:, 8]    
        totEng = data[:, 9]    

        x_min, x_max = simTime[0], simTime[-1]

        ## ------------- 绘制温度变化图 ------------- ##
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.plot(simTime, temp, label="System Temp", color="red", linewidth=2.5)
        ax.plot(simTime, c_ex, label="External Temp", color="blue", linestyle="--", linewidth=2)
        ax.plot(simTime, c_in, label="Internal Temp", color="green", linestyle="-.", linewidth=2)
        ax.plot(simTime, c_PKAin, label="PKA Internal Temp", color="purple", linestyle=":", linewidth=2)

        ax.set_xlabel("Simulation Time (ps)")
        ax.set_ylabel("Temperature (K)")
        ax.set_xlim(x_min, x_max)
        ax.legend(loc="best", frameon=True)
        ax.tick_params(**tick_params)

        plt.tight_layout()
        fig_temp = f"fig_{os.path.splitext(data_file)[0]}.png"
        plt.savefig(fig_temp, dpi=1200)
        plt.close()

        ## ------------- 绘制能量变化图 ------------- ##
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.plot(simTime, potEng, label="Potential Energy", color="blue", linewidth=2.5)
        ax.plot(simTime, totEng, label="Total Energy", color="black", linestyle="--", linewidth=2)

        ax.set_xlabel("Simulation Time")
        ax.set_ylabel("Energy (eV)")
        ax.set_xlim(x_min, x_max)
        ax.legend(loc="best", frameon=True)
        ax.tick_params(**tick_params)

        plt.tight_layout()
        fig_energy = f"flibe_equil_energy_{os.path.splitext(data_file)[0]}.png"
        plt.savefig(fig_energy, dpi=1200)
        plt.close()

        print(f"✔ 处理完成: {data_file} -> {fig_temp}, {fig_energy}")

    except Exception as e:
        print(f"❌ 处理 {data_file} 时出错: {e}")