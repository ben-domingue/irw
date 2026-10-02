"""Sweep the corpus for wording from instruments ruled blocking.

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
                cheap nor reversible, so this half REPORTS and never acts.

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
from irw_validate.rights import stem_core, stem_hit  # noqa: E402


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


def load_register():
    with open(REG, newline="") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        r["_text_pat"] = [p for p in (r["match_item_text"] or "").split("|") if p]
        r["_code_re"] = re.compile(r["match_item_code"], re.I) if r["match_item_code"] else None
    return rows


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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", default="next", choices=("current", "next"),
                    help="which shard version to sweep; 'next' is the draft that "
                         "reflects staged withdrawals, 'current' is what is published")
    ap.add_argument("--codes-only", action="store_true")
    ap.add_argument("--csv", help="also write every text-surface hit to this CSV")
    args = ap.parse_args()

    reg = load_register()
    blocking = [r for r in reg if r["verdict"] == "block"]
    print(f"register: {len(reg)} instruments, {len(blocking)} ruled blocking")
    unauditable = [r["instrument"] for r in blocking if not r["clause"]]
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
                          f" -- LEAD, read the items")
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
                w.writerow(["shard", "table", "family", "instrument", "column",
                            "n_items", "items", "new_via_translated"])
                for s, t, fam, inst, col, items in hits:
                    w.writerow([s, t, fam, inst, col, len(items), ";".join(items),
                                col != "item_text" and (s, t, inst) not in base])
            print(f"wrote {len(hits)} hit(s) to {args.csv}")

    print("\n=== item code surface (response tables) ===")
    print("  Not yet wired to the response shards. The two known cases are")
    print("  luu_2024_stai6 (irw#2123) and holden_2026_bsri (irw#2101); the remedy")
    print("  for a published item code is an open question, so this half must")
    print("  report only. See the register's match_item_code column.")


if __name__ == "__main__":
    main()
