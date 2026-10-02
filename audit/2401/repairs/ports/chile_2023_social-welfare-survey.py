"""Python port of the `_h` and `_yy` blocks of data/chile_2023_social-welfare-survey.do (#2401).

No Stata on the audit machine, so this reproduces the .do's code path for the two
tables the #2401 batch1 fixes touch, and nothing else.

    python3 chile_2023_social-welfare-survey.py RAW_DTA OUT_DIR [--legacy]

--legacy : the .do as it stood before #2401, AND before #2326 added
           `drop if missing(resp)` (which is what the live tables were built by),
           i.e. keeps NA-resp rows and applies no #2401 fix. Used only to prove the
           port reproduces the live tables.
default  : the edited .do: #2326's NA drop plus the #2401 fixes
           (h3_d/h3_e code 3 -> missing; yy3 moved to cov_income_clp).

Source: https://observatorio.ministeriodesarrollosocial.gob.cl/encuesta-bienestar-social-2023
        storage/docs/bienestar-social/2023/Base_de_datos_EBS_2023.dta.rar
"""
import sys
import numpy as np
import pandas as pd

SENT = (-88, -99, -89, -98)
BLOCKS = {
    "h": "h1 h2_a h2_b h2_c h2_d h3_a h3_b h3_c h3_d h3_e h4_a h4_b h4_c".split(),
    "yy": "yy1 yy2 yy3 yy4 yy5 yy5_a".split(),
}


def stata_substr4(s):
    return s.map(lambda x: x[3:] if isinstance(x, str) else x)


def prepare(path):
    r = pd.io.stata.StataReader(path)
    d = r.read(convert_categoricals=False)
    labs = r.value_labels()
    # decode (missing numeric -> "")
    def decode(col):
        m = labs.get(col, {})
        return d[col].map(lambda v: m.get(int(v), "") if pd.notna(v) else "")
    age = stata_substr4(decode("tramoebs2"))
    g = decode("sg02")
    g = g.replace({"No sabe": "6. No Sabe", "Otro (especifique)": "7. Otro (especifique)"})
    g = stata_substr4(g)
    # clock(hora_hr, "YMDhm") -> unix seconds
    dt = pd.to_datetime(d["hora_hr"], format="%Y-%m-%d %H:%M", errors="coerce")
    date = (dt - pd.Timestamp("1970-01-01")) // pd.Timedelta(seconds=1)
    out = pd.DataFrame({"id": np.arange(1, len(d) + 1), "date": date,
                        "cov_age_range": age.replace("", np.nan),
                        "cov_gender": g.replace("", np.nan)})
    items = [c for b in BLOCKS.values() for c in b]
    for c in items:
        v = pd.to_numeric(d[c], errors="coerce")
        out[c] = v.where(~v.isin(SENT))
    return out


def block(w, name, legacy):
    cols = BLOCKS[name]
    parts = []
    for c in reversed(cols):      # the .do appends each new item ABOVE the earlier ones
        p = w[["id", "date", "cov_age_range", "cov_gender", c]].rename(columns={c: "resp"})
        p.insert(1, "item", c)
        parts.append(p)
    long = pd.concat(parts, ignore_index=True)
    long = long[["id", "item", "resp", "date", "cov_age_range", "cov_gender"]]
    if not legacy:
        long = long[long["resp"].notna()]                       # #2326
        if name == "h":                                          # #2401
            long = long[~(long["item"].isin(["h3_d", "h3_e"]) & (long["resp"] == 3))]
        if name == "yy":                                         # #2401
            inc = w.set_index("id")["yy3"]
            long = long[long["item"] != "yy3"].copy()
            long["cov_income_clp"] = long["id"].map(inc)
    return long.reset_index(drop=True)


def write(df, path):
    df = df.copy()
    for c in df.columns:
        if c in ("id", "resp", "date", "cov_income_clp"):
            s = df[c]
            if s.dropna().eq(s.dropna().round()).all():
                df[c] = s.astype("Int64")
    df.to_csv(path, index=False)


if __name__ == "__main__":
    raw, out = sys.argv[1], sys.argv[2]
    legacy = "--legacy" in sys.argv
    w = prepare(raw)
    for name in BLOCKS:
        df = block(w, name, legacy)
        fn = f"{out}/chile_2023_social-welfare-survey_{name}.csv"
        write(df, fn)
        print(fn, len(df), df["id"].nunique())
