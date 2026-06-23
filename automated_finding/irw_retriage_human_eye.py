"""
Second-pass retriage of the "Automated queue - Human eye" CSV.

Rules applied to rows with refined_flag='human_review':
  1. resp has >50 unique values  → aggregate_continuous
  2. dup_id_item + bad license   → license_restricted
  3. dup_id_item + valid license → worth_retrying
  4. formatting-failed + bad license → license_restricted
  (all others stay human_review)

Bad license = UUID hex string, 'unknown', or explicitly restricted text.
"""

from __future__ import annotations

import csv
import re
from collections import Counter
from pathlib import Path

INPUT       = Path.home() / "Downloads" / "Automated queue - Human eye.csv"
OUTPUT      = Path.home() / "Downloads" / "Automated queue - Human eye.csv"
RETRY_QUEUE = Path(__file__).parent / "irw_retry_queue.csv"


def is_uuid(s: str) -> bool:
    return bool(re.match(r"^[0-9a-f]{24}$", s.strip().lower()))


def is_restricted(s: str) -> bool:
    return "not-to-be-distributed" in s or "limited-information" in s


def is_bad_license(lic: str) -> bool:
    lic = lic.strip().lower()
    return is_uuid(lic) or is_restricted(lic) or lic in ("unknown", "")


with open(INPUT, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    rows = list(reader)

counts = Counter()

for r in rows:
    if "human_review" not in r.get("refined_flag", ""):
        continue

    reasons = r.get("reasons", "")
    lic     = r.get("license", "")

    # Rule 1: continuous data
    if "resp has >50 unique values" in reasons:
        r["refined_flag"]   = "aggregate_continuous"
        r["refined_reason"] = "resp has >50 unique values after melt — likely continuous/aggregate data, not ordinal item responses"
        counts["aggregate_continuous"] += 1
        continue

    # Rules 2 & 3: dup_id_item
    if "QC failed on: dup_id_item" in reasons:
        if is_bad_license(lic):
            r["refined_flag"]   = "license_restricted"
            r["refined_reason"] = "dup_id_item failure with unrecognised or restricted license — skip per IRW policy"
            counts["license_restricted"] += 1
        else:
            r["refined_flag"]   = "worth_retrying"
            r["refined_reason"] = "dup_id_item failure with valid open license — likely longitudinal; retry with wave/timepoint detection"
            counts["worth_retrying"] += 1
        continue

    # Rule 4: formatting failed + bad license
    if "Automatic IRW formatting failed" in reasons and is_bad_license(lic):
        r["refined_flag"]   = "license_restricted"
        r["refined_reason"] = "column mapping failed and license is unrecognised or restricted — skip per IRW policy"
        counts["license_restricted"] += 1
        continue

with open(OUTPUT, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

# Write worth_retrying rows to a separate queue for irw_retry_dup.py
retry_rows = [r for r in rows if r.get("refined_flag") == "worth_retrying"]
if retry_rows:
    with open(RETRY_QUEUE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(retry_rows)
    print(f"Retry queue → {RETRY_QUEUE} ({len(retry_rows)} rows)")

print("Changes applied:")
for k, v in sorted(counts.items(), key=lambda x: -x[1]):
    print(f"  {k}: {v}")
print(f"  (unchanged human_review: {sum(1 for r in rows if 'human_review' in r.get('refined_flag',''))})")
print(f"Total rows: {len(rows)}")
