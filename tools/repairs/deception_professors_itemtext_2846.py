"""Re-key deception_professors__items (irw_text_3) to the rebuilt table's item codes (irw#2846).

    python3 deception_professors_itemtext_2846.py LIVE_ITEMS_CSV SOURCE_SAV OUT_CSV

data/deception_professors.R now names items by source variable and splits the
two coded open answers into one 0/1 item per category. This takes the live item
text (one row per item x observed resp) and:
  * renames items 1-4, 6-19 to the source variable names (mapping in #2846,
    checked against the .sav by value ranges);
  * drops item 5 (orthogonal_to_rigor, a category, not an item);
  * replaces items 20/21 by two rows (resp 0/1) per category item, whose
    item_text is the source variable label of that category column.
Every other column is carried over unchanged.
"""
import sys

import pandas as pd
import pyreadstat

NAMES = ("decept_percent_psych decept_percent_eco decept_percent_socsci decept_rigorous "
         "orthogonal_to_rigor psych_considerdecept eco_considerdecept gensci_considerdecept "
         "eco_poolbans eco_journalbans psych_poolbans psych_journalban gensci_journalban "
         "banharmful_eco banharmful_psych banharmful_gensci you_percent_decept you_worry_rigor "
         "you_limit_decept").split()
LESS = ["orthogonal_to_rigor", "necessary_or_more_rigorous", "immoral", "misinterprets_deception",
        "depends_on_method", "hurts_future_studies", "subjects_notdeceived",
        "its_lazy_unnecessary", "other"]
NODEC = ["not_relevant", "not_necessary", "iam_economist", "lose_trust_pool",
         "need_trust_study", "difficult_publish", "unethical", "other2"]


def main(live_csv, sav, out_csv):
    d = pd.read_csv(live_csv, dtype=str, keep_default_na=False)
    keep = d[~d.item.isin(["5", "20", "21"])].copy()
    keep["item"] = keep.item.map({str(i + 1): n for i, n in enumerate(NAMES)})
    assert keep.item.notna().all()
    _, meta = pyreadstat.read_sav(sav, metadataonly=True)
    label = {k.lower(): v for k, v in meta.column_names_to_labels.items()}
    tmpl = d.iloc[0].to_dict()
    rows = []
    for prefix, cats in (("reason_less_rigorous_", LESS), ("reason_no_deception_", NODEC)):
        for c in cats:
            for resp, opt in ((0, "No: the answer was not coded into this category"),
                              (1, "Yes: the answer was coded into this category")):
                r = dict(tmpl)
                r.update(item=prefix + c.replace("other2", "other"), item_text=label[c],
                         option_text=opt, resp=str(resp), correct_response="NA",
                         section_prompt="NA")
                rows.append(r)
    out = pd.concat([keep, pd.DataFrame(rows)], ignore_index=True)[d.columns]
    out.to_csv(out_csv, index=False)
    print(f"{out_csv}: rows={len(out)} items={out.item.nunique()}")


if __name__ == "__main__":
    main(*sys.argv[1:4])
