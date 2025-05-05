import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import argparse

# 設置全局畫圖參數
plt.rcParams.update({
    'font.weight': '400',
    'axes.labelweight': '400',
    'axes.linewidth': 2,
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
                        help="Ranges for coloring, e.g., 69-90-130-200")
    return parser.parse_args()

def assign_colors(values, ranges):
    """根據範圍分配顏色"""
    colors = []
    for value in values:
        for i, r in enumerate(ranges):
            if value <= r:
                colors.append(i)  # 分配顏色索引
                break
        else:
            colors.append(len(ranges))  # 超過最大範圍的顏色
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
    cmap = plt.cm.get_cmap("rainbow", len(ranges) + 1)  # 使用彩虹色 colormap
    colors = [cmap(i) for i in color_indices]

    # 畫圖
    plt.figure(figsize=(5, 3.8))
    scatter = plt.scatter(
        end_frame_counts.index,
        end_frame_counts.values,
        c=colors,
        edgecolors="black",
        s=100,
        alpha=1
    )

    # 添加圖例
    for i, r in enumerate(ranges):
        if i == 0:
            plt.scatter([], [], c=[cmap(i)], label=f"<= {r}")
        else:
            plt.scatter([], [], c=[cmap(i)], label=f"{ranges[i-1] + 1} - {r}")
    plt.scatter([], [], c=[cmap(len(ranges))], label=f"> {ranges[-1]}")

    # 設置圖例為兩列並使其背景透明
    legend = plt.legend(title="Frame Duration Ranges", frameon=True, ncol=2)  # 設置圖例為兩列
    legend.get_frame().set_alpha(0.0)  # 設置圖例背景透明

    # 設置圖表屬性
    plt.xlabel("Frame (each for 0.01ps)")
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
    output_df.to_csv("collect_end_frame_counts_with_custom_ranges.csv", index=False)