# `dup_id_item` worklist

Work items from `dup_id_item_verdicts_2026-09-02.csv` (evidence and method:
`README.md`). **73 of the 101 flagged tables need a data change**; the other 28
need none.

**Status, 2026-09-03.** Blocks A, B, C, D, E and G are **done, uploaded and
verified against the released versions** -- 47 tables, every `excess_pair` 0 (or
`excess_occ` 0 where the repeat is the design). Two of block F and two of block
J are repaired and staged. Block H is **re-diagnosed and should not be worked
from its table below**. What remains needs a source file somebody has to fetch
by hand: `stress_deboeck2012`, `realpic_souza2021`,
`non_parametric_mixture_modeling_exp1_Cleaned`, and the five tables moved out of
block H. **Block I (`duolingo_*`, 7 tables) will not be fixed** — ruled out of
scope by Ben on 2026-09-05; see its entry. Read its entry before
starting another block: a third of it was misdiagnosed here, always in the same
direction — a duplicate-looking flag that was really a collision, a selector
bug or an NA-indexing accident — so treat a block's stated fix as a hypothesis
to check against the source, not an instruction.

Blocks are sized so that **one block is one script and one sitting**, because
that is how the work actually divides — `PEMAIW_Qiu_2020.R` clears seven tables
in one edit. Take a block, not a table. Ordered by `PRIORITIES.md`: corpus trust
first, then gates.

**The `id` fix is settled.** For the collision blocks (B–E), prefix `id` with the
`study`/`group` label that identifies the sample — approved by Ben, 2026-09-02,
"where appropriate", so use judgment per table. Keep the label as a column too
(`cov_study`/`cov_group`); folding it into `id` and dropping it loses a real
covariate. Format is open (`2_1`, `study2_1`) provided it is consistent within a
table and the separator cannot occur in a source id. This rule is general enough
that it probably belongs in `datastandard.md`, not only here.

**Nothing here is uploaded by whoever does the work.** Regenerate, verify, hand
to Ben — uploading is his step, and only ever as a draft version.

## How to verify a fix

```bash
nice -n 19 python3 -m irw_validate.live_dup <table> -o irw_validate/results/recheck.csv
```

Queries the live table; exports nothing (the export allowance is 200GB/30d
against a 181.8GB corpus, so a fetch-based check is not affordable — see the
module docstring). What to look for depends on the block, and each says so.

---

## 1. Corpus trust

### Block A — `florida_twins_behavior.R` · 7 tables · 370,267 rows · dedupe · **DONE, staged**

`florida_twins_behavior_{cads,cadsyv,ecs,friends,panas,rcads,tas}`

Every `id`+`item` occurs **exactly** twice — never three or four times — with an
identical `resp` and zero conflicts anywhere (density 1.99 in `metadata.csv`,
against 1.24 for the separately-processed `florida_twins_cads`). The uniform 2×
is consistent with the **double-entry** layout standard in twin research, where
each pair contributes two rows so each twin appears once as the target and once
as the co-twin; the script's `bind_rows(df0, df1)` over the `bg_id0`/`bg_id1`
arms reproduces every person twice.

> **Read this if you saw the earlier draft.** This block first said *regenerate,
> do not dedupe*, on the reasoning that twins cannot agree on 100% of items so
> one twin's data must be missing. That was wrong, and the id counts refute it:
> `florida_twins_behavior_cads` holds **1,378** distinct ids against
> `florida_twins_cads`'s **1,272** on the identical 57 items. It has *more*
> people, not half as many. A plain dedupe is correct.

*Done when:* `excess_pair` is 0 **and the id count is unchanged** (1,378 for
`cads`). A drop in the id count would mean the dedupe keyed on the wrong columns.

**Result:** every table halved exactly and no id count moved — 1,378 / 861 /
1,387 / 858 / 1,387 / 1,387 / 861. The source file is double-entered, as
twin-pair files are: each pair occupies two rows, once with each twin as
`bg_id0`, so `bind_rows` over the two arms emits every person twice.
`distinct()` after the bind, in `florida_twins_behavior.R`.

### Block B — `PEMAIW_Qiu_2020.R` · 7 tables · 18,025 rows · id collision · **DONE, staged**

`PEMAIW_Qiu_2020_{BWSS,DASS,FFMQ,MEQ,MLQ,PANAS,SWLS}`

