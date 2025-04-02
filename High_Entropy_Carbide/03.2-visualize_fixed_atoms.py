from ase.io import read
import matplotlib.pyplot as plt

# read Selective Dynamics 的 POSCAR
atoms = read("POSCAR_FIX.vasp")

# find the indices of the fixed atoms
fix_flags = atoms.constraints[0].get_indices() if atoms.constraints else []

positions = atoms.get_positions()
x_coords = positions[:, 0]
y_coords = positions[:, 1]
z_coords = positions[:, 2]

colors = ['red' if i in fix_flags else 'blue' for i in range(len(atoms))]

fig, axs = plt.subplots(1, 3, figsize=(15, 4))

# z vs atom index
axs[0].scatter(range(len(z_coords)), z_coords, c=colors)
axs[0].set_xlabel("Atom index")
axs[0].set_ylabel("z (Å)")
axs[0].set_title("z vs Atom Index")

# z vs x
axs[1].scatter(x_coords, z_coords, c=colors)
axs[1].set_xlabel("x (Å)")
axs[1].set_ylabel("z (Å)")
axs[1].set_title("z-x Plane")

# z vs y
axs[2].scatter(y_coords, z_coords, c=colors)
axs[2].set_xlabel("y (Å)")
axs[2].set_ylabel("z (Å)")
axs[2].set_title("z-y Plane")

plt.tight_layout()
plt.savefig("fix_atoms_summary.png", dpi=1200)

