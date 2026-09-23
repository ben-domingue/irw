#!/usr/bin/env python3
"""Bailon et al. (2020), CoVidAffect -- momentary valence and arousal ratings
during the COVID-19 lockdown in Spain, via the openESM harmonised copy.

Source: https://zenodo.org/records/22763396 (openESM 0018_bailon)
DOI: 10.5281/zenodo.22763396
Original deposit: 10.5281/zenodo.3774526 (CC BY 4.0)
Paper: Bailon C, Goicoechea C, Banos O, et al. (2020). CoVidAffect, real-time
    monitoring of mood variations following the COVID-19 outbreak in Spain.
    Scientific Data 7, 365. doi:10.1038/s41597-020-00700-1
Data: 0018_bailon_ts.tsv
License: CC BY 4.0 (openESM copy and original deposit)
Item text: shipped. Spanish wording from 0018_bailon_codebook.pdf; English is
    the authors' own (paper Fig. 3 and Table 3), translation_source=study_supplied.

Adapted from the script in irw#2367 (Korsepati).

999 people, 17,452 mood reports, two visual analogue sliders per report:
valence (-50 "Muy mal" .. +50 "Muy bien", a modified Feeling Scale) and arousal
(0 "Nada activado" .. 100 "Muy activado", a modified Felt Arousal Scale).

Coding notes
------------
* `wave` is each person's report number in time order (sorted on
  timestamp_answer, ties on timestamp_issued). The file is NOT in time order
  within a person -- it lists a person's App reports and then their Web reports
  further down -- so numbering by row puts 4,299 of 17,452 reports on the
  wrong wave.
* `date` is timestamp_answer as Unix seconds. The source timestamps are UTC
  (trailing Z); they are parsed as UTC, so the value does not depend on the
  machine running this script.
* No `rt`. timestamp_answer - timestamp_issued is the delay between the app's
  notification and the person opening it, not the time taken to respond, and
  for Web reports the two timestamps are identical by construction (paper,
  data records section).
* One exact duplicate report (id 1073, 2020-05-22T21:10:34Z, Web, every column
  identical) is dropped, so (id, item, wave) is a key.
* 8 reports have valence but no arousal; those arousal rows are absent.

Columns not shipped
-------------------
input_method  App (prompted, six pseudo-random times a day) vs Web
              (self-initiated, up to six a day). Varies within person, so it
              cannot be a cov_; recoverable from the source by (id, date).
day, beep     day is study day, derivable from date; beep is empty throughout.
*_slider_initial  randomised starting position of each slider -- design
              metadata, not a response.
"""

import csv
import os
import sys

import pandas as pd
import requests

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "automated_finding"))
from irw_triage_updated import run_qc          # noqa: E402

REC = "22763396"
FILENAME = "0018_bailon_ts.tsv"
TABLE = "bailon_2020_covidaffect"
AF = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                  "automated_finding")
OUTDIR = os.path.join(AF, "irw_output")
ITEMDIR = os.path.join(AF, "itemtext_output")
HEADERS = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

INSTRUMENT = ("CoVidAffect mood assessment questionnaire (Bailon et al. 2020): "
              "two visual analogue scales, valence and arousal")
# item -> (Spanish stem, English stem, resp range, (lo anchor), (hi anchor));
# anchors are (Spanish, English). Spanish from the codebook, English from the
# paper; the endpoints alone are labelled.
ITEMS = {
    "valence": ("¿Cómo te sientes ahora mismo?",
                "How do you feel right now?",
                range(-50, 51), ("Muy mal", "Very bad"),
                ("Muy bien", "Very good")),
    "arousal": ("¿Cómo de activado sientes tu cuerpo ahora mismo?",
                "How physically active do you feel right now?",
                range(0, 101), ("Nada activado", "Not active"),
                ("Muy activado", "Very active")),
}


def load():
    path = os.path.join("/tmp", f"zenodo_{REC}_{FILENAME}")
    if not os.path.exists(path):
        api = requests.get(f"https://zenodo.org/api/records/{REC}",
                           headers=HEADERS, timeout=60).json()
        url = next(f["links"]["self"] for f in api["files"]
                   if f["key"] == FILENAME)
        r = requests.get(url, headers=HEADERS, timeout=600)
        r.raise_for_status()
        with open(path, "wb") as fh:
            fh.write(r.content)
    return pd.read_csv(path, sep="\t")


def write_items():
    rows = []
    for item, (stem, stem_en, scale, lo, hi) in ITEMS.items():
        for v in scale:
            opt = lo if v == scale[0] else hi if v == scale[-1] else ("", "")
            rows.append([TABLE, f"{TABLE}_1", item, INSTRUMENT, "Spanish",
                         "", "", "", "", stem, stem_en, "",
                         opt[0], opt[1], v])
    path = os.path.join(ITEMDIR, f"{TABLE}__items.csv")
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, quoting=csv.QUOTE_ALL, lineterminator="\n")
        w.writerow(["table", "section_id", "item", "instrument", "language",
                    "instructions", "instructions_translated",
                    "section_prompt", "section_prompt_translated",
                    "item_text", "item_text_translated", "correct_response",
                    "option_text", "option_text_translated", "resp"])
        w.writerows(rows)
    return path, len(rows)


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    os.makedirs(ITEMDIR, exist_ok=True)
    df = load()
    assert len(df) == 17452 and df["id"].nunique() == 999, df.shape

    n = len(df)
    df = df.drop_duplicates()
    assert n - len(df) == 1, n - len(df)

    for c in ("timestamp_issued", "timestamp_answer"):
        df[c] = pd.to_datetime(df[c], utc=True)
    assert df["timestamp_answer"].notna().all()
    df = df.sort_values(["id", "timestamp_answer", "timestamp_issued"],
                        kind="stable")
    df["wave"] = df.groupby("id").cumcount() + 1
    epoch = pd.Timestamp("1970-01-01", tz="UTC")
    df["date"] = (df["timestamp_answer"] - epoch) // pd.Timedelta(seconds=1)
    # study ran 2020-03-28 .. 2020-06-21 (UTC)
    assert df["date"].between(1585267200, 1592784000).all()

    long = df.melt(id_vars=["id", "wave", "date"], value_vars=list(ITEMS),
                   var_name="item", value_name="resp")
    long = long.dropna(subset=["resp"])
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp", "wave", "date"]]
    long = long.sort_values(["id", "wave", "item"]).reset_index(drop=True)

    for item, (_, _, scale, _, _) in ITEMS.items():
        r = long.loc[long["item"] == item, "resp"]
        assert r.between(scale[0], scale[-1]).all(), item
    assert not long.duplicated(["id", "item", "wave"]).any()
    # wave must follow time within person
    assert (long.groupby("id")["date"].diff().dropna() >= 0).all()
    bad = [c for c in run_qc(long) if c.status == "fail"]
    assert not bad, [(c.name, c.detail) for c in bad]

    path = os.path.join(OUTDIR, f"{TABLE}.csv")
    long.to_csv(path, index=False)
    print(f"{path}: {long['id'].nunique()} people x {long['item'].nunique()} "
          f"items = {len(long):,} responses, max wave {long['wave'].max()}")
    ipath, k = write_items()
    print(f"{ipath}: {k} item text rows")


if __name__ == "__main__":
    main()
