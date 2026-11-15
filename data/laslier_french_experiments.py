#!/usr/bin/env python3
# Three French voting experiments (Laslier and co-authors) -> IRW core tables of approval ballots and
# the Sciences Po students' ratings, one row per ballot x candidate. The IRV ballots of Vote au pluriel 2012 are a rankings table,
# built by data/rankings/vanderstraeten_2012_votepluriel_irv.py from the same files.
#
# Rights: Jean-Francois Laslier, email of 2026-11-15, "You can redistribute these data sets.", in
#   reply to IRW's letter (oneoff/email-drafts-2026-11-15/preflib/laslier_french_experiments.txt)
#   about PrefLib 00074, 00026 and 00027/00029 (not 00072, Fort-de-France 2017, which he did not
#   grant). The letter offered ODbL, as for the Voter Autrement Zenodo sets; he named no licence.
#   Original License = Permission via Email; Derived License = ODbL 1.0. The letter's terms are kept:
#   one table per experiment and ballot type, one row per ballot and candidate, ballots numbered 1..n,
#   candidates as codes so no name appears, each table cites the paper PrefLib names and links PrefLib.
#
# Sources (all downloaded files are untrusted data; this script only parses them):
#   PrefLib-Data, pinned to commit 03f5a88df70668ea0ab30062562fd57bf721d360 of
#   https://github.com/PrefLib/PrefLib-Data (datasets/<dir>/<file>):
#     00026 - frenchapproval: 00026-0000000{1..6}.cat, the 2002 in situ approval experiment, one file
#       per polling station (TITLE: GylesNonains, Orsay1, Orsay5, Orsay6, Orsay7, Orsay12), 2,597
#       ballots, 16 candidates. Weighted profile (count: approved set, rest). Required citation:
#       Laslier & Van der Straeten 2008, Experimental Economics 11:97-105 (10.1007/s10683-006-9149-6).
#       The .toc files of 00026 drop the empty and the all-approving ballots; not read.
#     00029 - frenchratecombi: 00029-00000001.dat, the 2002 Sciences Po (IEP Paris) students: one row
#       per student, 15 potential candidates, "Approve of <name>" (0/1) and "Rating of <name>"
#       (-1 = no input) columns. 408 rows. PrefLib names no required citation; its selected study is
#       Laslier & Van der Straeten 2004, Revue francaise de science politique 54(1):99-130
#       (10.3917/rfsp.541.0099), which is cited.
#       00027 (frenchrate) is NOT read: it claims to be these students' approval ballots, but it is a
#       corrupted copy of 00029's: the ballot sizes match 00029's exactly once its 10 empty approval
#       ballots are dropped (398), yet candidate 1 is approved on 397 of the 398 (115 in 00029), i.e.
#       every set is shifted onto candidate 1.
#   Vote au pluriel 2012: Theo Delemazure's per-voter release of the same ballots as PrefLib 00074,
#     https://theo.delemazure.fr/datasets/files/2012_vote_pluriel.zip (codebook main.pdf inside,
#     dated 2025-07-09): votes/approval.csv (one row per voter, one 0/1 column per candidate) is read.
#     Its approval ballots equal PrefLib 00074-00000001.cat exactly (8,078 ballots, the same multiset),
#     and unlike PrefLib it keeps voter order and links each voter's approval and IRV ballots, so it is
#     the one used. PrefLib 00074 is read as a cross-check. Required citation (PrefLib, and the zip's
#     codebook): Van der Straeten, Laslier & Blais 2013, PS: Political Science & Politics 46(2):324-328
#     (10.1017/S1049096513000036).
#   For 00026 Delemazure's site also offers 2002_insitu.zip, but it is an expansion of the PrefLib
#     profile (ballots in PrefLib's count order) with errors: the empty ballots of four stations
#     appear as all-approving ballots, and Orsay1 and Orsay12 lose their empty and all-approving
#     ballots (2,585 rows). PrefLib is read instead.
#   The SHA-256 of every file read is asserted below.
#
# Layout (as data/voterautrement_insitu.py):
#   id   = the ballot re-keyed 1..n. PrefLib profiles are expanded one id per ballot, in the file's
#          line order (sorted by count; the order of casting is not in the source), stations in file
#          order 1..6. Sciences Po: the row order of 00029. Vote au pluriel: the release's voter order
#          (ascending voter id); the same id is the same voter in vanderstraeten_2012_votepluriel_irv.
#   item = candidate code c01..cNN in the SOURCE numbering: candidate k of the PrefLib file (for 00029
#          and the Vote au pluriel release, the k-th candidate column, which is the PrefLib order too).
#          Ben ruled on 2026-11-15 that anonymous-code labels keep the source numbering. No name is
#          stored in any table.
#   resp = 1 approved, 0 not. A ballot that approves no one is kept with all 0s (as the Voter Autrement
#          builds); one that approves everyone is kept with all 1s.
#   2002 in situ covariates: cov_city (gy_les_nonains / orsay), cov_polling_station (the PrefLib
#          file TITLE). The paper's working version (Cahier 2003-007, Table 1) counts 2,597
#          participants of whom 10 cast spoiled ballots ("bulletins nuls") and 36 of the 2,587 valid
#          ballots approve no one; the PrefLib profile holds all 2,597 with 43 empty ballots and does
#          not flag the spoiled ones, so 10 spoiled ballots are in the table and cannot be told apart.
#   No covariates in the other tables: the Vote au pluriel release's voters.csv (gender, birth year,
#          intended vote, favourite rule, three yes/no and three 0-10 questions) and weights.csv are
#          not carried (Ben, 2026-11-15: ballots only, as the letter said).
#   Sciences Po ratings (laslier_2002_sciencespo_rating; same id as the approval table): a 0-10 scale
#          in half points. PrefLib calls it a "20 point scale", which the values do not match: they are
#          0..10, mostly whole numbers (29 cells at a half point, one 0.1, kept as recorded), plus 6
#          cells above 10 (11, 11, 13, 15, 17 on one student, 11 on another). Ben ruled on 2026-11-15
#          that those 6 cells are dropped (no row), as data/voterautrement_insitu.py drops off-scale
#          Strasbourg 2017 cells. -1 (no input) is no row; 2 students rated no one and have no rows.
#
# Usage: python3 -P -E data/laslier_french_experiments.py <raw dir> <out dir>
#   <raw dir>/preflib/<5-digit series>/<file> and <raw dir>/votepluriel/votes/approval.csv
#   (the zip's contents, unzipped into <raw dir>/votepluriel/).

