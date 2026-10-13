#!/usr/bin/env python3
"""Neubauer, Schmidt, Kramer & Schmiedek (2021), PACO -- Psychological
Adjustment to the COVID-19 Pandemic: daily diaries of German parents of
school-aged children in the 2020 lockdown, via the openESM harmonised copy.

Source: https://zenodo.org/records/17361779 (openESM 0072_neubauer)
DOI: 10.5281/zenodo.17361779
Original deposit: https://osf.io/wcerj/ (OSF, CC BY 4.0)
Paper: Neubauer AB, Schmidt A, Kramer AC, Schmiedek F (2021). A Little
    Autonomy Support Goes a Long Way: Daily Autonomy-Supportive Parenting,
    Child Well-Being, Parental Need Fulfillment, and Change in Child, Family,
    and Parent Adjustment Across the Adaptation to the COVID-19 Pandemic.
    Child Development 92(5), 1679-1697. doi:10.1111/cdev.13515
Data: 0072_neubauer_ts.tsv (daily diaries); 0072_neubauer_static_raw.csv
    (baseline questionnaire) for parent gender and age
License: CC BY 4.0 (openESM copy and OSF deposit)
Item text: shipped for every table except the BMPN. German wording and the
    authors' English from the PACO codebook (0072_neubauer_codebook.pdf,
    Section 3), translation_source=study_supplied. The codebook gives only
    excerpts of the BMPN items, so no BMPN item text is written.

562 parents, one evening diary a day for up to 21 days (April-May 2020),
reporting on themselves and on one target child. 559 answered at least one
rated item; per-table counts run 551-559.

Tables written
--------------
neubauer_2021_paco_parent_affect      10 items, 1-7: the parent's affect today
neubauer_2021_paco_child_affect       10 items, 1-7: the target child's affect
                                      today, as rated by the parent
neubauer_2021_paco_parenting          5 items, 1-7 (PD02): fun together,
                                      talked about worries, hard to assert
                                      oneself, drained energy, disagreements
neubauer_2021_paco_autonomy_support   5 items, 1-7 (PD03): let child decide,
                                      child did what he/she liked, told what
                                      to do, explained why, explained why not
neubauer_2021_paco_bmpn               18 items, 1-7: Balanced Measure of
                                      Psychological Needs (Sheldon & Hilpert
                                      2012; German version Neubauer & Voss
                                      2018), autonomy/competence/relatedness
                                      satisfaction and frustration
neubauer_2021_paco_worry              5 items, 1-7, from the Ambulatory Worry
                                      Scale
neubauer_2021_paco_mindfulness        4 items, 1-7, from the Multidimensional
                                      State Mindfulness Questionnaire
neubauer_2021_paco_stressors          8 yes/no items (0 = no, 1 = yes), after
                                      the Daily Inventory of Stressful
                                      Experiences
neubauer_2021_paco_corona_info        4 items, 1-5: how often one sought or
                                      shared information on the pandemic today

Coding notes
------------
* `wave` is the study day (1..21); there is one diary per person-day.
* `date` is the diary's start time as Unix seconds. openESM suffixes the
  stamps with `Z`, but the PACO files record them without a zone (SoSci
  Survey, server time) and the diary opened in the evening: 1,905 of 7,747
  start in the 19:00 hour as stamped and none between 06:00 and 18:59. They
  are parsed as Europe/Berlin (all CEST; DST began 2020-03-29, before day
  1). Diaries started after midnight refer to the previous day; `wave`
  follows the day they refer to.
* Stressors: the codebook codes 1 = no, 2 = yes; openESM's copy holds 0/1.
  0 = no, 1 = yes.
* resp is as shipped; no item is reverse-scored.
* cov_gender (female/male/diverse; "prefer not to say" -> missing) and
  cov_age are the parent's, from the baseline questionnaire, joined on
  SERIAL. One diary participant has no baseline row.

Not shipped
-----------
sleep_quality                  Single item.
school_*                       Parent report on the child's schoolwork, asked
                               only on days the child did schoolwork; mixes
                               bipolar (too easy - too difficult) and
                               agreement items.
corona_thinking_about, corona_worries, corona_acceptance
                               Two corona-worry items and one acceptance
                               item: not a scale.
time_*, activity_*, activities_total
                               Time-use reports (hours, minutes, yes/no).
baseline, post and follow-up questionnaires
                               Trait scales in the *_raw.csv files: a
                               separate job.
"""

