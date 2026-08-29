"""INFODEMIJA: Lithuanian residents on science communication and misinformation.

Source: Skarzauskiene, A., Maciuliene, M. & Guleviciute, G. (2026), Zenodo
10.5281/zenodo.21134839, CC BY 4.0 -- "INFODEMIJA: Survey of Lithuanian
Residents on Science Communication, Trust in Science, and Misinformation
(2024)". 1,005 respondents, already anonymised by the depositors.

The deposit ships a real data dictionary (`INFODEMIJA_data_dictionary.xlsx`)
giving each variable's group, question wording and full response-option set,
so the blocks below are read from it rather than inferred. Blocks are formed
by (variable group, IDENTICAL option set) and kept only at 4+ items: several
groups mix response formats -- "Science Engagement & Interest" spans five
different option sets and "Perception & Behavior Related to Fake News" three
-- and merging those would make `resp` ambiguous. Splitting by option set
also avoids the single-item tables a per-question split would produce.

Every block codes 9 as "Don't know / did not answer" alongside its 1-5 scale.
That is a missingness sentinel, not a sixth level, and is dropped; an assert
fires if any value outside {1..5, 9} ever appears.
"""
import os
import re

import pandas as pd
import requests

RECORD = 21134839
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")
PREFIX = "skarzauskiene_2026"

VALID = {1, 2, 3, 4, 5}
DK = 9          # "Don't know / did not answer" / "N/A"
MIN_ITEMS = 4

SLUG = {
    "Science Engagement & Interest": "science_engagement",
    "Trust in Science & Institutions": "trust_science",
    "Attitudes Toward Science & Technology": "attitudes_science",
    "Information Consumption & Sources": "information_sources",
    "Science-related Behaviors & Participation": "science_behaviors",
    "Perception & Behavior Related to Fake News": "fake_news",
    "Personality Traits (Big Five)": "big_five",
    "Social Trust": "social_trust",
}


def fetch(suffix, path=None):
    if path and os.path.exists(path):
        return path
    rec = requests.get(f"https://zenodo.org/api/records/{RECORD}",
                       timeout=120).json()
    f = next(x for x in rec["files"] if x["key"].lower().endswith(suffix))
    r = requests.get(f["links"]["self"], timeout=600)
    r.raise_for_status()
    local = os.path.join("/tmp", f["key"])
    with open(local, "wb") as fh:
        fh.write(r.content)
    return local


def parse_options(text):
    """'1. Man, 2. Woman, 3. Other' -> {1: 'Man', 2: 'Woman', 3: 'Other'}."""
    parts = re.split(r"(?:^|,\s*)(\d+)\.\s*", str(text))
    return {int(parts[i]): parts[i + 1].strip().rstrip(",")
            for i in range(1, len(parts) - 1, 2)}


def main(data_path=None, dict_path=None):
    d = pd.read_csv(fetch(".csv", data_path))
    dd = pd.read_excel(fetch(".xlsx", dict_path))
    dd.columns = [c.strip() for c in dd.columns]
    dd["opts"] = dd["Possible Answer Options"].astype(str).str.strip()
    lower = {c.lower(): c for c in d.columns}

    # Demographics become covariates, decoded through the dictionary.
    demo = dd[dd["Variable Group"] == "Demographics"]
    cov = {}
    for _, row in demo.iterrows():
        col = lower.get(str(row["Variable ID"]).lower())
        if col is None:
            continue
        name = "cov_" + re.sub(r"[^a-z0-9]+", "_",
                               str(row["Variable Description"]).lower()).strip("_")
        opts = parse_options(row["opts"])
        cov[name] = d[col].map(opts) if opts else d[col]
    covdf = pd.DataFrame(cov)
    covdf["id"] = range(1, len(d) + 1)

    os.makedirs(OUT_DIR, exist_ok=True)
    total = 0
    for (group, _opts), sub in dd[dd["Variable Group"] != "Demographics"] \
            .groupby(["Variable Group", "opts"], sort=False):
        cols = [lower[str(i).lower()] for i in sub["Variable ID"]
                if str(i).lower() in lower]
        if len(cols) < MIN_ITEMS:
            continue

        observed = {int(v) for v in pd.unique(d[cols].values.ravel())
                    if pd.notna(v)}
        bad = observed - VALID - {DK}
        assert not bad, f"{group}: unexpected response code(s) {sorted(bad)}"

        block = pd.concat([covdf, d[cols]], axis=1)
        long = block.melt(id_vars=list(covdf.columns), value_vars=cols,
                          var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"])
        long["resp"] = long["resp"].astype(int)
        long = long[long["resp"] != DK]          # sentinel, not a level

        # Only the fake-news group splits into two shippable blocks, so only
        # it takes a suffix; every other table name stays a plain slug.
        table = f"{PREFIX}_{SLUG[group]}"
        if group == "Perception & Behavior Related to Fake News":
            table += "_agree" if len(cols) == 6 else "_frequency"

        out = long[["id", "item", "resp"] + list(cov)]
        out.to_csv(os.path.join(OUT_DIR, f"{table}.csv"), index=False)
        total += len(out)
        print(f"{table}: {len(out):,} responses | {out['id'].nunique():,} ids | "
              f"{out['item'].nunique()} items")
    print(f"total: {total:,}")


if __name__ == "__main__":
    main()
