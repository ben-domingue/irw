#!/usr/bin/env python3
##Sweetpotato trait rankings by value-chain actors in Uganda -> one IRW rankings table.
##Source: Ojwang, S. O. (2025). "Sweetpotato Trait Preferences in Uganda: A Value Chain-Wide Survey
##Dataset (2020)", Zenodo doi:10.5281/zenodo.14831654, CC BY 4.0 (version record 14831654; the
##concept DOI is .14831653). The deposit names
##https://doi.org/10.3389/fpls.2022.808597 as the paper the data are a source of.
##File read: AbacusBio_Sweetpotato_Valuechain_Wide_Trait_Preference_Survey_Data_Uganda(2020)_07feb2025.dta
##(1,333 respondents x 266 columns; survey fielded February 2020 in Mpigi and Masaka, Central Uganda).
##
##Each respondent ranked SIXTEEN sweetpotato traits. The item text is the Stata VARIABLE LABEL of each
##`rank_*` column with its "Rank_" prefix removed ("Vine survival under stressful conditions",
##"Resistance to weevil", the three flesh colours, ...), and the covariate text is the file's own
##value labels.
##
##TIES ARE STORED AS AVERAGED MID-RANKS, which is not a position, so they are decoded here. Items
##that share a value are one tie group; a group of k items at mid-rank mu occupies positions
##mu-(k-1)/2 .. mu+(k-1)/2, and under this family's tie convention every item of the group takes the
##group's LOWEST position (README, "One position, one row, except ties"). The decode is exact and
##reversible -- the tie structure regenerates the source's mid-ranks -- and it was verified before
##building: 1,327 of the 1,333 rows reproduce the positions 1..16 with no gap and no overlap.
##The remaining 6 rows are internally inconsistent in the source (one, for example, has three items
##at 8 alongside a 9.5, which cannot tile) and are dropped; the count is in the design record and the
##rows are listed in issue #3179. Ties are common: 1,977 groups, sizes 2 to 9.
##
##Covariates keep the deposit's own labels: cov_actor (the value-chain role: root producer, vine
##multiplier, trader, processor, consumer), cov_district, cov_ethnicity, cov_sex, cov_age,
##cov_marital_status, cov_education_years, cov_household_size and cov_country. `Country` labels 32 of
##the 1,333 rows Kenya although the deposit describes a Ugandan survey and those rows carry Ugandan
##districts; that is the source's inconsistency and is kept as recorded, not corrected.
##Dropped: Longitude and Latitude (GPS, ~10 distinct values each), `sessionvariable` and `start_time`
##(session keys), and the deposit's own ResponseID (ids are re-keyed 1..n in file order).
##
##Usage: python3 ojwang_2020_sweetpotato_traits.py build <raw dir> <out dir>
##Table: ojwang_2020_sweetpotato_traits.
from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path

import pandas as pd

from rank_common import design_counts, fetch, upsert_design, write_table

TABLE = "ojwang_2020_sweetpotato_traits"
COLLECTION = "10.5281/zenodo.14831654"
FILENAME = ("AbacusBio_Sweetpotato_Valuechain_Wide_Trait_Preference_Survey_Data_Uganda(2020)"
            "_07feb2025.dta")
URL = ("https://zenodo.org/api/records/14831654/files/"
       "AbacusBio_Sweetpotato_Valuechain_Wide_Trait_Preference_Survey_Data_Uganda%282020%29"
       "_07feb2025.dta/content")
COVS = {"actor": "cov_actor", "district": "cov_district", "ethnicity": "cov_ethnicity",
        "sex": "cov_sex", "age": "cov_age", "marital": "cov_marital_status",
        "edu_years": "cov_education_years", "hhsize": "cov_household_size",
        "Country": "cov_country"}


