# movac_pakpour2022 (CONTROL)

**Lead.** Source `control`. In the legacy sweep this table got severity `ok` (72,096 rows, 12 items, 6,008 participants), and no problem is known. I ran the full checklist anyway.

## Checks run

1. **Size and live resolution.** `metadata.csv` gives 72,096 responses, 6,008 people, 12 items, 7 categories, columns `id|item|resp`. The live table is `datapages.item_response_warehouse:as2e:v65_0.movac_pakpour2022:01v3`.
2. **Live vs metadata row count.** The aggregate query returns 72,096 rows, 6,008 ids, 12 items and 0 null `resp`, with id running from 1 to 6008. **These match metadata exactly.**
3. **Upload validator on live data.** I read the rows (72,096) with `redivis_shim.install()` and then `to_pandas_dataframe`, wrote them to a scratch CSV, and ran `python3 -m irw_validate.cli <csv> --profile upload --verbose`.
   - Result: "conforms / passes / ok -- 4 checks, nothing to report", exit 0.
   - Independently: `resp` takes only {1,...,7} with no non-integers. Every id has exactly 12 rows, with no repeated `id`+`item`. The largest per-item modal share is 34%. MoVac7 has a reversed distribution, which is consistent with a reverse-worded item and not a defect.
4. **Rights check of the item text.**
   - The live item text is `irw_text` table `movac_pakpour2022`, 84 rows (12 items × 7 options). Its item codes are identical to the response table's.
   - With the register loaded, `rights.check_item_text(...)` returns `[]` and `rights.check_item_codes(...)` returns `[]`. The register's only Pakpour row is FCV-19S, a different instrument.
   - Source licences:
     - The Dataverse deposit doi:10.7910/DVN/U8ZYDF is **CC0 1.0** (from the Dataverse API).
     - The Data in Brief article (PMC8957882) states: "This is an open access article under the CC BY license (http://creativecommons.org/licenses/by/4.0/)".
   - The deposit's own `Questionnaire.docx` prints all 12 items and the 7 anchors, word for word as the live text has them. It contains no copyright, permission or commercial clause.
   - The article says the scale was adapted from MoVac-Flu "with the kind permission of" its developer (Vallée-Tourangeau). That is permission that was obtained, not a restriction on the wording. **No stated restriction.**
5. **Data-note check (script header plus the source).**
   - `data/movac_pakpour2022.R` has no header. It reads `imputate(fivecountries).tab`, drops `group, Gender, age, edu_level, profession`, and melts to long format with `id = row index + 1`. Nothing in `metadata/data_notes.csv` covers this table.
   - Because the file name says "imputate", I downloaded the deposit, which has one data file of 6,053 rows. Findings:
     - **45 rows are whole-person mean fills.** All 45 are in region `group == 4`. In each of them, all 12 items equal the same non-integer vector (MoVac1 = 5.50956, MoVac2 = 5.438783, ...), i.e. the item means.
     - Removing those 45 rows gives a 6,008 × 12 matrix that is **identical, cell for cell, to the live table**.
     - The local archive copy (`../data/pub`, dated 2024-10-09) already had 72,096 rows.
     - So the rows were dropped correctly when the table was built. The committed script, however, does not drop them: re-running it would produce 72,636 rows, 540 of them non-integer.
   - The article's full text says nothing about imputation or missing data. So if the deposit used whole-number imputation elsewhere, the table cannot show it.

## Verdict

The **response table is clean**, and all four standard checks pass.

The checklist did surface one real thing, and it is not a table defect. The source deposit is an imputed file: 45 of its 6,053 respondents are item-mean fills. IRW correctly excludes them, but nothing records that.
- A user comparing the table with the paper's N will see 6,008 vs 6,053 and has no way to learn why.
- The deposit's file name also signals imputation that the table cannot express.
That fits #2529's test (something about the source that a user should know). Suggested note: *"The deposit (imputate(fivecountries).tab) is an imputed file. 45 respondents (region 4) whose 12 answers were each the item mean are excluded here, so N = 6,008, not 6,053. Imputation that produced whole-number values, if any, cannot be detected."*

A secondary finding, recorded here only: the script does not reproduce the live table. The script needs one line (drop rows where any `resp` is a non-integer) plus a comment. This is not a data fix.

- **proposed_outcome:** `data_note`
- **confidence:** medium. The facts are high-confidence. Whether a correctly handled exclusion warrants a note is the judgement call.
- **group:** `note:source_mean_imputed_rows_excluded`
- **minutes:** about 35. Of that, 10 went on the four standard checks, and the rest on the "imputate" follow-up and the deposit download.
- **redivis_reads:** rows:72096 for the response table, plus rows:84 for the item text. There were also 3 aggregate queries.

**Noise count for a clean table:** 0 false alarms from the validator or the rights check. The one positive (the data note) is real, but it came from reading the script and fetching the source, not from any automated check.
