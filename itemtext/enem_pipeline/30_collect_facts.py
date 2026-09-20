#!/usr/bin/env python3
"""Collect, from ARTIFACTS ON DISK, every number the R9 sidecar files cite.

The 2023 batch's notes are trusted because they were checked against artifacts
rather than against what a previous note claimed. This script exists so the
same is true of the other eleven years: it reads the item tables, manifest.json,
join_report.json and the gate output, and writes facts.json. 31_assemble_batch.py
renders prose from that file and invents nothing.
"""
import collections, csv, glob, json, os, re, subprocess, sys

# Items checked INDIVIDUALLY against the printed page. Everything else is
# classified by stem language, which is a HEURISTIC and is known to misfire:
# it read 2016 CN 86572 as a figure item because the stem mentions "circuito",
# when the options are actually the fractions 1, 4/7, 10/27, 14/81, 4/81. So the
# generated prose names only these and stays neutral about the rest.
VERIFIED_FIGURE = {("2013","15947"),("2016","97711"),("2018","111411"),
                   ("2021","62293"),("2013","7867")}
VERIFIED_NOT_FIGURE = {("2015","14712"),("2016","60291"),("2016","86572")}

# An item whose option_text is all NA is NOT automatically a bare-figure item.
# 35 of the 37 are: the stem asks the reader to pick a drawing. TWO are not --
# 2015 MT 14712 and 2016 MT 60291 are probability questions whose options are
# STACKED FRACTIONS (numerator over denominator), which the line-based parser
# cannot segment and which the geometric extractor recovers with the next
# item's chart data mixed in. Calling those "drawings" in a shipped note would
# be a false claim, so they are counted separately and disclosed as missing.
FIGURE_STEM = re.compile(
    r"gr[áa]fico|esquema|figura|estrutura|desenho|diagrama|croqui|planta|mapa|imagem|"
    r"circuito|proje[çc][ãa]o|proje[çc][õo]es|sombra|vista|planifica[çc][ãa]o|"
    r"f[óo]rmula estrutural|esbo[çc]o|formato|forma de representa|selo|recipiente|"
    r"segmento|representad|representa[çc][ãa]o|pe[çc]a", re.I)

HERE = os.path.dirname(os.path.abspath(__file__))
T = "/scratch/users/mazzafe/itemtext_years"
# WHERE EACH YEAR'S TABLES COME FROM. This is the assembler's copy source,
# and getting it wrong is how a fix gets reverted for the third time.
#
# 42_rebuild.py writes out_rb/ for every year in its RECIPE, and
# 41_staleness.py's committed_matches_pipeline() compares the shipped tables
# against exactly that directory. So out_rb IS the canonical build, and the
# assembler has to copy from it -- otherwise `31_assemble_batch.py` silently
# rewinds the repo to whatever those older directories happened to hold.
# It pointed at 2018/out_v8, 2021/out_v8 and the bare year roots, all of
# which predate the stacked-fraction pass, the description relocation and the
# script-marker fixes. Nothing would have reported it: the tables would still
# have passed every content gate, just with the corrections gone.
#
# 2024 and 2025 are NOT in 42_rebuild.py's RECIPE (they are built from the
# DOSVOX text edition, not from booklet PDFs), so they keep their own dirs.
DIRS = {"2024": "2024/items", "2025": "2025/items_sp"}
REBUILT = {"2013", "2015", "2016", "2017", "2018", "2019",
           "2020", "2021", "2022"}
YEARS = ["2013", "2015", "2016", "2017", "2018", "2019",
         "2020", "2021", "2022", "2024", "2025"]
AREAS = ["ch", "cn", "lc", "mt"]


def year_dir(y):
    if y in REBUILT:
        return os.path.join(T, y, "out_rb")
    return os.path.join(T, DIRS.get(y, y))


def main():
    man = json.load(open(os.path.join(HERE, "manifest.json")))
    out = {}
    for y in YEARS:
        d = year_dir(y)
        e = {"dir": d, "areas": {}}
        for a in AREAS:
            p = f"{d}/enem_{y}_1mil_{a}__items.csv"
            if not os.path.exists(p):
                continue
            rows = list(csv.DictReader(open(p, encoding="utf-8")))
            items = {r["item"] for r in rows}
            ai = man[y]["areas"][a.upper()]
            blob = "".join((r["item_text"] or "") + (r["option_text"] or "") for r in rows)
            by_item = collections.defaultdict(list)
            for r in rows:
                by_item[r["item"]].append(r)
            fig, unseg, guess = [], [], []
            for it, rs in by_item.items():
                if not all((r["option_text"] or "").strip() in ("", "NA") for r in rs):
                    continue
                tail = re.sub(r"\s+", " ", rs[0]["item_text"] or "")[-300:]
                if (y, it) in VERIFIED_FIGURE: fig.append(it)
                elif (y, it) in VERIFIED_NOT_FIGURE: unseg.append(it)
                elif FIGURE_STEM.search(tail): guess.append(it)
                else: unseg.append(it)
            e["areas"][a] = {
                "n_items": len(items),
                "n_rows": len(rows),
                "published": len(ai["published_items"]),
                "missing": sorted(set(ai["published_items"]) - items),
                "no_key_declared": sorted(ai.get("no_scorable_key_not_shipped", [])),
                "aban_kept_valid_key": sorted(ai.get("aban_kept_valid_key", [])),
                "acc_co_prova": ai.get("accessibility_co_prova"),
                "figure_option_items": sorted(fig),
                "unsegmented_option_items": sorted(unseg),
                "untranscribable_option_items": sorted(guess),
                "generated_desc_items": sorted({r["item"] for r in rows
                                                if "gerada por IA" in (r["item_text"] or "")}),
                "replacement_char": blob.count("�"),
                "replacement_char_items": sorted({r["item"] for r in rows
                    if "�" in (r["item_text"] or "") + (r["option_text"] or "")}),
                "instructions_words": len(re.findall(r"[A-Za-zÀ-ÿ]{3,}",
                                                     rows[0]["instructions"] or "")) if rows else 0,
                "section_prompt_used": any((r["section_prompt"] or "").strip() for r in rows),
            }
        jr = f"{d}/join_report.json"
        if os.path.exists(jr):
            r = json.load(open(jr))
            e["position_convention"] = r.get("position_convention")
            e["derived_offset"] = r.get("derived_offset")
            e["aban_kept"] = r.get("aban_kept")
        e["standard_prova_codes"] = man[y]["standard_prova_codes"]
        # the gate, re-run so the cited figure is current
        gs = f"{T}/gab_strings_{y}.txt"
        if os.path.exists(gs):
            v = subprocess.run([sys.executable,
                                os.path.join(HERE, "20_verify_gabarito_microdata.py"), y],
                               capture_output=True, text=True).stdout
            e["gate_lines"] = [l.strip() for l in v.splitlines()
                               if re.search(r"TOTAL|offset|NOT SCORABLE", l)]
        out[y] = e
    with open(os.path.join(HERE, "facts.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    for y in YEARS:
        ar = out[y]["areas"]
        print(f"  {y}: " + " ".join(f"{a}={ar[a]['n_items']}" for a in AREAS if a in ar)
              + f"  conv={list((out[y].get('position_convention') or {}).values())[:1]}"
              + f"  gate={'yes' if out[y].get('gate_lines') else 'NO'}")
    print(f"  -> facts.json ({os.path.getsize(os.path.join(HERE,'facts.json'))} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
