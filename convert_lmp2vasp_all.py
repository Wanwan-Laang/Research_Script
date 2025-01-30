import os
import dpdata

atomic_species = ['F', 'Be', 'Li']

lmp_files = sorted([f for f in os.listdir() if f.endswith('.lmp')])

for lmp_file in lmp_files:
    try:
        system = dpdata.System(lmp_file, fmt='lammps/lmp', type_map=atomic_species)

        file_number = os.path.splitext(lmp_file)[0]  
        poscar_file = f"POSCAR_{int(file_number):02d}"  

        system.to('vasp/poscar', poscar_file)
        print(f"Saved POSCAR as {poscar_file}")

    except Exception as e:
        print(f"Error processing {lmp_file}: {e}")