"""Trang, Truong & Ha (2023), Heliyon -- Vietnamese validation of Gu's (2018)
Vocabulary Learning Questionnaire.

Source: https://doi.org/10.1016/j.heliyon.2023.e16009
DOI: 10.1016/j.heliyon.2023.e16009
Data: mmc1.xlsx (Europe PMC supplementary archive, PMC10176061)
License: CC BY 4.0

722 Vietnamese learners of English completing all 62 items of Gu's Vocabulary
Learning Questionnaire on a 1-7 scale. Found by the 2026-08-25
educational-measurement term sweep (PMC mode) -- the first candidate that gap
produced, and the reason the terms were added.

Tables written
--------------
trang_2023_vocabulary_beliefs      10 items, 1-7
trang_2023_vocabulary_strategies   52 items, 1-7

Two tables, matching the two constructs the paper validates and names in its
title ("vocabulary learning belief and strategy"). The strategies scale has
seven dimensions and the beliefs scale two; the full mapping is recorded below
so anyone wanting a finer split has it without re-deriving it.

How the item-to-scale mapping was obtained
------------------------------------------
The spreadsheet has a **three-row merged header** -- top-level construct,
dimension, then the `Q` number -- so the grouping comes from the data file
itself rather than from inference. Forward-filling rows 0 and 1 across the
merged cells gives:

    Beliefs about vocabulary learning   Q1-Q10
        Words should be memorized           Q1-Q6
        Words should be learned through use Q7-Q10
    Metacognitive strategies            Q11-Q17
        Selective attention                 Q11-Q13
        Self-initiation                     Q14-Q17
    Inferencing (guessing strategies)   Q18-Q24
    Using dictionary                    Q25-Q31
    Taking notes                        Q32-Q37
        Choosing which word to note         Q32-Q34
        Deciding what information to note   Q35-Q37
    Rehearsal                           Q38-Q46
        Use of word lists                   Q38-Q40
        Oral repetition                     Q41-Q46
    Encoding                            Q47-Q58
        Visual / auditory / word-structure / contextual, three items each
    Activation                          Q59-Q62

The deposit also ships the questionnaire as `mmc2.docx`, but that appendix is
Gu's *original* instrument "with deleted items highlighted", and the
highlighting is not present in the file's XML -- so its numbering (1-58, with
the guessing and dictionary items untagged) cannot be aligned to the 62
administered columns. The merged header is the reliable source; it also
explains the appendix's apparent gaps exactly (items 18-31 are the guessing
and dictionary blocks, and Activation is the material beyond 58).

Coding notes
------------
* `Student ID` is unique across all 722 rows and is used as `id`.
* All 62 items span 1-7 with no out-of-range values and no constant items.
* `Gender code` is carried as `cov_gender`. The parallel `Gender` text column
  is not: it is mojibaked in the source (`KhÃ¡c` for `Khác`) and, at 551/170/1,
  its single "other" respondent is collapsed into code 0 anyway, so the code
  is both cleaner and less identifying.
* Item labels are the source's `Q1`..`Q62` so item text joins back to the
  published appendix numbering.
"""

import io
import os
import zipfile

import pandas as pd
import requests

SUPP = ("https://www.ebi.ac.uk/europepmc/webservices/rest/"
        "PMC10176061/supplementaryFiles")
OUTDIR = "irw_output"

SCALES = {
    "vocabulary_beliefs":   ([f"Q{i}" for i in range(1, 11)],  10),
    "vocabulary_strategies": ([f"Q{i}" for i in range(11, 63)], 52),
}


def _load() -> pd.DataFrame:
    z = zipfile.ZipFile(io.BytesIO(requests.get(SUPP, timeout=300).content))
    name = [n for n in z.namelist() if n.endswith("mmc1.xlsx")]
    assert len(name) == 1, z.namelist()
    return pd.read_excel(io.BytesIO(z.read(name[0])), header=2)


def main():
    d = _load().rename(columns={"Unnamed: 0": "id",
                                "Unnamed: 2": "cov_gender"})
    assert d["id"].is_unique, "Student ID is not unique"

    os.makedirs(OUTDIR, exist_ok=True)
    for suffix, (items, n_expected) in SCALES.items():
        missing = [c for c in items if c not in d.columns]
        assert not missing, (suffix, missing)
        assert len(items) == n_expected

        long = d.melt(id_vars=["id", "cov_gender"], value_vars=items,
                      var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"])
        long["resp"] = long["resp"].astype(int)
        long["id"] = long["id"].astype(int)
        long = long[["id", "item", "resp", "cov_gender"]]

        assert long["resp"].between(1, 7).all(), (
            suffix, long["resp"].min(), long["resp"].max())
        assert long.groupby("item")["resp"].nunique().min() > 1
        assert not long.duplicated(["id", "item"]).any()

        path = os.path.join(OUTDIR, f"trang_2023_{suffix}.csv")
        long.to_csv(path, index=False)
        n_id, n_it = long["id"].nunique(), long["item"].nunique()
        print(f"{path}: {n_id} ids x {n_it} items = {len(long)} responses, "
              f"resp {long['resp'].min()}-{long['resp'].max()}, "
              f"density {len(long)/(n_id*n_it):.3f}")


if __name__ == "__main__":
    main()
