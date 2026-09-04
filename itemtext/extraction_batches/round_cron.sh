#!/usr/bin/env bash
# Cron entry point for one round of the IRW item-text batch extraction (#1709).
#
# Shaped after metadata/version_manifest_cron.sh and weekly_pipeline_cron.sh --
# dated log, guards before any work, a GitHub issue on failure so GitHub mails
# Ben. It differs from both in one respect that is worth stating plainly: those
# two run deterministic scripts, and this one launches an AGENT. It is the first
# unattended agent in this repo (decision (c) of extraction_batches/HANDOFF.md,
# ruled 2026-09-04).
#
# What bounds it:
#   - The round CANNOT PUBLISH. It writes __items.csv into a batch directory and
#     stops. Triage, staging into itemtables/clean/ and upload are separate
#     manual steps. The worst case here is spend, a mutated queue_state.csv and
#     files in a batch dir -- nothing a warehouse user can see. This is the same
#     rule weekly_pipeline_cron.sh follows by never running upload_meta.py.
#   - The batch cap in Step 0 of round_prompt_v1.md. Raise it deliberately;
#     when it is reached this script stops firing rounds and says so.
#   - extraction_batches/circuit_breaker.flag, which a bad round sets.
#
# The guards below duplicate the prompt's own Step 0 on purpose: checking them
# in bash costs nothing, and it means a capped or breakered queue never pays for
# an agent launch at all.
#
# It runs in its OWN worktree, never Ben's src checkout, which moved branch
# three times during the 2026-09-03 session -- twice mid-round. A round that
# reads a reparked tree gets the wrong protocol and a stale queue_state.csv.
set -uo pipefail

export PATH="/home/ben/.local/bin:/usr/local/bin:/usr/bin:/bin:$PATH"

WORKTREE="/home/ben/irw-queue-runner"
BRANCH="itemtext/queue-rounds"
ITEMTEXT="$WORKTREE/itemtext"
PROMPT="$ITEMTEXT/extraction_batches/round_prompt_v1.md"
QUEUE="$ITEMTEXT/extraction_batches/queue_state.csv"
LOG_DIR="$ITEMTEXT/extraction_batches/cron_logs"
DATE="$(date +%F)"
STAMP="$(date +%F_%H%M)"
LOG_FILE="$LOG_DIR/round_${STAMP}.log"
GH_REPO="ben-domingue/irw"
GH_MENTION="@ben-domingue"

mkdir -p "$LOG_DIR"

alert() {
  # $1 = title suffix, $2 = body preamble. The log is on disk either way; the
  # issue exists so GitHub sends mail.
  local body
  body="$(mktemp)"
  {
    echo "$GH_MENTION $2"
    echo
    echo "Log: \`$LOG_FILE\`"
    echo
    echo '```'
    tail -c 50000 "$LOG_FILE"
    echo '```'
  } > "$body"
  gh issue create --repo "$GH_REPO" \
    --title "IRW itemtext round -- $STAMP [$1]" \
    --body-file "$body" --assignee ben-domingue >> "$LOG_FILE" 2>&1
  rm -f "$body"
}

