# Zanesco_2023_Golleretal2020 — parked, NOT for upload (batch_298, 2026-09-22)

`Zanesco_2023_Golleretal2020__items.PARKED.csv` (180 rows = 36 items x 5 resp) was built,
gated and audited, then **held by Ben on 2026-09-22** rather than promoted. It is the single
audit WARN of batch_298 (100% blank `item_text`). Sidecars stay in `itemtables/batch_298/`,
so that batch still documents every table it claimed.

## Why it was parked

It is an **option-only item table**: one `instrument` string, five `option_text` anchors, and
nothing else. `item_text`, `instructions`, `section_prompt` and `correct_response` are blank on
all 180 rows.

The item axis makes it weaker than it first looks. `T1`..`T36` are **not 36 questions** — they
are the *same* attentional-focus probe administered 36 times during the SART. So the missing
`item_text` is one sentence that would then repeat identically on every row, and what a user
gains over the response table is a shared 5-point scale plus one instrument label.

Ben's call under irw#1770. Weaker than `twod_rotation_mather2023` (live in a similar shape but
carrying `instructions` and `correct_response` as well); stronger than `klatt_2016_speed_estimation`
(held, no `correct_response` and no `option_text`).

## Why the stem could not be supplied

Not a fetch failure — the wording appears genuinely unpublished:

- the OSF E-Prime `.ebs2` file's `ScriptContents` is an **encrypted blob**;
- the E-Prime export carries `ProbeD.RESP` and `ProbeD.RT` but **no stimulus-text column**;
- the *Memory & Cognition* version of record is not open access;
- Goller, Banks & Meier (2020), its preregistration, and Zanesco et al. (2024) all **describe**
  the second probe while quoting the paired **first** probe verbatim.

No stem was invented. This unblocks only if the probe wording surfaces — the authors could
supply it on request, which was offered and not taken up.

## What the file carries

- `option_text` — `Completely on-task` / `Mostly on-task` / `Both on the task and off-task` /
  `Mostly off-task` / `Completely off-task`, identical for all 36 items.
- `instrument` — "Mind wandering depth rating (attentional focus probe) embedded in the
  Sustained Attention to Response Task (SART)".

## Instrument attribution — true regardless of the parking decision

The item codes belong to **Goller, Banks & Meier (2020)**'s SART, *not* to any Zanesco
instrument: Zanesco et al. administered nothing, it is an IRT re-analysis, and the table name
points at the secondary source. Specifically the **second** of two paired probes (probe 1 has
six categorical options; probe 2 is this five-point depth rating), matching the live table's
36 items x 5 resp levels and the paper's "Only the attentional focus probe (second probe
question) was examined herein."

Rights: no block. Parked on item-text sufficiency, not on licensing.
