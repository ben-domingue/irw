#!/usr/bin/env python3
"""Second preview: the items an ANOMALY SCAN nominated, not ones I chose.

37_anomalies.py runs shape-based detectors over all 2,026 items and writes
anomalies.json. This renders a sample from each detector so a human can judge
them, with the detector's own reasoning printed above each item. Some detectors
are known to be noisy and say so -- the point is to make the noise visible
rather than to hide behind a clean-looking list.
"""
import csv, collections, html, json, os, re, sys

REPO = os.path.expanduser("~/irw/itemtext/itemtables")
OUT = os.path.expanduser("~/enem_itemtext_preview2.html")
PER = 3   # items rendered per detector

NOTE = {
 "duplicate_option_text":
   "Two options share identical text. In EVERY case checked these are FIGURE "
   "items whose option_text is the labels embedded in the drawings (axis names, "
   "atom symbols), and two of the five drawings carry the same labels while "
   "differing in shape. Not a parse fault -- but it does show that some figure "
   "items get label noise as option_text where others get the literal NA, and "
   "that inconsistency is worth a ruling.",
 "stem_ends_mid_sentence":
   "NOISY DETECTOR, 1285 of 2026 items. ENEM's house style ends the stem with "
   "the opening of a sentence the option completes ('...o circuito equivalente "
   "a esse sistema e'). So this fires on normal items and is NOT evidence of "
   "truncation. Shown so you can confirm that reading.",
 "stem_starts_lowercase":
   "Mostly false positives: Spanish items open with an inverted question mark, "
   "and poems and song lyrics legitimately start lowercase. Worth eyeballing "
   "for a genuinely lost lead-in.",
 "one_option_much_longer":
   "THIS ONE FOUND A REAL BUG. All three were INEP figure-description blocks "
   "stuck on the end of option E instead of moved to the stem -- lengths like "
   "[1,1,1,1,346]. The marker regex could not match plural 'Descricao das/dos' "
   "or a header wrapped across a line. Fixed in parser v10; these are shown "
   "AFTER the fix, so option E should now be short and clean.",
 "option_1_2_chars":
   "Expected for numeric-answer items where the options are '1'..'5' or single "
   "digits. Check none of them is a truncated word.",
 "possible_intraword_split":
   "A 1-2 letter fragment wedged between words, the 'sec ulo' shape. Some are "
   "real extraction artifacts from letter-spaced display type; some are "
   "ordinary Portuguese the stop-list missed.",
}

CSS = """body{font:15px/1.55 -apple-system,Segoe UI,Roboto,sans-serif;max-width:900px;
margin:2rem auto;padding:0 1rem;color:#1a1a1a}
h1{font-size:1.5rem} h2{font-size:1.2rem;margin-top:2.6rem;background:#222;color:#fff;
padding:.45rem .7rem;border-radius:4px}
h3{font-size:1rem;margin-top:1.6rem;border-top:1px solid #ccc;padding-top:.6rem}
.det{background:#eef3fa;border-left:4px solid #4a7fb5;padding:.6rem .8rem;font-size:13.5px}
.why{background:#fff8e1;border-left:4px solid #f0ad4e;padding:.45rem .7rem;margin:.4rem 0;font-size:13px}
.meta{color:#666;font-size:12.5px;margin:.3rem 0 .6rem}
.stem{white-space:pre-wrap;background:#f7f7f7;padding:.6rem;border-radius:4px;font-size:13.5px;
max-height:22rem;overflow:auto}
ol{padding-left:1.4rem} li{margin:.25rem 0;white-space:pre-wrap;font-size:13.5px}
li.key{background:#e6f7e6;font-weight:600;border-radius:3px;padding:.1rem .3rem}
code{background:#eee;padding:0 .25rem;border-radius:3px} .na{color:#a00;font-style:italic}"""

_cache = {}
def rows_for(y, a):
    k = (y, a)
    if k not in _cache:
        p = f"{REPO}/batch_enem_{y}/enem_{y}_1mil_{a}__items.csv"
        _cache[k] = list(csv.DictReader(open(p, encoding="utf-8")))
    return _cache[k]

def render(fh, y, a, item, detail):
    rs = [r for r in rows_for(y, a) if r["item"] == item]
    if not rs:
        fh.write(f"<h3>{y} {a.upper()} {item} &mdash; not found</h3>"); return
    r0 = rs[0]
    fh.write(f"<h3>{y} &middot; {a.upper()} &middot; <code>{item}</code></h3>")
    fh.write(f'<div class="why">detector said: {html.escape(detail[:300])}</div>')
    fh.write(f'<div class="meta">key <b>{r0["correct_response"]}</b> &middot; '
             f'{len(rs)} rows &middot; stem {len(r0["item_text"])} chars</div>')
    fh.write(f'<b>item_text</b><div class="stem">{html.escape(r0["item_text"])}</div>')
    fh.write("<b>option_text</b><ol type='A'>")
    for r in rs:
        t = r["option_text"] or ""
        cls = ' class="key"' if r["resp"] == "1" else ""
        body = '<span class="na">NA</span>' if t.strip() in ("NA", "") else html.escape(t)
        fh.write(f"<li{cls}>{body}</li>")
    fh.write("</ol>")

def main():
    h = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "anomalies.json"), encoding="utf-8"))
    order = sorted(h, key=lambda d: (-h[d][0][0], -len(h[d])))
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(f"<!doctype html><meta charset=utf-8><title>ENEM item text "
                 f"&mdash; anomaly preview</title><style>{CSS}</style>"
                 f"<h1>ENEM item text &mdash; anomaly preview</h1>"
                 f"<p>Items nominated by shape-based detectors over all 2,026 items "
                 f"(<code>37_anomalies.py</code>), not hand-picked. Each section says what "
                 f"the detector looks for and whether it turned out to be real. "
                 f"The correct option is shaded green.</p><p><b>Six detectors found "
                 f"nothing at all</b> and are not shown: option letters not A-E, more or "
                 f"fewer than one correct row, some options NA and others not, the key's "
                 f"option blank while others have text, an option carrying the next "
                 f"question's marker, and a stem repeating itself.</p>")
        for d in order:
            hits = h[d]
            fh.write(f"<h2>{d} &mdash; {len(hits)} item(s), severity {hits[0][0]}</h2>")
            if d in NOTE:
                fh.write(f'<div class="det">{html.escape(NOTE[d])}</div>')
            seen = set()
            shown = 0
            for sev, y, a, it, detail in hits:
                if (y, a, it) in seen: continue
                seen.add((y, a, it)); shown += 1
                render(fh, y, a, it, detail)
                if shown >= PER: break
            if len(hits) > shown:
                fh.write(f'<div class="meta">({len(hits) - shown} more not shown)</div>')
    print(f"  wrote {OUT} ({os.path.getsize(OUT)//1024} KB)")
    return 0

if __name__ == "__main__":
    sys.exit(main())
