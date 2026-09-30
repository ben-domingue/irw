"""Scout candidate members for the exact-instrument collections (#1712, roadmap item 10).

Writes curated/<slug>.review.csv, one per instrument: a worklist for a human, never read by
10_collections.R (see README, "two invariants"). Promotion copies approved rows into
curated/<slug>.csv and adds the registry line.

A table is a CANDIDATE if its construct name or item-text instrument field names the instrument,
or a whole table-name token does. It is then judged on its item text:

  key       the instrument's k items, taken as the k most common normalised wordings among
            the candidates (the modal wording, not one reference table's: RSES item 7 is
            "I'm" in most deposits and "I am" in some). Printed for a human to check.
  n_mapped  how many of the k key items the table carries: exact normalised match, or a
            near match (token Jaccard >= 0.8, or the key wording whole inside a longer item,
            e.g. behind "In the past week") counted separately as n_near.

basis (what a promoted member's `basis` will say):
  wording   >= 80% of items map and the text came from the study's own materials
            (provenance text_source = study_materials): identity is observed.
  supplied  >= 80% map, but IRW supplied the wording (canonical_instrument,
            translated_substitute, or no provenance row): identity is IRW's assertion.
  name      no usable English item text; only the metadata names the instrument.

verdict: MATCH (>= 80%), PARTIAL (some items map: short form, subscale, or a different form),
NO_MATCH (English text, < 2 items map: probably a different instrument), NAME_ONLY.

Run from src/:  python3 collections/scout_instruments.py [slug ...]
Item text is fetched with the irw package, which disk-caches under ~/.cache/irw.
"""
import collections as co
import glob, os, re, sys, unicodedata, warnings
import pandas as pd

warnings.filterwarnings("ignore")
SRC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
META = os.path.join(SRC, "metadata")
CUR = os.path.join(SRC, "collections", "curated")

# slug, label, k, regex over free-text instrument fields, regex a whole table-name token must match
INSTRUMENTS = [
    ("phq9", "PHQ-9", 9, r"phq-?9\b|patient health questionnaire-?9\b|patient health questionnaire \(phq-?9", r"phq9?"),
    ("gad7", "GAD-7", 7, r"gad-?7|generali[sz]ed anxiety disorder.{0,15}7", r"gad7?"),
    ("rses", "Rosenberg Self-Esteem Scale", 10, r"rosenberg|\brses?\b", r"rses?|rosenberg"),
    ("cesd", "CES-D", 20, r"ces-?d\b|center for epidemiologic", r"cesd\d*"),
    ("dass21", "DASS-21", 21, r"dass|depression,? anxiety,? (and )?stress scale", r"dass\d*"),
    ("panas", "PANAS", 20, r"panas|positive and negative affect", r"panas\w*"),
    ("swls", "Satisfaction With Life Scale", 5, r"swls|satisfaction with life scale", r"swls"),
    ("erq", "Emotion Regulation Questionnaire", 10, r"\berq\b|emotion regulation questionnaire", r"erq"),
    ("mspss", "MSPSS", 12, r"mspss|multidimensional scale of perceived social support", r"mspss"),
    ("gse", "General Self-Efficacy Scale", 10, r"\bgse\b|general (self-efficacy|perceived self)", r"gse"),
    ("tipi", "TIPI", 10, r"tipi|ten.item personality", r"tipi"),
    ("bfi44", "BFI-44", 44, r"bfi-?44|big five inventory(?!.{0,5}(-?2|10|s\b))", r"bfi(44)?"),
    ("bfi10", "BFI-10", 10, r"bfi-?10\b", r"bfi10"),
    ("sd3", "Short Dark Triad", 27, r"\bsd3\b|short dark triad", r"sd3"),
    ("pcl5", "PCL-5", 20, r"pcl-?5|ptsd checklist for dsm-5", r"pcl5?"),
    ("pss10", "Perceived Stress Scale (PSS-10)", 10, r"\bpss\b|pss-?1[04]|perceived stress scale", r"pss(10)?"),
    ("ucla_ls", "UCLA Loneliness Scale (20 items)", 20, r"ucla loneliness|ucla-?ls|revised ucla", r"ucla\w*"),
    ("fcv19s", "Fear of COVID-19 Scale", 7, r"fcv-?19s|fear of covid-19 scale", r"fcv\w*"),
    ("lotr", "LOT-R", 10, r"lot-?r\b|life orientation test", r"lotr"),
    ("isi", "Insomnia Severity Index", 7, r"insomnia severity index|\bisi\b", r"isi"),
    ("brief_cope", "Brief COPE", 28, r"brief.?cope", r"briefcope|cope"),
]


