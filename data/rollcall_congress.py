#!/usr/bin/env python3
# rollcall_house / rollcall_senate -- US congressional roll-call votes, one
# table per chamber spanning every Congress built (default 110th-118th,
# 2007-2024), from the chambers' own XML records (irw#2445).
#
# Sources (US government records; see "Rights" below):
#   House: Office of the Clerk, https://clerk.house.gov/evs/<year>/roll<NNN>.xml
#          (electronic voting system, 1990 onward). DTD and field dictionary:
#          https://xml.house.gov/rollcall/vote-metadata.html
#   Senate: Secretary of the Senate, LIS roll-call XML,
#          https://www.senate.gov/legislative/LIS/roll_call_votes/
#          vote<congress><session>/vote_<congress>_<session>_<NNNNN>.xml
#          (101st Congress, 1989, onward), enumerated from the session menus
#          https://www.senate.gov/legislative/LIS/roll_call_lists/vote_menu_<congress>_<session>.xml
#   Senate-id crosswalk: unitedstates/congress-legislators
#          (https://github.com/unitedstates/congress-legislators), CC0 1.0,
#          legislators-current.csv + legislators-historical.csv.
#
# Rights: roll-call records are compiled by the House Tally Clerks and the
# Senate Bill Clerk in their official duties -- works of the US Government,
# which have no copyright in the US (17 U.S.C. 105). Neither chamber's site
# states a licence, so this rests on the statutory reading, not a stated
# licence; the crosswalk is CC0. NOT Voteview: Voteview states no licence, and
# the Duck-Mayr & Montgomery (2023) CC0 deposit (doi:10.7910/DVN/HXORK9)
# cannot relicense it, so nothing here comes from either.
#
# Usage:
#   python3 data/rollcall_congress.py                    # Congresses 110-118
#   python3 data/rollcall_congress.py --congress 101-118 --chamber senate
# House XML starts in 1990, so the House 101st is partial (2nd session only);
# the script refuses House Congresses before 102. Raw XML is cached (gzip) in
# --cache (default ~/.cache/irw_rollcall) so reruns do not refetch.
#
# Shape:
#   id    member's bioguide ID. House XML carries it as legislator@name-id;
#         Senate XML carries lis_member_id, mapped to bioguide through the
#         crosswalk (every Senate member in 110-118 maps; the script stops if
#         one does not). The same person keeps the same id across Congresses
#         and chambers, so a member who served several Congresses answers
#         several blocks of items: each chamber is deliberately one long panel,
#         not one table per Congress (two tables against the 1000-table cap,
#         and dynamic ideal-point models need the linkage). Subset a Congress
#         by item prefix, e.g. items starting "118_".
#   item  <congress>_<session>_<rollnumber>, roll number zero-padded to 4
#         (House) or 5 (Senate) digits as in the source file names, e.g.
#         118_1_0042. Sessions follow the XML, not the calendar: a vote taken
#         on 1 Jan 2013 belongs to the 112th Congress, 2nd session.
#   resp  1 = Yea / Aye (and Guilty in impeachment trials), 0 = Nay / No
#         (Not Guilty). "Present", "Not Voting" and Senate live pairs
#         ("Present, Giving Live Pair") are missing and those rows are dropped,
#         as in the 2023 data/rollcall.R. So resp is "voted for the question as
#         put", and the question is sometimes a motion to table or to
#         recommit -- direction is NOT harmonised to any ideology; ideal-point
#         models estimate each vote's direction. Unfolding / ideal-point data:
#         do not reverse-key.
#   date  Unix time of the vote (House action-date + action-time, Senate
#         vote_date; both Eastern time).
#   cov_party   party letter as the XML records it for that vote (D, R, I;
#               Senate also ID). A member who switched party carries both, on
#               different rows (6 House and 3 Senate members in 110-118).
#   cov_state   two-letter state or territory code.
#
# Votes dropped whole (logged at run time): House quorum calls (vote-type
# QUORUM, everyone answers "Present") and House elections of the Speaker
# (votes are candidate names, not yea/nay). Any other vote whose casts fall
# outside the mapping above is dropped and reported, not guessed. Delegates and
# the Resident Commissioner never appear in the Clerk files for 110-118, so
# every House id is a voting Representative.
#
# Every remaining vote is kept, including lopsided and unanimous ones (a
# unanimous vote has no information for an IRT model but is part of the
# record). Duck-Mayr & Montgomery (2023) drop votes with <1% of members in the
# minority, members missing >90% of votes, and unanimous votes; filter on
# (item, resp) to reproduce that.

import argparse
import datetime as dt
import gzip
import io
import os
import re
import sys
import threading
import time
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from zoneinfo import ZoneInfo

import pandas as pd
import requests

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from irw_validate.compat import run_qc  # noqa: E402

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
EASTERN = ZoneInfo("America/New_York")
XWALK = "https://unitedstates.github.io/congress-legislators/legislators-{}.csv"

YES = {"Yea", "Aye", "Guilty"}
NO = {"Nay", "No", "Not Guilty"}
MISSING = {"Present", "Not Voting", "Present, Giving Live Pair"}

