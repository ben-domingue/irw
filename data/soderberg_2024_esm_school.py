"""Soderberg & Molsa (2024), Zenodo -- 10-day experience sampling study of
Finnish middle- and upper-secondary school students, 2022.

Source: https://zenodo.org/records/13332148
DOI: 10.5281/zenodo.13332148
Data: ESM_repository_2022.sav
License: CC BY 4.0
Item text: shipped (SPSS variable + value labels give every stem and all five
    anchors verbatim)

300 students, a one-off start-up survey plus up to 40 momentary assessments
each (8,260 occasions). Every scale is on the same labelled 1-5 format,
"No, not at all" .. "Yes, absolutely".

Tables written
--------------
soderberg_2024_peer_support             300 x 6 items    (PSS)
soderberg_2024_teacher_support          300 x 9 items    (TSR)
soderberg_2024_family_support           300 x 4 items    (FSL)
soderberg_2024_general_selfefficacy     300 x 5 items    (SGSE)
soderberg_2024_academic_selfefficacy    300 x 4 items    (SEQC)
soderberg_2024_esm_affect               300 x 8 items x wave
soderberg_2024_esm_lecture              300 x 6 items x wave
soderberg_2024_esm_morning              300 x 2 items x wave

Coding notes
------------
* The .sav is one row per momentary assessment, so the start-up survey answers
  are repeated down every row of a person. Verified constant within `ID4` (max
  1 distinct value per person for all 32 start-up variables) and de-duplicated
  to one row per student for the five start-up tables.
* `wave` for the ESM tables is the deposit's own `Time` = (Day-1)*8+(Session+2),
  the study's numeric occasion order. `(ID4, Time)` is unique -- 0 duplicate
  keys -- so `(id, item, wave)` is a real key.
* Blocks are split by construct, not by shared response format: all eight
  tables use the same 1-5 anchors, which is a format, not an instrument.
* `Le_enjoy_all` is observed only at 1-4 across 4,107 responses. The SPSS value
  label set declares all five anchors for it exactly as for its five block
  mates, so this is one left-skewed 1-5 scale, not a separate 1-4 one --
  `run_qc`'s `resp_scale_mixed` reads an observed maximum as a scale, so the
  check is waived for this table by named exemption (printed at write time).
* Dropped as items, each being the only item of its construct (IRW does not
  ship single-item scales): `SchoolEnj` and `SchoolAbs` -- carried instead as
  person-level covariates on the start-up tables -- plus the ESM items
  `PeerRel_all` (end-of-day classmate item, its own stem) and
  `SchooldaySatisfaction` (1-10, a different format from everything else).
* `Morning_breakfast` is a yes/no eaten-breakfast item on a different format
  from its two 1-5 block mates and is not a self-report rating; dropped rather
  than mixed into the morning table.
* `SessionInstanceResponseLapse` and `SessionLength` are app timing fields for
  the whole assessment, not per-item response times, so they are not `rt`
  (see memory feedback_rt_column_scope). Occasion-level rather than
  person-level, so they are not shipped as `cov_*` either.
* Covariates: `cov_gender` (1=Girl 2=Boy), `cov_edulevel` (1=middle secondary,
  2=upper secondary), and on the start-up tables `cov_school_enjoyment` (1-5)
  and `cov_school_absence` (1=No, 2=Yes once, 3=Yes several times).
"""

import csv
import os
import sys

import pandas as pd
import pyreadstat
import requests

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "automated_finding"))
from irw_triage_updated import run_qc          # noqa: E402

REC = "13332148"
FILENAME = "ESM_repository_2022.sav"
AF = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                  "automated_finding")
OUTDIR = os.path.join(AF, "irw_output")
ITEMDIR = os.path.join(AF, "itemtext_output")
INSTRUMENT = ("Soderberg & Molsa (2024) school experience sampling study -- "
              "start-up survey and momentary assessments")

