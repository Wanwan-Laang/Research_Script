#!/usr/bin/env python3
"""
cluster_stable_F2_detector.py

Detect “stable” F₂ molecules from OVITO cluster‐list exports.

Usage:
  python cluster_stable_F2_detector.py \
    -p raw-initerior-all \
    -t 2.7 \
    -n 50 \
    [-s 0-100,200]

Arguments:
  -p, --prefix     Filename prefix (e.g. raw-initerior-all)
  -t, --track-dist COM tracking distance threshold (Å), only size=2 clusters
  -n, --persist    Minimum consecutive frames to consider “stable” (default:1)
  -s, --select     (optional) Frames to include, e.g. 0-100,200

Outputs:
  cluster_stable_F2_<persist>.csv  with columns:
    start_frame,end_frame,duration,com_x,com_y,com_z
"""
import os
import re
import argparse
import numpy as np
import pandas as pd

def parse_args():
    p = argparse.ArgumentParser(
        description="Detect stable F₂ from OVITO cluster‐list exports"
    )
    p.add_argument(
        "-p", "--prefix", required=True,
        help="Filename prefix (e.g. raw-initerior-all)"
    )
    p.add_argument(
        "-t", "--track-dist", dest="track_dist", type=float, default=0.5,
        help="COM tracking distance threshold in Å (default: 0.5)"
    )
    p.add_argument(
        "-n", "--persist", type=int, default=1,
        help="Minimum consecutive frames to be stable (default: 1)"
    )
    p.add_argument(
        "-s", "--select", default=None,
        help="Frames to include, e.g. 0-100,200 (optional)"
    )
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
    """
    Search current dir for files starting with prefix+'.'<number>,
    read out size=2 COMs from each, return list of (frame, np.array of COMs).
    """
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

        # extract quoted column names
        cols = None
        with open(fn) as f:
            for L in f:
                if '"' in L:
                    cols = re.findall(r'"([^"]+)"', L)
                    break
        if not cols:
            print(f"⚠️ skip {fn}: no quoted header")
            continue

        df = pd.read_csv(
            fn,
            comment="#",
            delim_whitespace=True,
            header=None,
            names=cols
        )
        sub = df[df["Cluster Size"] == 2]
        com = sub[["Center of Mass.X","Center of Mass.Y","Center of Mass.Z"]].values
        entries.append((frame, com))

    return sorted(entries, key=lambda x: x[0])

def detect_stable_F2(frames_com, track_dist, persist):
    trajs = []
    stable = []
    cut2 = track_dist * track_dist

    for frame, coms in frames_com:
        for t in trajs:
            t['matched'] = False
        used = set()

        # match existing trajectories
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
                best['history'].append((frame, pt.copy()))
                best['last']    = frame
                best['com']     = pt.copy()
                best['matched'] = True
                used.add(i)

        # flush unmatched
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
                        'end_frame':   en,
                        'duration':    dur,
                        'com_x':       c0[0],
                        'com_y':       c0[1],
                        'com_z':       c0[2],
                    })
        trajs = new_trajs

        # start new trajectories
        for i, pt in enumerate(coms):
            if i not in used:
                trajs.append({
                    'last':    frame,
                    'com':     pt.copy(),
                    'history': [(frame, pt.copy())]
                })

    # final flush
    for t in trajs:
        dur = len(t['history'])
        if dur >= persist:
            st = t['history'][0][0]
            en = t['history'][-1][0]
            c0 = t['history'][0][1]
            stable.append({
                'start_frame': st,
                'end_frame':   en,
                'duration':    dur,
                'com_x':       c0[0],
                'com_y':       c0[1],
                'com_z':       c0[2],
            })

    return stable

def main():
    args = parse_args()
    select_ranges = parse_select(args.select) if args.select else None

    frames_com = load_cluster_COMs(args.prefix, select_ranges)
    print(f">>> matched {len(frames_com)} files with prefix “{args.prefix}”")
    for f, coms in frames_com[:5]:
        print(f" frame {f}: got {len(coms)} size-2 clusters")

    stable = detect_stable_F2(frames_com, args.track_dist, args.persist)
    df = pd.DataFrame(stable,
        columns=['start_frame','end_frame','duration','com_x','com_y','com_z'])
    out = f"cluster_stable_F2_{args.persist}.csv"
    df.to_csv(out, index=False)
    print(f"Detected {len(df)} stable F₂ → {out}")

if __name__=="__main__":
    main()