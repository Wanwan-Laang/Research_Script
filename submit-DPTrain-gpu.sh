#!/bin/bash
#SBATCH --job-name=DPA2_7680_nolayer
#SBATCH --time=3-00:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=16
#SBATCH --partition=IllinoisComputes-GPU
#SBATCH --gres=gpu:2
#SBATCH --account=jianqixi-ic

export OMP_NUM_THREADS=2 # 1 core
export TF_INTRA_OP_PARALLELISM_THREADS=1
export TF_INTER_OP_PARALLELISM_THREADS=8 # 8 cpu

export DP_INFER_BATCH_SIZE=8192  # control the batch size
export TF_FORCE_GPU_ALLOW_GROWTH=true  # avoid OOM
export OMPI_MCA_btl=self,vader,tcp  # MPI 
export OMPI_MCA_btl_vader_single_copy_mechanism=none 

module unload cuda/12.4

conda init

conda activate base
