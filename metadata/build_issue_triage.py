"""Regenerate metadata/issue_triage.csv — one row per open issue, one priority each.

The categories are PRIORITIES.md's, not new ones: p1-trust > p2-gate > p3-reach >
p4-volume > p5-later. `wrong-now` is the narrower ARCHITECTURE.md section 4 class —
the released data would give a *wrong* answer, not merely an incomplete one — and is
the query worth opening daily.

Explicit assignments below come from the 2026-09-06 triage pass, which read every
non-acquisition issue. Everything else is assigned by rule from its existing labels,
so a new issue lands somewhere sensible without being re-read.

`data queue` issues are deliberately left unlabelled: PRIORITIES.md section 5 ranks
acquisition as not-now as a class, and 240 identical labels would say nothing.

The CSV this writes is derived and is **not** committed: it changes every time an
issue is opened or closed, so a tracked copy would churn without recording
anything. The durable half is the assignment lists in this file. Regenerate, then
run apply_issue_labels.py:

    python3 metadata/build_issue_triage.py
    python3 metadata/apply_issue_labels.py            # dry run
    python3 metadata/apply_issue_labels.py --apply
"""

import csv, json, subprocess, sys
from pathlib import Path

REPOS = ["ben-domingue/irw", "itemresponsewarehouse/Rpkg",
         "itemresponsewarehouse/Python-pkg"]
OUT = Path(__file__).with_name("issue_triage.csv")

# Acquisition labels — exempt from the priority vocabulary (see module docstring).
QUEUE_LABELS = {"data queue", "data search", "data--needs license",
                "backlog-search", "request data", "data-joao"}

# The roadmap master issue. Deliberately unlabelled: it is the plan, not work to
# schedule, and tagging it p5-later would read as "the roadmap is not now".
EXEMPT = {("ben-domingue/irw", 1702)}

# --- explicit assignments, 2026-09-06 triage -------------------------------

P1_WRONG_NOW = [2002, 2001, 1996, 1973, 1972, 1971, 1969, 1965, 1964, 1960, 1952,
                1951, 1950, 1942, 1929, 1927, 1925, 1924, 1898, 1875, 1864, 1856,
                1849, 1842, 1816, 1754, 1694, 1342]
# Wrong, but the affected share is not yet known — an audit, not a repair.
P1_OTHER = [1955, 1954, 1897, 1690, 1571, 1474]
P2 = [1992, 1985, 1970, 1962, 1961, 1940, 1863, 1837, 1828, 1817, 1810, 1792,
      1745, 1733, 1731, 1730, 1729, 1812]
P3 = [1889, 1870, 1775, 1439, 1406, 1700]
P4 = [1956, 1930, 1853, 1831, 1809, 1807, 1801, 1800, 1799, 1777, 1650, 1649, 1646]
P5 = [1728, 1688]

ROADMAP = {
    "y3-1":  [1703, 1992, 1961, 1733, 1810, 1856, 1842, 1816],
    "y3-2":  [1863, 1837, 1864],
    "y3-4":  [1706, 1889, 1439, 1406],
    "y3-5":  [1707],
    # Item 7 is "extract the unextracted". Per-table defects in tables that already
    # have item text are corpus trust and deliberately do NOT get this label —
    # routing them here is what made item 7 look unfinishable.
    "y3-7":  [1709, 1853, 1831, 1799, 1800, 1801, 1809, 1777, 1650, 1646, 1807],
    "y3-11": [1713],
}

# Roadmap item issues, by the lens Project 4 already records for each.
ROADMAP_ITEMS = {1703: "p2-gate", 1706: "p3-reach", 1707: "p3-reach",
                 1709: "p4-volume", 1713: "p3-reach",
                 1710: "p5-later", 1711: "p5-later", 1712: "p5-later",
                 1714: "p5-later", 1715: "p5-later", 1716: "p5-later",
                 1717: "p5-later", 1718: "p5-later", 1719: "p5-later"}

# Data queue issues whose source identifier resembles a table already in the
# warehouse, but only on string similarity — labelled, never closed.
QUEUE_INGESTED = [1538, 1275, 1266, 1061, 748, 143, 64, 46]

# Blocked on a decision from ben-domingue rather than on work. Each is one
# question; none needs a session. Two of them gate steps in the structural
# sequence: #1342 (repair the PISA recode rather than filter) and #1955
# (`wording_rights` cannot express a fee, so neither rights re-audit can run).
DECISION = [1342, 1955, 2002, 1694, 1754, 1952, 1950, 1849, 1690, 1864, 1992,
            1940, 1792, 1889, 1870, 1775, 1801, 1650, 1649, 1700, 1728, 1406]

