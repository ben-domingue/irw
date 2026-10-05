"""ENCCEJA (Exame Nacional para Certificação de Competências de Jovens e
Adultos), INEP microdata, irw#2644.  Builds encceja_<year>_<level>_<area> and
its nominal companion encceja_<year>_<level>_<area>_nom.

    python3 data/encceja.py 2024 [2025 ...]   # writes CSVs into the cwd

Source: download.inep.gov.br/microdados/microdados_encceja_<year>.zip (INEP
"Dados abertos / microdados"), the same site and terms as ENEM. Ben ruled on
2026-10-01 (#2643, #2644) that the INEP licence covers the whole family.
Years published as of 2026-10: 2018-2020 and 2022-2025 (no 2021 file; the
exam was not held in 2021).  The zip is fetched into CACHE if missing and the
two CSVs are read straight out of it.

The build mirrors the ENEM scripts (data/enem_<year>.R) on every point that
carries over:

* one table per year x area, scored 0/1 against INEP's key, with the letter
  marked kept in resp_raw (A-D, "." blank, "*" double mark) and `position` +
  `booklet` (CO_POSICAO, CO_PROVA) alongside;
* the nominal companion is the same frame with resp_raw renamed to `text`
  (datastandard.md, "The raw response and the nominal tranche"), for
  irw_nominal, exactly as data/nominal/enem.R does for ENEM;
* "." and "*" score 0 for candidates who sat the area, which is INEP's own
  scoring; resp_raw keeps them distinguishable;
* only candidates INEP flags present (TP_PRESENCA_<area> == 1) enter a table;
  absent (0) and eliminated (2) do not;
* items whose key (TX_GABARITO) is not a letter are dropped: INEP writes "X"
  for an item it annulled (2022 "Exclusão pedagógica", 2025), which no
  response can match;
* candidates sitting an adapted booklet (the "Ledor" / reader version) are
  kept, scored by booklet x position, and only items on the standard booklet
  enter the table (ENEM's standard item set);
* item = INEP's CO_ITEM.  Items recur across ENCCEJA years under the same
  code, so tables of one level x area link across years by item;
* a table is capped at 1,000,000 candidates by simple random sample, as
  ENEM's are; no table reaches it (the largest, encceja_2019_em_mt, has
  874,787 present), so every table holds every candidate present;
* no covariates, as ENEM ships none.  The microdata carry sex, age band,
  state of testing and a questionnaire; none is taken.

What differs from ENEM, and why
* ENCCEJA certifies two levels, which are separate exams with their own items:
  ensino fundamental (TP_CERTIFICACAO 1, `ef`) and ensino médio (2, `em`).
  The microdata hold both in the same four columns (TX_RESPOSTAS_LC/CH/MT/CN);
  the item file names the areas per level, and that code is used in the table
  name: ef = lp (Língua Portuguesa, LEM, Artes, Ed. Física), hg (História e
  Geografia), ma (Matemática), ci (Ciências Naturais); em = lc, ch, mt, cn.
* Candidates register area by area (a person who already holds some areas
  sits only the rest), so presence is filtered per area, not across all four
  as in ENEM.  The same id appears in several areas of a year.
* Four options (A-D), not five.
* id = NU_INSCRICAO, which INEP publishes masked ("Campo com máscara").  It is
  unique within a year's file; it is not documented as stable across years
  and must not be used to follow anyone between years.
* Only the "Nacional Regular" file is used.  The prison-system file
  (Nacional PPL) is a different administration with its own booklets and is
  left out, as ENEM's PPL booklets are.
* The key is the item file's TX_GABARITO, checked slot by slot against the
  key string INEP ships per candidate (TX_GABARITO_<area>). They agree
  everywhere except 2019 em_lc item 58882 (item file C, microdata B); there
  the letter whose choice correlates with INEP's own score NU_NOTA_LC wins
  (B, r = +.18, against C, r = -.10), and any future conflict that is not
  that clear-cut stops the build.
* Items INEP abandoned when calibrating ("IN_ITEM_ABAN" = 1, e.g. "Problemas
  na convergência") but still keyed A-D are kept: ENEM keeps them too, and
  the responses are real.  Only unkeyed ("X") items are dropped.

Checks (each stops the build): the per-candidate key string INEP ships in
TX_GABARITO_<area> must equal the item file's keys for that booklet read in
position order (this is what validates the position mapping); response codes
are only A-D . *; no id x item duplicates; and, as enem_checks.R does, the
scored table must not look mis-keyed (share of items below chance, median
item-rest correlation, share of all-wrong candidates).
"""
import io
import os
import sys
import zipfile
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

