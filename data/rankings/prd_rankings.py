#!/usr/bin/env python3
##Survey ranking questions from the Political Rankings Database (PRD) -> 12 IRW rankings tables.
##Source: Atsusaka, Y. and Singh, S. 2026. "Ranking Data in Political Science." Working paper;
##database at https://political-rankings.github.io (repo https://github.com/YukiAtsusaka/PRD,
##contact atsusaka@uh.edu). File read: the archived release zip
##https://github.com/political-rankings/political-rankings.github.io/releases/latest/download/political-rankings.zip
##(sha256 recorded in PRD_SHA256 below; 52 standardized CSVs, codebook v0.0.7 of 2026-09-23).
##The release is NOT the same as the repository's main branch, which is three months older and
##misspells two study names (krupnov/deitrich); every file differs. Build from the release only.
##
##PRD is a COMPILATION and carries no licence of its own, so each table is admitted on its
##originating study's own replication deposit, named per table in TABLES below: all twelve are
##CC0 1.0 on Harvard Dataverse (irw rankings README, "Intake rules"; originator rule). PRD is
##cited beside the study for the standardisation. The other 40 files in the release are not built:
##7 are deposits IRW already holds (DVN/AJXRCV, DVN/UCTXEF), 19 are treatment-arm subsets of a
##pooled file built here, 6 have originating deposits under custom Dataverse terms, 4 are
##marginal/indicator encodings (one item's position only -- a single pick, not an ordering),
##2 are under the 50-ranker floor, 1 (Lin-Greenberg 2023) carries respondent email addresses in
##the PRD file, and 1 (Egan 2014) has no replication deposit we could find.
##See oneoff/rankings-scouting-pass4-2026-10-22/ (README.md, prd_verdicts.csv) for the per-file calls.
##
##Layout: PRD's own schema is one row per respondent, one column per ranked item holding the
##position (1 = most preferred, NA = not ranked or not released), plus `ranking` (a compact
##summary string), `treat` (0-indexed arm) and study covariates. That maps onto the rankings
##standard with no inference: id = the row re-keyed 1..n in file order (PRD's `unit` is dropped),
##task = 1 (one ranking question per file), item = the item column, resp = the position as
##recorded, cov_* = `treat` and every other source column. `ranking` is dropped as a restatement
##of the item columns, as are two columns derived from the outcome (pradel `rank1`, krupnikov
##`health_rank1`). A respondent with no recorded position contributes no rows; the count is in
##the design record's evidence.
##
##Where only some items' positions survive in the released data the table says so: fielding_2018
##keeps only UKIP and the BNP of seven parties, and krupnikov_2019 only inequality and health
##care of six issues (the authors released no more). The NA there is "not released", not "the
##respondent stopped ranking", and that is the one thing a user of these two tables must know.
##
##Items that are people take candidate codes, as everywhere in this family (README,
##"Candidate codes"): boudreau_2019_police_blame and malhotra_2008_katrina_blame rank named
##officials, so the whole item set of each is coded c01.. by case-insensitive sort, including the
##two collective items in Boudreau ("officers", "senators") -- the same rule the Voter Autrement
##list labels took. Values, issues, parties, speech types, identity categories and the
##self/hindu/muslim roles in Haas & Lindstam are not people and keep the text PRD shows.
##
##Usage: python3 prd_rankings.py build <raw dir> <out dir> [<table> ...]   (default: every table)
from __future__ import annotations

import csv
import hashlib
import io
import sys
import zipfile
from pathlib import Path

from rank_common import code_candidates, design_counts, fetch, upsert_design, write_table

PRD_ZIP = ("https://github.com/political-rankings/political-rankings.github.io/releases/latest/"
           "download/political-rankings.zip")
PRD_SHA256 = "0961f935041fa9c228490e0d62facba0c9cf5037543d77bdea226c03136e7860"  # the release zip as fetched 2026-10-22
PRD_CITE = "Atsusaka & Singh 2026, Political Rankings Database (archived release, codebook v0.0.7)"

