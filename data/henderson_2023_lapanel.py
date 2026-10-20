"""
Henderson (2023) — Louisiana COVID-19 five-wave panel ("Persisting Anxiety").

Source: Harvard Dataverse, "Replication Data for: 'Persisting Anxiety: The
        Duration of Emotions during the COVID-19 Pandemic'" (Public Opinion
        Quarterly). Michael Henderson, Louisiana State University.
DOI:    10.7910/DVN/QIEEJU
Data:   masterfile_wide.dta (format=original), 2,862 panel rows x 1,223 cols;
        ~1,000-1,025 respondents actually present per wave (present_w1..w5).
License: CC0 1.0 (confirmed on the Dataverse landing page / API
        latestVersion.license.rightsIdentifier == "CC0-1.0").

Item text: NOT extracted here. Full English item stems are present in the
        Stata variable labels (checked: `meta.column_names_to_labels` for
        q2_w1..q10_w1/q164_w1/q165_w1, q11_w1..q19_w1, q20_w1..q27_w1,
        q29_w1..q37_w1, q43_w1..q51_w1, q155_w1..q158_w1, q225_w5..q234_w5)
        and the 1-5 response options are in the Stata value labels (checked:
        `meta.value_labels` for Q2_W1, Q11_W1, Q20_W1, Q29_W1, Q43_W1,
        Q155_W1, Q225_W5). Item text is therefore cheap but is deliberately
        held: the racial-resentment battery (Kinder & Sanders) has no row in
        itemtext/instrument_rights_register.csv, and TIPI (Gosling, Rentfrow
        & Swann) needs a by-name register check that has not been done.
        Response tables ship now; item text is a separate follow-up.

Geographic columns DROPPED under the 2026-10-20 ruling (geographic/
        administrative codes are not carried into the IRW in any form — not
        as cov_*, not hashed, not truncated):
            inputzip_w1..inputzip_w5   (full 5-digit US residence ZIP)
            parish_name_w1..parish_name_w5
            parish_fips_w1..parish_fips_w5
        Names/emails: none present (string-column PII screen below).

IMPORTANT — overlap with 10.7910/DVN/1IWRQA. The ReadMe for this deposit
        points at 10.7910/DVN/1IWRQA as the project depository holding the
        per-wave survey files and codebooks: it is the SAME panel. All 1,000
        ids in each of the eight staged `henderson_2023_la_covid_*` tables
        built from 1IWRQA are wave-1 `caseid_w1` values in this file
        (1000/1000 match). These tables are the five-wave superset, keyed on
        the cross-wave `panelnum` with an explicit `wave` column. Ship these
        OR those, never both.

Output: one table per instrument, long format, `wave` as its own column.
        Nine tables: the seven batteries analysed in the paper plus the
        `comfort` and `policy_support` batteries, which exist in all five
        waves of this file and would otherwise have been lost when the
        wave-1-only 1IWRQA tables were dropped as duplicates.
"""

import sys
import os


import numpy as np
import pandas as pd
import pyreadstat

from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from irw_validate._checks import run_qc  # noqa: E402

DTA = sys.argv[1]
OUTDIR = sys.argv[2]

