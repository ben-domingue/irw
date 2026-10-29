"""Stem entries in the relevance vocabulary, and the non-English "raw data" words.

Two findings from 2026-10-29, while asking why German-titled PsychArchives
deposits fared worst at the relevance gate:

1. `_matcher()` wrapped every term in `\\b...\\b`, so a term written as a STEM
   could never match. `\\bpsychometri\\b` cannot match "psychometrische" --
   the boundary would have to fall between "i" and "s", both word characters.
   A dozen entries were written as stems and had therefore never matched
   anything: psychometri (four languages), psicométric, depressiv,
   itemantwort, itemrespons, redeneer. A trailing "*" now marks a stem.

2. A deposit titled "Primärdaten zu ..." announces itself as primary response
   data and was being dropped. Adding the raw/primary-data words in es/de/fr/
   nl admitted 24 more of 258 PsychArchives researchData records (48.1% ->
   57.4% pass) and lost none. Measured against all 3,434 historical lead
   titles the same change admits 2 more, so it is not a floodgate.

The ENGLISH equivalents stay out on purpose: "raw data" is a routine title
phrase in fields we don't want.

unittest, not pytest: CI runs `python -m unittest discover` over every test
directory (.github/workflows/tests.yml) and pytest is not installed there.
"""
import unittest

from irw_discover_updated import Hit, _matcher, is_relevant


def _rel(title, query=""):
    return is_relevant(Hit("psycharchives", title, ""), True, query)


class StemSyntax(unittest.TestCase):
    def test_star_matches_inflections(self):
        m = _matcher(["psychometri*", "psychométri*"])
        for word in ("psychometrische analyse", "psychometrie van de toets",
                     "analyse psychométrique", "psychometrics"):
            self.assertTrue(m.search(word), word)

    def test_star_still_requires_a_leading_boundary(self):
        self.assertIsNone(_matcher(["psychometri*"]).search("unpsychometric"))

    def test_unstarred_term_is_unchanged(self):
        m = _matcher(["irt", "bai"])
        self.assertTrue(m.search("an irt model"))
        self.assertIsNone(m.search("shirt"))
        self.assertIsNone(m.search("bait"))

    def test_short_stem_is_refused_rather_than_silently_unsafe(self):
        # A 3-letter prefix would match inside unrelated words exactly as
        # "bai" would match "bait", which is the guarantee _matcher exists
        # for -- so it raises instead of compiling.
        with self.assertRaises(ValueError):
            _matcher(["bai*"])


class StemsThatUsedToBeDead(unittest.TestCase):
    def test_german_psychometric_title(self):
        self.assertTrue(_rel("Psychometrische Analyse eines Fragebogens"))

    def test_spanish_and_dutch_and_german_inflections(self):
        self.assertTrue(_rel("Escala psicométrica de autoestima"))
        self.assertTrue(_rel("Itemresponstheorie voor toetsen"))
        self.assertTrue(_rel("Depressive Symptome bei Jugendlichen"))


class RawDataWords(unittest.TestCase):
    def test_the_four_languages(self):
        for title in ("Primärdaten einer Untersuchung zum Wahlverhalten",
                      "Rohdaten GAINS anonymisiert",
                      "Ruwe data van het onderzoek",
                      "Datos brutos del estudio",
                      "Données brutes de l'enquête"):
            self.assertTrue(_rel(title), title)

    def test_english_raw_data_is_still_not_a_pass(self):
        # The case the omission protects: every field deposits "raw data".
        self.assertFalse(_rel("Raw data for whole-genome sequencing"))
        self.assertFalse(_rel("Raw data from the flow sensor array"))

    def test_a_norming_sample_title_reaches_triage(self):
        # Real PsychArchives record, dropped before this change.
        self.assertTrue(_rel(
            "Skalen zur Erfassung von Hoffnungslosigkeit. "
            "Primärdaten der Normierungsstichprobe."))


class NoRegressionOnTheBlockedClasses(unittest.TestCase):
    def test_supplementary_titles_still_blocked(self):
        self.assertFalse(_rel("Table 3_Rasch analysis of the PHQ-9"))
        self.assertFalse(_rel("Data Sheet 1_questionnaire responses"))

    def test_an_irrelevant_title_still_fails(self):
        self.assertFalse(_rel("bait study of fish"))
        self.assertFalse(_rel("shirt manufacturing dataset"))


if __name__ == "__main__":
    unittest.main()
