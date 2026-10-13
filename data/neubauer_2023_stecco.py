#!/usr/bin/env python3
"""Neubauer & Schmiedek (2023), STECCO -- Starting Tertiary Education during
the Corona Crisis: the ambulatory assessment phase (five ESM beeps a day plus
an end-of-day questionnaire, 14 days, April-July 2021) of German first-year
university students, via the openESM harmonised copy.

Source: https://zenodo.org/records/17347975 (openESM 0062_neubauer)
DOI: 10.5281/zenodo.17347975
Original deposit: https://osf.io/bhq3p/ (OSF, CC BY 4.0); "data esm.csv",
    "data eod.csv" and "data baseline.csv"
Paper: Neubauer AB, Schmiedek F (2023). Approaching academic adjustment on
    multiple time scales. Zeitschrift für Erziehungswissenschaft 27(1),
    147-168. doi:10.1007/s11618-023-01182-8
Data: 0062_neubauer_ts.tsv (responses); "data baseline.csv" from OSF
    (https://osf.io/download/c8swh/) for gender and age, which openESM does
    not ship
License: CC BY 4.0 (openESM copy and OSF deposit)
Item text: shipped for every table except the BMPN. German wording and the
    authors' English from the STECCO codebook (Section 3, ambulatory
    assessment), translation_source=study_supplied. The codebook gives only
    excerpts of the BMPN items. The father version of the last control item
    reads "... das ihr nicht gepasst hat" in the codebook (carried over from
    the mother version) and is transcribed as printed.

322 students. The ESM beeps (1-5) were sent at quasi-random times in five
two-hour blocks; the end-of-day questionnaire (EOD, "beep 6") opened in the
evening.

Tables written (all items 1-7)
--------------
ESM, beeps 1-5:
neubauer_2023_stecco_esm_affect            10 items: "Right now, I feel..."
neubauer_2023_stecco_study_motivation      8 items: why one worked for one's
                                           studies since the last survey
                                           (only if one had)
neubauer_2023_stecco_activity_motivation   8 items: the same reasons for
                                           another activity of 30+ minutes
                                           (only if one had not studied)
neubauer_2023_stecco_emotion_regulation    5 items, after the HFERST
                                           (reappraisal x3, suppression,
                                           rumination)
End of day:
neubauer_2023_stecco_eod_bmpn              18 items, Balanced Measure of
                                           Psychological Needs, today
neubauer_2023_stecco_eod_affect            10 items: "Today, I felt..."
neubauer_2023_stecco_study_satisfaction    11 items, after the NEPS
neubauer_2023_stecco_mother_parenting      8 items: autonomy support and
                                           control by the mother today
neubauer_2023_stecco_father_parenting      8 items: the same for the father

Coding notes
------------
* `wave` is each person's report number in time order across ESM and EOD
  reports, shared by all nine tables; `date` is the report's start time as
  Unix seconds.
* openESM's start_time is true UTC for this record (unlike the other openESM
  copies, whose `Z` stamps are local time): the raw STARTED is Europe/Berlin
  local time and sits two hours after the raw Unix send time IV01_01, while
  openESM's start_time sits minutes after it. It is parsed as UTC.
* -1 means "not applicable" in the emotion-regulation items and "not
  applicable (no contact today)" in the parenting items: it is not a scale
  point and is dropped as missing.
* resp is as shipped; no item is reverse-scored.
* cov_gender (female/male/diverse; "prefer not to say" -> missing) and
  cov_age come from the baseline questionnaire, joined on id; 12 people have
  no baseline row.

Not shipped
-----------
location, company, activity and study-format checkboxes, number of
activities, time studying, time with mother/father
              Context and time-use reports, not ratings.
weekly and panel questionnaires
              Other STECCO study parts, not in this openESM record.
"""

import csv
import os
import sys

import pandas as pd
import requests

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "automated_finding"))
from irw_triage_updated import run_qc          # noqa: E402

REC = "17347975"
TS_FILE = "0062_neubauer_ts.tsv"
BASELINE_URL = "https://osf.io/download/c8swh/"
AF = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                  "automated_finding")
OUTDIR = os.path.join(AF, "irw_output")
ITEMDIR = os.path.join(AF, "itemtext_output")
HEADERS = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

SCALE = range(1, 8)
VERY = (("überhaupt nicht", "not at all"), ("sehr", "very"))
AGREE = (("Stimme überhaupt nicht zu", "completely disagree"),
         ("Stimme voll und ganz zu", "completely agree"))
