#!/usr/bin/env python3
"""Recall per collection, against a name-token baseline (review R-28, #3225).

WHY
---
The review hand-verified 4 instruments and 125 tables and found curated
collections pooling **75 of 125** -- 100% in shards 1/3/4 and 0% in shard 7 --
with 43 of the 50 misses carrying a correct `construct_name` tag, so the tables
are annotated and the collection simply does not have them. That is one number
over four instruments, which is enough to know something is wrong and not
enough to fix anything.

This computes the same quantity for every instrument and construct collection,
from the published metadata, at no API cost: a table is a BASELINE CANDIDATE
when the collection's own tokens -- its id, its label, and the alternatives of
its `cname:` rule -- appear in the table's name or in its `construct name` tag.
Candidates the collection does not contain are its misses.

WHAT IT IS NOT
--------------
It measures recall only, exactly as the review's benchmark did. A name-token
baseline cannot measure precision: it has no way to tell a table that belongs
in `phq9` from one that merely says "phq" in its name, which is why every miss
is printed rather than counted and acted on in bulk. Design collections
(`trials`, `clustered`, `response_time` ...) are excluded: their membership is
a rule over columns, where a name token means nothing. `metadata-complete`
collections are excluded for the same reason -- their rule IS their definition,
so recall against anything else is not a question.

USAGE (from src/metadata, no credentials needed)

  python3 collection_recall.py                  # the table, worst recall first
  python3 collection_recall.py --misses         # and every missed table name
  python3 collection_recall.py --collection phq9
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

#: Words that carry no instrument identity, so they cannot earn a candidate.
#: "scale", "inventory" and the like appear in hundreds of table names.
STOPWORDS = {
    "the", "and", "for", "scale", "inventory", "questionnaire", "survey",
    "test", "index", "short", "form", "brief", "revised", "version", "items",
    "item", "measure", "total", "score", "scores", "data",
    #: Words that appear in hundreds of IRW table names and in half the
    #: construct vocabulary. `self` and `general` alone took the `gse` baseline
    #: from 8 members to 355 candidates, which is not a recall measurement.
    "self", "general", "generalised", "generalized", "global", "positive",
    "negative", "child", "children", "adult", "student", "students", "study",
    "wave", "time", "pre", "post", "full", "long",
}

#: Collections whose membership is a rule over COLUMNS. A name token says
#: nothing about whether a table has a `rater` column.
SKIP_KINDS = {"design"}


def read_csv(name: str) -> list[dict]:
    path = HERE / name
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def canon(text: str) -> str:
    """Lowercase, alphanumerics only -- so `gad-7`, `GAD 7` and `gad7` match."""
    return re.sub(r"[^a-z0-9]", "", (text or "").lower())


def rule_tokens(rule: str) -> list[str]:
    """The literal alternatives of a `cname:` rule, with the regex stripped out.

    A rule is the collection's own statement of what it is looking for, so its
    alternatives are the best tokens available -- better than the id, which is
    an abbreviation, and better than the label, which is prose.
    """
    if not rule.startswith("cname:"):
        return []
    body = rule[len("cname:"):]
    body = re.sub(r"\(\?[^)]*\)", " ", body)          # (?!...) lookarounds
    out = []
    for alt in re.split(r"\|", body):
        lit = re.sub(r"\\b|\\s|[\\^$()\[\].*+?{}]", " ", alt)
        for word in lit.split():
            #: 4, not 3: a 3-character fragment of a stripped regex ("ing"
            #: out of `read|reading|spelling`) matches a third of the corpus.
            if len(word) >= 4 and word not in STOPWORDS:
                out.append(word)
    return out


def id_tokens(collection: dict) -> list[str]:
    """The collection's own id, as the instrument spells itself.

    The narrow baseline. `swls` matching the token `swls` is the scale naming
    itself; `swls` matching the word "satisfaction" in a construct tag is a
    construct, and there are 260 of those. Both numbers are worth having, so
    both are reported: the broad one bounds how much a generous reading could
    add, the narrow one is the set a maintainer can act on today.
    """
    #: The id as spelled, and nothing shorter. Splitting `bfi10` into `bfi`
    #: puts every BFI-44 table in the BFI-10 collection's candidate set, which
    #: is a different instrument: the prefix of an instrument id names a
    #: family, not the scale.
    toks = {canon(collection["collection"])}
    for tok in rule_tokens(collection.get("rule", "")):
        #: a rule alternative carrying a digit is an instrument name, not a word
        if any(ch.isdigit() for ch in tok):
            toks.add(canon(tok))
    return sorted(t for t in toks if t)


def tokens_for(collection: dict) -> list[str]:
    toks = set(rule_tokens(collection.get("rule", "")))
    for source in (collection["collection"], collection.get("label", "")):
        for word in re.split(r"[^A-Za-z0-9]+", source):
            if len(word) >= 3 and word.lower() not in STOPWORDS:
                toks.add(word.lower())
    #: An id like `bfi44` is also two tokens a table name may spell apart.
    for tok in list(toks):
        m = re.match(r"^([a-z]{2,})(\d{1,3})$", tok)
        if m:
            toks.add(m.group(1))
    return sorted(canon(t) for t in toks if canon(t))


def name_tokens(table: str) -> set[str]:
    """The table name's own tokens, plus its canonical whole form.

    Matching a token rather than a substring is what keeps an acronym honest:
    `gse` as a substring hits nothing useful, but `GSE` as one underscore-
    separated token of `GSE_Zhang_2021` is the instrument saying its own name.
    """
    parts = {p.lower() for p in re.split(r"[^A-Za-z0-9]+", table) if p}
    return parts | {canon(table)}


def matches(token: str, table: str, tag: str) -> bool:
    """Does one collection token identify this table?

    Three rules, loosest last:
      * the token IS one of the name's tokens -- an acronym, any length;
      * it is a substring of the whole canonical name, 5 characters or more --
        `vocabulary` inside `vocab_lexical_2021`;
      * it is a substring of the construct-name tag, 4 or more. The tag is
        prose written for this purpose, so a shorter token is safe there.
    """
    toks = name_tokens(table)
    if token in toks:
        return True
    if len(token) >= 5 and token in canon(table):
        return True
    return len(token) >= 4 and token in canon(tag)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--misses", action="store_true", help="print every missed table")
    ap.add_argument("--collection", help="one collection only")
    args = ap.parse_args(argv)

    collections = read_csv("collections.csv")
    members = read_csv("collection_members.csv")
    meta = read_csv("metadata.csv")
    tags = read_csv("tags.csv")

    #: Case-insensitive, because `tags.table` is all-lowercase while 295
    #: `metadata` names are mixed case -- an exact join loses those 295 (R-31).
    construct = {canon(r["table"]): (r.get("construct name") or "").lower()
                 for r in tags}
    by_collection: dict[str, set[str]] = {}
    for row in members:
        by_collection.setdefault(row["collection"], set()).add(row["table"])

    rows = []
    for coll in collections:
        if coll.get("coverage") == "metadata-complete" or coll.get("kind") in SKIP_KINDS:
            continue
        if args.collection and coll["collection"] != args.collection:
            continue
        toks = tokens_for(coll)
        if not toks:
            continue
        held = by_collection.get(coll["collection"], set())
        narrow_toks = id_tokens(coll)
        candidates, narrow = set(), set()
        for row in meta:
            tag = construct.get(canon(row["table"]), "")
            if any(matches(t, row["table"], tag) for t in toks):
                candidates.add(row["table"])
            if any(matches(t, row["table"], tag) for t in narrow_toks):
                narrow.add(row["table"])
        misses = sorted(narrow - held)
        broad_misses = sorted(candidates - held)
        recall = (len(held & candidates) / len(candidates)) if candidates else None
        recall_id = (len(held & narrow) / len(narrow)) if narrow else None
        rows.append({"collection": coll["collection"], "coverage": coll["coverage"],
                     "members": len(held), "candidates": len(candidates),
                     "narrow": len(narrow), "misses": misses,
                     "broad_misses": broad_misses,
                     "recall": recall, "recall_id": recall_id, "tokens": narrow_toks})

    rows.sort(key=lambda r: (r["recall_id"] if r["recall_id"] is not None else 2,
                             -len(r["misses"])))
    print(f"{'collection':<20}{'coverage':<19}{'members':>8}{'id-cand':>9}"
          f"{'id-miss':>9}{'id-rec':>8}{'broad-cand':>12}{'broad-rec':>11}")
    for r in rows:
        rec = "-" if r["recall"] is None else f"{r['recall']:.2f}"
        rid = "-" if r["recall_id"] is None else f"{r['recall_id']:.2f}"
        print(f"{r['collection']:<20}{r['coverage']:<19}{r['members']:>8}"
              f"{r['narrow']:>9}{len(r['misses']):>9}{rid:>8}"
              f"{r['candidates']:>12}{rec:>11}")
    total_miss = sum(len(r["misses"]) for r in rows)
    broad_miss = sum(len(r["broad_misses"]) for r in rows)
    print(f"\n{len(rows)} collection(s). {total_miss} table(s) name the "
          f"collection's own instrument and are not in it; {broad_miss} more "
          f"under the generous reading.")
    print("Recall only: a name token cannot establish that a candidate BELONGS, "
          "so read the misses rather than bulk-adding them.")
    if args.misses:
        for r in rows:
            if r["misses"]:
                print(f"\n{r['collection']} ({len(r['misses'])} missed, tokens "
                      f"{', '.join(r['tokens'])}):")
                for name in r["misses"]:
                    print(f"  {name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
