# `irw_validate` — one format validator, with an exit code

```
irw-validate out/*.csv                       # exit 1 if anything blocks
irw-validate out/x.csv --profile core        # the validate_irw.R subset
irw-validate out/x.csv --strict              # warnings block too
irw-validate out/x.csv --json                # for CI
```

Exit codes: `0` ok · `1` something blocks · `2` bad input. Same contract as `red_up`.

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