import csv
import os
import sys

import pandas as pd
import requests

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "automated_finding"))
from irw_triage_updated import run_qc          # noqa: E402

REC = "17361779"
TS_FILE = "0072_neubauer_ts.tsv"
STATIC_FILE = "0072_neubauer_static_raw.csv"
AF = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                  "automated_finding")
OUTDIR = os.path.join(AF, "irw_output")
ITEMDIR = os.path.join(AF, "itemtext_output")
HEADERS = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

AGREE = (("stimme überhaupt nicht zu", "completely disagree"),
         ("stimme voll und ganz zu", "completely agree"))
VERY = (("überhaupt nicht", "not at all"), ("sehr", "very"))
YESNO = {0: ("nein", "no"), 1: ("ja", "yes")}
OFTEN = {1: ("gar nicht", "not at all"), 2: ("selten", "rarely"),
         3: ("manchmal", "sometimes"), 4: ("oft", "often"),
         5: ("sehr oft", "very often")}

AFFECT = [("happy", "glücklich", "happy"), ("afraid", "ängstlich", "afraid"),
          ("sad", "traurig", "sad"), ("balanced", "ausgeglichen", "balanced"),
          ("exhausted", "erschöpft", "exhausted"),
          ("cheerful", "fröhlich", "cheerful"),
          ("worried", "besorgt", "worried"),
          ("lively", "voller Energie", "lively"),
          ("angry", "wütend", "angry"), ("relaxed", "entspannt", "relaxed")]

