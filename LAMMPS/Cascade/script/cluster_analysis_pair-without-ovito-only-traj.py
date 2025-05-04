#!/usr/bin/env python3
"""
cluster_analysis_pair.py: Analyze atom‐pair clustering over time

This script identifies clusters of specified atom pairs using user‐defined distance cutoffs.
For example, to focus solely on Li–Li interactions at 3.0 Å and skip every 10 frames, run:

  python cluster_analysis_pair.py \
    --dump dump.sum.interior \
    --types 1:F,2:Be,3:Li \
    --cutoffs Li-Li:3.0 \
    --skip 10

Then the script will:
  1. Read each frame from the LAMMPS dump (columns by label, not position).
  2. Filter only Li–Li pairs.
  3. Build a graph where edges connect atoms ≤ 3.0 Å.
  4. Find connected components (“clusters”) of size ≥2.
  5. Plot cluster count vs. timestep and a heatmap of cluster‐size distribution.

Fields order can vary between dumps; we look up “id”, “type”, “xu”, “yu”, “zu” by name.

Outputs:
  - cluster_count_vs_time.pdf
  - cluster_size_heatmap.pdf

Dependencies:
  numpy, scipy, matplotlib
"""

import argparse
from collections import deque, defaultdict
import numpy as np
from scipy.spatial import cKDTree
import matplotlib.pyplot as plt

def parse_args():
    p = argparse.ArgumentParser(
        description="Analyze clusters defined by atom‐pair cutoffs over time."
    )
    p.add_argument("--dump",    required=True,
                   help="LAMMPS dump file with “ITEM: ATOMS ...” blocks")
    p.add_argument("--types",   required=True,
                   help="Mapping of type IDs to symbols, e.g. 1:F,2:Be,3:Li")
    p.add_argument("--cutoffs", required=True,
                   help="Atom‐pair cutoffs, e.g. Li-Li:3.0,F-Be:2.8")
    p.add_argument("--skip",    type=int, default=1,
                   help="Only process every Nth frame (default 1: use all frames)")
    return p.parse_args()

def parse_types(txt):
    sym2id = {}
    for item in txt.split(","):
        tid, sym = item.split(":")
        sym2id[sym] = int(tid)
    return sym2id

def parse_cutoffs(txt):
    out = []
    for item in txt.split(","):
        pair, d = item.split(":")
        a,b = pair.split("-")
        out.append((a, b, float(d)))
    return out

def parse_lammps_dump(fname):
    """
    Yield (step, types_array, coords_array) for each frame in the dump.
    Automatically detects column order by name.
    """
    frames = []
    with open(fname) as f:
        while True:
            line = f.readline()
            if not line:
                break
            if line.startswith("ITEM: TIMESTEP"):
                step = int(f.readline().strip())
                # skip to "ITEM: ATOMS" line
                while True:
                    line = f.readline()
                    if not line:
                        return frames
                    if line.startswith("ITEM: ATOMS"):
                        cols = line.strip().split()[2:]
                        idx = {name:i for i,name in enumerate(cols)}
                        # required labels
                        i_type = idx["type"]
                        i_x    = idx["xu"]
                        i_y    = idx["yu"]
                        i_z    = idx["zu"]
                        break
                types, coords = [], []
                # read atom lines until next ITEM or EOF
                while True:
                    pos = f.tell()
                    line = f.readline()
                    if not line or line.startswith("ITEM:"):
                        f.seek(pos)
                        break
                    parts = line.split()
                    types.append(int(parts[i_type]))
                    coords.append((float(parts[i_x]),
                                   float(parts[i_y]),
                                   float(parts[i_z])))
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
    adj = {i:set() for i in range(N)}
    for symA, symB, cutoff in cutoffs:
        idA, idB = sym2id[symA], sym2id[symB]
        idxA = np.nonzero(types==idA)[0]
        idxB = np.nonzero(types==idB)[0]
        if len(idxA)==0 or len(idxB)==0:
            continue
        ptsA, ptsB = coords[idxA], coords[idxB]
        if idA==idB:
            tree = cKDTree(ptsA)
            for i,j in tree.query_pairs(r=cutoff):
                u, v = idxA[i], idxA[j]
                adj[u].add(v); adj[v].add(u)
        else:
            treeB = cKDTree(ptsB)
            for i,pa in enumerate(ptsA):
                u = idxA[i]
                for j in treeB.query_ball_point(pa, cutoff):
                    v = idxB[j]
                    adj[u].add(v); adj[v].add(u)
    return adj

def find_clusters(adj):
    """
    Given adjacency dict, find connected components (clusters).
    Returns list of lists of atom indices.
    """
    visited, clusters = set(), []
    for i in adj:
        if i not in visited:
            comp, queue = [], deque([i])
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
    args    = parse_args()
    sym2id  = parse_types(args.types)
    cutoffs = parse_cutoffs(args.cutoffs)
    frames  = parse_lammps_dump(args.dump)

    times, counts = [], []
    size_hist = defaultdict(lambda: defaultdict(int))

    for idx,(step,types,coords) in enumerate(frames):
        if idx % args.skip != 0:
            continue
        adj      = build_adjacency(types, coords, cutoffs, sym2id)
        clusters = [c for c in find_clusters(adj) if len(c)>=2]
        times.append(step)
        counts.append(len(clusters))
        for c in clusters:
            size_hist[len(c)][step] += 1

    # --- Plot cluster count vs time ---
    plt.figure(figsize=(6,4))
    plt.scatter(times, counts, s=40, c="tab:blue")
    plt.xlabel("Timestep"); plt.ylabel("Cluster Count (size ≥2)")
    plt.tight_layout()
    plt.savefig("cluster_count_vs_time.pdf", dpi=900)
    plt.close()

    # --- Prepare heatmap data ---
    steps = sorted(times)
    sizes = sorted(size_hist)
    Z = np.zeros((len(sizes), len(steps)), int)
    for i,s in enumerate(sizes):
        for j,st in enumerate(steps):
            Z[i,j] = size_hist[s].get(st, 0)

    # --- Plot cluster size heatmap ---
    fig, ax = plt.subplots(figsize=(8,6))
    X, Y = np.arange(len(steps)+1), np.arange(len(sizes)+1)
    pcm = ax.pcolormesh(X, Y, Z, cmap="viridis", shading="flat")
    ax.set_xticks(np.arange(len(steps))+0.5)
    ax.set_xticklabels(steps, rotation=90)
    ax.set_yticks(np.arange(len(sizes))+0.5)
    ax.set_yticklabels(sizes)
    ax.set_xlabel("Timestep"); ax.set_ylabel("Cluster Size")
    fig.colorbar(pcm, ax=ax, label="Count")
    plt.tight_layout()
    plt.savefig("cluster_size_heatmap.pdf", dpi=900)
    plt.close()

if __name__ == "__main__":
    main()
