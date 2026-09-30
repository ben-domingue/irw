"""Read the instrument rights register before a table ships (#2154).

Nothing between a finished extraction and a published table used to ask
whether the instrument is one IRW may ship: every rights block was enforced by
someone remembering, or found afterwards by `itemtext/sweep_instrument_rights.py`.
That is how `gillman_2023_pss` shipped. This is the sweep's matching, moved to
the write path, on the two surfaces a restricted instrument reaches the corpus
through:

  item text  -- `match_item_text`, case-insensitive substrings of canonical
                stems, against `item_text` and the `*_translated` columns in an
                `__items` table (the latter since 2026-09-29, irw#2401);
  item codes -- `match_item_code`, a regex, against `item` in a RESPONSE table.
                A script that uses source headers as codes carries the
                instrument into data no item-text withdrawal reaches
                (luu_2024_stai6 #2123, holden_2026_bsri #2101). Renaming a
                published code is not cheap; renaming an unpublished one is.

It WARNS, and only warns. The sweep's own header records why, from real
sessions, and each is a rule here:

  1. A hit is a lead, never a verdict -- three searches, three false positives
     (alkouri_2025_icu_stressors is not the PSS). So never an error.
  2. A miss is not an all-clear -- complete PSS reproductions scored 1 of 4.
     So a clean run emits NOTHING that could be read as "rights checked".
  3. Non-canonical wording is still covered -- dopmeijer_2022_loneliness
     matched 0 of 11 stems and was withdrawn. The message says so.

What it must do is put the register row in front of the person uploading.
The register lives in a checkout (`itemtext/instrument_rights_register.csv`);
installed from a wheel there is none, and the check does not run. That is
recorded in `checks_run` as `rights_register:unavailable`, not passed quietly.
"""
from __future__ import annotations

import csv
import os
import re
from pathlib import Path

from .model import Finding

#: Overridable, so a test -- or a contributor holding a copy -- can point at one.
REGISTER_ENV = "IRW_RIGHTS_REGISTER"
_DEFAULT = (Path(__file__).resolve().parent.parent
            / "itemtext" / "instrument_rights_register.csv")

#: Verdicts that put a table on hold for a person. `ship` and `allow` need
#: nothing; `ship_with_note` ships only once its issues-page note exists.
HOLD = {"block", "hold", "escalate"}
NOTE = {"ship_with_note"}

_cache: dict = {}


def register_path() -> Path:
    return Path(os.environ.get(REGISTER_ENV) or _DEFAULT)


def load_register(path: Path | None = None):
    """The register rows that can hold a table, with patterns compiled, or
    None when there is no register to read."""
    path = Path(path) if path else register_path()
    if not path.is_file():
        return None
    key = (str(path), path.stat().st_mtime)
    if key in _cache:
        return _cache[key]
    rows = []
    with path.open(newline="") as fh:
        for r in csv.DictReader(fh):
            verdict = (r.get("verdict") or "").strip()
            if verdict not in HOLD | NOTE:
                continue
            stems = [s.strip().lower() for s in (r.get("match_item_text") or "").split("|")
                     if s.strip()]
            try:
                code = re.compile(r["match_item_code"], re.I) if r.get("match_item_code") else None
            except re.error:
                code = None      # a prose cell, not a pattern; the text half still runs
            rows.append({"instrument": " ".join((r.get("instrument") or "").split()),
                         "family": r.get("family") or "", "verdict": verdict,
                         "rule": " ".join((r.get("rule") or "").split()),
                         "stems": stems, "code": code})
    _cache.clear()
    _cache[key] = rows
    return rows