def positions(values: dict[str, float]) -> dict[str, int] | None:
    """Mid-ranks -> positions. Each tie group takes its lowest position; None if the row does not tile."""
    out, used = {}, []
    for v in sorted(set(values.values())):
        group = [k for k, x in values.items() if x == v]
        start = Fraction(v).limit_denominator(2) - Fraction(len(group) - 1, 2)
        if start.denominator != 1:
            return None
        lo = int(start)
        used.extend(range(lo, lo + len(group)))
        for k in group:
            out[k] = lo
    if sorted(used) != list(range(1, len(values) + 1)):
        return None
    return out


def build(raw_dir: Path, out_dir: Path) -> None:
    src = fetch(URL, raw_dir / FILENAME)
    reader = pd.io.stata.StataReader(src)
    labels = reader.variable_labels()
    d = pd.read_stata(src, convert_categoricals=True)
    items = [c for c in d.columns if c.startswith("rank_") and c != "PrefTimemmss"]
    text = {c: labels[c].split("_", 1)[1].strip() if "_" in labels[c] else labels[c].strip()
            for c in items}
    assert len(items) == 16 and len(set(text.values())) == 16, text
    raw = pd.read_stata(src, convert_categoricals=False)[items]
    rows, dropped, tied, ties = [], [], 0, 0
    for i, (_, r) in enumerate(raw.iterrows(), start=1):
        vals = {c: float(r[c]) for c in items if pd.notna(r[c])}
        pos = positions(vals) if len(vals) == len(items) else None
        if pos is None:
            dropped.append(i)
            continue
        groups = {}
        for c, p in pos.items():
            groups[p] = groups.get(p, 0) + 1
        ties += sum(1 for n in groups.values() if n > 1)
        tied += any(n > 1 for n in groups.values())
        cov = {v: (None if pd.isna(d.iloc[i - 1][k]) else str(d.iloc[i - 1][k])) for k, v in COVS.items()}
        for c, p in pos.items():
            rows.append({"id": i, "task": 1, "item": text[c], "resp": p, **cov})
    ##ids are re-keyed after the drops so they run 1..n with no gaps
    remap = {old: new for new, old in enumerate(dict.fromkeys(r["id"] for r in rows), start=1)}
    for r in rows:
        r["id"] = remap[r["id"]]
    write_table(out_dir / f"{TABLE}.csv", rows)
    counts = design_counts(rows)
    upsert_design({
        "table": TABLE, "source_file": FILENAME, "collection": COLLECTION,
        "jurisdiction": "Mpigi and Masaka districts, Central Uganda (sweetpotato value-chain survey)",
        "date": "2020-02-01",
        "office": ("sixteen sweetpotato traits ranked by importance, 1 = most important, by farmers, "
                   "vine multipliers, traders, processors and consumers"),
        "method": "survey", "seats": "na", **counts,
        "n_ballots_cast": len(raw), "n_ballots_eligible_est": len(raw),
        "write_in_allowed": "no", "candidate_order": "unknown",
        "evidence": (f"Zenodo {COLLECTION} file {FILENAME}, CC BY 4.0; item text from the Stata variable "
                     f"labels, covariate text from the file's value labels; fielded February 2020 "
                     f"(deposit description), day unknown; seats na (a survey); the source stores ties as "
                     f"averaged mid-ranks and they are decoded to the tie group's lowest position (exact "
                     f"and reversible; verified on 1,327 of 1,333 rows); {len(dropped)} rows dropped as "
                     f"internally inconsistent (listed in issue #3179): {dropped}; n_tied_ballots {tied} "
                     f"with {ties} tie groups; candidate_order unknown; counts computed by "
                     f"{TABLE}.py"),
    })
    print(f"{TABLE}: {len(rows)} rows, {counts['n_ballots_with_marks']} respondents, "
          f"{counts['n_candidates']} traits, {len(dropped)} rows dropped, {tied} tied respondents")


def main(argv: list[str]) -> int:
    if len(argv) < 4 or argv[1] != "build":
        print("usage: ojwang_2020_sweetpotato_traits.py build <raw dir> <out dir>")
        return 2
    build(Path(argv[2]), Path(argv[3]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
