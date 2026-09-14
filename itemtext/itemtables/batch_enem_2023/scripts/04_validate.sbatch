#!/bin/bash
#SBATCH --job-name=itemtext_val
#SBATCH --array=0-3
#SBATCH --partition=normal
#SBATCH --mem=64G
#SBATCH --cpus-per-task=2
#SBATCH --time=02:00:00
#SBATCH --output=/home/users/mazzafe/enem/itemtext_run/logs/val_%a.out
#SBATCH --error=/home/users/mazzafe/enem/itemtext_run/logs/val_%a.err
#
# The non-negotiable join gate: item and resp sets in {table}__items.csv must match
# the live response table exactly. Run against the LOCAL response CSVs via
# --resp-csv, which is quota-free (the Redivis 200GB/30-day export limit was
# exhausted once already) and needs no REDIVIS_API_TOKEN.
#
# Never on a login node: read.csv on a 45M-row / 1.35GB CSV needs tens of GB.

set -u
RUN=/home/users/mazzafe/enem/itemtext_run
VAL=/home/users/mazzafe/irw/itemtext/.claude/skills/irw-auto-itemtext/scripts/validate_items.R
RESP=/scratch/users/mazzafe/enem_output/regular

AREAS=(lc ch cn mt)
A=${AREAS[$SLURM_ARRAY_TASK_ID]}
TABLE=enem_2023_1mil_${A}

echo "=== $TABLE ==="
echo "host=$(hostname)  started=$(date -Is)"
echo "items csv: $RUN/${TABLE}__items.csv"
echo "resp  csv: $RESP/${TABLE}.csv"
echo

Rscript "$VAL" "$TABLE" "$RUN/${TABLE}__items.csv" --resp-csv "$RESP/${TABLE}.csv"
rc=$?
echo
echo "Rscript exit=$rc  finished=$(date -Is)"
[ $rc -eq 0 ] && echo "VALIDATE_RAN_$TABLE" || echo "VALIDATE_ERROR_$TABLE"
