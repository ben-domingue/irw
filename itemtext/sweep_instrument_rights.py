"""Sweep the corpus for wording from instruments ruled non-shipping.

Non-shipping is `block` or `hold`. A block rests on a located clause or a settled
rule; a hold records that the search for a grant came up empty and names what
would resolve it. Neither ships, so both are swept.

Ben ruled on 2026-09-08 that a blocked instrument gets a standing corpus sweep,
rather than being rediscovered one round at a time. The PSS is why: the ruling
existed from 2026-09-06 and had been applied five times, but nothing swept behind
it, so six live tables carrying Cohen's PSS-10 were still being found two days
later, one at a time.

Reads `itemtext/instrument_rights_register.csv` and reports candidate matches on
BOTH surfaces a restricted instrument can reach the corpus through:

  item_text  -- every item-text shard in IRW_TEXT_DATASETS. A withdrawal removes
                these, so this is the surface every withdrawal so far has fixed.
  *_translated -- the same shards' item_text_translated, option_text_translated,
                instructions_translated and section_prompt_translated, where a table
                carries them. Ben ruled 2026-09-29 (irw#2401) that a block row covers
                these too: beck_2021_iesr shipped German IES-R in item_text, which no
                stem matches, and Weiss & Marmar's English IES-R in
                item_text_translated. Hits are labelled by column, and a hit on a
                table whose item_text did not match the same instrument is marked NEW.
  item code  -- the RESPONSE tables. A processing script that uses source column
                headers as item codes carries the instrument into data that no
                item-text withdrawal reaches: luu_2024_stai6 ships the six STAI-6
                stems as item codes (irw#2123), holden_2026_bsri the 20 BSRI
                adjectives (irw#2101). Renaming a published item code is neither
                cheap nor reversible, so this half REPORTS and never acts. It
                applies the write-path gate's own thresholds, imported from
                irw_validate.rights rather than restated, so a `match_item_code`
                pattern means the same thing here and before an upload. Wired
                2026-10-19; it printed "not yet wired" until then, while the
                docstring already advertised it -- and `--codes-only` did
                nothing at all. The corpus is ~6,700 response tables, so pilot
                with `--codes-shard item_response_warehouse_3` before running
                the lot.

============================ READ THIS BEFORE TRUSTING THE OUTPUT ============================

**A hit is a lead, never a verdict.** Three name-or-pattern searches in one session
produced a false positive each time: alkouri_2025_icu_stressors is Sheu et al. (1997)
and not the PSS; sun_2025_morality_study{1,2}_meaning are PERMA-Profiler and not the
MLQ; three of five DJG leads were UCLA/ULS-8/Asher scales. Read the items.

**A miss is not an all-clear.** The counts this produces are LOWER BOUNDS. On the PSS
sweep a substring matcher scored three complete tables at 9 of 10, because those
administrations read "things THAT HAPPENED that were outside of your control"; and
scored kfcovid_pss_li2020 at 1 of 4 because its items are negated rewordings ("felt
you LACK confidence", "things were NOT going your way") with an embedded newline.
All four were complete reproductions. Never decide "fragment or whole instrument"
from a pattern count.

**Wording that differs from canonical is still covered.** dopmeijer_2022_loneliness
matched 0 of 11 canonical DJG strings -- it carried the study's own back-rendering of
the Dutch -- and was withdrawn anyway, because the DJG's no-derivatives clause reaches
a rendering. So a table whose wording merely resembles a blocked instrument needs a
ruling, not a dismissal.

**Version scoping.** Table references are resolved through each version's own
`qualifiedReference`, NOT built as `datapages.<shard>.<table>`. A fully-qualified
bare name in a Redivis query IGNORES the dataset object's `version=` scope and
silently reads the PUBLISHED shard: during the PSS sweep that made a correctly
remediated draft table (87 rows) read as unremediated (137 rows). Any draft check
written as a bare-name query has been measuring the wrong version.
=============================================================================================

Read-only. Reports; never deletes.

Usage:
    python3 itemtext/sweep_instrument_rights.py [--version current|next] [--codes-only]
                                                [--csv hits.csv]
"""
import argparse, csv, os, re, sys
from pathlib import Path

