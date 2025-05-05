#!/usr/bin/env python3
"""
stable_pair_detector.py: Detect “persistent” atom–pair connections

本腳本偵測指定 atom-pair（例如 F–F 或 F–Li）跨多幀持續出現嘅情況，
只對指定元素對做分析，其他元素唔會讀取。
並將結果輸出為 CSV 格式。

Example:
  python stable_pair_detector.py \
    --dump dump.sum.interior \
    --types 1:F,2:Be,3:Li \
    --cutoff F-F:3.3 \
    --skip 10 \
    --select 0-1000 \
    --xaxis frame \
    --persist 5

Arguments:
  --dump      LAMMPS dump 檔案，需含 “ITEM: ATOMS …” 欄位標頭
  --types     typeID:symbol 映射，例如 1:F,2:Be,3:Li
  --cutoff    單一 atom-pair 截距，格式 SYMBOL-SYMBOL:距離（Å），例如 F-F:3.3
  --skip      每隔 N 幀處理一次（預設 1：處理所有幀）
  --select    篩選要分析嘅 x 軸值（frame index 或 timestep），支援 100-200 或 500,1000
  --xaxis     “timestep” 或 “frame”（預設 frame），決定橫軸用 timestep 定還是用 frame index
  --persist   最少連續出現幾多幀先算“持續”（預設 1）

Outputs:
  stable_pairs.csv   atom1,atom2,max_consecutive_frames
"""

import argparse
from collections import defaultdict, deque
import numpy as np
from scipy.spatial import cKDTree

def parse_args():
    p = argparse.ArgumentParser(
        description="偵測連續出現 ≥N 幀嘅 atom-pair（persistent pairs）"
    )
    p.add_argument("--dump",    required=True,
                   help="LAMMPS dump 檔案，需含 “ITEM: ATOMS …”")
    p.add_argument("--types",   required=True,
                   help="typeID:symbol 映射，例如 1:F,2:Be,3:Li")
    p.add_argument("--cutoff",  required=True,
                   help="單一 atom-pair 截距，格式 SYMBOL-SYMBOL:距離，例如 F-F:3.3")
    p.add_argument("--skip",    type=int, default=1,
                   help="每隔 N 幀處理一次（預設 1：全部帧）")
    p.add_argument("--select",  default=None,
                   help="篩選要分析嘅 x 軸值，支援 100-200,500 之類")
    p.add_argument("--xaxis",   choices=["timestep","frame"], default="frame",
                   help="橫軸用 ‘timestep’ 定 ‘frame’ （預設 frame）")
    p.add_argument("--persist", type=int, default=1,
                   help="最少連續出現幾多幀先算持續（預設 1）")
    return p.parse_args()

def parse_types(txt):
    """把 '1:F,2:Be,3:Li' → {'F':1,'Be':2,'Li':3}"""
    d = {}
    for token in txt.split(","):
        tid, sym = token.split(":")
        d[sym] = int(tid)
    return d

def parse_cutoff(txt):
    """把 'F-F:3.3' → ('F','F',3.3)"""
    pair, dist = txt.split(":")
    a, b = pair.split("-")
    return a, b, float(dist)

def parse_select(txt):
    """把 '100-200,500' → [(100,200),(500,500)]"""
    rng = []
    for seg in txt.split(","):
        if "-" in seg:
            a, b = seg.split("-")
            rng.append((int(a), int(b)))
        else:
            v = int(seg)
            rng.append((v, v))
    return rng

def in_selection(x, ranges):
    """檢查 x 是否落喺任一範圍內"""
    return any(a <= x <= b for (a, b) in ranges)

