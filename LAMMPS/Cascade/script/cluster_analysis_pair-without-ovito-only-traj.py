#!/usr/bin/env python3
"""
cluster_analysis_pair.py: Analyze cluster formation for specified atom‐pair cutoffs over time.

如果你只想分析 Li–Li，
就只在 --cutoffs 裡指定 Li-Li:3.0，不給其它對（像 F–Be、F–Li、Be–Be …）任何閾值，程式就只會挑出 Li–Li 這一種鍵距離來做 cluster 分析，完全忽略其它原子對。

Usage:
  python cluster_analysis_pair.py \
    --dump dump.sum.interior \
    --cutoffs Li-Li:3.0,F-Be:2.8 \
    --types 1:F,2:Be,3:Li
Notes:
	--types 只用來對應 type 編號和元素名稱，完整保留原始 Metadata。
    --cutoffs Li-Li:3.0 唯一指定 Li–Li 的連接距離（例如 3.0 Å）。
    腳本裡面,如果只有Li-Li:3.0，則 這個腳本會先把所有 atom pair 按 type 篩出 Li–Li，再用 ≤3.0 Å 的距離去建圖、找 cluster、畫圖，其他對完全不處理也不會貢獻任何 cluster。

Produces:
  - cluster_count_vs_time.png      # Number of clusters (size ≥ 2) vs timestep
  - cluster_size_heatmap.png      # Heatmap of cluster size distribution over time

Requirements:
  numpy, scipy, matplotlib
"""

import argparse
from collections import deque, defaultdict
import numpy as np
from scipy.spatial import cKDTree
import matplotlib.pyplot as plt

def parse_args():
    parser = argparse.ArgumentParser(
        description="Analyze clusters defined by atom‐pair cutoffs over time."
    )
    parser.add_argument(
        "--dump", required=True,
        help="LAMMPS dump file with trajectory"
    )
    parser.add_argument(
        "--cutoffs", required=True,
        help="Comma‐separated list of SYMBOL1-SYMBOL2:CUTOFF, e.g. Li-Li:3.0,F-Be:2.8"
    )
    parser.add_argument(
        "--types", required=True,
        help="Comma‐separated list of ID:SYMBOL, e.g. 1:F,2:Be,3:Li"
    )
    return parser.parse_args()

def parse_cutoffs(s):
    cutoffs = []
    for item in s.split(","):
        pair, dist = item.split(":")
        a, b = pair.split("-")
        cutoffs.append((a, b, float(dist)))
    return cutoffs

def parse_types(s):
    sym2id = {}
    for item in s.split(","):
        tid, sym = item.split(":")
        sym2id[sym] = int(tid)
    return sym2id

def parse_lammps_dump(fname):
    """
    Parse a LAMMPS dump with blocks:
      ITEM: TIMESTEP
      <step>
      ...
      ITEM: ATOMS id type xu yu zu ...
      <atom lines> ...
    Returns a list of (step, types_array, coords_array).
    """
    frames = []
    with open(fname) as f:
        while True:
            line = f.readline()
            if not line: break
            if line.startswith("ITEM: TIMESTEP"):
                step = int(f.readline().strip())
                # skip until ITEM: ATOMS
                while True:
                    line = f.readline()
                    if line.startswith("ITEM: ATOMS"):
                        cols = line.strip().split()[2:]
                        id_i = cols.index("id")
                        type_i = cols.index("type")
                        x_i = cols.index("xu")
                        y_i = cols.index("yu")
                        z_i = cols.index("zu")
                        break
                types = []
                coords = []
                # read until next ITEM or EOF
                while True:
                    pos = f.tell()
                    line = f.readline()
                    if not line or line.startswith("ITEM:"):
                        f.seek(pos)
                        break
                    parts = line.split()
                    types.append(int(parts[type_i]))
                    coords.append([float(parts[x_i]),
                                   float(parts[y_i]),
                                   float(parts[z_i])])
                frames.append((step,
                               np.array(types, dtype=int),
                               np.array(coords, dtype=float)))
    return frames

