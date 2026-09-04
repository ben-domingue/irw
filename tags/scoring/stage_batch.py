"""Stage a blind run's predictions into tags_auto.csv, publishing four columns.

**Publishing is an act of selection made here, at assembly — not by the agents.**
The agents fill every field they can support. This script decides what leaves
`tags/scoring/`, and it blanks the rest before a single row is staged.

Published, having cleared the >=90% per-atom precision bar against the human
gold set (#1704):

    primary language(s) · item format · measurement tool · sample SETTING facet

Withheld, written by the agents and kept in the predictions for later
measurement: `construct type` (50.0% per-atom precision on the 2026-09-03
comparison) and `sample`'s FRAME facet (57.1%). Also withheld: `age range` and
`child age`, which the `cov_age` derivation owns and outranks the Sheet on
(#1760, decision 7), and `construct name`, which is not one of the four.

Splitting `sample` is the fiddly part and the reason this is a script rather
than a spreadsheet gesture: one column carries two facets, and only one of them
publishes. `Workplace, Targeted/specific` stages as `Workplace`.

Abstentions are staged too, as sentinel rows carrying `table`, `Rater`, `Notes`,
`Status` and `Reason` and nothing else. `03_tags.R` drops them at the union so
they never reach the published table — but they stay here, and that file plus
the Sheet is what stops the tagger re-attempting a dead source forever.

    python3 stage_batch.py preds_calib_C*.json            # dry run, prints only
    python3 stage_batch.py --commit preds_calib_C*.json   # actually stages
"""

import argparse
import csv
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
STAGE = HERE.parent / ".claude/skills/irw-auto-tag/scripts/stage_tag_row.py"
AUTO = HERE.parent / "tags_auto.csv"

PUBLISH = ["primary_languages", "item_format", "measurement_tool"]  # plus sample setting
WITHHOLD = ["construct_type", "age_range", "child_age", "construct_name"]

#: Above this many codes, `primary language(s)` is read as an instrument
#: fielded in many languages rather than a table administered in a few.
MAX_LANGUAGE_CODES = 4

FRAME_ATOMS = {"Representative", "Targeted/specific", "General/non-specific"}
SETTING_ATOMS = {"Educational", "Clinical", "Program-based", "Non-human",
                 "Workplace", "Internet-based", "Internet-based (Mturkers, etc)"}


