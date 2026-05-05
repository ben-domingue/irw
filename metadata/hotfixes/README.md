# Hotfixes

One-off scripts that patch metadata outside the normal pipeline. Check the "run?" column before re-running.

| Script | What it does | Modifies | Run? |
|--------|-------------|----------|------|
| `fix-licenses.R` | Merges `Derived_License` and `Custom_License_Terms` from the IRW Google Sheet into `biblio.csv`. See [issue #93](https://github.com/itemresponsewarehouse/Rpkg/issues/93). | `biblio.csv` | ? |
| `fix-n_categories.R` | Recomputes `n_categories` from Redivis directly, excluding NA responses from the count. Writes intermediate results to `n_categories.csv`, then patches `metadata.csv`. | `metadata.csv`, `n_categories.csv` | ? |
| `fix-varnames.R` | Diagnostic only. Reads `metadata.csv`, parses the `variables` column, and prints frequency tables of variable names (split by plain, `cov_`, and `itemcov_` prefixes). Nothing is written. | — | ? |
| `itemtextprobs.R` | Diagnostic only. Flags rows in `itemtext_metadata.csv` where `mean_word > 5` but `mean_character < 20` (likely malformed item text). Nothing is written. | — | ? |
| `pezzuti.R` | Diagnostic only. Checks that all pezzuti tables in the IRW dict are present in Redivis metadata, and identifies any stale entries to remove. Nothing is written. | — | ? |