`mutate(id = row_number())` runs on each of two recruitment files, which are
then `rbind`ed with a `group` label — so id 1 in WebRecruit and id 1 in
InternalRecruit are **different people**. Namespace `id` (e.g. `paste(group, id)`).
`group` describes the sample, so it also wants to be `cov_group` per
`datastandard.md`.

**Do not dedupe** — every excess row is a real response from a real person.

*Done when:* `excess_pair` is 0 and the id count rises to about the sum of the
two samples (154 + ~930).

**Result:** exactly that — 154 InternalRecruit + 920-1,030 WebRecruit per table,
`excess_pair` 0 in all seven. Fixed at the point the id is made
(`paste0("WebRecruit_", row_number())`), which repairs all seven tables in one
edit.

### Block C — two-sample studies · 7 tables · 26,550 rows · id collision · **DONE, staged**

- `OS_TBMWTFS_Schubert_2023_{DMW,IPIP,MAAS,SMW}` — English (215 ids) and German
  (176) share a namespace; 176 collide.
- `AOMT_BR_SF_EDPANAB_Geiger_2021_{AOT,BRS,RF}` — Bulgaria (248) and North
  America (259) give 286 distinct ids where 507 people were measured.

Same fix and same *don't dedupe* as Block B.

**Result:** Schubert 215 → 391 (English 215 + German 176), Geiger 286 → 507
(Bulgaria 248 + North America 259) — both exactly the predicted counts, and
`excess_pair` 0. `AOMT_BR_SF_EDPANAB_Geiger_2021.R` fixed; **no processing
script exists in `data/` for `OS_TBMWTFS_Schubert_2023_*`**, so those four are
a data-only repair.

### Block D — small id collisions · 9 tables · 216 rows · **DONE, staged**

`CV_OASIS_ODSIS_PPE_Novak_2020_{BFI,DSES,RSES}` (1 colliding id),
`evpromisi_stone_2021_{cdiag,global}` (2), `pass20_klosowska_2025_{csq,dass,staix}_online`
(3), `deception_game` (1).

A handful of ids each. `pass20` is the clearest case in the whole sweep: three
ids carry two different ages, two different sexes **and** two different incomes.
Namespacing or dropping the affected respondents both work; say which was done.
Also rename `deception_game`'s `age` to `cov_age`.

**Result: namespaced, nothing dropped.** `CV_OASIS_*` and `evpromisi_*` carry a
`group`, so they took the same prefix as blocks B and C. `pass20_*` and
`deception_game` carry no sample label, so the id gained a suffix from a dense
rank over the person-level columns — **applied only to the ids that actually
hold more than one person**, so every other id is untouched, and ranked on the
demographic tuple rather than row order so the same person gets the same suffix
in all three `pass20` tables. 415 → 418 in each, 635 → 636 for
`deception_game`, whose `age` is now `cov_age`. No script exists in `data/` for
`evpromisi_stone_2021_*`.

### Block E — single-script id collisions · 4 tables · 34,840 rows · **DONE, staged**

`sris_silvia2022` (15 studies), `fcupanas_cffsdas_reyna_2018` (4 samples),
`selfcompassionscale_shortform_fuochi_2025` (`cov_sample`; 300 rows survive the
namespacing and still need the source), `EWAS_Sanford_2024` (`seq(1, nrow(df))`
per study — all 236 of study 1's ids collide with study 2's).

**Result, and `sris_silvia2022` is no longer soft.** It was flagged here as
resting "on a group-structure probe alone", never examined individually. It
holds **221 ids for 1,192 people** across its 15 studies — the largest ratio in
the whole sweep. `fcupanas` 805 → 1,636, `EWAS_Sanford_2024` 482 → 718 with all
236 of study 1 colliding exactly as predicted.

`selfcompassionscale_shortform_fuochi_2025` went 1,816 → 2,043 and **300 excess
rows survive**, exactly as this entry predicted: within a single sample the
source file still repeats an id, and those responses conflict, so it is not a
dedupe. It is staged but **`red_up` refuses it** — for the residual and for a
41-character name — which is the gate behaving correctly on a table that is
still half broken. It needs the source.

### Block F — the script dropped a column the source has · 3 tables · 60,030 rows · **2 of 3 DONE, staged**

