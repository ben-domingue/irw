# Judgement-class triage, 2026-09-29 (#2401, RULES.md Decision 5)

Per-family verdicts are in `judgement.csv`. All 75 flagged tables are covered, in 51 family rows. The work was read-only. Evidence came from:
- the `data/` scripts;
- live item text (`irw_text`, whose `resp` column gives the code behind each option);
- source codebooks fetched for ENCASBA 2024, EANNA 2023 and EUTIC 2022;
- `corpus.jsonl.gz` histograms.

No whole-table downloads.

## Counts

| class | verdict | families | tables |
|---|---|---|---|
| `resp_binary_plus` | real | 4 | 11 |
| | false_positive | 28 | 42 |
| | unsure | 2 | 2 |
| `resp_mixed_scale` | real | 4 | 4 |
| | false_positive | 8 | 11 |
| | unsure | 1 | 1 |
| `rt_units` | real | 4 | 4 |

The chile social-welfare mixed-scale tables are split into three rows (`yy`, `u`, `rr`) because their verdicts differ.

## The confirmed batch

**`resp_binary_plus`, 4 families.** Fixing these touches 20 tables: 11 flagged, plus 9 unflagged siblings with the same defect.

- **guatemala_2024_homes:**
  - The fix covers 8 flagged tables plus 7 unflagged siblings (water, trash, avenues, roads, safety, emergencies, nutrition).
  - In every "De acuerdo con su experiencia…" grid, 3 is the questionnaire's `NS` column. Set it to NA.
  - `country` and `transparency` are genuine 3-point items. Leave them alone.
- **chile_2023_social-welfare-survey_h:**
  - The flagged item `h1` is a real 3-point item.
  - The actual defect is on `h3_d` and `h3_e`, where 3 means "no children in the household" or "doesn't use public transport". Those codes make up 57% and 23% of the rows, so the <5% rule couldn't see them. Set them to NA.
- **EEN_Lacey_2024_Parent:**
  - `mh_treatable` is coded No=0/Yes=1/Maybe=2. Reorder it to 0/1/2 = No/Maybe/Yes, or set Maybe to NA.
  - Also set `covid_jobloss` 2 ("Not employed") to NA.
- **spain_2013_services_complaints:** set `p27c` 3 ("still being processed") to NA.

**`resp_mixed_scale`, 4 families:**
- **chile cp_c:** in `cp9_*`, the "88:88 no sabe" time code has been parsed to 89.47 hours. Set it to NA.
- **chile yy:** `yy3` is household income in pesos. Move it to a covariate or drop it.
- **DEMOS:** the table holds per-stimulus means, which are composites. That needs a withdraw or known-issue decision, not a units fix.
- **mclaughlin:** already in Decision 8's rebuild batch.

**`rt_units`, all 4 tables:** divide rt by 1000. Every median (610 to 2660) is a typical per-trial time in ms and an impossible one in seconds. Each script copies the raw rt through unchanged.

**Unsure, 3 families:**
- `sel_marca_2025_familiares`: the codebook is on a private OSF node.
- `western_reserve_project`: item ids are opaque.
- `chile_2023_social-welfare-survey_u`: the 14 `u*_a` items are minutes of travel or wait time. Are they items at all?

## Out-of-class findings from the same evidence (not in the CSV verdicts)

- **spain_2013_services_internet (`p21xx`) and `_purpose` (`p11xx`):**
  - Every item carries the same count of 0s (1,350 and 591). The item text maps 0 to "No procede", which looks like a skip leak.
  - The main checkout also has uncommitted edits to `data/spain_2013_services.do`. Coordinate before touching it.
- **Chile don't-know dummies:** `f4_88`/`f4_99` in chile social-welfare `_f` are don't-know/refuse indicator dummies shipped as items. So are `n7_77…n8_99` in children `_n`, and `n10` there is nominal.
- **deception_professors:** 3,262 non-numeric `resp` values.
- **magnus-format-study2:** attention-check `AC*` items are shipped as items, and there are lone 0s on the 1–3 PS items.
- **daiku_2021:** one respondent has 150 on `stranger_indirect`, where the next highest value is 12.

## Would a threshold change remove the false positives?

**Not by a threshold alone.** I replayed candidate rules over `corpus.jsonl.gz`:

- **Minority-share floor on the pure-binary sibling (5–20%):** keeps 24–34 of the false positives. It also starts dropping real ones.
- **Table max ≤ extra code, "no polytomous siblings":** keeps 0 of 10 real tables. The Guatemala tables all carry a 1–10 satisfaction item.
- **Majority of items binary:** removes almost nothing.

The one structural signal that separates the two groups is **the coding of the core pair**:

- A `{0,1}` core plus 2 is almost always partial credit or a 0–2 clinical scale: PISA ×8, sirt, CBCL, RPQ, HAMD, heise. EEN is the only real `{0,1}+2` case.
- A `{1,2}` core plus 3 is the survey convention (Sí=1, No=2, NS=3). That covers every real Guatemala, Chile and Spain case.

Suggested rule for `_flags` (not applied):

```python
# resp_binary_plus: survey yes/no (1=yes, 2=no) with a trailing 3
if core == {1, 2} and x == 3 and share < 0.05 \
   and not any(4 <= max(s) <= 7 for s in sets.values()):   # no short-Likert siblings
```

Replayed over the whole corpus, this flags 11 tables:
- the 8 flagged Guatemala tables;
- `goldberg_2018_prs_peo`, `goldberg_2018_spa_spey` and `vanteffelen_2020_rpq`, which are real 1–3 scales.

Precision rises from about 20% (11 of 55) to 73% (8 of 11). The cost is recall: it loses spain `p27c` and EEN, whose siblings are Likert or `{0,1}`-coded, and it still can't see chile `h3_d/e` or the 7 unflagged Guatemala tables, whose "don't know" share is above 5%.

So the higher-yield change is not a threshold at all:

1. **Option-text rule** for any table with item text: flag a numeric `resp` whose `option_text` matches `no sabe|no aplica|no procede|tramit|no usa|no hay|don't know|not applicable|not employed|maybe|prefer not`. A scan of the chile/spain/EEN item text with this pattern found every real case above, including the unflagged ones (h3_d, h3_e, covid_jobloss, the spain 0="No procede").
2. **Fix by script, not by table.** Once one table in a family is confirmed, sweep every table the same script writes. The Guatemala A-grid fix owed 15 tables; the detector saw 8.

**`resp_mixed_scale`:**
- About half the false positives are 0–100 sliders or estimates in a multi-format battery: deception ×2, rioux ×3, wang, wine.
- **Suggested change:** skip "wide" items whose support is within [0,100] and whose max is 100, and skip items already flagged by `resp_sentinel` (piterova).
- **Effect:** 7 of the 11 false-positive tables are removed (rioux ×3, deception_game, wang, wine, piterova) and no confirmed real ones. mclaughlin also drops, but it is already scheduled under Decision 8.
- **What's left:** DEMOS, chile cp_c/yy/u/rr, daiku, opladen and deception_professors (whose estimates top out at 82 or 91). Precision is 3 of 8.
- **A second cheap addition:** flag a wide item whose value clusters at 88–99.x, which catches HH:MM-parsed sentinels like chile's 89.47.

**`rt_units`:** 4 of 4 are real. Keep the threshold.
