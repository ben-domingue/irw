# Nguyen gynecologic surgery: provenance and metadata

Refs #1754. These five existing response tables come from one published
Dataverse workbook. This change reconstructs their missing conversion script,
prepares the missing dictionary/tag rows, and corrects the DOI resolver's
malformed author name. The dictionary and tag CSVs here are proposed inputs for
review and manual import; committing them does not update the public catalogue.

## Verified source

- [Harvard Dataverse, DOI 10.7910/DVN/X2C2PL, version 1.0](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/X2C2PL&version=1.0).
- Author field: **Van Bich Nguyen**. Depositor: **Tran, Son**. Neither field
  identifies the IRW uploader. The original local metadata names its contributor
  `automated`; this reconstruction and metadata submission are attributed to
  Sinew Lu (`sinew-07`, dictionary spelling `sinew`). Original upload identity
  has not independently been established from upload logs.
- Published 6 August 2026 under **CC0 1.0**. The 2026 filename year is the
  dataset publication year; observations were collected May–December 2024.
- [Source workbook, file 14113156](https://dataverse.harvard.edu/api/access/datafile/14113156):
  `gycosurganx_data_censored.xlsx`; MD5 `304a3442b9e3b0700410e65612f89602`;
  SHA-256 `d6642499ad8fea23787cd84372be70d6a7847b2dc893587b9ef57a0a2932df68`.
  Internal sheets are `data`, `vars`, and `codes`.

The 394 participants were women undergoing gynecologic surgery at the National
Hospital of Obstetrics and Gynecology in Hanoi. The shipped ID set contains all
394 source IDs, with ages 15–77: 11 under 18 and 383 aged 18 or older. `Mixed`
and `Adolescent (12-18y)` describe this same shipped sample; the younger group
is 2.79%, above the tag rule's 2% threshold.

| Existing table | Items | Responses | Measurement occasion | Recorded scores |
| --- | ---: | ---: | --- | --- |
| `nguyen_2026_barthel` | 10 | 3,940 | 48 hours after surgery | Weighted item scores, 0/5/10/15 across the table |
| `nguyen_2026_gad7` | 7 | 2,758 | Before surgery | 0–3 |
| `nguyen_2026_isi` | 7 | 2,758 | 48 hours after surgery | 0–4 |
| `nguyen_2026_mspss` | 12 | 4,728 | Before surgery | 1–7 |
| `nguyen_2026_pic` | 9 | 3,546 | Before surgery | 1–5 |

PIC denotes the deposit's preoperative information/counseling checklist. A
separate validated instrument or instrument citation is not established.
The workbook labels the Barthel activities but does not give item-specific
category definitions. Its weighted scores are preserved and are consistent
with the [standard Barthel scoring form](https://klassifikationen.bfarm.de/icd-10-gm/kode-suche/htmlgm2022/zusatz-06-barthelindex.htm);
the exact administered version and scoring protocol remain unverified.

## Reproduction and boundaries

From the repository root, using a Python environment with this repository and
Excel-reading dependencies installed:

```sh
python -m pip install -e . openpyxl
mkdir -p data/nguyen_2026_gyn_surgery_raw
curl -fL https://dataverse.harvard.edu/api/access/datafile/14113156 -o data/nguyen_2026_gyn_surgery_raw/source.xlsx
python data/nguyen_2026_gyn_surgery.py --input data/nguyen_2026_gyn_surgery_raw/source.xlsx --out-dir data/nguyen_2026_gyn_surgery_raw/reproduced
```

The script pins the published checksum and checks every table with the current
`upload` validator before writing. It refuses existing target files. It
preserves source `ID`, item identifiers, integer responses and the existing
`id,item,resp` layout and row order.

An independent comparison against the pre-existing local CSVs and ZIP found
all **17,730 responses**, **394 IDs** and **45 items** identical. All five files
were also reproduced byte-for-byte. No missing responses or duplicate
participant-item keys were found. This is a reconstructed converter; the
original processing script was not recovered.

The existing exports omit 14 source columns: eight demographic, three clinical
and three postoperative pain variables. Twelve derived total/group/subscale
variables listed in `vars` are already absent from the released `data` sheet;
the reconstruction does not claim to have removed them. No responses are
imputed, recoded, filtered or deduplicated by the reconstruction. Processing
before the public deposit remains unverified.

All tables pass the current `core` and `upload` profiles without overrides.
Barthel/MSPSS retain response-support heterogeneity warnings, and Barthel/GAD-7
retain category-concentration warnings. Those patterns are present in the
source. The heuristic reports only its first concentrated item per table;
that does not imply only two items exceed its threshold.

## Dictionary, tags, and citation

`dictionary_rows.csv` preserves all 14 live dictionary columns, including the
two separate columns both named `Custom License`. `DOI (for paper)` is the
historical column name; the existing dictionary and
`metadata/tests/test_dictionary_dois.R` also accept dataset DOIs there. These
rows explicitly cite a **data set**, with no claim of a verified article DOI.

`tags_proposed.csv` uses the live tag sheet's 13 columns. `Rater` is blank until
a human has reviewed the proposals. The clinical setting and restriction to
gynecologic surgical patients support `Clinical, Targeted/specific`. The
`vie` language tag is an inference from the Hanoi patient cohort, as allowed
by the tag rules; actual administration language is not established. English
GAD-7/MSPSS wording is available in the codebook, but this does not establish
the administered wording. Unverified item-text and Barthel administration-mode
fields are left blank.

On 6 September 2026, production-style DOI content negotiation returned
`author = {ich Nguyen, Bich}`. This contradicts the native Dataverse author
field. `metadata/bibtex_overrides.csv` records the verified citation and its
source. The pipeline uses it for new and already cached rows of this exact
DOI, preserves the literal author name, and never manufactures bibliography
rows before dictionary import. The ordinary DOI route remains unchanged for
other sources. Offline regression fixtures cover both paths and run in CI.

Keep the five existing table names. Their full names do not collide with the
Nguyen online-learning families, and they are already public identifiers.
Disambiguation belongs in the source DOI, study description and the descriptive
`nguyen_2026_gyn_surgery.py` script name. Any later rename requires a separate
coordinated decision across response tables, citations, tags and clients.

## Remaining publication steps

The 6 September 2026 snapshots of the live dictionary (4,375 rows) and tags
sheet contain none of these five names. The public catalogue's bibliographic
index also omits all five; a shard-routing entry alone is not a discoverable
dataset listing.

The [Barthel pilot page](https://itemresponsewarehouse.org/tables/nguyen_2026_barthel/)
shows the correct response counts, but its machine-readable record supplies
only a generic IRW citation and a license placeholder. The other four do not
have individual pilot pages; their HTTP 404 responses are not evidence that
the response tables are missing from Redivis.

1. Review and import the **five data rows only** from `dictionary_rows.csv`
   into the [core dictionary](https://docs.google.com/spreadsheets/d/1nhPyvuAm3JO8c9oa1swPvQZghAvmnf4xlYgbvsFH99s/edit?gid=1337607315#gid=1337607315).
   Recheck exact names first to avoid duplicates; retain both Custom License
   columns.
2. Review `tags_proposed.csv`, fill `Rater`, and import its five data rows into
   [IRW Tags](https://docs.google.com/spreadsheets/d/1V3ef0sa7HKtJJd2cgqRAkEdfbpGWDD1JIyQa6HwVK7g/edit?gid=126134123#gid=126134123).
   The human-sheet rows take precedence over the existing automated abstentions.
3. With this citation correction in the working checkout, regenerate the
   affected metadata through the authoritative wrapper, e.g.
   `.claude/skills/irw-site-update/scripts/run_pipeline.sh 02 03`. Review the
   complete diff, including unrelated rows the stages may encounter.
4. Use the normal `red_up` metadata path to prepare a Redivis draft for human
   review/publication. Verify the released bibliography and tags and the next
   site rendering; retain all five original table identifiers.

The public metadata repair remains pending these steps. This PR references
#1754 rather than automatically closing it. See `ARCHITECTURE.md` for the
manual Sheet-import and separate publication workflow.
