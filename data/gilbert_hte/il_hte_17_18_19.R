# IL-HTE Econ, 17/18/19: Duflo (2024) EJ - Math/English/Local Language
# Source: Josh Gilbert's IL-HTE Econ cleaning code, "00 clean_il_hte_econ.qmd"
# (gilbert_share/06 IL-HTE Econ/analysis/), split into one file per dataset (#2765).
# Code is verbatim; the qmd's prose is kept as comments. Dataset N here is IRW
# table gilbert_meta_N.
# Run il_hte_00_setup.R first (libraries, `raw`/`clean` paths, rasch_score()).

duflo <- read_dta(glue("{raw}/17 tcai_studentlevel_final_ej.dta")) |> 
  select(s_id = pupiltcaicode, treat = anytreat,
         cluster_id = schcode, block_id = strata,
         cov_female = bl_gender,
         cov_age = bl_child_age,
         cov_father_literate = bl_father_literate,
         cov_mother_literate = bl_mother_literate,
         # bl is baseline
         # e1 is endline
         # e2 is followup
         # w is written exam, which it looks like some subset of students took
         contains("bl_loclang_"), contains("bl_math"),
         contains("bl_eng"), contains("e1_math"), contains("e1_loclang"),
         contains("e1_eng"),
         contains("e2_loclang"), contains("e2_math"), contains("e2_eng"),
         # w are written tests that have no baseline;
         # excluding for now
         # contains("e1w_"),
         # contains("e2w_"),
         -contains("theta"),
         -contains("testtaker")) |> 
  # pivot to long
  pivot_longer(-c(s_id:cov_mother_literate), names_to = "item", values_to = "score") |> 
  drop_na(score) |> 
  mutate(
    # get time from item prefix
    time = case_when(
      str_detect(item, "bl") ~ 0,
      str_detect(item, "e1") ~ 1,
      str_detect(item, "e2") ~ 2
    ),
    # get outcome type from item text
    outcome = case_when(
      str_detect(item, "math") ~ "math",
      str_detect(item, "eng") ~ "eng_lang",
      str_detect(item, "loclang") ~ "loc_lang"
    ),
    # make item names constant across time
    item = str_remove(item, "bl_|e1_|e2_|e1w_|e2w_")
  ) |> 
  arrange(s_id, item, time)

duflo2024_a <- duflo |> 
  filter(outcome == "math")

duflo2024_b <- duflo |> 
  filter(outcome == "eng_lang")

duflo2024_c <- duflo |> 
  filter(outcome == "loc_lang")

rm(duflo)
