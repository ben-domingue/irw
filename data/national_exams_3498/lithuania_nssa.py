#!/usr/bin/env python3
# Lithuania, national student achievement studies (NSSA / NMPT), 2012-2016: seven studies.
# Tables: lithuania_<year>_nssa_g<grade>_<subject>, one per study and subject (21 tables).
#   subject codes as in the source: mat = mathematics, sk = reading, ras = writing,
#   pp = world knowledge (pasaulio pažinimas), gm = natural sciences (gamtos mokslai),
#   sm = social sciences (socialiniai mokslai).
#
# Source data: National Agency for Education (Nacionalinė švietimo agentūra), NSSA studies
#   deposited in the Lithuanian Data Archive for SSH (LiDA), Kaunas University of Technology:
#   2012 g4 hdl:21.12137/Y8T6GV, 2012 g8 WRL1OA, 2014 g4 THUGMK, 2014 g8 6WNHS0,
#   2015 g4 C2G2VF, 2015 g8 UW5I0U, 2016 g6 IE7M6H; file LiDA_SurveyData_05xx_Data_v1.tab of
#   each (the open "Data" file; the restricted Archive files are not used).
#   Licence: CC BY-SA 4.0, confirmed in writing by LiDA (2026-11-17), which updated the
#   records' terms the same day (irw/licenseinfo/emails/lida_lithuania_nssa_2026-11-17.txt).
#   ShareAlike: these tables are CC BY-SA 4.0. Changes from the source are listed below.
# Built from: lituania_nssa*_20261126.zip, national exams collection v2 by Santiago
#   Rivadeneira Quintero (irw#3498): long format, checked cell by cell against an
#   independent rebuild from the .tab files and DDI codebooks.
#
# Layout (Ben's ruling for the collection: one table per study and subject):
#   Each study rotated booklets; a booklet carries two or three subjects. The package has
#   one test per booklet and subject; here the booklets of a subject are one table.
#   id        LiDA's anonymous student code (IDMOKSL), which embeds anonymous school and
#             class codes (Ben, 2026-11-27: keep). The same id is the same student across
#             the subject tables of one study, not across studies.
#   item      b<booklet>_<item>: item codes do not link across booklets in the source (the
#             same code is a different question in another booklet), so every item carries
#             its booklet. Candidate links between booklets are in the package's
#             enlaces_candidatos.csv, not applied.
#   resp      points (0/1, partial credit up to 4 on open questions and writing criteria).
#   resp_raw  option marked on multiple-choice questions: 1-5 = A-E, 7 = several marked,
#             99 = blank (both scored 0); 99 on open questions = not answered (scored 0).
#             Empty where the source has no option (2012 g8, 2014 g8, 2015 g8, 2016 g6).
#   cov_booklet  booklet number.  cov_female  from the source's sex field.
#   item_family  shared stimulus or block, where the package gives one.
# Caveats (see the PACKAGE.md of each zip): writing criteria score the same text (local
#   dependence); sub-questions share a stem; 2015 g4 booklet 6 is split by the source into
#   mathematics and world knowledge; no sampling weights.

import hashlib
import os
import sys
import zipfile

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402


def qc(df, name):
    """Refuse to write a table that fails any validator check; print the warnings."""
    checks = run_qc(df)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, (name, fails)
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {name} {c.name}: {c.detail[:160]}")


PKG = os.environ.get(
    "IRW_NATEXAMS_DIR",
    os.path.expanduser("~/Dropbox/projects/irw/oneoff/national-exams-3498/raw"))
PACKAGES = ["lituania_nssa", "lituania_nssa_2012g08", "lituania_nssa_2014g04",
            "lituania_nssa_2014g08", "lituania_nssa_2015g04", "lituania_nssa_2015g08",
            "lituania_nssa_2016g06"]
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "..", "automated_finding", "irw_output")


def read_pkg(z, root, name, **kw):
    with z.open(root + name) as fh:
        return pd.read_csv(fh, compression="gzip" if name.endswith(".gz") else None, **kw)


def check_sums(z, root):
    for line in filter(None, z.read(root + "SHA256SUMS").decode().split("\n")):
        h, f = line.split(maxsplit=1)
        f = f.lstrip("*")
        assert hashlib.sha256(z.read(root + f)).hexdigest() == h, f"checksum fails: {f}"


def convert():
    os.makedirs(OUT_DIR, exist_ok=True)
    for pkg in PACKAGES:
        root = pkg + "/"
        with zipfile.ZipFile(os.path.join(PKG, pkg + "_20261126.zip")) as z:
            check_sums(z, root)
            man = read_pkg(z, root, "manifiesto.csv", dtype=str)
            assert man.licencia.str.contains("CC BY-SA 4.0").all()
            assert man.fichero_crudo.str.contains("_Data_v").all(), "not the open Data file"
            man["group"] = man.test.str.replace(r"_f\d+$", "", regex=True)
            for group, rows in man.groupby("group", sort=True):
                parts = []
                for _, r in rows.iterrows():
                    booklet = int(r.forma[1:])
                    d = read_pkg(z, root, f"data/{r.test}.csv.gz",
                                 dtype={"opcion": str, "item": str})
                    it = read_pkg(z, root, f"data/{r.test}_items.csv", dtype=str)
                    p = read_pkg(z, root, f"data/{r.test}_personas.csv", dtype=str)
                    assert not d.duplicated(["id", "item"]).any()
                    assert d.id.nunique() == int(r.personas)
                    d = d.merge(it[["item", "grupo"]], on="item", how="left",
                                validate="many_to_one")
                    d = d.merge(p[["id", "sexo"]].astype({"id": int}), on="id", how="left",
                                validate="many_to_one")
                    pre = f"b{booklet}_"
                    parts.append(pd.DataFrame({
                        "id": d.id.astype(int),
                        "item": pre + d["item"],
                        "resp": d.resp.astype(int),
                        "resp_raw": d.opcion,
                        "cov_booklet": booklet,
                        "cov_female": d.sexo.map({"F": 1, "M": 0}).astype("Int64"),
                        "item_family": d["grupo"].where(d["grupo"].isna(),
                                                        pre + d["grupo"].astype(str)),
                    }))
                out = pd.concat(parts, ignore_index=True)
                # a student takes one booklet, so no id is in two booklets of a subject
                assert out.groupby("id").cov_booklet.nunique().max() == 1, group
                assert not out.duplicated(["id", "item"]).any()
                for c in ("resp_raw", "cov_female", "item_family"):
                    if out[c].isna().all():
                        out = out.drop(columns=c)
                out = out.sort_values(["id", "item"])
                _, _, year, grade, subject = group.split("_")
                name = f"lithuania_{year}_nssa_{grade}_{subject}"
                if out.id.nunique() < 100:  # datastandard.md sample floor
                    print(name, "SKIPPED:", out.id.nunique(), "persons")
                    continue
                qc(out, name)
                out.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
                print(name, len(out), "rows", out.id.nunique(), "persons",
                      out.item.nunique(), "items")


if __name__ == "__main__":
    convert()
