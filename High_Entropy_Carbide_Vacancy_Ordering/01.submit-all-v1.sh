#!/bin/bash

for dir in 01.vacancy_structures/1vac_C*/; do
    vacancy=$(basename "$dir")
    cp INCAR-relax INCAR-static KPOINTS POTCAR 02.run_vasp.sh "$dir"
    cd "$dir" || exit
    sed -i "s/6layer_10A/$vacancy/" 02.run_vasp.sh
    sbatch 02.run_vasp.sh
    cd - > /dev/null
done