def build_adjacency(types, coords, cutoffs, sym2id):
    """
    Build adjacency list for atoms connected by any specified cutoff.
    Returns dict: atom_index -> set(neighbor_indices).
    """
    N = len(types)
    adj = {i: set() for i in range(N)}

    for symA, symB, cutoff in cutoffs:
        idA = sym2id[symA]
        idB = sym2id[symB]
        maskA = (types == idA)
        maskB = (types == idB)
        idxA = np.nonzero(maskA)[0]
        idxB = np.nonzero(maskB)[0]
        if len(idxA) == 0 or len(idxB) == 0:
            continue
        ptsA = coords[idxA]
        ptsB = coords[idxB]
        treeB = cKDTree(ptsB)
        if idA == idB:
            # same‐type: use query_pairs
            treeA = cKDTree(ptsA)
            pairs = treeA.query_pairs(r=cutoff)
            for ia, ib in pairs:
                a = idxA[ia]; b = idxA[ib]
                adj[a].add(b); adj[b].add(a)
        else:
            # cross‐type
            for ia, pa in enumerate(ptsA):
                neighbors = treeB.query_ball_point(pa, cutoff)
                a = idxA[ia]
                for jb in neighbors:
                    b = idxB[jb]
                    adj[a].add(b); adj[b].add(a)
    return adj

def find_clusters(adj):
    """
    Given adjacency dict, find connected components (clusters).
    Returns list of lists of atom indices.
    """
    visited = set()
    clusters = []
    for i in adj:
        if i not in visited:
            comp = []
            queue = deque([i])
            visited.add(i)
            while queue:
                u = queue.popleft()
                comp.append(u)
                for v in adj[u]:
                    if v not in visited:
                        visited.add(v)
                        queue.append(v)
            clusters.append(comp)
    return clusters

def main():
    args = parse_args()
    cutoffs = parse_cutoffs(args.cutoffs)
    sym2id = parse_types(args.types)
    frames = parse_lammps_dump(args.dump)

    times = []
    cluster_counts = []
    cluster_size_dict = defaultdict(lambda: defaultdict(int))
    # cluster_size_dict[size][step] = count

    for step, types, coords in frames:
        adj = build_adjacency(types, coords, cutoffs, sym2id)
        clusters = find_clusters(adj)
        # only count clusters of size >= 2
        sizes = [len(c) for c in clusters if len(c) >= 2]
        cluster_counts.append(len(sizes))
        times.append(step)
        for s in sizes:
            cluster_size_dict[s][step] += 1

    # --- Plot cluster count vs time ---
    plt.figure(figsize=(6,4))
    plt.scatter(times, cluster_counts, c="tab:blue", s=30)
    plt.xlabel("Timestep")
    plt.ylabel("Cluster Count (size ≥2)")
    plt.tight_layout()
    plt.savefig("cluster_count_vs_time.png", dpi=300)
    plt.close()

    # --- Prepare heatmap data ---
    all_steps = sorted(times)
    all_sizes = sorted(cluster_size_dict.keys())
    Z = np.zeros((len(all_sizes), len(all_steps)), dtype=int)
    for i, size in enumerate(all_sizes):
        for j, step in enumerate(all_steps):
            Z[i, j] = cluster_size_dict[size].get(step, 0)

    # --- Plot cluster size heatmap ---
    fig, ax = plt.subplots(figsize=(8,6))
    # use pcolormesh so grid lines line up
    X = np.arange(len(all_steps)+1)
    Y = np.arange(len(all_sizes)+1)
    pcm = ax.pcolormesh(X, Y, Z, cmap="viridis", shading="flat")
    ax.set_xticks(np.arange(len(all_steps))+0.5)
    ax.set_xticklabels(all_steps, rotation=90)
    ax.set_yticks(np.arange(len(all_sizes))+0.5)
    ax.set_yticklabels(all_sizes)
    ax.set_xlabel("Timestep")
    ax.set_ylabel("Cluster Size")
    fig.colorbar(pcm, ax=ax, label="Count")
    plt.tight_layout()
    plt.savefig("cluster_size_heatmap.png", dpi=300)
    plt.close()

if __name__ == "__main__":
    main()