# table -> dict(items=[(column, German, English)], scale, anchors, prompt,
#               instrument, n). anchors: (lo, hi) for 1..7 endpoints, or a
#               full {value: (German, English)} map. items=None: no item text.
TABLES = {
    "neubauer_2021_paco_parent_affect": dict(
        items=[(f"parent_{k}", f"...{de}", f"...{en}") for k, de, en in AFFECT],
        scale=range(1, 8), anchors=VERY, n=553,
        prompt=("Ich war heute…", "Today I was…"),
        instrument="PACO daily affect, parent (Neubauer et al. 2021)"),
    "neubauer_2021_paco_child_affect": dict(
        items=[(f"child_{k}", f"...{de}", f"...{en}") for k, de, en in AFFECT],
        scale=range(1, 8), anchors=VERY, n=557,
        prompt=("Mein Kind war heute…", "Today my child was…"),
        instrument="PACO daily affect, target child, parent report "
                   "(Neubauer et al. 2021)"),
    "neubauer_2021_paco_parenting": dict(
        items=[
            ("parenting_fun", "Mein Kind und ich hatten heute Spaß zusammen.",
             "My child and I had fun together today."),
            ("parenting_talked_worries",
             "Ich habe heute mit meinem Kind über seine / ihre Sorgen und "
             "Gedanken gesprochen.",
             "I talked to my child about his / her thoughts and worries "
             "today."),
            ("parenting_assert_difficult",
             "Es fiel mir heute schwer, mich gegen mein Kind durchzusetzen.",
             "I found it hard to assert myself with respect to my child "
             "today."),
            ("parenting_drained_energy",
             "Es hat mich heute viel Energie gekostet, mich um mein Kind zu "
             "kümmern.", "Looking after my child cost me a lot of energy "
             "today."),
            ("parenting_disagreements",
             "Mein Kind und ich hatten heute Unstimmigkeiten.",
             "My child and I had some disagreement today."),
        ], scale=range(1, 8), anchors=AGREE, n=559, prompt=("", ""),
        instrument="PACO daily parenting (Neubauer et al. 2021)"),
    "neubauer_2021_paco_autonomy_support": dict(
        items=[
            ("parenting_child_decide",
             "Ich habe meinem Kind heute soweit es ging erlaubt selbst zu "
             "entscheiden, was er / sie machen soll.",
             "As far as possible, I let my child decide today what he / she "
             "wanted to do."),
            ("parenting_child_liked",
             "Mein Kind konnte heute soweit es ging die Dinge machen, die er "
             "/ sie gerne machen wollte.",
             "As far as possible, my child was able to do what he or she "
             "liked today."),
            ("parenting_told_what_to_do",
             "Ich habe meinem Kind heute mehrfach gesagt, was er / sie tun "
             "soll.", "I told my child several times today what he or she "
             "was supposed to do."),
            ("parenting_explained_why",
             "Ich habe meinem Kind heute erklärt, warum er / sie bestimmte "
             "Dinge machen soll.", "I explained to my child today why he or "
             "she should do certain things."),
            ("parenting_explained_why_not",
             "Ich habe meinem Kind heute erklärt, warum er / sie bestimmte "
             "Dinge nicht machen darf.", "I explained to my child today why "
             "he or she should not do certain things."),
        ], scale=range(1, 8), anchors=AGREE, n=559, prompt=("", ""),
        instrument="PACO daily autonomy-supportive parenting "
                   "(Neubauer et al. 2021)"),
    "neubauer_2021_paco_bmpn": dict(
        items=None, n=554, scale=range(1, 8),
        columns=["contact_with_people", "excluded_ostracized", "failure",
                 "own_way", "completed_difficult_project", "true_self",
                 "connected", "mastered_challenges", "intimacy", "pressure",
                 "told_what_to_do", "unappreciated",
                 "disagreements_conflicts", "even_hard_things",
                 "against_own_will", "did_stupid", "struggled",
                 "did_interesting"]),
    "neubauer_2021_paco_worry": dict(
        items=[
            ("worry_many_things", "Heute habe ich mir über viele Dinge "
             "Sorgen gemacht.", "Today, I was worried about a lot of things."),
            ("worry_bothered", "Heute haben mich meine Sorgen sehr gestört.",
             "Today, my worries really bothered me."),
            ("worry_might_happen", "Heute habe ich mir Sorgen über Dinge "
             "gemacht, die vielleicht passieren werden.",
             "Today, I worried about things that might happen."),
            ("worry_cant_get_out_head", "Heute habe ich meine Sorgen nicht "
             "mehr aus dem Kopf bekommen.",
             "Today, I couldn’t get my worries out of my head."),
            ("worry_wrapped_up", "Heute war ich viel mit meinen Sorgen "
             "beschäftigt.", "Today, I was wrapped up in my worries."),
        ], scale=range(1, 8), anchors=AGREE, n=553,
        prompt=("Bitte beantworten Sie noch folgende Fragen zu Ihrem heutigen "
                "Tag. Bitte berücksichtigen Sie dabei alle Themen, über die "
                "Sie sich heute eventuell Sorgen gemacht haben.",
                "Please also respond to the following questions regarding "
                "today. Please consider all the aspects you might have "
                "worried about."),
        instrument="Ambulatory Worry Scale, five items (PACO daily)"),
    "neubauer_2021_paco_mindfulness": dict(
        items=[
            ("mindfulness_open_to_happening", "Ich habe mich heute jeweils "
             "auf das eingelassen, was gerade geschah.",
             "I opened myself up today to what was happening.", AGREE),
            ("mindfulness_inappropriate", "Ich habe heute mehrfach gedacht, "
             "dass das, was ich denke, fühle oder mache, etwas unpassend "
             "war.", "Several times today I felt that what I was thinking, "
             "feeling or doing was slightly off.", VERY),
            ("mindfulness_present_moment", "Ich habe meine Aufmerksamkeit "
             "heute auf den jeweils aktuellen Moment gerichtet.",
             "I focused my attention on the present moment today.", VERY),
            ("mindfulness_could_act_better", "Ich habe heute manchmal "
             "gedacht, dass ich mich in bestimmten Momenten besser hätte "
             "verhalten können.", "I sometimes thought today that I could "
             "have acted more appropriately at a certain time.", VERY),
        ], scale=range(1, 8), anchors=None, n=551,
        prompt=("Bitte beantworten sie kurz folgende Fragen zum Umgang mit "
                "Ihren Gedanken und Gefühlen heute. Wie sind Sie heute mit "
                "Ihren Gedanken und Gefühlen umgegangen?",
                "Please briefly respond to the following aspects regarding "
                "your feelings and thoughts today. How did you deal with "
                "your feelings and thoughts?"),
        instrument="Multidimensional State Mindfulness Questionnaire, four "
                   "items (Blanke & Brose 2017; PACO daily)"),
    "neubauer_2021_paco_stressors": dict(
        items=[
            ("stressor_argument", "Hatten Sie heute eine Auseinandersetzung "
             "oder eine Unstimmigkeit mit jemandem?",
             "Did you experience a conflict or disagreement with someone "
             "today?"),
            ("stressor_friend_relative", "Hat sich bei einem Freund oder "
             "Verwandten etwas Negatives ereignet, das Sie aufgewühlt oder "
             "bewegt hat?", "Did a family member or friend experience "
             "something negative that upset or irritated you?"),
            ("stressor_health", "Hat sich bei Ihnen heute im Bereich "
             "Gesundheit etwas Negatives ereignet, das Sie aufgewühlt oder "
             "bewegt hat?", "Did something negative happen to you today "
             "regarding health that upset or irritated you?"),
            ("stressor_work", "Hat sich bei der Arbeit etwas Negatives "
             "ereignet, das Sie aufgewühlt oder bewegt hat?",
             "Did something happen at work today that upset or irritated "
             "you?"),
            ("stressor_household", "Hat sich in Ihrem Haushalt etwas "
             "Negatives ereignet, das Sie aufgewühlt oder bewegt hat?",
             "Did something negative happen in your household that upset or "
             "irritated you?"),
            ("stressor_leisure", "Hat sich in Ihrer Freizeit etwas Negatives "
             "ereignet, das Sie aufgewühlt oder bewegt hat?",
             "Did something negative happen in your leisure time that upset "
             "or irritated you?"),
            ("stressor_financial", "Gab es in finanzieller Hinsicht etwas, "
             "das für Sie wichtig war (z.B. finanzielle Engpässe)?",
             "Was there something important with respect to finances, e.g. "
             "shortage of money?"),
            ("stressor_other", "Hat sich etwas Weiteres ereignet, das die "
             "meisten Leute als irritierend oder aufwühlend empfinden "
             "würden?", "Did something else happen that most people would "
             "consider to be irritating or upsetting?"),
        ], scale=range(0, 2), anchors=YESNO, n=555,
        prompt=("Bei den folgenden Fragen geht es um Ereignisse, die heute "
                "geschehen sein könnten. Uns interessieren Ereignisse, die "
                "von Personen als irritierend oder aufwühlend empfunden "
                "werden.", "The following paragraph concerns incidents that "
                "might have happened today. We are interested in incidents "
                "that might be experienced as being upsetting or irritating "
                "/ bewildering."),
        instrument="Daily stressors after the Daily Inventory of Stressful "
                   "Experiences (PACO daily)"),
    "neubauer_2021_paco_corona_info": dict(
        items=[
            ("corona_info_update", "Wie oft haben Sie sich heute über den "
             "aktuellen Stand der Corona-Pandemie informiert (z.B. durch "
             "Zeitung, Tagesschau, Podcasts, Push-Nachrichten, "
             "Onlinenachrichten)?", "How often did you update yourself about "
             "the corona pandemic today (e.g., by reading newspapers, "
             "watching the news, push notifications, online news)?"),
            ("corona_talk_friends_family", "Wie oft haben Sie sich heute mit "
             "Freunden oder Familie über die Corona-Pandemie ausgetauscht?",
             "How often did you talk /exchange information viewpoints to "
             "friends or family about the corona pandemic today?"),
            ("corona_social_media_check", "Wie oft haben Sie heute Posts "
             "(Bilder, Videos), Artikel oder Kommentare zur Corona-Pandemie "
             "in sozialen Medien angeschaut?", "How often did you check up "
             "on posts, articles, images, comments regarding the corona "
             "pandemic on social media today?"),
            ("corona_social_media_create", "Wie oft haben Sie heute Posts "
             "(Bilder, Videos), Artikel oder Kommentare zur Corona-Pandemie "
             "in sozialen Medien selbst verfasst oder geteilt?",
             "How often did you create or share posts, images or comments "
             "about the corona pandemic on social media today?"),
        ], scale=range(1, 6), anchors=OFTEN, n=552,
        prompt=("In den folgenden Fragen möchten wir mehr darüber erfahren, "
                "wie die Corona-Pandemie Ihren heutigen Tag beeinflusst hat.",
                "In the following, we would like to find out more about how "
                "the corona pandemic influenced your day today."),
        instrument="PACO daily corona information seeking "
                   "(Neubauer et al. 2021)"),
}
GENDER = {1: "female", 2: "male", 3: "diverse"}     # 4 = prefer not to say


