#!/usr/bin/env python3
"""
cluster_analysis_pair.py: Analyze atom‐pair clustering over time

This script identifies clusters of specified atom pairs using user‐defined distance cutoffs,
lets you choose x‐axis as timestep or frame index, select subsets of frames/timesteps,
and displays the per‐cell counts on the heatmap.

Example (Li–Li only, skip every 10 frames, plot vs. frame index, only frames 0–100 or specific ones):
  python cluster_analysis_pair.py \
    --dump dump.sum.interior \
    --types 1:F,2:Be,3:Li \
    --cutoffs Li-Li:3.0 \
    --skip 10 \
    --xaxis frame \
    --select 0-100,200,500

Arguments:
  --dump     Path to LAMMPS dump file with “ITEM: ATOMS …” blocks
  --types    Comma‐separated ID:SYMBOL mapping, e.g. 1:F,2:Be,3:Li
  --cutoffs  Comma‐separated SYMBOL1-SYMBOL2:CUTOFF, e.g. Li-Li:3.0,F-Be:2.8
  --skip     Only process every Nth frame (default=1 all frames)
  --xaxis    “timestep” or “frame” (default “timestep”)
  --select   Comma‐separated ranges or values of x‐axis to include,
             e.g. 2000-20000 or 200,2000,20000

Outputs:
  - cluster_count_vs_time.pdf
  - cluster_size_heatmap.pdf (zeros are blank, non-zeros annotated)

Dependencies:
  numpy, scipy, matplotlib
"""

import argparse
from collections import deque, defaultdict
import numpy as np
from scipy.spatial import cKDTree
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

def parse_args():
    p = argparse.ArgumentParser(
        description="Analyze atom‐pair clusters; choose x-axis, select subset, annotate heatmap."
    )
    p.add_argument("--dump",    required=True,
                   help="LAMMPS dump file with “ITEM: ATOMS …”")
    p.add_argument("--types",   required=True,
                   help="Mapping of type IDs to symbols, e.g. 1:F,2:Be,3:Li")
    p.add_argument("--cutoffs", required=True,
                   help="Atom‐pair cutoffs, e.g. Li-Li:3.0,F-Be:2.8")
    p.add_argument("--skip",    type=int, default=1,
                   help="Only process every Nth frame (default=1)")
    p.add_argument("--xaxis",   choices=["timestep","frame"], default="timestep",
                   help="Use LAMMPS timestep or frame index on x‐axis")
    p.add_argument("--select",  default=None,
                   help="Select only these x‐values, e.g. 2000-20000,200,5000")
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

def parse_select(txt):
    """Parse select string into list of (start,end) tuples."""
    ranges = []
    for seg in txt.split(","):
        if "-" in seg:
            a,b = seg.split("-")
            ranges.append((int(a), int(b)))
        else:
            v = int(seg)
            ranges.append((v, v))
    return ranges

def in_selection(x, ranges):
    return any(a <= x <= b for a,b in ranges)

def parse_lammps_dump(fname):
    """
    Yield list of (step, types_array, coords_array) for each frame in the dump.
    Detects column order by header labels.
    """
    frames = []
    with open(fname) as f:
        while True:
            line = f.readline()
            if not line: break
            if line.startswith("ITEM: TIMESTEP"):
                step = int(f.readline().strip())
                # skip to ATOMS header
                while True:
                    line = f.readline()
                    if not line: return frames
                    if line.startswith("ITEM: ATOMS"):
                        cols = line.strip().split()[2:]
                        idx = {name:i for i,name in enumerate(cols)}
                        i_type = idx["type"]
                        i_x    = idx["xu"]
                        i_y    = idx["yu"]
                        i_z    = idx["zu"]
                        break
                types, coords = [], []
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
    N = len(types)
    adj = {i:set() for i in range(N)}
    for symA, symB, cutoff in cutoffs:
        idA, idB = sym2id[symA], sym2id[symB]
        idxA = np.nonzero(types==idA)[0]
        idxB = np.nonzero(types==idB)[0]
        if len(idxA)==0 or len(idxB)==0: continue
        ptsA, ptsB = coords[idxA], coords[idxB]
        if idA==idB:
            tree = cKDTree(ptsA)
            for i,j in tree.query_pairs(r=cutoff):
                u,v = idxA[i], idxA[j]
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
    select_ranges = parse_select(args.select) if args.select else None

    frames      = parse_lammps_dump(args.dump)
    x_times     = []
    x_frames    = []
    cluster_cnt = []
    size_hist   = defaultdict(lambda: defaultdict(int))

    for idx,(step,types,coords) in enumerate(frames):
        if idx % args.skip != 0: continue
        xval = idx if args.xaxis=="frame" else step
        if select_ranges and not in_selection(xval, select_ranges):
            continue

        adj      = build_adjacency(types, coords, cutoffs, sym2id)
        clusters = [c for c in find_clusters(adj) if len(c)>=2]
        cluster_cnt.append(len(clusters))
        x_times.append(step)
        x_frames.append(idx)
        for c in clusters:
            size_hist[len(c)][xval] += 1

    # choose x-axis
    xvals = x_frames if args.xaxis=="frame" else x_times
    xlabel = "Frame index" if args.xaxis=="frame" else "Timestep"

    # --- plot cluster count ---
    plt.figure(figsize=(6,4))
    plt.scatter(xvals, cluster_cnt, s=40, c="tab:blue")
    plt.xlabel(xlabel); plt.ylabel("Cluster Count (≥2)")
    plt.tight_layout()
    plt.savefig("cluster_count_vs_time.pdf", dpi=900)
    plt.close()

    # --- prepare heatmap data ---
    steps = xvals
    sizes = sorted(size_hist)
    Z = np.zeros((len(sizes), len(steps)), int)
    for i,s in enumerate(sizes):
        for j,st in enumerate(steps):
            Z[i,j] = size_hist[s].get(st, 0)

    # --- plot annotated heatmap ---
    fig, ax = plt.subplots(figsize=(8,6))
    X, Y = np.arange(len(steps)+1), np.arange(len(sizes)+1)
    Zm = np.ma.masked_where(Z==0, Z)
    cmap = plt.cm.viridis; cmap.set_bad(color='white')
    pcm = ax.pcolormesh(X, Y, Zm, cmap=cmap, shading="flat")

    # annotate each non-zero cell
    for i in range(len(sizes)):
        for j in range(len(steps)):
            val = Z[i,j]
            if val:
                ax.text(j+0.5, i+0.5, str(val),
                        ha='center', va='center', fontsize=8, color='white')

    ax.set_xticks(np.arange(len(steps))+0.5)
    ax.set_xticklabels(steps, rotation=90)
    ax.set_yticks(np.arange(len(sizes))+0.5)
    ax.set_yticklabels(sizes)
    ax.set_xlabel(xlabel); ax.set_ylabel("Cluster Size")

    cbar = fig.colorbar(pcm, ax=ax, label="Count")
    cbar.locator = MaxNLocator(integer=True)
    cbar.update_ticks()

    plt.tight_layout()
    plt.savefig("cluster_size_heatmap.pdf", dpi=900)
    plt.close()

if __name__ == "__main__":
    main()