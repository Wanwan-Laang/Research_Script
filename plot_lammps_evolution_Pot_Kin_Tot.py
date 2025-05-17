#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
import argparse

def parse_args():
    p = argparse.ArgumentParser(
        description="Plot PotEng, KinEng and TotEng from a LAMMPS log file."
    )
    p.add_argument(
        "-i", "--input", default="data.log",
        help="LAMMPS log file to parse"
    )
    p.add_argument(
        "-s", "--header-skip", type=int, default=0,
        help="Number of lines to skip at the top of the file"
    )
    p.add_argument(
        "-t", "--dt", type=float, default=0.0005,
        help="Time per step in ps (default: 0.0005 ps)"
    )
    p.add_argument(
        "-o", "--output", default="fig_energy_evolution.pdf",
        help="Filename for the time‐evolution plot"
    )
    p.add_argument(
        "-l", "--plot-log", action="store_true",
        help="If set, also plot vs. log(step)"
    )
    p.add_argument(
        "-L", "--step-output", default="fig_energy_evolution_step_log.pdf",
        help="Filename for the log(step) plot (requires -l)"
    )
    return p.parse_args()

def parse_log(path, header_skip):
    steps, poteng, kineng, toteng = [], [], [], []
    with open(path) as f:
        lines = f.readlines()[header_skip:]
    for line in lines:
        parts = line.strip().split()
        if not parts or not parts[0].isdigit():
            continue
        # 格式: Step Temp Press Volume Density PotEng KinEng TotEng
        try:
            steps.append(int(parts[0]))
            poteng.append(float(parts[5]))
            kineng.append(float(parts[6]))
            toteng.append(float(parts[7]))
        except (IndexError, ValueError):
            continue
    return (np.array(steps),
            np.array(poteng),
            np.array(kineng),
            np.array(toteng))

def plot_time(steps, pot, kin, tot, dt, out_png):
    times = steps * dt
    fig, ax = plt.subplots(figsize=(5, 4), constrained_layout=True)
    ax.plot(times, pot, label="PotEng", color='red')
    ax.plot(times, kin, label="KinEng", color='blue')
    ax.plot(times, tot, label="TotEng", color='green')
    ax.set_xlabel("Time (ps)")
    ax.set_ylabel("Energy")
    ax.legend()
    ax.grid(True)
    plt.title("Energy vs. Time")
    plt.savefig(out_png, dpi=900, bbox_inches="tight")
    plt.close(fig)
    print(f"✅ Saved time‐evolution plot: {out_png}")

def plot_step_log(steps, pot, kin, tot, out_png):
    fig, ax = plt.subplots(figsize=(5, 4), constrained_layout=True)
    ax.plot(steps, pot, label="PotEng", color='red')
    ax.plot(steps, kin, label="KinEng", color='blue')
    ax.plot(steps, tot, label="TotEng", color='green')
    ax.set_xscale("log")
    ax.set_xlabel("Step (log scale)")
    ax.set_ylabel("Energy")
    ax.legend()
    ax.grid(True)
    plt.title("Energy vs. log(Step)")
    plt.savefig(out_png, dpi=900, bbox_inches="tight")
    plt.close(fig)
    print(f"✅ Saved log‐step plot: {out_png}")

if __name__ == "__main__":
    args = parse_args()
    steps, pot, kin, tot = parse_log(args.input, args.header_skip)
    if len(steps) == 0:
        print("❌ No data parsed. Check your header-skip or log format.")
        exit(1)

    # 1) 绘制时间演化
    plot_time(steps, pot, kin, tot, args.dt, args.output)

    # 2) 如果指定 -l，再绘制 log(step) 图
    if args.plot_log:
        plot_step_log(steps, pot, kin, tot, args.step_output)