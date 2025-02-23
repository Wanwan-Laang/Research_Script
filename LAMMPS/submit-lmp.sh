#!/bin/bash
#SBATCH --job-name=debug
#SBATCH --time=1-00:00:00
#SBATCH --nodes=4
#SBATCH --ntasks=4  # 4 個 MPI 進程，每個節點 1 個
#SBATCH --cpus-per-task=128  # 每個 MPI 進程使用 128 個 OpenMP 線程
#SBATCH --partition=zlab

export OMP_NUM_THREADS=128
export TF_INTRA_OP_PARALLELISM_THREADS=128
export TF_INTER_OP_PARALLELISM_THREADS=8

export OMPI_MCA_btl=self,tcp
export OMPI_MCA_btl_vader_single_copy_mechanism=none

export OMP_DISPLAY_ENV=TRUE

mpirun -np 4 --bind-to core --map-by node lmp -in FLiBe.lmp > mpirun_run.log 2>&1

