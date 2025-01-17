import numpy as np
import matplotlib.pyplot as plt
import glob
import os

# Use glob to find all matching files
file_list = glob.glob("./iter*/00.train/*/lcurve.out")

if not file_list:
    raise FileNotFoundError("No files found matching the pattern './dpgen_run/*/lcurve.out'")

for file_path in file_list:
    data = np.genfromtxt(file_path, names=True)

    dir_name = os.path.basename(os.path.dirname(file_path))
    title = f"lcurve_{dir_name}"

    # Plot scatter plot
    for name in data.dtype.names[1:-1]:
        plt.scatter(data['step'], data[name], label=name)
    plt.legend()
    plt.xlabel('Step')
    plt.ylabel('Loss')
    plt.yscale('log')
    plt.title(title)
    plt.xlim(0,20000)   
    plt.savefig(f'lcurve_D_{dir_name}.pdf')
    plt.close()

    # Plot line plot
    for name in data.dtype.names[1:-1]:
        plt.plot(data['step'], data[name], label=name)
    plt.legend()
    plt.xlabel('Step')
    plt.ylabel('Loss')
    plt.yscale('log')
    plt.title(title)
    plt.savefig(f'lcurve_L_{dir_name}.pdf')
    plt.close()
