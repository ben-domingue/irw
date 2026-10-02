# IL-HTE Econ, 3: Gilbert (2024) Epi Methods - Depression
# Source: Josh Gilbert's IL-HTE Econ cleaning code, "00 clean_il_hte_econ.qmd"
# (gilbert_share/06 IL-HTE Econ/analysis/), split into one file per dataset (#2765).
# Code is verbatim; the qmd's prose is kept as comments. Dataset N here is IRW
# table gilbert_meta_N.
# Run il_hte_00_setup.R first (libraries, `raw`/`clean` paths, rasch_score()).

# Note: this is simulated data based on the model output of Gilbert, et al. 2024; the items are random and do not correspond to the actual HDRS items, but the DGP is based on an IL-HTE model.

gilbert2024_a <- glue("{raw}/03 simulated_ssri_binary.csv") |> 
  # read csv2 because of the format
  read_csv2() |> 
  # rename variables
  rename(s_id = PID, 
         treat = SSRI, 
         item = itemID, 
         std_baseline = HAMD_BASE,
         score = itemScore) |> 
  mutate(time = 1)
