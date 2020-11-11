#!/bin/bash

#SBATCH --job-name=GA
#SBATCH --time=1-00:00:00
#SBATCH --output=outfiles/out-%x-%j.txt
#SBATCH --error=outfiles/err-%x-%j.txt
#SBATCH --ntasks=32
#SBATCH -N 1
#SBATCH --exclusive
#SBATCH --partition=learning

module load python/3.7_miniconda-4.8.3
source activate SP

export SLURM_CPU_BIND=none

hostname > hosts.txt
#CXPB=0.3
#MUTPB=0.01
n=96
MAXGENERATIONS=500
for CXPB in 0.01 0.05 0.1 0.15 0.2 0.25 0.3; do 
    for MUTPB in 0.001 0.005 0.01 0.02 0.04 0.05 0.07 0.1; do
        for stock in $(ls datasets); do
            pkl=datasets/${stock}/${stock}_CXPB${CXPB}_MUTPB${MUTPB}_n${n}_MAXGENERATIONS${MAXGENERATIONS}.pkl
            validation_csv=datasets/${stock}/${stock}validation.csv
            ls $pkl || ~/.conda/envs/SP/bin/python -m scoop --hostfile hosts.txt -n 32 GA.py $CXPB $MUTPB $n $stock $MAXGENERATIONS
            echo -n "RESULTS: "
            echo -n "In ${stock}:: CXPB ${CXPB}:: MUTPB ${MUTPB}:: n ${n}:: MAXGENERATIONS ${MAXGENERATIONS}: " | tee -a all_results.txt
            ~/.conda/envs/SP/bin/python print_solution.py $pkl $validation_csv | tee -a all_results.txt
        done
    done
done