# construct -> (table suffix, item columns, human-readable instrument name)
STARTUP = [
    ("peer_support", [f"PSS{i}" for i in range(1, 7)],
     "Perceived peer support at school (start-up survey)"),
    ("teacher_support", [f"TSR{i}" for i in range(1, 10)],
     "Perceived teacher and school support (start-up survey)"),
    ("family_support", [f"FSL{i}" for i in range(1, 5)],
     "Perceived family support for school (start-up survey)"),
    ("general_selfefficacy", [f"SGSE{i}" for i in range(1, 6)],
     "Short General Self-Efficacy scale (start-up survey)"),
    ("academic_selfefficacy", [f"SEQC{i}" for i in range(1, 5)],
     "Academic self-efficacy (start-up survey)"),
]
ESM = [
    ("esm_affect", ["Enjoy_all", "Stress_all", "Motivated_all", "Angry_all",
                    "Liked_all", "Lonely_all", "Alert_all", "Hostile_all"],
     "Momentary affect and school experience (experience sampling)"),
    ("esm_lecture", ["Le_enjoy_all", "Le_diff_all", "Le_intr_all",
                     "Te_str_all", "Te_fair_all", "Te_enc_all"],
     "Most recent lecture and teacher (experience sampling)"),
    ("esm_morning", ["Morning_sleep", "Morning_ok"],
     "Morning check-in (experience sampling)"),
]
STARTUP_COVS = {"Gender": "cov_gender", "EduLevel": "cov_edulevel",
                "SchoolEnj": "cov_school_enjoyment",
                "SchoolAbs": "cov_school_absence"}
ESM_COVS = {"Gender": "cov_gender", "EduLevel": "cov_edulevel"}
# columns deliberately not shipped as items, with the reason printed at run time
DROPPED = {
    "STARTUP": "SPSS section-header variable, no data",
    "ESM": "SPSS section-header variable, no data",
    "NotificationTime": "app metadata",
    "NotificationNo": "app metadata",
    "Reminder": "app metadata",
    "SessionInstanceResponseLapse": "whole-session timing, not per-item rt",
    "SessionLength": "whole-session timing, not per-item rt",
    "Session": "occasion label, folded into wave via Time",
    "Day": "occasion label, folded into wave via Time",
    "SchoolEnj": "single-item construct -> cov_school_enjoyment",
    "SchoolAbs": "single-item construct -> cov_school_absence",
    "PeerRel_all": "single-item construct, own stem",
    "SchooldaySatisfaction": "single item on a 1-10 format",
    "Morning_breakfast": "yes/no behaviour item, different format from block",
}
# resp_scale_mixed exemptions: table -> reason
QC_WAIVERS = {
    "soderberg_2024_esm_lecture":
        "Le_enjoy_all is observed only at 1-4; its SPSS value-label set "
        "declares the same five anchors as the rest of the block.",
}


def load():
    path = os.path.join("/tmp", f"zenodo_{REC}_{FILENAME}")
    if not os.path.exists(path):
        api = requests.get(f"https://zenodo.org/api/records/{REC}",
                           timeout=60).json()
        url = next(f["links"]["self"] for f in api["files"]
                   if f["key"] == FILENAME)
        with requests.get(url, stream=True, timeout=600) as r:
            r.raise_for_status()
            with open(path, "wb") as fh:
                for chunk in r.iter_content(1 << 20):
                    fh.write(chunk)
    return pyreadstat.read_sav(path)


def melt(d, cols, covs, wave=False):
    keep = ["id"] + (["wave"] if wave else []) + cols + list(covs)
    long = d[keep].melt(id_vars=["id"] + (["wave"] if wave else [])
                        + list(covs), value_vars=cols,
                        var_name="item", value_name="resp")
    long = long.dropna(subset=["resp"])
    long["resp"] = long["resp"].astype(int)
    long = long.rename(columns=covs)
    order = (["id", "item", "resp"] + (["wave"] if wave else [])
             + list(covs.values()))
    return long[order]


