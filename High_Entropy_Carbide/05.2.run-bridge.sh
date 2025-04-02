#!/bin/bash
#SBATCH --job-name=bridge
#SBATCH --time=30-00:00:00
#SBATCH --partition=xi
#SBATCH --nodes=1
#SBATCH --ntasks=64

source ~/.bashrc
conda activate deepmd

# Load VASP + Intel
export PATH=/projects/illinois/eng/npre/jianqixi/MNM/apps/vasp/vasp.6.4.2_vtst_2025/bin:$PATH
export PATH=/projects/illinois/eng/npre/jianqixi/MNM/apps/tool/intel/compiler/2025.0/bin/:$PATH
export SETVARS_ARGS="--force"
source /projects/illinois/eng/npre/jianqixi/MNM/apps/tool/intel/setvars.sh
unset SETVARS_ARGS

ulimit -s unlimited
set -e

cd bridge

for folder in {01..80}; do
    echo "🚀 Entering $folder"
    cd "$folder"

    cp INCAR-relax INCAR

    echo "[${folder}] Start relax at $(date)" >> time.log
    mpirun -n 64 vasp_std 1>>fp-relax.log 2>>fp-relax.log
    echo "[${folder}] End relax at $(date)" >> time.log

    cp POSCAR POSCAR-before-relax
    cp CONTCAR POSCAR

    cp INCAR-static INCAR
    echo "[${folder}] Start static at $(date)" >> time.log
    mpirun -n 64 vasp_std 1>>fp-static.log 2>>fp-static.log
    echo "[${folder}] End static at $(date)" >> time.log

    cd ..
done

echo "✅ All bridge jobs finished at $(date)"
