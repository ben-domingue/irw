#!/usr/bin/env python3
# Persian Lexicon Project: visual lexical decision, trial level.
# Nemati, F., Westbury, C., Hollis, G., & Haghbin, H. (2022). The Persian
# Lexicon Project: minimized orthographic neighbourhood effects in a dense
# language. Journal of Psycholinguistic Research. doi:10.1007/s10936-022-09863-x
# Data: OSF https://osf.io/tb4m6 (doi:10.17605/OSF.IO/TB4M6), CC BY 4.0 (OSF
# licence field). File "Persian Lexicon Project.xlsx", sheet "LD Data".
#
# Layout (person-first, as every lexical decision table in IRW):
#   id   = participant (`ID`, 1-113)
#   item = the letter string shown (`WORD`, Persian script); nonwords are items
#   resp = 1 if the yes/no lexical decision was correct (`CORRECT`; equals
#          TARGET == RESPONSE on every row)
#   rt   = `RTMS` / 1000 (seconds)
#   trial_number = `ORDER`, the presentation position within the session (0-199)
#   itemcov_lexicality = word / nonword (`TARGET` b / n)
#   cov_gender, cov_l1 = `GENDER`, `L1` (first language)
# Not carried: `TYPE` (0/AL/OL/SP for words, NW for nonwords; the deposit does
# not define the word codes), the item norms on the row (frequency, length,
# phonology; they are on the deposit's Dictionary sheet) and `WORDNUM`.
#
# Usage: python3 nemati_2022_persian_ld.py <Persian Lexicon Project.xlsx> <out_dir>
import os
import sys

import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from irw_validate._checks import run_qc  # noqa: E402

src = sys.argv[1] if len(sys.argv) > 1 else "Persian Lexicon Project.xlsx"
out_dir = sys.argv[2] if len(sys.argv) > 2 else "."

d = pd.read_excel(src, sheet_name="LD Data")
assert (((d.TARGET == d.RESPONSE).astype(int)) == d.CORRECT).all()
assert set(d.TARGET) == {"b", "n"}
assert not d.duplicated(["ID", "WORD"]).any()
assert (d.groupby("ID")[["GENDER", "L1"]].nunique() == 1).all().all()

out = pd.DataFrame({
    "id": d.ID.astype(int),
    "item": d.WORD.astype(str),
    "resp": d.CORRECT.astype(int),
    "rt": d.RTMS / 1000,
    "trial_number": d.ORDER.astype(int),
    "cov_gender": d.GENDER,
    "cov_l1": d.L1,
    "itemcov_lexicality": d.TARGET.map({"b": "word", "n": "nonword"}),
})
out = out.sort_values(["id", "trial_number"]).reset_index(drop=True)

name = "nemati_2022_persian_ld"
# The shared checks (irw_validate.contract `no_validator`): fails block,
# warnings are printed (concentrated 0/1 responses are expected here).
_checks = run_qc(out)
_fails = [(c.name, c.detail) for c in _checks if c.status == "fail"]
assert not _fails, _fails
for _c in _checks:
    if _c.status == "warn":
        print(f"  [qc warn] {_c.name}: {_c.detail[:120]}")
os.makedirs(out_dir, exist_ok=True)
out.to_csv(os.path.join(out_dir, name + ".csv"), index=False)
print(f"{name}: rows={len(out)} ids={out.id.nunique()} items={out.item.nunique()} "
      f"resp={out.resp.min()}-{out.resp.max()} rt={out.rt.min():.3f}-{out.rt.max():.3f}")
