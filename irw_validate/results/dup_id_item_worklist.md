# `dup_id_item` worklist

Work items from `dup_id_item_verdicts_2026-09-02.csv` (evidence and method:
`README.md`). **73 of the 101 flagged tables need a data change**; the other 28
need none.

Blocks are sized so that **one block is one script and one sitting**, because
that is how the work actually divides — `PEMAIW_Qiu_2020.R` clears seven tables
in one edit. Take a block, not a table. Ordered by `PRIORITIES.md`: corpus trust
first, then gates.

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

### Block A — `florida_twins_behavior.R` · 7 tables · 370,267 rows · **regenerate, do not dedupe**

`florida_twins_behavior_{cads,cadsyv,ecs,friends,panas,rcads,tas}`

The script builds `df0` from `bg_id0`/`ends_with("0")` and `df1` from
`bg_id1`/`ends_with("1")`, `bind_rows` them, then strips the trailing twin
suffix from `item`. Every `id`+`item` then occurs exactly twice with an
**identical** `resp`, zero conflicts — density 1.99 in `metadata.csv` against
1.24 for the separately-processed `florida_twins_cads`.

Twins cannot agree on 100% of items, so this is one twin's data emitted twice
and **the other twin's data probably missing entirely**. Deduping would produce
a clean-looking table with half the intended sample. Rebuild from
`multiparentandchild0311 LDBase.csv` and confirm the id count doubles.

*Done when:* `excess_pair` is 0 **and** the table has roughly twice the ids it
has now. The first alone is not enough — deduping achieves it and is wrong.

### Block B — `PEMAIW_Qiu_2020.R` · 7 tables · 18,025 rows · id collision

`PEMAIW_Qiu_2020_{BWSS,DASS,FFMQ,MEQ,MLQ,PANAS,SWLS}`

`mutate(id = row_number())` runs on each of two recruitment files, which are
then `rbind`ed with a `group` label — so id 1 in WebRecruit and id 1 in
InternalRecruit are **different people**. Namespace `id` (e.g. `paste(group, id)`).
`group` describes the sample, so it also wants to be `cov_group` per
`datastandard.md`.

**Do not dedupe** — every excess row is a real response from a real person.

*Done when:* `excess_pair` is 0 and the id count rises to about the sum of the
two samples (154 + ~930).

### Block C — two-sample studies · 7 tables · 26,550 rows · id collision

- `OS_TBMWTFS_Schubert_2023_{DMW,IPIP,MAAS,SMW}` — English (215 ids) and German
  (176) share a namespace; 176 collide.
- `AOMT_BR_SF_EDPANAB_Geiger_2021_{AOT,BRS,RF}` — Bulgaria (248) and North
  America (259) give 286 distinct ids where 507 people were measured.

Same fix and same *don't dedupe* as Block B.

### Block D — small id collisions · 9 tables · 216 rows

`CV_OASIS_ODSIS_PPE_Novak_2020_{BFI,DSES,RSES}` (1 colliding id),
`evpromisi_stone_2021_{cdiag,global}` (2), `pass20_klosowska_2025_{csq,dass,staix}_online`
(3), `deception_game` (1).

A handful of ids each. `pass20` is the clearest case in the whole sweep: three
ids carry two different ages, two different sexes **and** two different incomes.
Namespacing or dropping the affected respondents both work; say which was done.
Also rename `deception_game`'s `age` to `cov_age`.

### Block E — single-script id collisions · 4 tables · 34,840 rows

`sris_silvia2022` (15 studies), `fcupanas_cffsdas_reyna_2018` (4 samples),
`selfcompassionscale_shortform_fuochi_2025` (`cov_sample`; 300 rows survive the
namespacing and still need the source), `EWAS_Sanford_2024` (`seq(1, nrow(df))`
per study — all 236 of study 1's ids collide with study 2's).

### Block F — the script dropped a column the source has · 3 tables · 60,030 rows

- `IRTrees.R:17` — `fsdatT %>% select(-node, -sub)` on De Boeck & Partchev
  IRTrees data, whose design is one row per tree node. `ravens_deboeck2012` is
  exactly 2× its pair count; `stress_deboeck2012` is the same script.
- `KTEEM_Schoen_2019-2022.R` — renames `DataCollectionWave` to `group`. It *is*
  a wave: Spring19–Spring22, `PublicID` persists, 832 of 1,130 ids recur.
  **No data change** — rename `group` → `wave`, set `longitudinal=TRUE`.

*Done when:* `excess_occ` is 0. `excess_pair` will stay non-zero, correctly —
the repeat is the design once the column is back.

### Block G — plain dedupe · 12 tables · 3,790 rows

`RD_EppSCQRK_Kipkemoi_2024_scq` (1,000), `PROMISPME_Forrest_2021_{Family_Children,
Family_Proxy,Physical_Children,LS_Children,MP_Children,Strength_Children}` (441),
`FEDSP_Trzcinska_2023_{SMSD,MonKnow}`, `smacof_pvq40`, `concretewords`.

Every excess row is byte-identical to one already present and no pair holds
conflicting responses. Drop duplicates. The smallest, safest block — a good
first one for someone new.

Plus `Fh_Okcsr_Roos_2022_study1_Feeling_Heard` (2,328), which needs one extra
step. Its `group` column is a **subscale** label, not a condition: 12 items
belong to both the *Feeling Heard* and *Respect* subscales, so each of their
responses was emitted twice under the two labels, and the two copies never
disagree. Dedupe on `id`+`item`+`resp`, and record the dual subscale membership
as item metadata (`itemcov_subscale`) rather than as duplicated rows.

*Done when:* `excess_pair` is 0.

### Block H — dedupe, then take the residual to the source · 13 tables

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
| `FEDSP_Trzcinska_2023_PRD` | 2 | 3 |

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

### Block I — `duolingo_*` · 7 tables · 279,003 rows · restore a trial index

`duolingo_{en_es,es_en,fr_en}__{listen,reverse_tap,reverse_translate}` (7 of the 9).

A spaced-repetition trace, so meeting the same lexeme repeatedly **is** the
design — but `session` leaves most of the excess unseparated (repeats happen
within one session) and what actually makes rows unique is `rt`. A response time
is a measurement, not an occasion label. Restore a per-exposure index from the
source.

### Block J — trial-level, no trial index · 4 tables · 84,777 rows

`non_parametric_mixture_modeling_exp1_Cleaned`, `motion`, `rr98_accuracy` —
same `rt`-as-identifier problem; restore `trialnum`/`order`.

Plus `realpic_souza2021`: 28 excess rows, all conflicting, nothing explains
them. Needs the source. Small enough to fold in here.

---

## 2. Gates

Category 2 in `PRIORITIES.md` — stop the class, not the instance. **The first
item is the highest-leverage thing on this page**: it would have caught all 27
id collisions above at upload time, before any of them reached the corpus.

- [ ] **An id-uniqueness check.** One `id` holding conflicting values of a
      person-level column (`cov_age`, `cov_sex`, `group`, `study`, `treat`) is
      not a repeated measure — it is two people sharing an identifier.
      `pass20_klosowska_2025_*` is the ready-made test fixture.
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
- [ ] **Four sweep names are stale renames.** A rename map would stop future
      sweeps reporting them as missing:
      `Veterans.Affairs.SSVF.Survey.2016-17` → `Veterans_Affairs_SSVF_Survey_2016-17`,
      `Aspirations_Sonmez_2023` → `Aspirations_Sonmez_2022`,
      `Mechanical_Turk_Lexical` → `mturkddm_lexical`,
      `Mechanical_Turk_Recognition` → `mturkddm_recognition`.
