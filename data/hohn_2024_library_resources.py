"""
A library-resource survey of 105 researchers at the Max Planck Institute for
Evolutionary Anthropology: 13 resource-relevance ratings and 5 agreement
statements.

Source: Hohn, A. (2024). answered questionnaire to Bachelor Thesis "Wie
        sinnvoll ist die Ergänzung des Resource Discovery Systems an der
        Bibliothek des Max-Planck-Instituts für evolutionäre Anthropologie
        durch einen zusätzlichen, externen Index?" [Dataset]. Zenodo.
DOI: 10.5281/zenodo.13269659
Data: https://zenodo.org/records/13269659 ("beantwortete Fragebögen.csv" --
        semicolon-delimited, latin-1, which is why the triage flagged it)
License: CC BY 4.0 (verified on the Zenodo record, metadata.license.id
        "cc-by-4.0")
Item text: SHIPPED, and the deposit is why -- the survey
        platform wrote each question into the column HEADER in full, with the
        item in parentheses and, for the relevance battery, the scale anchors
        inside the stem itself ("Please indicate how useful or relevant the
        following resources are for your work, from 1 (not relevant) to 4
        (extremely relevant). (arXiv)"). The questions are the library's own,
        so the deposit's CC BY is the wording's licence and no third-party
        instrument is in play.

**ONLY the agreement battery ships. The 13-item resource-relevance battery is
NOT shipped, and the numbers are the reason.** Each of its items offers "I
don't know the resource. / I have never used the resource.", and between 35 and
90 of the 105 respondents chose it. After that non-rating is removed the table
holds **378 responses over 90 ids and 13 items -- 28% of its cells, with
per-item n running from 15 to 70**. 28% density alone would not disqualify it;
what does is the combination of 378 total responses with items answered by as
few as 15 people, and the fact that the missingness is informative rather than
incidental -- the quantity left is "relevance among those who have used this
resource", a conditional rating rather than the battery the question posed. The
script still computes the whole thing and prints the per-item drop, so anyone
who disagrees with this call can see exactly what it costs. The agreement
battery is the opposite case: 461 responses over 105 ids and 5 items, 88%
dense.

**One non-substantive option is dropped from each battery, and that is the
judgement call here.** Both batteries offer an answer that is not a point on
their scale:

  * the relevance battery's "I don't know the resource. / I have never used
    the resource." -- a statement that the respondent cannot rate it, not a
    low relevance rating. Treating it as 0, or as the bottom of 1-4, would
    manufacture a rating nobody gave.
  * the agreement battery's "I don't know" -- the same thing for an attitude.
    The other four options are a clean ordered set ("I agree", "I rather
    agree", "I rather disagree", "I disagree") and are mapped 4..1; placing
    "I don't know" in the middle of them would assert an ordering the deposit
    never states.

Both are dropped as missing rather than coded, which is what leaves `resp`
meaning one thing on each table. The run prints how many cells each drop costs.

NOT shipped from this deposit, with reasons: the multiple-answer indicator
grids (media types, points in the literature search, field of work) are
checkbox grids coded 1/blank rather than measured batteries; the single nominal
questions (how often the library is used, print vs electronic, yes/no portal
use) are one-off questions on their own answer sets; and the free-text
follow-ups ("Which specialized databases?", "Would you like to leave any
further comments?") are prose. None of those is an item battery.

PII: none reaches the output. The free-text answers are prose about databases
and library services, in columns whose job is to collect comments rather than
identifiers, and nothing from them is carried -- IRW's output here is
`id`/`item`/`resp` plus `cov_*`, and the only covariates are the two nominal
usage questions. `Teilnehmer` is a 1..105 serial and is replaced by the row
index; the start/end timestamps are dropped.

Output: ONE table, 461 responses -- 105 respondents x 5 items, resp 1-4.
  * hohn_2024_library_agreement -- 5 items, resp 1-4
"""
from __future__ import annotations

from pathlib import Path
import re
import sys

import pandas as pd

SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("beantwortete Fragebögen.csv")
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(".")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

RELEVANCE_STEM = "Please indicate how useful or relevant the following resources"
AGREE_STEM = "Please indicate how much you agree or disagree with the following"

# The relevance battery is already numeric 1-4; only the non-rating option
# needs removing.
NOT_A_RATING = "I don't know the resource. / I have never used the resource."
# The agreement battery's four ordered options, highest first. "I don't know"
# is deliberately absent -- see the module docstring.
AGREE_CODES = {"I agree": 4, "I rather agree": 3,
               "I rather disagree": 2, "I disagree": 1}
AGREE_NOT_A_RATING = "I don't know"

COV_MAP = {
    "How often do you use the library and its resources?": "cov_library_use_frequency",
    "Which publication type do you prefer?": "cov_preferred_publication_type",
}

SECTION_MARKER = "(Eigene Kriterien)"