APPLIES = (("trifft überhaupt nicht zu", "completely disagree"),
           ("trifft völlig zu", "completely agree"))
GENDER = {1: "female", 2: "male", 3: "diverse"}     # 4 = prefer not to say

AFFECT = [("happy", "glücklich", "happy"), ("afraid", "ängstlich", "afraid"),
          ("sad", "traurig", "sad"), ("balanced", "ausgeglichen", "balanced"),
          ("exhausted", "erschöpft", "exhausted"),
          ("cheerful", "fröhlich", "cheerful"),
          ("worried", "besorgt", "worried"),
          ("lively", "voller Energie", "lively"),
          ("angry", "wütend", "angry"), ("relaxed", "entspannt", "relaxed")]
# (suffix, German for studying, German for another activity, English for
#  studying, English for another activity)
MOTIVES = [
    ("others_disappointed",
     "…weil andere von mir enttäuscht gewesen wären, wenn ich das nicht "
     "gemacht hätte", None,
     "…because others would have been disappointed in me if I had not done "
     "so", None),
    ("felt_bad", "…weil ich mich schlecht gefühlt hätte, wenn ich das nicht "
     "gemacht hätte.", None, "...because I would have felt bad if I had not "
     "done this.", None),
    ("important", "…weil mir die Arbeit, die ich gemacht habe, persönlich "
     "wichtig war.", "…weil mir die Tätigkeit,persönlich wichtig war.",
     "...because the work I did was personally important to me.",
     "...because the activity I did was personally important to me."),
    ("interesting", "…weil ich die Arbeit interessant fand.",
     "…weil ich die Tätigkeit interessant fand.",
     "...because I found the work interesting.",
     "...because I found the activity interesting."),
    ("compulsory", "…weil ich musste (z.B. wegen Pflichtveranstaltung, oder "
     "als Voraussetzung für ein Seminar).", "…weil ich musste",
     "...because I had to (e.g. because of a compulsory course, or as a "
     "prerequisite for a seminar).", "...because I had to."),
    ("proving", "…weil ich mir selbst oder anderen beweisen wollte, dass ich "
     "etwas gut kann.", None, "..because I wanted to prove to myself or "
     "others that I can do something well.", None),
    ("understanding", "…weil ich Inhalte meines Studiums besser verstehen "
     "wollte.", "…weil ich etwas besser verstehen wollte.",
     "...because I wanted to understand the contents of my studies better.",
     "...because I wanted to understand it better."),
    ("enjoyment", "…weil mir die Arbeit Spaß bereitet hat.",
     "…weil mir die Tätigkeit Spaß bereitet hat.",
     "...because I enjoyed the work.", "...because I enjoyed the activity."),
]
PARENT = [  # (suffix, German with {M}/{m}, English with {p})
    ("autonomy", "Heute hat mich {M} meine eigenen Entscheidungen treffen "
     "lassen.", "Today my {p} allowed me to make choices of my own."),
    ("own_decisions", "Heute hat mich {M} Dinge für mich selbst entscheiden "
     "lassen.", "Today my {p} allowed me to decide things for myself."),
    ("asked_opinion", "Heute hat mich {M} bewusst nach meiner Meinung zu "
     "etwas gefragt.", "Today my {p} deliberately asked my opinion about "
     "some things."),
    ("interrupted", "Heute hat mich {M} in einem Gespräch unterbrochen.",
     "Today my {p} interrupted me during a conversation."),
    ("point_of_view", "Heute war {m} bereit, Dinge aus meiner Sicht zu "
     "betrachten.", "Today my {p} was willing to consider things from my "
     "point of view."),
    ("guilty", "Heute hat mir {m} Schuldgefühle eingeredet.",
     "Today my {p} made me feel guilty about something."),
    ("tried_change", "Heute hat {m} versucht zu beeinflussen, wie ich mich "
     "fühle oder was ich denke.", "Today my {p} tried to change how I feel "
     "or think about things."),
    ("disapproved", "Heute war {m} weniger freundlich zu mir, weil ich etwas "
     "getan habe, das ihr nicht gepasst hat.", "Today my {p} was less "
     "friendly with me because I did something {s} disapproved."),
]
PARENT_PROMPT = ("Geben Sie bitte an, wie sehr Sie diesen Aussagen in Bezug "
                 "auf heute zustimmen. Die folgenden Aussagen beziehen sich "
                 "auf Ihre{r} {who}.",
                 "Please indicate how much you agree with these statements "
                 "in relation to today. The following statements refer to "
                 "your {who_en}.")