REG = Path(__file__).resolve().parent / "instrument_rights_register.csv"

# One stem matcher for the sweep and the write-path check, so a `^stem$` anchor
# (irw#2544) means the same thing in both.
_SRC = str(Path(__file__).resolve().parents[1])
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)
from irw_validate.rights import (MIN_CODE_HITS, MIN_CODE_SHARE,  # noqa: E402
                                 stem_core, stem_hit)


def text_shard_names():
    """Every item-text shard, read from metadata/redivis_config.R.

    Not a hardcoded tuple: one naming irw_text and irw_text_2 would silently stop
    sweeping the moment irw_text_3 took tables.
    """
    src = str(Path(__file__).resolve().parents[1])
    if src not in sys.path:
        sys.path.insert(0, src)
    from red_up.targets import load_registry, text_shards
    return tuple(t.name for t in text_shards(load_registry()[1]))


def core_shard_names():
    """The response shards, from the same registry the uploader reads.

    Not a hardcoded tuple, for the reason text_shard_names() gives: a list
    naming shards 1-6 would silently stop sweeping the day shard 7 went live,
    and shard 7 is where 333 tables landed on 2026-10-18.
    """
    src = str(Path(__file__).resolve().parents[1])
    if src not in sys.path:
        sys.path.insert(0, src)
    from red_up.targets import load_registry
    owner, targets = load_registry()
    return owner, [t.name for t in targets
                   if not (t.is_itemtext or t.is_meta or t.is_conj or t.is_rank)]


def load_register():
    with open(REG, newline="") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        r["_text_pat"] = [p for p in (r["match_item_text"] or "").split("|") if p]
        r["_code_re"] = re.compile(r["match_item_code"], re.I) if r["match_item_code"] else None
    return rows


#: Verdicts whose wording must not be in the corpus. See the register's own
#: vocabulary note in the irw-auto-itemtext SKILL.
NONSHIPPING = ("block", "hold")

TRANSLATED = ("item_text_translated", "option_text_translated",
              "instructions_translated", "section_prompt_translated")


def translated_columns(tlist):
    """table name -> the *_translated columns it carries. One list_variables call
    per table, four threads (Redivis 429s above that)."""
    from concurrent.futures import ThreadPoolExecutor
    import time

    def cols(t):
        for attempt in range(5):
            try:
                return t.name, {v.name for v in t.list_variables()} & set(TRANSLATED)
            except Exception:
                time.sleep(2 ** attempt)
        return t.name, None           # unknown: reported, never assumed empty
    with ThreadPoolExecutor(max_workers=4) as pool:
        out = dict(pool.map(cols, tlist))
    unknown = sorted(n for n, c in out.items() if c is None)
    if unknown:
        print(f"  WARNING: could not list variables for {len(unknown)} table(s); their "
              f"*_translated columns are NOT swept: {unknown[:5]}")
    return {n: (c or set()) for n, c in out.items()}


