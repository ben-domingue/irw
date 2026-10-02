import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import irw_batch_updated as b


class DocFilesLast(unittest.TestCase):
    def test_codebook_moves_behind_data(self):
        # Zenodo 5040719's listing order, 2026-09-30.
        listing = [("u1", "Wave4_DICTIONARY.xls", 1),
                   ("u2", "CODE BOOK_English_Original_WHO_questionnaire.xlsx", 1),
                   ("u3", "Valide_DATA_4W.csv", 1),
                   ("u4", "Valide_DATA_1W.csv", 1)]
        with mock.patch.object(b, "_resolve_data_files_any_order",
                               return_value=(listing, "cc-by-4.0", [])):
            files, lic, _ = b.resolve_data_files({})
        self.assertEqual([f[1] for f in files],
                         ["Valide_DATA_4W.csv", "Valide_DATA_1W.csv",
                          "Wave4_DICTIONARY.xls",
                          "CODE BOOK_English_Original_WHO_questionnaire.xlsx"])
        self.assertEqual(lic, "cc-by-4.0")

    def test_codebook_only_deposit_still_has_a_file(self):
        listing = [("u1", "codebook.csv", 1)]
        with mock.patch.object(b, "_resolve_data_files_any_order",
                               return_value=(listing, "", [])):
            files, _, _ = b.resolve_data_files({})
        self.assertEqual(len(files), 1)

    def test_data_names_not_demoted(self):
        for name in ("questionnaire_data.csv", "responses.csv",
                     "study1.sav", "monkey_rt.csv"):
            self.assertFalse(b._looks_like_documentation(name), name)
        for name in ("README.csv", "data_dictionary.xlsx", "Codebook.xls",
                     "variable_list.csv", "metadata.csv"):
            self.assertTrue(b._looks_like_documentation(name), name)


if __name__ == "__main__":
    unittest.main()
