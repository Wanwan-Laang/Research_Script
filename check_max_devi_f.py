import os
import numpy as np
import matplotlib.pyplot as plt
import glob

# Specify the number of iterations
iterations = [8,9] 
for i in iterations:

# If not specified and wanna check all the iterations, use the following code with range function
#for i in range(5, 9): 
    max_devi_f_values = []
    # Dynamically determine the number of LAMMPS tasks, 
    # So you don't need manually specify the number of MD. 
    directory_pattern = "./iter.{:06d}/01.model_devi/task.*".format(i)
    task_directories = glob.glob(directory_pattern)
    for task_directory in task_directories:
        file_path = os.path.join(task_directory, "model_devi.out")
        if os.path.exists(file_path):
            data = np.genfromtxt(file_path, skip_header=1, usecols=4)
            max_devi_f_values.append(data)

    max_devi_f_values = np.concatenate(max_devi_f_values)

    # Use numpy.histogram() to calculate the frequency of each calculated region
    hist, bin_edges = np.histogram(max_devi_f_values, range=(0, 0.25), bins=100)

    # Normalize the frequency to percentage
    hist = hist / len(max_devi_f_values) * 100

    plt.tick_params(axis='both', direction='in')
    plt.plot(bin_edges[:-1], hist,label = 'iter{:02d}'.format(i),lw=4)
    #plt.axvline(x=0.05, color='grey', linestyle='--')
    #plt.xlim((min(bin_edges), max(bin_edges)))
    #plt.ylim(-.2, 7.2)
    plt.legend()
    plt.xlabel("max_devi_f eV/Å",fontsize=11)
    plt.ylabel("Distribution %",fontsize=11)

    with open(f'./iter{i:02d}_dist-max-devi-f.txt'.format(i), 'w') as f:
        f.write("{:>12} {:>12}\n".format("bin_edges", "hist"))
        for x, y in zip(bin_edges[:-1], hist):
            f.write('{:>12.3f} {:>12.3f}\n'.format(x, y))

plt.savefig('./max-devi-f.png',dpi=1200, bbox_inches='tight')