# battery -> (item suffix per question number, waves)
BATTERIES = {
    "health_emotion": {
        2: "anxious", 3: "worried", 4: "afraid", 5: "angry", 6: "outraged",
        7: "annoyed", 8: "relaxed", 9: "hopeful", 10: "optimistic",
        164: "skeptical", 165: "convinced",
    },
    "econ_emotion": {
        11: "anxious", 12: "worried", 13: "afraid", 14: "angry", 15: "outraged",
        16: "annoyed", 17: "relaxed", 18: "hopeful", 19: "optimistic",
    },
    "worry": {
        20: "family_sick", 21: "family_die", 22: "hospital_equipment",
        23: "health_system_overrun", 24: "pay_bills", 25: "lose_income",
        26: "local_business_close", 27: "economy_recession",
    },
    "health_threat": {
        29: "you", 30: "blacks", 31: "whites", 32: "over60", 33: "under40",
        34: "wealthy", 35: "poor", 36: "rural", 37: "cities",
    },
    "fin_threat": {
        43: "you", 44: "blacks", 45: "whites", 46: "over60", 47: "under40",
        48: "wealthy", 49: "poor", 50: "rural", 51: "cities",
    },
    # 1-4 (Very comfortable .. Very uncomfortable). q93 ("Sending your children
    # to school or daycare outside your home") carries a per-item screen: it was
    # asked only of respondents with children under 18, so it has ~300-330
    # responses per wave against ~1,000 for its 13 siblings. That is a
    # legitimate skip pattern in the instrument, not missingness to repair.
    "comfort": {
        80: "retail_store", 81: "restaurant", 82: "bar", 83: "workplace",
        84: "salon", 85: "large_event", 86: "visit_friends",
        87: "religious_service", 88: "group_meeting", 89: "campaign_rally",
        90: "protest", 91: "public_meeting", 92: "vote_in_person",
        93: "children_school",
    },
    # 1-5 (Strongly support .. Strongly oppose)
    "policy_support": {
        95: "unemployment_funding", 96: "mask_requirement",
        97: "limit_workers_customers", 98: "vaccine_requirement",
        99: "quarantine_positive", 100: "business_relief",
        101: "vote_by_mail", 102: "contact_info_collection",
        103: "eviction_ban",
    },
    "racial_resent": {
        155: "other_minorities", 156: "slavery_conditions",
        157: "less_than_deserve", 158: "not_trying_hard",
    },
    "tipi": {
        225: "extraverted", 226: "critical", 227: "dependable", 228: "anxious",
        229: "open", 230: "reserved", 231: "sympathetic", 232: "disorganized",
        233: "calm", 234: "conventional",
    },
}

WAVES = [1, 2, 3, 4, 5]
SENTINELS = {8, 9}  # 8 = skipped, 9 = not asked (Stata value labels)

df, meta = pyreadstat.read_dta(DTA)
print(f"source shape: {df.shape}")

# ---------------------------------------------------------------- PII screen
# NOTE: pd.api.types.is_string_dtype, NOT `dtype == object` — on pyreadstat
# frames the latter matches nothing and reports a clean file.
string_cols = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
print(f"PII screen: examined {len(string_cols)} string column(s)")
assert len(string_cols) > 0, "PII screen examined zero columns — screen is broken"

EMAIL = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
NAME_HINT = ("name", "email", "mail", "fname", "lname", "surname", "firstname",
             "lastname", "contact", "phone")
pii_hits = []
for c in string_cols:
    s = df[c].dropna().astype(str)
    if s.empty:
        continue
    if s.str.contains(EMAIL, regex=True, na=False).any():
        pii_hits.append((c, "email pattern in values"))
    lab = (meta.column_names_to_labels.get(c) or "").lower()
    if any(h in c.lower() for h in NAME_HINT) or any(h in lab for h in NAME_HINT):
        # parish_name_* is a place name, not a person name; dropped as geo anyway
        if not c.startswith("parish_name"):
            pii_hits.append((c, f"name/contact-like column (label={lab!r})"))
print(f"PII screen: {len(pii_hits)} hit(s): {pii_hits}")
assert not pii_hits, f"PII detected — stop, do not ship: {pii_hits}"

# -------------------------------------------------------------- build tables
ID = "panelnum"
assert df[ID].notna().all() and df[ID].nunique() == len(df), "panelnum not a clean key"

used_cols = {ID}
written = {}

