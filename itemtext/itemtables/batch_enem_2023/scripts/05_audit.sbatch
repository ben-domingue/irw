#!/bin/bash
#SBATCH --job-name=itemtext_audit
#SBATCH --partition=normal
#SBATCH --mem=96G
#SBATCH --cpus-per-task=4
#SBATCH --time=03:00:00
#SBATCH --output=/home/users/mazzafe/enem/itemtext_run/logs/audit.out
#SBATCH --error=/home/users/mazzafe/enem/itemtext_run/logs/audit.err
#
# audit_batch.R reads every response CSV in --resp-dir (4 x 1.35GB for 2023),
# so it cannot run on a login node -- it timed out there.
set -u
RUN=/home/users/mazzafe/enem/itemtext_run
SK=/home/users/mazzafe/irw/itemtext/.claude/skills/irw-auto-itemtext/scripts
DIR=$RUN/auditdir
mkdir -p "$DIR" && rm -f "$DIR"/*__items.csv
cp /home/users/mazzafe/irw/itemtext/itemtables/enem_2023_1mil_*__items.csv "$DIR"/
echo "host=$(hostname) started=$(date -Is)"
Rscript "$SK/audit_batch.R" "$DIR" "$RUN/audit_report.csv" \
        --resp-dir /scratch/users/mazzafe/enem_output/regular
echo "audit exit=$?  finished=$(date -Is)"