- `IRTrees.R:17` — `fsdatT %>% select(-node, -sub)` on De Boeck & Partchev
  IRTrees data, whose design is one row per tree node. `ravens_deboeck2012` is
  exactly 2× its pair count; `stress_deboeck2012` is the same script.
  *Confirmed:* `ravens_deboeck2012` is **every pair exactly 2x** and nothing
  else — 5,811 pairs, no singletons — and `stress_deboeck2012` runs 3 to 9.
  `KTEEM_Schoen_2019-2022` is 1 to 5, which is the wave count its `group`
  column is recording.
- `KTEEM_Schoen_2019-2022.R` — renames `DataCollectionWave` to `group`. It *is*
  a wave: Spring19–Spring22, `PublicID` persists, 832 of 1,130 ids recur.
  **No data change** — rename `group` → `wave`, set `longitudinal=TRUE`.
  **Done:** verified that `id`+`item`+`group` is already unique, so the rename
  alone takes 49,357 unexplained repeats to zero.

**Done for `ravens_deboeck2012` too, and the column was sitting in the source.**
`fsdatT` ships `sub` = `item:node`, the pseudo-item an IRTrees model treats as
an item, and line 17 deleted it alongside `node`. `item` is now `i01:node1`;
35 items become 105 and the row count does not move.

**`stress_deboeck2012` is not the same problem.** It already has an `occasion`
column, and 792 excess rows survive it: in the source, 36 of its 185 people
hold two or more complete sets of responses (id 48 appears twice over, differing
on some values). That needs the study, not a column.

*Done when:* `excess_occ` is 0. `excess_pair` will stay non-zero, correctly —
the repeat is the design once the column is back.

### Block G — ~~plain dedupe~~ · 12 tables · 3,790 rows · **DONE, uploaded 2026-09-03**

`RD_EppSCQRK_Kipkemoi_2024_scq` (1,000), `PROMISPME_Forrest_2021_{Family_Children,
Family_Proxy,Physical_Children,LS_Children,MP_Children,Strength_Children}` (441),
`FEDSP_Trzcinska_2023_{SMSD,MonKnow}`, `smacof_pvq40`, `concretewords`,
`Fh_Okcsr_Roos_2022_study1_Feeling_Heard` (2,328).

**A third of this block was not a plain dedupe, and on one table the prescribed
fix would have destroyed data.** It was described here as "the smallest, safest
block — a good first one for someone new"; the safe-looking part was the flag
count, not the diagnosis. What each turned out to be:

| table | what it actually was |
|---|---|
| `FEDSP_Trzcinska_2023_{SMSD,MonKnow}` | **an id collision.** `number` is labelled "Child's & parent's number" — a dyad — and one dyad has two caregiver rows with different `p_sex` and `p_age`. The parent scales are two respondents (namespace the caregiver); the child measures are one child recorded twice (dedupe). **Deduping SMSD, as this block said to, deletes a real caregiver.** |
| `Fh_Okcsr_Roos_2022_study1_Feeling_Heard` | **a selector bug, not dual subscale membership.** `ends_with("11")`/`("12")` is a suffix test and swept the twelve Respect matrix items `Q{3,4,5}.{14,15,16}_{11,12}` into the Feeling Heard group — that is all 2,328 duplicated rows — along with `Q4.11`/`Q5.11`, "is your relationship equal?", which is not an item of the scale. Naming the four real items fixes it and **no `itemcov_subscale` is needed**: `group` is now a function of `item`. |
| `smacof_pvq40` | **an R indexing trap.** `df[df$resp>0,]` — `NA > 0` is `NA`, and subsetting by an NA index *inserts* an all-NA row rather than dropping it. Six `id=NA, item=NA` rows reached the corpus. |
| `RD_EppSCQRK_Kipkemoi_2024_scq` | 25 rows byte-identical across all 66 source columns. The DOI recorded in the script was also wrong: `F4UYZQ` holds only `C_DOS`; the data is `NJHSAC`. |
| `concretewords`, `PROMISPME_Forrest_2021_*` | plain dedupe, as described. |

Two neighbours came along because the same script produces them:
**`FEDSP_Trzcinska_2023_PRD`** is a block H table whose residual was to be taken
"to the source" — the source answers it, nothing to chase — and
**`FEDSP_Trzcinska_2023_PSPCSA`**, never flagged, carried the same dyad.

`concretewords` and the six `PROMISPME_*` were repaired from the *published*
table (`irw_validate.repair_dedupe`) rather than regenerated, because their raw
source is gone: PROMISPME's OSF node `f7rp3` now holds one 714 KB `.sav` that
cannot be the origin of a 208k-row table. **Their processing scripts are still
wrong** — re-running either reintroduces the duplicates.

