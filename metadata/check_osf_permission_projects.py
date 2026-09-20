#!/usr/bin/env python3
"""Check that every project in OSF_PERMISSION_PROJECTS really is unlicensed (issue #2302).

ONE INVARIANT: `apply_osf_permission()` in metadata/dict_union.R stamps
`Derived_License = "Permission via Email"` on the OSF deposits that state no
licence. Its whole premise is that the DEPOSIT IS SILENT. When that premise is
wrong the stopgap publishes a weaker, less useful licence over a real public
grant -- and it does so quietly, because the sheet's `Derived License` cell is
blank in exactly the case the fill fires on.

That is not hypothetical. Eleven of the twenty-two projects listed there were
publishing CC BY / CC BY-SA / CC0 / MIT all along, so 61 biblio rows read
`Permission via Email` (#2302). Every one of them already carried the right
value in the dictionary's `Original License`; only column J was empty.

So this asks OSF directly. A project that publishes a licence must come out of
the list and get its value from `automated_finding/dictionary_auto.csv`
instead -- the path #2058 established.

Exempt, and reported rather than failed: an entry whose comment in dict_union.R
carries `held, #<issue>`. Three NC deposits are deliberately still listed
(4fdw9, t3a9r, g8dvj): `Permission via Email` may record a broader individual
grant than the public NC terms, and narrowing that is Ben's call, not a
checker's. The marker keeps them from turning this into a check nobody runs.

Run it:

    python check_osf_permission_projects.py            ##hits api.osf.io
    python check_osf_permission_projects.py --list     ##offline; just parse the list

Exits 1 if any non-exempt project publishes a licence, or if a node cannot be
read (withdrawn or made private is its own problem -- see #2302's "17 API
errors" -- and silence there must not read as a pass).
"""
import json
import re
import sys
import urllib.request
from pathlib import Path

SOURCE = Path(__file__).resolve().parent / "dict_union.R"
API = "https://api.osf.io/v2/nodes/{}/?embed=license"
TIMEOUT = 30

##The list is R source, and parsing it here rather than duplicating it is the
##point: a project added to dict_union.R is checked without anyone remembering
##to add it in two places.
ENTRY_RE = re.compile(r'^\s*"([a-z0-9]{5})"\s*,?\s*(?:#\s*(.*))?$')


def listed(path=SOURCE):
    text = path.read_text(encoding="utf-8")
    start = text.index("OSF_PERMISSION_PROJECTS <- c(")
    body = text[start:text.index("\n)", start)]
    out = []
    for line in body.splitlines()[1:]:
        m = ENTRY_RE.match(line)
        if m:
            comment = m.group(2) or ""
            out.append((m.group(1), "held, #" in comment, comment.strip()))
    if not out:
        sys.exit("could not parse OSF_PERMISSION_PROJECTS out of " + str(path))
    return out


def osf_license(node):
    """(name, None) if the node publishes one, (None, None) if unset, (None, err)."""
    req = urllib.request.Request(API.format(node),
                                 headers={"Accept": "application/vnd.api+json"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            payload = json.load(r)
    except Exception as exc:                      ##HTTP, JSON, network alike
        return None, f"{type(exc).__name__}: {exc}"
    lic = payload.get("data", {}).get("embeds", {}).get("license", {}).get("data")
    if not lic:
        return None, None
    return lic.get("attributes", {}).get("name"), None


def main():
    entries = listed()
    if "--list" in sys.argv:
        for node, held, comment in entries:
            print(f"{node}\t{'HELD' if held else 'checked'}\t{comment}")
        return 0

    bad, errors, held_hits = [], [], []
    for node, held, comment in entries:
        name, err = osf_license(node)
        if err:
            errors.append((node, err))
        elif name is None:
            print(f"ok    {node}: no node-level licence")
        elif held:
            held_hits.append((node, name))
            print(f"held  {node}: publishes {name} -- exempt ({comment})")
        else:
            bad.append((node, name))
            print(f"FAIL  {node}: publishes {name}")

    for node, err in errors:
        print(f"ERROR {node}: {err}")
    if held_hits:
        print(f"\n{len(held_hits)} project(s) held pending a ruling; see #2302.")
    if bad:
        print(f"\n{len(bad)} project(s) publish a licence and must leave "
              f"OSF_PERMISSION_PROJECTS. Record the licence in "
              f"automated_finding/dictionary_auto.csv (stage_dict_row.py) and "
              f"delete the entry -- the #2058 / #2302 path.")
    return 1 if (bad or errors) else 0


if __name__ == "__main__":
    sys.exit(main())
