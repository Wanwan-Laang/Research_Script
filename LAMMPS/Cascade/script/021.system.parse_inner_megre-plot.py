#!/usr/bin/env python3
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

def read_energy_dump(filename, average=False):
    with open(filename, 'r') as f:
        lines = f.readlines()

    timesteps = []
    ke_list = []
    pe_list = []
    i = 0
    while i < len(lines):
        if lines[i].startswith("ITEM: TIMESTEP"):
            timestep = int(lines[i + 1].strip())
            timesteps.append(timestep)
            i += 2
            while not lines[i].startswith("ITEM: ATOMS"):
                i += 1
            i += 1  # move to first atom line

            ke_total = 0.0
            pe_total = 0.0
            atom_count = 0
            while i < len(lines) and not lines[i].startswith("ITEM:"):
                parts = lines[i].split()
                # 注意：parts[6] 是動能，parts[5] 是勢能
                ke_total += float(parts[6])
                pe_total += float(parts[5])
                atom_count += 1
                i += 1

            if average and atom_count > 0:
                ke_total /= atom_count
                pe_total /= atom_count

            ke_list.append(ke_total)
            pe_list.append(pe_total)
        else:
            i += 1

    return np.array(timesteps), np.array(ke_list), np.array(pe_list)

# 讀檔
time_steps, ke, pe = read_energy_dump("dump.init", average=True)

# 開一張圖
fig, ax1 = plt.subplots(figsize=(8,6))

# 左側 y 軸：動能
ax1.plot(time_steps, ke, 'r-', linewidth=2, label='Kinetic Energy')
ax1.set_xlabel('Timestep')
ax1.set_ylabel('Per Atom Kinetic Energy (eV)', color='r')
ax1.tick_params(axis='y', labelcolor='r')

## 畫一些階段分界線（可選）
##for x in [42600, 62600]:
##    ax1.axvline(x=x, color='grey', linestyle='dashdot', linewidth=1)

# 右側 y 軸：勢能
ax2 = ax1.twinx()
ax2.plot(time_steps, pe, 'b--', linewidth=2, label='Potential Energy')
ax2.set_ylabel('Per Atom Potential Energy (eV)', color='b')
ax2.tick_params(axis='y', labelcolor='b')

# 合併圖例
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right')

plt.title('Per Atom Energy Evolution')
plt.xlim(min(time_steps), max(time_steps))
plt.tight_layout()
plt.savefig("figure-Energy-Kinetic_vs_Potential.pdf", dpi=1200,transparent=True)
#plt.show()