def scan(redivis, tables, names, col, pats):
    """Chunked LIKE scan of one text column. Returns ({(tbl, family, instrument):
    {item}}, [skipped])."""
    like = " OR ".join(
        # BigQuery uses backslash escapes; a doubled '' parses as two adjacent
        # string literals and is a syntax error, not an escaped quote.
        "LOWER(txt) LIKE '%%%s%%'"
        % stem_core(p).lower().replace("\\", "\\\\").replace("'", "\\'")
        for _, _, p in pats)
    # The filter is applied ONCE, outside the union. Repeating it per table (the
    # pre-2026-09-29 shape) passed Redivis's 1,000,000-character query cap once
    # the register reached ~80 blocking rows, and every chunk fell back to one
    # query per table.
    one = lambda n: (f"SELECT '{n}' AS tbl, CAST(item AS STRING) AS item, "
                     f"CAST({col} AS STRING) AS txt FROM `{tables[n]}`")
    sel = lambda ns: (f"SELECT tbl, item, txt FROM ("
                      + "\nUNION ALL\n".join(one(n) for n in ns) + f") WHERE {like}")
    CHUNK = 150
    found, skipped = {}, []
    for i in range(0, len(names), CHUNK):
        part = names[i:i + CHUNK]
        try:
            df = redivis.query(sel(part)).to_pandas_dataframe()
        except Exception as exc:
            # One malformed table (no such column, or an odd type) must not
            # silently drop the other 149 in its chunk -- a sweep that skips
            # tables without saying so is the failure mode this exists to fix.
            print(f"  [{col}] chunk {i}-{i+CHUNK} failed ({str(exc)[:80]}); "
                  f"retrying table by table")
            frames = []
            for n in part:
                try:
                    frames.append(redivis.query(sel([n])).to_pandas_dataframe())
                except Exception as e2:
                    skipped.append((n, col, str(e2)[:60]))
            import pandas as pd
            df = pd.concat(frames) if frames else pd.DataFrame(columns=["tbl", "item", "txt"])
        for row in df.itertuples(index=False):
            txt = (row.txt or "").lower()
            for inst, fam, p in pats:
                if stem_hit(p, txt):     # LIKE is a superset for `^stem$`
                    found.setdefault((row.tbl, fam, inst), set()).add(row.item)
                    break
        print(f"  [{col}] scanned {min(i+CHUNK, len(names))}/{len(names)}")
    # Rank by how much of the instrument is present. A single-item match on a
    # short generic stem ("I feel calm") is usually incidental -- zhou_2016_anxiety
    # is the Zung SAS and matched the STAI on exactly that. A multi-item match is
    # rarely an accident. Both are printed: a weak lead is still a lead, and the
    # sweep must not decide for the reader.
    return found, skipped


#: Regex constructs RE2 has no equivalent for, so BigQuery refuses them.
RE2_UNSAFE = re.compile(r"\(\?[=!<(]|\\[1-9]")


def re2_probe(redivis, srcs) -> bool:
    """Does BigQuery accept this alternation? One query, no table touched."""
    combined = "|".join(f"(?:{x})" for x in srcs)
    try:
        redivis.query(
            f'SELECT REGEXP_CONTAINS("probe", r"(?i)({combined})") AS ok'
        ).to_pandas_dataframe()
        return True
    except Exception:
        return False


def re2_accepts(redivis, usable):
    """Split `usable` into (accepted, [(instrument, pattern) rejected]).

    Bisects on a failure rather than probing 99 patterns one at a time: the
    normal case is one probe, and a corpus with one bad pattern costs about
    log2(n) more.
    """
    if not usable or re2_probe(redivis, [u[2] for u in usable]):
        return usable, []
    if len(usable) == 1:
        return [], [(usable[0][0], usable[0][2])]
    mid = len(usable) // 2
    left_ok, left_bad = re2_accepts(redivis, usable[:mid])
    right_ok, right_bad = re2_accepts(redivis, usable[mid:])
    return left_ok + right_ok, left_bad + right_bad


