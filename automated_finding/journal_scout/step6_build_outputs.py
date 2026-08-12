"""Step 6: assemble journal_yield.csv from Steps 1-4.

One row per journal-year: journal-level Step 3/4 sample summary columns
are repeated across that journal's year rows, matching the spec's layout.
"""
from __future__ import annotations

import csv
import os
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).parent

DATA_EXT = {".csv", ".tsv", ".txt", ".dat", ".xlsx", ".xls", ".sav", ".dta",
            ".rds", ".rdata", ".por", ".json", ".zip"}
AMBIG_EXT = {".zip", ".txt"}


def exts_of(manifest: str) -> set[str]:
    exts = set()
    for name in manifest.split(";"):
        if not name:
            continue
        i = name.rfind(".")
        if i >= 0:
            exts.add(name[i:].lower())
    return exts


def license_bucket(raw: str) -> str:
    raw = (raw or "").strip().lower()
    if raw == "":
        return "unknown"
    if raw == "cc by":
        return "cc_by"
    if raw == "cc by-nc":
        return "cc_by_nc"
    if raw == "cc by-nc-nd":
        return "cc_by_nc_nd"
    if raw in ("cc by-sa", "cc by-nc-sa"):
        return "other"  # not one of the spec's named buckets; grouped as other
    if raw == "cc0":
        return "other"  # spec buckets don't list cc0 separately; see summary note
    return "other"


def main():
    with (HERE / "journals_resolved.csv").open() as f:
        journals = list(csv.DictReader(f))
    with (HERE / "step2_yearly_counts.csv").open() as f:
        yearly = list(csv.DictReader(f))
    with (HERE / "step3_supp_manifest.csv").open() as f:
        sample = list(csv.DictReader(f))
    with (HERE / "step4_license.csv").open() as f:
        licenses = list(csv.DictReader(f))

    sample_by_journal = defaultdict(list)
    for r in sample:
        sample_by_journal[r["journal"]].append(r)
    license_by_journal = defaultdict(list)
    for r in licenses:
        license_by_journal[r["journal"]].append(r["license_raw"])

    j_by_title = {j["title_queried"]: j for j in journals}

    # Per-journal sample summary (Step 3 + Step 4 rollup)
    journal_summary = {}
    for title, recs in sample_by_journal.items():
        n = len(recs)
        has_supp = sum(1 for r in recs if int(r["n_files"] or 0) > 0)
        has_data = 0
        ambig_only = 0
        data_file_counts = []
        for r in recs:
            exts = exts_of(r["manifest"])
            d = exts & DATA_EXT
            if d:
                has_data += 1
                if d <= AMBIG_EXT:
                    ambig_only += 1
                # count of data-like files (not just extensions) for median
                n_data_files = sum(
                    1 for name in r["manifest"].split(";")
                    if name and ("." + name.rsplit(".", 1)[-1].lower()) in DATA_EXT
                )
                data_file_counts.append(n_data_files)
        data_file_counts.sort()
        median_data_files = (
            data_file_counts[len(data_file_counts) // 2] if data_file_counts else None
        )

        lic_counts = Counter(license_bucket(l) for l in license_by_journal.get(title, []))
        lic_total = sum(lic_counts.values()) or 1

        journal_summary[title] = {
            "sample_n": n,
            "pct_with_supp": round(100 * has_supp / n, 1) if n else None,
            "pct_with_data_like_supp": round(100 * has_data / n, 1) if n else None,
            "pct_data_like_ambiguous_only": round(100 * ambig_only / n, 1) if n else None,
            "median_data_files": median_data_files,
            "pct_cc_by": round(100 * lic_counts["cc_by"] / lic_total, 1),
            "pct_cc_by_nc": round(100 * lic_counts["cc_by_nc"] / lic_total, 1),
            "pct_cc_by_nc_nd": round(100 * lic_counts["cc_by_nc_nd"] / lic_total, 1),
            "pct_license_other": round(100 * lic_counts["other"] / lic_total, 1),
            "pct_license_unknown": round(100 * lic_counts["unknown"] / lic_total, 1),
        }

    springer_key_present = bool(os.environ.get("SPRINGER_API_KEY"))

    out_rows = []
    for y in yearly:
        title = y["journal"]
        j = j_by_title.get(title, {})
        js = journal_summary.get(title, {})
        out_rows.append({
            "journal": title,
            "issn_l": y["issn_l"],
            "publisher": y["publisher"],
            "in_pmc": "TRUE" if (y["n_records"] and int(y["n_records"]) > 0) else "UNKNOWN",
            "pmc_deposit_scope_proxy": j.get("pmc_deposit_ratio_2023_proxy", ""),
            "year": y["year"],
            "n_records": y["n_records"],
            "n_fulltext": y["n_fulltext"],
            "n_oa": y["n_oa"],
            "pct_fulltext": y["pct_fulltext"],
            "pct_oa": y["pct_oa"],
            "springer_oa_n": "" if not springer_key_present else "NA",
            "sample_n": js.get("sample_n", ""),
            "pct_with_supp": js.get("pct_with_supp", ""),
            "pct_with_data_like_supp": js.get("pct_with_data_like_supp", ""),
            "pct_data_like_ambiguous_only": js.get("pct_data_like_ambiguous_only", ""),
            "median_data_files": js.get("median_data_files", ""),
            "pct_cc_by": js.get("pct_cc_by", ""),
            "pct_cc_by_nc": js.get("pct_cc_by_nc", ""),
            "pct_cc_by_nc_nd": js.get("pct_cc_by_nc_nd", ""),
            "pct_license_other": js.get("pct_license_other", ""),
            "pct_license_unknown": js.get("pct_license_unknown", ""),
        })

    out_path = HERE / "journal_yield.csv"
    with out_path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()))
        w.writeheader()
        w.writerows(out_rows)
    print(f"Wrote {len(out_rows)} rows to {out_path}")


if __name__ == "__main__":
    main()
