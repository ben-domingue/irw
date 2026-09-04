"""red_up -- upload CSVs to a Redivis dataset, from any directory.

    red_up .                                  menu, then confirm
    red_up ~/some/batch
    red_up foo.csv
    red_up . --dataset item_response_warehouse_6 --yes
    red_up . --dry-run

Exit codes: 0 ok | 1 an upload or row-count check failed | 2 bad input.

This replaces thirteen near-identical copies of the same script, which
differed only in which dataset they hardcoded -- so the destination was
chosen by which file you happened to run, and the one written routing rule
had already gone stale. See red_up/README.md.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import plan as planning
from .auth import authenticate
from .checks import check_all, check_schema, validate_for_target
from .discover import Discovery, discover, table_name
from .push import open_draft, push_one
from .targets import ConfigError, Target, guess_target, load_registry

#: irw_meta holds a fixed set of pipeline outputs, not arbitrary tables. The
#: map lives in the irw-site-update skill's upload_meta.py; uploading anything
#: else into that dataset is always a mistake, so red_up refuses rather than
#: creating a stray table beside metadata/biblio/tags.
META_TABLES = {
    "metadata", "biblio", "tags", "nominal_tags", "comps_biblio",
    "nominal_biblio", "simsyn_biblio", "simsyn_metadata", "comps_metadata",
    "nominal_metadata", "itemtext_metadata", "collections",
    "collection_members",
}


def die(message: str, code: int = 2) -> None:
    sys.stdout.flush()   # keep the error after whatever we already printed
    print(f"\nred_up: {message}", file=sys.stderr)
    raise SystemExit(code)


def ask(prompt: str, valid: str, default: str, assume: bool) -> str:
    """One keystroke answer. `assume` (from --yes) takes the default."""
    if assume or not sys.stdin.isatty():
        return default
    while True:
        answer = input(prompt).strip().lower()
        if not answer:
            return default
        if answer in valid:
            return answer
        print(f"  please answer one of: {', '.join(valid)}")


def choose_target(targets: list[Target], default: Target, assume: bool) -> Target:
    if assume or not sys.stdin.isatty():
        return default
    print("\nUpload to which dataset?")
    for i, target in enumerate(targets, 1):
        mark = "<-- default" if target is default else ""
        print(f"  {i:>2}) {target.name:<28} {target.label:<28} {mark}")
    while True:
        answer = input(f"\n[Enter = {default.name}] ").strip()
        if not answer:
            return default
        if answer.isdigit() and 1 <= int(answer) <= len(targets):
            return targets[int(answer) - 1]
        match = [t for t in targets if t.name == answer]
        if match:
            return match[0]
        print("  not a valid choice")


def resolve_elsewhere(items: list[planning.Item], target: Target,
                      assume: bool) -> None:
    """Ask, per file, what to do about a table that already exists elsewhere.

    The default is 'update it where it already lives'. Uploading into the
    newer dataset would shadow rather than replace the existing copy, which is
    silent -- so the safe answer is the one that needs no thought.
    """
    for item in items:
        if item.status != planning.ELSEWHERE:
            continue
        where = ", ".join(item.found_in)
        home = item.found_in[-1]     # newest dataset already holding it
        if assume or not sys.stdin.isatty():
            item.dataset = home
            continue
        print(f"\n  {item.table} already exists in {where}, not in {target.name}.")
        print(f"  Clients resolve newest-first, so a copy in {target.name} would "
              f"shadow that one rather than replace it.")
        answer = ask(
            f"  [u] update it in {home}  [s] skip  [f] upload to {target.name} anyway "
            f"[u]: ", "usf", "u", assume)
        if answer == "u":
            item.dataset = home
        elif answer == "f":
            item.dataset = target.name
        else:
            item.dataset, item.status = None, planning.SKIP


def show(items: list[planning.Item], target: Target, owner: str,
         skipped: list[Path]) -> None:
    print(f"\ntarget: {owner}.{target.name}:next   ({target.label})")
    print()
    order = {planning.NEW: 0, planning.UPDATE: 1, planning.ELSEWHERE: 2,
             planning.SKIP: 3, planning.EXCLUDED: 4}
    for item in sorted(items, key=lambda i: (order[i.status], i.table)):
        note = item.note
        if item.status == planning.SKIP:
            note = "; ".join(item.report.errors) or "skipped"
        elif item.dataset and item.dataset != target.name:
            note = f"-> {item.dataset}"
        elif item.status == planning.UPDATE:
            note = "replaces the existing table"
        print(f"  {item.status:<10} {item.table:<44} "
              f"{item.report.rows:>10,} rows  {len(item.report.columns):>3} cols  {note}")

    warnings = [(i.table, w) for i in items if i.dataset for w in i.report.warnings]
    if warnings:
        print(f"\n  warnings ({len(warnings)})")
        for table, warning in warnings:
            print(f"    {table:<44} {warning}")
    if skipped:
        print(f"\n  not CSV, ignored ({len(skipped)})")
        for path in skipped[:10]:
            print(f"    {path.name}")
        if len(skipped) > 10:
            print(f"    ... and {len(skipped) - 10} more")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="red_up",
        description="Upload CSVs to a Redivis dataset (draft version only).")
    parser.add_argument("path", nargs="*", default=["."],
                        help="CSV files, or directories searched recursively "
                             "(default: the current directory)")
    parser.add_argument("--dataset", help="skip the menu and use this dataset")
    parser.add_argument("--yes", "-y", action="store_true",
                        help="take every default and do not prompt")
    parser.add_argument("--dry-run", action="store_true",
                        help="show the plan and exit without uploading")
    parser.add_argument("--allow-unregistered", action="store_true",
                        help="permit --dataset to name a dataset that is not in "
                             "redivis_config.R (scratch/test datasets only)")
    parser.add_argument("--no-validate", action="store_true",
                        help="skip the IRW format validator (the one check that "
                             "needs pandas). checks.py has pointed at this flag "
                             "since 2026-09-02; it did not exist until 2026-09-03")
    parser.add_argument("--strict", action="store_true",
                        help="treat warnings as errors and upload nothing")
    args = parser.parse_args(argv)

    # Resolved before anything else, and never chdir'd away from: the scripts
    # this replaces chdir'd into their own directory first, so `upload.py .`
    # meant the script's folder rather than the caller's.
    paths = [Path(p).expanduser().resolve() for p in (args.path or ["."])]
    missing = [p for p in paths if not p.exists()]
    if missing:
        die("does not exist: " + ", ".join(str(p) for p in missing))

    found = Discovery()
    for p in paths:
        one = discover(p)
        found.csvs.extend(one.csvs)
        found.skipped.extend(one.skipped)
    # A file named twice (say `red_up . batch/x.csv`) must not upload twice.
    found.csvs = list(dict.fromkeys(found.csvs))
    found.skipped = list(dict.fromkeys(found.skipped))
    if not found.csvs:
        where = ", ".join(str(p) for p in paths)
        die(f"no .csv files under {where}"
            + (f" ({len(found.skipped)} non-CSV files ignored)" if found.skipped else ""))

    reports = check_all([(p, table_name(p)) for p in found.csvs])

    try:
        owner, targets = load_registry()
    except ConfigError as exc:
        die(str(exc))

    where = paths[0] if len(paths) == 1 else f"{len(paths)} paths"
    print(f"red_up -- {len(found.csvs)} CSV file(s) under {where}")

    if args.dataset:
        match = [t for t in targets if t.name == args.dataset]
        if match:
            target = match[0]
        elif args.allow_unregistered:
            # Deliberately awkward to reach. Every real IRW dataset is in
            # redivis_config.R; anything else is a scratch dataset, and a typo
            # here would otherwise create a brand-new dataset full of tables.
            target = Target(name=args.dataset, label="UNREGISTERED (not in "
                            "redivis_config.R)", kind="aux")
        else:
            die(f"unknown dataset {args.dataset!r}. Known: "
                + ", ".join(t.name for t in targets)
                + "\nUse --allow-unregistered if this is a scratch dataset.")
    else:
        try:
            default = guess_target(found.csvs, targets)
        except ConfigError as exc:
            die(str(exc))
        target = choose_target(targets, default, args.yes)

    for report in reports:
        check_schema(report, target)
        validate_for_target(report, target, enabled=not args.no_validate)

    authenticate()

    # Scan every core shard plus the target, so a table that already lives
    # somewhere else is caught before it is duplicated rather than after.
    scan = [t.name for t in targets if t.kind == "core"]
    if target.name not in scan:
        scan.append(target.name)
    print(f"checking {len(scan)} datasets for existing tables ...")
    index = planning.index_tables(owner, scan)

    items = planning.build(reports, target, index)
    if target.is_meta:
        # irw_meta holds a fixed set of pipeline outputs. Anything else in the
        # directory is some other artefact of the metadata run, not a table.
        for item in items:
            if item.table not in META_TABLES:
                item.status, item.dataset = planning.EXCLUDED, None
                item.note = f"not one of {target.name}'s {len(META_TABLES)} tables"
    resolve_elsewhere(items, target, args.yes)
    show(items, target, owner, found.skipped)

    if args.strict and any(i.report.warnings for i in items if i.dataset):
        die("--strict: warnings above, nothing uploaded")

    live = [i for i in items if i.dataset]
    if not live:
        die(f"nothing here belongs in {target.name} -- every file was excluded "
            f"or skipped for the reason shown above.")
    # A file with errors is a SKIP; a file the target does not take is EXCLUDED.
    # Only the first is a failure -- excluding `provenance.csv` from irw_meta is
    # the design working. The all-skipped case already exits non-zero via die()
    # above; this covers the PARTIAL one, where twelve tables upload, the
    # thirteenth silently does not, and the run still reports success.
    skipped = [i for i in items if i.status == planning.SKIP]
    if skipped:
        print(f"\n{len(skipped)} file(s) skipped for errors and will NOT be "
              f"uploaded:", file=sys.stderr)
        for item in skipped:
            for err in item.report.errors:
                print(f"  {item.table}: {err}", file=sys.stderr)

    if args.dry_run:
        print(f"\n--dry-run: {len(live)} table(s) would be uploaded. Nothing was written.")
        return 1 if skipped else 0

    if ask(f"\nUpload {len(live)} table(s)? [y/N] ", "yn", "y" if args.yes else "n",
           args.yes) != "y":
        print("Cancelled.")
        return 0

    drafts: dict[str, object] = {}
    results = []
    for n, item in enumerate(live, 1):
        if item.dataset not in drafts:
            drafts[item.dataset] = open_draft(owner, item.dataset)
        dataset = drafts[item.dataset]
        print(f"  [{n}/{len(live)}] {item.table} -> {item.dataset}", flush=True)
        results.append(push_one(dataset, item.path, item.table, item.report.rows))

    for result in results:
        if result.stray_uploads:
            print(f"  note: {result.table} also carried upload(s) "
                  f"{result.stray_uploads} from an earlier run; the replace "
                  f"cleared them.")

    failed = [r for r in results if not r.ok]
    print(f"\n{len(results) - len(failed)}/{len(results)} uploaded and row-count "
          f"verified.")
    for result in failed:
        print(f"  FAILED  {result.dataset}.{result.table}: {result.error}",
              file=sys.stderr)
    if failed:
        return 1
    print("\nThese are DRAFT versions. Review the diff on Redivis and publish by hand.")
    return 1 if skipped else 0


if __name__ == "__main__":
    sys.exit(main())
