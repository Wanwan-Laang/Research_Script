import matplotlib.pyplot as plt
import numpy as np

files_and_rmse = [
    ("results_validation.e_peratom.out",  "8.943792e-04", "fig_e_validation.png"),
    ("results_training.e_peratom.out",    "8.662524e-04", "fig_e_training.png")
]

def plot_data(file_name, rmse, output_file):
    data = np.genfromtxt(file_name, names=["data_e", "pred_e"])

    data_e = data["data_e"]
    pred_e = data["pred_e"]

    plt.figure()

    plt.scatter(data_e, pred_e, color="b", label=f"Energy RMSE: {rmse} eV")

# add a 5% buffer to the plot, just for better visualization   
    buffer = 0.05 * (data_e.max() - data_e.min())
    min_val = min(data_e.min(), pred_e.min()) - buffer
    max_val = max(data_e.max(), pred_e.max()) + buffer
    plt.xlim(min_val, max_val)
    plt.ylim(min_val, max_val)

    plt.plot([min_val, max_val], [min_val, max_val], "r--", linewidth=2)

    plt.xlabel("Raw Data Energy (eV)")
    plt.ylabel("Deep Potential Predicted Energy (eV)")
    plt.title(f"Energy Comparison: {file_name.split('_')[-1].split('.')[0]}")
    plt.legend()

    plt.savefig(output_file, dpi=1200, bbox_inches="tight")
    plt.close()


for file_name, rmse, output_file in files_and_rmse:
    plot_data(file_name, rmse, output_file)