def code_scan(redivis, tables, names, pats):
    """Chunked scan of `item` in response tables. Returns ({(tbl, family,
    instrument): {code}}, {tbl: n_codes}, [skipped], [capped]).

    The regex is pushed down to the query and re-tested here, because what comes
    back must be attributed to an instrument and Python's `re` is what the
    register's patterns were written against. A pattern RE2 rejects is reported
    as not swept rather than dropped -- the thing this script exists to prevent
    is a sweep that skips something without saying so.
    """
    import re as _re
    usable, unsweepable = [], []
    for inst, fam, src in pats:
        # A double quote would close the r"..." literal the pattern is pushed
        # down inside. Backslash escapes are fine there and in RE2. A lookaround
        # or backreference is not: RE2 has no equivalent, and because the
        # patterns go down as ONE alternation, a single unparseable row takes
        # the whole sweep with it -- the PID5 row's `^pid5(?!bf)` skipped all
        # 957 tables of the 2026-10-19 pilot before this screen existed.
        if '"' in src or RE2_UNSAFE.search(src):
            unsweepable.append((inst, src))
            continue
        usable.append((inst, fam, src, _re.compile(src, _re.I)))
    if not usable:
        return {}, {}, [], []
    # Then prove it, because the screen above cannot know everything RE2 refuses.
    usable, rejected = re2_accepts(redivis, usable)
    unsweepable += rejected
    if unsweepable:
        # Leading newline: the probe query draws a progress bar with no newline
        # of its own, which otherwise swallows this line.
        print(f"\n  {len(unsweepable)} pattern(s) cannot be pushed down and are "
              f"NOT swept on this surface: "
              f"{[i for i, _ in unsweepable]}")
        print("  (their text surface still runs; a code pattern RE2 rejects has "
              "to be\n   rewritten without the lookaround to be sweepable)")
    if not usable:
        return {}, {}, [], []
    combined = "|".join(f"(?:{src})" for _, _, src, _ in usable)
    # One scan per table: the exact count of matching codes decides the
    # thresholds, and a capped sample of them carries the attribution. Capping
    # the sample keeps a word-list table from returning thousands of codes.
    SAMPLE = 60
    one = lambda n: (
        f"SELECT '{n}' AS tbl, COUNT(DISTINCT CAST(item AS STRING)) AS n_codes, "
        f"COUNT(DISTINCT IF(REGEXP_CONTAINS(CAST(item AS STRING), "
        f'r"(?i)({combined})"), CAST(item AS STRING), NULL)) AS n_hits, '
        f"ARRAY_TO_STRING(ARRAY_AGG(DISTINCT IF(REGEXP_CONTAINS("
        f'CAST(item AS STRING), r"(?i)({combined})"), CAST(item AS STRING), NULL) '
        f'IGNORE NULLS LIMIT {SAMPLE}), "\\u0001") AS hits '
        f"FROM `{tables[n]}`")
    sel = lambda ns: "\nUNION ALL\n".join(one(n) for n in ns)
    CHUNK = 40
    found, n_codes, skipped, capped = {}, {}, [], []
    for i in range(0, len(names), CHUNK):
        part = names[i:i + CHUNK]
        try:
            df = redivis.query(sel(part)).to_pandas_dataframe()
        except Exception as exc:
            print(f"  [item] chunk {i}-{i+CHUNK} failed ({str(exc)[:80]}); "
                  f"retrying table by table")
            frames = []
            for n in part:
                try:
                    frames.append(redivis.query(sel([n])).to_pandas_dataframe())
                except Exception as e2:
                    skipped.append((n, "item", str(e2)[:60]))
            import pandas as pd
            df = (pd.concat(frames) if frames
                  else pd.DataFrame(columns=["tbl", "n_codes", "n_hits", "hits"]))
        for row in df.itertuples(index=False):
            n_codes[row.tbl] = int(row.n_codes or 0)
            if not row.n_hits:
                continue
            sample = [c for c in (row.hits or "").split("\u0001") if c]
            if int(row.n_hits) > len(sample):
                capped.append((row.tbl, int(row.n_hits)))
            for inst, fam, _src, rx in usable:
                m = [c for c in sample if rx.search(c)]
                if m:
                    found.setdefault((row.tbl, fam, inst), set()).update(m)
        print(f"  [item] scanned {min(i+CHUNK, len(names))}/{len(names)}")
    return found, n_codes, skipped, capped