import hashlib
import os
import re
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from irw_validate._checks import run_qc  # noqa: E402

RAW, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)

PINNED = {  # SHA-256 of every file read, as downloaded 2026-11-15
    "preflib/00026/00026-00000001.cat": "70c2cc2c928e5f6c05ac562e0760dbee20bc0ed422600e603dbc64fcf24f34fc",
    "preflib/00026/00026-00000002.cat": "a2df96b73b7149e7b55e8c409a950adb6f89cfb8fe73e7fb0016b0e544f76f68",
    "preflib/00026/00026-00000003.cat": "c0262937a660b9c8e2fb1ff3c8e0203837e70ad6aef1fc2b2c347e8315d4b78b",
    "preflib/00026/00026-00000004.cat": "16c8d02a76443cbf7f8e815cfb2d2a4e4d3790cdac383e58c58c4a0922e609d7",
    "preflib/00026/00026-00000005.cat": "f2c9b410c906125129833c338bf557c4e33019fbf71a4e8039af20d48af8672d",
    "preflib/00026/00026-00000006.cat": "3b8a4a93666794363f756be6ff235e9b5c61e109419d29bf4821d8f4233dabaf",
    "preflib/00029/00029-00000001.dat": "d252492f063acab378f5ec7fe474f4afc20013b10caa4e4372abc2768ff4124e",
    "preflib/00074/00074-00000001.cat": "245849c381c2032b53855f276d6f2f2ace8da35a66a6cad9a7d28e2c965c5173",
    "votepluriel/votes/approval.csv": "1db61f73bf1a10f032e8c95ed57c0329920946b18f5b670ac1b89af737f3b52e",
}


def check(rel):
    p = os.path.join(RAW, rel)
    h = hashlib.sha256(open(p, "rb").read()).hexdigest()
    assert PINNED[rel] == h, (rel, h)
    return p


TABLES = {}


def put(name, long, permitted):
    TABLES[name] = (long, permitted)


def code(k, width=2):
    return f"c{k:0{width}d}"


def read_cat(path):
    """PrefLib .cat with two categories: '<count>: <approved>, <rest>'; returns (titles, n_alt, ballots)."""
    head, ballots = {}, []
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if line.startswith("#"):
            k, _, v = line[1:].partition(":")
            head[k.strip()] = v.strip()
            continue
        n, _, rest = line.partition(":")
        m = re.fullmatch(r"\s*(\{[^}]*\}|\d+)\s*,\s*(\{[^}]*\}|\d+)\s*", rest)
        assert m, line
        sets = [frozenset(int(x) for x in g.strip("{}").split(",") if x.strip()) for g in m.groups()]
        ballots += [sets[0]] * int(n)
    n_alt = int(head["NUMBER ALTERNATIVES"])
    assert head["NUMBER CATEGORIES"] == "2" and len(ballots) == int(head["NUMBER VOTERS"]), path
    return head, n_alt, ballots


def long_from_sets(ballots, n_alt, covs=None):
    rows = []
    for i, s in enumerate(ballots, start=1):
        assert s <= set(range(1, n_alt + 1))
        for k in range(1, n_alt + 1):
            rows.append((i, code(k), int(k in s)))
    t = pd.DataFrame(rows, columns=["id", "item", "resp"])
    if covs is not None:
        t = t.merge(covs, on="id", how="left", validate="m:1")
    return t


