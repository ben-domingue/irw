#!/usr/bin/env python3
"""Reconcile the tags' `primary language(s)` with item text's `language` (irw#1837 c).

    python3 tags/itemtext_language/reconcile.py              # report only
    python3 tags/itemtext_language/reconcile.py --stage      # also fill blanks

Two columns in the IRW describe the same fact and nothing ever compared them:

  * the tags' `primary language(s)`: ISO 639-2 bibliographic codes (`hun`),
    written by a human in the Sheet or by the tagger in tags/tags_auto.csv;
  * item text's `language`: the administered language named plainly
    (`Hungarian`), written by the item-text extractor from the source, present
    only when the administration was not English (itemtext_standard.md).

The #1838 measurement found 60 "conflicts" that were only this spelling
difference, so the join here is on mapped codes, never on strings.

Inputs (all local, no Redivis calls):
  itemtext_language.csv          snapshot from fetch_itemtext_language.py
  ../tags_auto.csv               the tagger's rows (Rater = claude-auto)
  the IRW Tags Sheet             public CSV export, read-only; or --sheet FILE
  ../../metadata/metadata.csv    the live-table oracle

Outputs:
  reconciliation.csv             one row per live table that item text gives a
                                 language for, with its verdict
  printed summary

WHAT `--stage` DOES, AND ALL IT DOES. It fills `primary language(s)` on a live
table that is otherwise tagged (a Sheet or auto row carrying a substantive
value) where NO source has a language -- the Sheet cell is blank and so is the
auto cell -- and item text names exactly ONE administered language that maps
to a code. A table with no substantive tags at all gets nothing: a
language-only row would take it out of the tagger's frame (the #1909 trap). It writes that into tags/tags_auto.csv as a
`claude-auto` value: into the table's existing auto row if it has one (only
that cell, only when blank), otherwise as a new row carrying nothing else.
03_tags.R's column-level merge (#1863) then publishes it only into a blank
cell, so a human value can never be displaced, now or after a later Sheet edit.

It never:
  * writes the Sheet (there is no write path, #1708, and there should not be);
  * changes a non-blank value in either source -- disagreements are REPORTED.
    Item text is the stronger evidence on paper, but "tags are living" asks for
    evidence against the source, and a report is the honest output of a
    comparison between two of our own derived records;
  * fills from a multi-language item-text value. vocab.md's rule for an
    instrument multilingual by construction is to leave the tag blank, and
    telling that case from a three-version translated instrument is a
    judgement about the study, not a string operation.
"""

from __future__ import annotations

import argparse
import csv
import io
import sys
import urllib.request
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
TAGS = HERE.parent
SRC = TAGS.parent
AUTO = TAGS / "tags_auto.csv"
SNAPSHOT = HERE / "itemtext_language.csv"
METADATA = SRC / "metadata" / "metadata.csv"
OUT = HERE / "reconciliation.csv"
SHEET_URL = ("https://docs.google.com/spreadsheets/d/"
             "1V3ef0sa7HKtJJd2cgqRAkEdfbpGWDD1JIyQa6HwVK7g/export?format=csv"
             "&gid=126134123")
INSTRUCTION_SENTINEL = "should match what is on redivis"
LANG_COL = "Primary Language(s)"
RATER = "claude-auto"

# Plain language name (as item text writes it) -> ISO 639-2 bibliographic code,
# the convention vocab.md sets for the tags. Varieties collapse to the language
# the tags can express: the tag has one code for Chinese, one for Arabic.
# A name missing here is reported as `unmapped`, never guessed.
NAME_TO_ISO = {
    "albanian": "alb", "amharic": "amh", "arabic": "ara",
    "egyptian arabic": "ara", "modern arabic": "ara", "standard arabic": "ara",
    "bengali": "ben", "bulgarian": "bul", "burmese": "bur", "myanmar": "bur",
    "catalan": "cat", "chinese": "chi", "mandarin chinese": "chi",
    "mandarin (simplified)": "chi", "mandarin (traditional)": "chi",
    "chinese (simplified)": "chi", "chinese (traditional, hong kong)": "chi",
    "croatian": "hrv", "czech": "cze", "dagbani": "dag", "danish": "dan",
    "dutch": "dut", "english": "eng", "filipino": "fil", "finnish": "fin",
    "french": "fre", "georgian": "geo", "german": "ger", "greek": "gre",
    "haitian creole": "hat", "hebrew": "heb", "hindi": "hin",
    "hungarian": "hun", "indonesian": "ind", "italian": "ita",
    "japanese": "jpn", "kazakh": "kaz", "khmer": "khm", "kinyarwanda": "kin",
    "korean": "kor", "lao": "lao", "lithuanian": "lit", "malay": "may",
    "mongolian": "mon", "norwegian": "nor", "persian": "per", "polish": "pol",
    "portuguese": "por", "portuguese (brazil)": "por", "romanian": "rum",
    "russian": "rus", "serbian": "srp", "slovak": "slo", "slovenian": "slv",
    "spanish": "spa", "swedish": "swe", "tagalog": "tgl", "telugu": "tel",
    "thai": "tha", "tigrinya": "tir", "turkish": "tur", "ukrainian": "ukr",
    "urdu": "urd", "vietnamese": "vie",
}

