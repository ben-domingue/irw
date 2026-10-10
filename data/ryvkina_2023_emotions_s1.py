#!/usr/bin/env python3
"""Ryvkina et al. (2023), the EMOTIONS project, Study 1: experience sampling of
social interactions, activities and affect in German university students,
January-April 2020, with coronavirus worries added in the second wave, via
the openESM harmonised copy.

Source: https://zenodo.org/records/17386601 (openESM 0056_ryvkina)
DOI: 10.5281/zenodo.17386601
Original deposit: https://osf.io/6kzx3/ (OSF). The OSF project carries no
    licence field; the data paper's repository metadata gives the licence as
    CC BY 4.0 for "all EMOTIONS data ... shared on osf.io/6kzx3/".
Paper: Ryvkina E, Kroencke L, Geukes K, Scharbert J, Back MD (2023).
    Understanding Psychological Responses to the COVID-19 Pandemic Through ESM
    Data: The EMOTIONS Project. Journal of Open Psychology Data 11(1), 6.
    doi:10.5334/jopd.83
Data: 0056_ryvkina_ts.tsv
License: CC BY 4.0 (openESM copy; JOPD data paper for the OSF deposit)
Item text: shipped. German wording and the authors' English from the Study 1
    codebooks (Codebook_EMOTIONS_Study1_Wave1.pdf / _Wave2.pdf),
    translation_source=study_supplied. The wording matches Study 2
    (data/ryvkina_2023_emotions_s2.py) for every item both studies share
    except worry_ownstudies, which Study 1 words "… mein Studium." / "… my
    university studies."

Study 1 is a separate sample from Study 2 (0057_ryvkina): the 315 id values
the two openESM records share are a numbering coincidence, since the Study 2
ids were generated after data collection. It ran in two waves, S1W1
(2020-01-14 to 04-17) and S1W2 (2020-03-17 to 04-18), merged by the authors:
327 people, 29,512 ESM reports. Each report asks first whether the person had
a social interaction of more than 5 minutes since the last report, then
either about that interaction or about their last activity; S1W2 reports
also ask about coronavirus worries.

Tables written (one per block as administered; all items 1-6)
--------------
ryvkina_2023_s1_interaction_behavior    6 items, after an interaction
ryvkina_2023_s1_interaction_perception  6 items, after an interaction
ryvkina_2023_s1_interaction_affect      12 emotions, after an interaction
ryvkina_2023_s1_activity_experience     8 items, after an activity without
                                        interaction
ryvkina_2023_s1_activity_affect         12 emotions, after an activity
ryvkina_2023_s1_corona_worries          13 items, S1W2 reports only

Study 1 asks fewer items than Study 2: no beh_corona, beh_help,
corona_asked, comfort, corona_thinking, "socially excluded" or "lonely", and
no worry about one's children's health.

Coding notes
------------
* Every report follows exactly one branch (interaction 18,034, activity
  11,478; asserted), so the interaction and activity tables are missing by
  design on the other branch's waves.
* The worry block exists only in S1W2 (every S1W2 report, no S1W1 report;
  asserted): it was added once the pandemic began.
* `wave` is each person's report number in time order across both study
  waves, shared by all six tables. For the 179 people in both waves, every
  S1W1 report precedes every S1W2 report. `date` is the report's start time
  as Unix seconds.
* The timestamps are German local time, although openESM suffixes them with
  `Z`: openESM's created_esm equals the OSF S1W1 and S1W2 files'
  created_esm verbatim, and as stamped 99.86% of S1W1 reports fall inside
  the participant's own chosen prompting window (98.65% if the stamps were
  UTC in winter time, 92.96% in summer time), as in Study 2. They are parsed
  as Europe/Berlin; S1W1 spans the 2020-03-29 DST change, and no stamp falls
  in the skipped hour (asserted by the parse).
* resp is as shipped; no item is reverse-scored.
* No covariates: the authors removed gender and age from the shared files
  for anonymisation.

Not shipped
-----------
int_pleasure, int_activity, occup_pleasure, occup_activity
              Affect-grid sliders (0-100), two single items per context.
type_interaction, communication, no_interactionpartner,
interaction_partner1-5, type_activity, digital
              Context and categorical reports, not ratings.
static file   Trait questionnaires: a separate job.
"""

import csv
import os
import sys

import pandas as pd
import requests

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "automated_finding"))
from irw_triage_updated import run_qc          # noqa: E402

REC = "17386601"
TS_FILE = "0056_ryvkina_ts.tsv"
AF = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                  "automated_finding")
OUTDIR = os.path.join(AF, "irw_output")
ITEMDIR = os.path.join(AF, "itemtext_output")
HEADERS = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

SCALE = range(1, 7)
APPLIES = (("Trifft gar nicht zu", "Does not apply at all"),
           ("Trifft voll und ganz zu", "Applies completely"))
