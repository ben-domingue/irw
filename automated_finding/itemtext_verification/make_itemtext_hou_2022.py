#!/usr/bin/env python3
"""Item text for hou_2022_perspective_taking / _trait_anger / _online_disinhibition / _cyberbullying
(Dataverse 10.7910/DVN/K643HB). Chinese administration.

Cheap case: the .sav variable labels are the Chinese stems ("2.我的脾气暴躁。)") and the value labels the
anchors; data/hou_2022_dark_triad_cyberbullying.py labels(block) exposes both, so the item code is the
deposit's own column name. The variable label of item 1 in each block holds the block instruction and is
truncated before the stem (SPSS label limit), so item 1 ships with instructions and a blank item_text.
PT_1's label ("１.在做决定前，") is cut mid-sentence and is also left blank. The leading item numbers and
stray ")" are stripped from the stems. English in *_translated is an IRW translation. The DT and MD
tables ship no item text (labels truncated at ~10 characters).
"""
import re

from _itemtext_writer_c import load_script, row, write

mod = load_script("hou_2022_dark_triad_cyberbullying")
META = {  # table -> (block, instrument, option translations)
    "hou_2022_perspective_taking": ("PT", "Interpersonal Reactivity Index, perspective-taking subscale (Chinese)",
                                    {"不恰当": "Does not fit me", "比较不恰当": "Does not fit me very well", "一般": "Neutral",
                                     "比较恰当": "Fits me fairly well", "很恰当": "Fits me very well"}),
    "hou_2022_trait_anger": ("TA", "Trait anger scale (Chinese)",
                             {"几乎不": "Almost never", "偶尔": "Sometimes", "经常": "Often", "总是": "Always"}),
    "hou_2022_online_disinhibition": ("OD", "Online disinhibition scale (Chinese)",
                                      {"不同意": "Disagree", "比较不同意": "Somewhat disagree", "比较同意": "Somewhat agree", "同意": "Agree"}),
    "hou_2022_cyberbullying": ("CB", "Cyberbullying perpetration scale (Chinese)",
                               {"从不": "Never", "很少": "Rarely", "偶尔": "Occasionally", "经常": "Often", "总是": "Always"}),
}
EN = {
    "PT_2": "I sometimes imagine how things look from my friends' point of view in order to understand them better.",
    "PT_3": "I believe that every question has two sides, so I try to look at it from these different points of view.",
    "PT_4": "When I am angry at someone, I usually try to think about their position for a while.",
    "PT_5": "Before criticizing someone, I try to imagine how I would feel if I were in their situation.",
    "TA_2": "I have a fiery temper.", "TA_3": "I am a quick-tempered person.",
    "TA_4": "I get angry when others' mistakes slow me down.",
    "TA_5": "I feel annoyed when I do good work and get no recognition.", "TA_6": "I get angry easily.",
    "TA_7": "When I feel angry, I say nasty things.", "TA_8": "I get furious when I am criticized in front of others.",
    "TA_9": "When I get frustrated, I feel like hitting someone.",
    "TA_10": "I get extremely angry when I do good work but get a poor evaluation.",
    "OD_2": "Communication on the internet is anonymous, so it is easier to express my true feelings or thoughts.",
    "OD_3": "Because I cannot see the other person's face, it is easier to express online the thoughts that are hard to express in real life.",
    "OD_4": "Because I can choose when to reply, communicating online is easier.",
    "OD_5": "When I read other people's email or message replies online, an image of the other person comes to mind.",
    "OD_6": "I feel that I am a completely different person online.",
    "OD_7": "I feel that online I can talk as an equal with people who are older or of higher status than me.",
    "OD_8": "I don't mind posting insulting remarks online, because it is all anonymous.",
    "OD_9": "It is easy to post insulting remarks online, because there are no consequences.",
    "OD_10": "There are no rules online, so I can do anything I want.",
    "OD_11": "Posting insulting remarks online is not an act of violence.",
    "CB_2": "Online, when others disagree with me, I argue with them.",
    "CB_3": "Online, I have used insulting language.",
    "CB_4": "Used the internet as a tool to slander others.",
    "CB_5": "On forums or Weibo, I post aggressive comments.",
    "CB_6": "Online, I send other people infected files or programs.",
    "CB_7": "Online, I send other people pornographic pictures or videos.",
    "CB_8": "Online, I ask other people to discuss pornographic topics with me.",
    "CB_9": "Online, in chat rooms (QQ), Weibo or other forums, spread rumours.",
    "CB_10": "In online groups (QQ friends, games, etc.), isolate or block other people.",
    "CB_11": "Used someone else's username and password without permission.",
    "CB_12": "Online, hid my identity information and misled others.",
}
INSTR_EN = {
    "PT": "", "TA": "Please read the following sentences carefully and choose, between \"almost never\" and \"always\", the option that matches what you usually think and do; there are no right or wrong answers.",
    "OD": "Please read the following sentences carefully and choose, between \"disagree\" and \"agree\", the option that matches what you usually think and do; there are no right or wrong answers.",
    "CB": "Please read the following sentences carefully and judge whether each description matches what you usually think.",
}


def clean(label: str) -> str:
    return re.sub(r"^[0-9０-９]+\.\s*", "", label).rstrip(")").strip()


def main():
    for table, (block, instrument, opt_en) in META.items():
        rows = []
        items = mod.labels(block)
        first_label = items[0][1]
        instr = "" if block == "PT" else clean(first_label).rstrip("，,")
        for code, label, vl in items:
            stem = "" if code.endswith("_1") else clean(label)
            if stem:
                assert code in EN, code
            for r in sorted(vl):
                rows.append(row(table, f"{table}_1", code, instrument, "Chinese", int(r), stem,
                                option_text=vl[r], instructions=instr, item_text_tr=EN.get(code, ""),
                                option_text_tr=opt_en[vl[r]], instructions_tr=INSTR_EN[block] if instr else ""))
        write(table, rows)


if __name__ == "__main__":
    main()
