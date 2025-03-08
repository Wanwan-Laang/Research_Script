#!/bin/bash
#SBATCH --job-name=CPU-DPA
#SBATCH --time=00:10:00
#SBATCH --nodes=2               
#SBATCH --ntasks=256            # the total number of tasks
#SBATCH --ntasks-per-node=128   # the number of tasks per node 
#SBATCH --partition=zlab

export TF_INTRA_OP_PARALLELISM_THREADS=1
export TF_INTER_OP_PARALLELISM_THREADS=1

# use pure MPI. AND do not use $SLURM_NTASKS, which is slightly slower 
mpirun -np 256 --bind-to core --map-by node lmp -in input.lammps