# ISO 639-2 terminology -> bibliographic, mirroring LANGUAGE_RENAMES in
# metadata/tag_normalize.R so both sides compare in the published spelling.
T_TO_B = {
    "sqi": "alb", "hye": "arm", "eus": "baq", "bod": "tib", "mya": "bur",
    "ces": "cze", "zho": "chi", "cym": "wel", "deu": "ger", "nld": "dut",
    "ell": "gre", "fas": "per", "fra": "fre", "kat": "geo", "isl": "ice",
    "mkd": "mac", "mri": "mao", "msa": "may", "ron": "rum", "slk": "slo",
    "jap": "jpn",
}


def blank(v: str | None) -> bool:
    v = (v or "").strip()
    return v == "" or v == "NA"


def tag_codes(cell: str) -> frozenset[str]:
    if blank(cell):
        return frozenset()
    out = set()
    for p in cell.replace(";", ",").split(","):
        p = p.strip().lower()
        if p:
            out.add(T_TO_B.get(p, p))
    return frozenset(out)


def itemtext_codes(value: str) -> tuple[frozenset[str], list[str]]:
    """(codes, names that did not map). A table whose snapshot holds two
    different values (joined with ' | ') is treated as their union."""
    codes, bad = set(), []
    for chunk in value.split("|"):
        # `; ` is the schema's separator. A bare comma list ("Khmer, Lao,
        # Myanmar") is split too, but never a comma inside parentheses:
        # "Chinese (Traditional, Hong Kong)" is one language.
        names = []
        for piece in chunk.split(";"):
            names += [piece] if "(" in piece else piece.split(",")
        for name in names:
            n = name.strip()
            if not n:
                continue
            code = NAME_TO_ISO.get(n.lower())
            if code:
                codes.add(code)
            else:
                bad.append(n)
    return frozenset(codes), bad


def read_csv_rows(text: str) -> list[dict[str, str]]:
    return list(csv.DictReader(io.StringIO(text)))


# The columns that make a row "tagged" in the #1704 frame (sample_untagged.py's
# SUBSTANTIVE, less the language column this script is about).
SUBSTANTIVE = ["Sample", "Construct type", "Measurement tool", "Item format",
               "Construct Name"]


def substantive(row: dict[str, str]) -> bool:
    return any(not blank(row.get(c)) for c in SUBSTANTIVE)


def load_sheet(path: str | None) -> tuple[dict[str, str], set[str]]:
    """(lower(table) -> the Sheet's language cell, '' when blank;
    tables whose Sheet row carries any substantive tag)."""
    if path:
        text = Path(path).read_text(encoding="utf-8")
    else:
        with urllib.request.urlopen(SHEET_URL, timeout=120) as r:
            text = r.read().decode("utf-8")
    rows = read_csv_rows(text)
    if not rows or rows[0]["table"].strip().lower() != INSTRUCTION_SENTINEL:
        sys.exit("Sheet: instruction row not found under the header; refusing "
                 "to read a sheet whose layout has changed.")
    out: dict[str, str] = {}
    tagged: set[str] = set()
    for r in rows[1:]:
        t = (r.get("table") or "").strip().lower()
        if not t:
            continue
        v = "" if blank(r.get(LANG_COL)) else r[LANG_COL].strip()
        # A table on two Sheet rows: any non-blank cell is a human value.
        out[t] = out.get(t) or v
        if substantive(r):
            tagged.add(t)
    return out, tagged


def load_snapshot() -> list[dict[str, str]]:
    lines = [ln for ln in SNAPSHOT.read_text(encoding="utf-8").splitlines()
             if not ln.startswith("#")]
    return list(csv.DictReader(lines))


