from ase.io import read, write
from ase.neighborlist import neighbor_list
from ase.atom import Atom
import numpy as np
import os
import matplotlib.pyplot as plt
from itertools import combinations

# ====== Step 1: Load structure ======
atoms = read("02.fix-slab-structure/CONTCAR_FIX.vasp")
positions = atoms.get_positions()
z_coords = positions[:, 2]

z_highest = np.max(z_coords)
z_lowest = z_highest - 1.0
z_set = z_highest + 2.0

top_layer_indices = [i for i, z in enumerate(z_coords) if z_lowest < z <= z_highest]
top_layer_positions = positions[top_layer_indices]
top_array = np.array(top_layer_positions)

# ====== Step 2: Ontop and Bridge Sites ======
ontop_sites = [(pos[0], pos[1], z_set) for pos in top_array]

cutoff = 3.0  # neighbor cutoff
i_idx, j_idx, _ = neighbor_list('ijS', atoms, cutoff)

bridge_pairs = set()
top_layer_set = set(top_layer_indices)
for i, j in zip(i_idx, j_idx):
    if i in top_layer_set and j in top_layer_set and i < j:
        bridge_pairs.add((i, j))

bridge_sites = []
for i, j in bridge_pairs:
    xi, yi = positions[i][:2]
    xj, yj = positions[j][:2]
    xm, ym = (xi + xj) / 2, (yi + yj) / 2
    bridge_sites.append((xm, ym, z_set))

# ====== Step 3: Hollow Sites via 4-atom clusters with geometric filtering ======
hollow_sites = []
tol_angle = 20  # degrees, allowable deviation from 90 degrees
tol_side = 0.4  # angstrom, allowable deviation of opposite sides

for combo in combinations(top_array, 4):
    vecs = [combo[i] - combo[j] for i, j in combinations(range(4), 2)]
    dists = [np.linalg.norm(v) for v in vecs]
    
    if max(dists) < 3.5 and min(dists) > 1.0:
        # Check shape: try to form a quadrilateral (check near-right angles)
        sides = [np.linalg.norm(combo[i] - combo[(i+1)%4]) for i in range(4)]
        diag1 = np.linalg.norm(combo[0] - combo[2])
        diag2 = np.linalg.norm(combo[1] - combo[3])

        # Check side symmetry and diagonals
        if abs(sides[0] - sides[2]) < tol_side and abs(sides[1] - sides[3]) < tol_side and abs(diag1 - diag2) < 2 * tol_side:
            center = np.mean(combo, axis=0)
            hollow_sites.append((center[0], center[1], z_set))

# Deduplicate hollow sites
def deduplicate(sites, tol=0.2):
    unique = []
    for s in sites:
        if all(np.linalg.norm(np.array(s) - np.array(u)) > tol for u in unique):
            unique.append(s)
    return unique

hollow_sites = deduplicate(hollow_sites)

# ====== Step 4: Save structures ======
def write_sites(sites, name):
    folder = f"adsorption_{name}"
    os.makedirs(folder, exist_ok=True)
    for i, site in enumerate(sites):
        new_atoms = atoms.copy()
        new_atoms.append(Atom("C", site))
        write(os.path.join(folder, f"{name}_site_{i}.vasp"), new_atoms, format='vasp')

write_sites(ontop_sites, "ontop")
write_sites(bridge_sites, "bridge")
write_sites(hollow_sites, "hollow")

# ====== Step 5: Visualization ======
fig, axs = plt.subplots(1, 3)
for ax, data, label, color in zip(
    axs,
    [ontop_sites, bridge_sites, hollow_sites],
    ["Ontop", "Bridge", "Hollow"],
    ["green", "red", "blue"]
):
    ax.set_title(label)
    ax.scatter(top_array[:, 0], top_array[:, 1], c="black", label="top layer")
    ax.scatter([x for x, y, z in data], [y for x, y, z in data], c=color, label=label.lower(), s=40)
    ax.set_aspect("equal")
    ax.legend(loc='upper right', fontsize=10)

plt.tight_layout()
plt.savefig("adsorption_sites_preview.png", dpi=1200)

# ====== Step 6: Summary ======
print(f"\n✅ Adsorption sites preview saved as 'adsorption_sites_preview.png'")
print(f"Ontop sites:  {len(ontop_sites)}")
print(f"Bridge sites: {len(bridge_sites)}")
print(f"Hollow sites: {len(hollow_sites)}")