def setting_only(sample):
    """Keep the SETTING atoms, drop the FRAME ones. Unknown atoms are dropped
    loudly rather than passed through -- TAG_VOCAB would halt the pipeline on
    them, and finding that out at staging time is cheaper than at export."""
    atoms = [a.strip() for a in (sample or "").split(",") if a.strip()]
    fixed, i = [], 0
    while i < len(atoms):                      # rejoin the value with a comma in it
        if atoms[i] == "Internet-based (Mturkers" and i + 1 < len(atoms):
            fixed.append("Internet-based (Mturkers, etc)"); i += 2
        else:
            fixed.append(atoms[i]); i += 1
    keep, unknown = [], []
    for a in fixed:
        if a in SETTING_ATOMS:
            keep.append(a)
        elif a not in FRAME_ATOMS:
            unknown.append(a)
    return ", ".join(keep), unknown


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("preds", nargs="+")
    ap.add_argument("--commit", action="store_true")
    args = ap.parse_args()

    rows = []
    for p in args.preds:
        rows += json.loads(Path(p).read_text())

    payloads, unknown_all, tally = [], [], Counter()
    multilingual = []
    for r in rows:
        setting, unknown = setting_only(r.get("sample"))
        unknown_all += [(r["table"], u) for u in unknown]
        if r.get("status") != "tagged":
            payloads.append({"table": r["table"], "notes": r.get("notes") or "",
                             "status": "abstained",
                             "reason": r.get("reason") or r.get("notes") or ""})
            tally["sentinel"] += 1
            continue
        pay = {"table": r["table"], "sample": setting, "status": "tagged",
               "notes": r.get("notes") or ""}
        for f in PUBLISH:
            pay[f] = (r.get(f) or "").strip()
        # An instrument fielded in many languages at once cannot be attributed
        # to one of them, and listing all of them asserts something false about
        # every respondent (#1704, ruled 2026-09-04). vocab.md tells the agents
        # this; the guard is here because assembly is where publication is
        # decided, and a long code list is the observable signature. The count
        # is a proxy for the rule, so every one it catches is named rather than
        # silently dropped -- a genuinely quadrilingual instrument would show up
        # here and should be let through by raising the threshold, not by
        # removing the report.
        codes = [c for c in pay["primary_languages"].split(",") if c.strip()]
        if len(codes) > MAX_LANGUAGE_CODES:
            multilingual.append((r["table"], len(codes)))
            pay["primary_languages"] = ""
        for f in PUBLISH + ["sample"]:
            if pay.get(f):
                tally[f] += 1
        if not any(pay.get(f) for f in PUBLISH + ["sample"]):
            tally["nothing_publishable"] += 1
        payloads.append(pay)

    print(f"{len(rows)} predictions -> {len(payloads)} rows to stage\n")
    print("what publishes, per column:")
    for f in PUBLISH + ["sample"]:
        print(f"  {f:<20}{tally[f]:>4} of {len(rows)}  ({100*tally[f]/len(rows):.1f}%)")
    print(f"\n  sentinel (abstention) rows      {tally['sentinel']:>4}")
    print(f"  tagged but nothing publishable  {tally['nothing_publishable']:>4}"
          "   (staged blank; the withheld columns carried their content)")
    print("\nwithheld from every row: " + ", ".join(WITHHOLD) + ", sample FRAME facet")

    if multilingual:
        print(f"\n{len(multilingual)} table(s) had `primary language(s)` blanked -- "
              f"more than {MAX_LANGUAGE_CODES} codes, so the instrument is "
              f"multilingual by construction and this table cannot be attributed "
              f"to one language (#1704):")
        for t, n in multilingual:
            print(f"   {t}  ({n} codes)")

    if unknown_all:
        print(f"\nREFUSING: {len(unknown_all)} `sample` atom(s) outside vocab.md.")
        for t, u in unknown_all[:10]:
            print(f"   {t}: {u!r}")
        sys.exit(1)

    if not args.commit:
        print("\ndry run. pass --commit to stage.")
        return

    # What is already in tags_auto.csv, so a re-drawn table is resolved here
    # rather than by hand. Three batches in a row have hit this: a table stays
    # in the untagged frame until it publishes, so anything that abstained --
    # or that the Sheet suppresses -- comes back around on the next draw.
    existing = {}
    if AUTO.exists():
        with AUTO.open(newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                existing[row["table"].strip().lower()] = row

    def is_tagged(pay):
        return pay.get("status") != "abstained"

    stale = [p for p in payloads
             if p["table"].lower() in existing
             and existing[p["table"].lower()]["Status"] == "abstained"
             and is_tagged(p)]
    dup_abstain = [p for p in payloads
                   if p["table"].lower() in existing
                   and existing[p["table"].lower()]["Status"] == "abstained"
                   and not is_tagged(p)]
    already = [p for p in payloads
               if p["table"].lower() in existing
               and existing[p["table"].lower()]["Status"] == "tagged"]

    # A sentinel says "do not re-attempt this source". Once the source IS
    # reachable that claim is false, and leaving it would suppress a table the
    # fetcher can now read. Drop it and let the new row take its place.
    if stale:
        print(f"\n{len(stale)} stale sentinel(s) -- abstained before, reached now. Replacing:")
        drop = {p["table"].lower() for p in stale}
        with AUTO.open(newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
            cols = list(rows[0].keys())
        kept = [r for r in rows
                if not (r["table"].strip().lower() in drop and r["Status"] == "abstained")]
        for p in stale:
            print(f"   {p['table']}: {existing[p['table'].lower()]['Notes'][:52]!r}")
        with AUTO.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=cols)
            w.writeheader(); w.writerows(kept)

    if dup_abstain:
        print(f"\n{len(dup_abstain)} table(s) abstained again for the same reason "
              f"-- existing sentinel left alone:")
        for p in dup_abstain:
            print(f"   {p['table']}")
    if already:
        print(f"\n{len(already)} table(s) already carry a tagged auto row and are "
              f"skipped. A table here that is still in the untagged frame is "
              f"Sheet-held (#1708) -- its row exists and cannot publish:")
        for p in already:
            print(f"   {p['table']}")

    skip = {p["table"].lower() for p in dup_abstain} | {p["table"].lower() for p in already}
    staged = failed = 0
    for pay in payloads:
        if pay["table"].lower() in skip:
            continue
        r = subprocess.run([sys.executable, str(STAGE)], input=json.dumps(pay),
                           capture_output=True, text=True)
        if r.returncode:
            failed += 1
            print(f"  FAILED {pay['table']}: {r.stdout.strip()} {r.stderr.strip()}")
        else:
            staged += 1
    print(f"\nstaged {staged}, skipped {len(skip)}, failed {failed} -> {AUTO}")


if __name__ == "__main__":
    main()