# table -> prd file, item columns (in PRD order), people?, drop, deposit, licence, study, task text
TABLES = {
    "bakker_2021_childrearing_values": dict(
        file="bakker-etal-2021.csv", items=["obey", "thnkself", "workhard", "helpoth", "popular"],
        people=False, drop=[], deposit="10.7910/DVN/WZI945", licence="CC0 1.0",
        study="Bakker, B. N., Lelkes, Y. & Malka, A. 2021. 'Reconsidering the Link Between Self-Reported "
              "Personality Traits and Political Preferences.' American Political Science Review 115(4)",
        task="GSS 2006 panel, Stenner child-rearing values: five qualities ranked 1 (most important) to 5; "
             "three waves stacked, one row per respondent x wave (cov_treat is the wave, cov_wave its label)",
        place="United States (GSS 2006 panel, three waves)", date="unknown"),
    "boudreau_2019_police_blame": dict(
        file="boudreau-etal-2019-police.csv",
        items=["clark", "officers", "hahn", "steinberg", "schubert", "brown", "senators"],
        people=True, drop=[], deposit="10.7910/DVN/V83FXD", licence="CC0 1.0",
        study="Boudreau, C., MacKenzie, S. A. & Simmons, D. J. 2019. 'Police Violence and Public Perceptions: "
              "An Experimental Study of How Information and Endorsements Affect Support for Law Enforcement.' "
              "The Journal of Politics 81(3)",
        task="full 1-7 ranking of the actors most to blame for the 2018 Stephon Clark shooting, in a "
             "three-arm information-framing experiment (cov_treat: 0 control, 1 pattern framing, 2 reform framing)",
        place="Sacramento, California (online survey experiment)", date="unknown"),
    "corstange_2022_syria_factions_2015": dict(
        file="corstange-2022-sy2015.csv",
        items=["freesyrianarmy", "syriangovernment", "syrianislamistgroups", "foreignislamistgroups",
               "kurdishgroups", "hizbalah"],
        people=False, drop=[], deposit="10.7910/DVN/S8LSKA", licence="CC0 1.0",
        study="Corstange, D. 2022. 'Mass Dissimulation in the Syrian Civil War.' The Journal of Politics 84(3); "
              "the deposit is titled 'Displacement and Dissimulation in the Syrian Civil War'",
        task="top-3 sympathy ranking of six civil-war factions, wave 1 (2015) of a survey of displaced Syrians; "
             "unranked factions are NA (cov_treat: 0 control, 1-3 framing arms)",
        place="Syrians in Lebanon (2015 wave)", date="2015-01-01"),
    "corstange_2022_syria_factions_2017": dict(
        file="corstange-2022-sy2017.csv",
        items=["freesyrianarmy", "syriangovernment", "syrianislamistgroups", "foreignislamistgroups",
               "kurdishgroups", "hizbalah"],
        people=False, drop=[], deposit="10.7910/DVN/S8LSKA", licence="CC0 1.0",
        study="Corstange, D. 2022. 'Mass Dissimulation in the Syrian Civil War.' The Journal of Politics 84(3); "
              "the deposit is titled 'Displacement and Dissimulation in the Syrian Civil War'",
        task="top-3 sympathy ranking of six civil-war factions, wave 2 (2017); questionnaire item numbering "
             "differs from the 2015 wave, so the cov_q* codes are not comparable across the two tables",
        place="Syrians in Lebanon (2017 wave)", date="2017-01-01"),
    "fielding_2018_party_ranking": dict(
        file="fielding-2018.csv",
        items=["conservative", "labour", "liberal_democrat", "green", "respect", "ukip", "bnp"],
        people=False, drop=[], deposit="10.7910/DVN/GCPZZB", licence="CC0 1.0",
        study="Fielding, D. 2018. 'Traditions of Tolerance: The Long-Run Persistence of Regional Variation in "
              "Attitudes towards English Immigrants.' British Journal of Political Science 48(1)",
        task="an imaginary alternative-vote ballot in the 2010 British Election Study, seven parties ranked. "
             "ONLY the UKIP and BNP positions are in the released extract; the other five parties are NA for "
             "every respondent because they were not released, not because the respondent stopped ranking. "
             "PRD converted the author's reverse-coded 0-6 ordinals to positions (rank = 7 - value, 0 -> NA)",
        place="Great Britain (British Election Study 2010)", date="2010-01-01"),
    "haas_2023_group_leader": dict(
        file="haas-lindstam-2023.csv", items=["self", "hindu", "muslim"],
        people=False, drop=[], deposit="10.7910/DVN/F8SRTA", licence="CC0 1.0",
        study="Haas, N. & Lindstam, E. 2023. 'My History or Our History? Historical Revisionism and Entitlement "
              "to Lead.' American Political Science Review 118(4)",
        task="full 1-3 ranking of the three members of a real-money group as ideal leader (self, another Hindu "
             "member, a Muslim member), Hindu respondents only (cov_treat: 0 neutral, 1 exclusive, 2 inclusive "
             "history). The raw file stores the two partners' reverse-coded demand scores and PRD derives the "
             "respondent's own position as the remaining rank; Muslim respondents' mirror task is not in PRD",
        place="India (lab-in-the-field group decision game)", date="unknown"),
    "jacoby_2014_political_values": dict(
        file="jacoby-2014.csv",
        items=["freedom", "equality", "economicsecurity", "morality", "individualism", "socialorder", "patriotism"],
        people=False, drop=[], deposit="10.7910/DVN/26564", licence="CC0 1.0",
        study="Jacoby, W. G. 2014. 'Is There a Culture War? Conflicting Value Structures in American Public "
              "Opinion.' American Political Science Review 108(4)",
        task="full 1-7 ranking of political values, produced by sequential elimination; observational, cov_treat 0",
        place="United States (online survey)", date="unknown"),
    "krupnikov_2019_issue_importance": dict(
        file="krupnikov-levine-2019.csv",
        items=["federaldebt", "unemployment", "ineq", "health", "immigration", "ethics"],
        people=False, drop=["health_rank1"], deposit="10.7910/DVN/EEMRS9", licence="CC0 1.0",
        study="Krupnikov, Y. & Levine, A. S. 2019. 'Political Issues, Evidence, and Citizen Engagement: The Case "
              "of Unequal Access to Affordable Health Care.' The Journal of Politics 81(2)",
        task="six policy issues ranked by importance in a five-arm evidence-format experiment, but ONLY the "
             "inequality and health-care positions are in the released data; the other four issues are NA for "
             "every respondent because they were not released (cov_treat: 0 control, 1 human-interest story, "
             "2 statistics as percentages, 3 statistics as counts, 4 counts with a denominator; 42 rows have no arm)",
        place="United States (online survey experiment)", date="unknown"),
    "malhotra_2008_katrina_blame": dict(
        file="malhotra-kuo-2008.csv",
        items=["blanco", "brown", "bush", "chertoff", "landrieu", "nagin", "vitter"],
        people=True, drop=[], deposit="10.7910/DVN/N7MFZW", licence="CC0 1.0",
        study="Malhotra, N. & Kuo, A. G. 2008. 'Attributing Blame: The Public's Response to Hurricane Katrina.' "
              "The Journal of Politics 70(1)",
        task="full 1-7 ranking of officials most to blame for Hurricane Katrina, in a four-arm cue experiment "
             "(cov_treat: 0 names only, 1 office cue, 2 party cue, 3 both)",
        place="United States (online survey experiment)", date="unknown"),
    "mcmurry_2022_identity_ranking": dict(
        file="mcmurry-2022.csv", items=["tribe", "nationality", "religion", "gender"],
        people=False, drop=[], deposit="10.7910/DVN/VW1GDD", licence="CC0 1.0",
        study="McMurry, N. 2022. 'From Recognition to Integration: Indigenous Autonomy, State Authority, and "
              "National Identity in the Philippines.' American Political Science Review 116(2)",
        task="full 1-4 ranking of identity categories (cov_treat: 0 control, 1 identity treatment, "
             "2 material treatment)",
        place="Philippines (survey experiment)", date="unknown"),
    "pradel_2024_speech_types": dict(
        file="pradel-etal-2024.csv", items=["civil", "uncivil", "intolerant", "threatening"],
        people=False, drop=["rank1"], deposit="10.7910/DVN/Y0YNMV", licence="CC0 1.0",
        study="Pradel, F., Zilinsky, J., Kosmidis, S. & Theocharis, Y. 2024. 'Toxic Speech and Limited Demand "
              "for Content Moderation on Social Media.' American Political Science Review 118(4)",
        task="full 1-4 ranking of four speech types in a five-arm experiment (cov_treat: 0 control, "
             "1 non-group-related control, 2 uncivil, 3 intolerant, 4 threatening; cov_treatment is the label)",
        place="United States (online survey experiment)", date="unknown"),
    "rathbun_2022_trait_ranking": dict(
        file="rathbun-pomeroy-2022.csv",
        items=["fair", "generous", "honest", "powerful", "friendly", "culture", "resolved", "organized",
               "intelligent"],
        people=False, drop=[], deposit="10.7910/DVN/RZ1JVJ", licence="CC0 1.0",
        study="Rathbun, B. C. & Pomeroy, C. 2022. 'See No Evil, Speak No Evil? Morality, Evolutionary "
              "Psychology, and the Nature of International Relations.' International Organization 76(3)",
        task="nine traits, of which respondents ranked at least two, so the NAs are by design (cov_treat is "
             "the rated group, 1 individuals / 2 countries, with no control arm -- it is not 0-indexed)",
        place="United States (online survey)", date="unknown"),
}

