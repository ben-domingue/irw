"""Rank prefiltered candidates so triage starts with the highest-yield slice.

Scored entirely from metadata the prefilter already collected (title,
resolved filenames, file count, licence, file size) -- no new network calls.
The score is a triage ORDERING, not a verdict: it cannot see N, item
structure, or whether a file is respondent-level. That is what triage is for.

This replaces the per-batch copies (runs/rank_2026-08-27.py and friends),
which had drifted apart. Its one substantive change over those is the SIZE
term. Tier B of the 2026-08-27 sweep scored lower than tier A on every signal
the old scorer read, yet carried ~7.8M candidate responses to tier A's 1.3M,
because `tu_2022_achievement_motivation` (3.7M responses) reads from its title
and filename exactly like a 300-respondent survey. Its `data.sav` is 6,095,027
bytes; the tier-A zenodo deposits it was ranked below are 18k-41k. Size is the
only cheap signal that separates them, and with the term below that deposit
scores 10 (tier A) instead of 7 (tier B).

Input needs a `bytes` column (max tabular file size, in bytes) alongside the
usual prefilter columns; rows without one are simply not scored on size.

    python3 rank_leads.py --in runs/<prefilter>.csv --out runs/ranked_<x>.csv \
                          --leads runs/leads_<x>.csv
"""
import argparse
import csv
import re
from collections import Counter

# Title signals that a deposit is an item-response instrument.
#
# These are matched against deposit titles in whatever language the repository
# recorded them, so the vocabulary is multilingual. An English-only title regex
# here is the same defect that the relevance gate had until 2026-08-25 -- it
# silently scores every non-English deposit at zero on the strongest cheap
# signal, which is exactly backwards for a sweep whose whole point is to reach
# them. Measured on the 2026-08-29 non-Latin sweep: 105 of 690 deposits carry a
# non-Latin-script title and 99 of those matched nothing.
#
# Latin-script additions keep \b word boundaries; CJK/Arabic/Cyrillic cannot
# use them (no word breaks), so those alternatives are matched bare. Do not
# move a Latin token into the bare group -- an unanchored "test" matches
# "Hypotheses Testing" and "Testing the Darwinian function".
_T_STRONG_EN = (r"questionnaire|inventory|likert|psychometric|rasch|"
                r"item response|factor structur|validation of the|scale")
_T_MED_EN = (r"scale|survey|assessment|test|items|responses|measure|"
             r"reliability|validity|instrument")
_T_STRONG_LAT = (r"cuestionario|escala|inventario|question[aá]rio|fragebogen|"
                 r"skala|[ée]chelle|vragenlijst|schaal|[oö]l[cç]ek")
_T_MED_LAT = (r"encuesta|prueba|fiabilidad|validez|pesquisa|teste|umfrage|"
              r"befragung|messung|enqu[eê]te|mesure|meting|anket|"
              r"[oö]l[cç][uü]m")
_T_STRONG_CJK = (r"问卷|量表|心理测量|信度|效度|質問紙|尺度|アンケート|信頼性|妥当性|"
                 r"설문지|척도|문항|신뢰도|타당도|استبيان|استبانة|مقياس|"
                 r"опросник|шкала|анкета")
_T_MED_CJK = (r"调查|测验|测试|评估|項目|調査|評価|조사|검사|평가|"
              r"استطلاع|اختبار|تقييم|тест|анкетирование")
T_STRONG = re.compile(
    rf"(\b({_T_STRONG_EN}|{_T_STRONG_LAT})\b)|({_T_STRONG_CJK})", re.I)
T_MED = re.compile(
    rf"(\b({_T_MED_EN}|{_T_MED_LAT})\b)|({_T_MED_CJK})", re.I)
# Deposits that are structurally not per-respondent item data.
T_NEG = re.compile(
    r"\b(systematic review|meta-analys|bibliometric|simulation|genome|"
    r"protein|spectra|imaging|satellite|transcriptom|sequencing|"
    r"interview transcript|codebook only|protocol|corpus of tweets)\b", re.I)

