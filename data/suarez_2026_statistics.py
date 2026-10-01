"""suarez_2026_statistics (+ suarez_2026_statistics_nom).

Source: Suárez Durán, M., Rodríguez Nieto, C. A., Barrera Pacheco, A. & Font, V.
(2026). University statistics assessment: student responses and item
descriptors dataset (Statistical Exam, Universidad de la Costa). Zenodo,
doi:10.5281/zenodo.21995919, file student_answers_statistics_2024-i.parquet
(pinned by md5). Paper: Journal on Mathematics Education 17(1), 27-42 (2026),
doi:10.22342/jme.v17i1.pp27-42.

Licence: Zenodo record metadata, license id "cc-by-4.0".

431 undergraduates, Moodle, 2024. Each took 16 multiple-choice items drawn
from an 85-item bank (4 per performance indicator); item order and option
order were randomised, which is why the deposit records the TEXT of the option
chosen rather than a letter. The text is therefore the category.

Mapping (the file is wide: 16 position blocks per student)
- id             = student
- item           = `question_id k` (bank id, e.g. C1I2ITEM5)
- resp           = 1 if `Respuesta k` equals `respuesta_correcta k`, else 0
- resp_raw       = `Respuesta k`, the text of the option chosen (Spanish)
- trial_position = k, the position the item was served in (1-16). Needed as
                   well as for order: 13 attempts were served the same bank
                   item twice, and the position tells those rows apart.
- itemcov_indicator = performance indicator, from the bank id (C1I1..C1I4)
- itemcov_*      = the deposit's 15 item descriptors (representation and
                   demand flags, 0/1), constant within an item:
                   grafica, numerica_algebra, alterna, equivalente, escrito,
                   tabular, caracteristica, parte_todo, implicacion,
                   conceptual_significado, modelado, procedimental,
                   reversibilidad, significado, metaforica

Dropped
- 238 position blocks with no question_id (and no key), so the item cannot be
  identified. 151 students lose one, 33 two, 3 three, 1 student twelve.
- blank answers (no option chosen) among the rest. There are none: all 42
  empty answers in the file sit in unidentified blocks. The filter stays as a
  guard.
Moodle's own grade (Calificación/5.0) agrees with the rescored total to
rounding once the unidentified blocks are accounted for.
"""
import hashlib
import sys
import urllib.request
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

URL = ("https://zenodo.org/api/records/21995919/files/"
       "student_answers_statistics_2024-i.parquet/content")
MD5 = "b9dfa2deb43eb5fb981287570643a708"
CACHE = Path.home() / ".cache" / "irw-nominal" / "udc_stats.parquet"

FEATURES = {
    "Grafica": "grafica", "Numerica/algebra": "numerica_algebra",
    "Alterna": "alterna", "Equivalente": "equivalente", "Escrito": "escrito",
    "Tabular": "tabular", "Característica": "caracteristica",
    "Parte-todo": "parte_todo", "Implicación": "implicacion",
    "Conceptual/Significado": "conceptual_significado", "Modelado": "modelado",
    "Procedimental": "procedimental", "Reversibilidad": "reversibilidad",
    "Significado": "significado", "Metafórica": "metaforica",
}

if not CACHE.exists():
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
    CACHE.write_bytes(urllib.request.urlopen(req).read())
assert hashlib.md5(CACHE.read_bytes()).hexdigest() == MD5

d = pd.read_parquet(CACHE)
assert len(d) == 431 and d["student"].is_unique

blocks = []
for k in range(1, 17):
    b = pd.DataFrame({
        "id": d["student"],
        "item": d[f"question_id {k}"],
        "resp_raw": d[f"Respuesta {k}"],
        "key": d[f"respuesta_correcta {k}"],
        "trial_position": k,
    })
    for src, dst in FEATURES.items():
        b[f"itemcov_{dst}"] = d[f"{src} {k}"]
    blocks.append(b)
df = pd.concat(blocks, ignore_index=True)

no_item = df["item"].isna()
assert df.loc[no_item, "key"].isna().all()
df = df[~no_item]
blank = df["resp_raw"].isna() | (df["resp_raw"].str.strip() == "")
print(f"dropped {int(no_item.sum())} unidentified blocks, {int(blank.sum())} blank answers")
df = df[~blank].copy()

df["resp_raw"] = df["resp_raw"].str.strip()
df["resp"] = (df["resp_raw"] == df["key"].str.strip()).astype(int)
df["itemcov_indicator"] = df["item"].str.extract(r"^(C\d+I\d+)", expand=False)
assert df["itemcov_indicator"].notna().all()
itemcovs = ["itemcov_indicator"] + [f"itemcov_{v}" for v in FEATURES.values()]
for c in itemcovs + ["key"]:
    assert (df.groupby("item")[c].nunique() <= 1).all(), c
for c in itemcovs[1:]:
    df[c] = df[c].astype(int)

df = df[["id", "item", "resp", "resp_raw", "trial_position"] + itemcovs]
df = df.sort_values(["id", "trial_position"], kind="stable")

checks = run_qc(df, permitted_values={i: {0, 1} for i in df["item"].unique()})
fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
assert not fails, fails

df.to_csv("suarez_2026_statistics.csv", index=False)
df.rename(columns={"resp_raw": "text"}).to_csv("suarez_2026_statistics_nom.csv", index=False)
print(len(df), df["id"].nunique(), df["item"].nunique())