def motives(prefix, study):
    out = []
    for suf, de_s, de_a, en_s, en_a in MOTIVES:
        de = de_s if study or de_a is None else de_a
        en = en_s if study or en_a is None else en_a
        out.append((f"{prefix}_{suf}", de, en))
    return out


def parent(who):
    if who == "mother":
        fmt = dict(M="meine Mutter", m="meine Mutter", p="mother", s="she")
        prompt = (PARENT_PROMPT[0].format(r="", who="Mutter"),
                  PARENT_PROMPT[1].format(who_en="mother"))
    else:
        fmt = dict(M="mein Vater", m="mein Vater", p="father", s="he")
        prompt = (PARENT_PROMPT[0].format(r="n", who="Vater"),
                  PARENT_PROMPT[1].format(who_en="father"))
    items = [(f"{who}_{suf}", de.format(**fmt), en.format(**fmt))
             for suf, de, en in PARENT]
    return prompt, items


ER_PROMPT = ("Wie sind Sie seit dem Aufstehen / seit der letzten Befragung "
             "mit Ihren Gefühlen umgegangen? Bitte entscheiden Sie aus dem "
             "Bauch heraus, inwieweit die unteren Aussagen auf Sie zutreffen.",
             "How have you dealt with your feelings since getting up / since "
             "the last survey? Please decide from your gut to what extent "
             "the statements below apply to you.")
MOT_PROMPT_STUDY = ("Warum haben Sie seit dem Aufstehen / seit der letzten "
                    "Befragung für Ihr Studium gearbeitet? Ich habe seit dem "
                    "Aufstehen/ seit der letzten Befragung für mein Studium "
                    "gearbeitet,…", "Why have you worked for your studies "
                    "since getting up / since the last survey? I have worked "
                    "for my studies since getting up / since the last "
                    "survey…")
MOT_PROMPT_OTHER = ("Denken Sie bitte an eine Tätigkeit, die Sie seit dem "
                    "Aufstehen / seit der letzten Befragung mindestens 30 "
                    "Minuten gemacht haben.", "Please think of an activity "
                    "that you have done for at least 30 minutes since the "
                    "last survey. I have pursued this activity....")
SAT_PROMPT = ("Wie bewerten Sie Ihr derzeitiges Studium? Bitte geben Sie an, "
              "inwieweit die folgenden Aussagen auf den heutigen Tag "
              "zutreffen.", "How would you rate your current studies? Please "
              "indicate to what extent the following statements apply to "
              "today.")
M_PROMPT, M_ITEMS = parent("mother")
F_PROMPT, F_ITEMS = parent("father")

