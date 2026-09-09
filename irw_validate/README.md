# `irw_validate` — one format validator, with an exit code

```
irw-validate out/*.csv                       # exit 1 if anything blocks
irw-validate out/x.csv --profile core        # the validate_irw.R subset
irw-validate out/x.csv --strict              # warnings block too
irw-validate out/x.csv --json                # for CI
```

Exit codes: `0` ok · `1` something blocks · `2` bad input. Same contract as `red_up`.

## Installing

```
pip install irw-validate                    # once published
pip install -e /path/to/irw/src/irw_validate   # from a checkout
```

pandas and the standard library, nothing else — no Redivis, no credentials, no
network. That is deliberate: this is the thing an outside contributor runs
against their own file before depositing it, and they should not have to clone
the pipeline or hold a token to do it.

Two optional extras exist for cases that are not that:

| Extra | Adds | Needed for |
|---|---|---|
| `[rdata]` | pyreadr | validating `.Rdata`/`.rda`/`.rds` directly. Converting to CSV first needs nothing. |
| `[live]` | redivis | the `live_*` and `repair_*` modules, which read published tables. Pipeline tools; `validate_file` never touches the network. |

Until 2026-09-09 this package shipped inside `irw-red-up`, the uploader
distribution, so the only way to get the validator was to install the writer.
That was an accident of packaging: `../pyproject.toml` keeps `red_up` out of
Python-pkg because a write-scoped uploader would change what that package is,
and none of that reasoning applies to a checker that opens a CSV.

`irw-validate` is a console script. In a checkout without the install,
`python3 -m irw_validate.cli` works from `src/`.

## Why this exists

The checks were forked, and neither half could gate anything:

| | checks | callers | exit code |
|---|---|---|---|
| `misc/validate_irw.R` | 5 | **nothing in the repo** | no |
| `irw_triage_updated.py::run_qc` | ~20 | 50 scripts in `data/` | no — its `__main__` exits 0 however many fail |

So "is this table valid?" had two answers and no way to act on either. This is
roadmap item 1 (`ben-domingue/irw#1703`), sub-items 1.3 and 1.4 — the other half
of the work `red_up` started.

It also makes `datastandard.md` executable. The standard is 348 lines of rules
stated in prose — a sample floor of 100 unique ids, table names ≤40 characters,
`[id, item, resp]` first — and until now not one was enforced by anything.
`ARCHITECTURE.md`'s Rule 2 asks for exactly this: *where a rule can be made
executable, make it executable instead of writing it down.*

## Profiles, and why severity is not a property of a check

**Severity depends on the (check, profile) pair.** This is the central design
decision, and it exists because the checks were written for *triage* — is a
machine's guess at a conversion worth a human's time — and are now also asked to
gate *publication*, which has a different cost of being wrong.

`resp_scale_mixed` is the worked example. It is `fail` today, and
`data/cao_2026_cdss.py` documents a table that trips it legitimately: an unused
top category on a left-skewed 1–7 scale reads as a second scale. Had every
heuristic become a blocking error, the gate would have rejected that correct
table on day one.

| profile | used by | contents |
|---|---|---|
| `core` | `validate_irw.R` parity, external contributors | the five R checks only |
| `triage` | `run_qc`'s 50 callers | core + heuristics, **exactly today's severities** |
| `upload` | the gate, the CLI, CI (default) | core + heuristics + the standard's prose rules; heuristics capped at `warn` except `GATE_ERRORS` |
| `legacy` | the 922 `.Rdata` sweep (1.5, not built) | `upload` minus rules that postdate the tables |

`GATE_ERRORS` is currently exactly `{resp_variation*}` — a `resp` with one
distinct value carries no information for any model, at any altitude. It grows
one documented case at a time.

### Literal missing-value tokens (#2029)

For `upload` and `legacy`, every non-missing `resp` must parse as a number.
There is no 1% allowance for invalid values. File validation preserves literal
text such as `NA`, `N/A`, `NULL` and whitespace so it can report an error with
the count and up to five examples. A genuinely empty CSV field (including
`""`) remains missing: partial missingness is a `resp_na` warning; an entirely
missing response column still blocks. No source file or input frame is edited.

CSV/TSV/TXT validation makes a second pass reading only `resp` with pandas'
default NA-token conversion disabled. Other columns keep their existing
parsing behavior, and clean numeric response columns still infer numeric types.
Item-text tables use their separate schema and retain their existing reader.
The `core` and `triage` profiles retain their earlier parsing and numeric
threshold; callers using `run_qc` should use `validate_file(..., profile="upload")`
on the written file when they need this publication check.

For an in-memory frame, genuine nulls remain missing and literal text is
checked, but a token already erased by an upstream reader cannot be recovered.
The existing 512 MiB file-size cap still applies; files over it receive only
name checks. This change does not repair historical tables, resolve the meaning
of their missingness, or alter published response counts. Review source coding
before changing rows; the finding deliberately does not prescribe deletion.

## The override

```
irw-validate x.csv --override-check resp_scale_mixed \
    --override "two response formats, one construct; author confirmed 2026-09-02"
```

The reason is the flag's **argument**, so overriding without saying why is
structurally impossible. It is not called `--force` or `--no-verify`: those names
invite reflex use. A reason under 20 characters is rejected. Overridden findings
are reprinted under `OVERRIDDEN` rather than suppressed, and appended to
`processing_notes/validator_overrides.csv`.

Without `--override-check` the reason waives every error; with it, only the named
checks, so unrelated failures keep blocking.

## The 50 callers

`data/*.py` scripts do `from irw_triage_updated import run_qc` and read
`.name` / `.status` / `.detail`. **None of them needed an edit.** The check
bodies were *moved* into `_checks.py` verbatim and re-exported, so `run_qc`
behaves exactly as before — profiles are layered on top by `core.py`, never
underneath.

`tests/test_validate.py` pins the exact `(name, status)` emission order for eight
fixtures, captured before the move. That golden test is the reason the refactor
was safe to make at all: 50 files that otherwise only fail at someone else's
runtime.

## Staying merged

A shared runtime between R and Python is not possible here — `validate_irw.R`'s
whole value is that it works for a stranger with an R session and a URL, with
nothing else installed. So instead the R file carries `# @check <name>` markers,
and a test parses them and asserts set-equality with `model.CORE_CHECKS`. Two
languages, one list, enforced. Edit one copy and the suite fails.