SESSION = {"1st": 1, "2nd": 2, "3rd": 3}


_LOCK = threading.Lock()
_LAST = [0.0]
PAUSE = 1.0  # seconds between requests; senate.gov answers 403 to bursts


def throttle():
    with _LOCK:
        wait = _LAST[0] + PAUSE - time.monotonic()
        if wait > 0:
            time.sleep(wait)
        _LAST[0] = time.monotonic()


def fetch(url, cache_path, session, tries=8):
    """Return bytes for url (cached gzip), or None on a 404."""
    if os.path.exists(cache_path):
        with gzip.open(cache_path, "rb") as f:
            return f.read()
    for k in range(tries):
        throttle()
        try:
            r = session.get(url, headers=UA, timeout=20)
        except requests.RequestException as e:
            print(f"  {type(e).__name__} on {url}", file=sys.stderr)
            time.sleep(2 ** k)
            continue
        if r.status_code == 404:
            return None
        # House files open with a UTF-8 byte-order mark
        if r.status_code == 200 and r.content.lstrip(b"\xef\xbb\xbf \r\n\t").startswith(b"<?xml"):
            os.makedirs(os.path.dirname(cache_path), exist_ok=True)
            tmp = cache_path + ".tmp"
            with gzip.open(tmp, "wb") as f:
                f.write(r.content)
            os.replace(tmp, cache_path)
            return r.content
        # 200 with an HTML page is the sites' soft 404 / error shell
        if r.status_code == 200:
            return None
        # 403/429 are rate limiting here, not a missing file
        wait = min(30 * 2 ** k, 900)
        print(f"  HTTP {r.status_code} on {url}; retry in {wait}s", file=sys.stderr)
        time.sleep(wait)
    raise RuntimeError(f"failed after {tries} tries: {url}")


def map_cast(v):
    v = v.strip()
    if v in YES:
        return 1
    if v in NO:
        return 0
    if v in MISSING:
        return None
    raise ValueError(v)


# ------------------------------------------------------------------ House ---

def house_years(congress):
    first = 1789 + 2 * (congress - 1)
    # a vote on 1-2 Jan of the following odd year can still belong to this
    # Congress; the Clerk files it under the earlier year, but look anyway
    return [first, first + 1]


def house_votes(congress, cache, session, dropped):
    rows = []
    for year in house_years(congress):
        n, misses = 0, 0
        def get(k):
            return k, fetch(f"https://clerk.house.gov/evs/{year}/roll{k:03d}.xml",
                            os.path.join(cache, "house", str(year), f"roll{k:04d}.xml.gz"),
                            session)
        k = 1
        with ThreadPoolExecutor(4) as ex:
            while misses < 3:
                batch = list(ex.map(get, range(k, k + 40)))
                for num, raw in batch:
                    if raw is None:
                        misses += 1
                        continue
                    misses = 0
                    n += 1
                    rows.extend(parse_house(raw, congress, dropped))
                k += 40
        print(f"  house {year}: {n} roll-call files", file=sys.stderr)
        if n == 0:
            raise RuntimeError(f"house {year}: no roll-call files found")
    return rows


def parse_house(raw, congress, dropped):
    root = ET.fromstring(raw)
    md = root.find("vote-metadata")
    c = int(md.findtext("congress"))
    if c != congress:
        return []
    sess = SESSION[md.findtext("session").strip()]
    num = int(md.findtext("rollcall-num"))
    item = f"{c}_{sess}_{num:04d}"
    vtype = (md.findtext("vote-type") or "").strip().upper()
    if vtype == "QUORUM" or "SPEAKER" in vtype:
        dropped.append((item, vtype))
        return []
    date = md.findtext("action-date").strip()
    t = md.find("action-time")
    hm = t.get("time-etz") if t is not None and t.get("time-etz") else "12:00"
    ts = dt.datetime.strptime(f"{date} {hm}", "%d-%b-%Y %H:%M").replace(tzinfo=EASTERN)
    out = []
    try:
        for rv in root.iter("recorded-vote"):
            leg = rv.find("legislator")
            resp = map_cast(rv.findtext("vote"))
            if resp is None:
                continue
            out.append((leg.get("name-id"), item, resp, int(ts.timestamp()),
                        leg.get("party"), leg.get("state")))
    except ValueError as e:
        dropped.append((item, f"{vtype}: unmapped cast {e}"))
        return []
    return out


# ----------------------------------------------------------------- Senate ---

