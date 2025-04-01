from ase.build import surface
from ase.visualize import view
from ase.io import write

from ase.spacegroup import crystal
bulk = crystal('ZrC', [(0, 0, 0), (0.5, 0.5, 0.5)], spacegroup=225, cellpar=4.68)

# Define surface parameters (Miller index, layers, vacuum size)
millers = (1, 0, 0)  # Miller index for the (110) surface
layers = 8           # Number of atomic layers
vacuum = 15.0        # Vacuum size in Å

# Generate the surface
slab = surface(bulk, millers, layers)
slab.center(vacuum=vacuum, axis=2)

write("POSCAR_ZrC_100_8layers", slab, format="vasp")

print("POSCAR file for ZrC surface generated successfully.")
