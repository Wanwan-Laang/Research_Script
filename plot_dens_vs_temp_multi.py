#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Flexible Density vs Temperature Plotter
========================================

Supports plotting multiple LAMMPS log files using:
python plot_dens_vs_temp_multi.py -i log1 -l Label1 -i log2 -l Label2 ...


python plot_dens_vs_temp_multi.py \
  -i data_1073K.log -l "1073K ZBL" \
  -i data_1000K.log -l "1000K noZBL" \
  -i data_900K.log -l "900K ZBL" \
  -o dens_vs_temp_comparison.pdf

  Each `-i` must be followed by a `-l`.
"""

import argparse
import numpy as np
import matplotlib.pyplot as plt

def parse_args():
    parser = argparse.ArgumentParser(description="Plot multiple Density vs Temperature curves from LAMMPS logs.")
    parser.add_argument('-i', '--input', action='append', required=True, help='Input log file')
    parser.add_argument('-l', '--label', action='append', required=True, help='Label for the dataset')
    parser.add_argument('-s', '--header-skip', type=int, default=0, help='Number of lines to skip')
    parser.add_argument('-t', '--dt', type=float, default=0.0005, help='Timestep to ps conversion (default: 0.0005)')
    parser.add_argument('-o', '--output', default='figure-dens_vs_temp_multi.pdf', help='Output figure file')
    return parser.parse_args()

def parse_log_lammps(path, header_skip):
    steps, temps, dens = [], [], []
    with open(path) as f:
        lines = f.readlines()[header_skip:]
    for line in lines:
        parts = line.strip().split()
        if len(parts) < 5 or not parts[0].isdigit():
            continue
        try:
            steps.append(int(parts[0]))
            temps.append(float(parts[1]))
            dens.append(float(parts[4]))
        except ValueError:
            continue
    return np.array(steps), np.array(temps), np.array(dens)

def main():
    args = parse_args()
    if len(args.input) != len(args.label):
        raise ValueError("Each input file must have a corresponding label (-i ... -l ... pairs).")

    plt.figure()

    # Color cycle
    color_cycle = [
    'blue',         # 深藍
    'orange',       # 橘
    'green',        # 鮮綠
    'red',          # 紅
    'purple',       # 紫
    'cyan',         # 青藍
    'magenta',      # 品紅
    'brown',        # 棕
    'black',        # 黑
    '#FFD700'       # 金黃
]

    for idx, (log_file, label) in enumerate(zip(args.input, args.label)):
        steps, temps, dens = parse_log_lammps(log_file, args.header_skip)
        color = color_cycle[idx % len(color_cycle)]
        plt.plot(temps, dens, label=label, linewidth=1.5, color=color)

    # Comparison datasets
    comparison_data = {
        "Temp": [0, 81, 300, 450, 700, 730, 750, 850, 1000, 1500, 2000],
        "NPT-Direct": [2.1367,2.1238,None,None,None,None,None,None,None,None,None],
        "Baral": [1.908,2.144, 1.866, 1.84, 1.8, 1.788, 1.757, 1.731, 1.675, 1.597, 1.571],
        "exp_min": [None,2.18, None, None, None, 1.97, 1.95, 1.9, 1.8, None, None],
        "exp_max": [None,2.18, None, None, None, 2.08, 2.05, 2.02, 1.95, None, None]
    }

    comp_temps = np.array(comparison_data["Temp"], dtype=float)
    comp_baral = np.array(comparison_data["Baral"], dtype=float)
    comp_exp_min = np.array(comparison_data["exp_min"], dtype=float)
    comp_exp_max = np.array(comparison_data["exp_max"], dtype=float)
    comp_npt = np.array(comparison_data["NPT-Direct"], dtype=float)

    valid_baral = ~np.isnan(comp_baral)
    valid_exp_min = ~np.isnan(comp_exp_min)
    valid_exp_max = ~np.isnan(comp_exp_max)
    valid_npt = ~np.isnan(comp_npt)

    plt.scatter(comp_temps[valid_baral], comp_baral[valid_baral], color="red", marker="o", label="Baral et al. 2021", s=75, zorder=10)
    plt.scatter(comp_temps[valid_exp_min], comp_exp_min[valid_exp_min], color="green", marker="s", label="Exp Min (Seiler 1993)", s=75, zorder=10)
    plt.scatter(comp_temps[valid_exp_max], comp_exp_max[valid_exp_max], color="orange", marker="^", label="Exp Max (Seiler 1993)", s=75, zorder=10)
    plt.scatter(comp_temps[valid_npt], comp_npt[valid_npt], color="purple", marker="d", label="Our NPT-Direct", s=75, zorder=10)

    # Plot formatting
    plt.xlabel("Temperature (K)", fontsize=14, fontweight='bold')
    plt.ylabel("Density (g/cm³)", fontsize=14, fontweight='bold')
    plt.grid(True, linestyle='--', linewidth=0.5)
    plt.legend(fontsize=12, loc='best', frameon=False)
    plt.tick_params(axis='both', which='major', labelsize=12, direction='in', length=6, width=1, top=True, right=True)
    plt.tick_params(axis='both', which='minor', labelsize=10, direction='in', length=3, width=0.5, top=True, right=True)
    plt.tight_layout()
    plt.savefig(args.output, dpi=1200, bbox_inches='tight', transparent=True)
    plt.close()

if __name__ == "__main__":
    main()