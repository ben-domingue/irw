"""Sweep the corpus for wording from instruments ruled blocking.

Ben ruled on 2026-09-08 that a blocked instrument gets a standing corpus sweep,
rather than being rediscovered one round at a time. The PSS is why: the ruling
existed from 2026-09-06 and had been applied five times, but nothing swept behind
it, so six live tables carrying Cohen's PSS-10 were still being found two days
later, one at a time.

Reads `itemtext/instrument_rights_register.csv` and reports candidate matches on
BOTH surfaces a restricted instrument can reach the corpus through:

  item_text  -- the item-text shards (irw_text, irw_text_2). A withdrawal removes
                these, so this is the surface every withdrawal so far has fixed.
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
"""
import argparse, csv, os, re, sys
from pathlib import Path

REG = Path(__file__).resolve().parent / "instrument_rights_register.csv"
TEXT_SHARDS = ("irw_text", "irw_text_2")


def load_register():
    with open(REG, newline="") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        r["_text_pat"] = [p for p in (r["match_item_text"] or "").split("|") if p]
        r["_code_re"] = re.compile(r["match_item_code"], re.I) if r["match_item_code"] else None
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", default="next", choices=("current", "next"),
                    help="which shard version to sweep; 'next' is the draft that "
                         "reflects staged withdrawals, 'current' is what is published")
    ap.add_argument("--codes-only", action="store_true")
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
        print(f"\n=== item_text surface ({args.version}) ===")
        # One query per CHUNK of tables testing every pattern at once, not one per
        # instrument: Redivis caps the tables referenced by a single query, and a
        # per-instrument sweep would also re-scan the corpus 18 times.
        pats = [(r["instrument"], p) for r in blocking for p in r["_text_pat"]]
        like = " OR ".join(
            # BigQuery uses backslash escapes; a doubled '' parses as two adjacent
            # string literals and is a syntax error, not an escaped quote.
            "LOWER(CAST(item_text AS STRING)) LIKE '%%%s%%'"
            % p.lower().replace("\\", "\\\\").replace("'", "\\'")
            for _, p in pats)
        for shard in TEXT_SHARDS:
            ds = redivis.user("datapages").dataset(shard, version=args.version)
            # qualifiedReference carries the version; a bare name would not.
            tables = {t.name: t.properties["qualifiedReference"] for t in ds.list_tables()}
            print(f"{shard} ({args.version}): {len(tables)} tables")
            names = sorted(tables)
            CHUNK = 150
            found = {}
            skipped = []
            for i in range(0, len(names), CHUNK):
                part = names[i:i + CHUNK]
                sql = "\nUNION ALL\n".join(
                    f"(SELECT '{n}' AS tbl, CAST(item AS STRING) AS item, "
                    f"CAST(item_text AS STRING) AS item_text "
                    f"FROM `{tables[n]}` WHERE {like})"
                    for n in part)
                try:
                    df = redivis.query(sql).to_pandas_dataframe()
                except Exception as exc:
                    # One malformed table (no item_text, or an odd type) must not
                    # silently drop the other 149 in its chunk -- a sweep that skips
                    # tables without saying so is the failure mode this exists to fix.
                    print(f"  chunk {i}-{i+CHUNK} failed ({str(exc)[:80]}); "
                          f"retrying table by table")
                    frames = []
                    for n in part:
                        try:
                            frames.append(redivis.query(
                                f"SELECT '{n}' AS tbl, CAST(item AS STRING) AS item, "
                                f"CAST(item_text AS STRING) AS item_text "
                                f"FROM `{tables[n]}` WHERE {like}").to_pandas_dataframe())
                        except Exception as e2:
                            skipped.append((n, str(e2)[:60]))
                    import pandas as pd
                    df = pd.concat(frames) if frames else pd.DataFrame(
                        columns=["tbl", "item", "item_text"])
                for row in df.itertuples(index=False):
                    txt = (row.item_text or "").lower()
                    for inst, p in pats:
                        if p.lower() in txt:
                            found.setdefault((row.tbl, inst), set()).add(row.item)
                            break
                print(f"  ...scanned {min(i+CHUNK, len(names))}/{len(names)}")
            # Rank by how much of the instrument is present. A single-item match on a
            # short generic stem ("I feel calm") is usually incidental -- zhou_2016_anxiety
            # is the Zung SAS and matched the STAI on exactly that. A multi-item match is
            # rarely an accident. Both are printed: a weak lead is still a lead, and the
            # sweep must not decide for the reader. But an output that buries one real hit
            # in fifteen incidental ones trains people to ignore it.
            for (tbl, inst), items in sorted(found.items(), key=lambda kv: -len(kv[1])):
                strength = "STRONG" if len(items) >= 3 else "weak  "
                print(f"  {strength} {shard}/{tbl}: {len(items)} item(s) match {inst}"
                      f" -- LEAD, read the items")
            if not found:
                print(f"  no item_text hits in {shard} ({args.version})")
            if skipped:
                print(f"  NOT SWEPT ({len(skipped)} tables could not be queried): "
                      f"{skipped[:5]}{' ...' if len(skipped) > 5 else ''}")

    print("\n=== item code surface (response tables) ===")
    print("  Not yet wired to the response shards. The two known cases are")
    print("  luu_2024_stai6 (irw#2123) and holden_2026_bsri (irw#2101); the remedy")
    print("  for a published item code is an open question, so this half must")
    print("  report only. See the register's match_item_code column.")


if __name__ == "__main__":
    main()
