#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
import argparse

def parse_args():
    p = argparse.ArgumentParser(
        description="從 LAMMPS log 中繪製溫度/壓力/體積/密度演化曲線，並可選擇額外畫 log(step) 圖"
    )
    p.add_argument("-i", "--input",   default="log.lammps",
                   help="LAMMPS log 檔案")
    p.add_argument("-s", "--header-skip", type=int, default=0,
                   help="跳過幾行標頭（header）")
    p.add_argument("-t", "--dt",     type=float, default=0.0005,
                   help="每一步對應的真實時間 (ps)，預設 0.0005 ps")
    p.add_argument("-o", "--output",  default="evolution_time.pdf",
                   help="輸出時間演化圖的檔名")
    p.add_argument("-l", "--plot-log", action="store_true",
                   help="若指定，額外畫以步數為 X 軸、X 軸用對數刻度的圖")
    p.add_argument("-L", "--step-output", default="evolution_step_log.pdf",
                   help="輸出步數 log 圖的檔名 (需搭配 -l)")
    return p.parse_args()

def parse_log_lammps(path, header_skip):
    steps, temps, press, vols, dens = [], [], [], [], []
    with open(path) as f:
        lines = f.readlines()[header_skip:]
    for line in lines:
        parts = line.strip().split()
        if not parts or not parts[0].isdigit(): continue
        try:
            steps.append(int(parts[0]))
            temps.append(float(parts[1]))
            press.append(float(parts[2]))
            vols.append(float(parts[3]))
            dens.append(float(parts[4]))
        except ValueError:
            continue
    return (np.array(steps), 
            np.array(temps), 
            np.array(press), 
            np.array(vols), 
            np.array(dens))

def plot_time_evolution(steps, temps, press, vols, dens, dt, out_png):
    times = steps * dt  # ps
    fig, axs = plt.subplots(1, 4, figsize=(20, 4), constrained_layout=True)

    axs[0].plot(times, temps, color='crimson')
    axs[0].set_xlabel("Time (ps)")
    axs[0].set_ylabel("Temperature (K)")
    axs[0].grid(True)

    axs[1].plot(times, press, color='blue')
    axs[1].set_xlabel("Time (ps)")
    axs[1].set_ylabel("Pressure")
    axs[1].grid(True)

    axs[2].plot(times, vols, color='green')
    axs[2].set_xlabel("Time (ps)")
    axs[2].set_ylabel("Volume")
    axs[2].grid(True)

    axs[3].plot(times, dens, color='orange')
    axs[3].set_xlabel("Time (ps)")
    axs[3].set_ylabel("Density")
    axs[3].grid(True)

    plt.suptitle("Time Evolution from LAMMPS log")
    plt.savefig(out_png, dpi=900, bbox_inches='tight')
    plt.close(fig)

def plot_step_log_evolution(steps, temps, press, vols, dens, out_png):
    fig, axs = plt.subplots(1, 4, figsize=(20, 4), constrained_layout=True)

    axs[0].plot(steps, temps, color='crimson')
    axs[0].set_xscale('log')
    axs[0].set_xlabel("Step (log)")
    axs[0].set_ylabel("Temperature (K)")
    axs[0].grid(True)

    axs[1].plot(steps, press, color='blue')
    axs[1].set_xscale('log')
    axs[1].set_xlabel("Step (log)")
    axs[1].set_ylabel("Pressure")
    axs[1].grid(True)

    axs[2].plot(steps, vols, color='green')
    axs[2].set_xscale('log')
    axs[2].set_xlabel("Step (log)")
    axs[2].set_ylabel("Volume")
    axs[2].grid(True)

    axs[3].plot(steps, dens, color='orange')
    axs[3].set_xscale('log')
    axs[3].set_xlabel("Step (log)")
    axs[3].set_ylabel("Density")
    axs[3].grid(True)

    plt.suptitle("Log-Step Evolution from LAMMPS log")
    plt.savefig(out_png, dpi=900, bbox_inches='tight')
    plt.close(fig)

if __name__ == "__main__":
    args = parse_args()
    steps, temps, press, vols, dens = parse_log_lammps(args.input, args.header_skip)
    plot_time_evolution(steps, temps, press, vols, dens, args.dt, args.output)
    if args.plot_log:
        plot_step_log_evolution(steps, temps, press, vols, dens, args.step_output)