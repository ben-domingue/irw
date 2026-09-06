# Hotfixes

One-off scripts that patch metadata outside the normal pipeline. Check the "run?" column before re-running.

| Script | What it does | Modifies | Run? |
|--------|-------------|----------|------|
| `fix-n_categories.R` | Recomputes `n_categories` from Redivis directly, excluding NA responses from the count. Writes intermediate results to `n_categories.csv`, then patches `metadata.csv`. | `metadata.csv`, `n_categories.csv` | ? |
| `fix-varnames.R` | Diagnostic only. Reads `metadata.csv`, parses the `variables` column, and prints frequency tables of variable names (split by plain, `cov_`, and `itemcov_` prefixes). Nothing is written. | — | ? |
| `itemtextprobs.R` | Diagnostic only. Flags rows in `itemtext_metadata.csv` where `mean_word > 5` but `mean_character < 20` (likely malformed item text). Nothing is written. | — | ? |
| `pezzuti.R` | Diagnostic only. Checks that all pezzuti tables in the IRW dict are present in Redivis metadata, and identifies any stale entries to remove. Nothing is written. | — | ? |

## Retired

`fix-licenses.R` (removed 2026-09-06, #1732) merged `Custom_License_Terms` from
the dictionary sheet into `biblio.csv`. It was a hotfix for
[Rpkg#93](https://github.com/itemresponsewarehouse/Rpkg/issues/93) that could
not stick: `02_biblio.R` rebuilds `biblio.csv` from a fixed column list, so the
next pipeline run erased the column every time. `02_biblio.R` now carries
`Custom_License_Terms` itself, for every row, which is what the hotfix was
reaching for.
