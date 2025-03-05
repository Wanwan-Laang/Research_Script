import matplotlib.pyplot as plt
import numpy as np

files_and_rmse = [
    ("results_training.f.out", "6.819175e-02", "Training"),
    ("results_validation.f.out", "7.387626e-02", "Validation")

]

plt.figure(figsize=(6, 5))

min_val, max_val = float('inf'), float('-inf')  # 記錄全局最小和最大值

for file_name, rmse, label in files_and_rmse:
    data = np.genfromtxt(file_name, names=["data_fx", "data_fy", "data_fz", "pred_fx", "pred_fy", "pred_fz"])
    
    # 將所有方向的數據合併處理
    data_all = np.concatenate([data["data_fx"], data["data_fy"], data["data_fz"]])
    pred_all = np.concatenate([data["pred_fx"], data["pred_fy"], data["pred_fz"]])

    # 記錄最小和最大值
    min_val = min(min_val, data_all.min(), pred_all.min())
    max_val = max(max_val, data_all.max(), pred_all.max())

    plt.scatter(data_all, pred_all, alpha=0.6, label=f"{label} (RMSE: {rmse})")

# 添加 5% 緩衝區
buffer = 0.05 * (max_val - min_val)
min_val -= buffer
max_val += buffer

# 設置範圍
plt.xlim(min_val, max_val)
plt.ylim(min_val, max_val)

# 添加 y = x 參考線
plt.plot([min_val, max_val], [min_val, max_val], "r--", linewidth=1.5)

# 標籤
plt.xlabel("DFT Force (eV/Å)")
plt.ylabel("Deep Potential Predicted Force (eV/Å)")
plt.legend()

# 保存圖像
plt.savefig("poster_Forces.png", dpi=900, bbox_inches="tight", transparent=True)
plt.show()