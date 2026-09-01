"""What adopting Rule A actually changes, before anything publishes (#1760).

Compares the derived age tags against the currently published `metadata/tags.csv`
and writes a markdown summary. Step 5 of the adoption checklist in
tags/decisions/1760_age_range_and_sample.md: the diff is reported and reviewed
BEFORE the pipeline runs, not after.
"""
import collections
import datetime
import os

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)

tags = pd.read_csv(os.path.join(SRC, "metadata", "tags.csv"))
der = pd.read_csv(os.path.join(HERE, "age_range_derived.csv"))
audit = pd.read_csv(os.path.join(HERE, "age_range_audit.csv"))
qpath = os.path.join(HERE, "age_range_quarantine.csv")
quar = pd.read_csv(qpath) if os.path.exists(qpath) else pd.DataFrame()

cur = dict(zip(tags["table"].str.lower(), tags["age range"]))
rows = []
for r in der.itertuples():
    was = cur.get(str(r.table).lower(), None)
    now = getattr(r, "_2")            # 'age range' is not a valid identifier
    if str(r.table).lower() not in cur:
        kind = "new row"
    elif str(was) == "Non-human":
        # 03_tags.R refuses this override; the report must show the same thing.
        kind = "Non-human preserved"
    elif (pd.isna(was) and pd.isna(now)) or str(was) == str(now):
        kind = "confirmed"
    elif pd.isna(was):
        kind = "filled a blank"
    else:
        kind = "changed"
    rows.append({"table": r.table, "was": was, "now": now, "kind": kind})
d = pd.DataFrame(rows)

lines = [f"# Rule A dry run — {datetime.date.today().isoformat()}", "",
         f"Derived from each table's own `cov_age`, Redivis-side. Nothing has been published.", ""]

lines += ["## What happens to the published column", "",
          "| outcome | tables |", "|---|---|"]
for k, n in d["kind"].value_counts().items():
    lines.append(f"| {k} | {n:,} |")
lines += [f"| **total derived** | **{len(d):,}** |", ""]

ch = d[d["kind"] == "changed"]
lines += ["## Every change, by direction", "",
          "| from | to | tables |", "|---|---|---|"]
for (a, b), n in collections.Counter(zip(ch["was"], ch["now"])).most_common():
    lines.append(f"| `{a}` | `{b}` | {n:,} |")
lines.append("")

lines += ["## Tables the rule declined to touch", "",
          "| verdict | tables | why |", "|---|---|---|"]
un = audit[audit["verdict"] == "unusable"]
for reason, n in collections.Counter(
        un["reason"].str.replace(r"\d+", "N", regex=True)).most_common(8):
    lines.append(f"| unusable | {n:,} | {reason} |")
if len(quar):
    lines.append(f"| quarantine | {len(quar):,} | ages equally consistent with months; held for a human |")
lines.append("")

near = audit[audit["reason"].fillna("").str.contains("not Mixed")]
lines += ["## Where the 2% floor decided the tag", "",
          f"{len(near)} table(s) have respondents on both sides of 18 but too few "
          "on the smaller side to count as `Mixed`.", ""]
if len(near):
    lines += ["| table | ages | under 18 | of | share | tag |", "|---|---|---|---|---|---|"]
    for r in near.sort_values("share_under_18", ascending=False).head(15).itertuples():
        lines.append(f"| `{r.table}` | {r.min_age:.0f}–{r.max_age:.0f} | {r.n_u18} | "
                     f"{r.n_u18 + r.n_a18} | {r.share_under_18:.2%} | `{getattr(r, '_14')}` |")
    lines.append("")

lines += ["## The #1760 tables", "",
          "The six named in the issue, plus the `sample` example.", "",
          "| table | was | now |", "|---|---|---|"]
for t in ["colombia_2023_politics_voting", "mexico_2023_quality_wellbeingservice",
          "spain_2025_democracy_parties", "spain_2024_politics_beliefs",
          "margaretto_2025_translation_study_2_lextale", "silvia_2024_funny",
          "mexico_2023_quality_low"]:
    r = d[d["table"].str.lower() == t]
    if len(r):
        lines.append(f"| `{t}` | `{r.iloc[0]['was']}` | `{r.iloc[0]['now']}` |")
    else:
        lines.append(f"| `{t}` | — | *not derived* |")
lines.append("")

out = os.path.join(HERE, "age_range_dry_run.md")
open(out, "w").write("\n".join(lines) + "\n")
d.to_csv(os.path.join(HERE, "age_range_dry_run.csv"), index=False)
print("\n".join(lines))
print(f"\nwrote {out}")