def _message(row, surface: str, hits: list) -> str:
    shown = ", ".join(repr(h) for h in hits[:4]) + (" ..." if len(hits) > 4 else "")
    if row["verdict"] in NOTE:
        act = ("It ships only with its note on the item-text issues page; "
               "check the note exists.")
    else:
        act = ("HOLD: read the items, then clear it with whoever owns rights "
               "rulings before this ships.")
    rule = f" Rule: {row['rule'][:160]}." if row["rule"] else ""
    return (f"{len(hits)} {surface} match the rights register's "
            f"{row['family'] or row['instrument']} row ({row['instrument'][:90]}; "
            f"verdict {row['verdict']}): {shown}.{rule} {act} A match is a lead, "
            f"not a verdict; a table with no match is not rights-cleared, and "
            f"wording that differs from the canonical stems can still be covered.")


#: Text columns the item-text surface reads. `*_translated` joined 2026-09-29
#: (Ben, irw#2401): a block row covers them too. beck_2021_iesr shipped the German
#: IES-R in item_text, which matches no stem, and Weiss & Marmar's English IES-R
#: in item_text_translated, which matches them all.
TEXT_COLUMNS = ("item_text", "item_text_translated", "option_text_translated",
                "instructions_translated", "section_prompt_translated")


def check_item_text(df, table: str, register=None) -> list:
    """Findings for an item-text frame: one per register row and text column it
    touches, so a hit that only the English carries says so."""
    out = []
    for col in TEXT_COLUMNS:
        if col not in df.columns:
            continue
        texts = df[col].dropna().astype(str)
        texts = texts[~texts.str.strip().isin(["", "NA"])]
        if texts.empty:
            continue
        low = texts.str.lower()
        items = df.loc[texts.index, "item"].astype(str) if "item" in df.columns else texts
        surface = "item(s)' text" if col == "item_text" else f"item(s)' {col}"
        for row in register:
            if not row["stems"]:
                continue
            hit = low.apply(lambda t: any(s in t for s in row["stems"]))
            if hit.any():
                names = sorted(set(items[hit]))
                out.append(Finding("rights_register", "warn",
                                   _message(row, surface, names),
                                   table=table, group="rights"))
    return out


#: The code surface needs more than one stray hit. Measured over the 861
#: legacy response tables in data/pub (2026-09-27): any-match flagged 308 of
#: them, 226 through one `escalate` row whose pattern is the single letter
#: 'B', and word-list tables (lexical decision, Duolingo) matched a dozen
#: unanchored patterns through one word among thousands. Requiring at least
#: three codes (or every code, in a smaller table) and a tenth of all codes,
#: and leaving `escalate` rows to the text surface, flags 59 -- each a table
#: that does carry the named instrument.
MIN_CODE_HITS = 3
MIN_CODE_SHARE = 0.10


def check_item_codes(df, table: str, register=None) -> list:
    """Findings for a response frame's item codes.

    A response table carrying a restricted instrument is not itself a problem
    -- the rulings are about wording -- so this asks the narrower question the
    code surface exists for (#2123, #2101): are these codes the instrument's
    WORDING? `pss1..pss10` is not; `luu_2024_stai6`'s six STAI stems were.
    """
    if "item" not in df.columns:
        return []
    codes = sorted({str(c) for c in df["item"].dropna().unique()})
    out = []
    for row in register:
        if row["code"] is None or row["verdict"] == "escalate":
            continue
        names = [c for c in codes if row["code"].search(c)]
        if len(names) < min(MIN_CODE_HITS, len(codes)) or \
                len(names) < MIN_CODE_SHARE * len(codes):
            continue
        out.append(Finding(
            "rights_register", "warn",
            f"{len(names)} item code(s) match the rights register's "
            f"{row['family'] or row['instrument']} row ({row['instrument'][:90]}; "
            f"verdict {row['verdict']}): "
            + ", ".join(repr(n) for n in names[:4]) + (" ..." if len(names) > 4 else "")
            + ". Response data from this instrument can ship; its wording cannot. "
              "If these codes ARE item wording (source column headers used as "
              "codes), rename them before this table is published -- afterwards a "
              "rename is neither cheap nor reversible -- and do not ship its item "
              "text without a ruling. A match is a lead, not a verdict.",
            table=table, group="rights"))
    return out
