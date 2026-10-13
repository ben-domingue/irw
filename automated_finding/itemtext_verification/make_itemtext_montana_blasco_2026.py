#!/usr/bin/env python3
"""Item text for four montana_blasco_2026_* tables (SMARS 2024, figshare 32626206).

Codebook_SMARS_2024 (1).csv ties each variable (P2101 ..) to its Spanish questionnaire
wording (questionnaire_wording_ES) and value labels (native_value_labels), and
data/montana_blasco_2026_smars.py ships the variable names as item, so the tie is by
name. Shipped here: digital skills (P21xx/P22xx), perceived social-media impact (P31xx),
content viewing frequency (P71xx) and digital well-being on TikTok (P81xx), the blocks
the record presents as the study's own. The "A) " option letters of the skills block are
stripped. Codes 6/7 (no sabe / no contesta) were dropped by the response script and get
no option row. English is IRW's (translation_source = irw_generated).
"""
import csv
import re
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent.parent
OUT_DIR = HERE / "itemtext_output"
RESP_DIR = HERE / "irw_output"
CB = HERE / "runs" / "raw" / "10_6084_m9_figshare_32626206_v2" / "Codebook_SMARS_2024 (1).csv"
COLS = ["table", "section_id", "item", "instrument", "language", "instructions", "section_prompt",
        "item_text", "correct_response", "option_text", "resp", "instructions_translated",
        "section_prompt_translated", "item_text_translated", "option_text_translated"]
P = "montana_blasco_2026_"
EN = {
    "P2101": "Install/uninstall basic programs and applications for my needs",
    "P2102": "Browse the Internet and use related services (e.g. email) for everyday tasks",
    "P2103": "Use content management platforms (such as WordPress, Wix, Drupal...) to create multimedia publications",
    "P2104": "Record, edit and upload audiovisual content to digital platforms",
    "P2105": "Share and distribute multimedia content on networks, platforms, mailing lists, etc.",
    "P2106": "Work with other people through digital collaborative tools (e.g. Google Drive or other applications)",
    "P2107": "Configure digital services and use tools to increase privacy and anonymity online",
    "P2108": "Read and/or write computer code (programming knowledge)",
    "P2109": "Repair and/or maintain devices (mobile, computer, etc.)",
    "P2201": "Check the reliability and truthfulness of the information I consume",
    "P2202": "Classify and filter information so that it fits my interests",
    "P2203": "Find and save information to use it when I need it",
    "P2204": "Interact with other people on digital networks and forums with self-control so as not to react impulsively",
    "P2205": "Identify users who behave in an explicitly provocative way (with aggression, violence, etc.)",
    "P2206": "Identify the presence of bots on digital networks and forums",
    "P2207": "Manage different profiles of my digital identity (social media accounts)",
    "P2208": "Adapt my behaviour according to the rules of each platform",
    "P2209": "Identify my needs and find tools and platforms that meet them",
    "P3101": "Psychological well-being",
    "P3102": "The ability to argue and debate",
    "P3103": "Socialising with peers (that is, interaction with other young people)",
    "P3104": "Communication with adults close to you",
    "P3105": "The possibility of expressing yourself as you are",
    "P3106": "Group belonging",
    "P3107": "The capacity for collective organisation",
    "P3108": "Acceptance of established social norms (rules that the people of a community must follow for better coexistence)",
    "P3109": "Decision-making and social autonomy (facing and making decisions on your own initiative)",
    "P7101": "Comedy (parodies, jokes, etc.)",
    "P7102": "Dance, lip sync and other trends with viral songs",
    "P7103": "News about influencers, streamers and other celebrities (videos they post, clips of their live streams, podcasts or interviews, etc.)",
    "P7104": "Music (concerts, artists' music videos, etc.)",
    "P7105": "Books, films, series and reality shows",
    "P7106": "Video games",
    "P7107": "Travel and tourism",
    "P7108": "Leisure and culture (theatres, festivals, restaurants, etc.)",
    "P7109": "Professional sport (matches, exhibitions, etc.)",
    "P7110": "Beauty (make-up, skin care, etc.)",
    "P7111": "Fashion (hauls, new trends, etc.)",
    "P7112": "Food (cooking recipes, tips, etc.)",
    "P7113": "Fitness (exercise routines, recommendations, etc.)",
    "P7114": "Medicine (information about illnesses, medical advice, etc.)",
    "P7115": "Psychology (information about mental health, psychological advice, etc.)",
    "P7116": "Other well-being routines (meditation, study, tidiness, etc.)",
    "P7117": "Tutorials (crafts, using apps and programs, etc.)",
    "P7118": "Current news (politics, society, sport, economy, etc.)",
    "P7119": "General knowledge (general culture, languages, etc.)",
    "P7120": "Other content you consider important: ____________ (specify which)",
    "P8101": "I feel emotionally stable when I am on TikTok.",
    "P8102": "I can manage any emotional challenge caused by my TikTok use.",
    "P8103": "I manage well any mood change brought on by my TikTok use.",
    "P8104": "I manage well the emotional harm caused by my TikTok use.",
    "P8105": "I manage well any digital harm I may see on TikTok (for example, cyberbullying).",
    "P8106": "I set limits on my TikTok use.",
    "P8107": "I limit my time on TikTok.",
    "P8108": "I feel good when others connect with me on TikTok.",
    "P8109": "I feel good when someone gets in touch with me during hard times for me.",
    "P8110": "I feel good when someone interacts with me on TikTok.",
    "P8111": "I feel good when other TikTok users show respectful behaviour.",
    "P8112": "I feel good when other TikTok users consider whether their content is appropriate before sharing it.",
    "P8113": "I feel good when the people I know on TikTok are kind to me.",
}
OPT_EN = {
    "skills": {1: "I know how to do it and could teach others", 2: "I know how to do it on my own",
               3: "I would know how to do it with help", 4: "I know what it is but do not know how to do it",
               5: "I do not know what it is / what it means"},
    "impact": {1: "Very positively", 2: "Positively", 3: "Neither negatively nor positively", 4: "Negatively", 5: "Very negatively"},
    "freq": {1: "Always", 2: "Almost always", 3: "Sometimes", 4: "Almost never", 5: "Never"},
    "agree": {1: "Totally agree", 2: "Agree", 3: "Neutral", 4: "Disagree", 5: "Totally disagree"},
}
TABLES = {
    P + "digital_skills": (r"P2[12]\d\d", "SMARS 2024 digital skills self-assessment, 18 items (P2.1 / P2.2 'grado de habilidad')", "skills"),
    P + "sm_impact": (r"P31\d\d", "SMARS 2024 perceived impact of social media on ... (P3.1), 9 items", "impact"),
    P + "content_freq": (r"P71\d\d", "SMARS 2024 frequency of viewing content types on social media (P7.1), 20 items", "freq"),
    P + "tiktok_wellbeing": (r"P81\d\d", "SMARS 2024 Digital Well-being on TikTok Scale (P8.1), 13 items, TikTok users", "agree"),
}


