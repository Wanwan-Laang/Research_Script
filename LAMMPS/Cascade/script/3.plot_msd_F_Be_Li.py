
# plot_msd_F_Be_Li.py
# Extract and plot MSD of F, Be, Li from LAMMPS log or thermo output
# 畫出 F、Be、Li 的 MSD 比較圖
import matplotlib.pyplot as plt

def read_thermo_msd(filename):
    time = []
    msdF = []
    msdBe = []
    msdLi = []

    with open(filename, 'r') as f:
        for line in f:
            if line.strip() and not line.startswith("#") and not line.startswith("Step"):
                parts = line.split()
                time.append(float(parts[0]))
                msdF.append(float(parts[-3]))
                msdBe.append(float(parts[-2]))
                msdLi.append(float(parts[-1]))
    
    return time, msdF, msdBe, msdLi

# Replace with your LAMMPS thermo output that includes msd values
time, msdF, msdBe, msdLi = read_thermo_msd("log.msd")

plt.plot(time, msdF, label="MSD (F)")
plt.plot(time, msdBe, label="MSD (Be)")
plt.plot(time, msdLi, label="MSD (Li)")
plt.xlabel("Time (ps)")
plt.ylabel("MSD (√Ö¬≤)")
plt.title("MSD of F, Be, Li Over Time")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

