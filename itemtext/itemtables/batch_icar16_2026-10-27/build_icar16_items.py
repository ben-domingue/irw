"""Build tolomeo_2026_icar16__items.csv from the deposit's own items PDF.

Source: Zenodo 10.5281/zenodo.23035572 (CC BY 4.0), file "ICAR 16 ITEMS.pdf",
read with `pdftotext` and checked against the rendered page images. The zip is
pinned by sha256 in data/tolomeo_2026_icar16.py; this script reads the same
cached copy.

Shape: one row per item per printed option, 102 rows over 16 items.

`resp` is EMPTY and `resp_raw` carries the option's printed label (i, ii, ...).
The response table scores items 0/1 for correctness and records no option-level
response, so no option can be tied to a resp value. `correct_response` is empty
for the same reason: the PDF is titled "Items and Keys" and prints no key, and
nothing else in the deposit supplies one.

The MR and R3D items are figures. Their stems are transcribed verbatim and the
option labels are the ones the PDF prints next to "Options:"; the figures
themselves are not reproduced and nothing is read out of them.
"""
import csv
import re
import subprocess
import zipfile
from pathlib import Path

CACHE = Path.home() / ".cache" / "irw-zenodo" / "tolomeo_2026_icar16.zip"
MEMBER = ("Mac3581-Italian-Adaptation-and-Validation-of-the-ICAR-16-Sample-Test-27d0830/"
          "ICAR 16 ITEMS.pdf")
TABLE = "tolomeo_2026_icar16"
OUT = Path(__file__).resolve().parent / f"{TABLE}__items.csv"

##The PDF's codes carry a dot (VR.4); the response table's items do not (VR4).
CODE = re.compile(r"^(VR|LN|MR|R3D)\.(\d+)\s+Item\s+(\d+)\.\s*(.*)$")
OPTS = re.compile(r"Options:")
##"i) 2; ii) 3; ..." -- the source's spacing around the separators is erratic
##("i) Q;ii) R;iii) S;iv) T; v) U"), so split on the label rather than on ";".
LABEL = re.compile(r"\b(i|ii|iii|iv|v|vi|vii|viii)\)\s*")

tmp = Path("/tmp") / "icar16_items_text.txt"
with zipfile.ZipFile(CACHE) as z:
    pdf = Path(tmp.parent / "icar16_items.pdf")
    pdf.write_bytes(z.read(MEMBER))
subprocess.run(["pdftotext", str(pdf), str(tmp)], check=True)
lines = tmp.read_text(encoding="utf-8").splitlines()

##Build one block per item -- a CODE line starts a block and everything up to
##the next CODE line belongs to it -- because both the stem and the option list
##wrap across lines, and the MR/R3D option lines sit below a figure.
blocks = []
for raw in lines:
    line = raw.strip()
    if not line:
        continue
    m = CODE.match(line)
    if m:
        blocks.append({"item": m.group(1) + m.group(2), "n": int(m.group(3)),
                       "lines": [m.group(4).strip()]})
    elif blocks:
        blocks[-1]["lines"].append(line)

items = []
for b in blocks:
    text = " ".join(x for x in b["lines"] if x)
    o = OPTS.search(text)
    assert o, b["item"]
    stem = text[:o.start()].strip()
    parts = LABEL.split(text[o.start():][len("Options:"):].strip())
    ##split() yields ['', label, text, label, text, ...]
    pairs = [(parts[i], parts[i + 1].strip().rstrip(";").strip())
             for i in range(1, len(parts) - 1, 2)]
    items.append({"item": b["item"], "n": b["n"], "stem": [stem], "options": pairs})

assert len(items) == 16, len(items)
assert [i["n"] for i in items] == list(range(1, 17))
EXPECTED = {"VR4": 6, "VR16": 4, "VR17": 6, "VR19": 6, "LN7": 6, "LN33": 6,
            "LN34": 6, "LN58": 6, "MR45": 6, "MR46": 6, "MR47": 6, "MR55": 6,
            "R3D3": 8, "R3D4": 8, "R3D6": 8, "R3D8": 8}
assert {i["item"] for i in items} == set(EXPECTED), sorted(i["item"] for i in items)
for i in items:
    assert i["options"], i["item"]
    assert len(i["options"]) == EXPECTED[i["item"]], (i["item"], i["options"])
    assert all(t for _, t in i["options"]), i["item"]

COLS = ["table", "section_id", "item", "instrument", "instructions", "section_prompt",
        "item_text", "correct_response", "option_text", "resp", "resp_raw",
        "item_text_translated", "option_text_translated", "instructions_translated",
        "section_prompt_translated", "language"]
INSTRUMENT = ("ICAR-16 sample test, Italian adaptation (Tolomeo, Ceraudo, Balducci & "
              "Liuzza 2026)")

rows = []
for i in items:
    stem = " ".join(i["stem"]).strip()
    for label, text in i["options"]:
        rows.append({"table": TABLE, "section_id": f"{TABLE}_1", "item": i["item"],
                     "instrument": INSTRUMENT, "instructions": "NA",
                     "section_prompt": "NA", "item_text": stem,
                     "correct_response": "", "option_text": text,
                     "resp": "", "resp_raw": label,
                     "item_text_translated": "NA", "option_text_translated": "NA",
                     "instructions_translated": "NA", "section_prompt_translated": "NA",
                     "language": "Italian"})

assert len(rows) == sum(EXPECTED.values()) == 102, len(rows)
with OUT.open("w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, COLS, quoting=csv.QUOTE_MINIMAL, lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
print(f"wrote {OUT.name}: {len(rows)} rows, {len(items)} items")
for i in items:
    print(f"  {i['item']:5} {len(i['options'])} opts  {' '.join(i['stem'])[:70]}")