*Left open, both surfaced by the Roos fix and neither part of this block:* its
four Feeling Heard items are on a **1–7** scale where every other item in the
table is **1–5**, so they are arguably a separate instrument and a separate
table; and its `group` column should become `itemcov_subscale`, which is only
safe now that group is a function of item.

### Block H — ~~dedupe, then take the residual to the source~~ · 13 tables · **RE-DIAGNOSED, do not follow the table below**

> **Three of these are not duplication at all, and this block's instruction
> would have destroyed data.** Read
> `results/copies_per_pair_2026-09-03.csv` before touching any of them.
>
> The verdict `mixed_dedupe_then_source` was reached from `excess_exact > 0`:
> some rows are byte-identical, so those rows are duplicates. That inference is
> wrong in a repeated-measures design, where a person answering the same item
> the same way on two occasions is byte-identical and entirely real. The
> distribution of *copies per `id`+`item`* tells them apart, and it is an
> aggregate, so it was always affordable to look:
>
> | table | copies per pair | what it is |
> |---|---|---|
> | `number_pattern_game` | **every pair exactly 30x** (9,088 of them) | 30 trials per person-item. The prescribed dedupe removes 255,155 real trials — 94% of the table. |
> | `SAS_Deters_2022` | 1 … 14, tapering | repeated measurement, not duplication |
> | `PTCI_Chinese_Zhan_2024` | 1, 2, 3, 4 | up to four occasions |
> | `Veterans_Affairs_SSVF_Survey_2016-17` | 158,637 once, 91,043 twice | strictly two — reads as two waves, not 91,043 accidents |
> | `Aspirations_Sonmez_2022` | 1,995 once, **7,280 twice** | ditto, and most pairs are doubled |
>
> Those five belong with blocks F/I/J — an occasion column that was dropped or
> never carried — not here. The rest do have the small tail at 2 that
> duplication looks like: `PROMISPME_*_Proxy` (53,928 pairs once, 56 twice),
> `PEPABAS2C_Kubicka_2024` (4,750 and 48), `5personalityfactors` (624,260 and
> 1,260), `pact_project`.
>
> **And the mechanical half cannot ship anyway.** `red_up` refuses a table that
> still has unexplained `id`+`item` repeats, so "do the first and record the
> second" produces a file no uploader will take. Block H is all-or-nothing: it
> needs the source before any of it reaches the corpus.

Two halves; the first is mechanical, the second is research. Do the first and
record the second, rather than blocking on it.

| table | dedupe | then chase |
|---|---|---|
| `pact_project` | 171,719 | see below |
| `number_pattern_game` | 255,155 | 8,456 |
| `SAS_Deters_2022` | 87,571 | 18,259 |
| `Veterans_Affairs_SSVF_Survey_2016-17` | 51,490 | 39,553 |
| `PTCI_Chinese_Zhan_2024` | 17,394 | 21,183 |
| `Aspirations_Sonmez_2022` | 2,320 | 4,960 |
| `5personalityfactors` | 264 | 996 |
| `PROMISPME_Forrest_2021_*_Proxy` (4) | 101 | 114 |
| `PEPABAS2C_Kubicka_2024` | 27 | 21 |
| ~~`FEDSP_Trzcinska_2023_PRD`~~ | — | **done** — resolved with block G; the caregiver collision explains all five, nothing to chase |

`5personalityfactors` also wants `age` → `cov_age`; 70 of its excess rows are
id collisions (one id, two ages), not duplicates.

`pact_project` has no conflicting responses to chase — all 138,035 repeated
pairs agree — but it has a second defect: `treat` is NULL on 581,824 of
1,018,383 rows, and 88,999 of the excess rows differ from their twin *only* in
whether `treat` is populated. Dedupe and populate `treat` consistently. Then
check the source: `pact_project.R:361` rbinds five frames under a
`# COMBINE WAVES` comment, and if those really are distinct waves the column
should be carried through as well — but see Decision note below, it is not what
causes this flag.

### Block I — `duolingo_*` · 7 tables · 279,003 rows · **WILL NOT FIX, ruled 2026-09-05**

