#!/usr/bin/env python3
"""
cluster_analysis.py: Process cluster files with customizable prefix, skip interval, and cluster-size range.

Usage:
  python cluster_analysis.py -p raw -s 10 -r 3-5

Options:
  -p, --prefix  File prefix to match (default: raw)
  -s, --skip    Skip interval for frames (default: 10)
  -r, --range   Cluster size range to include in heatmap, e.g. 3-5 (default: all sizes)
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

SKIP_BY_DEFAULT = 10  # 預設跳 frame 間隔


def parse_args():
    parser = argparse.ArgumentParser(
        description="Process and plot cluster files by prefix, skip interval, and size range."
    )
    parser.add_argument(
        '-p', '--prefix', default='raw',
        help="File prefix to match, e.g., raw or test, matches <prefix>.*"
    )
    parser.add_argument(
        '-s', '--skip', type=int, default=SKIP_BY_DEFAULT,
        help=f"Skip interval for frames (default {SKIP_BY_DEFAULT})"
    )
    parser.add_argument(
        '-r', '--range', dest='size_range', default=None,
        help="Cluster size range to include in heatmap, format min-max, e.g. 3-5"
    )
    return parser.parse_args()


def read_cluster_file(path, prefix, skip_by):
    """讀入單個 cluster 檔案，僅當 frame % skip_by == 0 時才返回 DataFrame"""
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
    """一併載入所有符合條件的 cluster 檔案"""
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
    """計算每個 frame 的 cluster 數量並存成 CSV"""
    stats = df.groupby('frame').agg({'cluster_id': 'count'}).reset_index()
    stats.columns = ['frame', 'cluster_count']
    out_csv = f"cluster_stats_summary_{prefix}.csv"
    stats.to_csv(out_csv, index=False)
    print(f"Saved time series stats: {out_csv}")
    return stats


def plot_time_series(stats, prefix):
    """畫 scatter 圖顯示 cluster count 隨 frame 變化"""
    fig, ax = plt.subplots()
    ax.scatter(stats['frame'], stats['cluster_count'], color='blue', s=100, alpha=0.8)
    ax.set_xlabel('Frame', fontweight='400')
    ax.set_ylabel('Cluster Count', fontweight='400')
    ax.tick_params(**tick_params)
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    plt.xlim(stats['frame'].min(), stats['frame'].max() + 1)
    plt.tight_layout()
    out_pdf = f"cluster_time_series_{prefix}.pdf"
    plt.savefig(out_pdf, dpi=1200, bbox_inches='tight', transparent=True)
    print(f"Saved time series scatter plot: {out_pdf}")
    plt.close(fig)


def plot_cluster_heatmap(df, prefix, size_min=None, size_max=None):
    """畫 heatmap，若指定 size_min, size_max 則先過濾"""
    # 過濾 cluster size
    if size_min is not None and size_max is not None:
        df = df[(df['cluster_size'] >= size_min) & (df['cluster_size'] <= size_max)]
    if df.empty:
        print("No clusters in specified size range. Skipping heatmap.")
        return
    pivot = pd.crosstab(df['cluster_size'], df['frame'])
    data = pivot.values
    masked = np.ma.masked_where(data == 0, data)

    nx, ny = pivot.shape[1], pivot.shape[0]
    X = np.arange(nx + 1)
    Y = np.arange(ny + 1)

    fig, ax = plt.subplots()
    cmap = plt.cm.viridis
    cmap.set_bad(color='white')
    pcm = ax.pcolormesh(X, Y, masked, cmap=cmap, shading='flat')

    ax.set_xlabel('Frame', fontweight='400')
    ax.set_ylabel('Cluster Size', fontweight='400')
    ax.set_xticks(np.arange(nx) + 0.5)
    ax.set_xticklabels(pivot.columns, rotation=90)
    ax.set_yticks(np.arange(ny) + 0.5)
    ax.set_yticklabels(pivot.index)

    cbar = fig.colorbar(pcm, ax=ax)
    cbar.locator = MaxNLocator(integer=True)
    cbar.update_ticks()
    cbar.set_label('Count', fontweight='400')

    # 在每個 cell 中心標值
    for i in range(ny):
        for j in range(nx):
            val = data[i, j]
            if val > 0:
                ax.text(j + 0.5, i + 0.5, str(val), ha='center', va='center', fontsize=8, color='white')

    plt.tight_layout()
    rng = f"_{size_min}-{size_max}" if size_min is not None else ''
    out_pdf = f"cluster_heatmap_{prefix}{rng}.pdf"
    plt.savefig(out_pdf, dpi=1200, bbox_inches='tight', transparent=True)
    print(f"Saved heatmap with pcolormesh: {out_pdf}")
    plt.close(fig)


if __name__ == "__main__":
    args = parse_args()
    # 處理 size range
    size_min = size_max = None
    if args.size_range:
        try:
            mn, mx = args.size_range.split('-')
            size_min, size_max = int(mn), int(mx)
        except:
            print("Invalid range format, use min-max. Skipping range filter.")
    df_all = load_all_clusters('.', args.prefix, args.skip)
    if df_all.empty:
        print(f"No files found with prefix '{args.prefix}.' divisible by skip {args.skip}.")
        exit(1)
    stats = compute_time_series_stats(df_all, args.prefix)
    plot_time_series(stats, args.prefix)
    plot_cluster_heatmap(df_all, args.prefix, size_min, size_max)
