"""LMArena text-arena preference votes, the 55k Kaggle release.

Source: https://huggingface.co/datasets/lmarena-ai/arena-human-preference-55k, one
file `train.csv` (176 MB), Apache 2.0 (the card's `license:` field). This is the
training split LMArena published for the Kaggle competition "LMSYS - Chatbot Arena
Human Preference Predictions".

Each row is one vote: a person saw two anonymous language models answer their own
prompt and picked one, or called it a tie. 57,477 votes between 64 named models.

Relation to `lmarena_text_2025`, built from the same organisation's 140k release:
these are different votes. The two use incompatible id schemes (ten-digit integers
here, UUIDs there) so they cannot be joined, but the 140k covers 2025-04-17 to
2025-07-24 with 53 models while this release predates it and has a 64-model roster
including the 2023-era entrants (vicuna, koala, alpaca, llama-2). Treat them as two
tables, not one series: this one has no timestamps at all, so it cannot be ordered
or sliced by time.

Why this is a competitions table: the 2026-10-08 shape rule puts pairwise preference
votes between fixed, named things in the family. See data/competitions/lmarena_text.py
for the fuller argument.

Columns beyond the standard: none. The source carries no timestamp, no voter
identifier and no annotations -- only the pair, the vote, the prompt and the two
responses, and the last three are not taken.

Choices:
- The source codes the result as three indicator columns, winner_model_a /
  winner_model_b / winner_tie, exactly one of which is 1. `winner` is
  "agent_a"/"agent_b"/"draw" and score_a/score_b are 1/0, 0/1 or 0.5/0.5.
  There is NO `outcome` column, unlike the other arena tables: this release has no
  both_bad category, so "tie" here silently pools genuine ties with both-bad votes
  that the live arena recorded separately. Do not compare its draw rate (30.9%) with
  `lmarena_text_2025`'s without that in mind.
- No `date` and no `homefield` column. There are no timestamps. On homefield: slot
  assignment is balanced (each model is agent_a in 50.00% of its appearances) and
  agent_a wins 20,064 of 39,716 decided votes, 50.52%, z = +2.07. That is short of
  the z = -3.90 measured on `lmarena_text_2025`, so no side is recorded as having an
  advantage here; the column is absent rather than blank-filled.
- `prompt`, `response_a` and `response_b` are not taken. They are 99% of the file.

Counts, 2026-10-27 run: 57,477 votes, 64 models, no self-play rows and no duplicate
id. agent_a 20,064, agent_b 19,652, draws 17,761.

Usage: python3 lmarena_text_55k.py <dir holding arena55k_train.csv> <output dir>
"""
import csv
import sys
from pathlib import Path

csv.field_size_limit(10 ** 9)      # response_a/response_b run to hundreds of KB

COLUMNS = ["agent_a", "agent_b", "winner", "score_a", "score_b"]


def main(raw, out):
    src = Path(raw) / "arena55k_train.csv"
    ids, models = set(), set()
    kept = selfplay = 0
    with open(src, newline="") as f, \
            open(Path(out) / "lmarena_text_55k.csv", "w", newline="") as fo:
        w = csv.writer(fo)
        w.writerow(COLUMNS)
        for r in csv.DictReader(f):
            assert r["id"] not in ids, r["id"]
            ids.add(r["id"])
            a, b = r["model_a"], r["model_b"]
            if a == b:
                selfplay += 1
                continue
            flags = (r["winner_model_a"], r["winner_model_b"], r["winner_tie"])
            assert flags.count("1") == 1, (r["id"], flags)
            win, sa, sb = (("agent_a", 1, 0) if flags[0] == "1" else
                           ("agent_b", 0, 1) if flags[1] == "1" else
                           ("draw", 0.5, 0.5))
            models.update((a, b))
            w.writerow([a, b, win, sa, sb])
            kept += 1
    print(f"wrote {kept} votes, {len(models)} models; dropped {selfplay} self-play",
          file=sys.stderr)
    assert kept > 0 and selfplay < kept / 100, (kept, selfplay)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