> **Ben ruled these out of scope on 2026-09-05:** the source files are more
> trouble than the tables are worth. Do not fetch the SLAM dataset and do not
> re-run `duolingo2018.R`. The diagnosis below stands and the script is already
> fixed, so if the data ever arrives for another reason the work is one command
> — but nobody should go looking for it.
>
> These seven stay in the corpus carrying the defect. It is class 1c, the mild
> one: the repeats are **real** and the data is not false, it is unusable as a
> longitudinal trace. Nothing about them should ever be deduped.

*Diagnosis as of 2026-09-03, retained for the record:*


**The index was never missing from the source -- the script reads it, names it,
documents its layout in a comment, and then drops it.** `resp.id` is "a unique
12-digit ID for each token instance: the first 8 digits are a B64-encoded ID
representing the session, the next 2 digits denote the index of this exercise
within the session, and the last 2 digits denote the index of the token (word)
in this exercise". That middle pair is exactly the exposure index, and it is
why `session` alone separated only 9.4% of the duplicated groups: a learner
meets the same lexeme several times *inside* one session, in different
exercises. `duolingo2018.R` now derives `trialnum` and `order` from digits 9-10
and 11-12.

Re-running it needs the SLAM dataset, which sits behind a Dataverse guestbook a
person has to complete (doi:10.7910/DVN/8SWHNO, 98 MB in three files).

*Confirmed by the copy histogram:* 89-96% of pairs occur once with a tail
running to 11-22, which is the shape of a spaced-repetition trace and not of
duplication. Block I's diagnosis stands.

`duolingo_{en_es,es_en,fr_en}__{listen,reverse_tap,reverse_translate}` (7 of the 9).

A spaced-repetition trace, so a learner meeting the same lexeme repeatedly **is**
the design. The problem is that nothing identifies which exposure a row belongs
to. Measured on `duolingo_fr_en__listen`, over its 7,641 duplicated `id`+`item`
groups, here is what actually separates them:

| column | separates | |
|---|---|---|
| `rt` | 84.1% | a measurement, not an identifier |
| `dependency_head` | 28.0% | item-level column that **varies within item** |
| `dependency_label` | 14.4% | ditto |
| `session` | 9.4% | the only real occasion column, and it barely helps |
| `morphology` | 8.0% | ditto |
| `part_speech` | 2.5% | ditto |
| `format`, `stem` | 0% | constant within item, as they should be |

Two things follow. **`rt` is carrying the load**, which is the defect — a
response time is a measurement, and rounding it would silently merge rows.
**And it is not even sufficient:** 861 of the 8,820 excess rows survive grouping
by all ten columns, so ~10% of the table is genuinely unidentifiable as it
stands.

The dependency and morphology columns varying *within* an item is the clue to
the fix, and a second finding in its own right. They are properties of the
token's syntactic role, so their variation means the same lexeme is being met in
**different exercises** — which is exactly the exposure index the table is
missing, present implicitly and never materialised. Per `datastandard.md` an
`itemcov_*` should be a function of the item; these are not, so `item` is
under-identifying.

Restore a per-exposure index from the source, and dedupe the byte-identical
residue (767 rows here) separately.

*Done when:* `excess_pair` is 0. Unlike Blocks A/F this one really should reach
zero — with an exposure index every row is uniquely keyed.

### Block J — trial-level, no trial index · 4 tables · 84,777 rows · **2 of 4 DONE, staged**

*Confirmed by the copy histogram, and emphatically:* `motion` is **every pair
exactly 10x**, `non_parametric_mixture_modeling_exp1_Cleaned` runs to **994**
copies, `rr98_accuracy` to 62. `realpic_souza2021` is the odd one out at
4,116 pairs once and 28 twice — the small tail that really is a defect.
`number_pattern_game` belongs in this block, not in H.

`non_parametric_mixture_modeling_exp1_Cleaned`, `motion`, `rr98_accuracy` —
same `rt`-as-identifier problem; restore `trialnum`/`order`.

**Done:** `motion` (the source's `trial`; every id+item pair appears exactly
10x and it says which of the ten) and `rr98_accuracy` (`block` **and** `trial`
-- `trial` restarts inside each block, so neither identifies a row alone).
Both from public sources: the paper's GitHub CSV and the `rtdists` CRAN package.

`rr98_accuracy` also forced a fix to the gate: `irw_validate` tried each
occasion column singly and no single one resolves a trials-within-blocks
design. It now falls back to testing every occasion column present together.