CACHE = Path(os.environ.get("ENCCEJA_CACHE", Path.home() / ".cache" / "irw-encceja"))
URL = "https://download.inep.gov.br/microdados/microdados_encceja_{y}.zip"

COL_AREAS = ["LC", "CH", "MT", "CN"]          # microdata column suffixes
LEVELS = {"1": "ef", "2": "em"}
KEYS = set("ABCD")
ALPHABET = set("ABCD.*")
CAP = 1_000_000
SEED = 5150                                    # ENEM's sampling seed

# enem_checks.R thresholds, chance moved to 1/4
CHANCE = 0.25
MAX_SHARE_BELOW_CHANCE = 0.50
MIN_MEDIAN_ITEM_REST = 0.05
MAX_SHARE_LOW_ITEM_REST = 0.60
MAX_SHARE_ALL_WRONG = 0.05
CHECK_IDS = 5000
CHECK_SEED = 1942

# Tables allowed past the below-chance check, with the evidence. 2018 em_mt:
# 17 of 30 items have p < 1/4, but the key is INEP's -- the per-candidate key
# string in the microdata matches the item file, the summed score correlates
# .75 with INEP's NU_NOTA_MT, no other booklet's key order fits better, and
# INEP's own 3PL difficulties for the form run b = 1.1 to 6.5 (median ~2.3).
# It is a very hard form, not a mis-keyed one; the other three checks pass.
BELOW_CHANCE_OK = {"encceja_2018_em_mt"}


def zip_path(year):
    p = CACHE / f"microdados_encceja_{year}.zip"
    if not p.exists():
        CACHE.mkdir(parents=True, exist_ok=True)
        tmp = p.with_suffix(".part")
        with urllib.request.urlopen(URL.format(y=year)) as r, open(tmp, "wb") as f:
            while chunk := r.read(1 << 20):
                f.write(chunk)
        tmp.rename(p)
    return p


def members(zf):
    """(item file, regular-national file) inside the zip; names vary by year."""
    names = [n for n in zf.namelist() if n.lower().endswith(".csv")]
    items = [n for n in names if "ITENS_PROVA" in n.upper()]
    reg = [n for n in names
           if ("REG_NAC" in n.upper() or "NACIONAL_REGULAR" in n.upper())
           and "QSE" not in n.upper()]
    assert len(items) == 1 and len(reg) == 1, (items, reg)
    return items[0], reg[0]


def read_csv(zf, name, **kw):
    with zf.open(name) as fh:
        first = fh.readline().decode("latin1")
    sep = ";" if first.count(";") > first.count(",") else ","
    with zf.open(name) as fh:
        return pd.read_csv(io.TextIOWrapper(fh, encoding="latin1"), sep=sep,
                           dtype=str, **kw)


def item_rest(w):
    """Item-rest correlations of a person x item 0/1 matrix (NaN = not taken)."""
    tot = np.nansum(w, axis=1)
    out = []
    for j in range(w.shape[1]):
        x = w[:, j]
        ok = ~np.isnan(x)
        r = tot[ok] - x[ok]
        if len(np.unique(x[ok])) < 2 or len(np.unique(r)) < 2:
            out.append(np.nan)
        else:
            out.append(np.corrcoef(x[ok], r)[0, 1])
    return np.array(out)


def check_scored(df, name):
    p = df.groupby("item")["resp"].mean()
    rng = np.random.default_rng(CHECK_SEED)
    ids = df["id"].unique()
    if len(ids) > CHECK_IDS:
        ids = rng.choice(ids, CHECK_IDS, replace=False)
    w = (df[df["id"].isin(ids)]
         .pivot(index="id", columns="item", values="resp").to_numpy(float))
    ir = item_rest(w)
    nper = df.groupby("id")["resp"].agg(["size", "sum"])
    full = nper[nper["size"] == nper["size"].mode().iloc[0]]
    stats = {
        "share_below_chance": float((p < CHANCE).mean()),
        "median_item_rest": float(np.nanmedian(ir)),
        "share_low_item_rest": float(np.nanmean(ir < 0.05)),
        "share_all_wrong": float((full["sum"] == 0).mean()),
        "min_item_rest": float(np.nanmin(ir)),
    }
    print(f"  {name}: " + " ".join(f"{k}={v:.3f}" for k, v in stats.items()))
    bad = []
    if stats["share_below_chance"] > MAX_SHARE_BELOW_CHANCE and name not in BELOW_CHANCE_OK:
        bad.append("below chance")
    if stats["median_item_rest"] < MIN_MEDIAN_ITEM_REST: bad.append("median item-rest")
    if stats["share_low_item_rest"] > MAX_SHARE_LOW_ITEM_REST: bad.append("low item-rest")
    if stats["share_all_wrong"] > MAX_SHARE_ALL_WRONG: bad.append("all wrong")
    if bad:
        raise SystemExit(f"{name}: scored table fails {bad}")
    return stats


