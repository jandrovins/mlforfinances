#!/bin/bash

for CXPB in 0.01 0.05 0.1 0.2 0.25 0.3; do
    for MUTPB in 0.001 0.005 0.01 0.02 0.05 0.1; do
        for lwlimit in -2 -1 0 ; do
            for rwlimit in 2 3 4 5 ; do
                    sbatch --job-name="GA_CXPB${CXPB}_MUTPB${MUTPB}_n${n}_MAXGENERATIONS${MAXGENERATIONS}_lwlimit${lwlimit}_rwlimit${rwlimit}"\
                        --time=4:00:00 --ntasks=32\
                        --output=outfiles/out-%x-%j.txt --error=outfiles/err-%x-%j.txt\
                        --nodes=1\
                        --partition=longjobs\
                        sub_job.sh $CXPB $MUTPB $lwlimit $rwlimit
            done
        done
    done
done