Plus `realpic_souza2021`: 28 excess rows, all conflicting, nothing explains
them. Needs the source. Small enough to fold in here. *Note while you are
there:* its `id` is a picture file name and its `resp` is a **mean** rating, so
the 28 are the smaller of its problems.

**`non_parametric_mixture_modeling_exp1_Cleaned` -- do not restore its trial
index first.** `Non_parametric_mixture_modeling_exp1.R` rebuilds `id` as
`rep(names(table(id)), times = table(id))` and assigns it onto rows that have
just been sorted by `item`, so the id a row carries has no connection to the
subject it came from. Settle that before anything else about the table means
much. The script records no source URL.

---

## 2. Gates

Category 2 in `PRIORITIES.md` — stop the class, not the instance. **The first
item is the highest-leverage thing on this page**: it would have caught all 27
id collisions above at upload time, before any of them reached the corpus.

- [ ] **An id-uniqueness check.** One `id` holding conflicting values of a
      person-level column (`cov_age`, `cov_sex`, `group`, `study`, `treat`) is
      not a repeated measure — it is two people sharing an identifier.
      `pass20_klosowska_2025_*` is the ready-made test fixture.
- [ ] **Report the distribution of copies per `id`+`item`, not just the total.**
      `excess_pair` cannot distinguish `number_pattern_game`, where every pair
      appears exactly 30 times because there are 30 trials, from
      `5personalityfactors`, where 1,260 of 625,520 pairs appear twice because
      something went wrong. Deduping the first destroys 94% of the table.
      A single spike at n>1 is a design; a long tail from 1 is repeated
      measurement; a dominant 1 with a small tail at 2 is duplication or a
      collision. `irw_validate/live_copies.py` computes it, as an aggregate, so
      it costs nothing — and it caught three wrong verdicts in block H.
- [ ] **Split `dup_id_item` into its classes.** It reports one error for six
      different defects. The three measures that made this triage possible —
      the exact-duplicate share, what survives grouping by every column, and
      whether only a person-level column separates the rows — belong in the
      check itself. `irw_validate/live_dup.py` computes all three.
- [ ] **Zero disagreement across many repeated pairs means duplication.** If a
      table has thousands of repeated `id`+`item` pairs and *none* of them
      differ on `resp`, it is duplicated, not re-measured — people vary when
      you measure them twice. This single number corrected two verdicts here
      (`Fh_Okcsr_Roos_2022_study1_Feeling_Heard`, `pact_project`), in both
      cases against a plausible-sounding design story. `live_dup.py` already
      reports it as `n_conflict_pairs`; the check should act on it.
- [ ] **`rt` must never be what makes rows unique.** That single rule turns
      Blocks I and J from judgment calls into a check.
- [ ] **Point the sweep at live data.** `data/pub` is a stale archive — 44 of
      the 101 were unanalysable from it. `live_dup.py` shows the shape: query,
      never fetch, so it costs no export quota.

---

## 3. Housekeeping · no data change

- [ ] **28 tables are `document_column`** — an occasion column already explains
      the repeat and the #1835 gate list already consults it. Nothing to do.
      Two nuances worth folding into whichever block touches them:
      `PSR-P_Scale_Intimacy_Hakim_2018_Study2_{PSI,PSR}` should expose `figure`
      as `itemcov_figure` (`item` alone under-identifies the measurement), and
      `deception_game`'s `age` should be `cov_age`.
- [ ] **`AAQ-II` is retired** — nothing in the corpus matches its 10,521 rows /
      1,497 ids / 7 items. Drop it from the sweep's input rather than
      re-flagging it every run.
- [ ] **`florida_twins_cads` and `florida_twins_behavior_cads` are the same
      instrument** — 57 items each, from two different scripts — yet they share
      only 449 ids (of 1,272 and 1,378). Either they are different cohorts that
      should be one table with a `cov_study` column, or the two scripts derive
      `id` differently and the 449 "shared" people are an id collision across
      tables. Worth resolving while Block A is open; it is not part of Block A.
- [ ] **Four sweep names are stale renames.** A rename map would stop future
      sweeps reporting them as missing:
      `Veterans.Affairs.SSVF.Survey.2016-17` → `Veterans_Affairs_SSVF_Survey_2016-17`,
      `Aspirations_Sonmez_2023` → `Aspirations_Sonmez_2022`,
      `Mechanical_Turk_Lexical` → `mturkddm_lexical`,
      `Mechanical_Turk_Recognition` → `mturkddm_recognition`.
