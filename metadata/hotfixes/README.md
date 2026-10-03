# Hotfixes

One-off scripts that patch metadata outside the normal pipeline. Check the "run?" column before re-running.

| Script | What it does | Modifies | Run? |
|--------|-------------|----------|------|
| `fix-n_categories.R` | Recomputes `n_categories` from Redivis directly, excluding NA responses from the count. Writes intermediate results to `n_categories.csv`, then patches `metadata.csv`. | `metadata.csv`, `n_categories.csv` | ? |
| `fix-varnames.R` | Diagnostic only. Reads `metadata.csv`, parses the `variables` column, and prints frequency tables of variable names (split by plain, `cov_`, and `itemcov_` prefixes). Nothing is written. | — | ? |
| `itemtextprobs.R` | Diagnostic only. Flags rows in `itemtext_metadata.csv` where `mean_word > 5` but `mean_character < 20` (likely malformed item text). Nothing is written. | — | ? |
| `pezzuti.R` | Diagnostic only. Checks that all pezzuti tables in the IRW dict are present in Redivis metadata, and identifies any stale entries to remove. Nothing is written. | — | ? |
| `08_itemtext_recompute.R` | Full recompute of `itemtext_metadata.csv` for every table, for when the schema gains a column; `08_itemtext.R` is the incremental stage. | `itemtext_metadata.csv` | rarely, on purpose |
| `fix-2301-bibtex-doi.R` | One-time backfill for #2301 (citations naming the wrong paper). `02_biblio.R`'s `refetch_stale_bibtex()` now does this on every run, so rerunning is a no-op. | `biblio.csv` | yes, superseded |
| `report_string_resp_na.R` | Measurement for #2029: what the literal string `"NA"` in a string-typed `resp` does to `n_responses`. The repair is `irw_validate/repair_string_na.py`. | — (report only) | yes, question settled |

## Retired

`fix-licenses.R` (removed 2026-09-06, #1732) merged `Custom_License_Terms` from
the dictionary sheet into `biblio.csv`. It was a hotfix for
[Rpkg#93](https://github.com/itemresponsewarehouse/Rpkg/issues/93) that could
not stick: `02_biblio.R` rebuilds `biblio.csv` from a fixed column list, so the
next pipeline run erased the column every time. `02_biblio.R` now carries
`Custom_License_Terms` itself, for every row, which is what the hotfix was
reaching for.
