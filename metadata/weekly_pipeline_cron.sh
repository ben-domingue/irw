#!/usr/bin/env bash
# Weekly cron entry point for the IRW metadata pipeline (Workflows 1 + 2 of
# .claude/skills/irw-site-update/SKILL.md). Regenerates the metadata CSVs,
# diffs them against what they replaced, and runs the cross-table audit --
# then writes a dated log so Ben can review at his convenience. Deliberately
# never runs Workflow 3 (upload_meta.py) or touches Redivis publish state;
# that stays a manual, explicit action after reviewing this log.
set -uo pipefail

export PATH="/usr/local/bin:/usr/bin:/bin:$PATH"

REPO_DIR="$HOME/Dropbox/projects/irw/src"
META_DIR="$REPO_DIR/metadata"
SKILL_SCRIPTS="$REPO_DIR/.claude/skills/irw-site-update/scripts"
LOG_DIR="$META_DIR/pipeline_logs"
DATE="$(date +%F)"
LOG_FILE="$LOG_DIR/pipeline_run_${DATE}.md"

mkdir -p "$LOG_DIR"

{
  echo "# IRW metadata pipeline run -- $DATE"
  echo
  echo "## Workflow 1: generate + diff (run_pipeline.sh)"
  echo '```'
  "$SKILL_SCRIPTS/run_pipeline.sh"
  rc1=$?
  echo '```'
  echo
  echo "## Workflow 2: cross-table audit (audit_tables.R)"
  echo '```'
  ( cd "$META_DIR" && Rscript "$SKILL_SCRIPTS/audit_tables.R" )
  rc2=$?
  echo '```'
  echo
  echo "_Workflow 3 (upload_meta.py) intentionally NOT run -- review the diffs"
  echo "and $META_DIR/table_audit_report.md above, then run it by hand if the"
  echo "changes look right._"
  echo
  if [[ "$rc1" -ne 0 || "$rc2" -ne 0 ]]; then
    echo "**ERROR: run_pipeline.sh exit=$rc1, audit_tables.R exit=$rc2 -- review output above.**"
  fi
} > "$LOG_FILE" 2>&1

exit 0
