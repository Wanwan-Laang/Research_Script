
# parse_PKA_energy_dissipation.py
# Parse kinetic & potential energy of PKA over time from LAMMPS dump

import matplotlib.pyplot as plt
import numpy as np

def read_energy_dump(filename, timestep_fs=0.01):
    with open(filename, 'r') as f:
        lines = f.readlines()

    timesteps = []
    ke = []
    pe = []
    i = 0
    while i < len(lines):
        if lines[i].startswith("ITEM: TIMESTEP"):
            timestep = int(lines[i + 1].strip())
            timesteps.append(timestep)
            while not lines[i].startswith("ITEM: ATOMS"):
                i += 1
            atom_line = lines[i + 1].strip().split()
            ke.append(float(atom_line[5]))
            pe.append(float(atom_line[6]))
        i += 1

    time_ps = np.array(timesteps) * timestep_fs * 0.001
    return time_ps, np.array(ke), np.array(pe)

# Change this to your actual file
time, ke, pe = read_energy_dump("dump.PKA.final")

plt.plot(time, ke, label="Kinetic Energy")
plt.plot(time, pe, label="Potential Energy")
plt.xlabel("Time (ps)")
plt.ylabel("Energy (eV)")
plt.title("PKA Energy Dissipation Over Time")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

