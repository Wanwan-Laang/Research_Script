#!/usr/bin/env python3
# parse_PKA_energy_dissipation.py
# Parse kinetic & potential energy of PKA over time from LAMMPS dump
# add PKA potential energy and kinetic energy, optional reset time

import matplotlib.pyplot as plt
import numpy as np
plt.rcParams.update({
    'font.weight': 'bold',
    'axes.labelweight': 'bold',
    'axes.linewidth': 2,
    'axes.titlesize': 12,
    'axes.labelsize': 12,
    'legend.fontsize': 13,
    'xtick.labelsize': 13,
    'ytick.labelsize': 13
})
tick_params = {'direction': 'in', 'width': 2, 'length': 6}

def read_energy_dump(filename, timestep_fs=0.01, reset_time=False):
    """
    读取 LAMMPS dump 文件中 PKA 的能量数据。
    参数:
      filename    dump 文件路径
      timestep_fs 每步对应的 fs（默认为 0.01 fs）
      reset_time  是否将第一帧的时间视为 0
    返回:
      time_ps (ps), ke (eV), pe (eV)
    """
    with open(filename, 'r') as f:
        lines = f.readlines()

    timesteps = []
    ke = []
    pe = []
    i = 0
    while i < len(lines):
        if lines[i].startswith("ITEM: TIMESTEP"):
            step = int(lines[i+1].strip())
            timesteps.append(step)
            # 找到下一个 ATOMS 块
            while not lines[i].startswith("ITEM: ATOMS"):
                i += 1
            # 取 ATOMS 块里第一行（PKA）里的动能和势能
            atom_line = lines[i+1].split()
            ke.append(float(atom_line[5]))
            pe.append(float(atom_line[6]))
        i += 1

    timesteps = np.array(timesteps)
    time_ps = timesteps * timestep_fs * 0.001  # 转为 ps
    if reset_time:
        time_ps = time_ps - time_ps[0]

    return time_ps, np.array(ke), np.array(pe)

if __name__ == "__main__":
    # 例：从 dump.PKA.init 读取，重置时间为 0
    time, ke, pe = read_energy_dump(
        filename="dump.PKA.init",
        timestep_fs=0.01,
        reset_time=True   # 改成 False 则保留原始时间
    )

    #plt.figure(figsize=(4, 3))
    plt.figure(figsize=(6,4))
    plt.plot(time, ke, label="PKA Kinetic Energy", color='r', linewidth=2)
    plt.plot(time, pe, label="PKA Potential Energy", color='b', linewidth=2)
    plt.xlabel("Time (ps)")
    plt.ylabel("Energy (eV)")
    plt.xlim(time.min(), time.max())
    #plt.title("PKA Energy Dissipation")
    plt.legend()
    plt.tight_layout()
    plt.savefig("fig-PKA_energy_dissipation.pdf", dpi=1200, transparent=True)
    plt.show()