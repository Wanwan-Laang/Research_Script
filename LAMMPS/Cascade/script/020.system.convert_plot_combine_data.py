#!/usr/bin/env python3
import pandas as pd
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

data = pd.read_csv('./combined_data.csv')
print(data.head())

data.columns = data.columns.str.strip()

fig, ax1 = plt.subplots(figsize=(8,6))

ax1.plot(data['Step'], data['Temp'],    color='red',    label='System Temp',   linewidth=2.0)
#ax1.plot(data['Step'], data['c_ex'],    color='blue',   label='External Temp', linewidth=1.5)
ax1.plot(data['Step'], data['c_in'],    color='green',  label='Internal Temp', linewidth=1.5)
#ax1.plot(data['Step'], data['c_PKAin'], color='purple',    label='PKA Temp',      linewidth=1.5, linestyle=':')

plt.axvline(x=12544, color='grey', linestyle='dashdot', linewidth=1)
plt.axvline(x=22544, color='grey', linestyle='dashdot', linewidth=1)
plt.axvline(x=42544, color='grey', linestyle='dashdot', linewidth=1)
plt.axvline(x=62544, color='grey', linestyle='dashdot', linewidth=1)

ax1.set_xlabel('Step')
ax1.set_ylabel('Temp')
ax1.set_xlim(data['Step'].min(), data['Step'].max())
ax1.legend()
ax1.tick_params(**tick_params)

ax2 = ax1.twiny()
ax2.set_xlim(ax1.get_xlim()) 
def step_to_simtime(x):
    return np.interp(x, data['Step'], data['convert_simTime'])
ax2.set_xticks(ax1.get_xticks())  
ax2.set_xticklabels(np.round(step_to_simtime(ax1.get_xticks()), 2))  
#ax2.set_xlabel('convert_simTime (ps)')
plt.tight_layout()
plt.savefig("fig-sys-Temperature-Evolution.pdf", dpi=1200,transparent=True)

plt.figure(figsize=(8,6))
plt.plot(data['Step'], data['PotEng'], label="Potential Energy", color="red", linewidth=2)
plt.plot(data['Step'], data['TotEng'], label="Total Energy",    color="blue", linewidth=2)
plt.xlim(data['Step'].min(), data['Step'].max())
plt.axvline(x=12544, color='grey', linestyle='dashdot', linewidth=1)
plt.axvline(x=22544, color='grey', linestyle='dashdot', linewidth=1)
plt.axvline(x=42544, color='grey', linestyle='dashdot', linewidth=1)
plt.axvline(x=62544, color='grey', linestyle='dashdot', linewidth=1)

plt.legend()
plt.savefig("fig-sys-Energy-Evolution.pdf", dpi=1200,transparent=True)
