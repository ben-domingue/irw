#!/usr/bin/env python3
##Fill the human fields of design_tables.csv from an evidence file, after checking every quote against a saved source.
##The four fields are seats, write_in_allowed, candidate_order and evidence. fairvote_cvr.py cannot fill them: they come
##from the jurisdiction's own documents. Nothing is written until every quote in the evidence file has been found in the
##saved copy of its source.
##
##Usage:
##  python3 fill_design_fields.py --design ../design_tables.csv --evidence slice.evidence.toml --sources <dir> [--check]
##
##--sources is the folder that holds the saved sources. Every quote names its file relative to that folder, so no path is
##written in this script or in the evidence file. --check does the checks and writes nothing.
##
##The evidence file (TOML). Candidate names do not belong in it. One entry per table:
##  [[quote]]                    optional, quotes that apply to the whole slice
##  text = "words as printed in the source"
##  file = "folder/saved-page.html"
##
##  [[contest]]
##  table = "rcv_mpls_20231107_councilw1"
##  seats = 1
##  write_in_allowed = "yes"            # yes or unknown
##  candidate_order = "rotated"         # fixed, rotated or unknown
##  evidence = "<where the seats come from>; write_in_allowed: <source>; candidate_order: <source>"   # added after "; seats:"
##  [[contest.quote]]
##  text = "..."
##  file = "..."
##
##What the script checks:
##  * the table has a design row, and every design row of the evidence file's tables exists;
##  * seats is a whole number of at least 1 and does not exceed n_candidates;
##  * write_in_allowed and candidate_order hold one of the allowed values;
##  * evidence has no dash character other than a plain hyphen (no em or en dash) and is not empty;
##  * the file has at least one quote (slice-level or in a contest), and no quote has an empty text;
##  * every quote is found in its file. Text is compared with all runs of spaces and line breaks collapsed to one space, case-sensitive.
##    An HTML file is compared by its visible text. A PDF is compared by the text file beside it with the same name and
##    the suffix .txt (make it with `pdftotext -layout file.pdf`).
##
##The new evidence cell is the builder's text up to "; seats:" followed by "; seats:" and the sentence of the evidence
##file, so running the script twice gives the same file. Other columns are not touched.
##Needs Python 3.11 or newer (tomllib).
##Exit code: 0 done (or checks passed), 1 a check failed and nothing was written, 2 bad input.
from __future__ import annotations

import argparse
import csv
import re
import sys
import tomllib
from html.parser import HTMLParser
from pathlib import Path

SEATS_MARK = "; seats:"
WRITE_IN = {"yes", "unknown"}
ORDER = {"fixed", "rotated", "unknown"}


class _Text(HTMLParser):
    """Visible text of an HTML page, with the text of each tag kept as its own piece."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.pieces: list[str] = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        self.skip += tag in ("script", "style")

    def handle_endtag(self, tag):
        self.skip -= tag in ("script", "style") and self.skip > 0

    def handle_data(self, data):
        if not self.skip:
            self.pieces.append(data)


def _collapse(s: str) -> str:
    return " ".join(s.split())


def source_texts(path: Path) -> list[str]:
    """The text(s) a quote may be found in. HTML gives two joins: tags inside a word and tags between blocks both match."""
    if path.suffix.lower() == ".pdf":
        path = path.with_suffix(".txt")
    raw = path.read_bytes()
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = raw.decode("cp1252", errors="replace")  # city files are often cp1252
    if path.suffix.lower() in (".html", ".htm") or re.match(r"\s*<(!doctype html|html)\b", text[:200], re.I):
        p = _Text()
        p.feed(text)
        return [_collapse("".join(p.pieces)), _collapse(" ".join(p.pieces))]
    return [_collapse(text)]


def find_quote(quote: str, path: Path) -> bool:
    q = _collapse(quote)
    return any(q in t for t in source_texts(path))


def problems(ev: dict, design: dict, sources: Path) -> list[str]:
    bad: list[str] = []
    seen: set = set()
    quotes = [(q, "slice") for q in ev.get("quote", [])]
    for c in ev.get("contest", []):
        t = c.get("table", "")
        if not t:
            bad.append("a [[contest]] has no table key")
            continue
        if t in seen:
            bad.append(f"{t}: listed twice")
        seen.add(t)
        row = design.get(t)
        if row is None:
            bad.append(f"{t}: no design row")
            continue
        seats = c.get("seats")
        if not isinstance(seats, int) or isinstance(seats, bool) or seats < 1:
            bad.append(f"{t}: seats must be a whole number of at least 1, got {seats!r}")
        elif row["n_candidates"].isdigit() and seats > int(row["n_candidates"]):
            bad.append(f"{t}: seats {seats} is more than n_candidates {row['n_candidates']}")
        if c.get("write_in_allowed") not in WRITE_IN:
            bad.append(f"{t}: write_in_allowed must be one of {sorted(WRITE_IN)}")
        if c.get("candidate_order") not in ORDER:
            bad.append(f"{t}: candidate_order must be one of {sorted(ORDER)}")
        text = c.get("evidence", "")
        if not text.strip():
            bad.append(f"{t}: evidence is empty")
        if any(ch in text for ch in (chr(0x2013), chr(0x2014))):
            bad.append(f"{t}: evidence has an em or en dash")
        quotes += [(q, t) for q in c.get("quote", [])]
    if not quotes:
        bad.append("the evidence file has no quote (0 quotes); every statement needs its source")
    for q, who in quotes:
        if not str(q.get("text", "")).strip():
            bad.append(f"{who}: a quote has an empty or missing text")
            continue
        try:
            ok = find_quote(q["text"], sources / q["file"])
        except (OSError, KeyError) as e:
            ok = False
            q = {**q, "file": f"{q.get('file')} ({e.__class__.__name__})"}
        if not ok:
            bad.append(f"{who}: {q.get('text', '')[:80]!r} not found in {q.get('file')}")
    return bad


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Fill the human fields of design_tables.csv from an evidence file.")
    ap.add_argument("--design", required=True, type=Path)
    ap.add_argument("--evidence", required=True, type=Path)
    ap.add_argument("--sources", required=True, type=Path)
    ap.add_argument("--check", action="store_true", help="check only, write nothing")
    args = ap.parse_args(argv)
    try:
        with open(args.design, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        with open(args.evidence, "rb") as f:
            ev = tomllib.load(f)
    except (OSError, tomllib.TOMLDecodeError) as e:
        print(f"cannot read input: {e}", file=sys.stderr)
        return 2
    design = {r["table"]: r for r in rows}
    if not ev.get("contest"):
        print("cannot read input: the evidence file has no [[contest]]", file=sys.stderr)
        return 2
    bad = problems(ev, design, args.sources)
    if bad:
        print("evidence check failed, nothing written:\n  " + "\n  ".join(bad))
        return 1
    n_quotes = len(ev.get("quote", [])) + sum(len(c.get("quote", [])) for c in ev["contest"])
    print(f"{len(ev['contest'])} contests, {n_quotes} quotes: all found")
    if args.check:
        return 0
    changed = 0
    for c in ev["contest"]:
        r = design[c["table"]]
        new = {"seats": str(c["seats"]), "write_in_allowed": c["write_in_allowed"], "candidate_order": c["candidate_order"],
               "evidence": f"{r['evidence'].split(SEATS_MARK)[0]}{SEATS_MARK} {c['evidence']}"}
        if any(r[k] != v for k, v in new.items()):
            r.update(new)
            changed += 1
    if changed:
        with open(args.design, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
            w.writeheader()
            w.writerows(rows)
    print(f"{changed} design row(s) changed")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
