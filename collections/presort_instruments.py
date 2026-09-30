"""Pre-sort the scout's review sheets into ACCEPT / REJECT / DECIDE suggestions for a human (#1712).

Reads curated/<slug>.review.csv (from scout_instruments.py) and writes
curated/instruments_presort.csv, one row per (instrument, table). The rows needing a
human sort first. Nothing here is membership: promotion to curated/<slug>.csv happens
only after Ben has marked the `decision` column.

Rules (Ben, 2026-09-30: a subscale-only table is a member, with a note; a short form is not):
  MATCH                          -> ACCEPT, basis wording/supplied as the scout set it.
  PARTIAL, matched items are one
    whole subscale (>= 80% of it,
    nothing outside it)          -> ACCEPT, note "subscale: <name> (n/k)".
  PARTIAL, anything else         -> DECIDE (a short form, or a mixed table).
  no usable English text (NAME_ONLY, or NO_MATCH whose text isn't English):
    table-name token names the
    instrument and n_items == k  -> ACCEPT, basis name.
    ... and n_items == a subscale
    size                         -> DECIDE (probably a subscale; which one can't be checked).
    no name token and n_items
    fits neither                 -> REJECT (the name hit came from a battery description).
    otherwise                    -> DECIDE.
  NO_MATCH with English text     -> REJECT (the items are a different instrument).

Rows the rules leave at DECIDE get a hand call, with its reason, in curated/instruments_overrides.csv.

Run from src/:  python3 collections/presort_instruments.py
"""
import os, re, sys
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import scout_instruments as sc

SLUGS = ["phq9", "gad7", "rses", "cesd", "dass21", "panas", "tipi", "pcl5", "gse", "erq", "mspss", "sd3"]

# subscale -> stems; a key wording belongs to the subscale whose stem it contains
# (PANAS items are single words, so those match exactly)
SUBSCALES = {
    "dass21": {
        "depression": ["positive feeling", "initiative", "look forward", "down hearted", "enthusiastic",
                       "worth much", "meaningless"],
        "anxiety": ["dryness", "breathing", "trembling", "make a fool", "close to panic", "action of my heart",
                    "scared without"],
        "stress": ["wind down", "over react", "nervous energy", "agitated", "difficult to relax", "intolerant",
                   "touchy"],
    },
    "panas": {
        "positive affect": ["interested", "excited", "strong", "enthusiastic", "proud", "alert", "inspired",
                            "determined", "attentive", "active"],
        "negative affect": ["distressed", "upset", "guilty", "scared", "hostile", "irritable", "ashamed",
                            "nervous", "jittery", "afraid"],
    },
    "erq": {
        "suppression": ["not to express", "not expressing", "to myself"],
        "reappraisal": ["change what i", "in a way that helps", "change the way i", "changing the way i", "change the way im"],
    },
    "mspss": {
        "significant other": ["special person"],
        "family": ["family"],
        "friends": ["friends"],
    },
}


def subscale_of(slug, wording):
    for name, stems in SUBSCALES.get(slug, {}).items():
        if slug == "panas":
            if wording in stems:
                return name
        elif any(s in wording for s in stems):
            return name
    return None


def english(lang):
    """The tags' language field is the only reliable signal: Portuguese text can be plain ASCII."""
    return lang.strip().lower() in ("eng", "english", "en")


# a table-name token naming one subscale -> that subscale
SUB_HINT = {
    "dass21": {"depression": r"d|dep\w*", "anxiety": r"a|anx\w*", "stress": r"s|str\w*"},
    "panas": {"positive affect": r"pa|pos\w*|positive", "negative affect": r"na|neg\w*|negative"},
}


