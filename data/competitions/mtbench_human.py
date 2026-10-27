"""MT-Bench expert human pairwise judgments of six chat models (2023).

Source: https://huggingface.co/datasets/lmsys/mt_bench_human_judgments, file
`data/human-00000-of-00001-25f4910818759289.parquet`. CC BY 4.0 (the card's own
`license:` field). Collected for Zheng et al. (2023), "Judging LLM-as-a-Judge with
MT-Bench and Chatbot Arena".

Each row is one expert's judgment of two models' answers to one MT-Bench question,
at one turn of the two-turn conversation. 3,355 judgments by 65 named judges over
80 questions and 6 models. This is the small, careful counterpart to the crowd
arenas: the judges are the paper's authors and recruited graduate-student experts,
and each conversation is judged twice, once after turn 1 and once after turn 2.

Why this is a competitions table: under the 2026-10-08 shape rule the family covers
pairwise comparisons between fixed, named things, and the six models recur across
every question. It is the `carlson_2017_*` pattern -- a panel of coders comparing
two fixed items -- with models in place of texts.

The companion `gpt4_pair` split of the same deposit is NOT built. Those 2,400 rows
are GPT-4 judging the same pairs, so they are machine responses; they belong in
simsyn if anywhere, never in a table of human judgments. `judge` is constant
("gpt4_pair") there, which is how the two splits are told apart.

Columns beyond the standard: outcome (the judgment as recorded: model_a, model_b or
tie), rater (the judge label as published -- "author_N" for a paper author,
"expert_N" for a recruited expert; these are already pseudonyms in the source and
are not re-keyed, because the author/expert distinction is informative), question
(the MT-Bench question id, 81..160) and turn (1 or 2).

Choices:
- `winner` is "agent_a"/"agent_b"/"draw"; `outcome` keeps the source wording.
  score_a/score_b are 1/0, 0/1 or 0.5/0.5.
- No `date` and no `homefield` column. The deposit carries no timestamp, and an
  all-empty column is worse than an absent one. On homefield: slot assignment is
  balanced (each model is agent_a in 50.00% of its appearances) and agent_a wins
  1,293 of 2,575 decided judgments, 50.21%, z = +0.22 -- no detectable side effect,
  unlike `lmarena_text_2025` where the same test gives z = -3.90. Blank is the
  measured answer here, not an omission.
- A judgment is kept even when the same judge rated the same pair twice at the same
  turn; the count of such repeats is printed rather than dropped, because a repeated
  rating is data about the rater.

Counts, 2026-10-27 run: 3,355 judgments, 6 models, 65 raters, 80 questions.
agent_a 1,293, agent_b 1,282, draws 780. Turn 1 1,689, turn 2 1,666.

Usage: python3 mtbench_human.py <dir holding mtbench_human.parquet> <output dir>
"""
import collections
import csv
import sys
from pathlib import Path

import pyarrow.parquet as pq

COLUMNS = ["agent_a", "agent_b", "winner", "score_a", "score_b", "outcome",
           "rater", "question", "turn"]

RESULT = {"model_a": ("agent_a", 1, 0), "model_b": ("agent_b", 0, 1),
          "tie": ("draw", 0.5, 0.5)}


def main(raw, out):
    src = Path(raw) / "mtbench_human.parquet"
    d = pq.read_table(src, columns=["question_id", "model_a", "model_b", "winner",
                                    "judge", "turn"]).to_pydict()
    seen = collections.Counter()
    models, raters = set(), set()
    with open(Path(out) / "mtbench_human_2023.csv", "w", newline="") as fo:
        w = csv.writer(fo)
        w.writerow(COLUMNS)
        for i in range(len(d["winner"])):
            a, b = d["model_a"][i], d["model_b"][i]
            assert a != b, (i, a)
            judge = d["judge"][i]
            if isinstance(judge, (list, tuple)):      # stored as a one-element list
                judge = judge[0]
            win, sa, sb = RESULT[d["winner"][i]]
            seen[(judge, d["question_id"][i], a, b, d["turn"][i])] += 1
            models.update((a, b))
            raters.add(judge)
            w.writerow([a, b, win, sa, sb, d["winner"][i], judge,
                        d["question_id"][i], d["turn"][i]])
    repeats = sum(v - 1 for v in seen.values() if v > 1)
    print(f"wrote {len(d['winner'])} judgments, {len(models)} models, "
          f"{len(raters)} raters; {repeats} repeated judge x question x pair x turn",
          file=sys.stderr)
    assert len(d["winner"]) == 3355 and len(models) == 6, (len(d["winner"]), models)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
