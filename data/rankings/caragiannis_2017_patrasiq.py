#!/usr/bin/env python3
##PatrasIQ 2016 cities survey (Caragiannis, Chatzigeorgiou, Krimpas & Voudouris, AAAI 2017) -> IRW rankings tables.
##Citation: Caragiannis, I., Chatzigeorgiou, X., Krimpas, G. A., & Voudouris, A. A. (2017). Optimizing
##Positional Scoring Rules for Rank Aggregation. Proceedings of the AAAI Conference on Artificial
##Intelligence, 31(1). https://doi.org/10.1609/aaai.v31i1.10585 (journal version: Artificial Intelligence
##267 (2019) 58-77, https://doi.org/10.1016/j.artint.2018.11.001). Data distributed by PrefLib as dataset
##00034 "cities" (https://www.preflib.org/dataset/00034), donated by Ioannis Caragiannis.
##Rights: no licence is stated by PrefLib or on the authors' pages. Ioannis Caragiannis granted permission
##by email on 2026-11-20 ("Sure, you can distribute our datasets.") in reply to IRW's letter of 2026-11-15,
##which offered CC BY 4.0 as the default licence; he named none. Dictionary: Original License =
##Permission via Email, Derived License = CC BY 4.0.
##
##Design (PrefLib info.txt; paper, section 6): 392 volunteers at the 3rd PatrasIQ research and technology
##exhibition, Patras, Greece, April 2016. Each was given a random bundle of six cities (from a pool of 36)
##and a random bundle of six countries (from a pool of 48), and gave a strict ranking of each bundle, in
##decreasing order of their estimate of the cities' cost-of-living index and of the countries' population.
##
##Files read (nothing in them is executed): PrefLib 00034-00000001.soi ("Cost of Living") and
##00034-00000002.soi ("Population") at PrefLib-Data commit 220b7e5. Each is a weighted profile:
##`count: a,b,c,d,e,f`, the first alternative ranked first, lines grouped by identical ranking.
##
##Layout: R5 (weighted profiles are expanded): one id per ranking, in PrefLib's line order, task = 1,
##item = the city or country name as shown, in lowercase snake_case ("New York" -> new_york, "Czech
##Republic" -> czech_republic): places, not people, but the validator's personal-name test (R4) cannot
##tell "San Francisco" from a person, and Eurovision's precedent (ISO codes) has no readable city
##equivalent. resp = position, 1 = highest estimate.
##**Two tables, not one table with two tasks** (the IRW letter proposed the latter): PrefLib publishes the
##two questions as separate profiles grouped by ranking, with no volunteer key, so a volunteer's cities
##ranking cannot be joined to the same volunteer's countries ranking. Putting both under `task` would make
##id 1 in task 1 and id 1 in task 2 look like one person when they are not.
##Ground truth: PrefLib's alternative ids are the true order (numbeo.com cost-of-living index and
##Wikipedia population, both April 2016), alternative 1 highest. The rankings standard has no column for a
##known correct order, so it is recorded in the design record's `evidence` and the dictionary description.
##Repeated rankings: some identical six-item rankings occur twice (the build prints how many). With
##C(36,6) and C(48,6) possible bundles, two volunteers drawing the same bundle and ranking it identically
##is very unlikely, so these are probably repeated submissions or entries; the source cannot say, and they
##are kept as recorded.
##
##Usage: python3 -I caragiannis_2017_patrasiq.py build <raw dir> <out dir>
##Tables: caragiannis_2017_patrasiq_costofliving, caragiannis_2017_patrasiq_population.
from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # so `python3 -I` still finds rank_common
from rank_common import design_counts, fetch, upsert_design, write_table  # noqa: E402

PREFLIB_COMMIT = "220b7e5c7a7e04dcde56ce04b8923b8c589cbb33"
BASE = ("https://raw.githubusercontent.com/PrefLib/PrefLib-Data/" + PREFLIB_COMMIT
        + "/datasets/00034%20-%20cities/")
PAPER = "https://doi.org/10.1609/aaai.v31i1.10585"

# PrefLib file -> (table, PrefLib title, n alternatives, what is ranked, truth source)
FILES = {
    "00034-00000001": ("caragiannis_2017_patrasiq_costofliving", "Cost of Living", 36,
                       "six cities by cost of living, highest first", "numbeo.com cost-of-living index"),
    "00034-00000002": ("caragiannis_2017_patrasiq_population", "Population", 48,
                       "six countries by population, largest first", "Wikipedia population figures"),
}
N_VOTERS = 392


def parse_soi(path: Path):
    head, prof = {}, []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("#"):
            k, _, v = line[1:].partition(":")
            head[k.strip()] = v.strip()
        elif line.strip():
            count, order = line.split(":", 1)
            prof.append((int(count), tuple(int(x) for x in order.split(","))))
    return head, prof


