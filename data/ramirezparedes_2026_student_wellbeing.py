#!/usr/bin/env python3
# Source: https://zenodo.org/records/23418564
# DOI: 10.5281/zenodo.23418564
#   Ramírez-Paredes, F., Arciniega Hidrobo, S. & Paz Espinoza, J. C. (2026).
#   "Database: Student Well-Being and Academic Performance Across Disciplinary
#   Contexts: A Comparative Study of Engineering and Non-Engineering Students."
#   Zenodo (published 2026-10-16).
# Data: "base_maestra_scoring_ENG-NOENG_ANON.xlsx", two sheets of the same three
#       instruments administered to two samples: ENG (237 engineering students,
#       ID-EST-COD "FICA-n") and NO-ENG (223 non-engineering students, "FECTYT-n").
#       Per sheet: an anonymised student code, programme and current GPA, then three
#       instrument sections, each carrying its own demographics block, its items as
#       text answers, the same items again numerically prefixed `num_`, and subscale
#       sums/means:
#         pavot/num_pavot_  5 items, 1-7   (satisfaction with life)
#         ryff/num_ryff_   42 items, 1-6   (psychological well-being, 6 x 7 items)
#         fel_             14 items, 1-10  (happiness; numeric already, no text twin)
#       No missing cells in any numeric item column on either sheet.
# License: CC BY 4.0 (the Zenodo record's license id is `cc-by-4.0`).
#
# Item text: not shipped. It *is* in hand -- the Spanish stems are the column headers
#   themselves (there is no label level in an .xlsx; the headers are the only one, and
#   they carry full stems) -- but two of the three instruments are third-party scales
#   whose terms are unsettled here: the 42 `ryff_` stems are a Spanish adaptation of
#   Ryff's Scales of Psychological Well-Being and the 5 `pavot_` stems a Spanish SWLS
#   (Diener et al. 1985; the prefix is Pavot & Diener). Neither the originals nor these
#   Spanish adaptations have a row in itemtext/instrument_rights_register.csv, and
#   silence does not ship. Where the text actually is: the column headers of this
#   xlsx, snake-cased and stripped of punctuation ("ryff_me_siento_autosuficiente_y_
#   capaz_para_manejar_mi_vida"), in the administered Spanish.
#
# Item codes: swls_1..5, ryff_1..42, fel_1..14 -- the 1-based position of each column
#   inside its own `num_`/`fel_` block, in sheet order. The headers are full stems with
#   dropped diacritics and no number of their own, so they are unusable as codes; the
#   tie from code to wording is the printed, asserted column order below, which is
#   identical on the two sheets (asserted) and recoverable from the file.
#
# Samples: one merged file per instrument with cov_sample = eng / no_eng, per the
#   same-instrument-across-samples rule. The source's own ID-EST-COD is already
#   sample-prefixed (FICA- / FECTYT-), so it is used verbatim as `id` and cannot
#   collide; the programme code is kept as cov_programme.
#
# Columns skipped, by class (all printed at run time):
#   *_hora_de_inicio / *_hora_de_finalizacion  survey start/finish timestamps; these are
#       whole-section completion clocks, not per-item response times, so they are not
#       `rt` (and are not carried as covariates either)
#   pavot_id / ryff_id / fel_id                per-section row counters
#   per-section repeats of age / gender / programme / ethnic group (the pavot_ copies
#       are carried as the covariates; the ryff_/fel_ copies are duplicates)
#   pavot_<stem> / ryff_<stem> without `num_`  the text-labelled twin of the numeric
#       item column that is shipped
#   *_sum / *_mean / nota / felicidad_*        derived scores
#   the two NO-ENG-only "nivel de estudios que esta cursando" columns (not collected on
#       the ENG sheet, so not comparable across the merged samples)
# Tables:
#   ramirezparedes_2026_swls        5 items, 1-7
#   ramirezparedes_2026_ryff       42 items, 1-6
#   ramirezparedes_2026_happiness  14 items, 1-10
from __future__ import annotations

import io
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "runs" / "stage_2026-10-20_s3"
URL = ("https://zenodo.org/api/records/23418564/files/"
       "base_maestra_scoring_ENG-NOENG_ANON.xlsx/content")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
SHEETS = {"ENG": "eng", "NO-ENG": "no_eng"}

COVS = {
    "notas_carrera": "cov_programme",
    "notas_promedio_actual": "cov_gpa",
    "pavot_cual_es_su_edad_responda_con_un_numero": "cov_age",
    "pavot_con_que_genero_se_identifica": "cov_gender",
    "pavot_a_que_grupo_etnico_pertenece": "cov_ethnic_group",
}
FEL_META = {"fel_id", "fel_hora_de_inicio", "fel_hora_de_finalizacion",
            "fel_cual_es_su_edad_responda_con_un_numero"}


