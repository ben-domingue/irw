#!/usr/bin/env python3
"""Item text for oliveira_2026_healthcare_experiences (figshare 33716635). Stems and option labels come from
the workbook's Codebook sheet, keyed by column name. The study was administered in Portuguese (Brazilian
adults) and the deposit carries only the English codebook wording, so item_text / option_text are left
blank and the English goes in the _translated columns (same handling as sakal_2026_ai_resistance)."""
from _itemtext_writer_c import load_script, row, write

mod = load_script("oliveira_2026_weight_stigma")


def main():
    cb = mod.codebook()
    table = "oliveira_2026_healthcare_experiences"
    rows = []
    for c in mod.EXP:
        stem, opts = cb[c]
        for r, opt in sorted(opts.items()):
            rows.append(row(table, f"{table}_1", c, "Healthcare experiences and experienced weight stigma inventory, 11 items",
                            "Portuguese", r, "", option_text="", item_text_tr=stem, option_text_tr=opt))
    write(table, rows)


if __name__ == "__main__":
    main()
