# AI benchmarks vs people: the two-factor IMV panel

`plot_2pl_2f.R` reproduces one panel of the overview figure from the
AI-benchmark IMV vignette (datapages/irw#186): the cross-validated IMV gain
from a 2PL to an exploratory two-factor 2PL, for AI benchmark response
matrices against size-matched draws from human IRW tables.

```
Rscript plot_2pl_2f.R      # writes fig_2pl_2f.png and fig_2pl_2f.pdf here
```

## Inputs

`ai_benchmark_imv_results.csv` is the results table of the full run
(62 matrices, all converged), computed against IRW v512 on 2026-10-02 by
`vignettes/ai_benchmark_imv_compute.R` on the `ai-benchmark-imv-vignette`
branch of datapages/irw (commit a61a62710). That script, the fits and the full
page live there; this directory only carries the summary table so the figure
can be redrawn without them.

One row per fitted matrix:

| column | meaning |
|---|---|
| `key` | matrix id, `ai__<benchmark>__<full|draw>` or `human__<benchmark>__<table>__<draw>` |
| `source` | `ai` or `human` |
| `benchmark` | the OpenEval benchmark (`jiang_2026_openeval_<name>` in IRW) that sets the matrix size |
| `table` | the IRW table the responses come from |
| `draw` | 0 = full item set; 1, 2 = random draws of 300 items (and, for humans, of N respondents) |
| `panel` | `primary` (7 benchmarks, 100+ models) or `secondary` (3 benchmarks, 50-60 models) |
| `kind` | `ability` (correctness) or `propensity` (compliance / refusal) |
| `N`, `J`, `n_obs` | respondents, items, cells after dropping near-constant items |
| `imv_rasch_2pl`, `imv_2pl_2f` | IMV averaged over 5 folds |

The figure uses the primary panel only: 7 AI full-item fits, 12 AI 300-item
draws, and 28 human draws (two each from `choi_2026_cmsce_2019_1` and
`previc_bohn2023` per benchmark, subsampled to the benchmark's model count).