# table -> dict(source, instrument, prompt, anchors, items=[(col, de, en)]
#               or None, columns (when items is None), sentinel)
TABLES = {
    "neubauer_2023_stecco_esm_affect": dict(
        source="esm", anchors=VERY,
        prompt=("Ich bin jetzt gerade…", "Right now, I feel…"),
        instrument="STECCO momentary affect (Neubauer & Schmiedek 2023)",
        items=[(k, f"…{de}", f"…{en}") for k, de, en in AFFECT]),
    "neubauer_2023_stecco_study_motivation": dict(
        source="esm", anchors=AGREE, prompt=MOT_PROMPT_STUDY,
        instrument="STECCO momentary study motivation: external, "
                   "introjected, identified and intrinsic regulation",
        items=motives("study_motivation", True)),
    "neubauer_2023_stecco_activity_motivation": dict(
        source="esm", anchors=AGREE, prompt=MOT_PROMPT_OTHER,
        instrument="STECCO momentary motivation for another activity: "
                   "external, introjected, identified and intrinsic "
                   "regulation",
        items=motives("activity_motivation", False)),
    "neubauer_2023_stecco_emotion_regulation": dict(
        source="esm", anchors=VERY, prompt=ER_PROMPT, sentinel=-1,
        instrument="Momentary emotion regulation, adapted from the "
                   "Heidelberg Form for Emotion Regulation Strategies "
                   "(Izadpanah et al. 2019)",
        items=[
            ("see_good_in_bad", "Ich habe versucht, auch die guten Aspekte "
             "in einer schlechten Situation zu erkennen.", "I have tried to "
             "see the good aspects in a bad situation as well."),
            ("focus_on_good", "Ich habe mich auf die guten Seiten meiner "
             "Situation konzentriert, um mich besser zu fühlen.",
             "I focused on the good aspects of my situation to feel "
             "better."),
            ("suppression", "Ich habe meine Gefühle unterdrückt.",
             "I suppressed my feelings."),
            ("changed_feeling", "Ich habe meine Gefühle geändert, indem ich "
             "über meine aktuelle Situation anders nachgedacht habe.",
             "I changed my feelings by thinking differently about my "
             "current situation."),
            ("rumination", "Ich habe immer wieder über meine Gefühle oder "
             "meine Situation nachgedacht.", "I have thought about my "
             "feelings or situation over and over again."),
        ]),
    "neubauer_2023_stecco_eod_bmpn": dict(
        source="daily", items=None,
        columns=["contact_with_people", "excluded_ostracized", "failure",
                 "own_way", "completed_difficult_project", "true_self",
                 "connected", "mastered_challenges", "intimacy", "pressure",
                 "told_what_to_do", "unappreciated",
                 "disagreements_conflicts", "even_hard_things",
                 "against_own_will", "did_stupid", "struggled",
                 "did_interesting"]),
    "neubauer_2023_stecco_eod_affect": dict(
        source="daily", anchors=VERY,
        prompt=("Ich war heute…", "Today, I felt…"),
        instrument="STECCO end-of-day affect (Neubauer & Schmiedek 2023)",
        items=[(f"{k}_daily", f"…{de}", f"…{en}") for k, de, en in AFFECT]),
    "neubauer_2023_stecco_study_satisfaction": dict(
        source="daily", anchors=APPLIES, prompt=SAT_PROMPT,
        instrument="Daily study satisfaction, items from the NEPS "
                   "(STECCO end of day)",
        items=[
            ("study_enjoy", "Heute hatte ich richtig Freude an dem, was ich "
             "studiere.", "Today I really enjoyed the subject I am "
             "studying."),
            ("study_wearing_down", "Heute hatte ich das Gefühl, dass mich "
             "das Studium auffrisst.", "Today my course of study was "
             "wearing me down."),
            ("study_satisfied", "Heute war ich mit meinem Studium insgesamt "
             "zufrieden.", "On the whole I was satisfied with my current "
             "course of study today."),
            ("study_difficult_reconcile", "Heute konnte ich mein Studium nur "
             "schwer mit anderen Verpflichtungen in Einklang bringen.",
             "Today it was very difficult for me to reconcile my course of "
             "study with other obligations."),
            ("study_interesting", "Heute fand ich mein Studium wirklich "
             "interessant.", "Today I found my course of study really "
             "interesting."),
            ("study_exhausted", "Heute fühlte ich mich durch das Studium "
             "müde und abgespannt.", "Today my course of study made me feel "
             "tired and exhausted."),
            ("study_only_necessary", "Heute habe ich für mein Studium nicht "
             "mehr gemacht, als unbedingt erforderlich war.", "Today I no "
             "longer did anything more for my studies than that which was "
             "absolutely necessary."),
            ("study_energy", "Heute habe ich sehr viel Energie investiert, "
             "um in meinem Studium erfolgreich zu sein", "Today I invested a "
             "lot of energy in being successful in my degree course"),
            ("study_identification", "Heute konnte ich mich mit meinem "
             "Studium voll identifizieren.", "Today I could fully identify "
             "with my degree program."),
            ("study_expectations", "Heute wurden die Erwartungen, die ich an "
             "mein Studium hatte, erfüllt.", "Today the expectations I had "
             "of my degree program were met."),
            ("study_consider_quitting", "Ich habe heute ernsthaft daran "
             "gedacht, mein Hauptfach zu wechseln oder das Studium ganz "
             "aufzugeben.", "Today I seriously considered changing my major "
             "subject or of giving up my course of study entirely?"),
        ]),
    "neubauer_2023_stecco_mother_parenting": dict(
        source="daily", anchors=AGREE, prompt=M_PROMPT, sentinel=-1,
        instrument="Perceived parenting today, mother: autonomy support and "
                   "psychological control (STECCO end of day)",
        items=M_ITEMS),
    "neubauer_2023_stecco_father_parenting": dict(
        source="daily", anchors=AGREE, prompt=F_PROMPT, sentinel=-1,
        instrument="Perceived parenting today, father: autonomy support and "
                   "psychological control (STECCO end of day)",
        items=F_ITEMS),
}


def fetch_zenodo(filename):
    path = os.path.join("/tmp", f"zenodo_{REC}_{filename}")
    if not os.path.exists(path):
        api = requests.get(f"https://zenodo.org/api/records/{REC}",
                           headers=HEADERS, timeout=60).json()
        url = next(f["links"]["self"] for f in api["files"]
                   if f["key"] == filename)
        r = requests.get(url, headers=HEADERS, timeout=600)
        r.raise_for_status()
        with open(path, "wb") as fh:
            fh.write(r.content)
    return path


