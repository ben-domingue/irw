#!/usr/bin/env bash
# One round of the IRW item-text batch extraction (#1709). YOU run this; nothing
# schedules it.
#
# Decision (c) of extraction_batches/HANDOFF.md, settled 2026-09-04: rounds are
# fired deliberately, one per triage session, and there is no scheduler at all.
# The reasoning is worth keeping, because "add a scheduler later" is the obvious
# wrong turn:
#
#   - The bottleneck is triage, not the trigger. Roughly 8 of the 12 tables in a
#     round need a human go/no-go (BATCH_PROCESS, "Triage and staging"), and at
#     ~1,165 pending that is ~98 rounds. Any cadence faster than "when someone is
#     ready to triage a batch" just grows an unreviewed branch -- which is also
#     what makes this script's pre-round merge of origin/main start conflicting,
#     and a failed merge stops the queue entirely.
#   - A round costs real money. Measured on batch_019 (2026-09-04, and a SHORT
#     round -- four of its agents were killed by 429s): 670K output tokens, 2.3M
#     cache writes and 49.4M cache reads across the orchestrator and 12
#     subagents, about $56 at Opus 5 list rates. A clean round is nearer $60-70,
#     and draining the queue is $5.5-7k. Nothing should be able to spend that on
#     a timer.
#   - GitHub Actions was considered and rejected (the version-manifest job moved
#     there; this one should not). Three reasons: the work is fetching publisher
#     and repository sources, and a datacenter IP gets bot-walled far more than
#     this laptop does -- and a WAF block lands in queue_state.csv as `blocked`,
#     which quietly removes a table from the queue for good; a cloud runner is
#     cancelled and evicted more readily, and every death leaves 12 rows
#     in_progress that block all later rounds; and --dangerously-skip-permissions
#     in a PUBLIC repo, with secrets in the environment and public logs, around
#     an agent whose whole job is reading untrusted third-party files, is a
#     different risk from the same flag on a machine Ben is sitting at.
#
# --dangerously-skip-permissions is what lets the round run without a babysitter
# for its 20-40 minutes. It is bounded by two things, and if either stops being
# true this line is the one to revisit:
#   - The round CANNOT PUBLISH. It writes __items.csv into a batch directory and
#     stops. Triage, staging into itemtables/clean/ and upload are separate
#     manual steps. The worst case is spend, a mutated queue_state.csv and files
#     in a batch dir -- nothing a warehouse user can see.
#   - The batch cap in Step 0 of round_prompt_v1.md, read out of the prompt
#     below rather than duplicated here.
#
# The guards below duplicate the prompt's own Step 0 on purpose: checking them in
# bash costs nothing, and it means a capped or breakered queue never pays for an
# agent launch at all. extraction_batches/circuit_breaker.flag still stops a
# round; a bad round still sets it.
#
# It runs in its OWN worktree, never Ben's src checkout, which moved branch three
# times during the 2026-09-03 session -- twice mid-round. A round that reads a
# reparked tree gets the wrong protocol and a stale queue_state.csv. The branch
# guard below is not paranoia: on 2026-09-04 the runner worktree itself was found
# parked on an unrelated branch.
#
# Output goes to a dated log under cron_logs/ and to your terminal. A failure
# exits nonzero and says so -- there is no GitHub issue any more, because you are
# the one who started it and are watching.
set -uo pipefail

# Run from a snapshot, because this script edits itself.
#
# The round merges origin/main into the worktree (below) to pick up protocol
# changes -- and this file lives in that worktree, so a merge carrying a change
# to round_cron.sh rewrites the very file bash is executing.
#
# All three conditions for corruption hold here, and each was checked rather
# than assumed:
#
#   1. git rewrites the file IN PLACE, keeping the inode (verified in a scratch
#      repo: same inode before and after a merge that changed the content). Had
#      it renamed a new file into position, bash's open fd would still point at
#      the old inode and none of this would matter.
#   2. Bash reads a script lazily, in blocks, seeking by byte offset -- so after
#      an in-place change it resumes at the old offset in the NEW content.
#      Reproduced: a >8KB script that rewrites itself in place dies with
#      "unexpected EOF while looking for matching quote" partway down.
#   3. This file is over that boundary -- 8643 bytes on main when this was
#      written, against bash's 8KB read block -- so it takes more than one read.
#
# Observed live on 2026-09-04: the 05:13 round merged the standing-PR change to
# this file and ran on regardless. It survived; that was luck about where the
# edit landed relative to the read boundary, not design. The failure is silent,
# depends on the size of the incoming diff, and would surface as a mangled round
# rather than as anything naming this cause.
#
# So: copy ourselves somewhere git will never touch and exec that. The snapshot
# is what runs; the merge below can rewrite the original freely, and the next
# fire picks the new version up.
if [[ "${ROUND_SNAPSHOT:-}" != "1" ]]; then
  _snap="$(mktemp -t run_round.XXXXXX)" || exit 1
  cat "$0" > "$_snap" && chmod +x "$_snap" || { rm -f "$_snap"; exit 1; }
  ROUND_SNAPSHOT=1 "$_snap" "$@"
  _rc=$?
  rm -f "$_snap"
  exit "$_rc"
fi

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

mkdir -p "$LOG_DIR"

