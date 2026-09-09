# `irw_validate` — one format validator, with an exit code

```
irw-validate out/*.csv                       # exit 1 if anything blocks
irw-validate out/x.csv --profile core        # the validate_irw.R subset
irw-validate out/x.csv --strict              # warnings block too
irw-validate out/x.csv --json                # for CI
```

Exit codes: `0` ok · `1` something blocks · `2` bad input. Same contract as `red_up`.

`irw-validate` is a console script declared in `pyproject.toml`. If the command is not
found, the editable install predates it — re-run `pip install -e .` from `src/` (this
machine needs `--break-system-packages`, PEP 668). Otherwise `python3 -m irw_validate.cli`
works, but only from `src/`.

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

Response-scale checks illustrate the distinction. An unused top category can
make items on one scale have different observed ranges. Upload already capped
that heuristic at `warn`, but callers of `run_qc()` still received a raw `fail`.
The shared checks now emit `warn` for observed range differences in either
direction; a response-scale `fail` requires explicit documentation, as below.

| profile | used by | contents |
|---|---|---|
| `core` | `validate_irw.R` parity, external contributors | the five R checks only |
| `triage` | callers of `run_qc` | core + heuristics; raw `fail` becomes `error`, raw `warn` stays `warn` |
| `upload` | the gate, the CLI, CI (default) | core + heuristics + the standard's prose rules; heuristics capped at `warn` except `GATE_ERRORS` |
| `legacy` | the 922 `.Rdata` sweep (1.5, not built) | `upload` minus rules that postdate the tables |

`GATE_ERRORS` contains `resp_variation*`, `resp_outside_permitted` and
`resp_scale_constructs`. The latter two are documentation-backed failures.
The width-only `resp_scale_mixed` warning has a separate name and remains
nonblocking unless strict mode is selected. A waiver for that old width-check
name cannot waive a documented `resp_scale_constructs` failure.

## Response-scale evidence

`run_qc()` accepts optional `permitted_values` and `item_constructs` arguments.
`validate_frame()` and `validate_file()` accept the same information through
`context`. These are Python API inputs; there are no corresponding CLI flags or
automatic codebook extraction.

`permitted_values` is either one collection of allowed numeric responses shared
by all items, or a mapping from item identifiers to their allowed collections.
Use the source's documented categories, never categories inferred from the
observed responses. `item_constructs` maps each item identifier to an explicit,
documented construct name. Prefixes and disjoint respondent sets are not
construct evidence.

Item keys must match the original identifiers exactly. Permitted categories
must be finite numeric values (numeric strings are accepted). Integer codes
retain exact precision; fractional categories are compared at the response's
floating-point storage precision, without an approximate matching tolerance.

```python
from irw_validate import validate_frame, validate_file

# Illustrative codebook for one construct assessed in two item formats.
context = {
    "permitted_values": {
        "mc_1": {0, 1}, "mc_2": {0, 1}, "cr_1": {0, 1, 2, 3},
    },
    "item_constructs": {
        "mc_1": "reasoning", "mc_2": "reasoning", "cr_1": "reasoning",
    },
}
report = validate_frame(df, label="reasoning", context=context)
file_report = validate_file("out/reasoning.csv", context=context)
# With run_qc imported by a conversion script: run_qc(df, **context)
```

| Evidence | Raw check result | Meaning |
|---|---|---|
| At least three observed items have different min/max ranges, fewer than 15% differ from the modal pair (checked before nesting) | `item_scale_outlier`: `warn` | Names the isolated items and ranges for source review; does not establish that a column is invalid |
| At least three observed items have different min/max ranges, at least 15% differ from the modal pair, and all ranges form a chain of nested intervals | `resp_scale_nested_support`: `warn` | Unequal observed coverage; this does not establish different scales |
| At least three observed items have non-nested ranges and at least 15% differ from the modal min/max pair | `resp_scale_mixed`: `warn` | Inspect the source and distributions; neither direction nor the majority range makes this a failure |
| Complete usable permitted values, with every observed response allowed | No width-only finding | Unequal documented sets are legitimate, including weighted Barthel items or multiple-choice/constructed-response items |
| A response outside a usable documented permitted set | `resp_outside_permitted`: `fail` | A documented coding violation; valid entries of a partial item mapping are still checked |
| Missing or unusable entries in supplied permitted-value metadata | `permitted_values_unusable`: `warn` | Coverage is incomplete; do not treat the supplied metadata as full validation |
| Complete explicit construct mapping identifies at least two constructs with different observed group min/max ranges | `resp_scale_constructs`: `fail` | Documented construct separation plus distinct observed ranges; independent of permitted sets and the three-item heuristic threshold |
| Unusable supplied construct mapping | `item_constructs_unusable`: `warn` | No strong construct conclusion can be drawn from this mapping |

The two documented failures become `error` under `triage`, `upload` and
`legacy`; `core` excludes these response-scale checks. Complete permitted values
suppress only width warnings, not a documented construct finding. A warning is
not permission to drop an item or split a scale: `multi_scale*` remains a
prefix-based warning requiring source verification before a split. Strict mode
can make warnings block; default upload does not. An HPQ-shaped isolated count
column is named by `item_scale_outlier` even when its range contains the modal
range. A rare legitimate item format also only warns. SDV-shaped ranges of
1–5, 1–7, 1–8 and 1–9 remain nested-support warnings without construct evidence;
this is an explicit limit of inference from response widths.

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
`.name` / `.status` / `.detail`. That interface and the existing positional
arguments remain compatible. The implementation lives in `_checks.py` and is
re-exported by triage; profiles are layered on top by `core.py`. The optional
documentation inputs above refine response-scale results without requiring
existing callers to provide them.

`tests/test_validate.py` pins the exact `(name, status)` emission order for eight
fixtures, captured before the move with one reviewed correction: text-only
responses still fail numeric checks but no longer produce a spurious numeric
range finding. Response-scale regression tests in
`irw_validate/tests/` additionally cover the shared checks and public API profile
behavior, and run in the existing unittest CI suite.

## Staying merged

A shared runtime between R and Python is not possible here — `validate_irw.R`'s
whole value is that it works for a stranger with an R session and a URL, with
nothing else installed. So instead the R file carries `# @check <name>` markers,
and a test parses them and asserts set-equality with `model.CORE_CHECKS`. Two
languages, one list, enforced. Edit one copy and the suite fails.
