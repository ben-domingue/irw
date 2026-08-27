"""WHODAS 2.0 administered pre- and post-treatment, for a Reliable Change
Index study in patients.

DOI: 10.17632/3fhcxn3zd3
Source: https://data.mendeley.com/datasets/3fhcxn3zd3
License: CC BY 4.0
Contributor (deposit record): Lozano, Cupani, Moraleda

178 patients with a baseline WHODAS 2.0 administration (`WHO_D<domain>_<item>`)
and 96 of them with a follow-up administration (`Post_WHO_...`). The two sets
carry identical item suffixes, so this is a genuine repeated administration of
the same instrument rather than two instruments: the pre/post distinction goes
in a `wave` column, and each of the six WHODAS domains ships as its own table.

`Seguimiento` ("follow-up") flags whether the patient had a follow-up and is
kept as a covariate.

Domains: D1 cognition (6), D2 mobility (5), D3 self-care (4),
D4 getting along (5), D5 life activities (4), D6 participation (8).
"""
from __future__ import annotations

import re
import sys
import tempfile
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
sys.path.insert(0, str(REPO_ROOT / "automated_finding"))
from irw_triage_updated import run_qc  # noqa: E402

DOI = "10.17632/3fhcxn3zd3"
KEY = "3fhcxn3zd3"
FILENAME = "Data.sav"
UA = {"User-Agent": "irw-batch/1.0 (research)"}

DOMAINS = {
    "cognition": "D1",
    "mobility": "D2",
    "self_care": "D3",
    "getting_along": "D4",
    "life_activities": "D5",
    "participation": "D6",
}
SCALE = (1, 5)


def fetch() -> pd.DataFrame:
    r = requests.get(f"https://data.mendeley.com/public-api/datasets/{KEY}",
                     headers=UA, timeout=60)
    r.raise_for_status()
    match = [f for f in r.json()["files"] if f["filename"] == FILENAME]
    assert len(match) == 1
    rr = requests.get(match[0]["content_details"]["download_url"],
                      headers=UA, timeout=180)
    rr.raise_for_status()
    import pyreadstat
    fh = tempfile.NamedTemporaryFile(suffix=".sav", delete=False)
    fh.write(rr.content); fh.close()
    return pyreadstat.read_sav(fh.name)[0]


def build() -> None:
    df = fetch()
    df.columns = [str(c).strip() for c in df.columns]
    df["id"] = range(1, len(df) + 1)

    used = {"Seguimiento"}
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    written = {}

    for suffix, dom in DOMAINS.items():
        pre = [c for c in df.columns if re.fullmatch(rf"WHO_{dom}_\d+", c)]
        post = [c for c in df.columns if re.fullmatch(rf"Post_WHO_{dom}_\d+", c)]
        assert pre and len(pre) == len(post), (dom, len(pre), len(post))
        assert sorted(c[len("WHO_"):] for c in pre) == \
               sorted(c[len("Post_WHO_"):] for c in post), dom
        used.update(pre); used.update(post)

        parts = []
        for cols, wave, strip in ((pre, "pre", "WHO_"), (post, "post", "Post_WHO_")):
            block = (df[["id", "Seguimiento"] + cols]
                     .melt(id_vars=["id", "Seguimiento"],
                           var_name="item", value_name="resp")
                     .dropna(subset=["resp"]))
            block["item"] = block["item"].str[len(strip):]
            block["wave"] = wave
            parts.append(block)

        long = pd.concat(parts, ignore_index=True)
        long["resp"] = long["resp"].astype(int)
        assert long["resp"].between(*SCALE).all(), \
            f"{suffix}: off-scale {sorted(long['resp'].unique())}"

        long = long.rename(columns={"Seguimiento": "cov_followup"})
        long = long[["id", "item", "resp", "wave", "cov_followup"]]

        checks = run_qc(long)
        fails = [c for c in checks if c.status == "fail"]
        assert not fails, f"{suffix} QC failed: {[(c.name, c.detail) for c in fails]}"
        for c in checks:
            if c.status == "warn":
                print(f"    NOTE [{suffix}] {c.name}: {c.detail}")

        assert long["id"].nunique() >= 100, suffix
        assert long["item"].nunique() > 1, suffix

        name = f"lozano_2018_{suffix}"
        assert name not in written
        long.to_csv(OUT_DIR / f"{name}.csv", index=False)
        written[name] = (long["id"].nunique(), long["item"].nunique(), len(long))
        n_pre = int((long["wave"] == "pre").sum())
        print(f"  {name}: {written[name][0]} ids x {written[name][1]} items "
              f"= {written[name][2]} responses ({n_pre} pre / "
              f"{written[name][2] - n_pre} post)")

    unused = [c for c in df.columns if c not in used and c != "id"]
    assert not unused, f"unaccounted source columns: {unused}"
    print(f"  total: {sum(v[2] for v in written.values())} responses "
          f"across {len(written)} tables")


if __name__ == "__main__":
    build()
