#!/usr/bin/env python3
"""Item text for burghartswieser_2021_* (10.1371/journal.pone.0259445, PLOS SI
S2 Text = the full SoSci Survey questionnaire, journal.pone.0259445.s002,
CC BY 4.0).

Source, level 1: the questionnaire PDF is SoSci's own export, so beneath every
question it prints the variable list -- each variable code (GG02_01, PE03_04,
...) beside the item wording, and each code's value labels ("1 = nie", "6 =
stimmt voll und ganz"). The response tables keep those codes lower-cased
(data/burghartswieser_2021_refugee_crisis.py), so code and text are tied at
the source: no positional step. This script parses that variable list from
`pdftotext -layout` output (wrapped lines joined by one space) and asserts
every shipped stem and anchor appears in the PDF text.

SHIPPED (study-authored or the study's own adaptation; CC BY 4.0):
  refugee_attitudes (GG02 normative + GG01 factual beliefs: two sections, as
  on the two questionnaire pages), refugee_threat (PG02; "adapted from
  Gollwitzer and Keller" per the article -- the German wording is the study's),
  political_info (PE03), participation (PE04), refugee_news (NK01; "adapted
  from Baumgartner and Morris"), opinion_exposure (PG01), facebook_exposure
  (NK02).
Options: the agreement blocks label only their endpoints (GG02/GG01/PG02,
  1 and 6); intermediate levels ship as rows with blank option_text. The
  frequency blocks label every level.
Language: German. English in *_translated was written by IRW
  (translation_source = machine_translation); the study published no English
  version of the items (the article quotes a few in English, paraphrased).

HELD, written to HOLD_DIR, not to itemtext_output (see the register):
  authoritarianism (KSA-3, Beierlein et al. 2014, GESIS) and sdo (German SDO
  items) -- named third-party instruments, no grant located. German only, no
  translation. pvq is not built at all: the register blocks the Schwartz
  instruments (SCHWARTZ family).

Run: RESP_DIR=<dir with staged response CSVs> [RAW=<s002 pdf>] \
     [HOLD_DIR=<dir>] python3 make_itemtext_burghartswieser_2021.py
"""
import csv
import os
import re
import subprocess
import tempfile
from pathlib import Path

import pandas as pd
import requests

HERE = Path(__file__).resolve().parent.parent
OUT_DIR = HERE / "itemtext_output"
RESP_DIR = Path(os.environ.get("RESP_DIR", HERE / "irw_output"))
HOLD_DIR = Path(os.environ.get("HOLD_DIR", "/home/ben/Dropbox/projects/irw/data/itemtext"))
RAW = os.environ.get("RAW")
URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0259445.s002"
INSTRUMENT = "Meinungen zur Flüchtlingskrise (Burghartswieser & Rothmund 2021, SoSci Survey questionnaire, Germany 2016)"
COLS = ["table", "section_id", "item", "instrument", "language", "instructions", "section_prompt",
        "item_text", "correct_response", "option_text", "resp", "instructions_translated",
        "section_prompt_translated", "item_text_translated", "option_text_translated"]

