#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LAMMPS Log Plotting Tool (Enhanced)
====================================

支持欄位：
Step, Temp, Press, Volume, Density, PotEng, KinEng, TotEng

CLI Usage Examples:
-------------------
1. Plot all quantities (Temperature, Pressure, Volume, Density) in a single figure:
   python3 plot_log.py  -t 0.0005

2. Plot only Temperature and Pressure (separate figures):
   python3 plot_log.py  -a temp dens pe ke --ps

3. Plot all quantities and add a log(step) scale version:
   python3 plot_log.py  -l 

4. 我常用的指令： 
    python3 plot_log.py  -a temp dens pe ke --ps

    Arguments:
----------
-i / --input         : Input log file (default: data.log)
-s / --header-skip   : Number of header lines to skip (default: 0)
-t / --dt            : Timestep to ps conversion factor (default: 0.0005)
-o / --output        : Output filename for full time evolution plot
-l / --plot-log      : Enable log-scale plot of step
-L / --step-output   : Output filename for log(step) plot
-a / --appear        : Choose specific quantities to plot separately (temp, press, vol, dens)
--ps                 : Use physical time (ps) instead of step as X-axis

"""

import argparse
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm

def parse_args():
    parser = argparse.ArgumentParser(description="繪製 LAMMPS log 資料的時間演化圖")
    parser.add_argument("-i", "--input", default="data.log", help="LAMMPS log 檔案")
    parser.add_argument("-s", "--header-skip", type=int, default=0, help="跳過 header 行數")
    parser.add_argument("-t", "--dt", type=float, default=0.0005, help="每一步對應的物理時間 (ps)")
    parser.add_argument("-o", "--output", default="fig_evolution_time.pdf", help="總圖輸出檔名")
    parser.add_argument("-l", "--plot-log", action="store_true", help="是否畫 log(step) 圖")
    parser.add_argument("-L", "--step-output", default="fig_evolution_step_log.pdf", help="log 圖輸出檔名")
    parser.add_argument("-a", "--appear", nargs="+", choices=["temp", "press", "vol", "dens", "pe", "ke", "etot"],
                        help="選擇繪製哪些欄位（單獨成圖）")
    parser.add_argument("--ps", action="store_true", help="橫軸使用時間 (ps) 而非 step")
    return parser.parse_args()

def parse_log_lammps(path, header_skip):
    steps, temps, press, vols, dens, pes, kes, etots = [], [], [], [], [], [], [], []
    with open(path) as f:
        lines = f.readlines()[header_skip:]
    for line in lines:
        parts = line.strip().split()
        if len(parts) < 8 or not parts[0].isdigit():
            continue
        try:
            steps.append(int(parts[0]))
            temps.append(float(parts[1]))
            press.append(float(parts[2]))
            vols.append(float(parts[3]))
            dens.append(float(parts[4]))
            pes.append(float(parts[5]))
            kes.append(float(parts[6]))
            etots.append(float(parts[7]))
        except ValueError:
            continue
    return (np.array(steps), np.array(temps), np.array(press),
            np.array(vols), np.array(dens), np.array(pes),
            np.array(kes), np.array(etots))

def plot_single(fig_name, x, y, xlabel, ylabel, title, color):
    plt.figure()
    plt.plot(x, y, color=color)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xlim(x[0], x[-1])
    plt.title(title)
    plt.grid(True)
    plt.savefig(fig_name, dpi=900, bbox_inches='tight')
    plt.close()

def plot_step_log_evolution(steps, data_map, out_png, color_map):
    fig, axs = plt.subplots(2, 4, figsize=(24, 8), constrained_layout=True)
    keys = list(data_map.keys())
    for i, key in enumerate(keys):
        row, col = divmod(i, 4)
        y, ylabel = data_map[key]
        axs[row][col].plot(steps, y, color=color_map[key])
        axs[row][col].set_xscale('log')
        axs[row][col].set_xlabel("Step (log)")
        axs[row][col].set_ylabel(ylabel)
        axs[row][col].grid(True)
    plt.suptitle("Log-Step Evolution from LAMMPS log")
    plt.savefig(out_png, dpi=900, bbox_inches='tight')
    plt.close(fig)

if __name__ == "__main__":
    args = parse_args()
    steps, temps, press, vols, dens, pes, kes, etots = parse_log_lammps(args.input, args.header_skip)

    if args.ps:
        x = steps * args.dt
        x_label = "Time (ps)"
    else:
        x = steps
        x_label = "Step"

    all_keys = ["temp", "press", "vol", "dens", "pe", "ke", "etot"]
    data_map = {
        "temp":  (temps, "Temperature (K)"),
        "press": (press, "Pressure (bar)"),
        "vol":   (vols, "Volume"),
        "dens":  (dens, "Density"),
        "pe":    (pes, "Potential Energy"),
        "ke":    (kes, "Kinetic Energy"),
        "etot":  (etots, "Total Energy")
    }

    # 自動分配彩虹色
    cmap = cm.get_cmap("rainbow", len(all_keys))
    color_map = {key: cmap(i) for i, key in enumerate(all_keys)}

    keys_to_plot = args.appear if args.appear else all_keys

    for key in keys_to_plot:
        y, ylabel = data_map[key]
        plot_single(f"fig_{key}_evolution.pdf", x, y, x_label, ylabel, f"{ylabel} vs {x_label}", color_map[key])

    fig, axs = plt.subplots(2, 4, figsize=(24, 8), constrained_layout=True)
    for i, key in enumerate(keys_to_plot):
        row, col = divmod(i, 4)
        y, ylabel = data_map[key]
        axs[row][col].plot(x, y, color=color_map[key])
        axs[row][col].set_xlabel(x_label)
        axs[row][col].set_ylabel(ylabel)
        axs[row][col].grid(True)
    plt.suptitle("Time Evolution from LAMMPS log")
    plt.savefig(args.output, dpi=900, bbox_inches='tight')
    plt.close(fig)

    if args.plot_log:
        plot_step_log_evolution(steps, {key: data_map[key] for key in keys_to_plot}, args.step_output, color_map)
