#!/usr/bin/env python3
import os
import re
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
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

SKIP_BY = 10  # 只读取每隔 SKIP_BY 帧的文件

# 1. 读取单个 cluster 文件
def read_cluster_file(path):
    fname = os.path.basename(path)
    m = re.search(r"raw[._]?(\d+)", fname)
    if not m:
        return None
    frame = int(m.group(1))
    if frame % SKIP_BY != 0:
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

# 2. 批量加载所有 cluster 文件
def load_all_clusters(folder):
    pattern = os.path.join(folder, "raw.*")
    files = [f for f in glob.glob(pattern) if os.path.isfile(f)]
    files.sort(key=lambda f: int(re.search(r"raw[._]?(\d+)", os.path.basename(f)).group(1)))
    dfs = []
    for f in files:
        df = read_cluster_file(f)
        if df is not None:
            dfs.append(df)
    return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()

# 3. 计算时间序列统计
def compute_time_series_stats(df):
    stats = df.groupby('frame').agg({
        'cluster_id':        'count',
        'cluster_size':    ['mean','max'],
        'radius_of_gyration':'max'
    })
    stats.columns = ['cluster_count','avg_cluster_size','max_cluster_size','max_Rg']
    stats = stats.reset_index()
    stats.to_csv("cluster_stats_summary.csv", index=False)
    return stats

# 4. 绘制时间序列图
def plot_time_series(stats):
    fig, axs = plt.subplots(4,1, figsize=(8,12), sharex=True)
    axs[0].plot(stats['frame'], stats['cluster_count'], '-o')
    axs[0].set_ylabel('Cluster Count')
    axs[1].plot(stats['frame'], stats['avg_cluster_size'], '-o')
    axs[1].set_ylabel('Avg Cluster Size')
    axs[2].plot(stats['frame'], stats['max_cluster_size'], '-o')
    axs[2].set_ylabel('Max Cluster Size')
    axs[3].plot(stats['frame'], stats['max_Rg'], '-o')
    axs[3].set_ylabel('Max Radius of Gyration')
    axs[3].set_xlabel('Frame')
    plt.xlim(stats['frame'].min(), stats['frame'].max())
    plt.tight_layout()
    plt.savefig("cluster_time_series.png", dpi=300)
    plt.show()

# 5. 构建并绘制热图
def plot_cluster_heatmap(df):
    """
    构建 pivot table：行=cluster_size, 列=frame，值=出现次数；
    并绘制热图。count==0 显示为白色，其它值使用 viridis 颜色映射。
    """
    pivot = pd.crosstab(df['cluster_size'], df['frame'])
    data = pivot.values

    # 将 0 值掩码，这样它们在 heatmap 上会显示为白色
    masked = np.ma.masked_where(data == 0, data)

    fig, ax = plt.subplots(figsize=(10, 8))
    cmap = plt.cm.viridis
    cmap.set_bad(color='white')  # 掩码（原始值==0）显示为白色

    im = ax.imshow(masked, aspect='auto', origin='lower',
                   interpolation='none', cmap=cmap)

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
    plt.savefig("cluster_heatmap.png", dpi=300)
    plt.show()

# 6. 主程序
def main():
    cluster_folder = "./"  # 存放 raw.* 文件的目录
    df_all = load_all_clusters(cluster_folder)
    if df_all.empty:
        print(f"No cluster files found in '{cluster_folder}' with skip interval {SKIP_BY}.")
        return
    stats = compute_time_series_stats(df_all)
    plot_time_series(stats)
    plot_cluster_heatmap(df_all)

if __name__ == "__main__":
    main()