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
    """
    解析命令行參數。

    使用方式：
    1. 指定輸入檔案和顏色分段範圍：
       python cluster_after_detector_all_1.py -f cluster_stable_F2_1.70.csv -r 69-100-150-200-250 -m

    2. 啟用過濾功能（可選）：
       -m 或 --filter-min：過濾掉 duration 小於或等於範圍中的第一個值（此例中為 69）
       無需再顯式指定具體閾值。

    3. 輸入檔案應包含以下欄位：
       - end_frame: 分子消失時的結束幀
       - duration: 該分子的存活持續時間（單位：幀）

    4. 輸出：
       - 圖表：fig_stable_F2_molecules_number_rainbow.pdf
       - 統計結果 CSV：collect_end_frame_counts_with_custom_ranges.csv
    """
    parser = argparse.ArgumentParser(description="Cluster analysis with custom ranges.")
    parser.add_argument("-f", "--file", type=str, required=True,
                        help="Input CSV file, e.g., cluster_stable_F2_1.43.csv")
    parser.add_argument("-r", "--ranges", type=str, required=True,
                        help="Ranges for coloring, e.g., 69-90-130-200")
    parser.add_argument("-m", "--filter-min", action='store_true',
                        help="Enable filtering of data with duration <= first range value")
    return parser.parse_args()


def assign_colors(values, ranges):
    """
    根據範圍分配顏色。
    :param values: 數據值列表。
    :param ranges: 顏色分段範圍。
    :return: 每個值對應的顏色索引列表。
    """
    colors = []
    for value in values:
        for i, r in enumerate(ranges):
            if value <= r:
                colors.append(i)
                break
        else:
            colors.append(len(ranges))
    return colors


if __name__ == "__main__":
    args = parse_args()

    # 解析範圍參數
    ranges = list(map(int, args.ranges.split("-")))
    print(f"Using ranges: {ranges}")

    # 讀取數據
    df = pd.read_csv(args.file)
    print(f"Loaded data from {args.file}")

    # 過濾數據（根據範圍的第一個值）
    if args.filter_min:
        original_count = len(df)
        threshold = ranges[0]
        df = df[df["duration"] > threshold]
        filtered_count = len(df)
        print(f"Filtered data: {original_count - filtered_count} rows removed (duration <= {threshold})")

    # 計算每個 end_frame 的分佈數量
    end_frame_counts = df["end_frame"].value_counts().sort_index()

    # 計算每個 end_frame 對應的 duration 平均值
    duration_means = df.groupby("end_frame")["duration"].mean()

    # 根據範圍分配顏色
    color_indices = assign_colors(duration_means[end_frame_counts.index], ranges)
    cmap = plt.cm.get_cmap("rainbow", len(ranges) + 1)
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
            plt.scatter([], [], c=[cmap(i)], label=f"{ranges[i - 1] + 1} - {r}")
    plt.scatter([], [], c=[cmap(len(ranges))], label=f"> {ranges[-1]}")

    legend = plt.legend(title="Frame Duration Ranges", frameon=True, ncol=2)
    legend.get_frame().set_alpha(0.0)

    # 設置圖表屬性
    plt.xlabel("Frame (each for 0.01ps)")
    plt.ylabel("Molecules Number")
    plt.title("Stable F2 Molecules Number")
    plt.tight_layout()
    plt.tick_params(**tick_params)

    # 保存圖表
    plt.savefig("fig_stable_F2_molecules_number_rainbow.pdf", dpi=900, transparent=True, bbox_inches='tight')

    # 保存統計結果到 CSV
    output_df = pd.DataFrame({
        "end_frame": end_frame_counts.index,
        "count": end_frame_counts.values,
        "duration_mean": [duration_means.get(end_frame, 0) for end_frame in end_frame_counts.index],
        "color_index": color_indices
    })
    output_df.to_csv("collect_end_frame_counts_with_custom_ranges.csv", index=True)