def senate_votes(congress, cache, session, dropped, lis2bio):
    rows = []
    for sess in (1, 2, 3):
        menu = fetch(f"https://www.senate.gov/legislative/LIS/roll_call_lists/vote_menu_{congress}_{sess}.xml",
                     os.path.join(cache, "senate", f"menu_{congress}_{sess}.xml.gz"), session)
        if menu is None:
            continue
        nums = sorted(int(v.findtext("vote_number")) for v in ET.fromstring(menu).iter("vote"))
        def get(k):
            return fetch(f"https://www.senate.gov/legislative/LIS/roll_call_votes/vote{congress}{sess}/vote_{congress}_{sess}_{k:05d}.xml",
                         os.path.join(cache, "senate", f"{congress}_{sess}", f"vote_{k:05d}.xml.gz"),
                         session)
        with ThreadPoolExecutor(4) as ex:
            raws = list(ex.map(get, nums))
        missing = [k for k, r in zip(nums, raws) if r is None]
        if missing:
            raise RuntimeError(f"senate {congress}-{sess}: menu lists votes with no XML: {missing[:10]}")
        for raw in raws:
            rows.extend(parse_senate(raw, dropped, lis2bio))
        print(f"  senate {congress}-{sess}: {len(nums)} roll-call files", file=sys.stderr)
    return rows


def parse_senate(raw, dropped, lis2bio):
    root = ET.fromstring(raw)
    c = int(root.findtext("congress"))
    sess = int(root.findtext("session"))
    num = int(root.findtext("vote_number"))
    item = f"{c}_{sess}_{num:05d}"
    date = re.sub(r"\s+", " ", root.findtext("vote_date").strip())
    ts = dt.datetime.strptime(date, "%B %d, %Y, %I:%M %p").replace(tzinfo=EASTERN)
    out = []
    try:
        for m in root.iter("member"):
            resp = map_cast(m.findtext("vote_cast"))
            if resp is None:
                continue
            lis = m.findtext("lis_member_id").strip()
            if lis not in lis2bio:
                raise RuntimeError(f"{item}: lis_member_id {lis} not in crosswalk")
            out.append((lis2bio[lis], item, resp, int(ts.timestamp()),
                        m.findtext("party").strip(), m.findtext("state").strip()))
    except ValueError as e:
        dropped.append((item, f"unmapped cast {e}"))
        return []
    return out


def load_crosswalk(session):
    frames = []
    for which in ("current", "historical"):
        r = session.get(XWALK.format(which), headers=UA, timeout=120)
        r.raise_for_status()
        frames.append(pd.read_csv(io.StringIO(r.text), dtype=str,
                                  usecols=["bioguide_id", "lis_id"]))
    x = pd.concat(frames).dropna()
    return dict(zip(x["lis_id"], x["bioguide_id"]))


# ------------------------------------------------------------------- main ---

def parse_range(s):
    if "-" in s:
        a, b = s.split("-")
        return list(range(int(a), int(b) + 1))
    return [int(v) for v in s.split(",")]


def main():
    global PAUSE
    ap = argparse.ArgumentParser()
    ap.add_argument("--congress", default="110-118")
    ap.add_argument("--chamber", choices=["house", "senate", "both"], default="both")
    ap.add_argument("--cache", default=os.path.expanduser("~/.cache/irw_rollcall"))
    ap.add_argument("--out", default=OUT_DIR)
    ap.add_argument("--pause", type=float, default=PAUSE,
                    help="seconds between requests")
    a = ap.parse_args()
    PAUSE = a.pause
    os.makedirs(a.out, exist_ok=True)
    session = requests.Session()
    chambers = ["house", "senate"] if a.chamber == "both" else [a.chamber]
    lis2bio = load_crosswalk(session) if "senate" in chambers else None
    cols = ["id", "item", "resp", "date", "cov_party", "cov_state"]
    for ch in chambers:
        rows, ndrop = [], 0
        for congress in parse_range(a.congress):
            if ch == "house" and congress < 102:
                print(f"skip house {congress}: Clerk XML starts in 1990", file=sys.stderr)
                continue
            dropped = []
            print(f"{ch} {congress}", file=sys.stderr)
            if ch == "house":
                got = house_votes(congress, a.cache, session, dropped)
            else:
                got = senate_votes(congress, a.cache, session, dropped, lis2bio)
            for item, why in dropped:
                print(f"  dropped {item}: {why}", file=sys.stderr)
            print(f"  {ch} {congress}: {len(got):,} rows, "
                  f"{len({r[1] for r in got})} items, {len(dropped)} votes dropped",
                  file=sys.stderr)
            rows.extend(got)
            ndrop += len(dropped)
        df = pd.DataFrame(rows, columns=cols)
        if df["id"].isna().any() or (df["id"] == "").any():
            raise RuntimeError(f"{ch}: rows without a member id")
        dup = df.duplicated(["id", "item"]).sum()
        if dup:
            raise RuntimeError(f"{ch}: {dup} duplicate id-item rows")
        df = df.sort_values(["item", "id"]).reset_index(drop=True)
        bad = [c for c in run_qc(df) if c.status == "fail"]
        if bad:
            raise RuntimeError(f"{ch}: {[(c.name, c.detail) for c in bad]}")
        name = f"rollcall_{ch}"
        df.to_csv(os.path.join(a.out, f"{name}.csv"), index=False)
        print(f"  {name}: {len(df):,} rows, {df['id'].nunique()} ids, "
              f"{df['item'].nunique()} items, {ndrop} votes dropped", file=sys.stderr)

if __name__ == "__main__":
    main()