for table, qmap in BATTERIES.items():
    frames = []
    for w in WAVES:
        cols = {f"q{q}_w{w}": name for q, name in qmap.items()
                if f"q{q}_w{w}" in df.columns}
        if not cols:
            continue
        used_cols.update(cols)
        sub = df[[ID] + list(cols)].copy()
        sub = sub.rename(columns=cols)
        long = sub.melt(id_vars=[ID], var_name="item", value_name="resp")
        long["wave"] = w
        frames.append(long)
    out = pd.concat(frames, ignore_index=True)
    out = out.dropna(subset=["resp"])
    out["resp"] = out["resp"].astype(float)
    n_sent = out["resp"].isin(SENTINELS).sum()
    out = out[~out["resp"].isin(SENTINELS)]
    out["resp"] = out["resp"].astype(int)
    out = out.rename(columns={ID: "id"})
    out["id"] = out["id"].astype("int64")
    out = out[["id", "item", "resp", "wave"]].sort_values(["id", "wave", "item"])
    if out["wave"].nunique() == 1:
        # TIPI was administered only in wave 5; a constant wave column carries
        # no information, so drop it rather than ship a degenerate column.
        out = out.drop(columns=["wave"])

    name = f"henderson_2023_lapanel_{table}"
    assert len(name) <= 40, f"table name too long: {name} ({len(name)})"
    assert out["resp"].between(1, 5).all(), f"{name}: resp outside 1-5"
    rng = out.groupby("item")["resp"].agg(["min", "max", "count"])
    if rng["min"].nunique() > 1 or rng["max"].nunique() > 1:
        print(f"  {name}: item ranges differ -> "
              f"{sorted(set(zip(rng['min'], rng['max'])))}")
    assert out["id"].nunique() >= 100, f"{name}: fewer than 100 ids"
    assert out["item"].nunique() >= 3, f"{name}: fewer than 3 items"
    path = os.path.join(OUTDIR, name + ".csv")
    _checks = run_qc(out)
    _fails = [(c.name, c.detail) for c in _checks if c.status == "fail"]
    assert not _fails, (name, _fails)
    for _c in _checks:
        if _c.status == "warn":
            print(f"  [qc warn] {name} {_c.name}: {_c.detail[:180]}")
    out.to_csv(path, index=False)
    written[name] = out
    print(f"{name}: {len(out)} rows, {out['id'].nunique()} ids, "
          f"{out['item'].nunique()} items, "
          f"waves {sorted(out['wave'].unique()) if 'wave' in out else '[5] (no wave column: single wave)'}, "
          f"{n_sent} sentinel (8/9) cells dropped")

assert len(set(written)) == len(written), "duplicate output table names"

# ----------------------------------------------------- balance the books
GEO_PREFIX = ("inputzip", "parish_name", "parish_fips")
reasons = {}
for c in df.columns:
    if c in used_cols:
        reasons[c] = None
        continue
    if c.startswith(GEO_PREFIX):
        reasons[c] = "DROPPED: geographic/administrative code (2026-10-20 ruling)"
    elif c.startswith("caseid_w"):
        reasons[c] = "skipped: wave-specific respondent id, superseded by panelnum"
    elif c.startswith(("present_w", "weight_w")) or c == "whichwaves":
        reasons[c] = "skipped: survey design / panel-participation bookkeeping"
    elif c.startswith(("cases_cumm", "cases_curr", "parishpop", "ur_w")):
        reasons[c] = "skipped: merged parish-level contextual aggregate, not a response"
    elif c.startswith("q"):
        reasons[c] = "skipped: survey item outside the nine scored batteries shipped here"
    else:
        reasons[c] = "skipped: administrative / media-insert / experiment-plumbing column"

unaccounted = [c for c, r in reasons.items() if r is None and c not in used_cols]
assert not unaccounted, unaccounted
assert set(reasons) == set(df.columns), "column accounting incomplete"

from collections import Counter
print("\ncolumn accounting (all %d source columns):" % len(df.columns))
print(f"  OUTPUT (id + battery items): {len(used_cols)}")
for r, n in Counter(r for r in reasons.values() if r).most_common():
    print(f"  {n:5d}  {r}")
assert len(used_cols) + sum(1 for r in reasons.values() if r) == len(df.columns) + 0, \
    "books do not balance"
print("books balance.")
