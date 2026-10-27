"""RepoChat Arena preference votes on code-repository questions (2024-2025).

Source: https://huggingface.co/datasets/lmarena-ai/repochat-arena-preference-4k,
one file `repochat_battles.json` (460 MB), CC BY 4.0 (the card's `license:` field).
RepoChat Arena is LMArena's variant in which a person pastes a GitHub repository
link, asks a question about it, and judges two anonymous models' answers.

3,844 battles between 13 named models, 2024-11-30 to 2025-02-11.

The contestant is really a pair. Each side runs a generating model AND a retriever
that chose which of the repository's files to put in context, and the two are drawn
independently: 1,932 battles used gemini-1.5-flash-002 as retriever_a and 1,912 used
gpt-4o-mini. `agent_a`/`agent_b` name the generating model only, because that is what
the vote is nominally about and what the leaderboard ranks; `retriever_a` and
`retriever_b` are kept as columns so the confound is visible rather than buried. A
Bradley-Terry fit that ignores them is fitting a mixture.

Why this is a competitions table: the 2026-10-08 shape rule. See
data/competitions/lmarena_text.py for the fuller argument.

Columns beyond the standard: outcome (model_a, model_b, tie or both_bad -- the
source's own `winner` field collapses the last two into "tie", but the separate
`tie` and `both_bad` booleans recover the distinction, and this column uses them),
retriever_a, retriever_b, and repo (the GitHub URL the question was about).

Choices:
- `winner` is "agent_a"/"agent_b"/"draw", score_a/score_b 1/0, 0/1 or 0.5/0.5.
- `date` is the source's `date` divided by 1000: it is milliseconds, and every value
  is midnight UTC, so this is a day, not a time of day.
- No `homefield` column. Slot assignment is balanced (each model is agent_a in
  50.00% of its appearances) and agent_a wins 1,264 of 2,607 decided battles,
  48.48%, z = -1.55 -- not the effect measured on `lmarena_text_2025` (z = -3.90),
  so no side is recorded as advantaged.
- `anony` is True on every row, so it is not kept as a column.
- The conversations (`full_conversation_a`, `full_conversation_b`), `conv_ids` and
  `conv_metadata` are not taken. The repo URL is kept because it is a public
  identifier of a public project, not user content.

Counts, 2026-10-27 run: 3,844 battles, 13 models, 2 retrievers, 2,377 distinct
repositories. agent_a 1,264, agent_b 1,343, draws 1,237 (717 tie, 520 both_bad).

Usage: python3 repochat_arena.py <dir holding repochat_battles.json> <output dir>
"""
import csv
import json
import sys
from pathlib import Path

COLUMNS = ["agent_a", "agent_b", "winner", "date", "score_a", "score_b", "outcome",
           "retriever_a", "retriever_b", "repo"]


def main(raw, out):
    battles = json.load(open(Path(raw) / "repochat_battles.json"))
    models, repos, retr = set(), set(), set()
    kept = selfplay = 0
    with open(Path(out) / "repochat_arena_2024_2025.csv", "w", newline="") as fo:
        w = csv.writer(fo)
        w.writerow(COLUMNS)
        for x in battles:
            a, b = x["model_a"], x["model_b"]
            if a == b:
                selfplay += 1
                continue
            ##`winner` pools tie and both_bad; the booleans do not.
            outcome = ("both_bad" if x["both_bad"] else
                       "tie" if x["tie"] else x["winner"])
            assert outcome in ("model_a", "model_b", "tie", "both_bad"), outcome
            win, sa, sb = (("agent_a", 1, 0) if outcome == "model_a" else
                           ("agent_b", 0, 1) if outcome == "model_b" else
                           ("draw", 0.5, 0.5))
            ##milliseconds, and always midnight UTC
            date = int(x["date"]) // 1000
            models.update((a, b))
            repos.add(x["github_link"])
            retr.update((x["retriever_a"], x["retriever_b"]))
            w.writerow([a, b, win, date, sa, sb, outcome, x["retriever_a"],
                        x["retriever_b"], x["github_link"]])
            kept += 1
    print(f"wrote {kept} battles, {len(models)} models, {len(retr)} retrievers, "
          f"{len(repos)} repos; dropped {selfplay} self-play", file=sys.stderr)
    assert kept > 0 and selfplay < kept / 100, (kept, selfplay)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