def report_codes(found, n_codes, capped, verdict_of):
    """Apply the gate's thresholds and print what survives them.

    MIN_CODE_HITS / MIN_CODE_SHARE are imported, not restated: they were
    measured over 861 legacy tables (2026-09-27), where any-match flagged 308
    and the thresholds flag 59. A sweep with its own looser rule would reopen
    exactly that noise and would disagree with the write path about what a
    pattern means.
    """
    rows = []
    for (tbl, fam, inst), codes in found.items():
        total = n_codes.get(tbl, 0)
        if len(codes) < min(MIN_CODE_HITS, total or MIN_CODE_HITS) or \
                len(codes) < MIN_CODE_SHARE * total:
            continue
        rows.append((len(codes), total, tbl, fam, inst, sorted(codes)))
    for n, total, tbl, fam, inst, codes in sorted(rows, key=lambda r: -r[0]):
        print(f"  LEAD {tbl}: {n} of {total} item code(s) match {inst} "
              f"[{verdict_of.get(inst, '?')}] -- {', '.join(codes[:6])}"
              f"{' ...' if len(codes) > 6 else ''}")
    print(f"  {len(rows)} table(s) over the gate's thresholds "
          f"({MIN_CODE_HITS}+ codes and {MIN_CODE_SHARE:.0%} of the table's codes), "
          f"from {len(found)} raw pattern hit(s)")
    if capped:
        print(f"  {len(capped)} table(s) matched more codes than the sample "
              f"carries, so their attribution is partial: {capped[:5]}")
    print("  Response data from a restricted instrument ships; its WORDING does")
    print("  not. A lead here means: are these codes the instrument's wording?")
    print("  `pss1..pss10` is not; luu_2024_stai6's six STAI stems were. Renaming")
    print("  a published code is neither cheap nor reversible, so this half")
    print("  reports and never acts.")
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", default="next", choices=("current", "next"),
                    help="which shard version to sweep; 'next' is the draft that "
                         "reflects staged withdrawals, 'current' is what is published")
    ap.add_argument("--codes-only", action="store_true",
                    help="skip the text surface and sweep item codes only")
    ap.add_argument("--no-codes", action="store_true",
                    help="skip the item-code surface")
    ap.add_argument("--codes-shard", action="append", default=[],
                    metavar="NAME",
                    help="sweep codes in this response shard only (repeatable); "
                         "the whole corpus is ~6,700 tables, so pilot on one")
    ap.add_argument("--csv", help="also write every text-surface hit to this CSV")
    args = ap.parse_args()

    reg = load_register()
    # `hold` is swept alongside `block`: both mean the wording does not ship, so
    # both need finding wherever they already reached the corpus. They differ in
    # evidence, not in effect -- a block rests on a located clause, a hold records
    # that the search came up empty -- which is why only blocks are audited for a
    # transcribed clause below. A hold with no clause is correct, not a gap.
    blocking = [r for r in reg if r["verdict"] in NONSHIPPING]
    verdict_of = {r["instrument"]: r["verdict"] for r in blocking}
    n_hold = sum(1 for r in blocking if r["verdict"] == "hold")
    print(f"register: {len(reg)} instruments, {len(blocking)} ruled non-shipping "
          f"({len(blocking) - n_hold} block, {n_hold} hold)")
    unauditable = [r["instrument"] for r in blocking
                   if r["verdict"] == "block" and not r["clause"]]
    if unauditable:
        print(f"WARNING: {len(unauditable)} blocking rows carry no transcribed clause and are "
              f"NOT auditable: {unauditable}")

    sys.path.insert(0, "/home/ben/Dropbox/projects/irw/src")
    import irw_secrets
    # The WRITE token is required to SEE the draft at all -- a read token is blind
    # to `next`. This script never writes; it deletes nothing and uploads nothing.
    os.environ["REDIVIS_API_TOKEN"] = irw_secrets.load_write_token("sweep_instrument_rights")
    import redivis

    if not args.codes_only:
        print(f"\n=== item_text + *_translated surface ({args.version}) ===")
        # One query per CHUNK of tables testing every pattern at once, not one per
        # instrument: Redivis caps the tables referenced by a single query, and a
        # per-instrument sweep would also re-scan the corpus 18 times.
        pats = [(r["instrument"], r["family"], p) for r in blocking for p in r["_text_pat"]]
        hits = []          # (shard, table, family, instrument, column, items)
        for shard in text_shard_names():
            ds = redivis.user("datapages").dataset(shard, version=args.version)
            # qualifiedReference carries the version; a bare name would not.
            tlist = ds.list_tables()
            tables = {t.name: t.properties["qualifiedReference"] for t in tlist}
            print(f"{shard} ({args.version}): {len(tables)} tables")
            # Ben ruled 2026-09-29 (irw#2401) that a block row covers the
            # *_translated columns too, so they are a surface of their own: the
            # 2026-09-01 language backfill put publisher English (Weiss & Marmar's
            # IES-R, for one) beside administered wording that the item_text half
            # never matches. Which tables carry which columns is read per table,
            # because a UNION over a column a table lacks fails the whole chunk.
            tcols = translated_columns(tlist)
            n_tr = sum(1 for c in tcols.values() if c)
            print(f"  {n_tr} table(s) carry *_translated columns")
            surfaces = [("item_text", sorted(tables))]
            for col in TRANSLATED:
                surfaces.append((col, sorted(n for n, c in tcols.items() if col in c)))
            skipped = []
            found_any = False
            for col, names in surfaces:
                found, sk = scan(redivis, tables, names, col, pats)
                skipped += sk
                for (tbl, fam, inst), items in sorted(found.items(), key=lambda kv: -len(kv[1])):
                    found_any = True
                    hits.append((shard, tbl, fam, inst, col, sorted(items)))
                    strength = "STRONG" if len(items) >= 3 else "weak  "
                    print(f"  {strength} {shard}/{tbl} [{col}]: {len(items)} item(s) match {inst}"
                          f" [{verdict_of[inst]}] -- LEAD, read the items")
            if not found_any:
                print(f"  no hits in {shard} ({args.version})")
            if skipped:
                print(f"  NOT SWEPT ({len(skipped)} table/column scans could not be queried): "
                      f"{skipped[:5]}{' ...' if len(skipped) > 5 else ''}")
        # A translated-column hit on a table whose item_text did NOT match the same
        # instrument is what the item_text-only sweep could never see.
        base = {(s, t, i) for s, t, _, i, c, _ in hits if c == "item_text"}
        for h in hits:
            if h[4] != "item_text":
                print(f"  {'NEW' if (h[0], h[1], h[3]) not in base else 'also'}: "
                      f"{h[0]}/{h[1]} [{h[4]}] {h[2]}")
        if args.csv:
            with open(args.csv, "w", newline="") as fh:
                w = csv.writer(fh)
                w.writerow(["shard", "table", "family", "instrument", "verdict",
                            "column", "n_items", "items", "new_via_translated"])
                for s, t, fam, inst, col, items in hits:
                    w.writerow([s, t, fam, inst, verdict_of[inst], col, len(items),
                                ";".join(items),
                                col != "item_text" and (s, t, inst) not in base])
            print(f"wrote {len(hits)} hit(s) to {args.csv}")

    if args.no_codes:
        print("\n=== item code surface: SKIPPED (--no-codes) ===")
        return
    print(f"\n=== item code surface, response tables ({args.version}) ===")
    pats = [(r["instrument"], r["family"], r["match_item_code"])
            for r in blocking if r["match_item_code"]]
    print(f"  {len(pats)} of {len(blocking)} non-shipping rows carry a code pattern; "
          f"the other {len(blocking) - len(pats)} cannot be swept on this surface")
    owner, shards = core_shard_names()
    if args.codes_shard:
        unknown = [s for s in args.codes_shard if s not in shards]
        if unknown:
            print(f"  no such response shard: {unknown} (have {shards})")
            return
        shards = args.codes_shard
    all_found, all_codes, all_skipped, all_capped = {}, {}, [], []
    for shard in shards:
        ds = redivis.organization(owner).dataset(shard, version=args.version)
        tlist = ds.list_tables(max_results=2000)
        tables = {t.name: t.properties["qualifiedReference"] for t in tlist}
        print(f"{shard} ({args.version}): {len(tables)} tables")
        found, n_codes, skipped, capped = code_scan(
            redivis, tables, sorted(tables), pats)
        all_found.update(found)
        all_codes.update(n_codes)
        all_skipped += skipped
        all_capped += capped
    rows = report_codes(all_found, all_codes, all_capped, verdict_of)
    if all_skipped:
        print(f"  NOT SWEPT ({len(all_skipped)} table(s) could not be queried): "
              f"{all_skipped[:5]}{' ...' if len(all_skipped) > 5 else ''}")
    if args.csv and rows:
        out = args.csv.rsplit(".", 1)
        path = f"{out[0]}_codes.{out[1]}" if len(out) == 2 else f"{args.csv}_codes"
        with open(path, "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["table", "family", "instrument", "verdict", "n_hits",
                        "n_codes", "codes"])
            for n, total, tbl, fam, inst, codes in rows:
                w.writerow([tbl, fam, inst, verdict_of.get(inst, ""), n, total,
                            ";".join(codes)])
        print(f"wrote {len(rows)} code lead(s) to {path}")


if __name__ == "__main__":
    main()
