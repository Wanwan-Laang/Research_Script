import matplotlib.pyplot as plt
import numpy as np

files_and_rmse = [
    ("results_training.e_peratom.out",    "8.662524e-04", "Training"),
    ("results_validation.e_peratom.out",  "8.943792e-04", "Validation")
]


plt.figure(figsize=(6, 5))

min_val, max_val = float('inf'), float('-inf')  

for file_name, rmse, label in files_and_rmse:
    data = np.genfromtxt(file_name, names=["data_e", "pred_e"])

    data_e = data["data_e"]
    pred_e = data["pred_e"]

    min_val = min(min_val, data_e.min(), pred_e.min())
    max_val = max(max_val, data_e.max(), pred_e.max())

    plt.scatter(data_e, pred_e, label=f"{label} (RMSE: {rmse})", alpha=0.7)

# 添加 5% 緩衝區
buffer = 0.05 * (max_val - min_val)
min_val -= buffer
max_val += buffer

plt.xlim(min_val, max_val)
plt.ylim(min_val, max_val)

plt.plot([min_val, max_val], [min_val, max_val], "r--", linewidth=2)

plt.xlabel("DFT Energy (eV/atom)")
plt.ylabel("Machine Learning Predicted Energy (eV/atom)")
plt.legend()
plt.savefig("poster_Energies.png", dpi=1200, bbox_inches="tight", transparent=True)

