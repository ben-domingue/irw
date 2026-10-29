"""
Four instruments answered by 711 Turkish university students: metacognitive
awareness, digital wellbeing, cognitive flexibility and digital literacy.

Source: Akkus Cutuk, Z. (2025). The Serial Mediating Role of Cognitive
        Flexibility and Digital Literacy in the Relationship Between
        Metacognitive Awareness and Digital Wellbeing [Dataset]. Zenodo.
DOI: 10.5281/zenodo.15855531
Data: https://zenodo.org/records/15855531 (the single file
        "Mart25-UZERINDE CALISILAN_SON.sav")
License: CC BY 4.0 (verified on the Zenodo record, metadata.license.id
        "cc-by-4.0")
Item text: NOT shipped. The `.sav` carries NO variable labels at all -- 0 of
        78 -- so there are no item stems. It DOES carry each block's Turkish
        response anchors as value labels, and those are recorded in
        `itemtext_provenance.csv`, but anchors with no stem is option_text
        alone, which irw#1770 forbids. Where to look: the article this deposit
        supports; the Zenodo record carries no related identifier, and the
        deposit names none of the four instruments, so a later pass must
        identify them from the article before a rights question can be asked.

**The four tables are the four blocks, and each block's own anchor set is what
separates them -- not a guess from the prefix.** All four happen to run 1-5,
but they are four different scales and the file says so: `ÜSTB` is anchored
"Hiçbir zaman" (never) to always, `DİO` "Hiç yansıtmıyor" (does not reflect me
at all), `BES` "Hiç uygun değil" (not at all suitable) and `DOKY` "Kesinlikle
Katılmıyorum" (strongly disagree). Four distinct anchor sets means four
instruments, so four tables, which is what `datastandard.md` asks for.

The item codes keep each block's own prefix and numbering (`üstb1`..`üstb18`),
so an item stays traceable to the deposit's column.

Dropped as derived: `kisiselfarkındalık`, `organizasyonefarkındalık`,
`yargısalfarkındalık` and `ÜSTBILISSELFARKINDALIK` are the metacognition
subscale and total scores; `DIJITALOKURYAZARLIKTOPLAM`, `dıjıtalokuryazarlık1`
and `dıjıtalokuryazarlık2` are digital-literacy totals and halves;
`DIJITALIYIOLUSTOPLAM`, `Dıjıtaltatmın`, `guvenlivesorunludavranıs` and
`dijitalrefah` are the digital-wellbeing total and its subscales;
`BILISSELESNEKLIKTOPLAM`, `kontrol` and `Alternatiflar` are the
cognitive-flexibility total and its subscales. `sira` is the deposit's own row
serial, which runs 2-712 over 711 rows -- i.e. it is not a clean index either
-- and `id` is assigned here instead.

PII: none. Every column is numeric, there is no identifier, and no name, date,
free-text or geographic column; the screen below prints its denominator.

Output: four tables, 42,660 responses -- 711 students, 60 items.
  * akkus_cutuk_2025_cognitive_flexibility -- 20 items, resp 1-5
  * akkus_cutuk_2025_metacognitive_awareness -- 18 items, resp 1-5
  * akkus_cutuk_2025_digital_wellbeing     -- 12 items, resp 1-5
  * akkus_cutuk_2025_digital_literacy      -- 10 items, resp 1-5
"""
from __future__ import annotations

from pathlib import Path
import re
import sys

import pandas as pd
import pyreadstat

SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("Mart25.sav")
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(".")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

PERMITTED = [1, 2, 3, 4, 5]

# table -> (source prefix, item count, the first anchor the block's value
# labels must carry). The anchor check is what establishes these are four
# instruments rather than one battery split on a prefix.
BLOCKS = {
    "akkus_cutuk_2025_metacognitive_awareness": ("ÜSTB", 18, "Hiçbir zaman"),
    "akkus_cutuk_2025_digital_wellbeing": ("DİO", 12, "Hiç yansıtmıyor"),
    "akkus_cutuk_2025_cognitive_flexibility": ("BES", 20, "Hiç uygun değil"),
    "akkus_cutuk_2025_digital_literacy": ("DOKY", 10, "Kesinlikle Katılmıyorum"),
}

COV_MAP = {
    "sinif": "cov_year_group",
    "yas": "cov_age",
    "cinsiyet": "cov_sex",
}

