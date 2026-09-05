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

### No-redistribution clauses override the source licence — ruled 2026-09-04

**A quotable clause barring redistribution of the instrument governs, even when IRW's wording came
from an openly licensed deposit.** Ruled by Ben on `CV_OASIS_ODSIS_PPE_Novak_2020_DSES`: the Daily
Spiritual Experience Scale requires registration with its author, and the Fetzer Institute copy
states *"Permission of author required to distribute or copy"*. IRW's wording came from Underwood's
own **CC BY 3.0** article; the clause was ruled to govern anyway.

This is the open question the WHOQOL ruling above declined to settle by drift, now settled in the
strict direction. Together with the fee-licence ruling it means **the source deposit's licence is no
longer sufficient on its own** — a rights holder's own restriction on the instrument outranks it,
whether that restriction is a redistribution bar or an enforced fee.

**It still fires only on something you can quote.** Silence remains permission, exactly as under the
NC rule: an instrument that is merely copyrighted, or reproduced without an explicit grant, is not
blocked. What changed is that finding the clause on the rights holder's copy is now enough — you no
longer get to rely on the deposit you happened to take the words from.

**Consequence not yet worked through:** this narrows the ECR-R decision for a whole class of
instruments, and already-shipped tables have never been audited against it. No re-audit has been
run; a table shipped before 2026-09-04 under "the source licence governs" may not survive this rule.
That sweep is outstanding work, not a settled position.

### Fee-licensed instruments — ruled 2026-09-04

**An enforced licence fee disqualifies an instrument's wording, even where IRW's copy came from an
openly licensed deposit.** Ben ruled this on the TAS-20 (Toronto Alexithymia Scale), whose rights
holders charge a per-study fee and have enforced it — a 2021 *Molecular Autism* paper was retracted
over it.

This is the deliberate extension the WHOQOL ruling above said should be settled rather than reached
by drift, and it goes further than that one in a way worth being explicit about. The WHOQOL turns on
a clause forbidding the *act* of distribution. This does not: `cucchi_2018_tas20`'s wording came
from Cucchi, Hampton & Moulton-Perkins (2018), a **CC BY 4.0** PeerJ article that reproduced all 20
items itself, and IRW is declining to redistribute text an open licensor already published. The
argument against was put and the ruling stands: the fee is enforced against exactly this kind of
reuse, and an open deposit does not extinguish it.

**What fires it.** The rights holder levies a fee for use of the instrument, and there is evidence
it is enforced. A scale being copyrighted, sold as part of a manual, or merely free-of-charge does
not fire it — that boundary is unchanged from the NC rule above.

**Scope.** Blocked on this rule so far: `cucchi_2018_tas20` (extracted, uploaded, then deleted from
the draft), the already-live `rmet_higgins_2022_tas` (removed from the draft, so it disappears at
the next release), and `ruiz_parra_2023_tas20` (blocked before extraction). Any future TAS-20 table
is blocked by the same rule.

**This one DOES generalise, unlike the WHOQOL ruling** — it is a rule about fee-licensed
instruments, not about the TAS-20. Apply it to any instrument meeting the test above, and record the
fee and the evidence of enforcement in `provenance.csv` `note` so the basis stays auditable. A
withdrawn table keeps its `uploaded` date as history and carries the withdrawal in `public_note`;
do not blank the date to make the table look as though it never shipped.

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

### Two pages, two terms, one rights holder — the SWLS, ruled 2026-09-04

**When a rights holder publishes the same instrument under two different statements of terms, the
terms of the page you actually took the wording from govern.** Ben ruled this on the Satisfaction
With Life Scale, after batch_028 blocked `duboz_2021_swls` and shipped `dudasova_2021_swls` — same
instrument, same batch, opposite verdicts.

The two pages, both fetched directly on 2026-09-04:

> "These scales are copyrighted by Ed Diener and his co-authors. Although copyrighted, all of these
> scales may be used by researchers as long as proper credit is given… **The use of these scales is
> permitted for non-commercial purposes only.**"
> — eddiener.com/scales, applying collectively to the SWLS, SPANE and the Flourishing Scale

> "The scale is copyrighted but **you are free to use it without permission or charge by all
> professionals (researchers and practitioners) as long as you give credit to the authors** of the
> scale: Ed Diener, Robert A. Emmons, Randy J. Larsen and Sharon Griffin…"
> — labs.psychology.illinois.edu/~ediener/SWLS.html, which is also where `SWLS_English.doc` — the
> file our extractions actually open — is hosted

