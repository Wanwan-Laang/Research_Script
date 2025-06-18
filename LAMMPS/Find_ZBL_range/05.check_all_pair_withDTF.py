import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.interpolate import make_interp_spline
import os

plt.rcParams.update({
    'font.family': 'serif',
    'font.serif': ['Computer Modern Roman'],
    'font.size': 12,
    'axes.labelsize': 14,
    'axes.titlesize': 14,
    'xtick.labelsize': 12,
    'ytick.labelsize': 12,
    'legend.fontsize': 10,
    'text.usetex': True
})

def plot_energy_distance(ax, csv_file, show_y_ticks=True):
    """為每個子圖繪製能量-距離關係"""
    # 讀取數據，支持分號註釋
    df = pd.read_csv(csv_file, comment=';')
    distance = df['Distance'].values
    dft = df['DFT'].values
    ml_zbl = df['ML-ZBL'].values

    # 排序數據
    sorted_indices = np.argsort(distance)
    distance_sorted = distance[sorted_indices]
    dft_sorted = dft[sorted_indices]
    ml_zbl_sorted = ml_zbl[sorted_indices]

    # 平滑插值
    x_smooth = np.linspace(distance_sorted.min(), distance_sorted.max(), 300)
    dft_smooth = make_interp_spline(distance_sorted, dft_sorted)(x_smooth)
    ml_zbl_smooth = make_interp_spline(distance_sorted, ml_zbl_sorted)(x_smooth)

    # 繪圖
    ax.plot(x_smooth, dft_smooth, label='DFT', color='#1f77b4', linewidth=2, linestyle='-')
    ax.plot(x_smooth, ml_zbl_smooth, label='ML-ZBL', color='#d62728', linewidth=2, linestyle='--')

    # 添加原始數據點
    ax.scatter(distance_sorted, dft_sorted, color='#1f77b4', s=30, alpha=0.5, zorder=5)
    ax.scatter(distance_sorted, ml_zbl_sorted, color='#d62728', s=30, alpha=0.5, zorder=5)

    # 獲取原子對名稱
    atom_pair = os.path.splitext(os.path.basename(csv_file))[0]
    ax.set_xlabel(rf'{atom_pair} (\AA)')
    
    # 設置網格和邊框
    ax.grid(True, linestyle='--', alpha=0.3)
    ax.spines['top'].set_linewidth(1.5)
    ax.spines['right'].set_linewidth(1.5)
    ax.spines['bottom'].set_linewidth(1.5)
    ax.spines['left'].set_linewidth(1.5)
    
    # 設置刻度
    ax.tick_params(direction='in', width=1.5, length=6, top=True, right=True)
    
    # 設置y軸範圍
    ax.set_ylim(-505, -370)
    
    # 控制是否顯示y軸刻度值
    if not show_y_ticks:
        ax.set_yticklabels([])

# 創建主圖和子圖
fig = plt.figure(figsize=(7, 6))
fig.subplots_adjust(wspace=0.03, hspace=0.3)  # 添加 hspace 參數

# 定義要處理的CSV文件列表
csv_files = ['Be-Be.csv', 'Be-Li.csv', 'Li-Li.csv', 'F-F.csv','F-Li.csv','Be-F.csv'] # 添加所有您需要的文件

# 創建3x2的子圖佈局
for i, csv_file in enumerate(csv_files):
    ax = fig.add_subplot(2, 3, i+1)
    # 只有每行的第一個圖（索引為0和3）顯示y軸刻度值
    show_y_ticks = (i % 3 == 0)
    plot_energy_distance(ax, csv_file, show_y_ticks=show_y_ticks)
    
    # 只在左側子圖顯示y軸標籤
    if i % 3 == 0:
        ax.set_ylabel('Energy (eV)')
    
    # 在第一個子圖添加圖例
    if i == 0:
        ax.legend(frameon=True, edgecolor='black', fancybox=False)

# 保存圖片
plt.savefig('energy_distance_all.pdf', bbox_inches='tight', dpi=300)
print("圖片已保存為: energy_distance_all.pdf")
plt.close()
