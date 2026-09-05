# IRW Item Text Schema

Verbatim field definitions, copied from https://itemresponsewarehouse.org/itemtext.html
(2026-09-01, updated for the administered-language columns agreed in irw#1777) so this
skill doesn't need to re-fetch the page every run. This is the
schema of the **merged** `{table}__items.csv` — the output of joining the four
per-table tabs (instrument, sections, items, responses) on `table` / `section_id` / `item`.

| Field | Definition |
|---|---|
| `table` | Identifier used to link to the IRW response data. |
| `section_id` | Identifier for a group of items that share a common context; functions like `item_family`, annotating testlets and grouped items. |
| `item` | Persistent identifier for the probe being used to measure — matches the core IRW dataset's `item` field exactly. |
| `instrument` | Full, human-readable name or title for the instrument identified by `table`. |
| `language` | Language the instrument was administered in, named plainly (`German`, `Spanish`) rather than as a code. Present when that language is not English. |
| `instructions` | Literal text of the instructions provided to the participant for the overall instrument. |
| `section_prompt` | Literal text of a shared prompt (e.g. a reading passage) that applies to all items within a given `section_id`. |
| `item_text` | Literal text of the specific prompt or question associated with an `item`. |
| `correct_response` | Scoring key for a given `item`. Blank when there is no correct answer; multiple correct answers are semicolon-separated (e.g. `A;C`). |
| `option_text` | Literal text for a specific response option available for an item. May legitimately be missing for behavior-scored items. |
| `wording_rights` | `NC` when the instrument's rights holder states a non-commercial restriction on the wording, even though IRW copied it from an openly licensed source. Omitted entirely when there is no such restriction. **Known gap (irw#1955): the value space is `NC` only, so it cannot express an enforced fee or a no-redistribution clause — the two 2026-09-04 triggers — and as of 2026-09-04 it is set on zero live tables. Do not rely on it to find rights-affected tables; record the quoted term in `provenance.csv` and `public_note` as well.** |
| `resp` | Response value assigned to a specific `option_text` — must match the numeric/ordinal values already present in the live response-level IRW dataset (`irw::irw_fetch(table)$resp`). |
| `instructions_translated`, `section_prompt_translated`, `item_text_translated`, `option_text_translated` | English translation of the correspondingly named field. Present only for instruments administered in a language other than English. |

`instructions` and `section_prompt` are scoped differently: `instructions` applies to
the entire table regardless of `section_id`; `section_prompt` applies only to the items
sharing one or more specific `section_id` values. The same span of source text should
never be recorded in both fields. If framing or task-level text applies across the whole
table, record it once in `instructions`. If it is specific to a subset of items sharing
a `section_id` (e.g. a passage or context given before a testlet), record it in
`section_prompt` only, even if it superficially resembles instructional language.

**Administered language.** For a study administered in a language other than English,
the four text fields hold the wording respondents actually read, verbatim, `language`
names that language, and the English goes in the parallel `_translated` fields. `item`
and `resp` are join keys and are never translated. For an English administration,
`language` and the `_translated` columns are left out entirely rather than emitted
empty.

**The fallback, and what `language` holds in it.** When the administered original
cannot be recovered and only an English version exists, the English goes in the base
fields, the `_translated` fields stay empty, and `text_source=translated_substitute`
records the fallback.

`language` is populated **whenever the administration was non-English, regardless of
what the base fields contain** — it is defined as a fact about the study, not a claim
about `item_text`. So in the fallback a table reads `language=Chinese` while
`item_text` is English, and that combination is deliberate:

> **Populated `language` + empty `_translated` is the signal that the base fields are
> NOT the administered wording.** It is also the query that finds tables needing a
> later backfill (`language != '' AND item_text_translated == ''`). Leaving `language`
> empty here would make a fallback table indistinguishable from an English
> administration and destroy that query.

**Recoverability is scoped, so the test is decidable at extraction time.** Look in the
data deposit and the paper's own supplements. If the administered wording is there,
ship it; if it is not, take the fallback and say in provenance which files you checked
and that they contained no text in that script. Do not go hunting off-source for a
published original — that is a later pass, not a blocker.

Whether the shipped English is the authors' own rendering or a canonical instrument
does **not** change any of this. `text_source` distinguishes those (`study_materials`
vs `canonical_instrument` vs `translated_substitute`); the base/`_translated`/`language`
layout is the same either way.

See SKILL.md's core model section 4 for the full rule.

**`resp_raw`** (per the public schema page): when the scoring key can't be recovered —
i.e. the item is on some categorical/lettered coding in the source material that doesn't
map cleanly onto the numeric `resp` already in the live data — the raw categorical option
goes here instead of being forced into `resp`. **Caveat observed in the actual Sheets**:
the real per-table `responses` tab spells this column `raw_resp`, not `resp_raw` (seen in
`gilbert_meta_11`). Treat both spellings as the same field; `scripts/validate_items.R`
checks for either.

## Per-tab schema (the 4 source tabs, before merging)

Confirmed against two populated examples (`coach_chen_2022_phq9`, `gilbert_meta_11`) —
inspect a live example yourself before assuming this is exhaustive, sheets can vary.

- **instrument** (gid=0): `table, instrument, instructions`
- **sections** (gid=971697782): `table, section_id, section_prompt` — one row per section;
  use a single trivial `section_id` (e.g. `<table>_1`) with blank `section_prompt` when the
  instrument has no real testlet/passage grouping, rather than omitting the tab.
- **items** (gid=653192405): `table, section_id, item, item_text, correct_response`
- **responses** (gid=1308795295): `table, section_id, item, option_text, resp` (or
  `raw_resp` in place of `resp` — see above)

For a non-English administration each tab additionally carries the translated twin of
its own text field — `instructions_translated` on instrument (alongside `language`),
`section_prompt_translated` on sections, `item_text_translated` on items,
`option_text_translated` on responses — so the merge carries them through unchanged.

Merge logic (what `join.R` and `validate_items.R` do): start from `items`, then
successively `merge(..., all.x=TRUE)` with `sections`, `instrument`, `responses` on their
shared key columns (`table`, `section_id`, `item` as applicable).

## Non-negotiable validation gate

Before anything is written as final output, the merged data must satisfy — exactly, not
approximately:

- `unique(items_csv$item)` == `unique(irw::irw_fetch(table)$item)`
- `unique(items_csv$resp)` == `unique(irw::irw_fetch(table)$resp)` (only when a real
  `resp` column, not `raw_resp`, is populated — see `validate_items.R`)

`item` must always be drawn from the existing response data's item values — never
invented. Same for `resp`. If the source paper discloses a different item count than the
live data (this has happened, e.g. `fivpei_perrig_2023_attdiff`: 28 items in the paper vs.
21 in the data), or the item/response text can't be fully recovered, do not force a match.
Emit whatever partial structure is defensible and record the discrepancy — see SKILL.md's
"Can't fully automate" handling.

## Rights: when item wording may not be shipped

Ruled 2026-09-04 by ben-domingue on irw#1891. Check this **before** transcribing, not
after — the TIMSS extractions that produced this rule were finished, gated and verified
before anyone asked whether they could be published.

**The rule.** If the wording's rights holder states a non-commercial restriction on the
item text, do not ship it. Write no `__items.csv`, record the table `blocked`, and quote
the clause in `notes_<table>.csv`. This is a determinate block ("licence bars reuse"), not
a retryable one — an unchanged retry cannot change it.

This mirrors `datastandard.md`, which stops response-data intake on "any NC/ND
restriction". Until this ruling that rule had no item-text counterpart, so wording was
being extracted under terms that would have barred the response data outright.

**It fires on a stated restriction, not on an inference.** The test is whether the rights
holder's own terms — a licence page, a PDF front matter, a per-page watermark, a
questionnaire's distribution notice — say the material is for non-commercial use. Quote
the sentence. If you cannot quote one, the rule does not fire.

It specifically does **not** fire because an instrument is a copyrighted scale, is
reproduced without an explicit grant, or is merely free of charge rather than sold by a
test publisher. Most academic scales are in that position and remain shippable; "silence
is not permission" was considered and rejected as the rule, because it would block most of
the queue. Record what you relied on in `provenance.csv` `note` so a weak basis stays
auditable.

**A public-domain statement does not override an NC clause.** TIMSS 2003's page says both
"Although the items are in the public domain" and "for non-commercial, educational, and
research purposes only". The restriction governs. All three TIMSS cycles are declined on
this rule, 2003 included.

**Whose terms govern: the source you copied from, not the instrument.** Ruled
2026-09-04 on the ECR-R. Its author states the scales are "in the public domain",
that no permission is needed "to use these scales in non-commercial research", and
that "You may not use the scales for commercial purposes without permission" — the
same public-domain-beside-an-NC-clause shape as TIMSS 2003. But IRW's copy of ECR
wording came from a CC BY PLOS deposit's own SPSS variable labels, not from that
page.

The rule is that **the licence of the source IRW actually copied from governs**. An
instrument author's non-commercial statement restricts administering the scale; it
does not retroactively narrow what an openly licensed publication published. So
wording taken from a CC BY paper ships, and wording taken from a CC BY-NC paper does
not — `chinvararak_2021_ecr` stays blocked because the only publication of its
18-item Thai selection is CC BY-NC, and that is a source-level restriction, not an
instrument-level one.

**A stated bar on REDISTRIBUTION is different from a non-commercial clause, and it blocks.**
Ruled 2026-09-04 on the WHOQOL. The rule above turns on whether a *non-commercial* restriction is
stated, and the WHOQOL centres' terms do not lead with one — commercial funding merely attracts a
royalty (NZ$500 for a single study), which is a fee, not a prohibition. What they do state is an
explicit bar on reproduction and redistribution:

> "You agree that you will not reproduce copies of the WHOQOL instruments except for the limited
> purpose of generating sufficient copies for use in investigations stated hereunder and shall in no
> event distribute them to third parties by sale, rental, lease, lending or any other means."
> — AUT / NZ WHOQOL, *Terms and Conditions of Use of the WHOQOL Tools*

Shipping item text IS distributing the instrument to third parties, so that clause bites directly on
what IRW does, in a way an NC clause does not. **IRW does not offer WHOQOL item text.** All six
WHOQOL tables in `queue_state.csv` are `blocked`, and the four that had already shipped were
withdrawn.

**This is a deliberate exception to the source-licence rule above, not an application of it.** IRW's
WHOQOL wording came from openly licensed deposits — CC0 in the COACH case — so under the ECR-R
ruling it would ship. Ben ruled otherwise: a rights holder's explicit no-redistribution term is
honoured even where the copy came from an open source.

**This has since been generalised — the open question was settled on 2026-09-04.** As written, the
WHOQOL ruling was a decision about one instrument, and it deliberately left open whether *any*
quotable no-redistribution clause should override the source licence. Ben answered that on
2026-09-04, ruling on the DSES (`CV_OASIS_ODSIS_PPE_Novak_2020_DSES`, "Permission of author required
to distribute or copy"): **yes, it generalises.** A quotable no-redistribution clause from the rights
holder outranks the deposit's licence, whatever that licence is. You no longer need to ask before
applying this to another instrument.

Note that finding the WHOQOL terms took a text proxy, because `cpcr.aut.ac.nz` returns 403 to a
direct fetch and Manchester's user-information PDF fails on a TLS certificate mismatch. **Absence of
a retrievable clause is not absence of a clause** — that caution still stands, and is why the rule
below is stated as a quote test rather than an inference.

**The second 2026-09-04 ruling: an enforced licence fee also disqualifies.** Ruled on the TAS-20
($40 per study, enforced — there is a 2021 *Molecular Autism* retraction over it). This generalises
too, to any fee-licensed instrument. It withdrew `cucchi_2018_tas20` and `rmet_higgins_2022_tas` and
blocked `ruiz_parra_2023_tas20`. It applies even where the source published the items under an open
licence: `cucchi_2018_tas20`'s wording came from a CC BY 4.0 PeerJ article that printed all 20 items.

**Both triggers are quote tests, and silence is permission.** Block only on something you can quote
from the rights holder — an enforced fee, or an explicit no-redistribution clause. An instrument
being merely copyrighted, commercially sold, well known, or reproduced somewhere without an explicit
grant is **not** a block. If you cannot find and quote a restriction, extract normally; do not block
on suspicion, and do not open a negotiation with a rights holder. Record the quoted sentence and its
URL — a rights block with no quote in it is not a rights block.

**But the instrument-level restriction is recorded, not ignored.** Where the rights
holder states one, set `wording_rights=NC` on every row of that table and add an
entry to the public issues page. The column is a filterable flag so a commercial
reuser can exclude those tables with a query instead of reading prose; the prose
belongs in `public_note` and on the issues page. Omit the column entirely for tables
with no such restriction — do not emit an empty column to no purpose, the same rule
the `_translated` columns follow.

This keeps the decision reversible. If the stricter reading — that the instrument's
terms travel with the wording wherever it appears — is ever adopted, `wording_rights`
is the query that finds every affected table.

**Watch for wording that is licensed separately from the response data.** The three
`cdm_timss*` tables record `License: GPL-3.0` — the CDM R package's licence, covering the
responses as that package redistributes them. It says nothing about IEA's wording, which
is separate copyright under narrower terms. A table's dictionary licence is evidence about
the response data only; go to the wording's own source for its terms. This recurs for any
assessment redistributed through a package or similar wrapper.
