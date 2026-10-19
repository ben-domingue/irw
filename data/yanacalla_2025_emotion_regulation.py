#!/usr/bin/env python3

# Source: https://data.mendeley.com/datasets/dpcc2wms6h/2
# DOI: 10.17632/dpcc2wms6h.2
#   Yana-Calla, V. R. (2025). Psychometric properties of the emotional
#   regulation questionnaire in Peruvian university students [Dataset].
#   Mendeley Data.
# Data: "Base de datos análisis Gross.sav" -- 1,317 Peruvian university
#   students, four instruments administered in Spanish, complete throughout.
# License: CC BY 4.0 (verified on the Mendeley record and DataCite, 2026-10-19).
# Item text: NOT shipped, and the rights position is why rather than the
#   extraction. Every item's full administered SPANISH stem is in its SPSS
#   variable label, numbered ("17. Aunque a veces me siento triste, suelo
#   tener una visión optimista"), so all 59 items are extraction-solved. But
#   the rights register blocks the wording of three of the four: the ERQ
#   (Gross & John 2003, ruled `block` on 2026-10-18 under the scoped-use
#   ruling, irw#3082), the SWLS, and PANAS in Spanish translation. The TMMS-24
#   has no register row. So the text waits on rulings, not on work.
#
#   A `block` STOPS THE WORDING, NOT THE RESPONSES. `irw_validate/rights.py`
#   says so in as many words, and the 2026-10-18 ERQ withdrawal took item text
#   out of `irw_text_2` (935 -> 930 rows), not response tables. This deposit
#   was deferred partly on that worry; it does not apply.
#
# FOUR tables, 1,317 respondents each, no missing cell anywhere:
#   yanacalla_2025_erq     10 items, 1-7  (Emotion Regulation Questionnaire;
#                          the deposit's own order puts the six reappraisal
#                          items first and the four suppression items after,
#                          but the ITEM NUMBER in each label is the ERQ's own,
#                          so ERQ_01..ERQ_10 follow the instrument, not the
#                          column order)
#   yanacalla_2025_swls     5 items, 1-7  (Satisfaction With Life Scale)
#   yanacalla_2025_tmms24  24 items, 1-5  (Trait Meta-Mood Scale, 24-item)
#   yanacalla_2025_panas   20 items, 1-5  (PANAS; 10 positive then 10 negative
#                          affect adjectives, in the deposit's order)
#
# ITEM CODES ARE POSITIONS, DELIBERATELY. The SWLS and TMMS-24 columns are
#   name-mangled copies of the Spanish stems ('@17.Aunqueavecesmesientotri...')
#   and the PANAS columns are the bare adjectives ('Nervioso'). Shipping those
#   as `item` would publish the wording of three blocked instruments through
#   the item codes -- which is exactly what `irw_validate`'s rights gate warns
#   about ("if these codes ARE item wording, rename them before this table is
#   published"). So each block is renumbered from the item number in its own
#   label, and the PANAS adjective order is recorded here instead:
#   PANAS_01..10 = Interesado, Dispuesto, Animado, Enérgico, Orgulloso,
#   Entusiasmado, Inspirado, Decidido, Atento, Activo;
#   PANAS_11..20 = Disgustado/enfadado, Culpable, Temeroso, Enojado, Irritado,
#   Tenso, Avergonzado, Nervioso, Intranquilo, Asustado.
#
# NOT SHIPPED: the deposit's nine `PD_*` subscale and total scores
#   (satisfaction, emotional attention/clarity/repair, emotional intelligence,
#   positive and negative affect, reappraisal, suppression) and
#   `Consentimiento`, which is 1 for every row.
#
# id: the deposit's own `ID` (1-1,317, unique), kept so the four tables link.
# Covariates: cov_sex, cov_age, cov_programme, cov_university -- the deposit's
#   own codes, which it does not label.
import os
import re
import sys
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = Path(os.environ.get(
    "IRW_RAW_DIR",
    REPO_ROOT / "automated_finding" / "runs" / "group2_t1" / "dpcc2wms6h" / "raw"))
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
DATASET, FNAME = "dpcc2wms6h", "Base de datos análisis Gross.sav"
COVS = {"Sexo": "cov_sex", "Edad": "cov_age",
        "Carreraoprogramaqueestudia": "cov_programme",
        "Universidad": "cov_university"}
SEVEN, FIVE = set(range(1, 8)), set(range(1, 6))


