#!/usr/bin/env python3
# ------------------------------------------------------------
#  C Adsorption Environment Analysis Script  (v2.3, 2025-04-24)
#
#  ➊ 讀取 bridge/hollow/ontop/*/CONTCAR
#  ➋ 將最後一個原子視為吸附 C
#  ➌ 以 cutoff Å 同時用
#        • ASE NeighborList
#        • 直接歐幾里得距離 (cdist)
#     判定鄰居
#  ➍ 各方法：
#        • 輸出每元素鄰居計數至 CSV
#        • 畫散點圖（每個元素加固定 y-offset 避免重疊）
#  ➎ 生成 summary.csv，比較兩方法結果並標示是否一致
# ------------------------------------------------------------

import os, glob, argparse, csv
from collections import Counter

import numpy as np
import matplotlib.pyplot as plt
from ase.io import read
from ase.neighborlist import NeighborList

# ─────────────────────────  Plot style  ──────────────────────
plt.rcParams.update({
    "axes.labelweight": "bold",
    "axes.linewidth":   2,
    "axes.titlesize":   15,
    "axes.labelsize":   15,
    "legend.fontsize":  15,
    "xtick.labelsize":  13,
    "ytick.labelsize":  13,
})

# ────────────────  全域設定  ────────────────
TARGET_ELEMENTS = ["Nb", "Hf", "Ti", "Ta", "Zr", "C"]
GROUPS          = ["bridge", "hollow", "ontop"]
COLOR_MAP       = {"Nb": "blue", "Hf": "orange", "Ti": "green",
                   "Ta": "red",  "Zr": "purple", "C": "gray"}

# ──────────────  CLI  ──────────────
def parse_args():
    p = argparse.ArgumentParser("Analyze C adsorption environments (NL vs cdist)")
    p.add_argument("--cutoff", type=float, default=3.0,
                   help="Cutoff distance (Å) [default: 3.0]")
    p.add_argument("--no-plot", action="store_true", help="Disable plotting")
    return p.parse_args()

# ──────────────  畫散點圖（加入固定 y 偏移）──────────────
def scatter_plot(env_list, filename, cutoff):
    if not env_list:
        return
    plt.figure(figsize=(12, 6))

    OFFSET_MAP = {"Nb": 0.1, "Hf": 0.2, "Ti": 0.3,
                  "Ta": 0.4, "Zr": 0.5, "C": 0.6}

    for el in TARGET_ELEMENTS:
        xs, ys = [], []
        for idx, env in env_list:
            cnt = env[el]
            if cnt > 0:
                xs.append(idx)
                ys.append(cnt + OFFSET_MAP[el])  # ✅ 加固定 offset 避免重疊
        if xs:
            plt.scatter(xs, ys, color=COLOR_MAP[el], label=el, s=60, alpha=0.85, edgecolors='k')

    plt.xlabel("Configuration Index")
    plt.ylabel(f"Neighbor Count + offset (cutoff = {cutoff} Å)")
    plt.title(os.path.splitext(filename)[0].replace("_", " "))
    plt.xlim(0, max(idx for idx, _ in env_list) + 1)
    plt.legend()
    plt.tight_layout()
    plt.savefig(filename, dpi=900, bbox_inches="tight")
    plt.close()

# ──────────────  主程式  ──────────────
def main():
    args   = parse_args()
    cutoff = args.cutoff

    envs_nl, envs_dist = [], []
    rows_nl, rows_dist, rows_sum = [], [], []
    conf_idx = 1

    for grp in GROUPS:
        for folder in sorted(glob.glob(f"{grp}/[0-9][0-9]")):
            contcar = os.path.join(folder, "CONTCAR")
            if not os.path.exists(contcar):
                continue

            try:
                atoms = read(contcar, format="vasp")
            except Exception as e:
                print(f"Skip {folder}: {e}")
                continue

            if atoms[-1].symbol != "C":
                print(f"❌ Last atom not C in {folder}")
                continue

            c_idx = len(atoms) - 1
            c_pos = atoms[c_idx].position

            # ── NeighborList ──
            nl = NeighborList([cutoff / 2.0] * len(atoms),
                              self_interaction=False, bothways=True)
            nl.update(atoms)
            idx_nl, _ = nl.get_neighbors(c_idx)
            set_nl    = set(idx_nl)
            env_nl_full = {el: 0 for el in TARGET_ELEMENTS}
            env_nl_full.update(Counter(atoms[i].symbol for i in set_nl))
            envs_nl.append((conf_idx, env_nl_full))

            # ── cdist ──
            dists    = np.linalg.norm(atoms.get_positions() - c_pos, axis=1)
            idx_dist = set(np.where((dists < cutoff) & (dists > 1e-8))[0])
            env_dist_full = {el: 0 for el in TARGET_ELEMENTS}
            env_dist_full.update(Counter(atoms[i].symbol for i in idx_dist))
            envs_dist.append((conf_idx, env_dist_full))

            # ── 個別 CSV 行 ──
            base = dict(Index=conf_idx, Group=grp, Folder=os.path.basename(folder),
                        AddedC_Index=c_idx, AddedC_X=c_pos[0],
                        AddedC_Y=c_pos[1], AddedC_Z=c_pos[2])
            rows_nl  .append(base | {el: env_nl_full [el] for el in TARGET_ELEMENTS})
            rows_dist.append(base | {el: env_dist_full[el] for el in TARGET_ELEMENTS})

            # ── summary 行 ──
            rows_sum.append(base | {
                "NeighborCount_total_NL":    len(set_nl),
                "NeighborCount_total_cdist": len(idx_dist),
                "NL_cdist_match":            int(set_nl == idx_dist),
            })

            # ── log ──
            if set_nl != idx_dist:
                print(f"⚠️  {folder}: NL={len(set_nl)} vs cdist={len(idx_dist)} (mismatch)")
            else:
                print(f"✅  {folder}: match={len(set_nl)}")

            conf_idx += 1

    # ──────────  寫 CSV  ──────────
    def write_csv(path, rows):
        if rows:
            with open(path, "w", newline="") as f:
                csv.DictWriter(f, fieldnames=rows[0].keys()).writeheader()
                csv.DictWriter(f, fieldnames=rows[0].keys()).writerows(rows)
            print(f"CSV saved: {path}")

    write_csv("C_adsorption_environment_NL.csv",      rows_nl)
    write_csv("C_adsorption_environment_cdist.csv",  rows_dist)
    write_csv("C_adsorption_environment_summary.csv", rows_sum)

    # ──────────  繪圖  ──────────
    if not args.no_plot:
        scatter_plot(envs_nl,   "C_adsorption_environment_scatter_NL.pdf",   cutoff)
        scatter_plot(envs_dist, "C_adsorption_environment_scatter_cdist.pdf", cutoff)
        print("Plots saved: *_NL.pdf & *_cdist.pdf")

if __name__ == "__main__":
    main()