import os
import numpy as np
import matplotlib.pyplot as plt

rdf_file = "flibe.rdf"
output_file = "rdf.txt"

nbins = 100  
expected_column_count = 14  
# the first column is the bin center, the next 13 columns are the g(r) values for each pair of atom types

rdf_data = np.zeros((nbins, expected_column_count - 1))  
count = 0 

print(f"Reading RDF file: {rdf_file}")
with open(rdf_file, "r") as f:
    lines = f.readlines()[3:]  

    for line in lines:
        nums = line.split()
        if len(nums) == expected_column_count: 
            for i in range(1, expected_column_count):  
                rdf_data[int(nums[0]) - 1, i - 1] += float(nums[i])
        elif len(nums) == 2:  # 時間步長行
            count += 1
        else:
            print(f"Warning: Skipping line due to unexpected column count: {line.strip()}")

if count > 0:
    rdf_data[:, 1:] /= count  
    print(f"RDF data successfully averaged over {count} accumulations.")
else:
    raise ValueError("No valid RDF data found in the file.")

np.savetxt(output_file, rdf_data, header="r g(1-1) g(1-2) g(1-3) g(2-2) g(2-3) g(3-3)", comments='')
print(f"Averaged RDF data saved to {output_file}")

labels = ['F-F', 'F-Be', 'F-Li', 'Be-Be', 'Be-Li', 'Li-Li']
colors = ['blue', 'orange', 'purple', 'red', 'green', 'brown']
ignore_labels = ['F-Be','Be-Be','Li-Li']  # Manually select pairs to ignore

# set the font family and weight for the plot
plt.rcParams['font.family'] = 'Times New Roman'
plt.rcParams['font.weight'] = 'bold'
plt.rcParams['axes.labelweight'] = 'bold'
plt.rcParams['axes.linewidth'] = 2    # linewidth of the frame
plt.rcParams['axes.titlesize'] = 15   # title size
plt.rcParams['axes.labelsize'] = 15   # label size
plt.rcParams['legend.fontsize'] = 16  # legend size
plt.rcParams['xtick.labelsize'] = 16  # x axis tick size
plt.rcParams['ytick.labelsize'] = 16  # y axis tick size


plt.figure(figsize=(8, 6))

for i, (label, color) in enumerate(zip(labels, colors)):
    if label not in ignore_labels: 
#        plt.plot(rdf_data[:, 0], rdf_data[:, i + 1], label=label, color=color, linewidth=3)
        plt.plot(rdf_data[:, 0], rdf_data[:, i + 1], label=label, color=color, linewidth=2.5, marker='*', markersize=10, markevery=max(1, len(rdf_data) // 35))
plt.ylim(0, 11) 
plt.xlim(0, max(rdf_data[:, 0])) 
plt.xlabel("r (Å)")
plt.ylabel("g(r)")
plt.title("Radial Distribution Function")
plt.legend()
plt.tight_layout()

#plt.savefig("flibe.png", dpi=1200)
plt.show()
