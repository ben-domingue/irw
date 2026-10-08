# data/

One self-contained processing script per dataset. Each reads its source and
writes IRW-format output. Read [`../datastandard.md`](../datastandard.md)
before writing one: it owns the output schema and the naming rule
(`authorname_year_construct`, lowercase, underscores).

## Subfolders

The first four hold the data families other than core (ARCHITECTURE.md section 2 defines
the families); the rest are groups inside core.

| Folder | Holds |
|---|---|
| `competitions/` | The competitions family, `irw_competitions` (contests, and pairwise comparisons of fixed things) |
| `nominal/` | The nominal family, `irw_nominal` (unscored categorical responses) |
| `simsyn/` | The simsyn family, `irw_simsyn` (simulated and synthetic data) |
| `conjoint/` | The conjoint family, `irw_conjoint` (conjoint experiments in their own layout; see its README) |
| `trials/` | Trial-level sports tables (shots, kicks, passes) |
| `gilbert_hte/` | The IL-HTE `gilbert_meta_*` series. File names carry the dataset numbers (`il_hte_07_08.R` builds `gilbert_meta_7` and `_8`); `il_hte_00_setup.R` is shared by the series |
| `pisa/` | PISA builds |
| `tests/` | CI checks for helpers used by `data/` scripts (run by `.github/workflows/tests.yml`) |

Everything else sits at the top level.

## Older names

Many older scripts predate the naming rule: upper-case acronyms, no year,
spaces, `.r` rather than `.R`. **Do not rename them.** `metadata/table_scripts.csv`,
processing notes, provenance records and the MCP's `get_processing_notes`
find scripts by path, and a rename silently breaks those links. Name new
scripts by the rule.
