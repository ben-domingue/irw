timu2024 <- read_dta(glue("{raw}/108 Data.dta")) |> 
  select(wave = time, id = hhid, l2a:l2h, 
         treat = trtmnt_orig,
         cov_hh_age = bsln_cntr_h_head_age,
         cov_hh_male = bsln_head_sex
         ) |> 
  mutate(treat = if_else(treat == 0, 0, 1)) |>
  # fill in missing treat values
  group_by(id) |> 
  mutate(treat = mean(treat, na.rm = TRUE)) |> 
  ungroup() |> 
  pivot_longer(l2a:l2h, values_to = "resp",
               names_to = "item") |> 
  drop_na(resp) |> 
  relocate(id, treat, item, wave, resp) |> 
  arrange(id, item, wave)

write_csv(timu2024, glue("{clean}/gilbert_meta_108.csv"))