def main() -> None:
    cb = pd.read_csv(CB).set_index("variable")
    for table, (pat, instr, optkey) in TABLES.items():
        resp = pd.read_csv(RESP_DIR / f"{table}.csv")
        items = [v for v in cb.index if re.fullmatch(pat, str(v))]
        assert set(items) == set(resp["item"]), (table, set(items) ^ set(resp["item"]))
        rows = []
        for it in items:
            wording = str(cb.loc[it, "questionnaire_wording_ES"]).split("\n")[0].strip()
            wording = re.sub(r"^[A-I]\)\s*", "", wording)
            vl = dict(re.findall(r"(\d+)=([^;]+)", str(cb.loc[it, "native_value_labels"])))
            vl = {int(k): v.strip() for k, v in vl.items()}
            for r in sorted(resp.loc[resp["item"] == it, "resp"].unique()):
                assert int(r) in vl and int(r) in OPT_EN[optkey], (it, r)
                rows.append({"table": table, "section_id": f"{table}_1", "item": it, "instrument": instr,
                             "language": "Spanish", "instructions": "", "section_prompt": "", "item_text": wording,
                             "correct_response": "", "option_text": vl[int(r)], "resp": int(r),
                             "instructions_translated": "", "section_prompt_translated": "",
                             "item_text_translated": EN[it], "option_text_translated": OPT_EN[optkey][int(r)]})
        with open(OUT_DIR / f"{table}__items.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=COLS, quoting=csv.QUOTE_ALL)
            w.writeheader()
            w.writerows(rows)
        print(table, len(rows), "rows")


if __name__ == "__main__":
    main()
