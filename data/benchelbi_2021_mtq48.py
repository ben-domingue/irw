"""Mental Toughness Questionnaire (MTQ48), Arabic version, Tunisian sample.

Source: Zenodo 10.5281/zenodo.6073642, CC BY 4.0, "Validation of the Arabic
version of the mental toughness questionnaire". Single file `MTQ48 p853.sav`,
853 respondents x 59 columns; 48 MTQ48 items on a 1-5 scale.

The deposit's creator field is literally `XXXXXXXX` with affiliation
`XXXXXX` -- anonymised, presumably for blind review. The authors come from the
companion paper the record itself cites (10.5281/zenodo.5390587, "Validation
psychometrique de la version arabe de la mesure de la force mentale", Ben
Chelbi, Alem, Boudhiba, Hamrouni & Gaied Chortane, 2021), whose sample matches
this deposit's description exactly (853 Tunisian participants, 444 male / 409
female, 409 athletes / 444 non-athletes, aged 14-27).

Seven computed columns are dropped: the six MTQ48 component scores (CHALLENGE,
COMMITTMENT, EMOTIONALCONTRO, LIFECONTROL, CONFIDENCEINABILITIES,
INTERPERSONALCONFIDENCE) and GlobalscoreMTQ. The deposit's own description
names these as the instrument's "six components ... and the global score", so
they are sums over the items rather than items.
"""
import os
import re

import pandas as pd
import pyreadstat
import requests

RECORD = 6073642
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")
TABLE = "benchelbi_2021_mtq48"

COVARIATES = {"Age": "cov_age", "Gender": "cov_gender",
              "Athleteounonathlete": "cov_athlete"}
COMPOSITES = ["CHALLENGE", "COMMITTMENT", "EMOTIONALCONTRO", "LIFECONTROL",
              "CONFIDENCEINABILITIES", "INTERPERSONALCONFIDENCE",
              "GlobalscoreMTQ"]


def fetch_raw(path=None):
    if path and os.path.exists(path):
        return path
    rec = requests.get(f"https://zenodo.org/api/records/{RECORD}",
                       timeout=120).json()
    f = next(x for x in rec["files"] if x["key"].lower().endswith(".sav"))
    r = requests.get(f["links"]["self"], timeout=600)
    r.raise_for_status()
    local = os.path.join("/tmp", f["key"])
    with open(local, "wb") as fh:
        fh.write(r.content)
    return local


def main(path=None):
    src = fetch_raw(path)
    try:
        df, _meta = pyreadstat.read_sav(src, apply_value_formats=False)
    except Exception:
        df, _meta = pyreadstat.read_sav(src, apply_value_formats=False,
                                        encoding="latin1")

    items = [c for c in df.columns if re.match(r"^Q\d+$", str(c))]
    assert len(items) == 48, f"expected 48 MTQ48 items, found {len(items)}"

    accounted = set(items) | set(COVARIATES) | set(COMPOSITES) | {"Paticipants"}
    unaccounted = [c for c in df.columns if c not in accounted]
    assert not unaccounted, f"unaccounted source columns: {unaccounted}"

    df = df.rename(columns=COVARIATES)
    covs = list(COVARIATES.values())
    # 'Paticipants' is the deposit's own (misspelled) participant number.
    df["id"] = df["Paticipants"].astype(int)
    assert df["id"].is_unique, "Paticipants is not one row per respondent"

    long = (df.melt(id_vars=["id"] + covs, value_vars=items,
                    var_name="item", value_name="resp")
              .dropna(subset=["resp"]))
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + covs]

    assert long["id"].nunique() >= 100
    assert long["item"].nunique() == 48
    assert long["resp"].between(1, 5).all(), "MTQ48 is a 1-5 scale"

    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, f"{TABLE}.csv"), index=False)
    print(f"{TABLE}: {len(long):,} rows, {long['id'].nunique():,} ids, "
          f"{long['item'].nunique()} items")


if __name__ == "__main__":
    main()
