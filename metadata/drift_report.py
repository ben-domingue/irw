#!/usr/bin/env python3
"""Report what downstream of the pipeline is behind (issue #1940).

IRW has a compute clock and no publish clock. The weekly metadata pipeline is
automated; every step that puts a number in front of a user -- `upload_meta.py`,
the Publish click on Redivis, the site render -- is a human action, unsequenced
and unmonitored. So the published corpus can be arbitrarily far behind the
repository with nothing reporting it.

That is not hypothetical. On 2026-09-08 the repository held 4,238 tables and the
homepage said 4,238, while every page that queries Redivis live was answering
from `irw_meta` v21.0, released four days earlier. The site had been rendered
*after* the repository caught up and *before* the warehouse ever did. Every one
of those facts was discoverable by hand; nobody checks by hand.

This is a substitute for remembering. It answers one question -- "is anything
downstream behind?" -- and writes the answer into ONE GitHub issue that it edits
in place, so it is a page you glance at rather than a stream you learn to ignore.

WHAT IT DELIBERATELY DOES NOT DO
--------------------------------
It never blocks, gates or fails anything. Exit status is 0 unless the report
itself could not be produced. A stale warehouse is a fact to act on, not a
broken build, and a report that can redden CI is a report people start routing
to a folder. `--check` exists for a human running it locally and is not used by
the workflow.

It also does not decide anything. Publishing to Redivis is a human act
(ARCHITECTURE.md section 4: "that click is always a human action") and the whole
point of reporting rather than automating is that the judgement stays with a
person.

AGE VOCABULARY
--------------
Reused verbatim from metadata/status_page/README.md so the report and the
morning status artifact grade staleness the same way:

    live   0-2 days      aging  3-6 days      stale  7+ days

Seven days is not arbitrary either: it is the draft window red_up documents and
enforces (`red_up/drafts.py:41`, ARCHITECTURE.md section 4 -- "changes may sit
in a draft for up to one week, and that is fine").

USAGE
-----
    python3 metadata/drift_report.py                 # print the report
    python3 metadata/drift_report.py --json          # machine-readable
    python3 metadata/drift_report.py --post          # edit the tracking issue
    python3 metadata/drift_report.py --check         # exit 1 if anything stale
    python3 metadata/drift_report.py --no-redivis    # skip the draft check
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import subprocess
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

REPO = "ben-domingue/irw"
#: The Quarto site. Note the repository is `datapages/irw`, not `datapages/irw_site`
#: -- the directory is called irw_site locally and the repository is not.
SITE_REPO = "datapages/irw"
SITE_HERO_URL = "https://raw.githubusercontent.com/datapages/irw/main/data/hero_stats.json"

#: The label that identifies the one tracking issue. Anything carrying it is
#: assumed to be ours to overwrite, so it must not be a label a human would put
#: on an ordinary issue.
ISSUE_LABEL = "drift-report"
ISSUE_TITLE = "Downstream drift report"

#: status_page/README.md's classes, in days.
AGING_AT = 3
STALE_AT = 7

OK, AGING, STALE, ERROR = "ok", "aging", "stale", "error"
MARK = {OK: "🟢", AGING: "🟡", STALE: "🔴", ERROR: "⚪"}


def classify(days: float | None) -> str:
    """Grade an age in days. `None` means "could not tell", not "fine"."""
    if days is None:
        return ERROR
    if days >= STALE_AT:
        return STALE
    if days >= AGING_AT:
        return AGING
    return OK


@dataclass
class Check:
    key: str
    title: str
    status: str
    headline: str
    detail: list[str] = field(default_factory=list)
    days: float | None = None

    def as_dict(self) -> dict:
        return {"key": self.key, "title": self.title, "status": self.status,
                "headline": self.headline, "detail": self.detail, "days": self.days}


def run(cmd: list[str], cwd: Path | None = None) -> str:
    """Run a command and return stdout, raising with stderr on failure."""
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(f"{' '.join(cmd[:3])}...: {p.stderr.strip().splitlines()[-1] if p.stderr.strip() else 'failed'}")
    return p.stdout


def gh_api(path: str, jq: str) -> str:
    return run(["gh", "api", path, "--jq", jq]).strip()


def days_since(when: dt.datetime, now: dt.datetime) -> float:
    return (now - when).total_seconds() / 86400


def parse_iso(s: str) -> dt.datetime:
    """Parse an ISO-8601 timestamp, tolerating the trailing Z."""
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))


# ---------------------------------------------------------------------------
# The checks. Each returns a Check and must never raise: a check that cannot
# answer reports ERROR with the reason, because one unreachable source must not
# cost you the other four answers.
# ---------------------------------------------------------------------------

def check_drafts(root: Path, now: dt.datetime, enabled: bool) -> Check:
    """Redivis datasets whose draft has diverged from the release past the window.

    Reuses red_up.drafts.inspect() rather than reimplementing it. Its clock
    choice is the subtle part and is already correct there: it counts time since
    the last RELEASED version, because a table's `updatedAt` and the draft
    version's own `createdAt` both reset whenever the draft is touched
    (drafts.py:18-30). It also fingerprints tables by content hash, not row
    count, because a repair that fixes values keeps the row count identical.
    """
    if not enabled:
        return Check("drafts", "Redivis drafts", ERROR, "skipped (--no-redivis)")
    try:
        sys.path.insert(0, str(root))
        from red_up.auth import authenticate
        from red_up.drafts import inspect as inspect_draft
        from red_up.targets import load_registry

        owner, targets = load_registry()
        authenticate()
    except Exception as exc:
        return Check("drafts", "Redivis drafts", ERROR,
                     f"could not reach Redivis ({str(exc).splitlines()[0][:80]})")

    rows, worst, failures = [], None, 0
    for target in targets:
        try:
            r = inspect_draft(owner, target, now)
        except Exception as exc:
            failures += 1
            rows.append(f"`{target.name}` — could not read ({str(exc).splitlines()[0][:60]})")
            continue
        if r.get("error"):
            failures += 1
            rows.append(f"`{r['dataset']}` — could not read ({r['error']})")
            continue
        if not r.get("has_draft") or not r.get("pending"):
            continue
        age = r.get("days_since_release")
        worst = age if worst is None else max(worst, age or 0)
        age_s = f"{age:.1f}d" if age is not None else "never released"
        rows.append(f"`{r['dataset']}` — **{r['pending']} pending**, {age_s} since "
                    f"{r.get('released_tag')} "
                    f"(+{len(r.get('added', []))} / −{len(r.get('removed', []))} / "
                    f"~{len(r.get('changed', []))})")

    if failures and not rows:
        return Check("drafts", "Redivis drafts", ERROR, "no dataset could be read", rows)
    if not rows:
        return Check("drafts", "Redivis drafts", OK, "no unreleased changes", days=0.0)
    status = classify(worst)
    n = len([r for r in rows if "pending" in r])
    return Check("drafts", "Redivis drafts", status,
                 f"{n} dataset(s) with unreleased changes, oldest "
                 f"{worst:.1f}d" if worst is not None else f"{n} dataset(s) with unreleased changes",
                 rows, worst)


def check_warehouse_behind_repo(root: Path, now: dt.datetime) -> Check:
    """Has `metadata/` moved in the repo since irw_meta was last released?

    This is the gap that motivated #1940. The repo is the source and irw_meta is
    what every live-querying page reads, so the interval between them is exactly
    how long users have been seeing numbers we have already superseded.

    Both sides come from files this repository commits -- version_manifest.tsv is
    refreshed daily by its own workflow -- so this check needs no credentials.
    """
    manifest = root / "metadata" / "version_manifest.tsv"
    try:
        released: dt.datetime | None = None
        tag = None
        with manifest.open() as fh:
            for row in csv.DictReader(fh, delimiter="\t"):
                if row.get("dataset") != "irw_meta":
                    continue
                when = row.get("redivis_released_at") or ""
                if not when:
                    continue
                d = parse_iso(when)
                if released is None or d > released:
                    released, tag = d, row.get("redivis_tag")
        if released is None:
            return Check("warehouse", "Warehouse vs repo", ERROR,
                         "no released irw_meta row in version_manifest.tsv")
    except Exception as exc:
        return Check("warehouse", "Warehouse vs repo", ERROR,
                     f"could not read version_manifest.tsv ({exc})")

    # When `metadata/` last changed on main. Try git first, so a local run works
    # against the checkout in front of you -- then fall back to the API, because
    # actions/checkout is shallow by default and `git log` over a path in a
    # one-commit clone answers "never" rather than failing, which would silently
    # report the warehouse as current.
    repo_at = None
    try:
        out = run(["git", "log", "-1", "--format=%cI", "origin/main", "--", "metadata/"],
                  cwd=root).strip()
        if out:
            repo_at = parse_iso(out)
    except Exception:
        pass
    if repo_at is None:
        try:
            repo_at = parse_iso(gh_api(f"repos/{REPO}/commits?path=metadata&per_page=1",
                                       ".[0].commit.committer.date"))
        except Exception as exc:
            return Check("warehouse", "Warehouse vs repo", ERROR,
                         f"could not date the last metadata/ commit ({exc})")

    # The warehouse is only "behind" if the repo moved AFTER the release. A repo
    # that has not changed since the last publish is current, however old the
    # publish is -- age alone is not drift, and reporting it as drift would make
    # this noisy every quiet week.
    if repo_at <= released:
        return Check("warehouse", "Warehouse vs repo", OK,
                     f"irw_meta {tag} is current with `metadata/`", days=0.0)
    lag = days_since(released, repo_at)
    return Check("warehouse", "Warehouse vs repo", classify(days_since(released, now)),
                 f"`metadata/` is **{lag:.1f}d ahead** of published irw_meta {tag}",
                 [f"irw_meta {tag} released {released:%Y-%m-%d %H:%M} UTC",
                  f"`metadata/` last changed {repo_at:%Y-%m-%d %H:%M} UTC",
                  "Fix: `git pull`, then `python3 upload_meta.py`, then Publish on Redivis."],
                 days_since(released, now))


def check_hero(root: Path) -> Check:
    """Does the homepage banner agree with metadata.csv?

    The hero is the one number the site reads off disk rather than from Redivis
    (`components/_hero_playful.qmd`), so it drifts independently of everything
    else and is the most visible figure in the project.
    """
    local = metadata_rows(root)
    if local is None:
        return Check("hero", "Homepage banner", ERROR, "could not count metadata.csv")
    try:
        with urllib.request.urlopen(SITE_HERO_URL, timeout=30) as fh:
            hero = json.load(fh)
    except (urllib.error.URLError, ValueError, TimeoutError) as exc:
        return Check("hero", "Homepage banner", ERROR, f"could not fetch hero_stats.json ({exc})")

    n = hero.get("totals", {}).get("n_tables")
    when = hero.get("generated_at")
    if n is None:
        return Check("hero", "Homepage banner", ERROR, "hero_stats.json has no totals.n_tables")
    if n == local:
        return Check("hero", "Homepage banner", OK, f"agrees with metadata.csv ({n:,} tables)",
                     days=0.0)
    return Check("hero", "Homepage banner", AGING,
                 f"says **{n:,}** tables; `metadata.csv` has **{local:,}**",
                 [f"hero_stats.json generated {when}",
                  "Fix: run `metadata/09_hero_status.R` and commit the result to "
                  f"`{SITE_REPO}`."])


def check_site_render(now: dt.datetime) -> Check:
    """How long since the site was actually built?"""
    try:
        built = parse_iso(gh_api(f"repos/{SITE_REPO}/commits/gh-pages",
                                 ".commit.committer.date"))
        main_at = parse_iso(gh_api(f"repos/{SITE_REPO}/commits/main",
                                   ".commit.committer.date"))
    except Exception as exc:
        return Check("site", "Site render", ERROR, f"could not read {SITE_REPO} ({exc})")

    age = days_since(built, now)
    if main_at > built:
        # Grade on how long the site has been out of date, not on how long ago
        # it was built. A site rebuilt an hour ago that main has since moved past
        # is not a problem; one that main moved past a week ago is.
        behind = days_since(built, now)
        return Check("site", "Site render", classify(behind),
                     f"built {age:.1f}d ago; `main` has moved since",
                     [f"gh-pages built {built:%Y-%m-%d %H:%M} UTC",
                      f"`main` last commit {main_at:%Y-%m-%d %H:%M} UTC",
                      "The daily conditional rebuild should pick this up; "
                      "`gh workflow run quarto_publish.yaml` to do it now."], age)
    return Check("site", "Site render", OK,
                 f"built {age:.1f}d ago, current with `main`", days=age)


def check_status_json(root: Path) -> Check:
    """Does status.json agree with the metadata.csv committed beside it?

    Since #1940 wired 11_status.R into the weekly pipeline (PR #2081) these are
    written in the same run and cannot disagree. So a mismatch here does not mean
    "the numbers are stale" -- it means the stage did not run, which is a
    different and more interesting failure.
    """
    local = metadata_rows(root)
    path = root / "metadata" / "status.json"
    try:
        status = json.loads(path.read_text())
    except Exception as exc:
        return Check("status", "status.json", ERROR, f"could not read status.json ({exc})")
    n = status.get("n_tables")
    if local is None:
        return Check("status", "status.json", ERROR, "could not count metadata.csv")
    if n == local:
        return Check("status", "status.json", OK,
                     f"consistent with metadata.csv ({n:,} tables)", days=0.0)
    return Check("status", "status.json", STALE,
                 f"says **{n:,}** tables against a metadata.csv of **{local:,}**",
                 [f"generated {status.get('generated')}",
                  "Since PR #2081 these are written in the same pipeline run, so this "
                  "means stage 11 did not run -- not merely that it ran a while ago."])


def metadata_rows(root: Path) -> int | None:
    """Row count of metadata.csv, or None if it cannot be read."""
    try:
        with (root / "metadata" / "metadata.csv").open(newline="") as fh:
            return sum(1 for _ in csv.DictReader(fh))
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Rendering and posting
# ---------------------------------------------------------------------------

def render(checks: list[Check], now: dt.datetime) -> str:
    worst = STALE if any(c.status == STALE for c in checks) else (
        AGING if any(c.status == AGING for c in checks) else OK)
    lead = {
        OK: "Everything downstream is current.",
        AGING: "Something downstream is starting to lag.",
        STALE: "Something downstream is past the one-week window.",
    }[worst]

    out = [f"_Generated {now:%Y-%m-%d %H:%M} UTC by "
           f"[`metadata/drift_report.py`](https://github.com/{REPO}/blob/main/metadata/drift_report.py) "
           f"(#1940). This issue is rewritten in place each day — comments are preserved._",
           "", f"**{lead}**", "",
           "| | Check | State |", "|---|---|---|"]
    for c in checks:
        out.append(f"| {MARK[c.status]} | {c.title} | {c.headline} |")

    detail = [c for c in checks if c.detail]
    if detail:
        out += ["", "## Detail", ""]
        for c in detail:
            out.append(f"**{c.title}** — {c.headline}")
            out += [f"- {line}" for line in c.detail]
            out.append("")

    out += ["---", "",
            f"`live` 0–{AGING_AT - 1}d · `aging` {AGING_AT}–{STALE_AT - 1}d · "
            f"`stale` {STALE_AT}d+ — the same classes "
            f"`metadata/status_page/README.md` uses. The seven-day line is the "
            f"draft window `red_up` enforces; a draft sitting inside it is a "
            f"normal state, not a loose end.",
            "",
            "This report blocks nothing. It exists because every fact above is "
            "discoverable by hand and nobody checks by hand."]
    return "\n".join(out)


def post(body: str, repo: str) -> str:
    """Create or update the one tracking issue. Returns a human-readable result.

    There is no edit-in-place precedent in this repository -- every other job
    files a NEW issue per run (version-manifest.yml, metadata-pipeline.yml) --
    so this is built here. Two constraints shape it:

      * `gh issue view` is broken repository-wide by GitHub's Projects-classic
        GraphQL deprecation (see metadata/apply_issue_labels.py:10-12), so the
        issue is never viewed. It is FOUND through the REST issues endpoint and
        WRITTEN through `gh issue edit`.
      * the lookup must NOT use `gh issue list --label`. That reads GitHub's
        search index, which is eventually consistent: in testing, a second run
        moments after the first found nothing and filed a duplicate. The REST
        `/issues?labels=` endpoint is read-your-writes and returned both
        immediately. Daily runs are 24h apart so the race is unlikely in
        production, but "find the issue I just created" must not depend on an
        index catching up.
      * the label is the identity. A human retitling the issue must not cause a
        second one to appear.
    """
    found = json.loads(run(["gh", "api",
                            f"repos/{repo}/issues?labels={ISSUE_LABEL}&state=open&per_page=5",
                            "--jq", "[.[] | {number, title}]"]))
    tmp = Path(".drift_report_body.md")
    tmp.write_text(body)
    try:
        if not found:
            url = run(["gh", "issue", "create", "--repo", repo, "--title", ISSUE_TITLE,
                       "--label", ISSUE_LABEL, "--body-file", str(tmp)]).strip()
            return f"created {url}"
        if len(found) > 1:
            nums = ", ".join(f"#{i['number']}" for i in found)
            return (f"refusing to post: {len(found)} open issues carry the "
                    f"`{ISSUE_LABEL}` label ({nums}). Close all but one.")
        num = found[0]["number"]
        run(["gh", "issue", "edit", str(num), "--repo", repo, "--body-file", str(tmp)])
        return f"updated {repo}#{num}"
    finally:
        tmp.unlink(missing_ok=True)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=None, help="repository root (default: infer)")
    ap.add_argument("--json", action="store_true", help="emit JSON instead of markdown")
    ap.add_argument("--post", action="store_true", help="create/update the tracking issue")
    ap.add_argument("--repo", default=REPO, help=f"repository for --post (default {REPO})")
    ap.add_argument("--check", action="store_true",
                    help="exit 1 if anything is stale (for a human; the workflow does not use it)")
    ap.add_argument("--no-redivis", action="store_true",
                    help="skip the draft check, which is the only one needing credentials")
    args = ap.parse_args(argv)

    root = Path(args.root) if args.root else Path(__file__).resolve().parent.parent
    now = dt.datetime.now(dt.timezone.utc)

    checks = [
        check_warehouse_behind_repo(root, now),
        check_drafts(root, now, enabled=not args.no_redivis),
        check_site_render(now),
        check_hero(root),
        check_status_json(root),
    ]

    if args.json:
        print(json.dumps({"generated": now.isoformat(),
                          "checks": [c.as_dict() for c in checks]}, indent=2))
    else:
        body = render(checks, now)
        print(body)
        if args.post:
            print(f"\n-- {post(body, args.repo)}", file=sys.stderr)

    if args.check and any(c.status == STALE for c in checks):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
