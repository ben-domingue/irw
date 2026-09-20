#!/usr/bin/env python3
"""Remove the option letter that 2022's booklet prints INSIDE the option text.

The 2022 LEDOR booklet sets each option as the letter, a space, then the letter
again: the parser sees the line

    A A exalta a investigação filosófica.

`OPT_INLINE` takes the first letter as the marker and leaves the second in the
text, so 176 of 2022's 184 items shipped every option prefixed with its own
letter. It is redundant -- the letter is already `resp_raw` -- and it corrupts
any string comparison between years.

WHY AN ALL-FIVE RULE. For option A the duplicate is genuinely ambiguous with
the Portuguese article ("A A casa..." could be marker + "A casa"), and for E
with the conjunction. So a per-option test would be a guess. The distribution
settles it: across 2022 an item has either FIVE self-prefixed options or ZERO,
never one to four. That is a layout, not a coincidence, and the rule only fires
on the whole set.

Scoped by measurement, not by year: the same scan over the other ten years
returns zero items, so this cannot silently reach into them.

Usage:  python3 46_strip_option_letter.py --items-dir <dir> [--apply]
"""
import argparse, collections, csv, glob, os, re, sys

SCHEMA = ["table","section_id","item","instrument","instructions","section_prompt",
          "item_text","correct_response","option_text","resp","item_text_translated",
          "option_text_translated","instructions_translated","section_prompt_translated",
          "language","resp_raw"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--items-dir", required=True)
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    n_items = n_rows = 0
    for p in sorted(glob.glob(os.path.join(a.items_dir, "*__items.csv"))):
        rows = list(csv.DictReader(open(p, encoding="utf-8")))
        by = collections.defaultdict(list)
        for r in rows:
            by[r["item"]].append(r)
        touched = False
        for it, rs in by.items():
            real = [r for r in rs if (r["option_text"] or "").strip() not in ("", "NA")]
            if not real:
                continue
            # [ \t] not \s: \s crosses a NEWLINE, and in a stacked fraction
            # the newline is the fraction bar. Ben spotted this on #2226 --
            # 2022 MT 89637's prefixes were "B \n", so the strip swallowed the
            # line break as well as the letter.
            pref = [r for r in real
                    if re.match(rf"^[ \t]*{re.escape(r['resp_raw'])}[ \t]*\S|"
                                rf"^[ \t]*{re.escape(r['resp_raw'])}[ \t]*\n",
                                r["option_text"])]
            if len(pref) != len(real) or len(real) < 5:
                continue          # all-or-nothing, and only on a full option set
            for r in pref:
                v = re.sub(rf"^[ \t]*{re.escape(r['resp_raw'])}[ \t]*", "",
                           r["option_text"], count=1)
                # a newline BETWEEN numerator and denominator is the fraction
                # bar and must survive; one LEADING the option is an artifact
                r["option_text"] = v.lstrip("\n")
                n_rows += 1
            n_items += 1
            touched = True
        if touched and a.apply:
            with open(p, "w", newline="", encoding="utf-8") as fh:
                w = csv.DictWriter(fh, SCHEMA); w.writeheader()
                for r in rows:
                    w.writerow({k: r.get(k, "") for k in SCHEMA})
    print(f"  {'stripped' if a.apply else 'WOULD strip'}: {n_items} item(s), {n_rows} row(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
