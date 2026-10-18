"""Gen Z acceptance of AI-powered study assistants (UTAUT-shaped, Indonesia).

Source: https://zenodo.org/records/18320735
DOI: 10.5281/zenodo.18320735
Data: Final Data.csv (259 respondents x 28 columns)
License: CC BY 4.0 (Zenodo record, licence id cc-by-4.0)
Item text: not shipped. The export carries positional codes only (PE1 .. USE4)
  with no stem, no codebook and no questionnaire file, and the constructs are
  UTAUT's. See the rights note below -- the wording is exactly what must not be
  reproduced without a located grant, so this is a skip on two grounds.

The deposit's creator field names an institution, "Binus University", with no
individual author, so the table is named for it -- the same convention the
2026-10-18 batch B used for its `binus` tables.

RIGHTS. The seven blocks are UTAUT/UTAUT2 constructs (Venkatesh et al.):
performance expectancy, effort expectancy, social influence, facilitating
conditions, perceived trust, behavioural intention, use behaviour. The register
carries a `hold` row for "UTAUT2 / task-technology fit / challenge-hindrance
appraisal blocks" but scoped to one other deposit (family Chen2026-GenAI), so no
row covers this one. Its 2026-10-15 silence rule is what applies: a named
third-party instrument with no located grant is a hold, not a permission.
The RESPONSE table ships because the item codes are positional and no item text
is shipped, so no instrument wording is exposed -- the same reasoning BATCH_LOG
2026-10-18i used for the ProQOL. Flagged in TODO as a register-row request for
UTAUT/UTAUT2 generally.

SCALE. Every block is 1-6, not the 1-5 that most of this Indonesian TAM family
uses. Asserted per item rather than inherited from the family, which is the
2026-10-18i lesson: three sibling deposits were 1-6 where the rest were 1-5 and
only a per-table assertion caught them.

Seven 4-item constructs, one table each, following batch B's one-file-per-scale
handling of PLS-SEM batteries (the open question for Ben is noted in TODO).
"""
import os

import pandas as pd

import sys
from pathlib import Path as _Path
sys.path.insert(0, str(_Path(__file__).resolve().parent.parent))
from irw_validate._checks import run_qc  # noqa: E402
_RAW_BASE = _Path(__file__).resolve().parent.parent / \
    "automated_finding" / "runs" / "raw"

RAW = os.environ.get(
    "BINUS_RAW",
    str(_RAW_BASE / "Final_Data.csv"))
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "..", "automated_finding", "irw_output")

SCALES = {
    "performance_expectancy":  ["PE1", "PE2", "PE3", "PE4"],
    "effort_expectancy":       ["EE1", "EE2", "EE3", "EE4"],
    "social_influence":        ["SI1", "SI2", "SI3", "SI4"],
    "facilitating_conditions": ["FC1", "FC2", "FC3", "FC4"],
    "perceived_trust":         ["PT1", "PT2", "PT3", "PT4"],
    "behavioural_intention":   ["BI1", "BI2", "BI3", "BI4"],
    "use_behaviour":           ["USE1", "USE2", "USE3", "USE4"],
}
SCALE = {1, 2, 3, 4, 5, 6}


def main():
    d = pd.read_csv(RAW)
    print(f"read {d.shape[0]} rows x {d.shape[1]} cols")
    used = set()
    for cols in SCALES.values():
        used |= set(cols)
    unaccounted = [c for c in d.columns if c not in used]
    for c in unaccounted:
        print(f"  UNACCOUNTED {c!r}")
    assert not unaccounted

    d = d.reset_index(drop=True)
    d["id"] = d.index + 1
    os.makedirs(OUT, exist_ok=True)
    written = set()
    for name, cols in SCALES.items():
        assert all(c in d.columns for c in cols), name
        long = d.melt(id_vars=["id"], value_vars=cols,
                      var_name="item", value_name="resp").dropna(subset=["resp"])
        long["resp"] = long["resp"].astype(int)
        for it, g in long.groupby("item"):
            bad = set(g["resp"].unique()) - SCALE
            assert not bad, f"{name}/{it}: {sorted(bad)} outside {sorted(SCALE)}"
        assert long["id"].nunique() >= 100 and long["item"].nunique() > 1
        table = f"binus_2025_{name}"
        assert table not in written
        written.add(table)
        # The shared checks, which the script's own assertions are not
        # (irw_validate.contract `no_validator`). Fails block; the
        # warnings here are legitimate and are printed.
        _checks = run_qc(long)
        _fails = [(c.name, c.detail) for c in _checks if c.status == "fail"]
        assert not _fails, _fails
        for _c in _checks:
            if _c.status == "warn":
                print(f"    [qc warn] {_c.name}: {_c.detail[:160]}")
        long[["id", "item", "resp"]].to_csv(
            os.path.join(OUT, f"{table}.csv"), index=False)
        print(f"  {table}: {long['id'].nunique()} ids x "
              f"{long['item'].nunique()} items = {len(long)} responses")


if __name__ == "__main__":
    main()
