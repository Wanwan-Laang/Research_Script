#!/bin/bash

total_folders=80     # 總資料夾數
batch_size=10        # 每批次資料夾數
start_folder=1

# 創建總 summary 文件，清空
echo "🚀 Creating master summary: summary_all_ontop.log"
echo "" > summary_all_ontop.log

while (( start_folder <= total_folders )); do
    end_folder=$(( start_folder + batch_size - 1 ))
    if (( end_folder > total_folders )); then
        end_folder=$total_folders
    fi

    job_name="on_${start_folder}_to_${end_folder}"

    echo "🚀 Submitting job for folders $start_folder to $end_folder"

    # 生成 run-zlab-ontop-${start_folder}-${end_folder}.sh
    cat > run-zlab-ontop-${start_folder}-${end_folder}.sh << EOF
#!/bin/bash
#SBATCH --job-name=$job_name
#SBATCH --time=30-00:00:00
#SBATCH --partition=zlab
#SBATCH --nodes=1
#SBATCH --ntasks=128
#SBATCH --output=${job_name}-%j.out
#SBATCH --error=${job_name}-%j.err
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=lww.phys@gmail.com

source ~/.bashrc
conda activate deepmd

module load intel/tbb/latest intel/compiler-rt/latest intel/mkl/latest intel/umf/latest intel/mpi/latest
export PATH=/projects/illinois/eng/npre/jianqixi/MNM/apps/vasp/vasp.6.4.2_vtst/bin:\$PATH

unset I_MPI_LOG_FILE
unset I_MPI_DEBUG
unset I_MPI_LOG_LEVEL

ulimit -s unlimited

cd ontop

# 為每個batch加一個標題進 master summary
echo "=== Batch ${start_folder} to ${end_folder} ===" >> ../summary_all_ontop.log

for folder in \$(seq -w ${start_folder} ${end_folder}); do
    echo "🚀 Entering \$folder"
    cd "\$folder"

    cp INCAR-relax INCAR
    cp POSCAR POSCAR-before-relax
    echo "[\${folder}] Start relax at \$(date)" >> time.log

    max_retry=10
    attempt=1
    relax_success=0
    while (( attempt <= max_retry )); do
        echo "🔁 Attempt \$attempt for relax"
        echo "[\${folder}] Relax attempt \$attempt at \$(date)" >> time.log

        rm -f fp-relax.log
        mpirun -n 128 vasp_std 1>>fp-relax.log 2>>fp-relax.log || true

        if grep -q "ZBRENT: fatal error" fp-relax.log; then
            echo "⚠️ ZBRENT error detected. Retrying..."
            cp CONTCAR POSCAR
            ((attempt++))
        else
            echo "✅ Relax completed on attempt \$attempt"
            relax_success=1
            break
        fi
    done

    if (( relax_success == 0 )); then
        echo "❌ Relax failed after \$max_retry attempts in \$folder" | tee -a ../error.log
        echo "\$folder ❌ FAILED" >> ../summary_all_ontop.log
        cd ..
        continue
    else
        echo "\$folder ✅ SUCCESS" >> ../summary_all_ontop.log
    fi

    echo "[\${folder}] End   relax at \$(date)" >> time.log
    cp CONTCAR CONTCAR-after-relax
    cp CONTCAR POSCAR

    cp INCAR-static INCAR
    echo "[\${folder}] Start static at \$(date)" >> time.log
    mpirun -n 128 vasp_std 1>>fp-static.log 2>>fp-static.log
    echo "[\${folder}] End   static at \$(date)" >> time.log

    cd ..
done

echo "✅ Finished batch ${start_folder}-${end_folder} at \$(date)"
EOF

    # 提交這個job
    sbatch run-zlab-ontop-${start_folder}-${end_folder}.sh

    start_folder=$(( end_folder + 1 ))
done