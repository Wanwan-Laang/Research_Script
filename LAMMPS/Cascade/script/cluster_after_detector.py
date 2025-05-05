import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import argparse

# 設置全局畫圖參數
plt.rcParams.update({
    'font.weight': '400',
    'axes.labelweight': '400',
    'axes.linewidth': '2',
    'axes.titlesize': 12,
    'axes.labelsize': 12,
    'legend.fontsize': 13,
    'xtick.labelsize': 13,
    'ytick.labelsize': 13
})
tick_params = {'direction': 'in', 'width': 2, 'length': 6}

def parse_args():
    parser = argparse.ArgumentParser(description="Cluster analysis with custom ranges.")
    parser.add_argument("-r", "--ranges", type=str, required=True,
                        help="Ranges for coloring, e.g., 70-90-130-150-200")
    return parser.parse_args()

def assign_colors(values, ranges):
    """根據範圍分配顏色"""
    colors = []
    for value in values:
        if value <= 70:  # 小於等於 70 的數據用藍色
            colors.append(0)  # 藍色索引
        else:
            for i, r in enumerate(ranges):
                if value <= r:
                    colors.append(i + 1)  # 其他範圍的顏色索引
                    break
            else:
                colors.append(len(ranges) + 1)  # 超過最大範圍的顏色
    return colors

if __name__ == "__main__":
    args = parse_args()

    # 解析範圍參數
    ranges = list(map(int, args.ranges.split("-")))  # 將範圍轉換為整數列表
    print(f"Using ranges: {ranges}")

    # 讀取數據
    df = pd.read_csv("cluster_stable_F2_70.csv")

    # 計算每個 end_frame 的分佈數量
    end_frame_counts = df["end_frame"].value_counts().sort_index()

    # 計算每個 end_frame 對應的 duration 平均值
    duration_means = df.groupby("end_frame")["duration"].mean()

    # 根據範圍分配顏色
    color_indices = assign_colors(duration_means[end_frame_counts.index], ranges)
    cmap = plt.cm.get_cmap("tab10", len(ranges) + 2)  # 使用高對比度 colormap
    colors = [cmap(i) for i in color_indices]

    # 畫圖
    plt.figure(figsize=(5, 4))
    scatter = plt.scatter(
        end_frame_counts.index,
        end_frame_counts.values,
        c=colors,
        edgecolors="black",
        s=80,
        alpha=0.9
    )

    # 添加圖例
    if ranges[0] > 70:  # 如果範圍的第一個值大於 70，則單獨添加藍色圖例
        plt.scatter([], [], c=[cmap(0)], label="<= 70")  # 藍色

    for i, r in enumerate(ranges):
        if i == 0 and r == 70:  # 如果範圍的第一個值是 70，直接標註為 "<= 70"
            plt.scatter([], [], c=[cmap(i + 1)], label=f"<= {r}")
        else:
            plt.scatter([], [], c=[cmap(i + 1)], label=f"{ranges[i-1] + 1 if i > 0 else 71} - {r}")

    plt.scatter([], [], c=[cmap(len(ranges) + 1)], label=f"> {ranges[-1]}")
    plt.legend(title="Duration Ranges")

    # 設置圖表屬性
    plt.xlabel("Frame")
    plt.ylabel("Molecules Number")
    plt.title("Stable F2 Molecules Number")
    plt.tight_layout()
    plt.tick_params(**tick_params)

    # 保存圖表
    plt.savefig("fig_stable_F2_molecules_number_100.pdf", dpi=900, transparent=True, bbox_inches='tight')

    # 將結果保存到 CSV
    output_df = pd.DataFrame({
        "end_frame": end_frame_counts.index,
        "count": end_frame_counts.values,
        "duration_mean": [duration_means.get(end_frame, 0) for end_frame in end_frame_counts.index],
        "color_index": color_indices
    })
    output_df.to_csv("collect_end_frame_counts_with_high_contrast.csv", index=False)