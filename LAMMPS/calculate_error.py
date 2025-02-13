import numpy as np
from collections import defaultdict

def load_reference_energies(file_path):
    """load reference DFT energies from file(modified to extract the third column)"""
    energies = {}
    with open(file_path) as f:
        for line in f:
            parts = line.strip().split()
            filename = parts[0].strip()  # grab the filename
            energy = float(parts[2])  # **修改为提取第三列,這是我後面自己加入的修正DFT列；我的第二列是我導入的原始的DFT數據列，使用第二列則改爲parts[1]**
            energies[filename] = energy
    return energies

def parse_lammps_line(line):
    parts = line.strip().split()
    params = {
        'd1': float(parts[0].split('=')[1]),
        'd2': float(parts[1].split('=')[1]),
        'filename': parts[2].split('/')[-1].replace(',', ''),
        'energy': float(parts[-1].split('=')[1])
    }
    return params

def load_lammps_results(file_path):
    """load results from LAMMPS output file"""
    results = defaultdict(list)
    with open(file_path) as f:
        for line in f:
            data = parse_lammps_line(line)
            key = (data['d1'], data['d2'])
            results[key].append((data['filename'], data['energy']))
    return results

def calculate_rmse(reference, lammps_data):
    """calculate RMSE for all (d1, d2) combinations"""
    rmse_values = {}
    for params, entries in lammps_data.items():
        errors = []
        for filename, energy in entries:
            if ref_energy := reference.get(filename):
                errors.append((energy - ref_energy)**2)
        if errors:
            rmse_values[params] = np.sqrt(np.mean(errors))
    return rmse_values

def format_results(rmse_data, top_n=3):
    output = []
    
    output.append("d1\t d2\t RMSE\n" + "="*30)
    sorted_rmse = sorted(rmse_data.items(), key=lambda x: x[1])
    for params, rmse in sorted_rmse:
        output.append(f"{params[0]:.2f}\t{params[1]:.2f}\t{rmse:.6f}")

    # calculate top N
    best_keys = sorted(rmse_data, key=rmse_data.get)[:top_n]
    output.append("\n📌 **RMSE 最小的3组(d1,d2)组合**")
    for rank, params in enumerate(best_keys, 1):
        output.append(f"🏆 第{rank}名 (d1={params[0]}, d2={params[1]}): RMSE = {rmse_data[params]:.6f}")

    return '\n'.join(output)

def main():
    ref_energies = load_reference_energies("ref_DFT_F-F.txt")
    lammps_results = load_lammps_results("./small_mesh-F-F/energies_DPA_ZBL.txt")
    
    rmse_data = calculate_rmse(ref_energies, lammps_results)
    
    with open("rmse_results_F-F.txt", "w") as f:
        f.write(format_results(rmse_data))
        f.write("\n\n" + "="*80 + "\n")
        
        best_combinations = sorted(rmse_data, key=rmse_data.get)[:3]
        headers = ["Structure Number", "DFT Energy"] + [f"d1={p[0]},d2={p[1]}" for p in best_combinations]
        f.write('\t'.join(headers) + '\n')
        
        for filename in ref_energies:
            row = [filename, f"{ref_energies[filename]:.6f}"]
            for params in best_combinations:
                lmp_energy = next((e for fname, e in lammps_results[params] if fname == filename), "N/A")
                row.append(f"{lmp_energy:.6f}" if isinstance(lmp_energy, float) else lmp_energy)
            f.write('\t'.join(row) + '\n')

    print("\n✅ Finished! Results saved to rmse_results_F-F.txt")

if __name__ == "__main__":
    main()