# Question text above each block, verbatim from the PDF (question number dropped).
PROMPT = {
    "GG02": "Politikerinnen und Politiker fordern unterschiedliche Maßnahmen, um die aktuelle Flüchtlingskrise zu bewältigen. Wir haben hier einige zusammengetragen. Wie sehr stimmen Sie den einzelnen Forderungen zu? Bitte geben Sie bei jeder Aussage an wie sehr Sie dieser persönlich zustimmen. Geben Sie Ihre Zustimmung an von „stimme überhaupt nicht zu“ bis „stimme voll und ganz zu“ ein.",
    "GG01": "Nun geht es um Fakten und Gerüchte im Zusammenhang mit der Flüchtlingskrise. Im folgenden haben wir einige Aussagen und Behauptungen zusammengetragen. Inwiefern glauben Sie, dass die einzelnen Aussagen wahr sind? Bitte geben Sie bei jeder Aussage an wie sehr Sie glauben, dass diese wahr ist. Schätzen Sie die Wahrheit von „stimmt überhaupt nicht“ bis „stimmt voll und ganz“ ein.",
    "PG02": "Jeder macht sich andere Gedanken zur Flüchtlingskrise und deren Einfluss auf die Gesellschaft. Wie ist das bei Ihnen? Bitte geben Sie bei jeder Aussage an wie sehr Sie zustimmen von „stimme gar nicht zu“ bis „stimme voll und ganz zu“ .",
    "PE03": "Wie häufig informieren Sie sich allgemein über politische Themen? Bitte kreuzen Sie immer die Antwort an, die am ehesten auf Sie zutrifft. Wie häufig haben Sie (sich) in den letzten 12 Monaten...",
    "PE04": "Menschen unterscheiden sich darin, wie häufig und in welcher Form Sie am politischen Leben teilnehmen. Bei den folgenden Fragen geht es darum, in welcher Art und Weise Sie politisch aktiv sind. Bitte kreuzen Sie immer die Antwort an, die am ehesten auf Sie zutrifft. Wie häufig haben Sie (sich) in den letzten 12 Monaten...",
    "NK01": "Wie häufig informieren Sie sich über die Flüchtlingskrise...",
    "PG01": "Wie häufig hören/lesen Sie Aussagen von Menschen, die ...",
    "NK02": "Wie oft lesen Sie auf Facebook ...",
    "SO01": "Wie beurteilen Sie die folgenden Aussagen?",
    "GP01": "Im Folgenden finden Sie eine Reihe von Aussagen darüber, in welcher Beziehung gesellschaftliche Gruppen zueinander stehen sollten. Gesellschaftliche Gruppen können dabei z.B. ethnische Gruppen, politische Gruppen, religiöse Gruppen, Berufsgruppen oder auch die beiden Geschlechter sein. Bitte geben Sie an, wie stark Sie persönlich den Aussagen zustimmen.",
    "GP02": "Bitte geben Sie an, wie stark Sie persönlich den Aussagen zustimmen.",
}
PROMPT_EN = {
    "GG02": "Politicians are calling for various measures to deal with the current refugee crisis. We have collected some of them here. How strongly do you agree with each of the demands? For each statement, please indicate how strongly you personally agree with it. Give your agreement from \"strongly disagree\" to \"completely agree\".",
    "GG01": "Now it is about facts and rumours in connection with the refugee crisis. Below we have collected some statements and claims. To what extent do you believe that each statement is true? For each statement, please indicate how strongly you believe it is true. Rate its truth from \"not at all true\" to \"completely true\".",
    "PG02": "Everyone has different thoughts about the refugee crisis and its influence on society. How is it for you? For each statement, please indicate how strongly you agree, from \"do not agree at all\" to \"completely agree\".",
    "PE03": "How often do you inform yourself about political topics in general? Please always tick the answer that applies to you best. How often in the last 12 months have you...",
    "PE04": "People differ in how often and in what form they take part in political life. The following questions are about the ways in which you are politically active. Please always tick the answer that applies to you best. How often in the last 12 months have you...",
    "NK01": "How often do you inform yourself about the refugee crisis...",
    "PG01": "How often do you hear/read statements from people who ...",
    "NK02": "How often do you read on Facebook ...",
}

