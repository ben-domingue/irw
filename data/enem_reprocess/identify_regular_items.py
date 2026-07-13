#!/usr/bin/env python3
"""Identify the ENEM MAIN (regular-application) items for a given year.

Principled rule (authoritative, not data-volume): the INEP microdata dictionary
(Dicionario_Microdados_Enem_YYYY.xlsx) labels every CO_PROVA value with its
booklet color, suffixing non-regular applications with "(Reaplicacao)" or
"Digital". Main items = CO_ITEMs whose CO_PROVA is a POSITIVELY-labeled regular
color (absence of a label != regular, since dicts don't enumerate every printed
variant).

Outputs, per year:
  - enem_<year>_prova_labels.csv : CO_PROVA | label | application (regular/reaplicacao/digital)
  - enem_<year>_regular_items.csv: SG_AREA | CO_ITEM  (the retained main items)
  - a printed summary (regular vs non-regular unique items per area)

Usage:
  python identify_regular_items.py --itens ITENS_PROVA_YYYY.csv --dict DICT.xlsx \
      --year YYYY --out-dir ENEM/output/regular
"""
from __future__ import annotations
import argparse, re
from pathlib import Path
import pandas as pd
import openpyxl

COLOR = re.compile(r"(azul|amarela|rosa|cinza|branca|verde|laranja)", re.I)
REAPLIC = re.compile(r"reaplic", re.I)
DIGITAL = re.compile(r"digital", re.I)


def parse_prova_labels(dict_path: Path) -> dict[int, str]:
    """Return {CO_PROVA code: label} by scanning the dictionary for adjacent
    (integer-code, color-label) cell pairs anywhere in any sheet."""
    wb = openpyxl.load_workbook(dict_path, read_only=True, data_only=True)
    code_label: dict[int, str] = {}
    for ws in wb.worksheets:
        for row in ws.iter_rows(values_only=True):
            cells = ["" if c is None else str(c).strip() for c in row]
            for i in range(len(cells) - 1):
                if re.fullmatch(r"\d{3,5}", cells[i]) and COLOR.search(cells[i + 1]):
                    # first label wins; dict lists each code once
                    code_label.setdefault(int(cells[i]), cells[i + 1])
    return code_label


ACCESSIBILITY = re.compile(
    r"amplia|superamplia|braile|braille|ledor|libras|videoprova|adaptad", re.I
)


def classify(label: str) -> str:
    if REAPLIC.search(label):
        return "reaplicacao"
    if DIGITAL.search(label):
        return "digital"
    return "regular"


def is_standard(label: str) -> bool:
    """Standard regular booklet = regular application AND a plain color
    (not an accessibility variant). Defines the clean 'main' item set."""
    return classify(label) == "regular" and not ACCESSIBILITY.search(label)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--itens", type=Path, required=True)
    ap.add_argument("--dict", type=Path, required=True)
    ap.add_argument("--year", type=int, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    args = ap.parse_args()

    code_label = parse_prova_labels(args.dict)
    labels_df = pd.DataFrame(
        [{"CO_PROVA": c, "label": l, "application": classify(l),
          "is_standard": is_standard(l)}
         for c, l in sorted(code_label.items())]
    )
    regular_codes = set(labels_df.loc[labels_df.application == "regular", "CO_PROVA"])
    standard_codes = set(labels_df.loc[labels_df.is_standard, "CO_PROVA"])

    it = pd.read_csv(args.itens, sep=";", encoding="latin-1")
    it["is_regular"] = it["CO_PROVA"].isin(regular_codes)
    it["is_standard"] = it["CO_PROVA"].isin(standard_codes)  # standard = clean main set

    args.out_dir.mkdir(parents=True, exist_ok=True)
    # prova codes file consumed by reprocess_enem.R
    labels_df.to_csv(args.out_dir / f"enem_{args.year}_prova_codes.csv", index=False)
    # the clean MAIN item set = items in STANDARD regular booklets
    main_items = (it[it.is_standard][["SG_AREA", "CO_ITEM"]]
                  .drop_duplicates().sort_values(["SG_AREA", "CO_ITEM"]))
    main_items.to_csv(args.out_dir / f"enem_{args.year}_main_items.csv", index=False)

    print(f"\n=== ENEM {args.year} — CO_PROVA labels: "
          f"{len(code_label)} labeled | standard={len(standard_codes)} "
          f"regular={len(regular_codes)} "
          f"reaplic={ (labels_df.application=='reaplicacao').sum() } "
          f"digital={ (labels_df.application=='digital').sum() } ===")
    cov = round(it['CO_PROVA'].isin(code_label).mean(), 3)
    print(f"ITENS CO_PROVA covered by dict: {cov}"
          + ("   *** LOW COVERAGE — verify dict parse / use majority fallback"
             if cov < 0.2 else ""))
    print("\nMain (standard) unique CO_ITEM per area:")
    for area in ["LC", "CH", "CN", "MT"]:
        a = it[it.SG_AREA == area]
        std = a[a.is_standard].CO_ITEM.nunique()
        reg = a[a.is_regular].CO_ITEM.nunique()
        print(f"  {area}: main(standard)={std:3d} | regular(all)={reg:3d} "
              f"| total={a.CO_ITEM.nunique():3d}")


if __name__ == "__main__":
    main()
