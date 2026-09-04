"""Agreement between two independent runs of the tagger on the same tables (#1850).

RELIABILITY, NOT VALIDITY. These tables have no human gold -- they were untagged
by construction, which is why the tagger ran on them. Nothing here says a value
is right. It says how much of the output is stable when the pipeline runs again.

Reported per column, three ways, because they answer different questions:

  both answered   -- the run where disagreement is possible at all
  agreed          -- of those, how often the two runs match
  commit agreement-- of ALL tables, how often the two runs made the same
                     answer/abstain DECISION, ignoring what the answer was

The third matters because a column can be stable in what it says and unstable
in whether it says anything, and a user filtering on it feels both.

`sample` is compared on its SETTING atoms only, matching what publishes.
Multi-value columns compare as sets, so ordering never counts as disagreement.

    python3 score_reliability.py reliability_key.json preds_reliability_K*.json
"""
import json
import sys
from collections import Counter
from pathlib import Path

FRAME = {"Representative", "Targeted/specific", "General/non-specific"}
SETTING = {"Educational", "Clinical", "Program-based", "Non-human", "Workplace",
           "Internet-based", "Internet-based (Mturkers, etc)"}
# key column -> prediction key
COLS = [("Primary Language(s)", "primary_languages"),
        ("Item format", "item_format"),
        ("Measurement tool", "measurement_tool"),
        ("Sample", "sample")]


def atoms(v):
    parts = [a.strip() for a in (v or "").split(",") if a.strip()]
    out, i = [], 0
    while i < len(parts):            # rejoin the value with a comma in it
        if parts[i] == "Internet-based (Mturkers" and i + 1 < len(parts):
            out.append("Internet-based (Mturkers, etc)"); i += 2
        else:
            out.append(parts[i]); i += 1
    return {a.replace("Internet-based (Mturkers, etc)", "Internet-based") for a in out}


def setting_only(v):
    return {a for a in atoms(v) if a in SETTING or a not in FRAME}


def main(keypath, predpaths):
    key = {k["table"].lower(): k for k in json.loads(Path(keypath).read_text())}
    new = {}
    for p in predpaths:
        for r in json.loads(Path(p).read_text()):
            new[r["table"].lower()] = r

    shared = [t for t in key if t in new]
    print(f"{len(shared)} tables re-tagged blind and compared against the first run\n")
    print(f"{'column':<22}{'both answered':>15}{'agreed':>10}{'commit agree':>15}")
    for kc, pc in COLS:
        both = agree = commit = 0
        for t in shared:
            a = (key[t]["first"].get(kc) or "").strip()
            b = (new[t].get(pc) or "").strip()
            if kc == "Sample":
                A, B = setting_only(a), setting_only(b)
            else:
                A, B = atoms(a), atoms(b)
            commit += bool(A) == bool(B)
            if A and B:
                both += 1
                agree += A == B
        pa = f"{100*agree/both:.1f}%" if both else "--"
        print(f"{kc:<22}{both:>15}{pa:>10}{100*commit/len(shared):>14.1f}%")

    print("\nwhere they disagreed, per column:")
    for kc, pc in COLS:
        diffs = []
        for t in shared:
            a = (key[t]["first"].get(kc) or "").strip()
            b = (new[t].get(pc) or "").strip()
            A, B = (setting_only(a), setting_only(b)) if kc == "Sample" else (atoms(a), atoms(b))
            if A and B and A != B:
                diffs.append((t, a, b))
        if diffs:
            print(f"\n  {kc} -- {len(diffs)}")
            for t, a, b in diffs[:8]:
                print(f"     {t}\n        run 1: {a!r}\n        run 2: {b!r}")

    print("\nasymmetry -- who committed when the other did not:")
    for kc, pc in COLS:
        only1 = only2 = 0
        for t in shared:
            A = atoms(key[t]["first"].get(kc)); B = atoms(new[t].get(pc))
            only1 += bool(A) and not B
            only2 += bool(B) and not A
        print(f"  {kc:<22}run 1 only {only1:>3}   run 2 only {only2:>3}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:])