ITEM_EN = {
    "GG02_01": "Refugees who have committed crimes should have no chance of asylum and should be deported immediately.",
    "GG02_02": "Asylum seekers without proof of nationality should be rejected in a fast-track procedure.",
    "GG02_03": "The number of refugees admitted to Germany should be limited.",
    "GG02_04": "Refugees should receive unrestricted access to health care and the social security systems.",
    "GG02_05": "Refugees should receive immediate access to work and education.",
    "GG02_06": "No one may be sent back to a country in which their life and limb are in danger.",
    "GG02_07": "It should be possible to send asylum seekers with poor prospects of being allowed to stay back to their home countries more quickly.",
    "GG02_08": "\"Safe\" escape routes to Europe should be set up for refugees.",
    "GG01_01": "Properties next to refugee shelters lose a great deal of value.",
    "GG01_02": "The number of xenophobic attacks on refugees rose sharply in the last year.",
    "GG01_03": "Refugees frequently riot and \"trash\" their surroundings.",
    "GG01_04": "The refugee routes are used by terrorists to enter Germany illegally.",
    "GG01_05": "Refugees take jobs away from locals.",
    "GG01_06": "Crimes by refugees are not prosecuted; the police and the state deliberately look away.",
    "GG01_07": "Refugees get more money than Hartz IV (welfare) recipients.",
    "GG01_08": "At least 30 percent of the supposed Syrians who come to Germany as refugees are not Syrians at all.",
    "PG02_01": "I am worried about how our society is dealing with the refugee crisis.",
    "PG02_02": "I fear negative consequences for our society as a result of the refugee crisis.",
    "PG02_04": "The more I think about the refugee crisis, the more worried I am about the future of our society.",
    "PG02_05": "I think that the cohesion of our society is threatened by the refugee crisis.",
    "PE03_01": "... informed yourself about foreign affairs in Europe or the world?",
    "PE03_02": "... informed yourself about domestic politics at the federal or state level?",
    "PE03_03": "... informed yourself about local politics in your district, city or municipality?",
    "PE03_04": "... had conversations about political topics with family or acquaintances?",
    "PE03_05": "... specifically searched for information on particular political topics (e.g. on the internet, in newspapers or magazines etc.)?",
    "PE04_01": "... deliberately bought or deliberately not bought a product for social, political or ethical reasons? (e.g. fair-trade goods etc.)",
    "PE04_02": "... signed a petition on a political issue?",
    "PE04_03": "... taken part in an authorised political event (e.g. rally, demonstration etc.)?",
    "PE04_04": "... taken part in spreading political information (e.g. flyers, posters, documents, files, internet links etc.)",
    "PE04_05": "... worked actively in a social or political organisation or movement (e.g. party, citizens' initiative, foundation, trade union, church, non-governmental organisation, association etc.)?",
    "NK01_01": "... on television?",
    "NK01_02": "... in newspapers?",
    "NK01_03": "... on the internet?",
    "NK01_04": "... in conversations with friends and acquaintances?",
    "PG01_01": "... speak out strongly against taking in refugees?",
    "PG01_02": "... are undecided about taking in refugees?",
    "PG01_03": "... speak out strongly in favour of taking in refugees?",
    "NK02_01": "... news about the refugee crisis?",
    "NK02_02": "... personal comments about the refugee crisis?",
    "NK02_03": "... personal comments by people who speak out in favour of taking in refugees?",
    "NK02_04": "... personal comments by people who speak out against taking in refugees?",
    "NK02_05": "... personal comments by people in which others are insulted?",
}
OPT_EN = {
    "stimme überhaupt nicht zu": "strongly disagree",
    "stimme voll und ganz zu": "completely agree",
    "stimmt überhaupt nicht": "not at all true",
    "stimmt voll und ganz": "completely true",
    "stimme gar nicht zu": "do not agree at all",
    "nie": "never",
    "alle paar Monate": "every few months",
    "alle paar Wochen": "every few weeks",
    "wöchentl.": "weekly",
    "mehrmals in der Woche": "several times a week",
    "täglich": "daily",
    "selten": "rarely",
    "manchmal": "sometimes",
    "oft": "often",
    "sehr oft": "very often",
}

SHIP = {
    "refugee_attitudes": ["GG02", "GG01"],
    "refugee_threat": ["PG02"],
    "political_info": ["PE03"],
    "participation": ["PE04"],
    "refugee_news": ["NK01"],
    "opinion_exposure": ["PG01"],
    "facebook_exposure": ["NK02"],
}
HOLD = {"authoritarianism": ["SO01"], "sdo": ["GP01", "GP02"]}
HOLD_INSTRUMENT = {
    "authoritarianism": "Kurzskala Autoritarismus (KSA-3; Beierlein, Asbrock, Kauff & Schmidt 2014), as administered by Burghartswieser & Rothmund 2021",
    "sdo": "Social dominance orientation items (German SDO), as administered by Burghartswieser & Rothmund 2021",
}


