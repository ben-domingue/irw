"""Python port of the Cuidador(a) Principal `_cp_c` block of
data/chile_2023_children-adolescents-survey.do (#2401).

No Stata on the audit machine, so this reproduces the .do's code path for the one
table the #2401 batch1 fix touches, and nothing else.

    python3 chile_2023_children-adolescents-survey.py RAW_DTA OUT_DIR [--legacy]

--legacy : the .do before #2401 (what built the live table).
default  : cp9_1..cp9_4 values >= 88 (the "88:88" No sabe code, parsed as 89.5 h)
           set to missing, and rows with a missing resp dropped.

Source: https://observatorio.ministeriodesarrollosocial.gob.cl/eanna-2023
        storage/docs/eanna/2023/Base_de_datos_EANNA_2023.dta.zip
"""
import math
import sys
import numpy as np
import pandas as pd

SENT = (-88, -99, -89, -98, 87, 77)
TIMES = ["cp7_1", "cp7_2", "cp7_3", "cp7_4", "cp9_1", "cp9_2", "cp9_3", "cp9_4"]
Q = ("ac1_1 ac1_2 ac1_3 ac1_4 ac1_5 ac1_6 ac1_7 ac1_8 ac2_1 ac2_2 ac2_3 ac2_4 ac2_5 ac3 "
     "ac5_1 ac5_10 ac5_2 ac5_3 ac5_4 ac5_5 ac5_6 ac5_7 ac5_77 ac5_8 ac5_9 ac6_1 ac6_2 ac6_3 "
     "ac6_4 ac6_77 cp2_1 cp2_10 cp2_2 cp2_3 cp2_4 cp2_5 cp2_6 cp2_7 cp2_77 cp2_8 cp2_9 cp3 "
     "cp4 cp5_1 cp5_2 cp5_3 cp5_4 cp5_5 cp5_6 cp5_7 cp6_1 cp6_2 cp6_3 cp6_4 cp6_5 cp6_6 cp6_7 "
     "cp6_8 cp7_1 cp7_2 cp7_3 cp7_4 cp8_1 cp8_2 cp8_3 cp8_4 cp8_5 cp8_6 cp9_1 cp9_2 cp9_3 "
     "cp9_4").split()


def hhmm(x):
    """real(substr(x,1,strpos(x,":")-1)) + real(substr(x,strpos(x,":")+1,.))/60,
    then round(.,0.1) and string(.,"%9.1f"), then destring.

    The live table carries the float32 image of these (0.30000001 for 0.3),
    because destring stored them as Stata floats; this writes the decimal."""
    if not isinstance(x, str) or ":" not in x:
        return np.nan
    h, m = x.split(":", 1)
    try:
        v = float(h) + float(m) / 60
    except ValueError:
        return np.nan
    # `gen` with no type makes a Stata float: round() then sees the float32
    # value (0.15 -> 0.150000006 -> 0.2; 0.65 -> 0.64999998 -> 0.6).
    v = float(np.float32(v))
    return float(f"{math.floor(v / 0.1 + 0.5) * 0.1:.1f}")


def build(path, legacy):
    r = pd.io.stata.StataReader(path)
    need = ["rp2", "sexo_eanna", "edad_tramos", "cp1"] + Q
    d = r.read(convert_categoricals=False, columns=need)
    labs = r.value_labels()
    age = d["edad_tramos"].map(lambda v: labs["edad_tramos"].get(int(v), "") if pd.notna(v) else "")
    d = d[age != "0 - 4 años"].copy()
    age = age[d.index]
    num = [c for c in d.columns if c not in TIMES and d[c].dtype != object]
    for c in num:
        d[c] = d[c].where(~d[c].isin(SENT))
    # string sentinels
    for c in TIMES:
        d[c] = d[c].where(~d[c].isin(["-88", "-89", "-99", "-98", "87", "77"]), "")
    d = d[d["rp2"] == 1].copy()
    age = age[d.index]
    # export delimited writes the value label of the (unlabelled-after-mvdecode) gender
    gl = labs["sexo_eanna"]
    gender = d["sexo_eanna"].map(lambda v: gl.get(int(v), str(int(v))) if pd.notna(v) else np.nan)
    for c in TIMES:
        d[c] = d[c].map(hhmm)
    w = pd.DataFrame({"id": np.arange(1, len(d) + 1),
                      "cov_gender": gender.values,
                      "cov_age_range": age.replace("", np.nan).values,
                      "cov_age_first_job": d["cp1"].values})
    parts = []
    for c in reversed(Q):
        p = w.copy()
        p.insert(1, "item", c)
        p.insert(2, "resp", pd.to_numeric(d[c], errors="coerce").values)
        parts.append(p)
    long = pd.concat(parts, ignore_index=True)
    long = long[long["item"].str.startswith("c")]
    if not legacy:
        cp9 = long["item"].str.startswith("cp9_")
        long = long[~(cp9 & (long["resp"] >= 88))]
        long = long[long["resp"].notna()]
    return long.reset_index(drop=True)


if __name__ == "__main__":
    raw, out = sys.argv[1], sys.argv[2]
    df = build(raw, "--legacy" in sys.argv)
    for c in ("id", "resp", "cov_age_first_job"):
        s = df[c].dropna()
        if s.eq(s.round()).all():
            df[c] = df[c].astype("Int64")
    fn = f"{out}/chile_2023_children-adolescents-survey_cp_c.csv"
    df.to_csv(fn, index=False)
    print(fn, len(df), df["id"].nunique())
