#!/usr/bin/env python3
"""
cluster_stable_F2_detector.py

Detect “stable” F₂ molecules from OVITO cluster‐list exports.

Usage:
  python cluster_stable_F2_detector.py \
    -p raw-initerior-all \
    -t 1.7 \
    -n 50 \
    [-s 0-100,200]

Arguments:
  -p, --prefix     Filename prefix (e.g. raw-initerior-all)
  -t, --track-dist COM tracking distance threshold (Å), only size=2 clusters
  -n, --persist    Minimum consecutive frames to consider “stable” (default:1)
  -s, --select     (optional) Frames to include, e.g. 0-100,200

Outputs:
  cluster_stable_F2_<track_dist>.csv  with columns:
    start_frame,end_frame,duration,com_x,com_y,com_z
    fig_delta_r_COM_hist.pdf              histogram of all matched displacements
    fig_delta_r_COM_stable_hist.pdf       histogram of Δr_COM from persist-qualified stable F₂
    collect_fig_delta_r_COM_stats.log      statistics summary for both categories
"""
import os
import re
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def parse_args():
    p = argparse.ArgumentParser(
        description="Detect stable F₂ from OVITO cluster‐list exports"
    )
    p.add_argument("-p", "--prefix", required=True, help="Filename prefix (e.g. raw-initerior-all)")
    p.add_argument("-t", "--track-dist", dest="track_dist", type=float, default=0.5,
                   help="COM tracking distance threshold in Å (default: 0.5)")
    p.add_argument("-n", "--persist", type=int, default=1,
                   help="Minimum consecutive frames to be stable (default: 1)")
    p.add_argument("-s", "--select", default=None,
                   help="Frames to include, e.g. 0-100,200 (optional)")
    return p.parse_args()

def parse_select(txt):
    rng = []
    for seg in txt.split(","):
        if "-" in seg:
            a, b = seg.split("-")
            rng.append((int(a), int(b)))
        else:
            v = int(seg)
            rng.append((v, v))
    return rng

def in_select(frame, ranges):
    return any(a <= frame <= b for a, b in ranges)

def load_cluster_COMs(prefix, select_ranges=None):
    entries = []
    for fn in sorted(os.listdir(".")):
        if not fn.startswith(prefix + "."):
            continue
        m = re.match(rf"{re.escape(prefix)}\.(\d+)", fn)
        if not m:
            continue
        frame = int(m.group(1))
        if select_ranges and not in_select(frame, select_ranges):
            continue

        cols = None
        with open(fn) as f:
            for L in f:
                if '"' in L:
                    cols = re.findall(r'"([^"]+)"', L)
                    break
        if not cols:
            print(f"⚠️ skip {fn}: no quoted header")
            continue

        df = pd.read_csv(fn, comment="#", delim_whitespace=True, header=None, names=cols)
        sub = df[df["Cluster Size"] == 2]
        com = sub[["Center of Mass.X", "Center of Mass.Y", "Center of Mass.Z"]].values
        entries.append((frame, com))

    return sorted(entries, key=lambda x: x[0])

def detect_stable_F2(frames_com, track_dist, persist):
    trajs = []
    stable = []
    cut2 = track_dist * track_dist
    delta_r_all = []
    delta_r_stable = []

    for frame, coms in frames_com:
        for t in trajs:
            t['matched'] = False
        used = set()

        for i, pt in enumerate(coms):
            best = None
            bestd = cut2
            for t in trajs:
                if t['last'] == frame - 1:
                    d2 = np.sum((t['com'] - pt)**2)
                    if d2 < bestd:
                        bestd = d2
                        best = t
            if best:
                d = np.sqrt(bestd)
                delta_r_all.append(d)
                best['history'].append((frame, pt.copy()))
                best['last'] = frame
                best['com'] = pt.copy()
                best['matched'] = True
                used.add(i)

        new_trajs = []
        for t in trajs:
            if t.get('matched'):
                new_trajs.append(t)
            else:
                dur = len(t['history'])
                if dur >= persist:
                    st = t['history'][0][0]
                    en = t['history'][-1][0]
                    c0 = t['history'][0][1]
                    stable.append({
                        'start_frame': st,
                        'end_frame': en,
                        'duration': dur,
                        'com_x': c0[0],
                        'com_y': c0[1],
                        'com_z': c0[2],
                        'history': t['history']
                    })
        trajs = new_trajs

        for i, pt in enumerate(coms):
            if i not in used:
                trajs.append({
                    'last': frame,
                    'com': pt.copy(),
                    'history': [(frame, pt.copy())]
                })

    for t in trajs:
        dur = len(t['history'])
        if dur >= persist:
            st = t['history'][0][0]
            en = t['history'][-1][0]
            c0 = t['history'][0][1]
            stable.append({
                'start_frame': st,
                'end_frame': en,
                'duration': dur,
                'com_x': c0[0],
                'com_y': c0[1],
                'com_z': c0[2],
                'history': t['history']
            })

    for s in stable:
        h = s['history']
        for i in range(1, len(h)):
            delta = np.linalg.norm(h[i][1] - h[i - 1][1])
            delta_r_stable.append(delta)

    return stable, delta_r_all, delta_r_stable