def main():
    import irw
    avail = {t.lower() for t in irw.list_tables_with_itemtext()}
    tabs = sc.load_tables()
    insts = {i[0]: i for i in sc.INSTRUMENTS}
    rows = []
    for slug in SLUGS:
        slug_, label, k, rx, trx = insts[slug]
        rv = pd.read_csv(os.path.join(sc.CUR, f"{slug}.review.csv"), dtype=str, keep_default_na=False)
        key = [l.split("  ", 1)[1].rstrip("\n") for l in open(os.path.join(sc.CUR, f"{slug}.key.txt"))
               if not l.startswith("#")]
        subs = {}
        for w in key:
            s = subscale_of(slug, w)
            if s:
                subs.setdefault(s, []).append(w)
        if slug in SUBSCALES:  # every key item must land in exactly one subscale
            assert sum(map(len, subs.values())) == len(key), (slug, subs)
        sizes = {len(v) for v in subs.values()}
        for r in rv.itertuples():
            v = r.verdict
            n_items = int(float(r.n_items)) if r.n_items else None
            token = any(re.fullmatch(trx, t) for t in r.table.lower().replace("-", "_").split("_"))
            snippet = r.note.split("first item: ", 1)[1] if r.note.startswith("first item: ") else ""
            sugg, note, why = "DECIDE", "", ""
            if v == "MATCH":
                sugg, why = "ACCEPT", f"{r.n_mapped}/{k} items match"
            elif v == "PARTIAL":
                tx = sc.itemtext(r.table, avail) or {}
                words = set(tx.values())
                hit = [w for w in key if w in words or any(sc.close(w, x) for x in words)]
                owners = {subscale_of(slug, w) for w in hit}
                if len(owners) == 1 and None not in owners:
                    s = owners.pop()
                    if len(hit) >= 0.8 * len(subs[s]):
                        sugg, note = "ACCEPT", f"subscale: {s} ({len(hit)}/{k})"
                        why = f"matched items are the {s} subscale"
                if sugg == "DECIDE" and n_items is not None and n_items <= len(hit):
                    sugg = "REJECT"
                    why = f"short form: all {n_items} of its items are instrument items, but only {len(hit)}/{k} (short forms are out)"
                elif sugg == "DECIDE":
                    why = f"{len(hit)}/{k} items match, not one whole subscale: short form or mixed table?"
            elif v == "NO_MATCH" and english(r.language):
                sugg, why = "REJECT", f"English item text matches 0-1 key items; first item: {snippet}"
            else:  # no usable English text
                toks = r.table.lower().replace("-", "_").split("_")
                form = re.search(r"\d+$", next((t for t in toks if re.fullmatch(trx, t)), ""))
                own = re.findall(r"\d+", label + " " + slug)  # SD3, PCL-5: a digit in the name
                hint = [sub for sub, hrx in SUB_HINT.get(slug, {}).items()
                        if any(re.fullmatch(hrx, t) for t in toks[1:])]
                # a digit that is part of the instrument's own name (SD3, PCL-5) is not a form length
                if token and form and int(form.group()) != k and form.group() not in own:
                    sugg, why = "REJECT", f"table name says a {form.group()}-item form (short forms are out)"
                elif token and len(hint) == 1 and n_items == len(subs[hint[0]]):
                    sugg, note = "ACCEPT", f"subscale: {hint[0]} ({n_items}/{k})"
                    why = f"table name names the instrument and the {hint[0]} subscale; {n_items} items fits"
                elif token and n_items == k:
                    sugg, why = "ACCEPT", f"table name names it and it has {k} items"
                elif token and n_items in sizes:
                    why = f"table name names it; {n_items} items = a subscale's size, which one unverified"
                elif not token and n_items not in sizes | {k}:
                    sugg, why = "REJECT", f"name hit is from a description; table name doesn't name it and {n_items} items != {k}"
                else:
                    why = f"table name {'names' if token else 'does not name'} it; {n_items} items vs {k}"
            basis = r.basis if v == "MATCH" else ("name" if sugg != "REJECT" and v not in ("PARTIAL",) else
                                                  ("wording" if r.text_source == "study_materials" else "supplied")
                                                  if v == "PARTIAL" else "")
            rows.append(dict(instrument=label, slug=slug, table=r.table, suggestion=sugg, decision="",
                             basis=basis, member_note=note, why=why, language=r.language,
                             text_source=r.text_source, n_items=r.n_items, k=k,
                             construct_name=r.construct_name, instrument_field=r.instrument))
    out = pd.DataFrame(rows)
    # hand calls on rows the rules leave open, each with its reason (curated/instruments_overrides.csv)
    ov = pd.read_csv(os.path.join(sc.CUR, "instruments_overrides.csv"), dtype=str, keep_default_na=False)
    for o in ov.itertuples():
        hit = (out.slug == o.slug) & (out.table == o.table)
        assert hit.sum() == 1, f"override matches {hit.sum()} rows: {o.slug} {o.table}"
        out.loc[hit, ["suggestion", "basis", "member_note"]] = [o.suggestion, o.basis, o.member_note]
        out.loc[hit, "why"] = "hand call: " + o.reason
    out["_o"] = out.suggestion.map({"DECIDE": 0, "REJECT": 1, "ACCEPT": 2})
    out = out.sort_values(["_o", "slug", "table"]).drop(columns="_o")
    out.to_csv(os.path.join(sc.CUR, "instruments_presort.csv"), index=False)
    print(out.groupby(["slug", "suggestion"]).size().unstack(fill_value=0).to_string())
    print(out.suggestion.value_counts().to_string())


if __name__ == "__main__":
    main()