DROP_ALWAYS = ("unit", "ranking")


def cov_name(col: str) -> str:
    out = "".join(ch if ch.isalnum() else "_" for ch in col.strip().lower())
    while "__" in out:
        out = out.replace("__", "_")
    return "cov_" + out.strip("_")


def read_release(raw_dir: Path) -> dict[str, list[dict]]:
    """Read the PRD release zip once; return {filename: rows}. The zip is untrusted data."""
    dest = fetch(PRD_ZIP, raw_dir / "political-rankings.zip")
    blob = dest.read_bytes()
    digest = hashlib.sha256(blob).hexdigest()
    out = {}
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        for name in z.namelist():
            if name.endswith(".csv"):
                with z.open(name) as f:
                    text = io.TextIOWrapper(f, encoding="utf-8-sig", newline="")
                    out[Path(name).name] = list(csv.DictReader(text))
    return out, digest


def build(raw_dir: Path, out_dir: Path, tables: list[str]) -> None:
    files, digest = read_release(raw_dir)
    if PRD_SHA256 != digest:
        print(f"note: release sha256 {digest} (header records {PRD_SHA256})")
    for t in tables:
        spec = TABLES[t]
        src = files[spec["file"]]
        items = spec["items"]
        codes = code_candidates(items) if spec["people"] else {i: i for i in items}
        covs = [c for c in src[0] if c not in DROP_ALWAYS and c not in items and c not in spec["drop"]]
        rows, no_marks, ties = [], 0, 0
        for i, r in enumerate(src, start=1):
            cov = {cov_name(c): (r.get(c) or "").strip() for c in covs}
            seen: dict[int, int] = {}
            marks = []
            for col in items:
                v = (r.get(col) or "").strip()
                if v in ("", "NA", "NaN"):
                    continue
                pos = int(float(v))
                if pos < 1:
                    continue
                seen[pos] = seen.get(pos, 0) + 1
                marks.append({"id": i, "task": 1, "item": codes[col], "resp": pos, **cov})
            if not marks:
                no_marks += 1
                continue
            ties += sum(v - 1 for v in seen.values() if v > 1)
            rows.extend(marks)
        write_table(out_dir / f"{t}.csv", rows)
        counts = design_counts(rows)
        coded = "item codes c01.. (named officials; see the script header)" if spec["people"] else \
                "item text as PRD prints it (the options are not people)"
        upsert_design({
            "table": t, "source_file": f'{spec["file"]} (PRD release zip)', "collection": spec["deposit"],
            "jurisdiction": spec["place"], "date": spec["date"],
            "office": spec["task"], "method": "survey", "seats": "na", **counts,
            "n_ballots_cast": len(src), "n_ballots_eligible_est": len(src),
            "write_in_allowed": "no", "candidate_order": "unknown",
            "evidence": (f'{PRD_CITE}, file {spec["file"]}, sha256 {digest} of the release zip; standardised from '
                         f'{spec["study"]}, replication deposit {spec["deposit"]} ({spec["licence"]}, the licence '
                         f'this table is admitted on -- PRD itself carries none). {len(src)} rows in the PRD file, '
                         f'{no_marks} with no recorded position and so no rows; {ties} tied positions; '
                         f'{coded}; n_positions is the largest position recorded; candidate_order unknown '
                         f'(PRD does not record whether the options were shown in a randomised order); '
                         f'counts computed by prd_rankings.py'),
        })
        print(f"{t}: {len(rows)} rows, {counts['n_ballots_with_marks']} respondents, "
              f"{counts['n_candidates']} items, {no_marks} dropped with no position, {ties} ties")


def main(argv: list[str]) -> int:
    if len(argv) >= 2 and argv[1] == "sha":
        _, digest = read_release(Path(argv[2] if len(argv) > 2 else "."))
        print(digest)
        return 0
    if len(argv) < 4 or argv[1] != "build":
        print(__doc__ or "usage: prd_rankings.py build <raw dir> <out dir> [<table> ...]")
        return 2
    raw_dir, out_dir = Path(argv[2]), Path(argv[3])
    tables = argv[4:] or list(TABLES)
    unknown = [t for t in tables if t not in TABLES]
    if unknown:
        print(f"unknown tables: {unknown}")
        return 2
    build(raw_dir, out_dir, tables)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
