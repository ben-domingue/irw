#!/usr/bin/env python3
"""Item text for szigeti_2022_bpq, szigeti_2022_cesd and szigeti_2022_eri_oc (figshare
10.6084/m9.figshare.20788174). Hungarian administration.

Cheap case: data/szigeti_2022_teacher_burnout.py stems(table) reads the .sav variable labels (Hungarian
stems, leading item number stripped); the item code is the deposit's own column name. The file carries
no value labels on any item, so option_text is blank on every scale point. The labels lost ő/ű to the
file's encoding ("er?sen"); the eleven affected words are restored from context (REPAIR below) and the
repair is recorded in provenance. The MBI table ships no item text (rights register). English in
*_translated is an IRW translation.
"""
from _itemtext_writer_c import load_script, row, write

mod = load_script("szigeti_2022_teacher_burnout")
REPAIR = {"er?sen": "erősen", "id?ben": "időben", "teend?m": "teendőm", "id?m": "időm", "tényez?t": "tényezőt",
          "rosszkedvemt?l": "rosszkedvemtől", "meger?ltet?": "megerőltető", "jöv?t": "jövőt", "id?szakaim": "időszakaim",
          "Az id? szorítása": "Az idő szorítása", "Egy id? óta": "Egy idő óta", "gondjaim vannak. ?": "gondjaim vannak."}
RANGES = {"szigeti_2022_bpq": range(0, 5), "szigeti_2022_cesd": range(0, 4), "szigeti_2022_eri_oc": range(0, 4)}
INSTR = {"szigeti_2022_bpq": "Kiégés Folyamat Kérdőív (Burnout Process Questionnaire)",
         "szigeti_2022_cesd": "CES-D (Center for Epidemiologic Studies Depression Scale), Hungarian",
         "szigeti_2022_eri_oc": "Effort-Reward Imbalance questionnaire, overcommitment scale, Hungarian"}
EN = {
    "kfk1": "Lately I strive hard to prove myself every day.",
    "kfk2": "I want to give my best.",
    "kfk3": "To feel successful, I have to finish everything I set out to do.",
    "kfk4": "People close to me say I sacrifice too much for my work.",
    "kfk5": "My work does not let me rest easily; it is still on my mind after I get home.",
    "kfk6": "Lately I take on too much work.",
    "kfk7": "I often forget to eat or drink on time while working.",
    "kfk8": "I have so much to do that I have no time to unwind.",
    "kfk9": "Because of my work I often give up things that would otherwise make me happy.",
    "kfk10": "I find it hard to keep a balance between work and my private life.",
    "kfk11": "The values that used to matter to me are slipping further down my priorities lately.",
    "kfk12": "I increasingly feel that nowadays it is normal to overload oneself.",
    "kfk13": "To be able to do my job at all, I am starting to push every other factor into the background (e.g. good relations with colleagues).",
    "kfk14": "My family / friends / colleagues say I have problems.",
    "kfk15": "I get into conflicts at my workplace more and more often.",
    "kfk16": "I am hurt at my workplace more and more often.",
    "kfk17": "I get into conflicts in my private life more and more often.",
    "kfk18": "I hold back when tasks are being assigned.",
    "kfk19": "I try to get my work done as quickly as possible.",
    "kfk20": "I only do even my most essential tasks half-heartedly now.",
    "kfk21": "I am emotionally exhausted.",
    "kfk22": "I can no longer really enjoy anything; my joy is only superficial.",
    "kfk23": "I feel I have become jaded.",
    "kfk24": "Sometimes I do my work like a robot, as if I were not really there.",
    "kfk25": "For some time I have been growing more and more insensitive.",
    "kfk26": "I often see my situation as hopeless.",
    "ces1": "I was bothered by things that usually don't bother me.",
    "ces2": "I did not feel like eating; my appetite was poor.",
    "ces3": "I felt that I could not shake off the blues even with help from my family or friends.",
    "ces4": "I felt that I was just as good as other people.",
    "ces5": "I had trouble keeping my mind on what I was doing.",
    "ces6": "I felt depressed.",
    "ces7": "I felt that everything I did was an effort.",
    "ces8": "I felt hopeful about the future.",
    "ces9": "I thought my life had been a failure.",
    "ces10": "I felt fearful.",
    "ces11": "My sleep was restless.",
    "ces12": "I was happy.",
    "ces13": "I talked less than usual.",
    "ces14": "I felt lonely.",
    "ces15": "People were unfriendly.",
    "ces16": "I enjoyed life.",
    "ces17": "I had crying spells.",
    "ces18": "I felt sad.",
    "ces19": "I felt that people disliked me.",
    "ces20": "I could not get going.",
    "eri1": "I often feel overloaded because of time pressure.",
    "eri2": "As soon as I wake up I start thinking about my problems at work.",
    "eri3": "When I get home, I can easily relax and switch off from work.",
    "eri4": "People close to me say I sacrifice too much for my work.",
    "eri5": "Work rarely lets me go; it is still on my mind when I go to bed.",
    "eri6": "If I postpone something that I was supposed to do today, I will have trouble sleeping at night.",
}


def main():
    for table, valid in RANGES.items():
        rows = []
        for code, stem in mod.stems(table):
            for k, v in REPAIR.items():
                stem = stem.replace(k, v)
            assert "?" not in stem, (code, stem)
            for r in valid:
                rows.append(row(table, f"{table}_1", code, INSTR[table], "Hungarian", r, stem, item_text_tr=EN[code]))
        write(table, rows)


if __name__ == "__main__":
    main()