# The lens PRIORITIES.md deliberately did not choose.
RESEARCH_LABELS = {"research project", "summer 2026 project"}

# Package repos: parity and porting work is reach; nothing there serves wrong data.
PKG = {("itemresponsewarehouse/Rpkg", 155): "p2-gate",
       ("itemresponsewarehouse/Rpkg", 149): "p3-reach",
       ("itemresponsewarehouse/Rpkg", 147): "p3-reach",
       ("itemresponsewarehouse/Rpkg", 156): "p3-reach",
       ("itemresponsewarehouse/Python-pkg", 42): "p2-gate",
       ("itemresponsewarehouse/Python-pkg", 28): "p3-reach",
       ("itemresponsewarehouse/Python-pkg", 27): "p3-reach",
       ("itemresponsewarehouse/Python-pkg", 26): "p3-reach",
       ("itemresponsewarehouse/Python-pkg", 25): "p5-later",
       ("itemresponsewarehouse/Python-pkg", 24): "p5-later",
       ("itemresponsewarehouse/Python-pkg", 23): "p5-later",
       ("itemresponsewarehouse/Python-pkg", 22): "p3-reach",
       ("itemresponsewarehouse/Python-pkg", 3): "p3-reach"}

EXPLICIT = {}
for ns, p in ((P1_WRONG_NOW, "p1-trust"), (P1_OTHER, "p1-trust"), (P2, "p2-gate"),
              (P3, "p3-reach"), (P4, "p4-volume"), (P5, "p5-later")):
    for n in ns:
        EXPLICIT[("ben-domingue/irw", n)] = p
EXPLICIT.update(PKG)


def fetch(repo):
    out = subprocess.run(
        ["gh", "issue", "list", "-R", repo, "--state", "open", "--limit", "600",
         "--json", "number,title,labels"],
        capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def classify(repo, issue):
    """Return (priority, flags, roadmap, note). priority may be '' for exemptions."""
    n = issue["number"]
    labels = {lab["name"] for lab in issue["labels"]}
    key = (repo, n)
    flags, note = [], ""

    if key in EXEMPT:
        return "", [], "", "roadmap master; the plan, not work to schedule"

    if labels & QUEUE_LABELS:
        if n in QUEUE_INGESTED:
            return "", ["queue-ingested?"], "", "medium-confidence match to a live table; verify before closing"
        return "", [], "", "acquisition queue; not-now as a class (PRIORITIES.md section 5)"

    priority = EXPLICIT.get(key)
    if priority:
        note = "2026-09-06 triage"
        if n in P1_WRONG_NOW:
            flags.append("wrong-now")
    elif n in ROADMAP_ITEMS and repo == "ben-domingue/irw":
        priority, note = ROADMAP_ITEMS[n], "roadmap item, lens from Project 4"
    elif labels & RESEARCH_LABELS:
        priority, note = "p5-later", "research output: the lens not chosen"
        flags.append("research-output")
    elif repo != "ben-domingue/irw":
        # The package repos hold no data, so nothing there can serve a wrong answer.
        # An untriaged package issue is client work until someone says otherwise.
        priority, note = "p3-reach", "by rule: untriaged package issue"
    else:
        # Everything else is an untriaged dataset offer of some kind — `trials`,
        # `1mode/competition`, `nominal`, `simulated`, or an unlabelled paper link.
        priority, note = "p5-later", "by rule: acquisition-adjacent, never triaged"

    if repo == "ben-domingue/irw" and n in DECISION:
        flags.append("lookhere_ben")

    roadmap = ""
    for lab, ns in ROADMAP.items():
        if repo == "ben-domingue/irw" and n in ns:
            roadmap = lab
            break
    return priority, flags, roadmap, note


def main():
    rows = []
    for repo in REPOS:
        for issue in fetch(repo):
            p, flags, roadmap, note = classify(repo, issue)
            rows.append({"repo": repo, "issue": issue["number"], "priority": p,
                         "flags": " ".join(flags), "roadmap": roadmap,
                         "title": issue["title"], "note": note})
    rows.sort(key=lambda r: (r["repo"], -r["issue"]))
    with OUT.open("w", newline="") as fh:
        w = csv.DictWriter(fh, ["repo", "issue", "priority", "flags", "roadmap",
                                "title", "note"])
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {OUT} ({len(rows)} rows)")


if __name__ == "__main__":
    sys.exit(main())
