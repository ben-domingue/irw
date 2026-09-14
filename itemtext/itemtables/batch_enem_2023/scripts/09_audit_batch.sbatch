#!/bin/bash
#SBATCH --job-name=itemtext_audit
#SBATCH --partition=normal
#SBATCH --mem=96G
#SBATCH --cpus-per-task=4
#SBATCH --time=02:00:00
#SBATCH --output=/home/users/mazzafe/enem/itemtext_run/logs/audit_batch.out
#SBATCH --error=/home/users/mazzafe/enem/itemtext_run/logs/audit_batch.out
#
# Generate batch_enem_2023/audit_report.csv, the fifth required file in a batch
# directory per BATCH_PROCESS.md. --resp-dir audits against the local
# #1942-CORRECTED response CSVs rather than live Redivis: no API token here, and
# audit_batch.R's header notes the account's 200GB/30-day export quota was
# exhausted once already on 2026-08-18.
#
# 96G because this reads all four ~1.4GB CSVs; the header warns a 45M-row
# read.csv needs tens of GB.
set -u
cd /home/users/mazzafe/irw/itemtext
echo "=== started=$(date -Is) host=$(hostname) ==="
Rscript .claude/skills/irw-auto-itemtext/scripts/audit_batch.R \
  itemtables/batch_enem_2023 \
  --resp-dir /scratch/users/mazzafe/fix1942_run/work/2023
rc=$?
echo "Rscript exit=$rc  finished=$(date -Is)"
[ $rc -eq 0 ] && echo "AUDIT_DONE" || echo "AUDIT_ERROR"
