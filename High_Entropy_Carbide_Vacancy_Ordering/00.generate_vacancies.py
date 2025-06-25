from pymatgen.io.vasp import Poscar
import itertools
import os

def generate_unique_vacancy_structures(
    poscar_path: str,
    element: str = "C",
    max_vacancies: int = 2,
    output_dir: str = "01.vacancy_structures"
):
    base_struct = Poscar.from_file(poscar_path).structure
    os.makedirs(output_dir, exist_ok=True)

    # Find all target atom indices (e.g., C atoms)
    target_indices = [i for i, site in enumerate(base_struct) if site.specie.symbol == element]
    
    print(f"Found {len(target_indices)} {element} atoms")
    
    # Step 1: 1-vacancy - 倒序遍歷
    count_1vac = 0
    for idx, i in enumerate(reversed(target_indices)):
        struct = base_struct.copy()
        struct.remove_sites([i])
        # 使用C原子的順序編號：C080, C079, C078, ..., C001
        c_number = len(target_indices) - idx
        folder = os.path.join(output_dir, f"1vac_C{c_number:03d}")
        os.makedirs(folder, exist_ok=True)
        Poscar(struct).write_file(os.path.join(folder, "POSCAR"))
        count_1vac += 1

    # Step 2: 2-vacancy - 全部遍歷，倒序移除原子
    count_2vac = 0
    distance_data = []
    
    for indices in itertools.combinations(target_indices, 2):
        struct = base_struct.copy()
        
        # 計算兩個C原子之間的距離
        site1 = base_struct[indices[0]]
        site2 = base_struct[indices[1]]
        distance = site1.distance(site2)
        
        # 按降序移除原子以避免索引錯位
        struct.remove_sites(sorted(indices, reverse=True))
        
        # 將索引轉換為C原子序號
        c1_number = target_indices.index(indices[0]) + 1
        c2_number = target_indices.index(indices[1]) + 1
        
        # 文件夾名包含距離信息
        folder = os.path.join(output_dir, f"2vac_C{c1_number:03d}_C{c2_number:03d}_d{distance:.3f}")
        os.makedirs(folder, exist_ok=True)
        Poscar(struct).write_file(os.path.join(folder, "POSCAR"))
        
        # 收集距離數據（保留3位小數）
        distance_data.append([f"C{c1_number:03d}", f"C{c2_number:03d}", round(distance, 3)])
        count_2vac += 1

    # 保存距離數據到CSV文件
    import csv
    with open("Data_vacancy_distances.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Atom1", "Atom2", "Distance_Angstrom"])
        for data in distance_data:
            writer.writerow(data)

    print(f"Generated {count_1vac} 1-vacancy structures")
    print(f"Generated {count_2vac} 2-vacancy structures")

# Example usage:
if __name__ == "__main__":
    generate_unique_vacancy_structures("POSCAR", element="C", max_vacancies=2)