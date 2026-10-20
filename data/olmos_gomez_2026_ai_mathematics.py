"""Perceptions of AI in mathematics education — Olmos-Gómez et al. (2026).

Source: Olmos-Gómez, M. C., Portillo-Sánchez, R., Poyato-Núñez, M., &
        Parra-González, M. E. (2026). The use of artificial intelligence in
        mathematics education: perceptions among young university students.
        Humanities and Social Sciences Communications, 7(1).
DOI: 10.1057/s41599-026-08011-3
Data: https://doi.org/10.7910/DVN/VSFCVG (Harvard Dataverse, "IA. MATH 853.xlsx")
License: CC0 1.0 on the deposit; the article's version of record is CC BY 4.0,
         which is what governs the item wording (the items are study-authored).
Item text: shipped (the column headers ARE the administered Spanish stems)

One table, not three. The article validates a single second-order construct
(MATH) over three correlated first-order factors with one overall alpha
(.883), and retains all 9 items; two of the factors hold 2 items each. These
are dimensions of one instrument rather than distinct constructs, so they ship
as one table. The factor structure is NOT written into the item text's
`section_id`: the nine items were administered as one block with no section
prompts, and the factors came out of the CFA rather than the administration,
so `section_id` is `<table>_1` throughout and the factor assignment is
recorded here instead (FACT1 = lookup_theory, solve_equations, solve_geometry,
modelling, verify_solution; FACT2 = create_practice, makes_mistakes; FACT3 =
unsure_reliable, trust_answers; alphas .918 / .760 / .633).

The instrument is author-developed ("an ad hoc quantitative research design ...
a questionnaire validated by a group of experts"). Three stems were searched
verbatim and match nothing published.

Item codes are derived from each stem's content words, not from position. The
derivation is corroborated independently: the article's CFA regression table
lists its own English rendering of all 9 items in the same order as the
spreadsheet's columns, so each Spanish header and each English item line up
without relying on either alone.

PII: `Edad` is a free-text age field and one of its 853 answers is an email
address. Under the structural/incidental rule narrowed 2026-10-19 that is
incidental — the column collects age, not identifiers — so the cell is nulled
rather than the candidate skipped. There is no name column and no other
identifier anywhere in the 12-column file; this was re-verified off the source.
"""
from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"
ITEM_DIR  = REPO_ROOT / "automated_finding" / "itemtext_output"

DOI     = "10.7910/DVN/VSFCVG"
FILE_ID = 14006774  # IA. MATH 853.xlsx
UA      = {"User-Agent": "irw-batch/1.0 (research)"}

TABLE = "olmos_gomez_2026_ai_mathematics"

# Spanish header exactly as the spreadsheet spells it -> item code. The codes
# come from the stems' content, so a one-position slip would be visible.
ITEMS = {
    "La IA me ayuda a buscar contenido teórico de matemáticas "
    "(definiciones, fórmulas, teoremas, etc.)": "ai_lookup_theory",
    "Las herramientas de IA me sirven para resolver problemas y/o ejercicios "
    "sobre ecuaciones, funciones, derivadas o integrales.": "ai_solve_equations",
    "La IA me ayuda a resolver tareas de geometría "
    "(sobre figuras planas o sólidos geométricos).": "ai_solve_geometry",
    "La IA es útil a la hora de trasformar situaciones reales o problemas "
    "verbales en lenguaje matemático.": "ai_modelling",
    "La IA me permite revisar y/o comprobar si he resuelto bien un problema "
    "matemático.": "ai_verify_solution",
    "Pido a la IA crear problemas matemáticos para practicar.": "ai_create_practice",
    "Pienso que la IA puede cometer errores en tareas matemáticas.": "ai_makes_mistakes",
    "No tengo seguridad de que la IA sea totalmente fiable en el conocimiento "
    "matemático que maneja": "ai_unsure_reliable",
    "Confío en las respuestas de la IA cuando se trata de matemáticas.": "ai_trust_answers",
}

INSTRUMENT = ("Perceptions of artificial intelligence in mathematics "
              "education (Olmos-Gómez et al. 2026 ad hoc questionnaire, 9 items)")

# The article's own English rendering of each stem, from its CFA
# regression-weights table ("Item-Factor Association"). It lists all nine in
# the spreadsheet's column order, which is the independent corroboration of
# the item codes above.
ITEM_TEXT_EN = {
    "ai_lookup_theory": "AI helps me look up theoretical mathematical content "
                        "(definitions, formulas, theorems, etc.).",
    "ai_solve_equations": "AI tools help me solve problems and/or exercises on "
                          "equations, functions, derivatives or integrals.",
    "ai_solve_geometry": "AI helps me solve geometry tasks (whether involving "
                         "plane figures or geometric solids).",
    "ai_modelling": "AI is useful when transforming real-life situations or "
                    "word problems into mathematical language.",
    "ai_verify_solution": "AI allows me to review and/or verify that a "
                          "mathematical problem has been solved correctly.",
    "ai_create_practice": "I ask AI to create math problems for me to practice.",
    "ai_makes_mistakes": "I think AI can make mistakes in mathematical tasks.",
    "ai_unsure_reliable": "I am not sure that AI is completely reliable in the "
                          "mathematical knowledge that it handles.",
    "ai_trust_answers": "I trust AI answers when it comes to math.",
}

