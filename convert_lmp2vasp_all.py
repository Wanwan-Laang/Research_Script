import os
import dpdata

atomic_species = ['F', 'Be', 'Li']
atomic_masses = [56, 14, 28]

current_dir = os.getcwd()
lmp_files = [f for f in os.listdir(current_dir) if f.endswith('.lmp')]

for lmp_file in lmp_files:
    try:
        system = dpdata.System(lmp_file, fmt='lammps/lmp', type_map=atomic_species)

        poscar_file = f"POSCAR_{os.path.splitext(lmp_file)[0]}"

        system.to('vasp/poscar', poscar_file)
        print(f"Saved POSCAR to {poscar_file}")

    except Exception as e:
        print(f"Error processing {lmp_file}: {e}")