AMOUNT = (("Sehr wenig", "Very little"), ("Sehr viel", "Very much"))
RATE = ("Sie können Ihre Antworten zwischen 1 (Trifft gar nicht zu) und 6 "
        "(Trifft voll und ganz zu) abstufen.",
        "You can give a rating between 1 (Does not apply at all) and 6 "
        "(Applies completely).")

EMOTIONS = [("proud", "Stolz", "Proud"), ("success", "Erfolgreich",
            "Successful"), ("superior", "Überlegen", "Superior"),
            ("angry", "Verärgert", "Angry"),
            ("envious", "Neidisch", "Envious"),
            ("resentful", "Missgünstig", "Resentful"),
            ("ashamed", "Beschämt", "Ashamed"),
            ("insecure", "Verunsichert", "Insecure"),
            ("enthusiastic", "Begeistert", "Enthusiastic"),
            ("relaxed", "Gelassen", "Relaxed"),
            ("anxious", "Ängstlich", "Anxious"), ("sad", "Traurig", "Sad")]
WORRY_PROMPT = ("Bitte beantworten Sie die folgenden Fragen auf einer Skala "
                "zwischen 1 (Sehr wenig) und 6 (Sehr viel). Ich mache mir "
                "wegen der Ausbreitung des Corona-Virus Sorgen um…",
                "Please answer the following questions on a scale from 1 "
                "(Very little) to 6 (Very much). Due to the coronavirus "
                "outbreak, I am worried about...")

# table -> (instrument, (German prompt, English prompt), anchors,
#           [(column, German, English)], number of people)
TABLES = {
    "ryvkina_2023_s1_interaction_behavior": (
        "EMOTIONS ESM: own behaviour in the last social interaction "
        "(partly after the Interpersonal Adjective Scales)",
        ("Während der Interaktion habe ich folgendes Verhalten gezeigt: "
         + RATE[0], "During the interaction, I exhibited the following "
         "behavior: " + RATE[1]), APPLIES, [
            ("beh_leadership", "Ich habe die Führung übernommen.",
             "I took the lead."),
            ("beh_criticism", "Ich habe andere kritisiert.",
             "I criticised others."),
            ("beh_uninvolved", "Ich habe mich nicht beteiligt.",
             "I did not get involved."),
            ("beh_selfesteem", "Ich war selbstsicher.", "I was self-assured."),
            ("beh_unfriendly", "Ich war unfreundlich.", "I was unfriendly."),
            ("beh_reserved", "Ich habe mich zurückgezogen.",
             "I was reserved."),
        ]),
    "ryvkina_2023_s1_interaction_perception": (
        "EMOTIONS ESM: perceived treatment in the last social interaction",
        ("Während der Interaktion habe ich Folgendes wahrgenommen: "
         + RATE[0], "During the interaction, I perceived the following: "
         + RATE[1]), APPLIES, [
            ("status_admired", "Ich wurde bewundert.", "I was admired."),
            ("status_criticised", "Ich wurde kritisiert.",
             "I was criticised."),
            ("status_ignored", "Ich wurde nicht beachtet.", "I was ignored."),
            ("status_respected", "Ich wurde respektiert.",
             "I was respected."),
            ("status_upstaged", "Andere haben versucht, mir die Schau zu "
             "stehlen.", "Others tried to steal the show from me."),
            ("status_sidelined", "Ich wurde übergangen.", "I was sidelined."),
        ]),
    "ryvkina_2023_s1_interaction_affect": (
        "EMOTIONS ESM: affect after the last social interaction "
        "(partly after the PANAS/PANAS-X)",
        ("Wie haben Sie sich direkt nach der Interaktion gefühlt? "
         + RATE[0], "How did you feel immediately after the interaction? "
         + RATE[1]), APPLIES,
        [(f"int_{k}", de, en) for k, de, en in EMOTIONS]),
    "ryvkina_2023_s1_activity_experience": (
        "EMOTIONS ESM: experience of the last activity without interaction",
        ("Während der Beschäftigung habe ich Folgendes erlebt: " + RATE[0],
         "During the activity, I perceived the following: " + RATE[1]),
        APPLIES, [
            ("pleasant", "Ich fand die Beschäftigung angenehm.",
             "I found the activity pleasant."),
            ("fun", "Ich habe Spaß gehabt.", "I had fun."),
            ("done", "Ich habe Aufgaben erledigt, die mir von anderen "
             "aufgetragen wurden.", "I did tasks that others assigned to "
             "me."),
            ("intellectual", "Ich war intellektuell/geistig angeregt.",
             "I was intellectually/mentally stimulated."),
            ("overwhelmed", "Ich war überfordert.", "I was overwhelmed."),
            ("bored", "Ich war gelangweilt.", "I was bored."),
            ("concentrated", "Ich war konzentriert.", "I was concentrated."),
            ("motivated", "Ich war motiviert.", "I was motivated."),
        ]),
    "ryvkina_2023_s1_activity_affect": (
        "EMOTIONS ESM: affect after the last activity "
        "(partly after the PANAS/PANAS-X)",
        ("Wie haben Sie sich direkt nach der Beschäftigung gefühlt? "
         + RATE[0], "How did you feel immediately after the activity? "
         + RATE[1]), APPLIES,
        [(f"occup_{k}", de, en) for k, de, en in EMOTIONS]),
    "ryvkina_2023_s1_corona_worries": (
        "EMOTIONS ESM: coronavirus-related momentary worries",
        WORRY_PROMPT, AMOUNT, [
            ("worry_ownhealth", "… meine Gesundheit.", "… my health."),
            ("worry_ownsoclife", "… mein soziales Leben.",
             "… my social life."),
            ("worry_ownstudies", "… mein Studium.",
             "… my university studies."),
            ("worry_healthsystem", "… das Gesundheitssystem in Deutschland.",
             "… the healthcare system in Germany."),
            ("worry_soclife", "… den sozialen Zusammenhalt in Deutschland.",
             "… social cohesion in Germany."),
            ("worry_economy", "… die Wirtschaft/das Arbeitsleben in "
             "Deutschland.", "… the economy/working life in Germany."),
            ("worry_cullife", "… das kulturelle Leben in Deutschland.",
             "… cultural life in Germany."),
            ("worry_parentshealth", "… die Gesundheit meiner Eltern.",
             "… my parents’ health."),
            ("worry_grandparentshealth", "… die Gesundheit meiner "
             "Großeltern.", "… my grandparents’ health."),
            ("worry_siblingshealth", "… die Gesundheit meiner Geschwister.",
             "… my siblings’ health."),
            ("worry_partnerhealth", "… die Gesundheit meiner Partnerin/"
             "meines Partners.", "… my partner’s health."),
            ("worry_friendshealth", "… die Gesundheit meiner engen Freunde.",
             "… my close friends’ health."),
            ("worry_peoplehealth", "… die Gesundheit meines weiteren "
             "sozialen Umfelds (Kommilitonen/innen, sonstige Bekannte).",
             "… the health of my wider social environment (fellow "
             "university students, other acquaintances)"),
        ]),
}