def fetch(filename):
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


def columns(spec):
    return spec.get("columns") or [it[0] for it in spec["items"]]


def option(spec, item, v):
    anchors = item[3] if len(item) > 3 else spec["anchors"]
    if isinstance(anchors, dict):
        return anchors[v]
    lo, hi = anchors
    scale = spec["scale"]
    return lo if v == scale[0] else hi if v == scale[-1] else ("", "")


def write_items(table, spec):
    rows = []
    for item in spec["items"]:
        col, de, en = item[:3]
        for v in spec["scale"]:
            opt = option(spec, item, v)
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


def covariates():
    s = pd.read_csv(fetch(STATIC_FILE), encoding="latin-1", low_memory=False)
    assert (s["QUESTNNR"] == "Baseline").all() and s["SERIAL"].is_unique
    assert s["SD01"].dropna().isin([1, 2, 3, 4]).all()
    return pd.DataFrame({"id": s["SERIAL"].astype(str),
                         "cov_gender": s["SD01"].map(GENDER),
                         "cov_age": s["SD02_01"]})


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    os.makedirs(ITEMDIR, exist_ok=True)
    df = pd.read_csv(fetch(TS_FILE), sep="\t")
    assert len(df) == 7747 and df["id"].nunique() == 562, df.shape
    assert not df.duplicated(["id", "day"]).any()
    assert df["day"].between(1, 21).all()
    df["wave"] = df["day"].astype(int)

    # stamped "Z" but German local time (see coding notes)
    local = pd.to_datetime(df["start_time"].str.rstrip("Z"))
    assert not local.dt.hour.between(6, 18).any()
    df["date"] = (local.dt.tz_localize("Europe/Berlin", ambiguous="raise",
                                       nonexistent="raise")
                  .dt.tz_convert("UTC").astype("int64") // 10**9)

    cov = covariates()
    df = df.merge(cov, on="id", how="left", validate="many_to_one")
    assert df.drop_duplicates("id")["cov_age"].isna().sum() == 1
    covs = ["cov_gender", "cov_age"]

    for table, spec in TABLES.items():
        cols = columns(spec)
        long = df.melt(id_vars=["id", "wave", "date"] + covs, value_vars=cols,
                       var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"])
        assert (long["resp"] % 1 == 0).all()
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp", "wave", "date"] + covs]
        long = long.sort_values(["id", "wave", "item"]).reset_index(drop=True)

        scale = spec["scale"]
        assert long["resp"].between(scale[0], scale[-1]).all(), table
        assert long["id"].nunique() == spec["n"], (table,
                                                   long["id"].nunique())
        assert not long.duplicated(["id", "item", "wave"]).any()
        bad = [c for c in run_qc(long) if c.status == "fail"]
        assert not bad, (table, [(c.name, c.detail) for c in bad])

        path = os.path.join(OUTDIR, f"{table}.csv")
        long.to_csv(path, index=False)
        print(f"{path}: {long['id'].nunique()} people x "
              f"{long['item'].nunique()} items = {len(long):,} responses")
        if spec["items"]:
            ipath, k = write_items(table, spec)
            print(f"  {ipath}: {k} item text rows")


if __name__ == "__main__":
    main()
