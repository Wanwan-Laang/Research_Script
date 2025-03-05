import matplotlib.pyplot as plt
import numpy as np

files_and_rmse = [
    ("results_validation.f.out",  "7.387626e-02", "fig_f_validation.png"),
    ("results_training.f.out",    "7.378531e-02", "fig_f_training.png")
]


def plot_forces(file_name, rmse, output_file):
    data = np.genfromtxt(file_name, names=["data_fx", "data_fy", "data_fz", "pred_fx", "pred_fy", "pred_fz"])

    directions = ['fx', 'fy', 'fz']
    colors = ['g', 'orange', 'b']
    plt.figure()

    buffer = 0.05 * (data['data_fx'].max() - data['data_fx'].min())  # 5% buffer
    min_val = min(data['data_fx'].min(), data['pred_fx'].min()) - buffer
    max_val = max(data['data_fx'].max(), data['pred_fx'].max()) + buffer
    plt.xlim(min_val, max_val)
    plt.ylim(min_val, max_val)

    plt.plot([min_val, max_val], [min_val, max_val], "r--", linewidth=2)
    plt.scatter([], [], color='none', label=f"RMSE: {rmse} eV")  # 空数据点用于显示 RMSE

    for direction, color in zip(directions, colors):
        data_col = f"data_{direction}"
        pred_col = f"pred_{direction}"
        plt.scatter(data[data_col], data[pred_col], color=color, label=f"{direction.upper()}")

    plt.xlabel("Raw Data Force (eV/Å)")
    plt.ylabel("Deep Potential Predicted Force (eV/Å)")
    plt.title(f"Force Comparison: {file_name.split('_')[-1].split('.')[0]}")
    plt.legend()

    plt.savefig(output_file, dpi=900, bbox_inches="tight")
    plt.close()

for file_name, rmse, output_file in files_and_rmse:
    plot_forces(file_name, rmse, output_file)
