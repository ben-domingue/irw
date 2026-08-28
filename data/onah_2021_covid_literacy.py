"""Health information literacy of Nigerians on COVID-19 preventive measures.

Source: Onah, Momohjimoh & Okonkwo (2021), Mendeley Data 10.17632/cf3s3v8wb3,
CC BY 4.0. Single file `SPSS-DATA-COVID-19.sav`, 7,890 respondents x 38 columns.

Two instruments ship as separate tables:

  onah_2021_covid_knowledge      25 true/false knowledge items, scored 1/0
  onah_2021_covid_info_sources   10 binary "do you use this source" items

The knowledge items need per-item recoding, not a blanket 1/0 map. SPSS codes
them 1/2, but the *polarity is not constant*: COVID_11, 12, 15, 21, 22 and 23
label 1='incorrect' and 2='correct', while the other 19 label 1='correct'.
Scoring the raw codes would silently invert six of the 25 items. The value
labels are the authority here, so the recode reads them rather than assuming.

The deposit has no respondent identifier, so `id` is the row index. There is
one row per respondent (7,890 rows, 7,890 questionnaires reported in the
source), so the row is the person.
"""
import os

import pandas as pd
import pyreadstat
import requests

DOI = "10.17632/cf3s3v8wb3"
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")

KNOWLEDGE = [f"COVID_{i}" for i in range(1, 26)]
SOURCES = ["WHO_website", "NCDC_website", "social_media", "Television",
           "Radio", "Newspapers", "UNICEF_website", "From_friends_and_family",
           "From_health_worker", "From_church_or_mosque"]
COVARIATES = {"Gender": "cov_gender",
              "Educational_Level": "cov_education",
              "Location": "cov_location"}


def fetch_raw(path=None):
    """Read the .sav, downloading from Mendeley unless a local copy is given.

    Uses `/public-api/datasets/{key}` (the endpoint the IRW pipeline's own
    resolver uses), which returns the *latest* version's files. Selecting by
    extension rather than by filename is deliberate: this deposit renamed its
    .sav between versions, so a pinned name breaks on the next revision.
    """
    if path and os.path.exists(path):
        return path
    key = DOI.split("/")[-1]
    data = requests.get(f"https://data.mendeley.com/public-api/datasets/{key}",
                        timeout=120).json()
    sav = [f for f in data.get("files", [])
           if f.get("filename", "").lower().endswith(".sav")]
    assert len(sav) == 1, f"expected one .sav, found {[f['filename'] for f in sav]}"
    url = sav[0]["content_details"]["download_url"]
    r = requests.get(url, timeout=600)
    r.raise_for_status()
    local = os.path.join("/tmp", sav[0]["filename"])
    with open(local, "wb") as fh:
        fh.write(r.content)
    return local


def correct_code(col, meta):
    """Which raw code means 'correct' for this item, per its value labels."""
    label_set = meta.variable_to_label.get(col)
    labels = meta.value_labels.get(label_set, {}) if label_set else {}
    for code, text in labels.items():
        # The deposit contains the typo 'icorrect' for COVID_11; matching on
        # 'correct' alone would catch it, so test for the negation first.
        if "incorrect" in str(text).lower() or "icorrect" in str(text).lower():
            continue
        if "correct" in str(text).lower():
            return code
    raise ValueError(f"{col}: no 'correct' level in {labels}")


def to_long(wide, items, covs):
    out = wide.melt(id_vars=["id"] + list(covs), value_vars=items,
                    var_name="item", value_name="resp")
    out = out.dropna(subset=["resp"])
    out["resp"] = out["resp"].astype(int)
    return out[["id", "item", "resp"] + list(covs)]


def main(path=None):
    df, meta = pyreadstat.read_sav(fetch_raw(path), apply_value_formats=False)
    df = df.reset_index(drop=True)
    df["id"] = df.index + 1
    df = df.rename(columns=COVARIATES)
    covs = list(COVARIATES.values())

    # Knowledge: 1 = correct, 0 = incorrect, resolved per item.
    know = df[["id"] + covs + KNOWLEDGE].copy()
    for c in KNOWLEDGE:
        know[c] = (know[c] == correct_code(c, meta)).astype(int)
    know_long = to_long(know, KNOWLEDGE, covs)

    # Sources: SPSS codes 1='agree', 2='disagree'; ship as 1/0 endorsement so
    # the direction is the conventional one rather than reversed.
    src = df[["id"] + covs + SOURCES].copy()
    for c in SOURCES:
        src[c] = (src[c] == 1).astype(int)
    src_long = to_long(src, SOURCES, covs)

    os.makedirs(OUT_DIR, exist_ok=True)
    for name, frame in [("onah_2021_covid_knowledge", know_long),
                        ("onah_2021_covid_info_sources", src_long)]:
        assert frame["id"].nunique() >= 100, name
        assert frame["item"].nunique() > 1, name
        assert set(frame["resp"].unique()) <= {0, 1}, name
        frame.to_csv(os.path.join(OUT_DIR, f"{name}.csv"), index=False)
        print(f"{name}: {len(frame):,} rows, "
              f"{frame['id'].nunique():,} ids, {frame['item'].nunique()} items")


if __name__ == "__main__":
    main()
