#!/usr/bin/env python3
"""Verify mendes_lobao_2018_hpv_* item text against the article's Table 2
(10.1371/journal.pone.0206726, "Total" column, n = 807), which prints each
statement's percentage BY WORDING. If the questionnaire numbering (b2..c40,
the .sav names) were tied to the wrong statement, the raw .sav percentages
would land on another row of Table 2.

Table 2 reports, for knowledge statements, % answering correctly -- with
"don't know" counted as correct for false statements (100 - % yes) -- and for
attitude statements % agreeing. Percentages here are computed from the raw
.sav (codes 1 yes / 0 no / 2 don't know) over non-missing answers, the same
way for every row, then matched row-for-row.

Run: RAW=<s001.sav> python3 verify_mendes_lobao_2018.py
"""
import os
import sys

import pyreadstat

# code -> (Table 2 wording, Total %, how the paper computes it)
T2 = {
    "b3": ("HPV is transmitted by sexual contact (T)", 92, "yes"),
    "b4": ("HPV is spread by airborne transmission (F)", 92, "notyes"),
    "b8": ("Even without symptoms, someone can transmit HPV (T)", 83, "yes"),
    "b2": ("HPV is transmitted through use of public bathrooms / pools / showers (F)", 66, "notyes"),
    "b9": ("Condom use fully protects against HPV (F)", 37, "notyes"),
    "c34": ("HPV can cause cervical cancer (T)", 86, "yes"),
    "c35": ("Cervical cancer is NOT a common cause of cancer death among women (F)", 75, "notyes"),
    "c36": ("HPV does not cause cancer in men (F)", 75, "notyes"),
    "c37": ("HPV can cause genital warts (T)", 69, "yes"),
    "b7": ("Men cannot catch HPV (F)", 66, "notyes"),
    "b10": ("HPV can be cured with antibiotics (F)", 62, "notyes"),
    "b5": ("Someone with HPV usually has symptoms (F)", 58, "notyes"),
    "b6": ("HPV is a very common virus (T)", 55, "yes"),
    "b11": ("A vaccine against HPV already exists (T)", 89, "yes"),
    "c40": ("The HPV vaccine works better when given before the start of sexual activity (T)", 87, "yes"),
    "c31": ("The HPV vaccine is not for boys (F)", 71, "notyes"),
    "c22": ("The most common reactions ... are minor (T)", 65, "yes"),
    # The two rows below are where the article's own scoring departs from its
    # key: printed 65 for a (V)/true statement equals 100 - % yes, and 30 for a
    # (F) statement equals % yes. The wording-to-code tie still holds (each
    # number is matched by this code's distribution and no other's).
    "c32": ("There is a vaccine against cervical cancer (V)", 65, "notyes"),
    "c33": ("There is no vaccine against genital warts (F)", 30, "yes"),
    "c38": ("If a preventive exam/Pap smear is normal, then a woman does not have HPV (F)", 64, "notyes"),
    "c39": ("GIRLS that receive the HPV vaccine do not need to have preventive exams (F)", 82, "notyes"),
    "c14": ("I generally believe in vaccines", 96, "yes"),
    "c27": ("I trust the National Immunization Programme", 94, "yes"),
    "c11": ("The HPV vaccine is efficacious/ it works", 83, "yes"),
    "c20": ("I don't think the HPV vaccine is safe/ I think it can cause severe reactions", 21, "yes"),
    "c29": ("I would give my child a vaccine against a sexually transmitted infection", 72, "notyes"),
    "c15": ("I think my DAUGHTER is at risk/has a chance of getting HPV", 71, "yes"),
    "c16": ("I think my SON is at risk/has a chance of getting HPV", 68, "yes"),
    "c21": ("GIRLS between 9 and 13 years are too young to get the vaccine", 22, "yes"),
    "c23": ("Getting the HPV vaccine can cause GIRLS to become sexually active much earlier", 15, "yes"),
}
TOL = 2.0


def main():
    df, _ = pyreadstat.read_sav(os.environ["RAW"])
    codes = list(T2)
    pct = {}
    for c in codes:
        x = df[c].dropna()
        yes = 100 * (x == 1).mean()
        pct[c] = {"yes": yes, "notyes": 100 - yes}
    bad = 0
    for c, (wording, p, how) in T2.items():
        own = pct[c][how]
        # nearest competing code under the same computation
        others = sorted((abs(pct[o][how] - p), o) for o in codes if o != c)
        ok = abs(own - p) <= TOL
        bad += not ok
        print(f"{c:4s} {own:5.1f} vs {p:3d}  {'OK ' if ok else 'BAD'}  nearest other {others[0][1]} ({others[0][0]:.1f} away)  {wording}")
    print(f"\n{len(T2) - bad}/{len(T2)} Table 2 rows matched by their own code within {TOL} points")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