def main():
    args = parse_args()
    select_ranges = parse_select(args.select) if args.select else None
    frames_com = load_cluster_COMs(args.prefix, select_ranges)
    print(f">>> matched {len(frames_com)} files with prefix \"{args.prefix}\"")
    for f, coms in frames_com[:5]:
        print(f" frame {f}: got {len(coms)} size-2 clusters")

    stable, delta_r_all, delta_r_stable = detect_stable_F2(frames_com, args.track_dist, args.persist)
    df = pd.DataFrame([{k: s[k] for k in s if k != 'history'} for s in stable],
                      columns=['start_frame','end_frame','duration','com_x','com_y','com_z'])
    out = f"cluster_stable_F2_{args.track_dist:.2f}.csv"
    df.to_csv(out, index=False)
    print(f"Detected {len(df)} stable F₂ → {out}")

    def plot_and_report(data, fname):
        arr = np.array(data)
        mean_r = np.mean(arr)
        max_r = np.max(arr)
        p95_r = np.percentile(arr, 95)

        plt.figure(figsize=(8, 5))
        plt.hist(arr, bins=50, alpha=0.8, label="Δr_COM",color='orange')
        #plt.axvline(args.track_dist, color='r', linestyle='--', label=f'track_dist = {args.track_dist:.2f} Å')
        plt.axvline(mean_r, color='g', linestyle='--', label=f'mean = {mean_r:.2f} Å')
        plt.axvline(p95_r, color='b', linestyle='--', label=f'95th pct = {p95_r:.2f} Å')
        plt.axvline(max_r, color='k', linestyle=':', label=f'max = {max_r:.2f} Å')
        plt.xlabel("Δr_COM per frame (Å)")
        plt.ylabel("Count")
        plt.title(f"Histogram of COM displacement: {fname}")
        plt.legend()
        plt.tight_layout()
        plt.savefig(fname, dpi=300)
        return mean_r, max_r, p95_r, len(arr)

    stats_all = plot_and_report(delta_r_all, "fig_delta_r_COM_hist.pdf")
    stats_stable = plot_and_report(delta_r_stable, "fig_delta_r_COM_stable_hist.pdf")

    with open("collect_fig_delta_r_COM_stats.log", "w") as f:
        f.write("Δr_COM statistics\n=================\n")
        f.write("[All matched F₂ pairs]\n")
        f.write(f"track_dist       = {args.track_dist:.3f} Å\n")
        f.write(f"mean Δr_COM      = {stats_all[0]:.3f} Å\n")
        f.write(f"max Δr_COM       = {stats_all[1]:.3f} Å\n")
        f.write(f"95th percentile  = {stats_all[2]:.3f} Å\n")
        f.write(f"total Δr_COM pairs = {stats_all[3]}\n\n")
        f.write("[Persist-qualified stable F₂ only]\n")
        f.write(f"mean Δr_COM      = {stats_stable[0]:.3f} Å\n")
        f.write(f"max Δr_COM       = {stats_stable[1]:.3f} Å\n")
        f.write(f"95th percentile  = {stats_stable[2]:.3f} Å\n")
        f.write(f"total Δr_COM pairs = {stats_stable[3]}\n")
    print("📝 Saved Δr_COM stats → collect_fig_delta_r_COM_stats.log")

if __name__ == "__main__":
    main()