def build(raw_dir: Path, out_dir: Path) -> int:
    for stem, (t, title, n_alt_exp, what, truth) in FILES.items():
        src = fetch(BASE + f"{stem}.soi", raw_dir / "preflib" / f"{stem}.soi")
        head, prof = parse_soi(src)
        n_alt = int(head["NUMBER ALTERNATIVES"])
        labels = {k: head[f"ALTERNATIVE NAME {k}"] for k in range(1, n_alt + 1)}
        n_voters = int(head["NUMBER VOTERS"])
        # Stop on anything the build's reading of the file depends on.
        if head.get("DATA TYPE") != "soi" or head.get("TITLE") != title or n_alt != n_alt_exp:
            raise SystemExit(f"{stem}: header not as expected -- stop and look")
        if n_voters != N_VOTERS or sum(c for c, _ in prof) != n_voters:
            raise SystemExit(f"{stem}: counts do not add up to the header -- stop and look")
        if len(prof) != int(head["NUMBER UNIQUE ORDERS"]) or len({o for _, o in prof}) != len(prof):
            raise SystemExit(f"{stem}: unique orders do not match the header -- stop and look")
        if any(len(o) != 6 or len(set(o)) != 6 or not set(o) <= set(labels) for _, o in prof):
            raise SystemExit(f"{stem}: a ranking is not six distinct alternatives -- stop and look")
        labels = {k: re.sub(r"[^a-z0-9]+", "_", v.casefold()).strip("_") for k, v in labels.items()}
        if len(set(labels.values())) != n_alt:
            raise SystemExit(f"{stem}: alternative names repeat -- stop and look")
        out, i = [], 0
        for count, order in prof:
            for _ in range(count):
                i += 1
                out.extend({"id": i, "task": 1, "item": labels[a], "resp": pos}
                           for pos, a in enumerate(order, start=1))
        counts = design_counts(out)
        n_repeat = sum(c - 1 for c, _ in prof if c > 1)
        n_max = max(c for c, _ in prof)
        # Agreement with the true order, pairwise over each ranking's 15 pairs.
        agree = sum(sum(1 for x in range(6) for y in range(x + 1, 6) if o[x] < o[y]) * c for c, o in prof)
        pct = 100 * agree / (15 * n_voters)
        truth_order = " > ".join(labels[k] for k in range(1, n_alt + 1))
        sha = hashlib.sha256(src.read_bytes()).hexdigest()
        design = {
            "table": t, "source_file": f"{stem}.soi (PrefLib-Data {PREFLIB_COMMIT[:7]})",
            "collection": "https://www.preflib.org/dataset/00034",
            "jurisdiction": "PatrasIQ exhibition, Patras, Greece (volunteer survey)", "date": "2016-04",
            "office": (f"PatrasIQ 2016 {title.lower()} question: rank a random bundle of {what} "
                       f"(PrefLib {stem}, {n_alt} {'cities' if n_alt == 36 else 'countries'} in the pool)"),
            "method": "survey", "seats": "na", **counts,
            "n_ballots_cast": n_voters, "n_ballots_eligible_est": n_voters,
            "write_in_allowed": "no", "candidate_order": "unknown",
            "evidence": (
                f"{BASE}{stem}.soi, sha256 {sha}, read 2026-11-20; a weighted profile of {len(prof)} distinct "
                f"rankings of 6 expanded to one id per ranking (R5) in the file's line order; design from PrefLib "
                f"info.txt and Caragiannis et al. (2017), {PAPER}, section 6: 392 volunteers at PatrasIQ, April "
                f"2016, each ranked a random bundle of {what}; GROUND TRUTH (PrefLib alternative ids, from "
                f"{truth}, April 2016, highest first): {truth_order}; {pct:.1f}% of the pairs within rankings "
                f"agree with it; {n_repeat} rankings repeat an identical earlier ranking (at most {n_max} "
                "copies), kept as recorded (probably repeated entries; the source cannot say); the two PrefLib "
                "files are separate profiles with no volunteer key, so this table cannot be joined to its "
                "sibling (caragiannis_2017_patrasiq_costofliving / _population) by id; candidate_order "
                "unknown (how the bundle was shown is not reported); write_in_allowed no and n_positions 6: a "
                "strict ranking of the six given; seats na (a survey); date is the exhibition month; "
                "n_ballots_eligible_est equals n_ballots_cast; counts computed by caragiannis_2017_patrasiq.py")}
        write_table(out_dir / f"{t}.csv", out)
        upsert_design(design)
        print(f"{t}: {n_voters} rankings, {len(prof)} distinct, {n_repeat} repeats (max {n_max}), "
              f"{pct:.1f}% pairs agree with truth, {len(out)} rows")
    return 0


def main(argv: list[str]) -> int:
    if argv[:1] == ["build"] and len(argv) == 3:
        return build(Path(argv[1]), Path(argv[2]))
    print("usage: caragiannis_2017_patrasiq.py build <raw dir> <out dir>", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
