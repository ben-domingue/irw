# IL-HTE Econ, 37/38: Carpena (2024) JDS - Health Knowledge/Behavior
# Source: Josh Gilbert's IL-HTE Econ cleaning code, "00 clean_il_hte_econ.qmd"
# (gilbert_share/06 IL-HTE Econ/analysis/), split into one file per dataset (#2765).
# Code is verbatim; the qmd's prose is kept as comments. Dataset N here is IRW
# table gilbert_meta_N.
# Run il_hte_00_setup.R first (libraries, `raw`/`clean` paths, rasch_score()).

carpena_pre <- read_dta(glue("{raw}/37 baseline.dta")) |> 
  mutate(treat = 1 - control) |> 
  select(s_id = Id, block_id = neighborhood, treat, 
         cov_female = female,
         cov_hh_size = hhsize,
         cov_hh_income = hhincome,
         cov_age = age,
         cov_married = married,
         cov_hindu = hindu,
         cov_completed_elementary = completed_elementary,
         cov_completed_secondary = completed_secondary,
         aids_curable:water_tap)

# there are only 5 baseline items - combining and using for both outcomes
# and very little overlap with post items; so only post in item level file
carpena_irt <- carpena_pre |> 
  select(aids_curable:water_tap) |> 
  mirt(1, "Rasch", verbose = FALSE)

carpena2024_p <- carpena_pre |> 
  mutate(baseline = fscores(carpena_irt)[,],
         std_baseline = scale(baseline)[,]) |> 
  select(contains("_id"), treat, std_baseline, contains("cov_"))

carpena_post <- read_dta(glue("{raw}/37 endline.dta")) |> 
  select(s_id = Id, wash_defecation:bought_ins,
         -ever_had_ins)

carpena2024_a <- carpena_post |> 
  select(-c(water_boil_filter:bought_ins)) |> 
  pivot_longer(wash_defecation:nightblindness_curable,
               names_to = "item", 
               values_to = "score") |> 
  mutate(time = 1) |> 
  drop_na(score) |> 
  left_join(carpena2024_p, by = "s_id") |> 
  arrange(s_id, item, time)

carpena2024_b <- carpena_post |> 
  select(-c(wash_defecation:nightblindness_curable)) |> 
  pivot_longer(water_boil_filter:bought_ins,
               names_to = "item", 
               values_to = "score") |> 
  mutate(time = 1) |> 
  drop_na(score) |> 
  left_join(carpena2024_p, by = "s_id") |> 
  arrange(s_id, item, time)

rm(carpena_post, carpena_irt, carpena_pre)