# Anchors as the article states them: "a five-point Likert scale, where 1 is
# 'Strongly disagree', 2 is 'Disagree', 3 is 'Somewhat agree', 4 is 'Agree'
# and 5 is 'Strongly agree'". The deposit stores only the numeric codes and
# the administered SPANISH anchors are published nowhere, so this English --
# the authors' own rendering of their own scale -- is what ships in
# `option_text`, with `option_text_translated` left empty. That is the
# documented fallback for unrecoverable administered wording, applied to the
# option axis alone; the stems beside it ARE the administered Spanish.
OPTIONS_EN = {
    1: "Strongly disagree",
    2: "Disagree",
    3: "Somewhat agree",
    4: "Agree",
    5: "Strongly agree",
}

COV_MAP = {
    "Género": "cov_gender",                 # Mujer / Hombre / Otro
    "Edad": "cov_age",                      # free text, in years
    "Nivel socioeconómico": "cov_ses",      # Bajo / Medio / Alto
}
# Source category labels are kept in Spanish as deposited rather than
# translated, so the shipped values are the ones the respondents saw.


def fetch_data() -> pd.DataFrame:
    url = f"https://dataverse.harvard.edu/api/access/datafile/{FILE_ID}"
    r = requests.get(url, headers=UA, timeout=300)
    r.raise_for_status()
    return pd.read_excel(io.BytesIO(r.content))


def clean_age(s: pd.Series) -> pd.Series:
    """Age as deposited is free text: '19', '18 años', '21Si ', one email.

    Takes the leading integer and leaves everything else missing. That is what
    drops the one respondent's self-volunteered email address -- it has no
    leading digits -- so the incidental PII cannot reach `cov_age`.
    """
    years = s.astype("string").str.strip().str.extract(r"^(\d{1,3})", expand=False)
    return pd.to_numeric(years, errors="coerce").astype("Int64")


def convert() -> pd.DataFrame:
    raw = fetch_data()

    missing = [h for h in ITEMS if h not in raw.columns]
    if missing:
        raise SystemExit(f"headers not found in the deposit: {missing}")

    # No respondent identifier is deposited, so `id` is the row index.
    raw = raw.reset_index(drop=True)
    raw["id"] = raw.index + 1

    for src, dst in COV_MAP.items():
        raw[dst] = raw[src]
    raw["cov_age"] = clean_age(raw["cov_age"])

    cov_cols = list(COV_MAP.values())
    long = raw[["id"] + cov_cols + list(ITEMS)].melt(
        id_vars=["id"] + cov_cols,
        value_vars=list(ITEMS),
        var_name="item",
        value_name="resp",
    )
    long["item"] = long["item"].map(ITEMS)
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)

    long = long[["id", "item", "resp"] + cov_cols]
    return long.sort_values(["id", "item"]).reset_index(drop=True)


def build_itemtext(long: pd.DataFrame) -> pd.DataFrame:
    """One row per item x response option.

    `item_text` is the administered Spanish, taken verbatim from the
    spreadsheet's column headers -- the header IS the stem, which is why the
    mapping basis is `data_labels` and needs no statistical verification.
    """
    es_by_code = {code: header for header, code in ITEMS.items()}
    rows = []
    for code in ITEMS.values():
        for resp, option_en in OPTIONS_EN.items():
            rows.append({
                "table": TABLE,
                "section_id": f"{TABLE}_1",
                "item": code,
                "instrument": INSTRUMENT,
                "language": "Spanish",
                "instructions": "",
                "section_prompt": "",
                "item_text": es_by_code[code],
                "correct_response": "",
                "option_text": option_en,
                "resp": resp,
                "instructions_translated": "",
                "section_prompt_translated": "",
                "item_text_translated": ITEM_TEXT_EN[code],
                "option_text_translated": "",
            })
    items = pd.DataFrame(rows)

    # THE PRIME COMMANDMENT: both join keys must match the response table.
    assert set(items["item"]) == set(long["item"]), "item sets differ"
    assert set(items["resp"]) == set(long["resp"]), "resp sets differ"
    return items


def main() -> None:
    long = convert()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"{TABLE}.csv"
    long.to_csv(out, index=False)
    print(f"{out.name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()}")
    print("cov_age non-missing:", int(long['cov_age'].notna().sum() / long['item'].nunique()),
          "of", long['id'].nunique(), "respondents")

    items = build_itemtext(long)
    ITEM_DIR.mkdir(parents=True, exist_ok=True)
    item_out = ITEM_DIR / f"{TABLE}__items.csv"
    items.to_csv(item_out, index=False)
    print(f"{item_out.name}: rows={len(items)} items={items['item'].nunique()} "
          f"options={items['resp'].nunique()}")


if __name__ == "__main__":
    main()
