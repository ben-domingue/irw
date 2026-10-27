"""LMArena text-arena human preference votes, April to July 2025 (#3183 follow-up).

Source: https://huggingface.co/datasets/lmarena-ai/arena-human-preference-140k,
seven parquet shards `data/train-0000{0..6}-of-00007.parquet`, 1.6 GB, 135,634 votes.
Each row is one vote in which a person was shown two anonymous language models'
answers to their own prompt and picked one, declared a tie, or said both were bad.

Licence: the dataset card states "User prompts are licensed under CC-BY-4.0, and model
outputs are governed by the terms of use set by the respective model providers." This
table publishes neither the prompts nor the outputs -- only the two model names, the
vote, a re-keyed session identifier, and the per-vote annotations LMArena ships. So the
only material taken is under CC BY 4.0, and the provider-terms clause does not reach it.
The HuggingFace card's own `license:` field reads cc-by-4.0.

Why this is a competitions table. Under the 2026-10-08 shape rule, competitions covers
pairwise comparisons between fixed, named things, preference votes included. The
contestants here are 53 named models that recur across the corpus, which is the
`carlson_2017_*` pattern (crowd coders comparing texts) with models in place of texts.

Columns beyond the standard: outcome (the vote as recorded: model_a, model_b, tie,
both_bad), rater (the evaluation session, re-keyed, see below), eval_order (the vote's
position within its session, 1..28), language (BCP-47 as LMArena detected it, 126
values incl. "und"), turns (conversation turns the vote covered), is_code, math,
creative_writing, instruction_following and hardness. The last five come from
`category_tag`, LMArena's own automatic annotations of the prompt: the first four are
0/1 flags, and hardness counts how many of the seven `criteria_v0.1` booleans
(complexity, creativity, domain_knowledge, problem_solving, real_world, specificity,
technical_accuracy) are true, so 0..7.

Choices:
- `rater` is `evaluation_session_id` re-keyed to 1..n in order of first appearance; the
  mapping is not kept, and the source UUIDs are not published. A session is one person's
  sitting and can hold several votes, so `rater` + `eval_order` give an ordered sequence
  per rater. It is a weak person identifier: 102,166 of 115,372 sessions hold a single
  vote, and nothing links two sessions by the same person. Do not read it as a panel.
- `homefield` is "agent_b" in every row, and that is an empirical finding rather than a
  convention. Slot assignment is balanced -- each model appears as agent_a in 50.00% of
  its battles -- so the marginal is an unbiased estimate of the slot effect, and agent_a
  wins only 48,559 of 98,341 decided battles, 49.38% (z = -3.90 against 0.5). Restricting
  to within-matchup comparisons gives the same 49.38%. The effect is real but small, and
  it is the reason slot order is worth recording at all: a post-hoc shuffle at export
  would have produced exactly 50%, so the a/b ordering carries something systematic,
  most plausibly which pane the answer appeared in. Anyone fitting Elo or Bradley-Terry
  here should carry a slot term; anyone treating 0.6 percentage points as a meaningful
  home advantage should not.
- `winner` is "agent_a"/"agent_b"/"draw". Both tie and both_bad become "draw", because
  the standard allows three values; `outcome` keeps the distinction. score_a/score_b are
  1/0, 0/1 or 0.5/0.5 to match.
- `date` is the vote's timestamp in Unix seconds.
- Dropped: votes where the same model was drawn on both sides (10 rows); nothing else.
  No row has a null in any column used, and the 135,634 source `id` values are unique.

Counts, 2026-10-27 run: 135,624 votes between 53 models, 115,363 raters. Votes run
2025-04-17 to 2025-07-24. agent_a wins 48,559, agent_b 49,782, draws 37,283 (21,529
ties and 15,754 both_bad). Languages: en 71,169, pl 13,813, und 11,833, ru 9,262,
zh 6,501, then 121 more. Hardness is skewed high: 30,644 votes score 7 of 7 and
12,183 score 0.

Not taken from the source: conversation_a, conversation_b and full_conversation (the
prompt and both answers), and conv_metadata's token and markdown counts, which exist
for style control and describe text this table does not carry.

Usage: python3 lmarena_text.py <dir holding the seven parquet shards> <output dir>
"""
import csv
import sys
from pathlib import Path

import pyarrow.parquet as pq

COLUMNS = ["agent_a", "agent_b", "winner", "date", "homefield", "score_a", "score_b",
           "outcome", "rater", "eval_order", "language", "turns", "is_code", "math",
           "creative_writing", "instruction_following", "hardness"]

READ = ["id", "model_a", "model_b", "winner", "evaluation_session_id",
        "evaluation_order", "category_tag", "conv_metadata", "language", "is_code",
        "timestamp"]

CRITERIA = ("complexity", "creativity", "domain_knowledge", "problem_solving",
            "real_world", "specificity", "technical_accuracy")

#: winner as recorded -> (winner column, score_a, score_b)
RESULT = {"model_a": ("agent_a", 1, 0), "model_b": ("agent_b", 0, 1),
          "tie": ("draw", 0.5, 0.5), "both_bad": ("draw", 0.5, 0.5)}


def main(raw, out):
    shards = sorted(Path(raw).glob("train-*-of-00007.parquet"))
    assert len(shards) == 7, shards
    raters, ids, models = {}, set(), set()
    kept = selfplay = 0
    with open(Path(out) / "lmarena_text_2025.csv", "w", newline="") as fo:
        w = csv.writer(fo)
        w.writerow(COLUMNS)
        for shard in shards:
            d = pq.read_table(shard, columns=READ).to_pydict()
            for i in range(len(d["id"])):
                a, b = d["model_a"][i], d["model_b"][i]
                assert d["id"][i] not in ids, d["id"][i]
                ids.add(d["id"][i])
                if a == b:
                    selfplay += 1
                    continue
                models.update((a, b))
                sess = d["evaluation_session_id"][i]
                if sess not in raters:
                    raters[sess] = len(raters) + 1
                win, sa, sb = RESULT[d["winner"][i]]
                tag = d["category_tag"][i]
                hardness = sum(1 for c in CRITERIA if tag["criteria_v0.1"][c])
                w.writerow([
                    a, b, win, int(d["timestamp"][i].timestamp()), "agent_b", sa, sb,
                    d["winner"][i], raters[sess], d["evaluation_order"][i],
                    d["language"][i], d["conv_metadata"][i]["turns"],
                    int(d["is_code"][i]), int(tag["math_v0.1"]["math"]),
                    int(tag["creative_writing_v0.1"]["creative_writing"]),
                    int(tag["if_v0.1"]["if"]), hardness])
                kept += 1
    print(f"kept {kept} votes, {len(models)} models, {len(raters)} raters; "
          f"dropped {selfplay} self-play", file=sys.stderr)
    assert kept > 0 and selfplay < kept / 100, (kept, selfplay)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