def fetch() -> Path:
    p = RAW_DIR / FNAME
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        j = requests.get("https://data.mendeley.com/public-api/datasets/"
                         f"{DATASET}", headers=UA, timeout=120).json()
        url = [f["content_details"]["download_url"] for f in j["files"]
               if f["filename"] == FNAME][0]
        r = requests.get(url, headers=UA, timeout=600)
        r.raise_for_status()
        p.write_bytes(r.content)
    return p


def main():
    df, meta = pyreadstat.read_sav(str(fetch()), apply_value_formats=False)
    labels = meta.column_names_to_labels
    assert len(df) == 1317, len(df)
    assert df["ID"].is_unique

    erq = [c for c in df.columns if c.startswith("Item_G_")]
    at = [c for c in df.columns if c.startswith("@")]
    panas = [c for c in df.columns
             if (labels.get(c) or "").strip().startswith("[")]
    scores = [c for c in df.columns if c.startswith("PD_")]
    rest = [c for c in df.columns
            if c not in erq + at + panas + scores]
    assert len(erq) == 10 and len(at) == 29 and len(panas) == 20, \
        (len(erq), len(at), len(panas))
    assert sorted(rest) == sorted(list(COVS) + ["ID", "Consentimiento"]), rest
    print(f"not shipped: {len(scores)} PD_* subscale/total scores, "
          f"Consentimiento (1 for every row)")

    # Every block is renumbered from the item number in its own label.
    def numbered(cols, prefix, n_expected, scale):
        out = {}
        for c in cols:
            m = re.match(r"^(\d+)\.", (labels.get(c) or "").strip())
            assert m, (c, labels.get(c))
            out[c] = f"{prefix}_{int(m.group(1)):02d}"
        assert len(set(out.values())) == n_expected, (prefix, len(out))
        for c in cols:
            vals = set(pd.to_numeric(df[c]).dropna().unique())
            assert vals <= scale, (c, sorted(vals))
        return out

    # The 29 '@' columns are two instruments: the five 1-7 SWLS items and the
    # twenty-four 1-5 TMMS-24 items. Split on the observed scale, then assert
    # the counts, rather than on position.
    swls_cols = [c for c in at
                 if set(pd.to_numeric(df[c]).dropna().unique()) - FIVE]
    tmms_cols = [c for c in at if c not in swls_cols]
    assert len(swls_cols) == 5 and len(tmms_cols) == 24, \
        (len(swls_cols), len(tmms_cols))

    plan = {
        "yanacalla_2025_erq": (numbered(erq, "ERQ", 10, SEVEN), SEVEN),
        "yanacalla_2025_swls": (numbered(swls_cols, "SWLS", 5, SEVEN), SEVEN),
        "yanacalla_2025_tmms24": (numbered(tmms_cols, "TMMS", 24, FIVE), FIVE),
        "yanacalla_2025_panas": ({c: f"PANAS_{i:02d}" for i, c in
                                  enumerate(panas, 1)}, FIVE),
    }

    df = df.rename(columns=COVS)
    df["id"] = pd.to_numeric(df["ID"]).astype(int)
    cov_cols = list(COVS.values())
    for cov in cov_cols:
        v = pd.to_numeric(df[cov])
        assert (v % 1 == 0).all(), cov
        df[cov] = v.astype("Int64")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, (renames, scale) in plan.items():
        cols = list(renames)
        assert not df[cols].isna().any().any(), f"{name}: unexpected missing"
        t = (df[["id", *cov_cols, *cols]]
             .rename(columns=renames)
             .melt(id_vars=["id", *cov_cols], value_vars=list(renames.values()),
                   var_name="item", value_name="resp"))
        t["resp"] = pd.to_numeric(t["resp"])
        assert (t["resp"] % 1 == 0).all(), name
        t["resp"] = t["resp"].astype(int)
        bad = sorted(set(t["resp"]) - scale)
        assert not bad, f"{name}: resp outside the administered scale: {bad}"
        t = t[["id", "item", "resp", *cov_cols]]
        assert not t.duplicated(["id", "item"]).any(), name
        assert t["id"].nunique() == 1317 and t["item"].nunique() == len(cols)
        checks = run_qc(t, permitted_values=scale)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {name} {c.name}: {c.detail[:130]}")
        report = irw_validate.validate_frame(t, label=name, profile="upload",
                                             context={"permitted_values": scale})
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
