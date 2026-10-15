#!/usr/bin/env python3
"""Item text for the four li_2026_hsc_* tables (Dataverse 10.7910/DVN/A9NUD7). Chinese administration.

Cheap case: data/li_2026_hsc_collaboration.py stems() reads each item's Chinese stem from the xlsx
column header (question number stripped); the anchors come from the deposited .docx questionnaire,
which lists five options per block (the docx mislabels the fourth option "C" twice; the xlsx codes
them 1-5 in listed order). The implementation block is shipped 1 = 有 (yes) / 0 = 没有 (no), with
不清楚 dropped by the processing script. English in *_translated is an IRW translation.
"""
from _itemtext_writer_c import load_script, row, write

mod = load_script("li_2026_hsc_collaboration")
OPTS = {
    "li_2026_hsc_awareness": ({1: "非常认同", 2: "认同", 3: "一般认同", 4: "不认同", 5: "非常不认同"},
                              {1: "Strongly agree", 2: "Agree", 3: "Somewhat agree", 4: "Disagree", 5: "Strongly disagree"},
                              "协同育人认知度", "Awareness of home-school-community collaborative education"),
    "li_2026_hsc_recognition": ({1: "非常重要", 2: "重要", 3: "一般重要", 4: "不重要", 5: "非常不重要"},
                                {1: "Very important", 2: "Important", 3: "Moderately important", 4: "Unimportant", 5: "Very unimportant"},
                                "协同育人认同度", "Recognition of home-school-community collaborative education"),
    "li_2026_hsc_implementation": ({1: "有", 0: "没有"}, {1: "Yes", 0: "No"},
                                   "协同育人实施度", "Implementation of home-school-community collaborative education"),
    "li_2026_hsc_competence": ({1: "完全能", 2: "能", 3: "基本能", 4: "不能", 5: "完全不能"},
                               {1: "Fully able", 2: "Able", 3: "Basically able", 4: "Unable", 5: "Completely unable"},
                               "协同育人胜任度", "Competence in home-school-community collaborative education"),
}
EN = {
    "AW1": "In home-school-community collaborative education, the school's role is that of organiser.",
    "AW2": "In home-school-community collaborative education, the school's role is that of participant.",
    "AW3": "In home-school-community collaborative education, parents should strengthen their sense of responsibility that the family is the first classroom and parents the first teachers, and should build harmonious family relationships to create a good home environment for their children's healthy growth.",
    "AW4": "In home-school-community collaborative education, the school should provide family-education guidance services and support resources and include them in the school work plan.",
    "AW5": "In home-school-community collaborative education, the school should establish and improve a school family-education guidance committee, a parent school and a parent committee.",
    "AW6": "In home-school-community collaborative education, the community should provide venues for students' social practice and community service, and resources and services for the school's extended courses.",
    "RD1": "In your view, collaboration between teachers and parents in students' education is",
    "RD2": "In your view, collaboration between teachers and the community in students' education is",
    "RD3": "In your view, collaboration among home, school and community in students' education is",
    "RD4": "In your view, the contribution of home-school-community collaboration to the relationships among home, school and community is",
    "ID1": "Does your school have a department that manages home-school-community collaborative education?",
    "ID2": "Has your school established management rules for home-school-community collaborative education?",
    "ID3": "Has your school issued implementation guidelines for home-school-community collaborative education?",
    "ID4": "Does your school have a work plan for home-school-community collaborative education?",
    "ID5": "Does your school carry out its work according to the home-school-community collaborative education work plan?",
    "ID6": "Has your school held lectures, special meetings, themed seminars, practical activities or similar to strengthen teachers' competence in home-school-community collaborative education?",
    "CO1": "You are able to fully grasp and promptly communicate to parents students' thoughts and emotions, academic status, behaviour and physical and mental development while at school",
    "CO2": "You are able to actively innovate everyday communication channels and keep regular close contact between school and family through home-contact booklets, telephone, WeChat, the internet and other means",
    "CO3": "You are able to provide concrete guidance tailored to the individual needs of different families, paying particular attention to children in difficulty such as rural left-behind children, children with disabilities, orphans and children from special families",
    "CO4": "You are able to strengthen guidance of the parent committee's work, clarify its duties, improve its rules, regulate its conduct, strictly manage the posting of information in parent messaging groups, and strictly prohibit irregular fee collection in the parent committee's name.",
    "CO5": "You are able, on the basis of the school's relatively stable social-practice education bases and resource directory, to jointly develop social-practice courses according to each base's resources and to carry out, in a targeted and regular way, Communist Youth League and Young Pioneers activities, labour education, practical teaching, volunteer service, legal education, safety education and study tours.",
}


def main():
    for table, items in mod.stems().items():
        zh, en, instr_zh, instr_en = OPTS[table]
        rows = []
        for code, stem in items:
            for r in sorted(zh):
                rows.append(row(table, f"{table}_1", code, instr_zh, "Chinese", r, stem, option_text=zh[r],
                                item_text_tr=EN[code], option_text_tr=en[r]))
        write(table, rows)


if __name__ == "__main__":
    main()