**Correct the record on one thing before using this.** The batch_028 orchestrator reported that both
agents had misquoted the Illinois page and that it declares the SWLS *in the public domain*. It does
not; the phrase does not appear on that page at all, checked directly. The agents' quotes were right
and the re-check was wrong. So this is **not** the TIMSS 2003 shape — one page stating a
public-domain claim and an NC restriction together, where the restriction governs. It is two separate
pages stating different terms, and the TIMSS rule does not reach it.

**The rule.** This is the ECR-R decision applied one level in: the licence of the source IRW actually
copied from governs, and that stays true when both candidate sources belong to the same rights
holder. So for the SWLS:

- wording published in the **study's own openly licensed deposit** ships (this is what makes
  `altahla_2024_swls` safe — it was rebuilt on 2026-08-17 to take `item_text` from the study's own
  source-file headers, `mapping_basis=data_labels`, not from any Diener page);
- wording taken from **`SWLS_English.doc` on the Illinois page** ships — that page distributes the
  document and states no non-commercial restriction;
- wording taken from **eddiener.com** does not — that page states one.

**Record which page you opened.** The whole ruling turns on it, so `source_ref` must name the
specific page, not "Diener's site". A table blocked for taking the words from eddiener.com is not
determinately blocked: the same words are available from the Illinois page under terms that permit
shipping, so it is a *retryable* verdict and belongs back in the queue as `pending`, not `blocked`.
`duboz_2021_swls` was reopened on exactly that basis.

**The weakness Ben accepted, stated plainly so nobody rediscovers it as a defect.** This lets an
extractor take the more permissive of two pages from the same holder, which is close to
forum-shopping. It was ruled the better error than the alternative, which would block ~11 SWLS tables
and eventually reach a live one on terms the holder's own distribution page contradicts. If a rights
holder ever withdraws or supersedes the permissive page, this ruling should be revisited rather than
relied on.

**Scope.** 14 SWLS-named tables: `altahla_2024_swls` and `campos_2023_swls` already shipped,
`dudasova_2021_swls` ships under this ruling, `duboz_2021_swls` is reopened, and 10 remain pending.
Each pending table takes the same three-way test above — the answer depends on which source published
the wording, not on the instrument.

### PROMIS and the HealthMeasures family — ruled 2026-09-05

**IRW does not ship PROMIS item wording.** Ruled by Ben after batch_031, where three agents
blocked their PROMIS tables and a fourth shipped one on the batch_022 precedent. The clause,
from the rights holder's own Terms of Use (Approved Version 1.12-2017, section "Single Use,
Reproducibility, and Distribution"), fetched independently three times — the PDF's md5 is
`fe672ca0c092d6b324a8098ac049c7e3` and two agents plus the triage pass all retrieved it
byte-identically:

> "User shall not reproduce HealthMeasures Instruments except as needed to conduct the
> authorized single use … User shall not distribute, publish, sell, license, or provide
> HealthMeasures products, by any means whatsoever, to third parties not involved with the
> authorized single use as stated above, without the prior written agreement of the Provider."

That is a quotable redistribution bar, so the DSES ruling applies unchanged: **it governs even
though IRW's copies came from CC0 deposits.** The same section also reads "publicly available
for use without licensing or royalty fees for individual research", the free-but-restricted
shape already ruled on for TIMSS and HEXACO — free of charge is not free of terms.