def norm(s):
    s = unicodedata.normalize("NFKC", str(s)).lower()
    s = re.sub(r"[‘’“”]", "'", s)
    s = re.sub(r"^\s*(\(?[a-z]?\d+[a-z]?[\.\):]|[a-z][\.\)])\s+", "", s)  # leading "1." / "a)"
    s = re.sub(r"[.']", "", s)
    s = re.sub(r"[^\w\s]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def close(w, x):
    """A near match: token Jaccard >= 0.8, or the key wording whole inside a longer item
    ("in the past week i felt down hearted and blue")."""
    return jaccard(w, x) >= 0.8 or (len(w.split()) >= 3 and f" {w} " in f" {x} ")


def jaccard(a, b):
    a, b = set(a.split()), set(b.split())
    return len(a & b) / max(1, len(a | b))


def load_tables():
    rd = lambda f: pd.read_csv(os.path.join(META, f), dtype=str, keep_default_na=False)
    tags, itm, md = rd("tags.csv"), rd("itemtext_metadata.csv"), rd("metadata.csv")
    for d in (tags, itm, md):
        d["k"] = d.table.str.lower()
    tabs = pd.DataFrame({"k": sorted(set(md.k) | set(tags.k) | set(itm.k))})
    name_of = {**dict(zip(tags.k, tags.table)), **dict(zip(itm.k, itm.table)), **dict(zip(md.k, md.table))}
    tabs["table"] = tabs.k.map(name_of)
    tabs = (tabs.merge(tags[["k", "construct name", "primary language(s)"]], on="k", how="left")
                .merge(itm[["k", "instrument"]], on="k", how="left")
                .merge(md[["k", "n_items", "n_participants"]], on="k", how="left").fillna(""))
    tabs = tabs.rename(columns={"construct name": "cname", "primary language(s)": "lang"})
    tabs["name"] = (tabs.cname + " | " + tabs.instrument).str.lower()
    tabs["toks"] = tabs.k.str.replace("-", "_").str.split("_")
    prov = pd.concat([pd.read_csv(f, dtype=str) for f in
                      glob.glob(os.path.join(SRC, "itemtext", "itemtables", "*", "provenance.csv"))])
    prov["k"] = prov.table.str.lower()
    src = prov.dropna(subset=["text_source"]).drop_duplicates("k", keep="last").set_index("k").text_source
    tabs["text_source"] = tabs.k.map(src).fillna("none_recorded")
    return tabs


_TEXT = {}


def itemtext(table, avail):
    """normalised wording per item, or None. A fetch error is not absence: it raises."""
    if table.lower() not in avail:
        return None
    if table not in _TEXT:
        import irw
        d = irw.itemtext(table)
        if not isinstance(d, pd.DataFrame) or d.empty:
            _TEXT[table] = None
        else:
            d = d[d.item_text.notna()].drop_duplicates("item")
            _TEXT[table] = dict(zip(d["item"].astype(str), d.item_text.map(norm)))
    return _TEXT[table]


def scout(inst, tabs, avail):
    slug, label, k, rx, trx = inst
    hit = tabs.name.str.contains(rx, regex=True) | tabs.toks.apply(lambda ts: any(re.fullmatch(trx, t) for t in ts))
    cand = tabs[hit].copy()
    texts = {t: itemtext(t, avail) for t in cand.table}
    counts = co.Counter(w for tx in texts.values() if tx for w in set(tx.values()))
    key = [w for w, _ in counts.most_common(k)]
    rows = []
    for r in cand.itertuples():
        tx = texts[r.table]
        lang = r.lang
        base = dict(table=r.table, construct_name=r.cname, instrument=r.instrument, language=lang,
                    text_source=r.text_source, n_items=r.n_items, n_participants=r.n_participants, k=k)
        if not tx:
            rows.append({**base, "n_mapped": 0, "n_near": 0, "verdict": "NAME_ONLY", "basis": "name",
                         "note": "no item text"})
            continue
        words = set(tx.values())
        exact = sum(w in words for w in key)
        near = sum(w not in words and any(close(w, x) for x in words) for w in key)
        n = exact + near
        if n >= 0.8 * k:
            verdict, basis = "MATCH", ("wording" if r.text_source == "study_materials" else "supplied")
        elif n >= 2:
            verdict, basis = "PARTIAL", ""
        elif lang and not lang.lower().startswith("eng"):
            verdict, basis = "NAME_ONLY", "name"
        else:
            verdict, basis = "NO_MATCH", ""
        note = {"NAME_ONLY": "item text not in English",
                "PARTIAL": "first item: " + next(iter(tx.values()))[:80],
                "NO_MATCH": "first item: " + next(iter(tx.values()))[:80]}.get(verdict, "")
        rows.append({**base, "n_mapped": n, "n_near": near, "verdict": verdict, "basis": basis, "note": note})
    out = pd.DataFrame(rows).sort_values(["verdict", "table"])
    return out, key, counts


def main(slugs):
    import irw
    avail = {t.lower() for t in irw.list_tables_with_itemtext()}
    tabs = load_tables()
    os.makedirs(CUR, exist_ok=True)
    summary = []
    for inst in INSTRUMENTS:
        if slugs and inst[0] not in slugs:
            continue
        out, key, counts = scout(inst, tabs, avail)
        out.to_csv(os.path.join(CUR, f"{inst[0]}.review.csv"), index=False)
        with open(os.path.join(CUR, f"{inst[0]}.key.txt"), "w") as f:
            f.write(f"# {inst[1]}: the {inst[2]} modal wordings (n tables carrying each)\n")
            f.writelines(f"{counts[w]:3d}  {w}\n" for w in key)
        v = out.verdict.value_counts()
        summary.append(dict(slug=inst[0], candidates=len(out), **{c: int(v.get(c, 0)) for c in
                            ["MATCH", "PARTIAL", "NO_MATCH", "NAME_ONLY"]},
                            wording=int((out.basis == "wording").sum()), supplied=int((out.basis == "supplied").sum())))
        print(summary[-1], flush=True)
    print(pd.DataFrame(summary).to_string(index=False))


if __name__ == "__main__":
    main(sys.argv[1:])