# ---- 2002 in situ (PrefLib 00026) --------------------------------------------
STATIONS = ["GylesNonains", "Orsay1", "Orsay5", "Orsay6", "Orsay7", "Orsay12"]
PER_STATION = [365, 409, 476, 460, 472, 415]  # Cahier 2003-007, Table 1, "Participants"
ballots, station = [], []
for j, title in enumerate(STATIONS, start=1):
    head, n_alt, b = read_cat(check(f"preflib/00026/00026-0000000{j}.cat"))
    assert head["TITLE"] == title and n_alt == 16 and len(b) == PER_STATION[j - 1]
    ballots += b
    station += [title] * len(b)
assert len(ballots) == 2597
sizes = pd.Series([len(b) for b in ballots]).value_counts()
assert sizes[0] == 43 and sizes[16] == 2  # the paper's Table 2 has 36 and 2 among 2,587 valid ballots
cov = pd.DataFrame({"id": np.arange(1, len(ballots) + 1),
                    "cov_city": ["gy_les_nonains" if s == "GylesNonains" else "orsay" for s in station],
                    "cov_polling_station": station})
put("laslier_2002_insitu_approval", long_from_sets(ballots, 16, cov), [0, 1])

# ---- 2002 Sciences Po students (PrefLib 00029) ------------------------------
d = pd.read_csv(check("preflib/00029/00029-00000001.dat"))
appr = [c for c in d.columns if c.startswith("Approve of ")]
rate = [c for c in d.columns if c.startswith("Rating of ")]
assert len(appr) == len(rate) == 15 and list(d.columns) == [x for p in zip(appr, rate) for x in p]
assert [a[len("Approve of "):] for a in appr] == [r[len("Rating of "):] for r in rate]
assert len(d) == 408 and d.notna().all(axis=None)
A, R = d[appr].to_numpy(), d[rate].to_numpy()
assert set(np.unique(A)) == {0.0, 1.0}
assert (A.sum(axis=1) == 0).sum() == 10  # the 10 rows 00027 leaves out (398 = 408 - 10)
ids = np.arange(1, len(d) + 1)
long = pd.DataFrame({"id": np.repeat(ids, 15), "item": [code(k) for k in range(1, 16)] * len(d),
                     "resp": A.astype(int).ravel()})
put("laslier_2002_sciencespo_approval", long, [0, 1])
assert ((R % 0.5) != 0).sum() == 1 and (R > 10).sum() == 6 and R.min() == -1  # one 0.1, six > 10
long = pd.DataFrame({"id": np.repeat(ids, 15), "item": [code(k) for k in range(1, 16)] * len(d),
                     "resp": R.ravel()})
long = long[(long.resp != -1) & (long.resp <= 10)]  # no input; the 6 off-scale cells (Ben, 2026-11-15)
assert len(long) == (R != -1).sum() - 6 and long.resp.between(0, 10).all()
put("laslier_2002_sciencespo_rating", long, None)

# ---- Vote au pluriel 2012, approval -----------------------------------------
v = pd.read_csv(check("votepluriel/votes/approval.csv"))
cands = list(v.columns[1:])
assert len(cands) == 10 and len(v) == 8078 and v.id.is_unique and v.id.is_monotonic_increasing
_, n_alt, pl = read_cat(check("preflib/00074/00074-00000001.cat"))
assert n_alt == 10
names_pl = [ln.split(":", 1)[1].strip() for ln in open(check("preflib/00074/00074-00000001.cat"),
                                                       encoding="utf-8") if ln.startswith("# ALTERNATIVE NAME")]
assert names_pl == cands  # the release's column order is PrefLib's numbering
M = v[cands].to_numpy()
assert set(np.unique(M)) == {0, 1}
mine = sorted(tuple(sorted(np.flatnonzero(r) + 1)) for r in M)
assert mine == sorted(tuple(sorted(s)) for s in pl)  # the same 8,078 ballots as PrefLib 00074
put("vanderstraeten_2012_votepluriel_approval", long_from_sets(
    [frozenset((np.flatnonzero(r) + 1).tolist()) for r in M], 10), [0, 1])

# ---- QC + write --------------------------------------------------------------
for name, (t, permitted) in sorted(TABLES.items()):
    t = t.sort_values(["id", "item"]).reset_index(drop=True)
    for c in t.columns:
        if c.startswith("cov_"):
            assert (t.groupby("id")[c].nunique(dropna=False) == 1).all(), (name, c)
    checks = run_qc(t, permitted_values=permitted) if permitted is not None else run_qc(t)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, (name, fails)
    assert t.id.nunique() >= 100, name
    t.to_csv(os.path.join(OUT, name + ".csv"), index=False)
    print(f"{name}: {len(t)} rows, {t.id.nunique()} ballots, "
          f"{t.item.nunique()} items, resp {t.resp.min()}..{t.resp.max()}")
