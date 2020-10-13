#!/bin/bash

#SBATCH --job-name=GAfourthdataset
#SBATCH --time=1-00:00:00
#SBATCH --output=out-%x-%j.txt
#SBATCH --error=err-%x-%j.txt
#SBATCH --ntasks=32
#SBATCH -N 1
#SBATCH --exclusive
#SBATCH --partition=learning

module load python/3.6.8_intel-2019_update-4
source activate stockprices

export SLURM_CPU_BIND=none

hostname > hosts.txt

python -m scoop --hostfile hosts.txt -n 32 GA4.py