def write_items(name, cols, labels, value_labels, instrument):
    """Item text from the .sav's own variable and value labels."""
    rows = []
    for col in cols:
        stem = labels[col]
        # variable labels are "<shared stem>: <item>" for the blocks that had
        # one; keep the item half as item_text and do not invent instructions
        text = stem.split(": ", 1)[1] if ": " in stem else stem
        for val, opt in sorted(value_labels[col].items()):
            rows.append({"table": name, "section_id": f"{name}_1",
                         "item": col, "instrument": instrument,
                         "instructions": "", "section_prompt": "",
                         "item_text": text, "correct_response": "",
                         "option_text": opt, "resp": int(val)})
    path = os.path.join(ITEMDIR, f"{name}__items.csv")
    assert not os.path.exists(path), name
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh, quoting=csv.QUOTE_ALL, lineterminator="\n")
        w.writerow(["table", "section_id", "item", "instrument",
                    "instructions", "section_prompt", "item_text",
                    "correct_response", "option_text", "resp"])
        for r in rows:
            w.writerow([r["table"], r["section_id"], r["item"],
                        r["instrument"], r["instructions"],
                        r["section_prompt"], r["item_text"],
                        r["correct_response"], r["option_text"], r["resp"]])
    return len(rows)


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    os.makedirs(ITEMDIR, exist_ok=True)
    df, meta = load()
    labels = meta.column_names_to_labels
    vls = meta.variable_value_labels

    d = df.rename(columns={"ID4": "id", "Time": "wave"})
    person = d.drop_duplicates("id")
    assert len(person) == 300, len(person)
    for col in [c for grp in STARTUP for c in grp[1]] + list(STARTUP_COVS):
        assert d.groupby("id")[col].nunique(dropna=True).max() <= 1, col
    assert not d.duplicated(["id", "wave"]).any()

    shipped, total, itemtext_total = set(), 0, 0
    for group, src, covs, wave in [(STARTUP, person, STARTUP_COVS, False),
                                   (ESM, d, ESM_COVS, True)]:
        for suffix, cols, instrument in group:
            name = f"soderberg_2024_{suffix}"
            long = melt(src, cols, covs, wave=wave)
            shipped.update(cols)

            assert long["resp"].between(1, 5).all()
            key = ["id", "item"] + (["wave"] if wave else [])
            assert not long.duplicated(key).any(), name
            assert long["id"].nunique() >= 100, name
            assert long["item"].nunique() >= 2, name
            checks = run_qc(long)
            bad = [c for c in checks if c.status == "fail"]
            if name in QC_WAIVERS:
                waived = [c for c in bad if c.name == "resp_scale_mixed"]
                if waived:
                    print(f"  [qc waiver] {name}: {QC_WAIVERS[name]}")
                bad = [c for c in bad if c.name != "resp_scale_mixed"]
            assert not bad, (name, [(c.name, c.detail) for c in bad])

            path = os.path.join(OUTDIR, f"{name}.csv")
            assert not os.path.exists(path), name
            long.to_csv(path, index=False)
            total += len(long)
            n_id, n_it = long["id"].nunique(), long["item"].nunique()
            print(f"{path}: {n_id} students x {n_it} items = {len(long)} "
                  f"responses" + (f", {long['wave'].nunique()} waves"
                                  if wave else ""))
            itemtext_total += write_items(name, cols, labels, vls, instrument)

    for c in df.columns:
        if c in ("ID4", "Time"):
            continue
        assert (c in shipped or c in DROPPED
                or c in STARTUP_COVS), f"unaccounted source column: {c}"
    for c, why in DROPPED.items():
        print(f"  [dropped] {c}: {why}")
    print(f"\n8 tables, {total:,} responses; "
          f"{itemtext_total} item text rows")


if __name__ == "__main__":
    main()