def pdf_text():
    src = RAW
    tmp = None
    if not src:
        r = requests.get(URL, headers={"User-Agent": "IRW-Finder/1.0"}, timeout=180)
        r.raise_for_status()
        tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        tmp.write(r.content)
        tmp.close()
        src = tmp.name
    out = subprocess.run(["pdftotext", "-layout", src, "-"], capture_output=True, text=True).stdout
    if tmp:
        os.remove(tmp.name)
    return out


def parse(text):
    """SoSci variable list: '  CODE wording' with wrapped continuation lines,
    then '  n = label' value-label lines."""
    items, opts, cur = {}, {}, None
    for ln in text.splitlines():
        m = re.match(r"^\s{20,}([A-Z]{2}\d{2}_\d{2}) (.*)$", ln)
        o = re.match(r"^\s{20,}(-?\d+) = (.*)$", ln)
        if m:
            cur = m.group(1)
            items[cur] = m.group(2).strip()
        elif o and cur:
            opts.setdefault(cur.split("_")[0], {})[int(o.group(1))] = o.group(2).strip()
        elif cur and re.match(r"^\s{30,}\S", ln) and "Seite" not in ln and not opts.get(cur.split("_")[0]):
            items[cur] += " " + ln.strip()
        elif ln.strip() and not re.match(r"^\s{20,}", ln):
            cur = None
    return items, opts


def build(table, blocks, items, opts, flat, translate):
    resp = pd.read_csv(RESP_DIR / f"{table}.csv")
    levels = sorted(resp["resp"].unique())
    multi = len(blocks) > 1
    rows = []
    for k, blk in enumerate(blocks, start=1):
        assert re.sub(r"\s+", " ", PROMPT[blk]) in flat, (blk, "prompt not in PDF")
        codes = [c for c in items if c.split("_")[0] == blk and c.lower() in set(resp["item"])]
        for c in codes:
            assert re.sub(r"\s+", "", items[c]) in re.sub(r"\s+", "", flat), c
            for v in levels:
                lab = opts[blk].get(int(v), "")
                row = {"table": table, "section_id": f"{table}_{k if multi else 1}", "item": c.lower(),
                       "instrument": HOLD_INSTRUMENT.get(table.split("2021_")[1], INSTRUMENT),
                       "language": "German",
                       "instructions": "" if multi else PROMPT[blk],
                       "section_prompt": PROMPT[blk] if multi else "",
                       "item_text": items[c], "correct_response": "", "option_text": lab, "resp": int(v)}
                if translate:
                    row.update({"instructions_translated": "" if multi else PROMPT_EN[blk],
                                "section_prompt_translated": PROMPT_EN[blk] if multi else "",
                                "item_text_translated": ITEM_EN[c],
                                "option_text_translated": OPT_EN[lab] if lab else ""})
                rows.append(row)
    assert {r["item"] for r in rows} == set(resp["item"]), table
    assert {r["resp"] for r in rows} == set(resp["resp"]), table
    return rows


def write(rows, path, translate):
    cols = COLS if translate else COLS[:11]
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, quoting=csv.QUOTE_ALL, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def main():
    text = pdf_text()
    flat = re.sub(r"\s+", " ", text)
    items, opts = parse(text)
    for name, blocks in SHIP.items():
        t = f"burghartswieser_2021_{name}"
        rows = build(t, blocks, items, opts, flat, True)
        write(rows, OUT_DIR / f"{t}__items.csv", True)
        print(f"{t}__items.csv: {len(rows)} rows, {len({r['item'] for r in rows})} items")
    for name, blocks in HOLD.items():
        t = f"burghartswieser_2021_{name}"
        rows = build(t, blocks, items, opts, flat, False)
        write(rows, HOLD_DIR / f"{t}__items.csv", False)
        print(f"HELD {t}__items.csv -> {HOLD_DIR}: {len(rows)} rows")


if __name__ == "__main__":
    main()
