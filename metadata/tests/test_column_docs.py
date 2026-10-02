"""Unit tests for metadata/14_column_docs.py (#2763).

The fixtures are the shapes found in the corpus on 2026-10-02: the gilbert_meta
R `select(new = old)` rename that prompted #2755, a pandas rename dict, Stata
single and grouped renames, and the run-time-built names (`paste0("cov_", x)`)
that must never be read as "kept its source name". Run as a script, like
test_script_index.py:
    python metadata/tests/test_column_docs.py -v
"""

import importlib.util
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("column_docs", HERE.parent / "14_column_docs.py")
cd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cd)

STANDARD = """| Column | Required | Rules |
|--------|----------|-------|
| `id` | yes | Identifier. |
| `item` | yes | Item. |
| `resp` | yes | Response. |
| `cov_*` | no | Covariates. |
| `treat` | no | Treatment. |
| `cluster_id` | no | Cluster. |
| `block_id` | no | Block. |
| `std_baseline`, `std_baseline_*` | no | Baseline. |
| `qmatrix1`…`qmatrixN` | no | Q-matrix. |

Prose naming `wave` is not a definition.
"""

SCRIPTS = {
    "data/gilbert_meta_102through104.R": (
        "##Paper: https://doi.org/10.1002/rrq.70048\n"
        "relyea_wide <- read_dta(f) |>\n"
        "  select(id = s_id, cluster_id = teacher_name, block_id = school_name,\n"
        "         treat = g3_treatment, cov_male = s_male,\n"
        "         std_baseline = scale(s_map)[,])\n"
        "relyea_long <- read_dta(g) |> rename(item_cov_transfer = transfer)\n"
    ),
    "data/survey_2024.py": (
        "# cov_gender is recoded below\n"
        'COVS = {"Gender": "cov_gender", "Age": "cov_age"}\n'
        'long = df.melt(id_vars=["id"] + list(COVS.values()), var_name="item", value_name="resp")\n'
    ),
    "data/chile_2024.do": (
        "* rename sexo cov_ignored  (a comment, not code)\n"
        "rename rph_nivel cov_education\n"
        "ren (correct trial responsetime) (resp item rt)\n"
    ),
    "data/oxford_2024.r": (
        'cov_list <- c("age", "gender")\n'
        'd <- d |> rename_with(~ paste0("cov_", .), all_of(cov_list))\n'
    ),
    "data/notes_only.txt": "##data already in irw-compliant format\n",
}
PATHS = sorted(SCRIPTS)
TABLES = {
    "gilbert_meta_103": ["id", "item", "resp", "rt", "cluster_id", "block_id",
                         "treat", "cov_male", "std_baseline", "item_cov_transfer", "ln_rt"],
    "survey_2024": ["id", "item", "resp", "cov_gender", "cov_age", "wave"],
    "chile_2024": ["id", "item", "resp", "rt", "cov_education", "cov_sex"],
    "oxford_2024_rse": ["id", "item", "resp", "cov_gender"],
    "orphan_2020": ["id", "item", "resp", "cov_x"],
}
INDEX = {"gilbert_meta_103": ["data/gilbert_meta_102through104.R"]}


class ColumnDocsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        exact, prefix = cd.parse_standard(STANDARD)
        rows = cd.build(TABLES, PATHS, SCRIPTS, INDEX, exact, prefix)
        cls.rows = {(r["table"], r["column"]): r for r in rows}

    def row(self, table, column):
        return self.rows[(table, column)]

    def test_standard_table_only(self):
        exact, prefix = cd.parse_standard(STANDARD)
        self.assertIn("cluster_id", exact)
        self.assertIn("std_baseline", exact)
        self.assertNotIn("wave", exact)
        self.assertEqual(prefix, {"cov_", "std_baseline_", "qmatrix"})

    def test_the_2755_columns_trace_to_their_source_names(self):
        self.assertEqual(self.row("gilbert_meta_103", "cluster_id")["source_column"], "teacher_name")
        self.assertEqual(self.row("gilbert_meta_103", "block_id")["source_column"], "school_name")
        self.assertEqual(self.row("gilbert_meta_103", "treat")["source_column"], "g3_treatment")
        self.assertEqual(self.row("gilbert_meta_103", "cluster_id")["script_line"], "3")
        self.assertEqual(self.row("gilbert_meta_103", "cluster_id")["match"], "index")

    def test_a_transformed_column_is_built_not_renamed(self):
        r = self.row("gilbert_meta_103", "std_baseline")
        self.assertEqual((r["basis"], r["source_column"]), ("built", ""))
        self.assertEqual(r["documented"], "true")  # the standard defines it

    def test_a_column_the_code_never_names_is_not_traced(self):
        # ln_rt passes through from the source, probably -- but not provably.
        r = self.row("gilbert_meta_103", "ln_rt")
        self.assertEqual((r["basis"], r["defined_by"], r["documented"]), ("", "", "false"))

    def test_a_nonstandard_rename_is_documented_by_its_source(self):
        r = self.row("gilbert_meta_103", "item_cov_transfer")
        self.assertEqual((r["defined_by"], r["source_column"], r["documented"]), ("", "transfer", "true"))

    def test_pandas_rename_dict(self):
        r = self.row("survey_2024", "cov_gender")
        self.assertEqual((r["basis"], r["source_column"], r["script_line"]), ("renamed", "Gender", "2"))
        self.assertEqual(r["defined_by"], "standard_family")

    def test_comment_lines_are_ignored(self):
        self.assertEqual(self.row("chile_2024", "cov_sex")["basis"], "")

    def test_stata_single_and_grouped_renames(self):
        self.assertEqual(self.row("chile_2024", "cov_education")["source_column"], "rph_nivel")
        self.assertEqual(self.row("chile_2024", "rt")["source_column"], "responsetime")
        self.assertEqual(self.row("chile_2024", "item")["source_column"], "trial")

    def test_run_time_names_point_at_the_line_that_builds_them(self):
        r = self.row("oxford_2024_rse", "cov_gender")
        self.assertEqual((r["basis"], r["script_line"], r["documented"]), ("built", "2", "false"))
        self.assertEqual(r["match"], "prefix")

    def test_no_script_leaves_basis_blank(self):
        r = self.row("orphan_2020", "cov_x")
        self.assertEqual((r["match"], r["basis"], r["documented"]), ("none", "", "false"))
        self.assertEqual(self.row("orphan_2020", "id")["documented"], "true")

    def test_r_constants_are_not_source_columns(self):
        self.assertIsNone(cd.rename_source("cov_flag", "data/x.R", "mutate(cov_flag = TRUE)"))
        self.assertIsNone(cd.rename_source("cov_age", "data/x.R", "mutate(cov_age = age * 12)"))

    def test_match_mirrors_the_mcp(self):
        paths = ["data/gilbert_meta_102through104.R", "data/study_2026.py", "data/nominal/himmelstein.R"]
        self.assertEqual(cd.match_scripts("gilbert_meta_10", paths, {}), ([], "none"))
        self.assertEqual(cd.match_scripts("study_2026_phq", paths, {}), (["data/study_2026.py"], "prefix"))
        self.assertEqual(cd.match_scripts("himmelstein-number_series-2025", paths, {}), ([], "none"))


if __name__ == "__main__":
    unittest.main()
