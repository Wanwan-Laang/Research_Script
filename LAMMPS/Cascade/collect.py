"""
FLiBe 熔鹽系統平衡過程數據可視化腳本

📌 功能：
本腳本用於處理 FLiBe 熔鹽體系的多階段模擬數據，通過合併不同時間段的數據文件，並繪製溫度與能量變化趨勢圖，以幫助分析系統在不同條件下的演變過程。

📌 主要特性：
- **自動加載並合併多個階段的模擬數據**：通過識別命名規則 `flibe_equil_*.txt` 的數據文件，將其按時間順序合併成一個完整的數據序列。
- **自動處理時間偏移**：針對不同模擬階段的時間軸進行校正，確保數據能夠連續拼接。
- **條件變化點標記**：在圖表中標記系統條件變化的時間點，以便識別系統狀態發生變化的時機。
- **繪製兩類圖表**：
  1. **溫度演化圖**：展示系統、外部、內部及 PKA（主動碰撞原子）內部的溫度變化趨勢。
  2. **能量演化圖**：追蹤勢能和總能量隨時間的變化趨勢。
- **高解析度輸出**：圖表將以 `1200 dpi` 高解析度保存，適用於學術論文或報告。

📌 依賴：
- 需要 Python 環境，並安裝 `numpy` 和 `matplotlib` 庫。
- 數據文件應為 `flibe_equil_*.txt` 格式，並包含時間和物理量數據。

📌 適用場景：
- 用於 FLiBe 熔鹽相關的分子動力學 (MD) 模擬後處理。
- 分析模擬過程中的溫度與能量變化，確定系統平衡狀態。


📌 版本：
1.1

📌 最後更新：
2023-08-20
"""

import numpy as np
import matplotlib.pyplot as plt
import glob
import re
from typing import List, Tuple

# --------------------------
# 配置參數區域 (使用者可修改)
# --------------------------
PLOT_STYLE = {
    'font.size': 12,
    'axes.titlesize': 14,
    'axes.labelsize': 13,
    'xtick.labelsize': 12,
    'ytick.labelsize': 12,
    'axes.linewidth': 1.5,
    'lines.linewidth': 2,
    'legend.fontsize': 12
}

COLOR_SCHEME = {
    'temperature': ('#FF5252', '#2196F3', '#4CAF50', '#9C27B0'),
    'energy': ('#795548', '#000000'),
    'condition_change': '#607D8B'
}

FILE_PATTERN = "flibe_equil_*.txt"
OUTPUT_SETTINGS = {
    'dpi': 1200,
    'figsize': (10, 7),
    'tick_params': {'direction': 'in', 'width': 1.8, 'length': 6}
}

# --------------------------
# 核心功能函式
# --------------------------

def natural_sort_key(text: str) -> list:
    """自然排序鍵函式，用於正確處理數字序號"""
    return [
        int(segment) if segment.isdigit() else segment.lower()
        for segment in re.split(r'(\d+)', text)
    ]

def load_and_merge_data(file_pattern: str) -> Tuple[np.ndarray, dict, List[float]]:
    """
    加載並合併多個階段的數據檔案
    回傳:
        simulation_time: 合併後的時間序列
        data_dict: 包含各物理量的字典
        change_points: 條件變化時間點列表
    """
    file_list = sorted(glob.glob(file_pattern), key=natural_sort_key)
    if not file_list:
        raise FileNotFoundError(f"未找到匹配的檔案: {file_pattern}")

    # 初始化數據容器
    data_columns = {
        'temp': [], 'c_ex': [], 'c_in': [], 'c_PKAin': [],
        'potEng': [], 'totEng': []
    }
    time_data = []
    change_points = []
    time_offset = 0.0

    for idx, file_path in enumerate(file_list):
        try:
            data = np.loadtxt(file_path, skiprows=1)
        except Exception as e:
            print(f"加載檔案 {file_path} 時出錯: {str(e)}")
            continue

        # 處理時間偏移
        current_time = data[:, 0] + time_offset
        time_data.extend(current_time)
        
        # 記錄條件變化點
        if idx > 0:
            change_points.append(time_offset)
        
        # 累加時間偏移量
        time_offset = current_time[-1]

        # 收集各列數據
        for i, key in enumerate(data_columns.keys(), start=4):
            data_columns[key].extend(data[:, i])

    # 轉換為NumPy陣列
    return (
        np.array(time_data),
        {k: np.array(v) for k, v in data_columns.items()},
        change_points
    )

def create_figure(title: str, ylabel: str):
    """初始化繪圖畫布"""
    fig, ax = plt.subplots(figsize=OUTPUT_SETTINGS['figsize'])
    ax.set_title(title, pad=15)
    ax.set_xlabel("模擬時間 (ps)", fontweight='medium')
    ax.set_ylabel(ylabel, fontweight='medium')
    ax.tick_params(**OUTPUT_SETTINGS['tick_params'])
    return fig, ax

def plot_condition_changes(ax, change_points: List[float]):
    """繪製條件變化標記線"""
    for i, cp in enumerate(change_points):
        label = "條件變化點" if i == 0 else None
        ax.axvline(cp, color=COLOR_SCHEME['condition_change'],
                   linestyle='--', linewidth=1.2, alpha=0.7,
                   label=label)

# --------------------------
# 主程式
# --------------------------

def main():
    # 初始化繪圖樣式
    plt.style.use('seaborn')
    plt.rcParams.update(PLOT_STYLE)

    try:
        # 加載並處理數據
        time, data_dict, change_points = load_and_merge_data(FILE_PATTERN)
        
        # 繪製溫度變化圖
        fig_temp, ax_temp = create_figure(
            "FLiBe系統溫度演化過程", "溫度 (K)")
        ax_temp.plot(time, data_dict['temp'], label='系統溫度', 
                    color=COLOR_SCHEME['temperature'][0])
        ax_temp.plot(time, data_dict['c_ex'], label='外部溫度', 
                    color=COLOR_SCHEME['temperature'][1], linestyle='--')
        ax_temp.plot(time, data_dict['c_in'], label='內部溫度',
                    color=COLOR_SCHEME['temperature'][2], linestyle='-.')
        ax_temp.plot(time, data_dict['c_PKAin'], label='PKA內部溫度',
                    color=COLOR_SCHEME['temperature'][3], linestyle=':')
        plot_condition_changes(ax_temp, change_points)
        ax_temp.legend(loc='upper right', framealpha=0.9)
        fig_temp.savefig("temperature_evolution.png", 
                        dpi=OUTPUT_SETTINGS['dpi'], bbox_inches='tight')

        # 繪製能量變化圖
        fig_energy, ax_energy = create_figure(
            "FLiBe系統能量演化過程", "能量 (eV)")
        ax_energy.plot(time, data_dict['potEng'], label='勢能',
                      color=COLOR_SCHEME['energy'][0])
        ax_energy.plot(time, data_dict['totEng'], label='總能量',
                      color=COLOR_SCHEME['energy'][1], linestyle='--')
        plot_condition_changes(ax_energy, change_points)
        ax_energy.legend(loc='upper right', framealpha=0.9)
        fig_energy.savefig("energy_evolution.png", 
                          dpi=OUTPUT_SETTINGS['dpi'], bbox_inches='tight')

        print("可視化結果已保存: temperature_evolution.png, energy_evolution.png")

    except Exception as e:
        print(f"程式執行出錯: {str(e)}")

if __name__ == "__main__":
    main()