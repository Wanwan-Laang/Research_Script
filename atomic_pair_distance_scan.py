import os
import numpy as np
import dpdata

### **Step 1: 计算 F-Li 逐步缩小的距离，并存入 txt 文件** ###
moving_atom_coords = np.array([8.1038967418, 3.9422009685, 7.8977365798])  # 需要移动的原子
fixed_f_coords = np.array([7.4446380149, 2.3267454550, 6.9173398169])      # 固定的原子

target_distance = 0.4  # 最小目标距离 (Å)
num_steps = 9 

atomic_species = ['F', 'Be', 'Li']

initial_distance = np.linalg.norm(fixed_f_coords - moving_atom_coords)
print(f"🔹 初始 F-Li 距离: {initial_distance:.6f} Å")

distance_steps = np.linspace(initial_distance, target_distance, num_steps)

distance_file = "distance"
with open(distance_file, "w") as f:
    f.write("Step\tLi_x\tLi_y\tLi_z\tDistance\n")
    
    for i, target_dist in enumerate(distance_steps):
        if i == 0:
            new_atom_coords = moving_atom_coords
        else:
            displacement_vector = moving_atom_coords - fixed_f_coords
            unit_vector = displacement_vector / np.linalg.norm(displacement_vector)
            new_atom_coords = fixed_f_coords + unit_vector * target_dist
        
        distance = np.linalg.norm(new_atom_coords - fixed_f_coords)
        f.write(f"{i + 1}\t{new_atom_coords[0]:.10f}\t{new_atom_coords[1]:.10f}\t{new_atom_coords[2]:.10f}\t{distance:.6f}\n")
        print(f"✅ Step {i + 1}: Li position = {new_atom_coords}, Distance = {distance:.6f} Å")

print(f"🎯 结果已保存至: {distance_file}")


### **Step 2: 读取 txt 文件，并修改 LAMMPS 结构** ###
input_filename = "../eq/conf1.lmp"           # 原始 LAMMPS 结构文件
output_dir = "mod_stru"                      # 生成的新结构文件夹
os.makedirs(output_dir, exist_ok=True)

# 读取新的 Li 原子坐标
new_coordinates = []
with open(distance_file, "r") as dist_file:
    lines = dist_file.readlines()[1:]       # 跳过表头
    for line in lines:
        parts = line.strip().split()
        new_coordinates.append([float(parts[1]), float(parts[2]), float(parts[3])])

# 读取 LAMMPS 原始文件
with open(input_filename, "r") as infile:
    original_lines = infile.readlines()

# 自动查找需要修改的 Li 原子所在行
line_to_modify = None
for i, line in enumerate(original_lines, start=1):
    parts = line.strip().split()
    if len(parts) >= 5:
        try:
            x, y, z = float(parts[2]), float(parts[3]), float(parts[4])
            if all(abs(xyz1 - xyz2) < 1e-6 for xyz1, xyz2 in zip([x, y, z], moving_atom_coords)):
                line_to_modify = i
                break
        except ValueError:
            continue

if line_to_modify is None:
    raise ValueError(f"❌ 未在 {input_filename} 中找到坐标 {moving_atom_coords} 的原子")

# 生成新的 LAMMPS 结构
for i, coords in enumerate(new_coordinates, start=1):
    modified_lines = original_lines[:]  
    original_line = modified_lines[line_to_modify - 1].strip().split()
    new_line = f"    {original_line[0]:<8}{original_line[1]:<5}{coords[0]:.10f}    {coords[1]:.10f}    {coords[2]:.10f}\n"
    modified_lines[line_to_modify - 1] = new_line

    output_filename = os.path.join(output_dir, f"{i:02d}.lmp")
    with open(output_filename, "w") as outfile:
        outfile.writelines(modified_lines)

    print(f"✅ 生成: {output_filename}")

print(f"🎯 所有修改后的 LAMMPS 结构已保存至 {output_dir}/")


### **Step 3: 将 `.lmp` 结构转换为 `POSCAR`** ###
lmp_files = sorted([f for f in os.listdir(output_dir) if f.endswith('.lmp')])

for lmp_file in lmp_files:
    try:
        system = dpdata.System(os.path.join(output_dir, lmp_file), fmt='lammps/lmp', type_map=atomic_species)
        file_number = os.path.splitext(lmp_file)[0]  
        poscar_file = os.path.join(output_dir, f"POSCAR_{int(file_number):02d}")  
        system.to('vasp/poscar', poscar_file)
        print(f"✅ POSCAR 生成: {poscar_file}")

    except Exception as e:
        print(f"❌ 处理 {lmp_file} 时出错: {e}")

print(f"🎯 所有 POSCAR 文件已保存至 {output_dir}/")