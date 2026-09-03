# The two tagging paths: what they are, and what to do with them

**Status: NOTHING RULED. Every proposal below is put to Ben and awaits his
answer.** Written in the form #1760 established — the case as it was put, so
each answer's basis stays legible later. No published tag was changed to
produce it, nothing was staged, and neither path was modified.

Context: the #1704 rollout was paused on 2026-09-03 with the question *there
are two tagging paths in this repo and it is not established which is better,
or even whether they differ in how they extract.* This is the answer.

---

## The finding, in one line

**They are not two taggers.** Path B is Path A plus a measurement harness and a
publication gate. The extraction is the same code, the same vocabulary, and — on
every table where both commit — very nearly the same answer.

## Q1 — do they differ in extraction?

No, and four independent artifacts say so. This is stronger than
`tags/scoring/README.md`'s line 3, which merely *asserts* that B scores the
skill; that line is still unverified and is deliberately left alone.

1. **The commit that created the first predictions** (`b67064e`, #1721) says the
   subagents "ran the skill's real Steps 2-4 blind."
2. **Cache overlap.** `fetch_source.py` is a Path A script that caches what it
   fetches. Tables in each predictions set that carry a cache entry: w5 pilot
   **60/60**, A/B/C runs 74/78, w2 re-measure 27/30, first run 44/60 — the last
   consistent with that run's reported 37% unreachable, since blocker pages are
   refused rather than cached.
3. **Enum conformance.** Across **402 prediction rows**, every value in all six
   controlled columns is inside `vocab.md`'s enums. Zero violations.
4. **The feedback runs backwards, which is the clincher.** Path A's own files
   cite Path B's runs as measurements *of themselves* and were amended in
   response: `fetch_source.py`'s repository-API fix ("this cost w2 70% of its
   reachability in the 2.3 blind run"), `vocab.md`'s frame amendment ("one blind
   rater measured it applying to 9 of 10 tables"), `SKILL.md` twice, and
   `decisions/1760`. B's findings rewrote A's rules and A's code.

**What cannot be established:** the literal dispatch prompt for any historical
run. No prompt text exists anywhere in git — not as a file, not in a commit. So
the agents demonstrably ran the skill's *scripts* and obeyed its *vocabulary*;
whether they were handed `SKILL.md` verbatim or a paraphrase is unknown and
unknowable from the artifacts.

**The schema difference is not a divergence.** Predictions add `status`/`reason`
and omit `context_text` and `item_text_available`. `03_tags.R`'s
`KEEP_COLS <- c(1, 6:12, 3)` drops both of those at export — so the predictions
schema omits exactly the two fields that never publish.

## Q2 — head-to-head on the same 40 tables

`seed=20260903`. Twenty untagged (5 each w2–w5) and twenty human-tagged (5 each
w1–w4), **shuffled together and handed to both arms unlabelled**. Arm A is the
skill as documented, two agents of twenty; Arm B the harness, four blind agents
of ten. Sonnet. Full output in `tags/scoring/results_comparison_2026-09-03.txt`.

**Where both arms commit a value, they agree:**

| column | tables both answered | identical |
|---|---|---|
| `primary language(s)` | 35 | **100.0%** |
| `measurement tool` | 35 | 97.1% |
| `sample` (setting) | 21 | 95.2% |
| `item format` | 24 | 91.7% |

**What differs is willingness to commit, consistently and in one direction:**

| column | A fill | B fill | delta |
|---|---|---|---|
| `measurement tool` | 87.5% | 97.5% | **+10.0** |
| `sample` (setting) | 57.5% | 65.0% | +7.5 |
| `primary language(s)` | 90.0% | 92.5% | +2.5 |
| `item format` | 67.5% | 67.5% | 0.0 |
| *`construct type`* (held) | 77.5% | 92.5% | **+15.0** |
| *`construct name`* (held) | 82.5% | 92.5% | +10.0 |
| *`sample` frame* (held) | 70.0% | 70.0% | 0.0 |
| *`age range`* (held) | 37.5% | 37.5% | 0.0 |

Table-level abstentions: A three, B one. That gap is **the dispatch prompt, not
the extraction** — B's says *fill every field you can support, selection happens
later at assembly*; A's is the skill's own *leave it blank rather than guess*.

**The extra fill is not bought with precision.** On the gold twenty, B's
`item format` is 100% accurate where A's is 70%, at near-identical coverage;
`measurement tool` is 93.3% (A) against 89.5% (B) with B answering 19 of 19
against A's 15 of 17. No accuracy difference survives the sample size — per
column n is 17–19 and the gaps run 5–15 points in **both** directions.

`sample` is reported per facet only (`score_sample_facets.py`). Whole-cell match
is not quoted: gold answers the frame facet on 13–15 of 23–25 while the
prediction answers it on 14, so exact match penalises filling a facet the key
leaves blank. `age range` is scored against `tags/age_range_derived.csv`, never
the sheet — but only four tables carry both a derived value and an answer, so
that column settles nothing here.

## Q3 — the difference that matters is the gate, not the tagger

**Yes. A + B's gate is the sensible combination, and this run measures why.**

Path A has no publication gate. Everything it writes goes to `tags_auto.csv`,
which `03_tags.R` publishes wholesale. Measured on the gold twenty, Arm A's
per-atom precision on the columns #1704 holds back:

| column | A per-atom precision | published under Path A alone? |
|---|---|---|
| `construct type` | **50.0%** | yes — and it should not be |
| `sample` frame facet | **57.1%** | yes — and it should not be |

Both are far below the 90% bar, and both would publish. Under B's gate neither
does. The gate has already earned itself once: #1802 withheld 44 of 60
`primary language(s)` rows after four agents disclosed they had inferred the
language from the study's *country*, a move `vocab.md` forbids for age and had
never addressed for language.

**But the gate cannot currently read the skill's output.** `score.py` and
`score_sample_facets.py` both skip any prediction whose `status` is not
`"tagged"`, and `score.py` additionally wants a table→warehouse sidecar. The
skill's payload models neither field, so the scorers read Path A's output as
**zero rows and report nothing rather than failing** — the worst available
failure mode. `tags/scoring/compare_paths.py` is the adapter that bridges it and
is about fifteen lines. That gap is the whole practical distance between the two
paths.

---

## Proposals

**P1 — Name the relationship in `SKILL.md`, and make the harness the only route
to publication.** The skill is the extraction spec; the harness is how its
output is measured and gated. Neither is deprecated and neither is deleted.
Concretely: `SKILL.md` Step 6 currently ends at "open a pull request with the new
rows" with no mention of a precision bar. It should say that columns publish per
column against a measured bar, and point at `tags/scoring/`.

**P2 — Record that Path A as documented cannot be measured.** Step 1 tells the
skill to run `check_table_status.py` and consult existing rows. On any table
that already has a tag, that is reading the answer key. Every scoring run has
had to suppress Step 1 to stay honest, and no document says so. This is the trap
that prompted the pause: *a run that follows the skill exactly cannot be scored,
and nothing warns you.*

**P3 — Add the `status`/`reason` fields to `stage_tag_row.py`'s payload**, so a
skill run is scorable without an adapter. Two fields, and they are dropped at
export by `KEEP_COLS` anyway.

**P4 — Fix `fetch_source.py`'s blind spot.** A JS shell that is big enough
passes. Spain's CIS barometer pages return 300KB+ of Liferay/React chrome, the
byte count inflated by embedded UI-string JSON, clearing `MIN_USEFUL_CHARS`
without tripping any `BLOCKER_MARKERS`; three arms found this independently on
the same publisher, and a DOI resolving to a journal *homepage* shell went
uncaught too. This is the third sighting of one rule failing — 21kB reCAPTCHA,
4.2kB OSF shell, now 300KB CMS chrome. **Length does not separate an article
from a wrapper**, and the classifier should stop trying to make it.

**P5 — Give the cache per-run isolation.** `fetch_source.py` has neither
isolation nor locking. Under concurrent arms two agents reported files appearing
they had not fetched, and one watched its own entry vanish between fetching and
reading. Both mitigated by hand; neither should have had to. This also means
per-arm reachability was not identifiable in this run.

**P6 — Three vocabulary gaps, all producing false abstentions:**
- `sample`'s SETTING facet has **no atom for a plain workplace**. Hospitality
  frontline employees fit none of Educational/Clinical/Program-based/
  Internet-based/Non-human, so the setting was left blank — on a **published**
  column.
- `item format` has no ruling for a **binary yes/no checklist** or a **0–3
  ordinal** scale. Both were mapped to `Likert Scale/selected response` as
  closest fit, unsanctioned.
- `SKILL.md`'s Step 3 table covers paywall-vs-blocked only for the DOI case. A
  **no-DOI URL returning 403** (government open-data portals) has no row; three
  agents independently defaulted it to `no working link`, which looks right and
  is written down nowhere.

**P7 — Refer the `celik_2026_*` family upstream.** `celik_2026_bpns` fetches a
Mendeley record (n=653, matching the dictionary exactly) describing BFI and
ASTDL, with "BPNS" appearing zero times — found blind by one agent in each arm.
#1802 reported the identical defect for `celik_2026_tipi`. This is a dictionary
defect, not a tagging one, and it is upstream of both paths: neither can tag
correctly through it, and confident output on a mislabelled table is worse than
an abstention. `sumner_2022_asi` is softer — right paper, wrong description.

**P8 — `tags/scoring/README.md` line 3 stays as written until Ben rules.** The
artifact evidence supports it; direct proof is absent.

---

## What remains unknown

- **Whether the paths differ in accuracy.** n=17–19 per column on the gold
  twenty. Differences of 5–15 points appear in both directions and none is
  separable from noise. Forty tables was enough to show the paths agree and to
  locate the gate as the real difference; **it is not enough to rank them.** If
  ranking matters, that is a bigger comparison — but on this evidence there may
  be nothing to rank.
- **Per-arm reachability**, confounded by the shared cache (P5).
- **`age range` accuracy** — only 4 of 40 tables carry both a derived value and
  an answer.
- **`child age`** — 2 gold tables. **w5 gold** — 1 table.
- **The historical dispatch prompts.** No artifact exists.
- **The 367 "reached and abstained" tables** from #1704's population table are
  not derivable from anything in the tree: there is no abstention log,
  `tags_auto.csv` holds 438 rows of which 5 are sentinels, and the tagger cache
  has 177 entries. The figure could not be reproduced.
