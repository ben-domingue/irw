import csv, os
import pandas as pd, pyreadstat

SRC = "/tmp/zenodo_5156068_BASE_DATOS_PERFILES.sav"
AF = "/home/ben/Dropbox/projects/irw/src/automated_finding"
RESP = os.path.join(AF, "irw_output")
OUT = os.path.join(AF, "itemtext_output")
os.makedirs(OUT, exist_ok=True)

_, meta = pyreadstat.read_sav(SRC, metadataonly=True)
vvl = meta.variable_value_labels

TABLES = [f"estevez_2021_{s}" for s in
          ["homework_engagement", "motiv", "gest", "inter", "actitu",
           "feepr", "feepad", "math_attitudes"]]

FIELDS = ["table", "section_id", "item", "instrument", "instructions",
          "section_prompt", "item_text", "correct_response", "option_text",
          "resp"]

for t in TABLES:
    d = pd.read_csv(os.path.join(RESP, f"{t}.csv"))
    items = list(dict.fromkeys(d["item"]))
    obs = sorted(set(d["resp"]))
    rows = []
    for it in items:
        assert it in vvl, (t, it)
        for resp, text in sorted(vvl[it].items()):
            rows.append({"table": t, "section_id": f"{t}_1", "item": it,
                         "instrument": "", "instructions": "",
                         "section_prompt": "", "item_text": "",
                         "correct_response": "", "option_text": text,
                         "resp": int(resp)})
    labset = sorted({int(k) for it in items for k in vvl[it]})
    print(f"{t}: {len(items)} items, resp observed={obs}, labelled={labset}, rows={len(rows)}")
    with open(os.path.join(OUT, f"{t}__items.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
