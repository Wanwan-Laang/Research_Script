# parse_energy_from_dump_direct_timestep.py
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

# === main ===
time_steps, ke, pe = read_energy_dump("dump.init", average=False)

plt.figure()
plt.plot(time_steps, ke, label="Kinetic Energy", color='r', linewidth=2)
plt.axvline(x=42600, color='grey', linestyle='dashdot', linewidth=1)
plt.axvline(x=62600, color='grey', linestyle='dashdot', linewidth=1)
plt.xlabel("Timestep")
plt.ylabel("Energy (eV)")
plt.xlim(time_steps[0], time_steps[-1])
#plt.title("Internal Kinetic Energy vs Timestep")
plt.legend()
plt.tight_layout()
plt.savefig("figure-Inner-kinetic_energy.pdf",dpi=1200,transparent=True)


plt.figure()
plt.plot(time_steps, pe, label="Potential Energy", color='b', linewidth=2)
plt.axvline(x=42600, color='grey', linestyle='dashdot', linewidth=1)
plt.axvline(x=62600, color='grey', linestyle='dashdot', linewidth=1)
plt.xlabel("Timestep")
plt.ylabel("Energy (eV)")
plt.xlim(time_steps[0], time_steps[-1])
#plt.title("Internal Potential Energy vs Timestep")
plt.legend()
plt.tight_layout()
plt.savefig("figure-Inner-potential_energy.pdf",dpi=1200,transparent=True)