def parse_lammps_dump(fname):
    """
    讀 LAMMPS dump，回傳 list of (step, types_array, coords_array)
    自動 detect 欄位順序，支援任意 order 嘅 id/type/xu/yu/zu
    """
    frames = []
    with open(fname) as f:
        while True:
            line = f.readline()
            if not line:
                break
            if line.startswith("ITEM: TIMESTEP"):
                step = int(f.readline().strip())
                # 跳到 ITEM: ATOMS header
                while True:
                    hdr = f.readline()
                    if not hdr:
                        return frames
                    if hdr.startswith("ITEM: ATOMS"):
                        cols = hdr.strip().split()[2:]
                        idx = {c: i for i, c in enumerate(cols)}
                        i_type = idx["type"]
                        i_x    = idx["xu"]
                        i_y    = idx["yu"]
                        i_z    = idx["zu"]
                        break
                types, coords = [], []
                # 讀 atom lines
                while True:
                    pos = f.tell()
                    l = f.readline()
                    if not l or l.startswith("ITEM:"):
                        f.seek(pos)
                        break
                    sp = l.split()
                    types.append(int(sp[i_type]))
                    coords.append((float(sp[i_x]),
                                   float(sp[i_y]),
                                   float(sp[i_z])))
                frames.append((step,
                               np.array(types, dtype=int),
                               np.array(coords, dtype=float)))
    return frames

def detect_persistent_pairs(frames, sym2id, cutoff, skip, select_ranges, use_frame, persist_thres):
    """
    只對指定 atom-pair（如 F-F 或 F-Li）做距離 ≤ cutoff 偵測，
    先過濾出相關元素嘅原子，其他元素完全忽略。
    """
    symA, symB, cut = cutoff
    idA, idB = sym2id[symA], sym2id[symB]
    lifetimes = defaultdict(int)
    stable    = {}

    for idx, (step, types, coords) in enumerate(frames):
        if idx % skip != 0:
            continue
        xval = idx if use_frame else step
        if select_ranges and not in_selection(xval, select_ranges):
            continue

        # 只保留 symA 同 symB 嘅原子
        rel_idx = np.where((types == idA) | (types == idB))[0]
        current = set()
        if rel_idx.size >= 2:
            rel_types  = types[rel_idx]
            rel_coords = coords[rel_idx]

            if idA == idB:
                # same-type
                tree = cKDTree(rel_coords)
                for i, j in tree.query_pairs(r=cut):
                    a, b = rel_idx[i], rel_idx[j]
                    current.add(tuple(sorted((a, b))))
            else:
                # cross-type
                maskA = np.where(rel_types == idA)[0]
                maskB = np.where(rel_types == idB)[0]
                ptsA  = rel_coords[maskA]
                ptsB  = rel_coords[maskB]
                treeB = cKDTree(ptsB)
                for ia, pa in enumerate(ptsA):
                    u = rel_idx[maskA[ia]]
                    for jb in treeB.query_ball_point(pa, cut):
                        v = rel_idx[maskB[jb]]
                        current.add(tuple(sorted((u, v))))

        # 更新 lifetimes，同 flush 消失嘅 pairs
        for pair in list(lifetimes):
            if pair not in current:
                if lifetimes[pair] >= persist_thres:
                    stable[pair] = lifetimes[pair]
                del lifetimes[pair]
        for pair in current:
            lifetimes[pair] += 1

    # 最後一次 flush
    for pair, cnt in lifetimes.items():
        if cnt >= persist_thres:
            stable[pair] = cnt

    return stable

def main():
    args = parse_args()
    sym2id       = parse_types(args.types)
    cutoff       = parse_cutoff(args.cutoff)
    select_ranges= parse_select(args.select) if args.select else None
    use_frame    = (args.xaxis == "frame")

    frames = parse_lammps_dump(args.dump)
    if not frames:
        print("⚠️ 無讀到任何 frame，請檢查 dump 檔案。")
        return

    stable = detect_persistent_pairs(
        frames, sym2id, cutoff,
        args.skip, select_ranges,
        use_frame, args.persist
    )

    out_file = "stable_pairs.csv"
    with open(out_file, "w") as fw:
        fw.write("atom1,atom2,max_consecutive_frames\n")
        for (i, j), cnt in sorted(stable.items()):
            fw.write(f"{i},{j},{cnt}\n")
    print(f"偵測到 {len(stable)} 組穩定對，已存到 {out_file}")

if __name__ == "__main__":
    main()