def load():
    path = os.path.join("/tmp", f"zenodo_{REC}_{TS_FILE}")
    if not os.path.exists(path):
        api = requests.get(f"https://zenodo.org/api/records/{REC}",
                           headers=HEADERS, timeout=60).json()
        url = next(f["links"]["self"] for f in api["files"]
                   if f["key"] == TS_FILE)
        r = requests.get(url, headers=HEADERS, timeout=600)
        r.raise_for_status()
        with open(path, "wb") as fh:
            fh.write(r.content)
    return pd.read_csv(path, sep="\t", low_memory=False)


def write_items(table, instrument, prompt, anchors, items):
    rows = []
    for col, de, en in items:
        for v in SCALE:
            opt = (anchors[0] if v == SCALE[0] else
                   anchors[1] if v == SCALE[-1] else ("", ""))
            rows.append([table, f"{table}_1", col, instrument, "German", "",
                         "", prompt[0], prompt[1], de, en, "", opt[0],
                         opt[1], v])
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
    df = load()
    assert len(df) == 29512 and df["id"].nunique() == 327, df.shape
    assert df["interaction"].isin([1, 2]).all()
    assert (df["interaction"] == 1).sum() == 18034
    cols_of = {t: [c for c, *_ in spec[3]] for t, spec in TABLES.items()}
    beh = cols_of["ryvkina_2023_s1_interaction_behavior"]
    act = cols_of["ryvkina_2023_s1_activity_experience"]
    assert df.loc[df["interaction"] == 1, beh].notna().all().all()
    assert df.loc[df["interaction"] == 2, act].notna().all().all()
    assert df.loc[df["interaction"] == 2, beh].isna().all().all()
    worry = df["worry_ownhealth"].notna()
    assert (worry == (df["dataset"] == "S1W2")).all()

    # stamped "Z" but German local time (see coding notes)
    local = pd.to_datetime(df["created_esm"].str.rstrip("Z"))
    df["date"] = (local.dt.tz_localize("Europe/Berlin", ambiguous="raise",
                                       nonexistent="raise")
                  .dt.tz_convert("UTC").astype("int64") // 10**9)
    assert not df.duplicated(["id", "date"]).any()
    span = df.groupby(["id", "dataset"])["date"].agg(["min", "max"]).unstack()
    both = span.dropna()
    assert len(both) == 179
    assert (both[("max", "S1W1")] < both[("min", "S1W2")]).all()
    df = df.sort_values(["id", "date"], kind="stable")
    df["wave"] = df.groupby("id").cumcount() + 1

    for table, (instrument, prompt, anchors, items) in TABLES.items():
        cols = cols_of[table]
        long = df.melt(id_vars=["id", "wave", "date"], value_vars=cols,
                       var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"])
        assert (long["resp"] % 1 == 0).all()
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp", "wave", "date"]]
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
        ipath, k = write_items(table, instrument, prompt, anchors, items)
        print(f"  {ipath}: {k} item text rows")


if __name__ == "__main__":
    main()
