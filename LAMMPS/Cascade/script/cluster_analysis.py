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

# 設定全局繪圖參數
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

SKIP_BY_DEFAULT = 10  # 默認跳過幀

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
    """讀取單個叢集文件，符合前綴且幀數符合條件時才返回 DataFrame"""
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
    """批量加載所有符合條件的叢集文件"""
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
    """計算每幀的叢集數量，並保存成 CSV"""
    stats = df.groupby('frame').agg({'cluster_id': 'count'}).reset_index()
    stats.columns = ['frame','cluster_count']
    out_csv = f"cluster_stats_summary_{prefix}.csv"
    stats.to_csv(out_csv, index=False)
    print(f"Saved time series stats: {out_csv}")
    return stats


def plot_time_series(stats, prefix):
    """繪製叢集數量隨時間變化圖並保存"""
    fig, ax = plt.subplots(figsize=(8,4))
    ax.plot(stats['frame'], stats['cluster_count'], '-o', linewidth=2)
    ax.set_xlabel('Frame', fontweight='bold')
    ax.set_ylabel('Cluster Count', fontweight='bold')
    ax.tick_params(**tick_params)
    plt.xlim(stats['frame'].min(), stats['frame'].max())
    plt.tight_layout()
    out_pdf = f"cluster_time_series_{prefix}.pdf"
    plt.savefig(out_pdf, dpi=1200, bbox_inches='tight', transparent=True)
    print(f"Saved time series plot: {out_pdf}")
    plt.close(fig)


def plot_cluster_heatmap(df, prefix):
    """繪製叢集大小分佈熱圖"""
    pivot = pd.crosstab(df['cluster_size'], df['frame'])
    data = pivot.values
    masked = np.ma.masked_where(data == 0, data)

    fig, ax = plt.subplots(figsize=(10, 8))
    cmap = plt.cm.viridis
    cmap.set_bad(color='white')
    im = ax.imshow(masked, aspect='auto', origin='lower', interpolation='none', cmap=cmap)

    ax.set_xlabel('Frame', fontweight='bold')
    ax.set_ylabel('Cluster Size', fontweight='bold')
    ax.set_title('Cluster Size Distribution Heatmap', fontweight='bold')

    ax.set_xticks(np.arange(pivot.shape[1]))
    ax.set_xticklabels(pivot.columns, rotation=90)
    ax.set_yticks(np.arange(pivot.shape[0]))
    ax.set_yticklabels(pivot.index)

    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label('Count', fontweight='bold')

    plt.tight_layout()
    out_pdf = f"cluster_heatmap_{prefix}.pdf"
    plt.savefig(out_pdf, dpi=1200)
    print(f"Saved heatmap: {out_pdf}")
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