**Adaptations are covered too.** Ruled the same day on the three `evpromisi_stone_2021_dd*`
tables, whose wording is the *study's own* modified daily-diary rewrite of PROMIS bank items
(24-hour recall, Never…Always anchors, labelled in the codebook "Modified daily diary version of
EDDEPnn") rather than standard PROMIS short-form wording. A derivative of a barred instrument
stays barred. This avoids having to draw a line about how much rewriting stops being the
original, and it is the reason `_ddeddep` was withdrawn to `itemtext/quarantine/batch_031/`
after an agent had shipped it.

**What is NOT covered — check the instrument, not the deposit's name.** `promis1wave1_cesd` and
`promis1wave1_haq` sit in the same PROMIS Wave 1 deposit but are the CES-D and the HAQ, which
the codebook keeps in its *legacy-items* tables rather than its PROMIS bank sections. They carry
their own separate rights and are untouched. Likewise `evpromisi_stone_2021_cdiag` is the study's
own 12-item chronic-diagnosis checklist despite the `evpromisi_` prefix (see irw#1972). A table
is in scope because of the instrument it holds, never because of what the study or the file is
called.

**Scope applied 2026-09-05.** Four tables blocked in batch_031 (`evpromisi_stone_2021_ddedanx`,
`_ddeddep`, `_ddpainin`, `_global`). Seven withdrawn from the corpus:
`promis1wave1_{anger,anxiety,depression,fatigue,pain,physicalfunction,social}`, deleted from the
`irw_text` draft so they leave at the next release. **They were LIVE in v16.0 when this was
decided, not sitting unreleased** — a fact that was got wrong first time round and had to be
corrected before the decision was final. `red_up.drafts --verbose` labels every upload `added`;
that reflects what the draft session added and is **not** a diff against the released version.
To tell whether something is public, compare `version="current"` against `version="next"`
directly. Until the next release the withdrawn wording still exists in v16.0, so the deletion is
recoverable up to that point and not after it.

**Withdrawal entries are not published.** Ruled by Ben 2026-09-05, at the same time: the issues
page carries no entries recording withdrawn item text. The seven WHOQOL/DSES/TAS-20 entries that
existed were removed, and no PROMIS entries were written. His reasoning: the fact of a withdrawal
is not useful to a data user and tacitly advertises that IRW published material it should not
have. Record withdrawals in `provenance.csv` and the round log, which are the internal audit
trail; do not add them to `itemtext_issues.qmd`.

### Picture-stimulus tasks: ship the table, leave `item_text` blank — ruled 2026-09-05

**A task whose stimuli are images with no text still gets an item table; `item_text` is left blank
by design.** Ruled by Ben on the Enkavi 2019 Self-Regulation Ontology battery. The table then
carries what the source really does publish — `instructions`, section structure, and the
accuracy labels in `option_text` — while the stimulus identity stays where it already is, in the
item code. Nothing is invented, and nothing IRW wrote is placed in a field defined as the wording
respondents read.

**This settles a corpus that had answered the same question three ways.** `twod_rotation_mather2023`
(batch_011) shipped 304 picture items with `item_text` blank by design and is the precedent this
ruling adopts. `enkavi_2019_stroop`, `_navon`, `_ant_flanker` and `dd_rotation` shipped IRW-authored
stimulus descriptions — navon's own note says "item_text for this table is IRW's description of the
Navon stimulus, not wording anyone read". `gilbert_meta_39` was left unshipped as figural.

**The already-shipped descriptions stand.** Ruled at the same time: the three live `enkavi_2019_*`
tables are correct, disclosed, and in v16.0, and re-uploading live tables to *remove* usable
information is not worth it. So the corpus is knowingly mixed — four tables carry authored
descriptors, everything from here does not. Do not "fix" them, and do not cite them as precedent.

**Reopened under this ruling:** `enkavi_2019_simon`, `enkavi_2019_gonogo` and
`enkavi_2019_stopsignal` go back to `pending`. Each was blocked only because no wording exists,
which is no longer a reason to block. Their recovered material is already banked in
`itemtables/pending_index_notes.csv` so nothing needs re-deriving — including, for `gonogo`, the
binding that `style.css` fixes `#stim1=orange` and `#stim2=DodgerBlue` with only the go/no-go role
counterbalanced. Note for whoever extracts `stopsignal`: it has no shippable `correct_response`,
because the shape-to-key mapping is shuffled per session.

**`enkavi_2019_dpx_axcpt` stays blocked, and for a different reason.** Its probe labels are
randomised **per participant** — `experiment.js` shuffles `probe1..6` for each worker, confirmed
in the raw data — so `AX_probe3` denotes a different image for different people. The item code
does not name a stable stimulus, which is a statement about that dataset rather than about
pictures. Blank `item_text` would not fix it, because the problem is the code, not the text.

**The general test this leaves.** Ask whether the source publishes wording, not whether the task
is verbal. If it does, ship it. If it does not, ship the table with `item_text` blank. Block only
when something else is wrong — the rights bar it, or, as here, the item codes do not denote a
stable thing.
