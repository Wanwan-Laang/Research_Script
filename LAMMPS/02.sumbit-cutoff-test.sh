#!/bin/bash
#SBATCH --job-name=Cutoff-TEST
#SBATCH --partition=YOUR_PARTITION
#SBATCH --nodes=1
#SBATCH --ntasks=64
#SBATCH --time=2:00:00  

export OMP_NUM_THREADS=16
export TF_INTRA_OP_PARALLELISM_THREADS=4
export TF_INTER_OP_PARALLELISM_THREADS=1

WORKDIR="./MD"
subdir="small_mesh-test"

cd "$WORKDIR/$subdir" || { echo "❌ Error: Could not enter $WORKDIR/$subdir"; exit 1; }

start=70   # 0.7 * 100
end=120    # 1.2 * 100
step=2     # 0.02 * 100

echo "🔹 Running calculations in $subdir..."

for (( cut1_val = start; cut1_val <= end; cut1_val += step )); do
    cut1=$(awk "BEGIN {printf \"%.2f\", $cut1_val/100}")
    for (( cut2_val = cut1_val; cut2_val <= end; cut2_val += step )); do  # ✅ we only need cut2 >= cut1
        cut2=$(awk "BEGIN {printf \"%.2f\", $cut2_val/100}")
        
        echo "  ➤ Running cut1=$cut1, cut2=$cut2 in $subdir"

        sed -i "/^variable cut1 equal /c\variable cut1 equal $cut1" in_DPA_zbl.lmp
        sed -i "/^variable cut2 equal /c\variable cut2 equal $cut2" in_DPA_zbl.lmp

        lmp_mpi -in in_DPA_zbl.lmp 
    done
done

echo "✅ Completed calculations in $subdir."
echo "🎉 All calculations done!"