# A subshell, not a brace group: the steps use `exit` to stop early, and in a
# brace group that would exit the whole script and skip the reporting below.
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

  # --dangerously-skip-permissions is what lets the round run for its 20-40
  # minutes without a babysitter. It is bounded by the fact that the round cannot
  # publish, and by the cap above. If that stops being true, this line is the one
  # to revisit. See the header for why this posture is defensible here and would
  # not be on a cloud runner.
  #
  # Keep a copy of the transcript so the rate-limit check below can read it; the
  # copy is deleted at the end of the round.
  _agent_out="$(mktemp -t round_agent.XXXXXX)"
  claude -p "$(cat "$PROMPT")" \
    --dangerously-skip-permissions 2>&1 | tee "$_agent_out"
  rc="${PIPESTATUS[0]}"
  echo
  echo "Round agent exited $rc at $(date -Is)."

  # A 429 does NOT fail the round. When subagents are killed by a rate limit or a
  # spend cap the orchestrator finishes and exits 0, so nothing above notices and
  # the round self-reports as a normal completion with a poor yield. That has
  # already cost real work: in batch_018 eight of twelve agents were killed this
  # way, and in batch_019 three were -- two of which had actually FINISHED, with
  # a complete 65-row items CSV on disk, and were reported as plain failures
  # because the harness shows an agent's first message, not its last.
  #
  # So say it out loud. A round that hit a limit is not a round whose blocked and
  # failed counts mean anything, and its batch directory must be read before
  # queue_state.csv is believed.
  if grep -qiE '(rate.?limit|429|spend (cap|limit)|usage limit)' "$_agent_out"; then
    echo
    echo "WARNING: the transcript mentions a rate limit / spend cap. Some agents"
    echo "were probably killed. Before trusting this round's classifications, ls"
    echo "the batch directory -- a killed agent may have written a complete table"
    echo "and still been reported as failed. Do not mark those tables 'blocked'."
  fi
  rm -f "$_agent_out"

  [[ "$rc" -ne 0 ]] && exit "$rc"

  # The round commits its own work (BATCH_PROCESS "Repo hygiene"). Push it, so
  # a round's output is never stranded on a local branch -- an unpushed branch
  # has cost this project published tables before.
  #
  # The remote branch may not exist: merging the standing PR with --delete-branch
  # removes it, which is what happened to #1904. When it is gone the range
  # `origin/$BRANCH..HEAD` is not a revision at all -- git exits 128 and prints
  # nothing, so the old `-n "$(...)"` test read as "nothing to push" and the
  # round's commits stayed local. That is precisely the stranded-branch failure
  # the paragraph above is about, so check the ref exists before using the range.
  if ! git rev-parse --verify --quiet "origin/$BRANCH" >/dev/null \
     || [[ -n "$(git log --oneline "origin/$BRANCH..HEAD")" ]]; then
    git push -u origin "$BRANCH" 2>&1 || {
      echo "ERROR: push failed. The round's commits are local only."
      exit 1
    }
    echo "Pushed."
  else
    echo "Nothing new to push."
  fi

  # A STANDING pull request, opened once and left open. Rounds accumulate into
  # it; it is not one PR per round.
  #
  # Without this the branch just grows: rounds pile up unreviewed, and the
  # further it drifts from main the likelier the wrapper's pre-round merge is to
  # hit a conflict -- which stops the queue entirely, since a failed merge skips
  # the round. It is also the review surface the work actually needs: roughly 8
  # of the 12 tables in a round want a human go/no-go before anything is staged
  # for upload, and a PR is where that happens.
  #
  # MERGE THIS PR WITHOUT DELETING THE BRANCH. "Standing" depends on it: #1904
  # was merged with --delete-branch, which removed origin/itemtext/queue-rounds,
  # broke the push check above and meant the next round would open a fresh PR
  # rather than accumulate into one. GitHub's "delete branch" button after a
  # merge does the same thing.
  #
  # Failure here is deliberately NOT fatal. The round's work is already
  # committed and pushed by this point, and losing a PR link is not worth
  # failing or re-running a round for.
  open_pr="$(gh pr list --repo "$GH_REPO" --head "$BRANCH" --state open \
    --json number --jq '.[0].number' 2>/dev/null)"
  if [[ -n "$open_pr" ]]; then
    echo "Standing PR #$open_pr already open; this round's commits are on it."
  else
    gh pr create --repo "$GH_REPO" --base main --head "$BRANCH" \
      --title "itemtext: extraction rounds from the queue runner" \
      --body "Standing PR for \`$BRANCH\`, opened automatically by \
\`itemtext/extraction_batches/run_round.sh\`. Rounds accumulate here rather than \
opening a PR each; it stays open between merges.

**Nothing here is published.** A round writes \`__items.csv\` into a batch directory and \
stops -- triage, staging into \`itemtables/clean/\` and upload are all separate manual \
steps. Merging this PR commits the extractions to the repo, not to the warehouse.

Review per \`itemtext/BATCH_PROCESS.md\` § 'Triage and staging'. Round-by-round detail is \
in \`extraction_batches/round_log.md\` and the per-round logs under \
\`extraction_batches/cron_logs/\` (untracked, local to the runner worktree).

**Do not delete the branch when merging.** Rounds accumulate into this one PR; deleting \
\`$BRANCH\` on merge breaks the runner's push check and starts a new PR per round." \
      2>&1 | tail -2
    echo "Opened the standing PR."
  fi
  exit 0
) 2>&1 | tee "$LOG_FILE"

# tee is the last command in the pipe, so take the subshell's status, not tee's.
rc="${PIPESTATUS[0]}"
if [[ "$rc" -ne 0 ]]; then
  echo
  echo "ROUND FAILED (exit $rc). Log: $LOG_FILE"
  echo "Nothing was published -- rounds cannot publish -- but the queue may have"
  echo "rows left in_progress, which blocks every later round until you reconcile"
  echo "them. Check the batch directory before touching queue_state.csv: a killed"
  echo "agent often finished its table first."
fi

exit "$rc"
