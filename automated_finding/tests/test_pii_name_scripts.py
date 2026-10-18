"""A roster of personal names is a roster in every writing system.

The bare-`name` content check used the regex
`^[A-Za-zÀ-ɏ][A-Za-zÀ-ɏ .'-]{0,40}$`, which is Latin-only. figshare 27635013
held 455 distinct real Chinese personal names in a column literally called
`name`, over 460 rows, and the whole PII screen returned clean (2026-10-18).
The other tiers cannot cover for it: the column name is the bare word `name`,
which is exactly the case this content check exists for, and the values are
names rather than emails.

CJK, Cyrillic, Greek, Arabic, Hebrew, Thai and Devanagari all failed it. Thai
and Devanagari need more than `isalpha()`, because they write vowels as
combining marks (category Mn/Mc).

unittest, not pytest: CI runs `python -m unittest discover` over every test
directory (.github/workflows/tests.yml) and pytest is not installed there.
"""
import itertools
import unittest

import pandas as pd

from irw_triage_updated import screen_for_pii


def roster(first, last, n=30):
    return [a + " " + b for a, b in
            itertools.islice(itertools.product(first, last), n)]


def screens(values):
    df = pd.DataFrame({"name": values, "q1": [1] * len(values)})
    return bool(screen_for_pii(df.columns, df))


class RostersFireInEveryScript(unittest.TestCase):
    CASES = {
        "chinese": [a + b for a, b in itertools.islice(
            itertools.product("王李张刘陈杨黄赵吴周", "伟芳娜秀英敏静丽强磊洋勇"), 100)],
        "cyrillic": roster(["Иван", "Пётр", "Анна", "Мария", "Олег", "Юлия",
                            "Сергей"],
                           ["Иванов", "Петров", "Смирнов", "Кузнецов", "Попов"]),
        "arabic": roster(["محمد", "أحمد", "فاطمة", "علي", "سارة", "خالد", "نور"],
                         ["العلي", "الحسن", "السالم", "المنصور", "الزهراني"]),
        "greek": roster(["Γιάννης", "Μαρία", "Νίκος", "Ελένη", "Κώστας",
                         "Σοφία", "Δημήτρης"],
                        ["Παπαδόπουλος", "Νικολάου", "Γεωργίου", "Δημητρίου",
                         "Ιωάννου"]),
        "hebrew": roster(["דוד", "שרה", "יוסף", "רחל", "משה", "מרים", "אברהם"],
                         ["כהן", "לוי", "מזרחי", "פרץ", "ביטון"]),
        # combining marks: isalpha() alone is not enough for these two
        "thai": roster(["สมชาย", "สมหญิง", "ประเสริฐ", "วิไล", "อนันต์", "สุดา",
                        "ชัยวัฒน์"],
                       ["ใจดี", "สุขสันต์", "รักไทย", "พงษ์ไทย", "ศรีสุข"]),
        "devanagari": roster(["राहुल", "प्रिया", "अमित", "सुनीता", "विकास",
                              "अंजलि", "संजय"],
                             ["शर्मा", "वर्मा", "गुप्ता", "सिंह", "यादव"]),
        "latin": roster(["Ana", "Bob", "Carla", "Dan", "Eve", "Luis", "Marta"],
                        ["Lopez", "Smith", "Diaz", "Ruiz", "Mora"]),
    }

    def test_each_script(self):
        for script, values in self.CASES.items():
            with self.subTest(script=script):
                self.assertTrue(screens(values),
                                f"{script} roster screened clean")


class ThingsThatMustStayClean(unittest.TestCase):
    def test_a_six_level_categorical(self):
        self.assertFalse(screens(["Control", "Treatment", "Waitlist",
                                  "Active", "Sham", "Other"] * 40))

    def test_free_text_answers(self):
        self.assertFalse(screens(
            ["I think that the policy is wrong because it does not help"] * 60))

    def test_numeric_codes_held_as_strings(self):
        self.assertFalse(screens([str(1000 + i) for i in range(60)]))

    def test_city_names_are_low_cardinality(self):
        self.assertFalse(screens(["Roma", "Milano", "Napoli", "Torino"] * 15))

    def test_chinese_likert_anchors_are_not_names(self):
        """The shape most likely to break a Unicode-aware name test."""
        self.assertFalse(screens(
            ["非常同意", "同意", "中立", "不同意", "非常不同意"] * 20))


if __name__ == "__main__":
    unittest.main()
