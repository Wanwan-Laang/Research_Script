# ------------------------------------------------------------
# FLiBe Radial Distribution Function (RDF) Analysis Script
# Date: 2025-02-17
# 說明：
# 此腳本用於處理 LAMMPS 輸出的 RDF 數據，並進行平均化與可視化。
# 包含數據讀取、平均計算、儲存及繪圖等功能。
# ------------------------------------------------------------

import numpy as np
import matplotlib.pyplot as plt

# ============================================================
# 1. 參數設定
# ============================================================

rdf_file        = "flibe.rdf"               # LAMMPS 輸出的 RDF 文件
output_file     = "averaged_rdf.txt"        # 儲存 RDF 平均值的文件

# 設定 RDF 分佈參數
nbins               = 100                   # RDF 的徑向分佈 bins 數量
expected_column_count = 14                  # RDF 文件的列數 (根據 LAMMPS 設定)
g_indices           = [2, 4, 6, 8, 10, 12]  # RDF g(r) 數據對應的列索引

# 初始化 RDF 數據儲存矩陣 (第一列為 r 值)
rdf_data = np.zeros((nbins, len(g_indices) + 1))
frame_count = 0                             # 記錄 RDF 幀數

# ============================================================
# 2. 讀取 RDF 數據
# ============================================================
print(f"Reading RDF file: {rdf_file}")
with open(rdf_file, "r") as f:
    lines = f.readlines()[3:]               # 跳過前 3 行 (標題資訊)

line_idx = 0
while line_idx < len(lines):
    line = lines[line_idx].strip()
    if len(line.split()) == 2:              # 檢測新幀標記
        frame_count += 1
        line_idx += 1
        for i in range(nbins):
            data_line = lines[line_idx].strip().split()
            if len(data_line) == expected_column_count:
                rdf_data[i, 0] += float(data_line[1])  # r 值
                for col_idx, g_idx in enumerate(g_indices):
                    rdf_data[i, col_idx + 1] += float(data_line[g_idx])  # RDF 值
            else:
                raise ValueError(f"Unexpected data format at line {line_idx + 1}: {lines[line_idx]}")
            line_idx += 1
    else:
        raise ValueError(f"Unexpected format in line {line_idx + 1}: {line}")

# ============================================================
# 3. 計算 RDF 平均值
# ============================================================
if frame_count > 0:
    rdf_data /= frame_count                 # 除以總幀數以獲得平均值
    print(f"RDF data successfully averaged over {frame_count} frames.")
else:
    raise ValueError("No valid frames found in the file.")

# ============================================================
# 4. 儲存 RDF 平均數據
# ============================================================
np.savetxt(output_file, rdf_data, header="r g(1-1) g(1-2) g(1-3) g(2-2) g(2-3) g(3-3)", comments='')
print(f"Averaged RDF data saved to {output_file}")

# ============================================================
# 5. 設定 Matplotlib 參數
# ============================================================
plt.rcParams.update({
#    'font.family':       'Times New Roman',
    'font.weight':       'bold',
    'axes.labelweight':  'bold',
    'axes.linewidth':    2,
    'axes.titlesize':    15,
    'axes.labelsize':    15,
    'legend.fontsize':   16,
    'xtick.labelsize':   16,
    'ytick.labelsize':   16
})

# ============================================================
# 6. 繪製 RDF 圖像
# ============================================================

# 定義要繪製的 RDF 類型
labels_to_plot  = ['F-F', 'F-Be', 'F-Li']
all_labels      = ['F-F', 'F-Be', 'F-Li', 'Be-Be', 'Li-Be', 'Li-Li']
colors          = ['red', 'green', 'blue', 'purple', 'orange', 'cyan']

plt.figure(figsize=(8, 6))
for i, (label, color) in enumerate(zip(all_labels, colors)):
    if label in labels_to_plot:
        plt.plot(
            rdf_data[:, 0], rdf_data[:, i + 1],
            label=label, color=color, linewidth=2.5,
            marker='*', markersize=10,
            markevery=max(1, len(rdf_data) // 35)
        )

plt.ylim(0, 11)
plt.xlim(0, 6)
plt.xlabel("r (Å)")
plt.ylabel("g(r)")
plt.legend()
plt.tight_layout()

# ============================================================
# 7. 儲存與顯示圖像
# ============================================================
plt.savefig("rdf-atten.png", dpi=1200, bbox_inches='tight')
plt.show()
# ============================================================