# Filename signals.
F_SURVEY_FMT = re.compile(r"\.(sav|dta|sas7bdat|por)$", re.I)
F_RAW = re.compile(r"(raw|rohdaten|datos|base de datos|dataset|data|"
                   r"responses|respostas|answers|wide|long|item)", re.I)
F_AGG = re.compile(r"(summary|aggregat|descriptive|mean|_sd|correlat|anova|"
                   r"regression|figure|^fig|table\s*\d|output|result)", re.I)

# Size bands, in bytes of the largest tabular file. A single-instrument
# deposit of 100-600 respondents lands at 20k-80k; the bands above that are
# where the deposits worth prioritising actually live. 0 means the repo API
# reported no size -- not evidence of smallness, so it scores nothing.
SIZE_BANDS = [
    (2_000_000, 3, "size:large"),
    (300_000,   2, "size:substantial"),
    (50_000,    1, "size:moderate"),
]
# Below this, the file cannot hold the N>=100 floor times a real item set.
SIZE_TINY = 3_000


def score(row):
    title = str(row.get("title") or "")
    files = [f for f in str(row.get("tabular") or "").split("|") if f]
    try:
        nfiles = int(float(row.get("n_files") or 0))
    except ValueError:
        nfiles = 0
    try:
        nbytes = int(float(row.get("bytes") or 0))
    except ValueError:
        nbytes = 0
    s, why = 0, []

    if T_NEG.search(title):
        s -= 6; why.append("title:not-item-data")
    if T_STRONG.search(title):
        s += 5; why.append("title:instrument")
    elif T_MED.search(title):
        s += 2; why.append("title:measurement")

    if any(F_SURVEY_FMT.search(f) for f in files):
        s += 4; why.append("file:survey-format")
    if any(F_RAW.search(f) for f in files):
        s += 2; why.append("file:raw-ish")
    if files and all(F_AGG.search(f) for f in files):
        s -= 4; why.append("file:aggregate-only")

    # A single tabular file is the common shape for one instrument; hundreds
    # of files is usually per-trial/per-subject dumps needing bespoke work.
    if 1 <= nfiles <= 6:
        s += 1; why.append("files:tractable")
    elif nfiles > 50:
        s -= 2; why.append("files:many")

    for floor, pts, label in SIZE_BANDS:
        if nbytes >= floor:
            s += pts; why.append(label)
            break
    else:
        if 0 < nbytes < SIZE_TINY:
            s -= 2; why.append("size:tiny")

    if re.search(r"cc0|public domain|zero", str(row.get("license") or ""), re.I):
        s += 1; why.append("lic:cc0")
    return s, ";".join(why)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--leads", required=True,
                    help="tier A+B subset, the actual worklist")
    args = ap.parse_args()

    rows = [r for r in csv.DictReader(open(args.inp)) if r["verdict"] == "keep"]
    if not rows:
        raise SystemExit(f"no 'keep' rows in {args.inp}")
    for r in rows:
        r["score"], r["signals"] = score(r)
    rows.sort(key=lambda r: -r["score"])
    for r in rows:
        r["tier"] = ("A" if r["score"] >= 9 else
                     "B" if r["score"] >= 6 else
                     "C" if r["score"] >= 3 else "D")

    with open(args.out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)

    lead_cols = ["tier", "score", "source", "title", "doi", "url",
                 "license", "n_files", "bytes", "tabular", "signals"]
    leads = [r for r in rows if r["tier"] in ("A", "B")]
    with open(args.leads, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=lead_cols, extrasaction="ignore")
        w.writeheader(); w.writerows(leads)

    print("tier:", dict(sorted(Counter(r["tier"] for r in rows).items())))
    print("A+B by source:",
          dict(Counter(r["source"] for r in leads).most_common()))
    print(f"-> {args.out} ({len(rows)}), {args.leads} ({len(leads)})")


if __name__ == "__main__":
    main()
