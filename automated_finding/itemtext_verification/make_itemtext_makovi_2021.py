#!/usr/bin/env python3
"""Item text for the three makovi_2021 tables (10.1038/s41598-021-00329-z).

The cheap case in Step 3.5: the article's own SI PDF (41598_2021_329_MOESM1_ESM.pdf,
section "Survey First Data Collection") prints the Qualtrics survey verbatim,
stems and every response option. The data file (MOESM2) stores each answer as
its option label, and data/makovi_2021_racism_environment.py keeps the
deposit's column names (rscale_1..11, escale_1..7, air_polluted, white.risk,
black.risk, poor.risk, self.risk) as `item`.

Code-to-stem tie: rscale_k / escale_k are the k-th question of the survey's
Symbolic Racism / Environmental Concern block (positional), checked by
verify_makovi_2021_*.R; air_polluted and the four *.risk columns are tied by
name ("Air pollution is an issue in the area where you live", "Risk - White
Americans" ...). This script asserts every stem and option string below occurs
in the PDF text, in block order, and that the option labels for each item are
exactly the labels observed in that data column (so each option_text row maps
to the data's own label for that resp).

Survey typos are kept verbatim: "Neither agree not disagree" (item 10 only),
"Pushing way to slowly". Administered in English to US MTurk workers, so no
language/_translated columns.
"""
import csv
import io
import re
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

import pandas as pd
import requests

HERE = Path(__file__).resolve().parent.parent
REPO = HERE.parent
sys.path.insert(0, str(REPO / "data"))
import makovi_2021_racism_environment as P  # noqa: E402

OUT_DIR = HERE / "itemtext_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
SUPP = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC8589981/supplementaryFiles"
COLS = ["table", "section_id", "item", "instrument", "instructions",
        "section_prompt", "item_text", "correct_response", "option_text", "resp"]
INSTR = "Please answer the following questions according to your personal beliefs."

STEMS = {
    "rscale_1": "It's really a matter of some people not trying hard enough; if Black people would only try harder they could be just as well off as White people.",
    "rscale_2": "Irish, Italian, Jewish, and many other minorities overcame prejudice and worked their way up. Black people should do the same.",
    "rscale_3": "Black people work just as hard to get ahead as most other Americans.",
    "rscale_4": "How responsible, in general, do you hold Black people in this country for their outcomes in life?",
    "rscale_5": "Black people are demanding too much from the rest of society.",
    "rscale_6": "Some say that Black leaders have been trying to push too fast. Others feel that they haven't pushed fast enough. What do you think?",
    "rscale_7": "How much of the racial tension that exists in the United States today do you think Black people are responsible for creating?",
    "rscale_8": "Black people generally do not complain as much as they should about their situation in society.",
    "rscale_9": "Generations of slavery and discrimination have created conditions that make it difficult for Black people to work their way out of the lower class.",
    "rscale_10": "Discrimination against Black people is no longer a problem in the United States.",
    "rscale_11": "Has there been a lot of real change in the position of Black people in the past few years, only some, not much at all?",
    "escale_1": "How concerned are you about environmental issues?",
    "escale_2": "How willing would you be to pay much higher prices to help the environment?",
    "escale_3": "How willing would you be to accept cuts in your standard of living in order to protect the environment?",
    "escale_4": "In general, how dangerous do you think air pollution caused by cars is to people?",
    "escale_5": "Do you think air pollution caused by industry is dangerous for the environment?",
    "escale_6": "Many environmental threats are exaggerated.",
    "escale_7": "The Earth simply cannot continue to support population growth at its present rate.",
    "air_polluted": "Air pollution is an issue in the area where you live.",
    "white.risk": "White Americans' lives are negatively impacted by environmental issues.",
    "black.risk": "Black Americans' lives are negatively impacted by environmental issues.",
    "poor.risk": "Poor Americans' lives are negatively impacted by environmental issues.",
    "self.risk": "Your own life is negatively impacted by environmental issues.",
}
META = {
    "makovi_2021_symbolic_racism": ("Symbolic Racism Scale (11 items, as administered by Makovi & Kasak-Gliboff 2021)", INSTR),
    "makovi_2021_environmental_concern": ("Environmental Concern Scale (as administered by Makovi & Kasak-Gliboff 2021)", INSTR),
    "makovi_2021_environmental_risk": ("Perceived environmental risk to groups (authors' items)", None),
}


def norm(s: str) -> str:
    s = s.replace("’", "'").replace("‘", "'")
    return re.sub(r"\s+", " ", s).strip()


def pdf_text() -> str:
    r = requests.get(SUPP, headers=UA, timeout=300)
    r.raise_for_status()
    blob = zipfile.ZipFile(io.BytesIO(r.content)).read("41598_2021_329_MOESM1_ESM.pdf")
    with tempfile.NamedTemporaryFile(suffix=".pdf") as f:
        f.write(blob)
        f.flush()
        txt = subprocess.run(["pdftotext", "-layout", f.name, "-"], check=True,
                             capture_output=True, text=True).stdout
    return norm(txt)


def main() -> None:
    txt = pdf_text()
    start = txt.index("Symbolic Racism Scale Please answer")
    assert INSTR in txt[start:start + 200]
    pos = start
    for item, stem in STEMS.items():          # stems occur in block order
        i = txt.find(norm(stem), pos)
        assert i >= 0, ("stem not found in order", item)
        pos = i + len(stem)
        m = {**P.SR, **P.EC, **P.RISK}[item]
        seg = txt[pos:pos + 400]
        for lab in m:                         # every option printed right after its stem
            assert lab in seg, (item, lab)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for table, items in P.TABLES.items():
        resp = pd.read_csv(HERE / "irw_output" / f"{table}.csv")
        assert set(resp["item"]) == set(items)
        instrument, instr = META[table]
        rows = []
        for item, m in items.items():
            assert set(resp.loc[resp["item"] == item, "resp"]) <= set(m.values())
            for lab, v in sorted(m.items(), key=lambda kv: kv[1]):
                rows.append([table, f"{table}_1", item, instrument, instr, None,
                             STEMS[item], None, lab, v])
        out = pd.DataFrame(rows, columns=COLS)
        out.to_csv(OUT_DIR / f"{table}__items.csv", index=False,
                   quoting=csv.QUOTE_NONNUMERIC, na_rep="NA")
        print(f"{table}__items.csv: {len(out)} rows, {out['item'].nunique()} items")


if __name__ == "__main__":
    main()