def fetch_osf(url, name):
    path = os.path.join("/tmp", f"osf_bhq3p_{name}")
    if not os.path.exists(path):
        r = requests.get(url, headers=HEADERS, timeout=600)
        r.raise_for_status()
        with open(path, "wb") as fh:
            fh.write(r.content)
    return path


def columns(spec):
    return spec.get("columns") or [it[0] for it in spec["items"]]


def write_items(table, spec):
    rows = []
    lo, hi = spec["anchors"]
    for col, de, en in spec["items"]:
        for v in SCALE:
            opt = lo if v == SCALE[0] else hi if v == SCALE[-1] else ("", "")
            rows.append([table, f"{table}_1", col, spec["instrument"],
                         "German", "", "", spec["prompt"][0],
                         spec["prompt"][1], de, en, "", opt[0], opt[1], v])
    path = os.path.join(ITEMDIR, f"{table}__items.csv")
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, quoting=csv.QUOTE_ALL, lineterminator="\n")
        w.writerow(["table", "section_id", "item", "instrument", "language",
                    "instructions", "instructions_translated",
                    "section_prompt", "section_prompt_translated",
                    "item_text", "item_text_translated", "correct_response",
                    "option_text", "option_text_translated", "resp"])
        w.writerows(rows)
    return path, len(rows)


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    os.makedirs(ITEMDIR, exist_ok=True)
    df = pd.read_csv(fetch_zenodo(TS_FILE), sep="\t", low_memory=False)
    assert len(df) == 13880 and df["id"].nunique() == 322, df.shape
    assert ((df["source"] == "daily") == (df["beep"] == 6)).all()
    # ESM rows: the raw Unix send time (IV01_01) precedes start_time by
    # minutes, so start_time is on the UTC clock (see coding notes)
    esm = df[df["source"] == "esm"]
    lag = (pd.to_datetime(esm["start_time"], utc=True)
           - pd.to_datetime(esm["timestamp"], unit="s", utc=True))
    assert lag.between(pd.Timedelta(0), pd.Timedelta(hours=1)).mean() > 0.99

    df["date"] = (pd.to_datetime(df["start_time"], utc=True).astype("int64")
                  // 10**9)
    assert not df.duplicated(["id", "date"]).any()
    df = df.sort_values(["id", "date"], kind="stable")
    df["wave"] = df.groupby("id").cumcount() + 1

    b = pd.read_csv(fetch_osf(BASELINE_URL, "data_baseline.csv"),
                    low_memory=False)
    assert b["id"].is_unique and b["SD01"].dropna().isin([1, 2, 3, 4]).all()
    cov = pd.DataFrame({"id": b["id"].astype(str),
                        "cov_gender": b["SD01"].map(GENDER),
                        "cov_age": b["SD02_01"]})
    df = df.merge(cov, on="id", how="left", validate="many_to_one")
    assert df.drop_duplicates("id")["cov_age"].isna().sum() == 12
    covs = ["cov_gender", "cov_age"]

    for table, spec in TABLES.items():
        cols = columns(spec)
        part = df[df["source"] == spec["source"]]
        assert df.loc[df["source"] != spec["source"], cols].isna().all().all()
        long = part.melt(id_vars=["id", "wave", "date"] + covs,
                         value_vars=cols, var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"])
        if "sentinel" in spec:
            long = long[long["resp"] != spec["sentinel"]]
        assert (long["resp"] % 1 == 0).all()
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp", "wave", "date"] + covs]
        long = long.sort_values(["id", "wave", "item"]).reset_index(drop=True)

        assert long["resp"].between(SCALE[0], SCALE[-1]).all(), table
        assert not long.duplicated(["id", "item", "wave"]).any()
        assert (long.groupby("id")["date"].diff().dropna() >= 0).all()
        bad = [c for c in run_qc(long) if c.status == "fail"]
        assert not bad, (table, [(c.name, c.detail) for c in bad])

        path = os.path.join(OUTDIR, f"{table}.csv")
        long.to_csv(path, index=False)
        print(f"{path}: {long['id'].nunique()} people x "
              f"{long['item'].nunique()} items = {len(long):,} responses")
        if spec.get("items"):
            ipath, k = write_items(table, spec)
            print(f"  {ipath}: {k} item text rows")


if __name__ == "__main__":
    main()