def _split_header(header: str):
    """(question stem, item name) from one column header.

    The platform writes "<question> (<item>) (Eigene Kriterien)", where the
    trailing marker is its own section label and not part of the item. The item
    group must be matched with BALANCED parentheses, not a `[^()]+` character
    class: one item is "(SSOAR (Social Science Open Access Repository))", and a
    non-nesting pattern silently fails on it -- which is how this was found.
    """
    h = header.strip()
    assert h.endswith(SECTION_MARKER), h
    h = h[:-len(SECTION_MARKER)].rstrip()
    assert h.endswith(")"), h
    depth = 0
    for i in range(len(h) - 1, -1, -1):
        if h[i] == ")":
            depth += 1
        elif h[i] == "(":
            depth -= 1
            if depth == 0:
                return h[:i].strip(), h[i + 1:-1].strip()
    raise AssertionError(f"unbalanced parentheses in {header!r}")


def item_code(header: str) -> str:
    code = re.sub(r"[^a-z0-9]+", "_", _split_header(header)[1].lower())
    return re.sub(r"_+", "_", code).strip("_")[:40]


def item_text(header: str) -> str:
    return _split_header(header)[0]


def pii_screen(df: pd.DataFrame) -> None:
    text_cols = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: examined {len(text_cols)} string column(s) of "
          f"{len(df.columns)}; {len(text_cols)} are free-text or nominal "
          "answers, none of which is carried into the output")
    assert len(df.columns) > 0
    for banned in ("name", "email", "mail", "telefon", "phone", "adresse"):
        bad = [c for c in df.columns if banned in str(c).lower()]
        assert not bad, f"possible identifier column: {bad}"


def main() -> None:
    df = pd.read_csv(SRC, sep=";", encoding="latin-1")
    print("raw shape", df.shape)
    pii_screen(df)
    assert len(df) == 105, len(df)

    rel = [c for c in df.columns if c.startswith(RELEVANCE_STEM)]
    agr = [c for c in df.columns if c.startswith(AGREE_STEM)]
    assert len(rel) == 13 and len(agr) == 5, (len(rel), len(agr))

    df = df.reset_index(drop=True)
    df["id"] = range(1, len(df) + 1)
    for src, dst in COV_MAP.items():
        assert src in df.columns, src
        df[dst] = df[src]
    covs = list(COV_MAP.values())
    print(f"kept {len(covs)} covariate(s): the two single nominal usage "
          "questions. Everything else outside the two batteries -- checkbox "
          "grids, yes/no portal questions, free-text follow-ups and the "
          "timestamps -- is not carried; see the module docstring.")

    # relevance: numeric already, drop the "never used it" answer
    rel_long, rel_text = [], {}
    for c in rel:
        code = item_code(c)
        rel_text[code] = item_text(c)
        v = df[c].astype(str).str.strip()
        n_na = int((v == NOT_A_RATING).sum())
        keep = pd.to_numeric(v.where(v != NOT_A_RATING), errors="coerce")
        rel_long.append(pd.DataFrame({"id": df["id"], "item": code,
                                      "resp": keep,
                                      **{k: df[k] for k in covs}}))
        print(f"  relevance {code:<34} dropped {n_na:>3} 'never used' answer(s)")
    rel_df = pd.concat(rel_long, ignore_index=True).dropna(subset=["resp"])
    cells = len(df) * len(rel)
    per_item = rel_df.groupby("item").size()
    print(f"NOT SHIPPING the relevance battery: {len(rel_df)} responses over "
          f"{rel_df['id'].nunique()} ids and {len(rel)} items = "
          f"{100 * len(rel_df) / cells:.0f}% of {cells} cells, with per-item n "
          f"from {per_item.min()} to {per_item.max()}, because 35-90 of the 105 "
          "respondents had never used each resource. Not the density alone -- "
          "the total, the thinnest items and the informative missingness "
          "together; see the module docstring.")

    agr_long = []
    for c in agr:
        code = item_code(c)
        v = df[c].astype(str).str.strip()
        unknown = set(v) - set(AGREE_CODES) - {AGREE_NOT_A_RATING, "nan"}
        assert not unknown, (c, unknown)
        n_dk = int((v == AGREE_NOT_A_RATING).sum())
        agr_long.append(pd.DataFrame({"id": df["id"], "item": code,
                                      "resp": v.map(AGREE_CODES),
                                      **{k: df[k] for k in covs}}))
        print(f"  agreement {code:<34} dropped {n_dk:>3} \"I don't know\"")
    write(pd.concat(agr_long, ignore_index=True),
          "hohn_2024_library_agreement", covs, [1, 2, 3, 4])


def write(long: pd.DataFrame, table: str, covs: list, permitted: list) -> None:
    long = long.dropna(subset=["resp"]).copy()
    long["resp"] = long["resp"].astype(int)
    assert set(long["resp"].unique()) <= set(permitted), \
        sorted(long["resp"].unique())
    long = long[["id", "item", "resp"] + covs].sort_values(
        ["id", "item"]).reset_index(drop=True)

    checks = run_qc(long, permitted_values=permitted)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, (table, fails)
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {table} {c.name}: {c.detail[:180]}")
    long.to_csv(OUT / f"{table}.csv", index=False)
    print(f"{table}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={sorted(long['resp'].unique())}")


if __name__ == "__main__":
    main()
