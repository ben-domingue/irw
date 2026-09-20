#!/usr/bin/env python3
"""Hunt for inconsistencies in the shipped item text, by detector, and rank them.

Hand-picked examples show what you already suspect. These detectors look for
SHAPES that a bad parse produces, without knowing what the text should say:
truncation, merged options, duplicated extraction, letters lost inside words,
one option swallowing another. Each finding is a candidate, not a verdict --
the point is to put the worst-looking ones in front of a human.
"""
import csv, collections, glob, json, os, re, sys

REPO = os.path.expanduser("~/irw/itemtext/itemtables")
YEARS = ["2013","2015","2016","2017","2018","2019","2020","2021","2022","2024","2025"]

def load():
    out=[]
    for y in YEARS:
        for p in sorted(glob.glob(f"{REPO}/batch_enem_{y}/*__items.csv")):
            a=re.search(r"_1mil_(\w\w)__",p).group(1)
            by=collections.OrderedDict()
            for r in csv.DictReader(open(p,encoding="utf-8")):
                by.setdefault(r["item"],[]).append(r)
            for it,rs in by.items(): out.append((y,a,it,rs))
    return out

NA=lambda v:(v or "").strip() in ("","NA")
norm=lambda v:re.sub(r"\s+"," ",(v or "")).strip()

def detectors(y,a,it,rs):
    """yield (detector, severity, detail)"""
    stem=norm(rs[0]["item_text"])
    opts={r["resp_raw"]:norm(r["option_text"]) for r in rs}
    real=[v for v in opts.values() if not NA(v)]

    # 1 truncation: a stem should end on a question, a colon, or a period
    if stem and not re.search(r"[.?:;!\)\"'”»]$", stem):
        yield ("stem_ends_mid_sentence", 3, f"ends {stem[-45:]!r}")
    # 2 lost lead-in: stems open on a capital, a digit, or a quote
    if stem and not re.match(r"[A-Z0-9À-Ü\"'“«\(\[]", stem):
        yield ("stem_starts_lowercase", 3, f"starts {stem[:45]!r}")
    # 3 one option swallowing the others
    if len(real) >= 2:
        ln=sorted(len(v) for v in real)
        if ln[-1] > 6*max(1,ln[len(ln)//2]) and ln[-1] > 200:
            yield ("one_option_much_longer", 3, f"lengths {sorted(len(v) for v in real)}")
    # 4 duplicated options -- a parse that read the same block twice
    if len(real) != len(set(real)) and real:
        d=[v for v,c in collections.Counter(real).items() if c>1]
        yield ("duplicate_option_text", 4, f"{len(d)} repeated: {d[0][:60]!r}")
    # 5 an option carrying the NEXT question's marker
    for L,v in opts.items():
        if re.search(r"QUEST[ÃA]O\s*\d", v, re.I):
            yield ("option_contains_next_marker", 4, f"{L}: {v[:60]!r}")
            break
    # 6 intra-word split: a 1-2 letter fragment wedged between real words
    m=re.search(r"[a-zà-ü]{3,} ([a-zà-ü]{1,2}) [a-zà-ü]{3,}", stem)
    if m and m.group(1) not in ("a","e","o","as","os","da","de","do","em","na","no","ao",
                                "se","um","ou","ja","la","ha","he","to","of","in","is",
                                "it","as","at","on","by","el","la","un","su","y","a"):
        yield ("possible_intraword_split", 2, f"...{stem[max(0,m.start()-30):m.end()+20]}...")
    # 7 very short option text
    sh=[f"{L}={v!r}" for L,v in opts.items() if not NA(v) and len(v)<=2]
    if sh: yield ("option_1_2_chars", 2, "; ".join(sh[:3]))
    # 8 mixed NA: some options NA, others not
    nas=[L for L,v in opts.items() if NA(v)]
    if nas and len(nas)!=len(opts):
        yield ("mixed_na_options", 4, f"NA on {sorted(nas)} but not the rest")
    # 9 the key's option is NA while others have text
    k=rs[0]["correct_response"]
    if k in opts and NA(opts[k]) and len(nas)!=len(opts):
        yield ("key_option_is_na", 4, f"key {k} has no text")
    # 10 repeated long substring inside the stem (double extraction)
    if len(stem)>300:
        half=len(stem)//2
        for w in (120, 80):
            probe=stem[:w]
            if probe and stem.count(probe)>1:
                yield ("stem_repeats_itself", 4, f"first {w} chars occur twice"); break
    # 11 row/letter integrity
    if sorted(opts)!=list("ABCDE"):
        yield ("option_letters_not_ABCDE", 5, f"letters {sorted(opts)}")
    if sum(1 for r in rs if r["resp"]=="1")!=1:
        yield ("resp_not_exactly_one", 5, f"{sum(1 for r in rs if r['resp']=='1')} rows with resp=1")

def main():
    rows=load()
    hits=collections.defaultdict(list)
    for y,a,it,rs in rows:
        for det,sev,detail in detectors(y,a,it,rs):
            hits[det].append((sev,y,a,it,detail))
    print(f"  scanned {len(rows)} items across {len(YEARS)} years\n")
    print("  detector                        items  severity")
    order=sorted(hits, key=lambda d:(-hits[d][0][0], -len(hits[d])))
    for d in order:
        print(f"  {d:32s} {len(hits[d]):5d}  {hits[d][0][0]}")
    json.dump({d:[list(x) for x in v] for d,v in hits.items()},
              open("anomalies.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
    print("\n  -> anomalies.json")
    return 0

if __name__=="__main__":
    sys.exit(main())