DROP_PATTERNS = [
    (r"^sira$", "the deposit's own row serial (2-712 over 711 rows, so not a "
                "clean index); id is assigned here instead"),
    (r"farkındalık|FARKINDALIK", "a metacognition subscale or total score"),
    (r"OKURYAZARLIKTOP|okuryazarlık\d", "a digital-literacy total or half"),
    (r"IYIOLUSTOPLAM|tatmın|guvenlive|dijitalrefah",
     "the digital-wellbeing total or one of its subscales"),
    (r"ESNEKLIKTOPLAM|^kontrol$|^Alternatiflar$",
     "the cognitive-flexibility total or one of its subscales"),
]


def pii_screen(df: pd.DataFrame) -> None:
    text_cols = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: examined {len(text_cols)} string column(s) of "
          f"{len(df.columns)}; dtypes present: "
          f"{sorted({str(t) for t in df.dtypes})}")
    assert len(df.columns) > 0
    assert not text_cols, f"unexpected text column(s): {text_cols}"


def main() -> None:
    df, meta = pyreadstat.read_sav(SRC)
    print("raw shape", df.shape)
    pii_screen(df)
    assert len(df) == 711, len(df)

    labelled = sum(1 for c in df.columns
                   if (meta.column_names_to_labels.get(c) or "").strip())
    print(f"variable labels present: {labelled} of {len(df.columns)}; "
          f"value-labelled variables: {len(meta.variable_value_labels)} -- "
          "anchors but no stems, so no item text can be recovered here")
    assert labelled == 0

    item_cols = {}
    for table, (prefix, n, first_anchor) in BLOCKS.items():
        cols = sorted((c for c in df.columns
                       if re.match(rf"^{re.escape(prefix)}\d+$", c)),
                      key=lambda c: int(re.sub(r"\D", "", c)))
        assert len(cols) == n, (table, len(cols), n, cols)
        labels = meta.variable_value_labels.get(cols[0]) or {}
        assert labels, f"{cols[0]} has no value labels"
        assert sorted(int(k) for k in labels) == PERMITTED, (table, labels)
        assert labels[1.0].strip() == first_anchor, \
            f"{table}: anchor 1 is {labels[1.0]!r}, expected {first_anchor!r}"
        print(f"{table}: {n} items, anchors {labels[1.0]!r}..{labels[5.0]!r}")
        item_cols[table] = cols

    df = df.reset_index(drop=True)
    df["id"] = range(1, len(df) + 1)
    for src, dst in COV_MAP.items():
        assert src in df.columns, src
        df[dst] = df[src]
    covs = list(COV_MAP.values())

    accounted = set(COV_MAP) | set(covs) | {"id"}
    accounted |= {c for cs in item_cols.values() for c in cs}
    dropped = {}
    for c in df.columns:
        if c in accounted:
            continue
        for pat, why in DROP_PATTERNS:
            if re.search(pat, c):
                dropped[c] = why
                break
    leftover = [c for c in df.columns
                if c not in accounted and c not in dropped]
    assert not leftover, f"unaccounted source columns: {leftover}"
    for why in sorted(set(dropped.values())):
        cs = sorted(c for c, w in dropped.items() if w == why)
        print(f"skipped {len(cs)} column(s) -- {why}: {cs}")

    for table, cols in item_cols.items():
        write(df, table, cols, covs)


def write(df: pd.DataFrame, table: str, cols: list, covs: list) -> None:
    codes = {c: c.lower() for c in cols}
    assert len(set(codes.values())) == len(cols), codes
    long = df[["id"] + covs + cols].rename(columns=codes)
    long = long.melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
    before = long["resp"].notna().sum()
    long = long[long["resp"].isin(PERMITTED)]
    assert before == len(long), \
        f"{table}: {before - len(long)} cell(s) outside {PERMITTED}"

    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + covs].sort_values(
        ["id", "item"]).reset_index(drop=True)

    checks = run_qc(long, permitted_values=PERMITTED)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, (table, fails)
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {table} {c.name}: {c.detail[:180]}")
    long.to_csv(OUT / f"{table}.csv", index=False)
    print(f"  -> {table}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={sorted(long['resp'].unique())}")


if __name__ == "__main__":
    main()
