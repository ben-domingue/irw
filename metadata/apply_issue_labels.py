"""Apply metadata/issue_triage.csv to GitHub. Dry-run unless --apply is passed.

Run metadata/build_issue_triage.py first — the CSV is a derived, uncommitted
build artifact, and the assignments that produce it live in that script.

Adds the labels a row calls for and removes priority labels it does not, so the
file stays the single description of the triage rather than an append-only log.
Labels outside the vocabulary below are never touched.

Note: `gh issue view` is broken repo-wide on ben-domingue/irw by GitHub's
Projects-classic GraphQL deprecation. `gh issue list` and `gh issue edit` are
unaffected, which is why this reads through the former and writes through the latter.
"""

import argparse, csv, json, subprocess, sys
from pathlib import Path

CSV = Path(__file__).with_name("issue_triage.csv")

PRIORITIES = {"p1-trust", "p2-gate", "p3-reach", "p4-volume", "p5-later"}
FLAGS = {"wrong-now", "research-output", "queue-ingested?", "lookhere_ben"}
ROADMAP = {"y3-1", "y3-2", "y3-4", "y3-5", "y3-7", "y3-11"}

# `lookhere_ben` predates this file and ben-domingue applies it by hand. This
# script may add it and must never take it off, or a triage run would silently
# clear a flag he set himself.
ADD_ONLY = {"lookhere_ben"}

OWNED = PRIORITIES | FLAGS | ROADMAP


def current_labels(repo):
    out = subprocess.run(
        ["gh", "issue", "list", "-R", repo, "--state", "open", "--limit", "600",
         "--json", "number,labels"],
        capture_output=True, text=True, check=True).stdout
    return {i["number"]: {lab["name"] for lab in i["labels"]}
            for i in json.loads(out)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true",
                    help="write to GitHub (default is a dry run)")
    args = ap.parse_args()

    rows = list(csv.DictReader(CSV.open()))
    have = {}
    changed = 0

    for row in rows:
        repo, n = row["repo"], int(row["issue"])
        if repo not in have:
            have[repo] = current_labels(repo)
        if n not in have[repo]:
            print(f"  skip {repo}#{n}: not open")
            continue

        want = set(filter(None, [row["priority"], row["roadmap"]]))
        want |= set(row["flags"].split())
        now = have[repo][n] & OWNED

        add = sorted(want - have[repo][n])
        remove = sorted((now - want) - ADD_ONLY)
        if not add and not remove:
            continue
        changed += 1
        verb = "apply" if args.apply else "would"
        print(f"  {verb} {repo}#{n}: +{','.join(add) or '-'} -{','.join(remove) or '-'}")
        if args.apply:
            cmd = ["gh", "issue", "edit", str(n), "-R", repo]
            for lab in add:
                cmd += ["--add-label", lab]
            for lab in remove:
                cmd += ["--remove-label", lab]
            subprocess.run(cmd, capture_output=True, text=True, check=True)

    print(f"{changed} issue(s) {'changed' if args.apply else 'would change'}"
          f" of {len(rows)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
