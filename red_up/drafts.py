"""How long a Redivis dataset has had unreleased changes sitting in its draft.

Uploads only ever write a *draft* version (see `red_up.push`), and publishing is
a human action. That is deliberate -- it puts a review between a script and the
public corpus -- but it means a draft can quietly accumulate, and until the
version is released nothing a script uploaded is visible to `irw_fetch()`,
`irw_itemtext()` or the site. Project policy is that changes may sit on `next`
for **up to one week**. This reports datasets past that line, so the window is
something that gets noticed rather than a sentence in a document.

    python3 -m red_up.drafts                 # every dataset in redivis_config.R
    python3 -m red_up.drafts --dataset irw_text
    python3 -m red_up.drafts --days 3
    python3 -m red_up.drafts --verbose       # also list what the draft changes

Exit codes: 0 nothing overdue - 1 something is overdue - 2 bad input.

**What is measured, and why it is not the obvious thing.** Two tempting clocks
are both wrong:

  * A *table's* `updatedAt` resets for every table in the draft whenever the
    draft is touched, because opening a draft copies the whole dataset. Every
    table in a 578-table draft reads as minutes old the moment you upload one.
  * The *draft version's* own `createdAt` resets on each upload too, so a
    dataset that receives something weekly would never look overdue even with
    changes from a month ago still unpublished.

What survives both is **time since the last released version**, counted only
when the draft actually differs from it. That is also the quantity the policy is
about: how long the public corpus has been behind what we have.
"""
from __future__ import annotations

import argparse
import datetime as dt
import sys

from .auth import authenticate
from .targets import ConfigError, load_registry

POLICY_DAYS = 7


def _when(epoch_ms: int | None) -> dt.datetime | None:
    if not epoch_ms:
        return None
    return dt.datetime.fromtimestamp(epoch_ms / 1000, tz=dt.timezone.utc)


def inspect(owner: str, target, now: dt.datetime):
    """Return a dict describing one dataset's draft, or an `error` key."""
    import redivis

    out = {"dataset": target.name, "label": target.label}
    try:
        ds = redivis.user(owner).dataset(target.name)
        versions = ds.list_versions()
    except Exception as exc:
        return {**out, "error": str(exc).splitlines()[0][:90]}

    released = [v for v in versions if v.properties.get("isReleased")]
    draft = next((v for v in versions if not v.properties.get("isReleased")), None)
    if draft is None:
        return {**out, "has_draft": False}

    last = max(released, key=lambda v: v.properties.get("createdAt") or 0, default=None)
    since = _when(last.properties.get("createdAt")) if last is not None else None
    out.update(
        has_draft=True,
        released_tag=(last.properties.get("tag") if last is not None else None),
        days_since_release=((now - since).total_seconds() / 86400 if since else None),
    )

    # Only count it as a backlog if the draft actually differs from the release.
    try:
        d_tables = {t.name: t.properties.get("numRows")
                    for t in redivis.user(owner).dataset(target.name, version="next").list_tables()}
        r_tables = {t.name: t.properties.get("numRows")
                    for t in redivis.user(owner).dataset(target.name, version="current").list_tables()} \
            if last is not None else {}
    except Exception as exc:
        return {**out, "error": str(exc).splitlines()[0][:90]}

    out.update(
        added=sorted(set(d_tables) - set(r_tables)),
        removed=sorted(set(r_tables) - set(d_tables)),
        changed=sorted(t for t in set(d_tables) & set(r_tables) if d_tables[t] != r_tables[t]),
    )
    out["pending"] = len(out["added"]) + len(out["removed"]) + len(out["changed"])
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="red_up.drafts",
        description="Report Redivis datasets with unreleased changes past the policy window.",
    )
    ap.add_argument("--dataset", help="only this dataset (default: all of them)")
    ap.add_argument("--days", type=int, default=POLICY_DAYS,
                    help=f"the policy window in days (default {POLICY_DAYS})")
    ap.add_argument("--verbose", action="store_true", help="list the tables the draft changes")
    args = ap.parse_args(argv)

    try:
        owner, targets = load_registry()
    except ConfigError as exc:
        print(f"red_up.drafts: {exc}", file=sys.stderr)
        return 2
    if args.dataset:
        targets = [t for t in targets if t.name == args.dataset]
        if not targets:
            print(f"red_up.drafts: no dataset named {args.dataset!r} in redivis_config.R",
                  file=sys.stderr)
            return 2

    authenticate()
    now = dt.datetime.now(dt.timezone.utc)
    overdue = []
    for target in targets:
        r = inspect(owner, target, now)
        if r.get("error"):
            print(f"{r['dataset']:36s} -- could not read ({r['error']})")
            continue
        if not r.get("has_draft"):
            print(f"{r['dataset']:36s} no draft")
            continue
        if not r.get("pending"):
            print(f"{r['dataset']:36s} draft matches {r.get('released_tag')} -- nothing pending")
            continue
        age = r.get("days_since_release")
        age_s = f"{age:.1f}d" if age is not None else "never released"
        late = age is not None and age > args.days
        if late:
            overdue.append(r)
        print(f"{r['dataset']:36s} {r['pending']:>4} pending, {age_s:>14} since "
              f"{r.get('released_tag')}  {'OVERDUE' if late else ''}")
        if args.verbose:
            for kind in ("added", "removed", "changed"):
                for name in r.get(kind, []):
                    print(f"      {kind:8s} {name}")

    if overdue:
        print(f"\n{len(overdue)} dataset(s) past the {args.days}-day window: "
              f"{', '.join(r['dataset'] for r in overdue)}")
        print("Release the version on Redivis, or record on the issue why it is held.")
        return 1
    print("\nnothing past the window.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
