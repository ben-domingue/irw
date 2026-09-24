#!/usr/bin/env python3
"""Render a human-readable HTML preview of the shipped item text.

For eyeballing. A CSV whose cells hold multi-line passages is unreadable in a
browser; this lays each item out as stem + five lettered options with the key
marked, and deliberately leads with the AWKWARD cases rather than the clean
ones, so a reviewer sees what is actually worth arguing about.
"""
import csv, html, os, sys, collections

REPO = os.path.expanduser("~/irw/itemtext/itemtables")
OUT = os.path.expanduser("~/enem_itemtext_preview.html")
YEARS = ["2013","2015","2016","2017","2018","2019","2020","2021","2022","2024","2025"]

# (year, area, item, why this one is worth looking at)
PICKS = [
 ("2015","lc","67408","RECOVERED: lost for two sessions to a parser bug -- the stem contains 'EE UU' (Spanish for Estados Unidos) and the parser read it as a doubled option marker"),
 ("2021","cn","117627","AI-MARKED NOTATION: chemistry the font cannot express; note the inline (gerada por IA) marker"),
 ("2021","cn","88403","DECODED NOTATION: reads E deg = -3,05 V ... I2 + 2 e- -> 2 I-, matching the booklet's own prose"),
 ("2013","cn","15947","BARE FIGURE: five circuit diagrams, so option_text is the literal NA"),
 ("2015","mt","14712","KNOWN GAP: options are stacked fractions, disclosed as a gap and NOT as a figure item"),
 ("2016","cn",None,"FONT-REPAIRED YEAR: accents and punctuation should read perfectly"),
 ("2017","lc","39670","2017 LC: one of the two items where INEP's own accessibility key string disagrees with every other source"),
 ("2019","lc",None,"CLEAN YEAR, no repair needed -- the baseline for comparison"),
 ("2025","lc",None,"SHARED PASSAGE: carried in section_prompt with its own section_id"),
 ("2015","lc","6830","U+FFFD: 25 decorative bullet glyphs per option row left visible rather than guessed (this is CO_ITEM 6830 -- it sits at printed position 118, and calling it \"LC 118\" was the slip that made this entry read NOT FOUND)"),
]

CSS = """body{font:15px/1.55 -apple-system,Segoe UI,Roboto,sans-serif;max-width:900px;
margin:2rem auto;padding:0 1rem;color:#1a1a1a}
h1{font-size:1.5rem} h2{font-size:1.05rem;margin-top:2.2rem;border-top:2px solid #333;padding-top:.7rem}
.why{background:#fff8e1;border-left:4px solid #f0ad4e;padding:.55rem .8rem;margin:.5rem 0;font-size:13.5px}
.meta{color:#666;font-size:12.5px;margin:.3rem 0 .7rem}
.stem{white-space:pre-wrap;background:#f7f7f7;padding:.7rem;border-radius:4px;font-size:14px}
.sp{white-space:pre-wrap;background:#eef6ff;padding:.7rem;border-radius:4px;font-size:13.5px;border-left:4px solid #6aa3d5}
ol{padding-left:1.4rem} li{margin:.3rem 0;white-space:pre-wrap}
li.key{background:#e6f7e6;font-weight:600;border-radius:3px;padding:.15rem .3rem}
code{background:#eee;padding:0 .25rem;border-radius:3px}
.na{color:#a00;font-style:italic}"""


def rows_for(y, a):
    p = f"{REPO}/batch_enem_{y}/enem_{y}_1mil_{a}__items.csv"
    return list(csv.DictReader(open(p, encoding="utf-8")))


def render(fh, y, a, item, why):
    rows = rows_for(y, a)
    by = collections.OrderedDict()
    for r in rows:
        by.setdefault(r["item"], []).append(r)
    if item is None:
        item = list(by)[3]
    rs = by.get(item)
    if not rs:
        # Loud, because the first version of this said only "NOT FOUND" and the
        # cause was a printed POSITION used where a CO_ITEM belongs (R0).
        fh.write(f'<h2>{y} {a.upper()} {item} &mdash; NOT FOUND</h2>'
                 f'<div class="why"><b>This is a bug in the preview, not in the data.</b> '
                 f'No CO_ITEM <code>{item}</code> exists in {y} {a.upper()}. The usual cause '
                 f'is a printed question number used where an item code belongs &mdash; the '
                 f'two are different and R0 requires the item code.</div>')
        return
    r0 = rs[0]
    fh.write(f"<h2>{y} &middot; {a.upper()} &middot; item <code>{item}</code></h2>")
    fh.write(f'<div class="why">{html.escape(why)}</div>')
    fh.write(f'<div class="meta">table <code>{r0["table"]}</code> &middot; '
             f'section <code>{r0["section_id"]}</code> &middot; '
             f'key <b>{r0["correct_response"]}</b> &middot; '
             f'language {r0["language"]} &middot; {len(rs)} rows</div>')
    sp = (r0.get("section_prompt") or "").strip()
    if sp and sp != "NA":
        fh.write("<b>section_prompt</b> (shared passage)"
                 f'<div class="sp">{html.escape(sp[:1800])}'
                 f'{"…" if len(sp)>1800 else ""}</div>')
    fh.write(f'<b>item_text</b><div class="stem">{html.escape(r0["item_text"])}</div>')
    fh.write("<b>option_text</b><ol type='A'>")
    for r in rs:
        t = (r["option_text"] or "")
        cls = ' class="key"' if r["resp"] == "1" else ""
        body = (f'<span class="na">NA &mdash; options are figures, '
                f'nothing printed to transcribe</span>' if t.strip() in ("NA", "")
                else html.escape(t))
        fh.write(f"<li{cls}>{body}</li>")
    fh.write("</ol>")


def main():
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(f"<!doctype html><meta charset=utf-8><title>ENEM item text preview</title>"
                 f"<style>{CSS}</style><h1>ENEM item text &mdash; preview</h1>")
        tot = 0
        for y in YEARS:
            for a in ("ch", "cn", "lc", "mt"):
                tot += len({r["item"] for r in rows_for(y, a)})
        fh.write(f"<p>{tot} items over {len(YEARS)} years, in "
                 f"<code>~/irw/itemtext/itemtables/batch_enem_&lt;YYYY&gt;/</code>. "
                 f"The correct option is shaded green. These examples are chosen to be "
                 f"AWKWARD, not representative &mdash; the interesting decisions are all "
                 f"at the edges.</p>")
        for y, a, it, why in PICKS:
            render(fh, y, a, it, why)
    print(f"  wrote {OUT} ({os.path.getsize(OUT)//1024} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
