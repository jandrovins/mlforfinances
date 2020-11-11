#!/bin/bash

module load python/3.7_miniconda-4.8.3
source activate SP

export SLURM_CPU_BIND=none

n=64
MAXGENERATIONS=100
CXPB=$1
MUTPB=$2
lwlimit=$3
rwlimit=$4

for stock in $(ls datasets); do
    pkl=datasets/${stock}/${stock}_CXPB${CXPB}_MUTPB${MUTPB}_n${n}_MAXGENERATIONS${MAXGENERATIONS}_lwlimit${lwlimit}_rwlimit${rwlimit}.pkl
    validation_csv=datasets/${stock}/${stock}validation.csv
    echo "In stock: $stock"

    ls $pkl &> /dev/null || ~/.conda/envs/SP/bin/python -m scoop --host $(hostname) -n 32 GA.py $CXPB $MUTPB $n $stock $MAXGENERATIONS $lwlimit $rwlimit $pkl

    print_prefix="RESULTS: In ${stock}:: CXPB ${CXPB}:: MUTPB ${MUTPB}:: n ${n}:: MAXGENERATIONS ${MAXGENERATIONS}:: lwlimit ${lwlimit}:: rwlimit ${rwlimit}: " 
    ~/.conda/envs/SP/bin/python print_solution.py $pkl $validation_csv "$print_prefix" | tee -a /home/vaarcilal/StockPrices/all_results.txt
    echo 
done
