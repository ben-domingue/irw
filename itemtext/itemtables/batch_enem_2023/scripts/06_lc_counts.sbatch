#!/bin/bash
#SBATCH --job-name=lc_counts
#SBATCH --partition=normal
#SBATCH --mem=8G
#SBATCH --time=00:40:00
#SBATCH --output=/home/users/mazzafe/enem/itemtext_run/logs/lc_counts.out
set -u
# Row counts per item for enem_2023_1mil_lc: confirms the audit's row-count WARN is
# the foreign-language block (each candidate answers only their chosen language).
awk -F',' 'NR>1{gsub(/"/,"",$2); n[$2]++} END{for(i in n) print n[i]"\t"i}' \
    /scratch/users/mazzafe/enem_output/regular/enem_2023_1mil_lc.csv | sort -n
