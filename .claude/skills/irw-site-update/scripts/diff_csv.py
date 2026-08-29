#!/usr/bin/env python3
"""Keyed diff between a pre-run snapshot and a freshly regenerated pipeline CSV.

Used by run_pipeline.sh after every metadata/*.R stage. Never overwrites
silently: prints a human summary and writes a row-level *.diff.csv next to
the new file so changes can be reviewed (and are themselves diffable/greppable)
before anything gets pasted into Redivis.

Also carries a blunt, explicitly-labeled stopgap safeguard: flags any
added/changed cell that is suspiciously long, on the theory that a public
metadata/biblio/tags CSV should never gain a full paragraph of raw source
text. This is NOT the hash-cache / similarity-flagged / pending-review
system described for a future construct_description field -- that system
does not exist yet anywhere in this repo (confirmed by grep across metadata/,
tags/, itemtext/ on 2026-07-27). This is a length tripwire standing in for it
until something more principled is built. See references/pipeline.md.
"""
import argparse
import sys
from pathlib import Path

import pandas as pd

LONG_TEXT_WARN = 500
LONG_TEXT_FLAG = 2000


def load(path: Path, key: str) -> pd.DataFrame:
    # `key` may name several columns, comma-separated, for tables whose identity
    # needs more than one -- collection_members.csv is long, so `table` alone
    # repeats and would be silently de-duplicated into a meaningless diff.
    cols = key_cols(key)
    if path is None or not path.exists():
        return pd.DataFrame(columns=cols)
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise SystemExit(f"key column(s) {missing} not found in {path} (columns: {list(df.columns)})")
    df["_key"] = (df[cols].astype(str)
                  .apply(lambda r: "\u001f".join(v.strip().lower() for v in r), axis=1))
    n_before = len(df)
    dup_keys = df.loc[df["_key"].duplicated(), "_key"].unique().tolist()
    if dup_keys:
        df = df.drop_duplicates(subset="_key", keep="first")
        print(f"   ! {path.name}: dropped {n_before - len(df)} duplicate-key row(s) before diffing "
              f"(source CSV had >1 row for the same '{key}', e.g. {dup_keys[:5]}) "
              f"-- check the upstream source (Google Sheet fetches have been flaky today)")
    return df.set_index("_key", drop=True)


def key_cols(key: str) -> list[str]:
    return [c.strip() for c in key.split(",") if c.strip()]


def label(df: pd.DataFrame, k, key: str) -> str:
    """Human-readable identity for one row. With a composite key the key itself
    is not a column, so join the parts the way a reader would say them."""
    cols = key_cols(key)
    row = df.loc[k]
    return " / ".join(str(row[c]) for c in cols)


def label_many(df: pd.DataFrame, keys, key: str) -> list[str]:
    cols = key_cols(key)
    if len(cols) == 1:
        return df.loc[keys, cols[0]].tolist()
    return df.loc[keys, cols].apply(lambda r: " / ".join(str(v) for v in r), axis=1).tolist()


def classify_long_text(value: str) -> str | None:
    n = len(value or "")
    if n >= LONG_TEXT_FLAG:
        return f"FLAG ({n} chars) -- resembles a raw excerpt/full-text dump; verify before merging"
    if n >= LONG_TEXT_WARN:
        return f"warn ({n} chars) -- longer than expected, spot-check"
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("old_csv", type=Path, help="pre-run snapshot (may not exist for a brand-new file)")
    ap.add_argument("new_csv", type=Path, help="freshly written CSV from the R pipeline")
    ap.add_argument("--key", default="table",
                    help="join key column, or several comma-separated for a composite "
                         "key (default: table)")
    ap.add_argument("--out", type=Path, default=None, help="diff CSV path (default: <new_csv>.diff.csv)")
    args = ap.parse_args()

    if not args.new_csv.exists():
        print(f"-- {args.new_csv.name}: not produced this run (script may have found nothing new / errored)")
        return

    old = load(args.old_csv if args.old_csv and args.old_csv.exists() else None, args.key)
    new = load(args.new_csv, args.key)

    added_keys = new.index.difference(old.index)
    removed_keys = old.index.difference(new.index)
    common_keys = new.index.intersection(old.index)

    rows = []
    flags = []

    for k in added_keys:
        rows.append({"table": label(new, k, args.key), "status": "added", "column": "", "old_value": "", "new_value": ""})
        for col in new.columns:
            if col in ("_key",):
                continue
            flag = classify_long_text(new.loc[k, col])
            if flag:
                flags.append((label(new, k, args.key), col, flag))

    for k in removed_keys:
        rows.append({"table": label(old, k, args.key), "status": "removed", "column": "", "old_value": "", "new_value": ""})

    changed_keys = []
    shared_cols = [c for c in new.columns if c in old.columns and c != "_key"]
    for k in common_keys:
        row_old, row_new = old.loc[k], new.loc[k]
        changed_cols = [c for c in shared_cols if str(row_old[c]) != str(row_new[c])]
        if changed_cols:
            changed_keys.append(k)
            for col in changed_cols:
                rows.append({
                    "table": label(new, k, args.key), "status": "changed", "column": col,
                    "old_value": row_old[col], "new_value": row_new[col],
                })
                flag = classify_long_text(row_new[col])
                if flag:
                    flags.append((label(new, k, args.key), col, flag))

    diff_df = pd.DataFrame(rows, columns=["table", "status", "column", "old_value", "new_value"])
    out_path = args.out or args.new_csv.with_suffix(".diff.csv")
    diff_df.to_csv(out_path, index=False)

    print(f"-- {args.new_csv.name}")
    print(f"   added:   {len(added_keys)}")
    print(f"   removed: {len(removed_keys)}")
    print(f"   changed: {len(changed_keys)}")
    if len(added_keys):
        sample = ", ".join(sorted(label_many(new, added_keys, args.key))[:10])
        more = f" (+{len(added_keys)-10} more)" if len(added_keys) > 10 else ""
        print(f"     + {sample}{more}")
    if len(removed_keys):
        sample = ", ".join(sorted(label_many(old, removed_keys, args.key))[:10])
        more = f" (+{len(removed_keys)-10} more)" if len(removed_keys) > 10 else ""
        print(f"     - {sample}{more}")
    if flags:
        print(f"   LONG-TEXT REVIEW FLAGS: {len(flags)} cell(s) -- see {out_path.name}")
        for table, col, flag in flags[:10]:
            print(f"     ! {table} / {col}: {flag}")
        if len(flags) > 10:
            print(f"     ... (+{len(flags)-10} more)")
    print(f"   diff written: {out_path}")


if __name__ == "__main__":
    sys.exit(main())
