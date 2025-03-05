# thermo_style    custom step temp press vol density ; input file in.lammps
import numpy as np
import matplotlib.pyplot as plt

def parse_log_lammps(file_path):

    timesteps = []
    temperatures = []
    pressures = []
    volumes = []
    densities = []

    with open(file_path, 'r') as f:
        lines = f.readlines()

    # skip the first 212 lines, until this line is reached:
    # Step          Temp          Press          Volume        Density

    lines = lines[212:]

    for line in lines:
        # check for numerical lines, and skip column headers lines and non-numerical lines
        parts = line.strip().split()
        if parts and parts[0].isdigit():  # check if the first part is a digit
            try:
                timestep = int(parts[0])
                temperature = float(parts[1])
                pressure = float(parts[2])
                volume = float(parts[3])
                density = float(parts[4])
                timesteps.append(timestep)
                temperatures.append(temperature)
                pressures.append(pressure)
                volumes.append(volume)
                densities.append(density)
            except ValueError:
                # skip lines that cannot be converted to float
                continue

    return (np.array(timesteps), np.array(temperatures), np.array(pressures), 
            np.array(volumes), np.array(densities))

def plot_density_evolution(timesteps, temperatures, pressures, volumes, densities, output_file):

    plt.figure(figsize=(10, 8))

    plt.subplot(2, 2, 1)
    plt.xscale("log")
    plt.plot(timesteps, temperatures, marker="o", linestyle="-", color="r", label="Temperature (K)")
    plt.xlabel("Time-step")
    plt.ylabel("Temperature (K)")
    plt.title("Temperature Evolution")
    plt.legend()

    plt.subplot(2, 2, 2)
    plt.xscale("log")
    plt.plot(timesteps, pressures, marker="o", linestyle="-", color="g", label="Pressure (atm)")
    plt.xlabel("Time-step")
    plt.ylabel("Pressure (atm)")
    plt.title("Pressure Evolution")
    plt.legend()

    plt.subplot(2, 2, 3)
    plt.xscale("log")
    plt.plot(timesteps, volumes, marker="o", linestyle="-", color="b", label="Volume (Å³)")
    plt.xlabel("Time-step")
    plt.ylabel("Volume (Å³)")
    plt.title("Volume Evolution")
    plt.legend()

    plt.subplot(2, 2, 4)
    plt.xscale("log")
    plt.plot(timesteps, densities, marker="o", linestyle="-", color="m", label="Density (g/cm³)")
    plt.xlabel("Time-step")
    plt.ylabel("Density (g/cm³)")
    plt.title("Density Evolution")
    plt.legend()

    plt.tight_layout()
    plt.savefig(output_file, dpi=1200, bbox_inches="tight")
    plt.show()

log_file = "log.lammps" 
output_image = "evolution_log.png"

timesteps, temperatures, pressures, volumes, densities = parse_log_lammps(log_file)
plot_density_evolution(timesteps, temperatures, pressures, volumes, densities, output_image)