def classify(it: frozenset[str], tags: frozenset[str]) -> str:
    if not tags:
        return "tags_blank"
    if it == tags:
        return "agree"
    if tags < it:
        return "tags_subset"      # tags name fewer languages than item text
    if tags > it:
        return "tags_superset"    # tags name more
    if tags & it:
        return "overlap"
    return "disjoint"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet", help="a local copy of the Sheet CSV export")
    ap.add_argument("--stage", action="store_true",
                    help="fill blank cells in tags_auto.csv (see docstring)")
    ap.add_argument("--sample", type=int, default=8)
    args = ap.parse_args()

    live = {r["table"].strip().lower(): r["table"].strip()
            for r in csv.DictReader(METADATA.open(encoding="utf-8"))}
    sheet, sheet_tagged = load_sheet(args.sheet)
    with AUTO.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        auto_cols = reader.fieldnames
        auto_rows = list(reader)
    auto = {r["table"].strip().lower(): r for r in auto_rows}

    out = []
    for s in load_snapshot():
        if not s["language"]:
            continue
        k = s["table"].strip().lower()
        codes, bad = itemtext_codes(s["language"])
        sheet_v = sheet.get(k, "")
        auto_v = "" if k not in auto or blank(auto[k][LANG_COL]) else auto[k][LANG_COL]
        # Whose value the published tag is: the Sheet's cell wins where filled
        # (#1723/#1863), else the auto cell.
        source = "sheet" if sheet_v else ("auto" if auto_v else "")
        tags = tag_codes(sheet_v or auto_v)
        if k not in live:
            verdict = "not_live"
        elif bad:
            verdict = "unmapped"
        else:
            verdict = classify(codes, tags)
        multi = len(codes) > 1
        # Only where language is the one hole in an otherwise-tagged table. A
        # language-only row on an untagged table makes sample_untagged.py count
        # it as tagged, and stage_batch.py then skips the tagger's full row for
        # it -- the #1909 trap, where 369 such rows hid from #1704. Those
        # tables are reported (`untagged`) and left for the tagger.
        has_tags = k in sheet_tagged or (
            k in auto and auto[k].get("Status") == "tagged" and substantive(auto[k]))
        fill = (verdict == "tags_blank" and not multi and len(codes) == 1
                and has_tags)
        if verdict == "tags_blank" and not has_tags:
            verdict = "untagged"
        out.append({
            "table": live.get(k, s["table"]), "shard": s["shard"],
            "itemtext_language": s["language"],
            "itemtext_codes": ",".join(sorted(codes)),
            "unmapped_names": "; ".join(bad),
            "tag_value": sheet_v or auto_v, "tag_source": source,
            "sheet_row": "yes" if k in sheet else "no",
            "verdict": verdict,
            "action": ("fill" if fill else
                       "tagger" if verdict == "untagged" else
                       "report" if verdict not in ("agree", "not_live") else ""),
        })

    out.sort(key=lambda r: (r["verdict"], r["table"].lower()))
    with OUT.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0].keys()), lineterminator="\n")
        w.writeheader()
        w.writerows(out)

    c = Counter(r["verdict"] for r in out)
    bysrc = Counter((r["verdict"], r["tag_source"]) for r in out)
    print(f"{len(out)} tables carry an item-text `language`\n")
    print(f"{'verdict':<15}{'tables':>7}{'sheet':>7}{'auto':>7}")
    for v, n in sorted(c.items(), key=lambda x: -x[1]):
        print(f"{v:<15}{n:>7}{bysrc[(v, 'sheet')]:>7}{bysrc[(v, 'auto')]:>7}")
    blanks = [r for r in out if r["verdict"] == "tags_blank"]
    fills = [r for r in out if r["action"] == "fill"]
    print(f"\ntags_blank (table otherwise tagged): {len(fills)} single-language "
          f"(fill), {len(blanks) - len(fills)} multi-language (left blank, "
          f"vocab.md multilingual-by-construction rule)")
    print(f"untagged: {c['untagged']} table(s) with no substantive tag row -- "
          f"left for the tagger, not given a language-only row (#1909)")
    for v in ("disjoint", "overlap", "tags_subset", "tags_superset", "unmapped"):
        rows = [r for r in out if r["verdict"] == v][: args.sample]
        if rows:
            print(f"\n{v} (first {len(rows)}):")
            for r in rows:
                print(f"  {r['table']:<48} tag={r['tag_value']!r:<14} "
                      f"[{r['tag_source']}]  itemtext={r['itemtext_language'][:60]!r}")
    print(f"\nwrote {OUT}")

    if not args.stage:
        return

    added = changed = 0
    for r in fills:
        k = r["table"].strip().lower()
        code = r["itemtext_codes"]
        if k in auto:
            row = auto[k]
            if not blank(row[LANG_COL]):
                continue          # re-checked; never overwrite
            row[LANG_COL] = code
            note = (f"primary language(s) {code} from the published item text's "
                    f"administered `language` ({r['itemtext_language']}), irw#1837.")
            row["Notes"] = f"{row['Notes']} {note}".strip() if row["Notes"] else note
            changed += 1
        else:
            row = {c: "" for c in auto_cols}
            row.update({
                "table": r["table"], "Rater": RATER, LANG_COL: code,
                "Notes": (f"primary language(s) only, from the published item "
                          f"text's administered `language` "
                          f"({r['itemtext_language']}), irw#1837."),
                "Status": "tagged",
            })
            auto_rows.append(row)
            auto[k] = row
            added += 1
    with AUTO.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=auto_cols, lineterminator="\n")
        w.writeheader()
        w.writerows(auto_rows)
    print(f"staged: {changed} blank cell(s) filled in existing auto rows, "
          f"{added} new language-only auto row(s) -> {AUTO}")


if __name__ == "__main__":
    main()
