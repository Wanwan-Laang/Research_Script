
# plot_displacement_vs_time.py
# Plot displacement of PKA (or any atom) over time from LAMMPS dump
# 畫出單顆原子的位移演化圖
import matplotlib.pyplot as plt
import numpy as np

def read_dump_displacement(filename, timestep_fs=0.01):
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    timesteps = []
    positions = []
    i = 0
    while i < len(lines):
        if lines[i].startswith("ITEM: TIMESTEP"):
            timestep = int(lines[i + 1].strip())
            timesteps.append(timestep)
            while not lines[i].startswith("ITEM: ATOMS"):
                i += 1
            atom_line = lines[i + 1].strip().split()
            xu, yu, zu = map(float, atom_line[2:5])
            positions.append((xu, yu, zu))
        i += 1
    
    positions = np.array(positions)
    initial_pos = positions[0]
    displacements = np.linalg.norm(positions - initial_pos, axis=1)
    time_ps = np.array(timesteps) * timestep_fs * 0.001  # fs to ps

    return time_ps, displacements

# Change this to your actual file
time, disp = read_dump_displacement("dump.PKA.final")

plt.plot(time, disp, marker='o')
plt.xlabel("Time (ps)")
plt.ylabel("Displacement (√Ö)")
plt.title("PKA Displacement vs Time")
plt.grid(True)
plt.tight_layout()
plt.show()
