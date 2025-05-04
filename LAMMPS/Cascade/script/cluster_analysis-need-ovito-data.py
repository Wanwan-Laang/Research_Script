#!/usr/bin/env python3
"""
cluster_analysis.py: Process cluster files with customizable prefix and skip interval.

Usage:
  python cluster_analysis.py -p raw -s 10

Options:
  -p, --prefix  File prefix to match (default: raw)
  -s, --skip    Skip interval for frames (default: 10)
"""
import os
import re
import glob
import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

# 設置全局畫圖參數
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

SKIP_BY_DEFAULT = 10  # 預設跳 frame 間隔

def parse_args():
    parser = argparse.ArgumentParser(
        description="Process and plot cluster files by prefix and skip interval."
    )
    parser.add_argument(
        '-p', '--prefix', default='raw',
        help="File prefix to match, e.g., raw or test, matches <prefix>.*"
    )
    parser.add_argument(
        '-s', '--skip', type=int, default=SKIP_BY_DEFAULT,
        help=f"Skip interval for frames (default {SKIP_BY_DEFAULT})"
    )
    return parser.parse_args()

def read_cluster_file(path, prefix, skip_by):
    """讀入單個 cluster 檔案，夾到 prefix 同埋 frame 屬於 skip_by 條件先返 DataFrame"""
    fname = os.path.basename(path)
    m = re.search(rf"{re.escape(prefix)}[._]?(\d+)", fname)
    if not m:
        return None
    frame = int(m.group(1))
    if frame % skip_by != 0:
        return None
    df = pd.read_csv(
        path, delim_whitespace=True, comment='#',
        names=[
            'cluster_id', 'cluster_size',
            'com_x', 'com_y', 'com_z',
            'radius_of_gyration',
            'g_XX', 'g_YY', 'g_ZZ', 'g_XY', 'g_XZ', 'g_YZ'
        ]
    )
    df['frame'] = frame
    return df

def load_all_clusters(folder, prefix, skip_by):
    """一齊 load晒所有符合條件嘅 cluster 檔案"""
    pattern = os.path.join(folder, f"{prefix}.*")
    files = sorted(
        glob.glob(pattern),
        key=lambda f: int(re.search(rf"{re.escape(prefix)}[._]?(\d+)", os.path.basename(f)).group(1))
    )
    dfs = []
    for f in files:
        df = read_cluster_file(f, prefix, skip_by)
        if df is not None:
            dfs.append(df)
    return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()

def compute_time_series_stats(df, prefix):
    """計算每個 frame 入面有幾多 cluster，並存成 CSV"""
    stats = df.groupby('frame').agg({'cluster_id': 'count'}).reset_index()
    stats.columns = ['frame','cluster_count']
    out_csv = f"cluster_stats_summary_{prefix}.csv"
    stats.to_csv(out_csv, index=False)
    print(f"Saved time series stats: {out_csv}")
    return stats

def plot_time_series(stats, prefix):
    """畫 scatter 圖顯示 cluster count 隨 frame 變化"""
    fig, ax = plt.subplots()
    ax.scatter(stats['frame'], stats['cluster_count'], color='blue', s=100, alpha=0.8)
    ax.set_xlabel('Frame', fontweight='bold')
    ax.set_ylabel('Cluster Count', fontweight='bold')
    ax.tick_params(**tick_params)
    # ★ 令 y 軸淨係顯示整數
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    plt.xlim(stats['frame'].min(), stats['frame'].max()+1)
    plt.tight_layout()
    out_pdf = f"cluster_time_series_{prefix}.pdf"
    plt.savefig(out_pdf, dpi=1200, bbox_inches='tight', transparent=True)
    print(f"Saved time series scatter plot: {out_pdf}")
    plt.close(fig)

def plot_cluster_heatmap(df, prefix):
    """用 pcolormesh 畫 heatmap，方便調整格仔大小，同時顯示每格嘅數值"""
    pivot = pd.crosstab(df['cluster_size'], df['frame'])
    data = pivot.values
    masked = np.ma.masked_where(data == 0, data)

    nx = pivot.shape[1]
    ny = pivot.shape[0]
    X = np.arange(nx+1)
    Y = np.arange(ny+1)

    fig, ax = plt.subplots(figsize=(10, 6))
    cmap = plt.cm.viridis
    cmap.set_bad(color='white')

    pcm = ax.pcolormesh(X, Y, masked, cmap=cmap, shading='flat')

    ax.set_xlabel('Frame', fontweight='bold')
    ax.set_ylabel('Cluster Size', fontweight='bold')
    ax.set_title('Cluster Size Distribution Heatmap', fontweight='bold')

    ax.set_xticks(np.arange(nx) + 0.5)
    ax.set_xticklabels(pivot.columns, rotation=90)
    ax.set_yticks(np.arange(ny) + 0.5)
    ax.set_yticklabels(pivot.index)

    # ★ 強制 colorbar 只顯示整數
    from matplotlib.ticker import MaxNLocator
    cbar = fig.colorbar(pcm, ax=ax)
    cbar.locator = MaxNLocator(integer=True)
    cbar.update_ticks()
    cbar.set_label('Count', fontweight='bold')

    # ─── 在每個 cell 中心加上數值 ───
    for i in range(ny):
        for j in range(nx):
            val = data[i, j]
            if val > 0:
                ax.text(
                    j + 0.5,      # x 位置
                    i + 0.5,      # y 位置
                    str(val),     # 要顯示嘅數字
                    ha='center',  # 水平置中
                    va='center',  # 垂直置中
                    fontsize=8,
                    color='white' #if val > data.max()/2 else 'black' # 可以把註釋取消
                )

    plt.tight_layout()
    out_pdf = f"cluster_heatmap_{prefix}.pdf"
    plt.savefig(out_pdf, dpi=1200, bbox_inches='tight', transparent=True)
    print(f"Saved heatmap with pcolormesh: {out_pdf}")
    plt.close(fig)

if __name__ == "__main__":
    args = parse_args()
    df_all = load_all_clusters('.', args.prefix, args.skip)
    if df_all.empty:
        print(f"No files found with prefix '{args.prefix}.' divisible by skip {args.skip}.")
        exit(1)
    stats = compute_time_series_stats(df_all, args.prefix)
    plot_time_series(stats, args.prefix)
    plot_cluster_heatmap(df_all, args.prefix)