def screen_for_pii(df: pd.DataFrame, label: str) -> None:
    text_cols = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"[pii] {label}: examined {df.shape[1]} columns, "
          f"{len(text_cols)} of them string-typed")
    assert df.shape[1] > 0 and len(text_cols) > 0
    pats = [r"[\w.+-]+@[\w-]+\.[A-Za-z]{2,}", r"\+?\d[\d \-()]{8,}",
            r"\d{1,4}[/-]\d{1,2}[/-]\d{1,4}"]
    hits = [(c, p) for c in text_cols for p in pats
            if df[c].dropna().astype(str).str.contains(p, regex=True, na=False).any()]
    assert not hits, hits
    print(f"[pii] {label}: string columns are the anonymised student code, the "
          "programme name and the text-labelled Likert answers -- no identifiers")


def blocks(df: pd.DataFrame) -> dict[str, list[str]]:
    num = [c for c in df.columns if c.startswith("num_")]
    swls = [c for c in num if "pavot" in c]
    ryff = [c for c in num if "ryff" in c]
    fel = [c for c in df.columns if c.startswith("fel_")
           and c not in FEL_META and not c.endswith("_mean")]
    assert (len(swls), len(ryff), len(fel)) == (5, 42, 14), (len(swls), len(ryff), len(fel))
    return {"swls": swls, "ryff": ryff, "fel": fel}


def convert() -> None:
    r = requests.get(URL, headers=UA, timeout=300)
    r.raise_for_status()
    book = pd.ExcelFile(io.BytesIO(r.content))
    assert set(book.sheet_names) == set(SHEETS), book.sheet_names

    per_block: dict[str, list[pd.DataFrame]] = {"swls": [], "ryff": [], "fel": []}
    order_check: dict[str, list[str]] = {}
    skipped_report: dict[str, list[str]] = {}
    for sheet, tag in SHEETS.items():
        df = book.parse(sheet)
        screen_for_pii(df, sheet)
        bl = blocks(df)
        for k, cols in bl.items():
            if k in order_check:
                assert order_check[k] == cols, (k, sheet)
            else:
                order_check[k] = cols
        df = df.rename(columns=COVS)
        cov_cols = list(COVS.values())
        base = df[["ID-EST-COD"] + cov_cols].rename(columns={"ID-EST-COD": "id"})
        base["cov_sample"] = tag
        for k, cols in bl.items():
            codes = {c: f"{'swls' if k == 'swls' else k}_{i}"
                     for i, c in enumerate(cols, start=1)}
            long = (pd.concat([base, df[cols].rename(columns=codes)], axis=1)
                    .melt(id_vars=["id"] + cov_cols + ["cov_sample"],
                          var_name="item", value_name="resp"))
            per_block[k].append(long)
        accounted = set(COVS) | {"ID-EST-COD"} | {c for cs in bl.values() for c in cs}
        skipped = [c for c in df.columns
                   if c not in cov_cols + ["cov_sample"]
                   and c not in {v for cs in bl.values() for v in cs}
                   and c != "id"]
        skipped_report[sheet] = skipped
        print(f"[books] {sheet}: {len(accounted)} columns kept "
              f"(1 id + {len(COVS)} covariates + 61 items), {len(skipped)} skipped "
              "(section timestamps and row counters, repeated demographics, the "
              "text-labelled twins of the numeric items, and derived sums/means)")

    print("[codes] item order (code <- source header), swls then ryff then fel:")
    for k, cols in order_check.items():
        for i, c in enumerate(cols, start=1):
            print(f"    {'swls' if k == 'swls' else k}_{i} <- {c}")

    spec = {
        "ramirezparedes_2026_swls": ("swls", [1, 2, 3, 4, 5, 6, 7]),
        "ramirezparedes_2026_ryff": ("ryff", [1, 2, 3, 4, 5, 6]),
        "ramirezparedes_2026_happiness": ("fel", list(range(1, 11))),
    }
    assert len(set(spec)) == len(spec)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    cov_cols = list(COVS.values()) + ["cov_sample"]
    for name, (key, pv) in spec.items():
        t = pd.concat(per_block[key], ignore_index=True)
        t["resp"] = pd.to_numeric(t["resp"], errors="coerce")
        t = t.dropna(subset=["resp"])
        assert (t["resp"] % 1 == 0).all(), name
        t = t[["id", "item", "resp"] + cov_cols].reset_index(drop=True)
        assert not t.duplicated(["id", "item"]).any(), name
        assert t["id"].nunique() >= 100 and t["item"].nunique() >= 3, name
        checks = run_qc(t, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {name} {c.name}: {c.detail[:160]}")
        rep = irw_validate.validate_frame(t, label=name, profile="upload",
                                          context={"permitted_values": pv})
        assert rep.conforms and not rep.errors, \
            (name, [(f.check, f.message) for f in rep.errors])
        for f in rep.warnings:
            print(f"    [validate warn] {name} {f.check}: {f.message[:160]}")
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min():g}-{t['resp'].max():g}")


if __name__ == "__main__":
    convert()
