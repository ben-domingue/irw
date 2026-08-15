#!/usr/bin/env bash
# Weekly cron entry point for the IRW metadata pipeline (Workflows 1 + 2 of
# .claude/skills/irw-site-update/SKILL.md). Regenerates the metadata CSVs,
# diffs them against what they replaced, and runs the cross-table audit --
# then writes a dated log so Ben can review at his convenience. Deliberately
# never runs Workflow 3 (upload_meta.py) or touches Redivis publish state;
# that stays a manual, explicit action after reviewing this log.
#
# After each run, opens a GitHub issue on ben-domingue/irw with the log
# attached and @ben-domingue tagged in the body, so GitHub emails a
# notification -- this is the alerting mechanism, run every week regardless
# of whether the diffs are empty.
set -uo pipefail

export PATH="/usr/local/bin:/usr/bin:/bin:$PATH"

REPO_DIR="$HOME/Dropbox/projects/irw/src"
META_DIR="$REPO_DIR/metadata"
SKILL_SCRIPTS="$REPO_DIR/.claude/skills/irw-site-update/scripts"
LOG_DIR="$META_DIR/pipeline_logs"
DATE="$(date +%F)"
LOG_FILE="$LOG_DIR/pipeline_run_${DATE}.md"
GH_REPO="ben-domingue/irw"
GH_MENTION="@ben-domingue"

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

if [[ "${rc1:-1}" -ne 0 || "${rc2:-1}" -ne 0 ]]; then
  STATUS="FAILED"
else
  STATUS="ok"
fi

ISSUE_BODY_FILE="$(mktemp)"
{
  echo "$GH_MENTION weekly metadata pipeline run for $DATE finished with status: **$STATUS**."
  echo
  echo "Full log: \`$LOG_FILE\`"
  echo
  cat "$LOG_FILE"
} > "$ISSUE_BODY_FILE"

# GitHub issue bodies cap at ~65536 chars; truncate the copy we upload if needed,
# the full log always stays on disk at $LOG_FILE regardless.
if [[ "$(wc -c < "$ISSUE_BODY_FILE")" -gt 60000 ]]; then
  head -c 60000 "$ISSUE_BODY_FILE" > "${ISSUE_BODY_FILE}.trunc"
  echo -e "\n\n... [truncated, see $LOG_FILE for full output]" >> "${ISSUE_BODY_FILE}.trunc"
  mv "${ISSUE_BODY_FILE}.trunc" "$ISSUE_BODY_FILE"
fi

gh issue create \
  --repo "$GH_REPO" \
  --title "IRW metadata pipeline run -- $DATE [$STATUS]" \
  --body-file "$ISSUE_BODY_FILE" \
  --assignee ben-domingue \
  >> "$LOG_FILE" 2>&1

rm -f "$ISSUE_BODY_FILE"

exit 0
