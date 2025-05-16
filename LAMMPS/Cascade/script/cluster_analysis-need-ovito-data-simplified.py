#python cluster_analysis_simplified.py -p raw-init-peak  -s 10
import os
import re
import glob
import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

# Plot style
plt.rcParams.update({
    'font.weight': '400',
    'axes.labelweight': '400',
    'axes.linewidth': 2,
    'axes.titlesize': 12,
    'axes.labelsize': 12,
    'legend.fontsize': 12,
    'xtick.labelsize': 12,
    'ytick.labelsize': 12
})
tick_params = {'direction': 'in', 'width': 2, 'length': 6}

# 固定順序
CATEGORY_ORDER = ["free F", "1 Be", "2 Be", "3 Be", "polymer"]
CATEGORY_MAP = {
    "free F": lambda s: s == 1,
    "1 Be":   lambda s: 3 <= s <= 5,
    "2 Be":   lambda s: s == 9,
    "3 Be":   lambda s: s == 13,
    "polymer":lambda s: s >= 17
}

def parse_args():
    p = argparse.ArgumentParser(description="Simplified cluster category heatmap and trend plots.")
    p.add_argument('-p', '--prefix', default='raw', help="File prefix to match")
    p.add_argument('-s', '--skip', type=int, default=10, help="Skip interval for frames")
    return p.parse_args()

def read_cluster_file(path, prefix, skip_by):
    fname = os.path.basename(path)
    m = re.search(rf"{re.escape(prefix)}[._]?(\d+)", fname)
    if not m: return None
    frame = int(m.group(1))
    if frame % skip_by != 0: return None
    df = pd.read_csv(
        path, delim_whitespace=True, comment='#',
        names=['cluster_id', 'cluster_size', 'com_x', 'com_y', 'com_z',
               'radius_of_gyration', 'g_XX', 'g_YY', 'g_ZZ', 'g_XY', 'g_XZ', 'g_YZ']
    )
    df['frame'] = frame
    return df

def load_all_clusters(folder, prefix, skip_by):
    pattern = os.path.join(folder, f"{prefix}.*")
    files = sorted(glob.glob(pattern), key=lambda f: int(re.search(rf"{re.escape(prefix)}[._]?(\d+)", os.path.basename(f)).group(1)))
    dfs = [read_cluster_file(f, prefix, skip_by) for f in files]
    return pd.concat([df for df in dfs if df is not None], ignore_index=True) if dfs else pd.DataFrame()

def categorize(df):
    def assign_label(size):
        for label in CATEGORY_ORDER:
            if CATEGORY_MAP[label](size):
                return label
        return None
    df['category'] = df['cluster_size'].apply(assign_label)
    df = df.dropna(subset=['category']).copy()  
    return df

def plot_heatmap(df, prefix):
    df['category'] = pd.Categorical(df['category'], categories=CATEGORY_ORDER, ordered=True)
    pivot = pd.crosstab(df['category'], df['frame']).reindex(CATEGORY_ORDER)
    data = pivot.values
    masked = np.ma.masked_where(data == 0, data)

    fig, ax = plt.subplots()
    nx, ny = pivot.shape[1], pivot.shape[0]
    X = np.arange(nx + 1)
    Y = np.arange(ny + 1)

    cmap = plt.cm.viridis
    cmap.set_bad(color='white')
    pcm = ax.pcolormesh(X, Y, masked, cmap=cmap, shading='flat')

    ax.set_xlabel('Frame', fontweight='400')
    ax.set_ylabel('Cluster Type', fontweight='400')
    ax.set_xticks(np.arange(nx) + 0.5)
    ax.set_xticklabels(pivot.columns, rotation=90)
    ax.set_yticks(np.arange(ny) + 0.5)
    ax.set_yticklabels(pivot.index)

    cbar = fig.colorbar(pcm, ax=ax)
    cbar.locator = MaxNLocator(integer=True)
    cbar.update_ticks()
    cbar.set_label('Count', fontweight='400')

    for i in range(ny):
        for j in range(nx):
            val = data[i, j]
            if val > 0:
                ax.text(j + 0.5, i + 0.5, str(val), ha='center', va='center', fontsize=8, color='white')

    plt.tight_layout()
    plt.savefig(f"category_heatmap_{prefix}.pdf", dpi=1200, bbox_inches='tight', transparent=True)
    plt.close(fig)
    print(f"✅ Saved heatmap: category_heatmap_{prefix}.pdf")

def plot_overall_trend(df, prefix):
    trend = df.groupby(['frame', 'category']).size().unstack(fill_value=0).reindex(columns=CATEGORY_ORDER)
    fig, ax = plt.subplots()
    for label in CATEGORY_ORDER:
        ax.plot(trend.index, trend[label], label=label, lw=2)
    ax.set_xlabel("Frame")
    ax.set_ylabel("Count")
    ax.legend()
    ax.grid(True)
    plt.tight_layout()
    plt.savefig(f"category_barplot_{prefix}.pdf", dpi=1200, bbox_inches='tight', transparent=True)
    plt.close(fig)
    print(f"✅ Saved overview trend: category_barplot_{prefix}.pdf")

def plot_individual_category_trends(df, prefix):
    trend = df.groupby(['frame', 'category']).size().unstack(fill_value=0).reindex(columns=CATEGORY_ORDER)
    for label in CATEGORY_ORDER:
        fig, ax = plt.subplots()
        ax.plot(trend.index, trend[label], color='blue', lw=2)
        ax.set_xlabel("Frame")
        ax.set_ylabel(f"Count of {label}")
        ax.set_title(f"{label} Trend")
        ax.grid(True)
        plt.tight_layout()
        fname = f"fig_{prefix}_{label.replace(' ', '_')}_trend.pdf"
        plt.savefig(fname, dpi=1200, bbox_inches='tight', transparent=True)
        plt.close(fig)
        print(f"✅ Saved individual trend: {fname}")

def export_trend_to_csv(df, prefix):
    trend = df.groupby(['frame', 'category']).size().unstack(fill_value=0).reindex(columns=CATEGORY_ORDER)
    csv_path = f"category_trend_{prefix}.csv"
    trend.to_csv(csv_path)
    print(f"✅ Saved trend CSV: {csv_path}")

if __name__ == "__main__":
    args = parse_args()
    df_all = load_all_clusters('.', args.prefix, args.skip)
    if df_all.empty:
        print(f"❌ No valid cluster files with prefix '{args.prefix}' found.")
        exit(1)
    df_cat = categorize(df_all)
    if df_cat.empty:
        print("❌ No clusters matched specified categories.")
        exit(1)
    plot_heatmap(df_cat, args.prefix)
    plot_overall_trend(df_cat, args.prefix)
    plot_individual_category_trends(df_cat, args.prefix)
    export_trend_to_csv(df_cat, args.prefix)