# A subshell, not a brace group: the steps use `exit` to stop early, and in a
# brace group that would exit the whole script and skip the alerting.
(
  echo "# IRW itemtext extraction round -- $STAMP"
  echo

  [[ -d "$ITEMTEXT" ]] || { echo "ERROR: no worktree at $WORKTREE."; exit 1; }
  cd "$WORKTREE" || exit 1

  branch="$(git rev-parse --abbrev-ref HEAD)"
  if [[ "$branch" != "$BRANCH" ]]; then
    echo "SKIP: worktree is on '$branch', not '$BRANCH'. Nothing done."
    exit 0
  fi
  if [[ -n "$(git status --porcelain)" ]]; then
    echo "SKIP: worktree is dirty. A previous round may have died mid-write;"
    echo "that needs a human before another round claims tables."
    git status --porcelain
    exit 0
  fi

  # Pick up protocol changes merged to main -- a raised cap, a new gate, the
  # rights rule. A merge, never a rebase or a reset: this branch carries the
  # rounds' own commits and unattended history rewriting is not worth the risk.
  git fetch origin --quiet || { echo "ERROR: fetch failed."; exit 1; }
  if ! git merge --no-edit origin/main >/dev/null 2>&1; then
    git merge --abort 2>/dev/null
    echo "ERROR: could not merge origin/main cleanly. Conflict needs a human;"
    echo "no round was run."
    exit 1
  fi

  # --- Step 0's stop conditions, checked before paying for an agent ---

  if [[ -f "$ITEMTEXT/extraction_batches/circuit_breaker.flag" ]]; then
    echo "SKIP: circuit_breaker.flag is set. A prior round tripped it and human"
    echo "review is pending. Delete the flag to resume."
    exit 0
  fi

  in_flight="$(awk -F, 'NR>1 && $2=="in_progress"' "$QUEUE" | wc -l)"
  if [[ "$in_flight" -gt 0 ]]; then
    echo "SKIP: $in_flight row(s) still in_progress -- a round is running, or"
    echo "died mid-round. Not claiming tables. Reconciling in_progress rows back"
    echo "to pending is a HUMAN decision (a dead round may have left half-written"
    echo "files), so this will keep skipping until someone looks."
    awk -F, 'NR>1 && $2=="in_progress"' "$QUEUE"
    exit 0
  fi

  pending="$(awk -F, 'NR>1 && $2=="pending"' "$QUEUE" | wc -l)"
  if [[ "$pending" -eq 0 ]]; then
    echo "SKIP: queue exhausted, 0 pending rows."
    exit 0
  fi

  # The cap. Step 0 names the batch that must not already exist; read it from
  # the prompt rather than duplicating the number here, so raising the cap in
  # one place is enough.
  cap="$(grep -oP 'itemtables/\Kbatch_\d+(?= already exists \(round cap reached\))' "$PROMPT" | head -1)"
  if [[ -z "$cap" ]]; then
    echo "ERROR: could not read the round cap out of $PROMPT."
    exit 1
  fi
  if [[ -d "$ITEMTEXT/itemtables/$cap" ]]; then
    echo "SKIP: round cap reached ($cap exists). Raise it in Step 0 of BOTH"
    echo "BATCH_PROCESS.md and round_prompt_v1.md to run more rounds. Note the"
    echo "off-by-one: the cap allows rounds UP TO AND INCLUDING that batch."
    exit 0
  fi

  echo "Guards clear: $pending pending, cap $cap not yet reached."
  echo "Launching round agent at $(date -Is)."
  echo

  # --skip-permissions is what makes this unattended. It is bounded by the fact
  # that the round cannot publish, and by the cap above. If that stops being
  # true, this line is the one to revisit.
  claude -p "$(cat "$PROMPT")" \
    --dangerously-skip-permissions 2>&1
  rc=$?
  echo
  echo "Round agent exited $rc at $(date -Is)."
  [[ "$rc" -ne 0 ]] && exit "$rc"

  # The round commits its own work (BATCH_PROCESS "Repo hygiene"). Push it, so
  # a round's output is never stranded on a local branch -- an unpushed branch
  # has cost this project published tables before.
  if [[ -n "$(git log --oneline "origin/$BRANCH..HEAD" 2>/dev/null)" ]]; then
    git push -u origin "$BRANCH" 2>&1 || {
      echo "ERROR: push failed. The round's commits are local only."
      exit 1
    }
    echo "Pushed."
  else
    echo "Nothing new to push."
  fi
  exit 0
) > "$LOG_FILE" 2>&1

rc=$?
if [[ "$rc" -ne 0 ]]; then
  alert "FAILED" "an unattended item-text extraction round failed. Nothing was \
published -- rounds cannot publish -- but the queue may have rows left \
in_progress, which blocks every later round until a human reconciles them."
fi

exit 0
