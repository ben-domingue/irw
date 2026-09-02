#!/usr/bin/env python3
"""rederive_promis.py -- batch_016, issue #1831

Re-parses the PROMIS Wave 1 study codebook (Appendix A) from scratch and
writes rederived.json, so verify_promis1wave1_*.R diffs the shipped text
against a rebuild of the source rather than against a prose claim.

Also carries, per item, the item text independently extracted from the
official PROMIS item-bank PDFs (promis_compiled.pdf). Those extracts are
line-wrap truncated, so they are stored as `official_prefix` and checked as
a prefix, not for equality -- a second route on the wording either way.

Reads   .cache/promis1wave1/{codebook.txt,public_items.json}
Writes  itemtables/batch_016/rederived.json
Run from itemtext/:  python3 itemtables/batch_016/rederive_promis.py
"""
import json, os, re, sys

CACHE = ".cache/promis1wave1"
OUT   = "itemtables/batch_016/rederived.json"

SECTIONS = ["Emotional Distress - Anger", "Emotional Distress - Anxiety",
    "Emotional Distress - Depression", "Emotional Distress - Alcohol Abuse",
    "Fatigue - Fatigue Experience", "Fatigue - Fatigue Impact",
    "Pain - Behavior", "Pain - Interference", "Pain - Quality",
    "Physical Function - Part I", "Physical Function - Part II",
    "Physical Function - Part III", "Social Role - Satisfaction",
    "Social Role - Performance", "Global", "Clinical", "Social Demographic"]

def main():
    cb_txt = os.path.join(CACHE, "codebook.txt")
    if not os.path.exists(cb_txt):
        sys.exit("cached codebook absent (%s); the committed rederived.json stands.\n"
                 "The deposit's download is guestbook-gated -- see provenance.csv source_ref."
                 % cb_txt)
    raw = re.sub(r"\s+", " ", open(cb_txt, encoding="utf-8").read())

    secs = []
    for name in SECTIONS:
        pat = re.escape(name).replace(r"\ \-\ ", r"\s*[–—-]\s*") \
              + r"\s+Items\s+Variable\s+Name"
        secs += [(m.start(), name) for m in re.finditer(pat, raw)]
    secs.sort()

    def section_at(pos):
        cur = None
        for s, name in secs:
            if s < pos: cur = name
            else: break
        return cur

    # The last item of a section carries the next section header into its final
    # option label; cut the boilerplate, then peel the section name itself.
    tail = re.compile(r"\s*(?:Items\s+)?Variable\s+Name\s+Item\s+(?:Context|Stem).*$")
    names = [re.compile(r"\s*" + re.escape(n).replace(r"\ \-\ ", r"\s*[–—-]\s*") + r"\s*$")
             for n in sorted(SECTIONS + ["Legacy Items - Form A", "Legacy Items - Form B"],
                             key=len, reverse=True)]
    def strip_tail(b):
        b = tail.sub("", b)
        for rx in names:
            b2 = rx.sub("", b)
            if b2 != b:
                return b2.strip()
        return b.strip()

    CODE  = r"[A-Z][A-Z0-9]{2,10}\d"
    LOWER = r"(?:clinic|Clinic|Socio|Global)\d{1,3}"
    pat   = re.compile(r"\b(" + CODE + r")\s+(.*?)\s*(\d{1,2} ?= ?.*?)"
                       r"(?=\s+(?:" + CODE + r"|" + LOWER + r")\s|\Z)")
    CTX   = re.compile(r"^(In the past \d+ days?|In the past \w+)\s+(.*)$")

    def contiguous(ks):
        return len(set(ks)) == len(ks) and sorted(ks) == list(range(min(ks), min(ks) + len(ks)))

    out = {}
    for m in pat.finditer(raw):
        code, mid, blob = m.group(1), m.group(2).strip(), strip_tail(m.group(3).strip())
        pairs = []
        for chunk in re.split(r"(?=\d{1,2} ?= ?)", blob):
            mm = re.match(r"^(\d{1,2}) ?= ?(.+)$", chunk.strip())
            if mm and mm.group(2).strip():
                pairs.append([int(mm.group(1)), mm.group(2).strip()])
        if len(pairs) < 2 or len(mid) < 3:
            continue
        keys = [k for k, _ in pairs]
        repair = ""
        if not contiguous(keys):
            # One key printed twice in an otherwise complete run: read the
            # duplicate as the single value missing from the run.
            span    = list(range(min(keys), min(keys) + len(keys)))
            missing = [v for v in span if v not in keys]
            dups    = [k for k in set(keys) if keys.count(k) == 2]
            if len(missing) == 1 and len(dups) == 1:
                want = sorted(span, reverse=keys[0] > keys[-1])
                for i in range(len(pairs)):
                    if pairs[i][0] != want[i] and pairs[i][0] in dups:
                        repair = "key %d printed twice; read as %d for %r" % (
                            pairs[i][0], want[i], pairs[i][1])
                        pairs[i][0] = want[i]
                        break
                keys = [k for k, _ in pairs]
            if not contiguous(keys):
                continue
        c = CTX.match(mid)
        out[code] = {"section": section_at(m.start()),
                     "context": c.group(1) if c else "",
                     "text":    (c.group(2) if c else mid).strip(),
                     "opts":    {str(k): v for k, v in pairs},
                     "order":   [k for k, _ in pairs],
                     "key_repair": repair}

    pub_path = os.path.join(CACHE, "public_items.json")
    if os.path.exists(pub_path):
        pub = json.load(open(pub_path, encoding="utf-8"))
        for code, txt in pub.items():
            if code in out:
                out[code]["official_prefix"] = txt

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1, sort_keys=True)
    print("wrote %s: %d codes (%d with an official-PDF prefix, %d key repairs)" % (
        OUT, len(out), sum("official_prefix" in v for v in out.values()),
        sum(1 for v in out.values() if v["key_repair"])))

if __name__ == "__main__":
    main()