def build_year(year):
    zf = zipfile.ZipFile(zip_path(year))
    itf, regf = members(zf)
    items = read_csv(zf, itf)
    if "TP_PROVA" in items:                       # 2022+: 1 = Nacional Regular
        items = items[items["TP_PROVA"] == "1"]
    items["pos"] = items["CO_POSICAO"].astype(int)

    cols = (["NU_INSCRICAO", "TP_CERTIFICACAO"]
            + [f"{p}_{a}" for p in ("TP_PRESENCA", "CO_PROVA", "TX_RESPOSTAS",
                                    "TX_GABARITO", "NU_NOTA") for a in COL_AREAS])
    md = read_csv(zf, regf, usecols=cols)
    assert md["NU_INSCRICAO"].is_unique
    print(f"[{year}] {len(md)} registrations in {regf}")

    summary = []
    for lev, levname in LEVELS.items():
        for ca in COL_AREAS:
            sub = md[(md["TP_CERTIFICACAO"] == lev) & (md[f"TP_PRESENCA_{ca}"] == "1")]
            sub = sub[["NU_INSCRICAO", f"CO_PROVA_{ca}", f"TX_RESPOSTAS_{ca}",
                       f"TX_GABARITO_{ca}", f"NU_NOTA_{ca}"]]
            sub.columns = ["id", "booklet", "raw", "gab", "nota"]
            assert sub[["id", "booklet", "raw", "gab"]].notna().all().all(), \
                f"{year} {levname} {ca}: present with no string"

            used = sub["booklet"].unique()
            bk = items[items["CO_PROVA"].isin(used)]
            assert set(bk["CO_PROVA"]) == set(used), f"booklet not in item file: {set(used)-set(bk['CO_PROVA'])}"
            assert (bk["TP_CERTIFICACAO"] == lev).all()
            # 2022 lists one LC item under a CN booklet's code for a non-regular
            # TP_PROVA; within the regular booklets the area must be single
            area = bk["SG_AREA"].unique()
            assert len(area) == 1, (year, levname, ca, area)
            area = area[0].lower()
            name = f"encceja_{year}_{levname}_{area}"

            std = bk[bk["IN_ITEM_ADAPTADO"] == "0"]["CO_PROVA"].unique()
            assert len(std) == 1, (name, std)
            std = std[0]

            width = sub["raw"].str.len().mode().iloc[0]
            off = (sub["raw"].str.len() != width).sum()
            assert off / len(sub) < 0.01, f"{name}: {off} off-length"
            sub = sub[sub["raw"].str.len() == width]
            if off:
                print(f"  {name}: dropped {off} off-length strings")

            std_set = set(bk.loc[bk["CO_PROVA"] == std, "CO_ITEM"])

            # position map per booklet: string slot j = j-th smallest CO_POSICAO
            maps = {}
            overrides = []
            for b, g in bk.groupby("CO_PROVA"):
                g = g.sort_values("pos")
                assert len(g) == width and g["pos"].is_unique, (name, b, len(g))
                assert (np.diff(g["pos"].to_numpy()) == 1).all(), (name, b)
                keystr = "".join(g["TX_GABARITO"])
                gabs = sub.loc[sub["booklet"] == b, "gab"].unique()
                assert len(gabs) == 1, f"{name} booklet {b}: {len(gabs)} key strings"
                # compared only where the slot holds a standard-booklet item:
                # in 2025 the ef_lp reader booklet swaps in item 143331 (key B)
                # at slot 11, yet its microdata key string repeats the standard
                # booklet's (C). That item never enters the table either way.
                instd = g["CO_ITEM"].isin(std_set).to_numpy()
                keys = g["TX_GABARITO"].to_numpy().copy()
                # an item the item file annuls ("X") is dropped below whatever
                # the microdata string says (2025 ef_hg item 137322 reads D there)
                diff = [j for j in range(width)
                        if instd[j] and keystr[j] in KEYS and gabs[0][j] != keystr[j]]
                if gabs[0] != keystr and not diff:
                    print(f"  {name} booklet {b}: key string differs from the item file "
                          f"only at slots that do not enter the table; ignored")
                # Where the two keys disagree on a standard item, keep the one
                # INEP scored with: the letter whose choice correlates higher
                # with INEP's own proficiency score NU_NOTA. One case so far,
                # 2019 em_lc item 58882 (slot 19): item file C (r = -.10),
                # microdata B (r = +.18), so B.
                if diff:
                    gb = sub[(sub["booklet"] == b) & sub["nota"].notna()]
                    nota = gb["nota"].astype(float).to_numpy()
                    for j in diff:
                        ch = gb["raw"].str[j].to_numpy()
                        r = {k: np.corrcoef(ch == k, nota)[0, 1]
                             for k in (keystr[j], gabs[0][j])}
                        win = max(r, key=r.get)
                        assert win in KEYS and abs(r[keystr[j]] - r[gabs[0][j]]) > 0.1, \
                            f"{name} booklet {b} slot {j+1}: key conflict not clear-cut {r}"
                        keys[j] = win
                        overrides.append(f"{g['CO_ITEM'].iloc[j]}:{keystr[j]}->{win}")
                        print(f"  {name} booklet {b} slot {j+1} item {g['CO_ITEM'].iloc[j]}: "
                              f"item file key {keystr[j]} (r={r[keystr[j]]:.2f}) vs microdata "
                              f"{gabs[0][j]} (r={r[gabs[0][j]]:.2f}); using {win}")
                m = g[["pos", "CO_ITEM"]].to_numpy()
                maps[b] = np.column_stack([m, keys])

            n_present = len(sub)
            if len(sub) > CAP:
                rng = np.random.default_rng(SEED)
                keep = rng.choice(len(sub), CAP, replace=False)
                sub = sub.iloc[np.sort(keep)]
                print(f"  {name}: sampled {CAP} of {n_present}")

            parts = []
            for b, g in sub.groupby("booklet"):
                m = maps[b]
                arr = np.frombuffer("".join(g["raw"]).encode("ascii"),
                                    dtype="S1").reshape(len(g), width).astype(str)
                n = len(g)
                parts.append(pd.DataFrame({
                    "id": np.repeat(g["id"].to_numpy(), width),
                    "item": np.tile(m[:, 1], n),
                    "key": np.tile(m[:, 2], n),
                    "resp_raw": arr.ravel(),
                    "position": np.tile(m[:, 0], n).astype(int),
                    "booklet": b,
                }))
            df = pd.concat(parts, ignore_index=True)
            del parts

            std_items = items[items["CO_PROVA"] == std]
            annulled = std_items[~std_items["TX_GABARITO"].isin(KEYS)]
            if len(annulled):
                print(f"  {name}: dropping {len(annulled)} annulled item(s): "
                      + ", ".join(f"{r.CO_ITEM}(key={r.TX_GABARITO})"
                                  for r in annulled.itertuples()))
            keep_items = set(std_items.loc[std_items["TX_GABARITO"].isin(KEYS), "CO_ITEM"])
            df = df[df["item"].isin(keep_items)]
            assert df["key"].isin(KEYS).all()

            bad = set(df["resp_raw"].unique()) - ALPHABET
            assert not bad, f"{name}: unexpected codes {bad}"
            df["resp"] = (df["resp_raw"] == df["key"]).astype(int)
            df = df[["id", "item", "resp", "resp_raw", "position", "booklet"]]
            df = df.sort_values(["id", "position"], kind="stable")
            assert not df.duplicated(["id", "item"]).any(), f"{name}: duplicate id x item"

            st = check_scored(df, name)
            codes = df["resp_raw"].value_counts(normalize=True)
            print(f"  {name}: {df['id'].nunique()} ids, {df['item'].nunique()} items, "
                  f"{len(df)} rows; raw " + " ".join(f"{k}={v:.4f}" for k, v in codes.items()))

            df.to_csv(f"{name}.csv", index=False)
            df.rename(columns={"resp_raw": "text"}).to_csv(f"{name}_nom.csv", index=False)
            summary.append({"table": name, "year": year, "level": levname, "area": area,
                            "n_present": n_present, "n_ids": df["id"].nunique(),
                            "n_items": df["item"].nunique(), "n_rows": len(df),
                            "annulled_dropped": len(annulled),
                            "key_overrides": ";".join(sorted(set(overrides))),
                            "booklets": ",".join(sorted(used)), "standard_booklet": std,
                            "blank": float(codes.get(".", 0)),
                            "double": float(codes.get("*", 0)),
                            "p_mean": float(df["resp"].mean()), **st})
            del df
    return summary


if __name__ == "__main__":
    rows = []
    for y in sys.argv[1:]:
        rows += build_year(int(y))
    out = Path("encceja_build_summary.csv")
    s = pd.DataFrame(rows)
    if out.exists():
        old = pd.read_csv(out)
        s = pd.concat([old[~old["table"].isin(s["table"])], s])
    s.to_csv(out, index=False)
