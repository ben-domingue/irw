"""What the language-only backfill added, and where it disagrees (#1850).

These 369 rows carried `primary language(s)` and nothing else. The agents tagged
them fully and independently, without being shown the existing language value,
so this file reports two different things:

  1. FILL on `item format`, `measurement tool` and `sample` -- columns these
     rows never had. Nothing to disagree with; this is new information.

  2. AGREEMENT on `primary language(s)` -- an independent second opinion on a
     value already published, at 369 tables against the 60 of the #1850
     reliability run.

The second is the interesting one and it must not be read as "the new value is
better". Both runs can be wrong in characteristic ways: the old one by inferring
the language from the study's country (the failure #1802 caught four agents
committing), the new one by reading the language of the PAPER rather than of the
administration. Where they disagree, this script reports the disagreement and
does not adjudicate it.
"""
import json, glob, collections, re, sys

BT_PAIRS = {("fra","fre"),("fre","fra"),("cze","ces"),("ces","cze"),("deu","ger"),
            ("ger","deu"),("nld","dut"),("dut","nld"),("zho","chi"),("chi","zho"),
            ("ell","gre"),("gre","ell"),("fas","per"),("per","fas")}

def atoms(v):
    return {a.strip() for a in (v or "").split(",") if a.strip()}

def main():
    key={k["table"].lower():k for k in json.load(open("backfill_frame.json"))}
    new={}
    for f in sorted(glob.glob("preds_backfill_L*.json")):
        for r in json.load(open(f)): new.setdefault(r["table"].lower(), r)
    shared=[t for t in key if t in new]
    print(f"{len(key)} rows in the frame, {len(new)} tagged, {len(shared)} compared\n")

    print("NEW VALUES on the three columns these rows never carried")
    for pk,label in [("item_format","item format"),("measurement_tool","measurement tool"),
                     ("sample","sample")]:
        n=sum(1 for t in shared if (new[t].get(pk) or "").strip())
        print(f"  {label:<20}{n:>4} of {len(shared)}   {100*n/len(shared):5.1f}%")

    both=agree=0; diffs=[]
    for t in shared:
        A,B=atoms(key[t]["existing_language"]),atoms(new[t].get("primary_languages"))
        if A and B:
            both+=1
            if A==B: agree+=1
            else: diffs.append((t,key[t]["existing_language"],new[t].get("primary_languages")))
    print(f"\nAGREEMENT on primary language(s): {both} both answered, "
          f"{100*agree/both:.1f}% identical, {len(diffs)} disagree")

    # A disagreement that is only ISO 639-2 B-vs-T is a standards problem, not a
    # judgement problem, and mixing the two silently breaks exact-match filtering.
    variant=[d for d in diffs if len(atoms(d[1]))==1 and len(atoms(d[2]))==1
             and (next(iter(atoms(d[1]))), next(iter(atoms(d[2])))) in BT_PAIRS]
    other=[d for d in diffs if d not in variant]
    print(f"\n  ISO 639-2 bibliographic-vs-terminological variants: {len(variant)}")
    for t,a,b in variant: print(f"     {t:<44}{a!r:>8} -> {b!r}")
    print(f"\n  substantive, NOT adjudicated here: {len(other)}")
    for t,a,b in other: print(f"     {t:<44}{a!r:>8} -> {b!r}")
    fam=collections.Counter(re.split(r"[_\d]",t)[0] for t,_,_ in diffs)
    print("\n  by family:", dict(fam.most_common(8)))

if __name__ == "__main__":
    main()
