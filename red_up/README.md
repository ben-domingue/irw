# `red_up` — one uploader for every IRW Redivis dataset

```
red_up .                              # menu, then a confirmation
red_up ~/some/batch
red_up a.csv b.csv
red_up . --dataset item_response_warehouse_6 --yes
red_up . --dry-run
```

Exit codes: `0` ok · `1` an upload or row-count check failed · `2` bad input.

## Why this exists

Until now there were **thirteen** near-identical copies of the same ~150-line
script — six in `data/add2redivis/`, four for item text, `src/upload.py`, a
stale one in `automated_finding/irw_output/`, and `data/itemtext/upload.py`.
They differed in one line: the dataset they hardcoded. So the destination was
chosen by *which file you happened to run*, and the only written routing rule
(`irw-automated-finding/SKILL.md`) had gone stale — it still pointed at shard 4.

`red_up` replaces all of them. It is roadmap item 1 (`ben-domingue/irw#1703`),
sub-items 1.1 and 1.2.

## What it does

**Finds the files.** A path argument, resolved to an absolute path *before*
anything else. The old scripts `chdir`'d into their own directory first, so
`python3 upload.py .` never meant your shell's directory.

**Picks a default dataset.** Any `*__items.csv` present ⇒ the newest item-text
shard; otherwise the newest core shard. The menu shows every dataset in
`metadata/redivis_config.R` — Enter takes the default.

Both response data and item text are **shard lists**, because Redivis caps a
dataset at 1000 tables (`ARCHITECTURE.md` §2). A second item-text shard is a
one-line edit to `IRW_TEXT_DATASETS`; nothing in this package changes.

**Excludes what does not belong.** Once a dataset is chosen, files of the wrong
kind are listed and skipped rather than uploaded. This is the guard against the
failure `itemtext/itemtables/clean/` exists to undo: item-text batch
directories legitimately contain `provenance.csv`, `notes.csv` and
`audit_report.csv`, and the old uploaders turned each of them into a Redivis
table. A CSV with *none* of `id`/`item`/`resp` is rejected outright.

**Looks across every shard first.** Which shard a table lives in is not
predictable from its name, and both client packages search newest-first and
return the first match. So uploading an existing table into a *newer* shard
does not replace it — it **shadows** it, leaving two divergent copies with no
error and no suspicious row count. Any such file is flagged `ELSEWHERE` and
defaults to updating the dataset it already lives in.

Every shard of *both* kinds is scanned, so a stray `__items` table that has
landed in a warehouse is still reported. A cross-family match never becomes a
cross-family upload, though: the offered home must itself be able to hold the
file, and when none can, the file is skipped for a human rather than routed
somewhere plausible-looking.

**Replaces properly.** Redivis uploads *append*. `replace_on_conflict` only
replaces an upload of the same name; rows inherited from the previously
released version survive beside it, silently doubling the table (#1677/#1683 —
a batch came back at exactly 2×). Deleting the draft table and recreating it is
the only true replace, and the table description is carried across.

**Proves the row count.** After each table, an actual
`select count(*)` against the draft, compared to the CSV. `numRows` is never
consulted — it reported "no change" for tables that had just doubled.

**Never publishes.** Everything lands on the unreleased draft. Publishing stays
a human click after reviewing the diff (`ARCHITECTURE.md` §4).

## Where things come from

| Thing | Source |
|---|---|
| Owner and dataset names | `metadata/redivis_config.R`, *parsed*, not restated (`IRW_CORE_DATASETS`, `IRW_TEXT_DATASETS`, `IRW_AUX_DATASETS`) |
| Write token | `irw_secrets.load_write_token()` → `~/.config/irw/redivis-write.env` |
| Required columns | `datastandard.md` |

There is no dataset list in this package. `redivis_config.R` is already
authoritative (`ARCHITECTURE.md` §5) and the project already carries three
files that each call themselves the single source of truth; they have drifted
once (#1733). A new shard appears in the menu as soon as it is added there.

`--dataset` refuses any name not in that file. `--allow-unregistered` overrides
it, for scratch datasets only.

## Install

```
pip install -e /path/to/irw/src --break-system-packages
```

Editable, and pointing at a real `src` checkout — `red_up` reads
`metadata/redivis_config.R` relative to itself. Afterwards `red_up` is on
`PATH` and `python3 -m red_up` works from anywhere.

## Tests

```
cd src && python3 -m unittest discover -s red_up/tests -t .
```

Offline; no credentials. The Redivis-facing paths are covered by this
procedure instead, which was run when `red_up` was written:

1. Create a throwaway dataset, upload a 500-row CSV, confirm `count(*)` = 500.
2. Re-upload: confirm still 500, not 1000.
3. **Release** that version, re-upload again, confirm still 500. This is the
   #1677/#1683 case — the draft inheriting rows from a released version — and
   it only reproduces after a real release.
4. Set a table description, re-upload, confirm it survives.
5. Delete the dataset.

Step 3 is also how the missing-draft bug was found: `dataset(name,
version="next")` raises `NotFoundError` when the last version has been released
and no new draft is open. All thirteen predecessors fail there; `red_up` opens
the draft itself (`push.open_draft`).

## Not covered

Roadmap 1.3–1.5: merging `misc/validate_irw.R` with
`automated_finding/irw_triage_updated.py::run_qc()` into one validator, the
GitHub Action, and the sweep over `data/pub/`. `checks.run_validator` is the
seam it plugs into.

## The format gate

Since 2026-09-02 `red_up` will not upload a table that
[`irw_validate`](../irw_validate/README.md) blocks — the other half of
"one validator, one uploader, and a gate between them" (#1703). Findings appear
beside the cheap checks, and a blocked file is skipped with its reason shown.

Three things worth knowing:

- **It does not break the streaming design.** The checks above load nothing;
  the validator needs a whole frame, so it is imported lazily and skipped above
  `irw_validate.MAX_BYTES` (512 MB), with a warning recording the skip. A check
  that quietly does not run is worse than one that says it did not.
- **A missing dependency is an error, not a pass.** If `irw_validate` cannot be
  imported, the upload is blocked. Blocking because pandas is not installed is
  annoying exactly once; passing because pandas is not installed is undetectable
  forever.
- **Heuristics warn, they do not block** — see the profile table in
  `irw_validate/README.md` for why.

## Drafts, and the one-week window

`red_up` only ever writes a **draft** version. Releasing is a human action on
Redivis, and project policy allows changes to sit in a draft for **up to one
week** — releasing after every upload is unmanageable, so batching is expected.

```
python3 -m red_up.drafts              # every dataset, how far behind each one is
python3 -m red_up.drafts --verbose    # and what the draft actually changes
python3 -m red_up.drafts --days 3
```

Exit code 1 means something is past the window.

Two cautions the tool exists to enforce:

- **A successful upload is not a published one.** The `count(*)` check in
  `red_up` verifies the draft. Everything users touch reads the released
  version.
- **Only a wrong answer skips the week.** Not staleness — the test is whether
  the released data would give someone a *wrong* result rather than an
  *incomplete* one. Missing tables and missing rows wait happily; a table
  returning every item twice (`ben-domingue/irw#1816`) does not. See
  `ARCHITECTURE.md` §4.

The check counts *time since the last release*, not the age of a table or of the
draft — both of those reset whenever the draft is touched, so both would read as
minutes old on a month-old backlog.
