import dpdata
import numpy as np

lammpstrj_file = "conf.dump"  
output_poscar = "POSCAR" 

system = dpdata.System(lammpstrj_file, fmt='lammps/dump', type_map=["Zr", "H"])

system.to_vasp_poscar(output_poscar, coord_sys='Cartesian')

print(f"The POSCAR file has been written to {output_poscar}")

